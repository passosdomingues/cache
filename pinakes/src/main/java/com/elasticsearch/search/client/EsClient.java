package com.elasticsearch.search.client;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch._types.SortOrder;
import co.elastic.clients.elasticsearch._types.query_dsl.*;
import co.elastic.clients.elasticsearch.core.SearchRequest;
import co.elastic.clients.elasticsearch.core.SearchResponse;
import co.elastic.clients.elasticsearch.core.search.Hit;
import co.elastic.clients.json.JsonData;
import com.elasticsearch.search.model.SearchParams;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.github.resilience4j.retry.annotation.Retry;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/**
 * Low-level Elasticsearch client — atomic, single-responsibility methods.
 *
 * ══════════════════════════════════════════════════════════════
 * IMPROVEMENTS IN THIS VERSION:
 *
 * §EXACT-PHRASE  — buildExactPhraseQuery() emits match_phrase clauses for
 *                  each quoted segment extracted by QueryAnalyser.
 *                  When quotes are present the full query becomes:
 *                    bool {
 *                      must:  [ match_phrase("binary search"), ... ]   ← exact
 *                      should:[ multiMatch(fuzzy remainder), ... ]      ← fuzzy
 *                    }
 *
 * §WORD-VECTOR   — suggestWord() issues one suggest request PER WORD so we
 *                  always get a full corrected word back (not a stemmed root).
 *                  The old approach passed the entire multi-word query at once
 *                  which caused the ES term-suggest to return partial stems.
 *
 * §RAW-SUGGEST   — All suggests target content.raw_suggest (standard analyser,
 *                  no Snowball) so vocabulary retains real surface forms.
 *
 * §ATOMICITY     — Each public method does exactly one ES operation.
 *                  Composition is the service layer's responsibility.
 *
 * §SOURCE-FILTER — §2.4: content excluded from _source when highlight=true.
 *
 * §FILTERS       — §2.3: reading_time and dt_creation range filters.
 *
 * §SORT          — §2.6: configurable sort field + direction.
 *
 * §DID-YOU-MEAN  — SuggestMode changed from Missing to Popular so corrections
 *                  appear even when the misspelled word exists in the corpus.
 * ══════════════════════════════════════════════════════════════
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class EsClient {

    private final ElasticsearchClient esClient;

    @Value("${elasticsearch.index:wikipedia_v2}")
    private String index;

    // ── Full-text search ───────────────────────────────────────────────────

    /**
     * Executes a full boolean query.
     *
     * When the params contain quoted phrases (detected by QueryAnalyser upstream
     * and passed in {@link SearchParams#getExactPhrases()}), we inject a
     * match_phrase MUST clause for each phrase alongside the fuzzy multi_match.
     */
    @Retry(name = "esClient")
    public SearchResponse<ObjectNode> search(SearchParams params) throws IOException {
        boolean hl = params.isHighlight();

        // §2.4: exclude heavy 'content' field when highlight fragments suffice
        List<String> sourceIncludes = hl
                ? List.of("title", "url", "reading_time")
                : List.of("title", "url", "content", "reading_time");

        // §HIGHLIGHT-FIX: only attach the highlight block when highlight=true.
        // The ES Java Client validates that Highlight.fields is non-empty on build(),
        // so returning an empty Highlight.Builder (when hl=false) causes
        // "Missing required property 'Highlight.fields'". Skipping .highlight()
        // entirely avoids the validation and is semantically correct.
        //
        // NOTE: SearchRequest exposes only SearchRequest.of(lambda) — no static .builder().
        // We capture a reference to the inner builder (r) in the lambda so we can
        // conditionally call r.highlight() before returning it.
        final SearchParams p = params; // effectively-final for lambda
        var req = SearchRequest.of(r -> {
            r.index(index)
             .from((p.getPage() - 1) * p.getSize())
             .size(p.getSize())
             .source(src -> src.filter(f -> f.includes(sourceIncludes)))
             .query(q -> q.bool(b -> buildBoolQuery(b, p)))
             .sort(sortBuilder(p));

            if (hl) {
                r.highlight(h -> buildHighlight(h, p));
            }
            return r;
        });

        log.debug("ES search [idx={} q='{}' page={} hl={} phrases={}]",
                index, params.getQuery(), params.getPage(), hl,
                params.getExactPhrases());

        return esClient.search(req, ObjectNode.class);
    }

    // ── Single-word spell suggestion ───────────────────────────────────────

    /**
     * Corrects a SINGLE word using ES term-suggest on content.raw_suggest.
     *
     * §WORD-VECTOR fix: calling this once per token (not once for the whole
     * query) ensures ES returns the full corrected word, not a stemmed root.
     * The caller (QueryAnalyser / SearchService) iterates the token vector.
     *
     * §RAW-SUGGEST fix: targets content.raw_suggest (standard analyser, no
     * Snowball) so "Schrödinger" stays "Schrödinger" not "schroding".
     *
     * §DID-YOU-MEAN fix: uses SuggestMode.Popular (not Missing) so corrections
     * are returned when the suggested term has higher document frequency than
     * the input — even if the misspelled term exists somewhere in the corpus.
     * Missing mode silently swallowed corrections for typos that happened to
     * appear in any Wikipedia article, preventing the "Did you mean?" banner.
     *
     * @param word  a single token (no spaces)
     * @return      best correction, or {@code word} if none found
     */
    @Retry(name = "esClient")
    public String suggestWord(String word) throws IOException {
        if (!StringUtils.hasText(word) || word.length() < 2) return word;

        var resp = esClient.search(s -> s
                .index(index)
                .size(0)
                .suggest(sg -> sg
                        .suggesters("word-suggest", ts -> ts
                                .text(word)
                                .term(t -> t
                                        .field("content.raw_suggest")
                                        .size(1)
                                        .suggestMode(
                                            co.elastic.clients.elasticsearch._types.SuggestMode.Popular)
                                )
                        )
                ), ObjectNode.class);

        if (resp.suggest() == null) return word;
        var entries = resp.suggest().get("word-suggest");
        if (entries == null || entries.isEmpty()) return word;
        var options = entries.get(0).term().options();
        if (options == null || options.isEmpty()) return word;

        return options.get(0).text();
    }

    // ── Autocomplete ───────────────────────────────────────────────────────

    /**
     * match_phrase_prefix autocomplete on the title field.
     * max_expansions=10 bounds the prefix fan-out to protect ES query cost.
     */
    @Retry(name = "esClient")
    public SearchResponse<ObjectNode> autocomplete(String partialQuery, int maxResults)
            throws IOException {

        return esClient.search(s -> s
                .index(index)
                .size(maxResults)
                .source(src -> src.filter(f -> f.includes("title", "url")))
                .query(q -> q.matchPhrasePrefix(mp -> mp
                        .field("title")
                        .query(partialQuery)
                        .maxExpansions(10)
                )), ObjectNode.class);
    }

    // ── Aggregation stats ──────────────────────────────────────────────────

    /**
     * Returns index-level statistics using metric aggregations (size=0).
     * match_all with filter context — very fast, no scoring.
     */
    @Retry(name = "esClient")
    public SearchResponse<ObjectNode> stats() throws IOException {
        return esClient.search(s -> s
                .index(index)
                .size(0)
                .query(q -> q.matchAll(m -> m))
                .aggregations("reading_time_stats",
                        a -> a.stats(st -> st.field("reading_time")))
                .aggregations("reading_time_ranges",
                        a -> a.range(rng -> rng
                                .field("reading_time")
                                .ranges(r -> r.key("fast").to("5.0"))
                                .ranges(r -> r.key("medium").from("5.0").to("10.0"))
                                .ranges(r -> r.key("slow").from("10.0"))
                        ))
                .aggregations("top_labels",
                        a -> a.terms(t -> t.field("label").size(20)))
                , ObjectNode.class);
    }

    // ── Abstract extraction ────────────────────────────────────────────────

    /**
     * Extracts the display abstract from a hit.
     * Priority: content highlight → title highlight → raw content (truncated).
     * Atomic: no ES call, pure mapping logic.
     */
    public String extractAbstract(Hit<ObjectNode> hit, boolean highlight) {
        if (highlight && hit.highlight() != null) {
            var cf = hit.highlight().get("content");
            if (cf != null && !cf.isEmpty()) return String.join(" … ", cf);
            var tf = hit.highlight().get("title");
            if (tf != null && !tf.isEmpty()) return tf.get(0);
        }
        ObjectNode src = hit.source();
        if (src != null && src.has("content")) {
            String c = src.get("content").asText("");
            return c.length() > 500 ? c.substring(0, 500) + "…" : c;
        }
        return "";
    }

    // ── Private builders ───────────────────────────────────────────────────

    /**
     * Builds the bool query.
     *
     * Structure when NO quoted phrases:
     *   must:   multiMatch(title^boost, content) with fuzziness
     *   should: matchPhrase(content, slop, phraseBoost)
     *   should: matchPhrase(title, phraseBoost * titleBoost)
     *   filter: reading_time range (if maxReadingTime set)
     *   filter: dt_creation range (if dateFrom/dateTo set)
     *
     * Structure when quoted phrases present:
     *   must:   matchPhrase(content, phrase) for each quoted phrase  ← exact
     *   must:   multiMatch(fuzzy remainder)  if remainder non-empty
     *   should: matchPhrase(title, phraseBoost * titleBoost)
     *   filter: (same as above)
     */
    private BoolQuery.Builder buildBoolQuery(BoolQuery.Builder bool, SearchParams params) {
        String q = params.getQuery();
        List<String> exactPhrases = params.getExactPhrases() != null
                ? params.getExactPhrases() : List.of();

        if (!exactPhrases.isEmpty()) {
            // Exact phrase mode: each quoted phrase is a MUST match_phrase
            for (String phrase : exactPhrases) {
                bool.must(m -> m.matchPhrase(mp -> mp
                        .field("content")
                        .query(phrase)
                        .slop(params.getSlop())
                ));
                // Also match phrase in title for higher scoring
                bool.should(sh -> sh.matchPhrase(mp -> mp
                        .field("title")
                        .query(phrase)
                        .boost(params.getTitleBoost())
                ));
            }
            // Fuzzy search on the non-quoted remainder (if any)
            String remainder = params.getFuzzyRemainder();
            if (StringUtils.hasText(remainder)) {
                bool.should(sh -> sh.multiMatch(mm -> mm
                        .fields("title^" + params.getTitleBoost(), "content")
                        .query(remainder)
                        .fuzziness(params.getFuzziness())
                        .operator(Operator.Or)
                ));
            }
        } else {
            // Normal fuzzy search mode
            bool.must(m -> m.multiMatch(mm -> mm
                    .fields("title^" + params.getTitleBoost(), "content")
                    .query(q)
                    .fuzziness(params.getFuzziness())
                    .operator(Operator.Or)
            ));
            // Phrase boost in content
            bool.should(sh -> sh.matchPhrase(mp -> mp
                    .field("content")
                    .query(q)
                    .slop(params.getSlop())
                    .boost(params.getPhraseBoost())
            ));
            // Phrase boost in title (highest signal)
            bool.should(sh -> sh.matchPhrase(mp -> mp
                    .field("title")
                    .query(q)
                    .boost(params.getPhraseBoost() * params.getTitleBoost())
            ));
        }

        // §2.3: reading_time range filter (does NOT affect score)
        if (params.getMaxReadingTime() != null) {
            bool.filter(f -> f.range(rng -> rng
                    .field("reading_time")
                    .lte(JsonData.of(params.getMaxReadingTime()))
            ));
        }

        // §2.3: dt_creation range filter
        if (StringUtils.hasText(params.getDateFrom()) || StringUtils.hasText(params.getDateTo())) {
            bool.filter(f -> f.range(rng -> {
                rng.field("dt_creation");
                if (StringUtils.hasText(params.getDateFrom()))
                    rng.gte(JsonData.of(params.getDateFrom()));
                if (StringUtils.hasText(params.getDateTo()))
                    rng.lte(JsonData.of(params.getDateTo()));
                return rng;
            }));
        }

        return bool;
    }

    /**
     * Builds the highlight configuration.
     * §4.3: uses an independent highlight_query with higher slop for better
     * phrase highlighting without loosening the main ranking query.
     */
    /**
     * Builds the highlight configuration.
     * §4.3: uses an independent highlight_query with higher slop for better
     * phrase highlighting without loosening the main ranking query.
     *
     * NOTE: This method is ONLY called when params.isHighlight() == true.
     * Callers MUST NOT invoke this method with highlight=false — the resulting
     * builder would be empty and trigger ES client validation:
     *   "Missing required property 'Highlight.fields'"
     */
    private co.elastic.clients.elasticsearch.core.search.Highlight.Builder buildHighlight(
            co.elastic.clients.elasticsearch.core.search.Highlight.Builder h,
            SearchParams params) {

        return h.preTags("<strong>").postTags("</strong>")
                .fields("content", hf -> hf
                        .numberOfFragments(2)
                        .fragmentSize(250)
                )
                .fields("title", hf -> hf
                        .numberOfFragments(0)
                        .noMatchSize(150)  // return first 150 chars when no highlight match
                );
    }

    /**
     * Builds the sort clause.
     * §2.6: explicit sort when sortField is set; null = BM25 default (_score desc).
     *
     * The lambda MUST return ObjectBuilder<SortOptions>, not SortOptions directly —
     * the ES Java client uses builder-chaining and the compiler enforces this.
     */
    private java.util.function.Function<
            co.elastic.clients.elasticsearch._types.SortOptions.Builder,
            co.elastic.clients.util.ObjectBuilder<co.elastic.clients.elasticsearch._types.SortOptions>>
    sortBuilder(SearchParams params) {

        if (!StringUtils.hasText(params.getSortField())) {
            return s -> s.score(sc -> sc.order(SortOrder.Desc));
        }
        return s -> s.field(f -> f
                .field(params.getSortField())
                .order("asc".equalsIgnoreCase(params.getSortOrder())
                        ? SortOrder.Asc : SortOrder.Desc));
    }
}
