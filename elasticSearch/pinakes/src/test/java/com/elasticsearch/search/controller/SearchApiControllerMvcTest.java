package com.elasticsearch.search.controller;

import com.elasticsearch.search.model.*;
import com.elasticsearch.search.service.SearchService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.*;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.params.provider.ValueSource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.io.IOException;
import java.util.*;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * MVC slice tests for SearchApiController (REST endpoints).
 *
 * GlobalExceptionHandler imported so ConstraintViolationException → 400.
 *
 * §SUGGEST-OK        — /api/suggest returns 200 + SuggestResponse JSON
 * §SUGGEST-NO-RESULT — /api/suggest no correction → hasSuggestion=false
 * §SUGGEST-ERR       — /api/suggest IOException → 500
 * §SUGGEST-VALID     — blank/over-500-char query → 400
 * §AUTOCOMPLETE-OK   — /api/autocomplete returns 200 + string array
 * §AUTOCOMPLETE-ERR  — /api/autocomplete IOException → 500
 * §AUTOCOMPLETE-VALID— 1-char or blank q → 400
 * §STATS-OK          — /api/stats returns 200 + StatsResponse JSON
 * §STATS-ERR         — /api/stats IOException → 500
 * §SEARCH-API-OK     — /api/search returns 200 + SearchResponse JSON
 * §SEARCH-API-VALID  — invalid params → 400
 * §SEARCH-API-ERR    — /api/search IOException → 500
 * §HEALTH            — /api/health returns 200 + {status:UP}
 * §PAIRWISE          — suggest/autocomplete/search size + queryType combos
 */
@WebMvcTest(SearchApiController.class)
@Import(GlobalExceptionHandler.class)
@DisplayName("SearchApiController MVC Tests")
class SearchApiControllerMvcTest {

    @Autowired MockMvc mvc;
    @MockBean  SearchService searchService;

    private final ObjectMapper mapper = new ObjectMapper();

    // ── §SUGGEST-OK ───────────────────────────────────────────────────────

    @Test
    @DisplayName("§SUGGEST-OK: /api/suggest returns 200 + hasSuggestion=true JSON")
    void suggestOk() throws Exception {
        when(searchService.suggest(eq("kolmogrov"), anyInt())).thenReturn(
                SuggestResponse.builder()
                        .original("kolmogrov")
                        .suggestions(List.of("kolmogorov"))
                        .correctedQueryHtml("<strong>kolmogorov</strong>")
                        .hasSuggestion(true)
                        .build());

        mvc.perform(get("/api/suggest").param("query", "kolmogrov"))
                .andExpect(status().isOk())
                .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$.hasSuggestion").value(true))
                .andExpect(jsonPath("$.original").value("kolmogrov"))
                .andExpect(jsonPath("$.suggestions[0]").value("kolmogorov"));
    }

