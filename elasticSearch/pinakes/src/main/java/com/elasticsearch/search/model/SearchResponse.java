package com.elasticsearch.search.model;

import lombok.Builder;
import lombok.Data;

import java.util.List;

/**
 * Paginated search response returned by the service layer.
 * Includes optional spell-check suggestions and timing metadata.
 */
@Data
@Builder
public class SearchResponse {
    private List<SearchResult> results;
    private long totalCount;
    private int totalPages;
    private int currentPage;
    private int pageSize;
    /** Wall-clock time the ES query took (from the ES took field, ms) */
    private long tookMs;
    /** Spell-check suggestions; null when spellCheck=false */
    private SuggestResponse suggestion;
}
