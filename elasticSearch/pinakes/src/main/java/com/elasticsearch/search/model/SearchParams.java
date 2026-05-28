package com.elasticsearch.search.model;

import jakarta.validation.constraints.*;
import lombok.Data;

import java.util.List;

/**
 * Validated input parameters for a search request.
 *
 * New fields in this version:
 *   exactPhrases    — populated by QueryAnalyser from quoted segments in query
 *   fuzzyRemainder  — the query with quoted segments stripped (for fuzzy pass)
 */
@Data
public class SearchParams {

    @NotBlank(message = "Query must not be blank")
    @Size(min = 2, max = 500, message = "Query must be between 2 and 500 characters")
    private String query;

    @Min(value = 1)
    private int page = 1;

    @Min(value = 1) @Max(value = 50)
    private int size = 10;

    private String fuzziness = "AUTO";

    @DecimalMin("0.0") @DecimalMax("10.0")
    private float phraseBoost = 2.0f;

    @DecimalMin("0.0") @DecimalMax("10.0")
    private float titleBoost = 1.5f;

    @Min(0) @Max(50)
    private int slop = 0;

    private boolean highlight = true;
    private boolean spellCheck = true;

    // ── Filters (§2.3) ────────────────────────────────────────────────────
    @Min(1) private Integer maxReadingTime;
    private String dateFrom;
    private String dateTo;

    // ── Sort (§2.6) ───────────────────────────────────────────────────────
    private String sortField;
    private String sortOrder = "desc";

    // ── Exact phrase support (§busca exata) ───────────────────────────────
    /**
     * Quoted phrases extracted by QueryAnalyser.
     * Populated by SearchService before passing params to EsClient.
     * Not a user-facing request parameter — derived internally.
     */
    private List<String> exactPhrases;

    /**
     * The query with quoted phrases stripped — used for the fuzzy multi_match pass.
     * E.g., input: '"binary search" tree' → fuzzyRemainder: "tree"
     */
    private String fuzzyRemainder;
}