    @Test
    @DisplayName("§SUGGEST-NO-RESULT: no correction → hasSuggestion=false")
    void suggestNoResult() throws Exception {
        when(searchService.suggest(anyString(), anyInt())).thenReturn(
                SuggestResponse.builder()
                        .original("binary")
                        .suggestions(Collections.emptyList())
                        .hasSuggestion(false)
                        .build());

        mvc.perform(get("/api/suggest").param("query", "binary"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.hasSuggestion").value(false));
    }

    @Test
    @DisplayName("§SUGGEST-ERR: IOException → 500")
    void suggestIoException() throws Exception {
        when(searchService.suggest(anyString(), anyInt())).thenThrow(new IOException("ES down"));
        mvc.perform(get("/api/suggest").param("query", "test query"))
                .andExpect(status().isInternalServerError());
    }

    @Test
    @DisplayName("§SUGGEST-VALID: blank query → 400")
    void suggestBlankQuery() throws Exception {
        mvc.perform(get("/api/suggest").param("query", ""))
                .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("§SUGGEST-VALID: query over 500 chars → 400")
    void suggestQueryTooLong() throws Exception {
        mvc.perform(get("/api/suggest").param("query", "a".repeat(501)))
                .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("§SUGGEST-VALID: missing query param → 400")
    void suggestMissingQuery() throws Exception {
        mvc.perform(get("/api/suggest"))
                .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("§SUGGEST-VALID: size=0 → 400 (min=1)")
    void suggestSizeZero() throws Exception {
        mvc.perform(get("/api/suggest")
                .param("query", "test query")
                .param("size", "0"))
                .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("§SUGGEST-VALID: size=11 → 400 (max=10)")
    void suggestSizeTooLarge() throws Exception {
        mvc.perform(get("/api/suggest")
                .param("query", "test query")
                .param("size", "11"))
                .andExpect(status().isBadRequest());
    }

    // ── §AUTOCOMPLETE-OK ──────────────────────────────────────────────────

    @Test
    @DisplayName("§AUTOCOMPLETE-OK: /api/autocomplete returns 200 + string array")
    void autocompleteOk() throws Exception {
        when(searchService.autocomplete(eq("bin"), anyInt()))
                .thenReturn(List.of("Binary Search", "Binary Tree", "Binomial Theorem"));

        mvc.perform(get("/api/autocomplete").param("q", "bin"))
                .andExpect(status().isOk())
                .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$[0]").value("Binary Search"))
                .andExpect(jsonPath("$.length()").value(3));
    }

    @Test
    @DisplayName("§AUTOCOMPLETE-OK: empty result returns empty array (not null)")
    void autocompleteEmpty() throws Exception {
        when(searchService.autocomplete(anyString(), anyInt())).thenReturn(Collections.emptyList());
        mvc.perform(get("/api/autocomplete").param("q", "xyzzy"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.length()").value(0));
    }

    @Test
    @DisplayName("§AUTOCOMPLETE-ERR: IOException → 500")
    void autocompleteIoException() throws Exception {
        when(searchService.autocomplete(anyString(), anyInt())).thenThrow(new IOException("ES down"));
        mvc.perform(get("/api/autocomplete").param("q", "bi"))
                .andExpect(status().isInternalServerError());
    }

    @Test
    @DisplayName("§AUTOCOMPLETE-VALID: 1-char query → 400 (min=2)")
    void autocompleteOneCharQuery() throws Exception {
        mvc.perform(get("/api/autocomplete").param("q", "b"))
                .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("§AUTOCOMPLETE-VALID: blank q → 400")
    void autocompleteBlankQuery() throws Exception {
        mvc.perform(get("/api/autocomplete").param("q", ""))
                .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("§AUTOCOMPLETE-VALID: missing q param → 400")
    void autocompleteMissingParam() throws Exception {
        mvc.perform(get("/api/autocomplete"))
                .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("§AUTOCOMPLETE-VALID: size=11 → 400 (max=10)")
    void autocompleteSizeTooLarge() throws Exception {
        mvc.perform(get("/api/autocomplete")
                .param("q", "bi")
                .param("size", "11"))
                .andExpect(status().isBadRequest());
    }

    // ── §STATS-OK ─────────────────────────────────────────────────────────

    @Test
    @DisplayName("§STATS-OK: /api/stats returns 200 + StatsResponse JSON")
    void statsOk() throws Exception {
        when(searchService.stats()).thenReturn(
                StatsResponse.builder()
                        .totalArticles(5000L)
                        .avgReadingTime(8.5)
                        .minReadingTime(1.0)
                        .maxReadingTime(45.0)
                        .stdDevReadingTime(0)
                        .readingTimeDistribution(Map.of("fast", 1000L, "medium", 2000L, "slow", 2000L))
                        .topLabels(Map.of("Science", 300L, "Technology", 250L))
                        .build());

        mvc.perform(get("/api/stats"))
                .andExpect(status().isOk())
                .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$.totalArticles").value(5000))
                .andExpect(jsonPath("$.avgReadingTime").value(8.5));
    }

    @Test
    @DisplayName("§STATS-ERR: IOException → 500")
    void statsIoException() throws Exception {
        when(searchService.stats()).thenThrow(new IOException("ES down"));
        mvc.perform(get("/api/stats"))
                .andExpect(status().isInternalServerError());
    }

    // ── §SEARCH-API-OK ────────────────────────────────────────────────────

    @Test
    @DisplayName("§SEARCH-API-OK: /api/search returns 200 + SearchResponse JSON")
    void searchApiOk() throws Exception {
        when(searchService.search(any())).thenReturn(
                SearchResponse.builder()
                        .results(List.of(SearchResult.builder()
                                .title("Quantum Computing")
                                .url("https://en.wikipedia.org/wiki/Quantum_computing")
                                .abs("Abstract text")
                                .readingTime(10)
                                .score(1.5f)
                                .matchedQueries(Collections.emptyList())
                                .build()))
                        .totalCount(1L).totalPages(1)
                        .currentPage(1).pageSize(10).tookMs(25L)
                        .build());

        mvc.perform(get("/api/search").param("query", "quantum computing"))
                .andExpect(status().isOk())
                .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$.totalCount").value(1))
                .andExpect(jsonPath("$.results[0].title").value("Quantum Computing"))
                .andExpect(jsonPath("$.tookMs").value(25));
    }

    @Test
    @DisplayName("§SEARCH-API-OK: tookMs propagated in JSON response")
    void searchApiTookMsPropagated() throws Exception {
        when(searchService.search(any())).thenReturn(
                SearchResponse.builder()
                        .results(Collections.emptyList())
                        .totalCount(0L).totalPages(0)
                        .currentPage(1).pageSize(10).tookMs(77L)
                        .build());

        mvc.perform(get("/api/search").param("query", "quantum physics"))
                .andExpect(jsonPath("$.tookMs").value(77));
    }

    @Test
    @DisplayName("§SEARCH-API-VALID: 1-char query → 400")
    void searchApiOneCharQuery() throws Exception {
        mvc.perform(get("/api/search").param("query", "x"))
                .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("§SEARCH-API-VALID: missing query param → 400")
    void searchApiMissingQuery() throws Exception {
        mvc.perform(get("/api/search"))
                .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("§SEARCH-API-VALID: size=51 → 400 (max=50)")
    void searchApiSizeOverMax() throws Exception {
        mvc.perform(get("/api/search")
                .param("query", "quantum")
                .param("size", "51"))
                .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("§SEARCH-API-VALID: page=0 → 400 (min=1)")
    void searchApiPageZero() throws Exception {
        mvc.perform(get("/api/search")
                .param("query", "quantum")
                .param("page", "0"))
                .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("§SEARCH-API-ERR: IOException → 500")
    void searchApiIoException() throws Exception {
        when(searchService.search(any())).thenThrow(new IOException("ES down"));
        mvc.perform(get("/api/search").param("query", "quantum physics"))
                .andExpect(status().isInternalServerError());
    }

    // ── §HEALTH ───────────────────────────────────────────────────────────

    @Test
    @DisplayName("§HEALTH: /api/health returns 200 + {status:UP}")
    void healthEndpoint() throws Exception {
        mvc.perform(get("/api/health"))
                .andExpect(status().isOk())
                .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$.status").value("UP"));
    }

    @Test
    @DisplayName("§HEALTH: /api/health does not require any params")
    void healthNoParamsNeeded() throws Exception {
        mvc.perform(get("/api/health"))
                .andExpect(status().isOk());
        verifyNoInteractions(searchService);
    }

    // ── §PAIRWISE ─────────────────────────────────────────────────────────

    @ParameterizedTest(name = "size={0}")
    @ValueSource(ints = {1, 3, 10})
    @DisplayName("§PAIRWISE: /api/suggest valid size boundary values → 200")
    void suggestSizeBoundaries(int size) throws Exception {
        when(searchService.suggest(anyString(), eq(size))).thenReturn(
                SuggestResponse.builder().original("test")
                        .suggestions(Collections.emptyList()).hasSuggestion(false).build());

        mvc.perform(get("/api/suggest")
                .param("query", "test query")
                .param("size", String.valueOf(size)))
                .andExpect(status().isOk());
    }

    @ParameterizedTest(name = "size={0}")
    @ValueSource(ints = {1, 5, 10})
    @DisplayName("§PAIRWISE: /api/autocomplete valid size boundary values → 200")
    void autocompleteSizeBoundaries(int size) throws Exception {
        when(searchService.autocomplete(anyString(), eq(size)))
                .thenReturn(Collections.emptyList());

        mvc.perform(get("/api/autocomplete")
                .param("q", "bi")
                .param("size", String.valueOf(size)))
                .andExpect(status().isOk());
    }

    @ParameterizedTest(name = "query={0}")
    @CsvSource({
        "'quantum physics'",
        "'\"binary search\"'",
        "'machine learning algorithms'",
    })
    @DisplayName("§PAIRWISE: /api/search various query types → 200")
    void searchApiQueryTypes(String query) throws Exception {
        when(searchService.search(any())).thenReturn(
                SearchResponse.builder()
                        .results(Collections.emptyList())
                        .totalCount(0L).totalPages(0)
                        .currentPage(1).pageSize(10).tookMs(1L)
                        .build());

        mvc.perform(get("/api/search").param("query", query))
                .andExpect(status().isOk());
    }

    @ParameterizedTest(name = "highlight={0} spellCheck={1} page={2} size={3}")
    @CsvSource({
        "true,  true,  1, 10",
        "false, false, 1,  5",
        "true,  false, 2, 25",
        "false, true,  1, 50",
    })
    @DisplayName("§PAIRWISE: /api/search highlight×spellCheck×page×size combos → 200")
    void searchApiParamCombinations(boolean hl, boolean sc, int page, int size) throws Exception {
        when(searchService.search(any())).thenReturn(
                SearchResponse.builder()
                        .results(Collections.emptyList())
                        .totalCount(0L).totalPages(0)
                        .currentPage(page).pageSize(size).tookMs(1L)
                        .build());

        mvc.perform(get("/api/search")
                .param("query", "quantum computing")
                .param("highlight", String.valueOf(hl))
                .param("spellCheck", String.valueOf(sc))
                .param("page", String.valueOf(page))
                .param("size", String.valueOf(size)))
                .andExpect(status().isOk());
        clearInvocations(searchService);
    }
}
