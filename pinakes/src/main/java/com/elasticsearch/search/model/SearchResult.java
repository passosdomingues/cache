package com.elasticsearch.search.model;

import lombok.Builder;
import lombok.Data;

import java.util.List;

/**
 * Internal DTO for a single search hit.
 * Keeps service layer decoupled from the ES wire format.
 */
@Data
@Builder
public class SearchResult {
    /** Article title (field: title) */
    private String title;
    /** Wikipedia URL (field: url) */
    private String url;
    /**
     * Highlighted abstract from ES highlight API.
     * When highlight=false, this is the raw content excerpt.
     * Either way, at most {@code fragmentSize} characters to avoid huge payloads.
     */
    private String abs;
    /** Estimated reading time in minutes (field: reading_time) */
    private Integer readingTime;
    /** BM25 relevance score from Elasticsearch */
    private Float score;
    /** Named queries that matched — used for ranking analytics */
    private List<String> matchedQueries;
}
