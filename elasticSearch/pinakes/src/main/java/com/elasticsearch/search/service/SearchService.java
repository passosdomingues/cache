package com.elasticsearch.search.service;

import co.elastic.clients.elasticsearch.core.search.Hit;
import com.elasticsearch.search.client.EsClient;
import com.elasticsearch.search.config.SearchProperties;
import com.elasticsearch.search.model.*;
import com.fasterxml.jackson.databind.node.ObjectNode;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Search orchestration service.
 *
 * Responsibilities:
 * 1. Run QueryAnalyser to detect quoted phrases and spell-corrections.
 * 2. Enrich SearchParams with exactPhrases + fuzzyRemainder before ES call.
 * 3. Delegate to EsClient for all ES I/O (atomic methods).
 * 4. Map ES hits to SearchResult DTOs.
 * 5. Assemble the final SearchResponse.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class SearchService {

    private final EsClient esClient;
    private final QueryAnalyser queryAnalyser;
    private final SearchProperties props;

    private static final int SPARSE_THRESHOLD = 5;

    // ── search ─────────────────────────────────────────────────────────────

    public SearchResponse search(SearchParams params) throws IOException {

        // 1. Analyse query: extract exact phrases + build spell-oracle
        QueryAnalysisResult analysis = null;
        if (params.isSpellCheck()) {
            analysis = queryAnalyser.analyse(
                    params.getQuery(),
                    word -> esClient.suggestWord(word)   // atomic per-word oracle
            );
        }

        // 2. Extract quoted phrases for exact-match ES clauses
        List<String> exactPhrases = queryAnalyser.extractQuotedPhrases(params.getQuery());
        String fuzzyRemainder      = queryAnalyser.stripQuotedPhrases(params.getQuery());
        params.setExactPhrases(exactPhrases.isEmpty() ? null : exactPhrases);
        params.setFuzzyRemainder(fuzzyRemainder.isBlank() ? null : fuzzyRemainder);

        // 3. ES search
        var esResp = esClient.search(params);

        long totalHits  = esResp.hits().total() != null ? esResp.hits().total().value() : 0;
        long tookMs     = esResp.took();
        int  totalPages = (int) Math.ceil((double) totalHits / params.getSize());

        List<SearchResult> results = esResp.hits().hits().stream()
                .map(hit -> mapHit(hit, params.isHighlight()))
                .collect(Collectors.toList());

        log.info("Search '{}' → {} hits in {}ms (page {}/{})",
                params.getQuery(), totalHits, tookMs, params.getPage(), totalPages);

        // 4. Build suggestion: use analysis if available, else trigger on sparse results
        SuggestResponse suggestion = buildSuggestion(params, analysis, totalHits);

        return SearchResponse.builder()
                .results(results)
                .totalCount(totalHits)
                .totalPages(totalPages)
                .currentPage(params.getPage())
                .pageSize(params.getSize())
                .tookMs(tookMs)
                .suggestion(suggestion)
                .build();
    }

    // ── suggest (public — used by API controller) ─────────────────────────

    /**
     * Holistic suggestion for a full query string.
     * Calls the per-word oracle for each token and assembles the result.
     */
    public SuggestResponse suggest(String query, int maxSuggestions) throws IOException {
        QueryAnalysisResult analysis = queryAnalyser.analyse(
                query,
                word -> esClient.suggestWord(word)
        );

        if (!analysis.isHasCorrectedTokens()) {
            return SuggestResponse.builder()
                    .original(query)
                    .suggestions(Collections.emptyList())
                    .hasSuggestion(false)
                    .build();
        }

        return SuggestResponse.builder()
                .original(query)
                .suggestions(List.of(analysis.getCorrectedQuery()))
                .correctedQueryHtml(analysis.getCorrectedQueryHtml())
                .hasSuggestion(true)
                .build();
    }

    // ── autocomplete ───────────────────────────────────────────────────────

    public List<String> autocomplete(String partial, int maxResults) throws IOException {
        return esClient.autocomplete(partial, maxResults).hits().hits().stream()
                .map(Hit::source)
                .filter(Objects::nonNull)
                .filter(src -> src.has("title"))
                .map(src -> src.get("title").asText())
                .collect(Collectors.toList());
    }

    // ── stats ──────────────────────────────────────────────────────────────

    public StatsResponse stats() throws IOException {
        var esResp = esClient.stats();
        long total = esResp.hits().total() != null ? esResp.hits().total().value() : 0;

        double avg = 0, min = 0, max = 0;
        Map<String, Long> distribution = new LinkedHashMap<>();
        Map<String, Long> topLabels    = new LinkedHashMap<>();

        var aggs = esResp.aggregations();
        if (aggs != null) {
            var statsAgg = aggs.get("reading_time_stats");
            if (statsAgg != null) {
                var s = statsAgg.stats();
                avg = s.avg();
                min = s.min();
                max = s.max();
            }
            var rangeAgg = aggs.get("reading_time_ranges");
            if (rangeAgg != null) {
                for (var b : rangeAgg.range().buckets().array())
                    distribution.put(b.key(), b.docCount());
            }
            var termsAgg = aggs.get("top_labels");
            if (termsAgg != null) {
                for (var b : termsAgg.sterms().buckets().array())
                    topLabels.put(b.key().stringValue(), b.docCount());
            }
        }

        return StatsResponse.builder()
                .totalArticles(total)
                .avgReadingTime(avg)
                .minReadingTime(min)
                .maxReadingTime(max)
                .stdDevReadingTime(0)
                .readingTimeDistribution(distribution)
                .topLabels(topLabels)
                .build();
    }

    // ── private helpers ────────────────────────────────────────────────────

    private SearchResult mapHit(Hit<ObjectNode> hit, boolean highlight) {
        ObjectNode src = hit.source();
        String title = src != null && src.has("title") ? src.get("title").asText("") : "";
        String url   = src != null && src.has("url")   ? src.get("url").asText("")   : "";
        int rt = src != null && src.has("reading_time") ? src.get("reading_time").asInt(0) : 0;

        List<String> mq = hit.matchedQueries() != null
                ? new ArrayList<>(hit.matchedQueries())
                : Collections.emptyList();

        return SearchResult.builder()
                .title(title)
                .url(url)
                .abs(esClient.extractAbstract(hit, highlight))
                .readingTime(rt)
                .score(hit.score() != null ? hit.score().floatValue() : 0f)
                .matchedQueries(mq)
                .build();
    }

    /**
     * Determines if we should show a "Did you mean?" suggestion and builds it.
     */
    private SuggestResponse buildSuggestion(SearchParams params,
                                             QueryAnalysisResult analysis,
                                             long totalHits) {
        boolean sparseResults = totalHits <= SPARSE_THRESHOLD;

        if (analysis != null && analysis.isHasCorrectedTokens()) {
            return SuggestResponse.builder()
                    .original(params.getQuery())
                    .suggestions(List.of(analysis.getCorrectedQuery()))
                    .correctedQueryHtml(analysis.getCorrectedQueryHtml())
                    .hasSuggestion(true)
                    .build();
        }

        if (sparseResults && !params.getQuery().isBlank()) {
            try {
                return suggest(params.getQuery(), 3);
            } catch (Exception e) {
                log.warn("Auto-suggest failed: {}", e.getMessage());
            }
        }
        return null;
    }
}
