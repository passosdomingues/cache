package com.elasticsearch.search.service;

import co.elastic.clients.elasticsearch.core.SearchResponse;
import co.elastic.clients.elasticsearch.core.search.Hit;
import co.elastic.clients.elasticsearch.core.search.Suggestion;
import co.elastic.clients.elasticsearch.core.search.TermSuggestOption;
import com.elasticsearch.search.api.model.Result;
import com.elasticsearch.search.api.model.SuggestResponse;
import com.elasticsearch.search.domain.EsClient;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * @brief Core search service that processes Elasticsearch responses
 *        into API model objects.
 *
 * Responsibilities:
 * - Maps raw ES hits to {@link Result} objects with highlight extraction
 * - Computes pagination metadata (totalHits, totalPages) in a single query
 * - Processes Term Suggest responses into {@link SuggestResponse} objects
 */
@Service
public class SearchService {

    private final EsClient esClient;

    public SearchService(EsClient esClient) {
        this.esClient = esClient;
    }

    public com.elasticsearch.search.api.model.SearchResponse search(
            String query, Integer page, Integer pageSize,
            String fuzziness, Float phraseBoost, Float titleBoost,
            Integer slop, Boolean highlight) {
        SearchResponse<ObjectNode> esResponse = esClient.search(
            query, page, pageSize, fuzziness, phraseBoost, titleBoost, slop, highlight
        );

        List<Result> results = esResponse.hits().hits().stream().map(h -> {
            String title   = getField(h, "title");
            String url     = getField(h, "url");
            String content = getField(h, "content");

            /* Prioritize highlighted fragments; fall back to sanitized content */
            String abs = extractHighlight(h, "content");
            if (abs == null || abs.isBlank()) {
                abs = sanitizeContent(content);
            }

            return new Result()
                .abs(abs)
                .title(title)
                .url(url);
        }).collect(Collectors.toList());

        long totalHits = 0L;
        if (esResponse.hits().total() != null) {
            totalHits = esResponse.hits().total().value();
        }

        long totalPages = (totalHits + pageSize - 1) / pageSize;

        com.elasticsearch.search.api.model.SearchResponse response = new com.elasticsearch.search.api.model.SearchResponse();
        response.setResults(results);
        response.setTotalCount((int) totalHits);
        response.setTotalPages((int) totalPages);
        response.setCurrentPage(page);
        response.setPageSize(pageSize);

        return response;
    }

    /**
     * @brief Generates spelling correction suggestions using Elasticsearch Term Suggest.
     *
     * For each token in the query, the suggest API returns correction options
     * ordered by similarity score. Only the top suggestion per token is collected
     * to build the "Did you mean?" feature.
     *
     * @param query The user input potentially containing misspelled words.
     * @param size  Maximum number of suggestions per token.
     * @return A {@link SuggestResponse} with the original text and suggested corrections.
     */
    public SuggestResponse getSuggestions(String query, Integer size) {
        SearchResponse<ObjectNode> response = esClient.suggest(query, size);

        Set<String> suggestions = new LinkedHashSet<>();
        Map<String, List<Suggestion<ObjectNode>>> suggestMap = response.suggest();

        if (suggestMap != null && suggestMap.containsKey("spell_check")) {
            for (Suggestion<ObjectNode> suggestion : suggestMap.get("spell_check")) {
                List<TermSuggestOption> options = suggestion.term().options();
                if (options != null && !options.isEmpty()) {
                    options.stream()
                        .findFirst()
                        .ifPresent(opt -> suggestions.add(opt.text()));
                }
            }
        }

        List<String> suggestionList = new ArrayList<>(suggestions);
        boolean hasSuggestion = !suggestionList.isEmpty();

        SuggestResponse resp = new SuggestResponse();
        resp.setOriginal(query);
        resp.setSuggestions(suggestionList);
        resp.setHasSuggestion(hasSuggestion);
        return resp;
    }

    // ── Private Helpers ─────────────────────────────────────────────────────

    /**
     * @brief Safely extracts a string field from an Elasticsearch hit source.
     *
     * @param hit   The search hit containing the source document.
     * @param field The field name to extract.
     * @return The field value as a string, or an empty string if absent.
     */
    private String getField(Hit<ObjectNode> hit, String field) {
        if (hit.source() == null || !hit.source().has(field)) return "";
        return hit.source().get(field).asText("");
    }

    /**
     * @brief Extracts the first highlight fragment for a given field.
     *
     * Highlight fragments contain matched terms wrapped in {@code <strong>} tags,
     * as configured in the EsClient query builder.
     *
     * @param hit   The search hit potentially containing highlight data.
     * @param field The field name to extract highlights from.
     * @return The first highlight fragment, or null if none available.
     */
    private String extractHighlight(Hit<ObjectNode> hit, String field) {
        if (hit.highlight() == null) return null;
        List<String> fragments = hit.highlight().get(field);
        if (fragments != null && !fragments.isEmpty()) {
            return fragments.get(0);
        }
        return null;
    }

    /**
     * @brief Sanitizes raw content by stripping HTML tags and special characters.
     *
     * Used as a fallback when no highlight fragment is available for a hit.
     *
     * @param content The raw content string from the document source.
     * @return A cleaned string safe for display.
     */
    private String sanitizeContent(String content) {
        if (content == null) return "";
        content = content.replaceAll("</?\\w[^>]*>", "");
        content = content.replaceAll("[^A-Za-z\u00C0-\u00FF\\s.,;:!?()-]+", " ");
        content = content.replaceAll("\\s+", " ");
        return content.trim();
    }
}
