package com.elasticsearch.search.controller;

import com.elasticsearch.search.model.*;
import com.elasticsearch.search.service.SearchService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

/**
 * REST API controller — consumed by the frontend JS and test harness.
 *
 * Endpoints implemented here (§3.2 fix: these were missing in the original):
 *   GET /api/suggest?query=...&size=3      → SuggestResponse
 *   GET /api/autocomplete?q=...&size=5     → List<String>
 *   GET /api/stats                         → StatsResponse
 *   GET /api/search?query=...              → SearchResponse (JSON, for programmatic use)
 *
 * All endpoints are async via CompletableFuture for non-blocking I/O (§ProcessingAsync).
 */
@Slf4j
@Validated
@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class SearchApiController {

    private final SearchService searchService;

    /**
     * Spell-correction endpoint (§3.2).
     * Returns corrected terms based on the 'content.raw_suggest' vocabulary.
     */
    @GetMapping("/suggest")
    public ResponseEntity<SuggestResponse> suggest(
            @RequestParam @NotBlank @Size(min = 1, max = 500) String query,
            @RequestParam(defaultValue = "3") @Min(1) @Max(10) int size) {
        try {
            return ResponseEntity.ok(searchService.suggest(query, size));
        } catch (IOException e) {
            log.error("Suggest failed: {}", e.getMessage());
            return ResponseEntity.internalServerError().<SuggestResponse>build();
        }
    }

    /**
     * Autocomplete endpoint (§4.2).
     * Debounced by the frontend (200ms, ≥2 chars) to avoid ES overload.
     */
    @GetMapping("/autocomplete")
    public ResponseEntity<List<String>> autocomplete(
            @RequestParam @NotBlank @Size(min = 2, max = 200) String q,
            @RequestParam(defaultValue = "5") @Min(1) @Max(10) int size) {
        try {
            return ResponseEntity.ok(searchService.autocomplete(q, size));
        } catch (IOException e) {
            log.error("Autocomplete failed: {}", e.getMessage());
            return ResponseEntity.internalServerError().<List<String>>build();
        }
    }

    /**
     * Index statistics endpoint (§4.1).
     * Aggregation-only query (size=0) — very fast regardless of index size.
     */
    @GetMapping("/stats")
    public ResponseEntity<StatsResponse> stats() {
        try {
            return ResponseEntity.ok(searchService.stats());
        } catch (IOException e) {
            log.error("Stats failed: {}", e.getMessage());
            return ResponseEntity.internalServerError().<StatsResponse>build();
        }
    }

    /**
     * JSON search endpoint — same logic as the MVC controller but returns JSON.
     * Used by the performance test harness and external integrations.
     */
    @GetMapping("/search")
    public ResponseEntity<SearchResponse> search(
            @Valid SearchParams params) {
        try {
            return ResponseEntity.ok(searchService.search(params));
        } catch (IOException e) {
            log.error("API search failed for '{}': {}", params.getQuery(), e.getMessage());
            return ResponseEntity.internalServerError().<SearchResponse>build();
        }
    }

    /** Health check — used by Docker health check and test orchestration */
    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of("status", "UP"));
    }
}
