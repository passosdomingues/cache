package com.elasticsearch.search.model;

import lombok.Builder;
import lombok.Data;

import java.util.List;
import java.util.Map;

/**
 * Aggregation statistics from the /stats endpoint.
 * Values are derived from ES metric aggregations (no scoring, size=0).
 */
@Data
@Builder
public class StatsResponse {
    /** Total number of indexed articles */
    private long totalArticles;
    /** Mean reading time in minutes across all articles */
    private double avgReadingTime;
    /** Min reading time */
    private double minReadingTime;
    /** Max reading time */
    private double maxReadingTime;
    /** Std dev of reading time — useful for understanding distribution */
    private double stdDevReadingTime;
    /**
     * Distribution bucketed as: fast (≤5 min), medium (≤10 min), slow (>10 min).
     * Key = label, value = document count.
     */
    private Map<String, Long> readingTimeDistribution;
    /** Top article labels/categories by document count */
    private Map<String, Long> topLabels;
}
