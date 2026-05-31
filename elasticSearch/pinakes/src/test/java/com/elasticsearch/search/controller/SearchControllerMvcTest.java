package com.elasticsearch.search.controller;

import com.elasticsearch.search.config.SearchProperties;
import com.elasticsearch.search.model.*;
import com.elasticsearch.search.service.QueryAnalyser;
import com.elasticsearch.search.service.SearchService;
import org.junit.jupiter.api.*;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;
import org.springframework.test.web.servlet.MockMvc;

import java.io.IOException;
import java.util.Collections;
import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * MVC slice tests for SearchController.
 *
 * Uses @WebMvcTest (web layer only, no ES beans).
 * SearchProperties is @MockBean so @ConfigurationProperties binding is skipped.
 * QueryAnalyser is a real bean (pure logic, no dependencies).
 *
 * §HOME        — no-query renders home, service not called
 * §SEARCH-OK   — results model attributes populated
 * §SEARCH-EMPTY — zero results → hasResults=false, no error
 * §SEARCH-ERR  — ES exception → error attribute set
 * §VALIDATION  — invalid params → error attribute, service not called
 * §PHRASE-BADGE — hasExactPhrases flag for quoted queries
 * §PAIRWISE    — highlight × spellCheck × page × queryType combos
 */
@WebMvcTest(SearchController.class)
@Import(QueryAnalyser.class)
@DisplayName("SearchController MVC Tests")
class SearchControllerMvcTest {

    @Autowired MockMvc mvc;
    @MockBean  SearchService searchService;

    /**
     * SearchProperties is @ConfigurationProperties + @Component.
     * @WebMvcTest does not process @ConfigurationProperties by default,
     * so we mock it to avoid a missing-bean error. The controller only calls
     * props.getFuzziness() when params.fuzziness is null — which it never is
     * given SearchParams defaults — so no mock setup is needed.
     */
    @MockBean SearchProperties searchProperties;

    // ── §HOME ─────────────────────────────────────────────────────────────

    @Test
    @DisplayName("§HOME: no query renders home page, service not called")
    void homeRendered() throws Exception {
        mvc.perform(get("/"))
                .andExpect(status().isOk())
                .andExpect(view().name("search/index"))
                .andExpect(model().attribute("hasQuery", false));
        verifyNoInteractions(searchService);
    }

    @Test
    @DisplayName("§HOME: blank query renders home page, service not called")
    void blankQueryIsHome() throws Exception {
        mvc.perform(get("/").param("query", "   "))
                .andExpect(model().attribute("hasQuery", false));
        verifyNoInteractions(searchService);
    }

    // ── §SEARCH-OK ────────────────────────────────────────────────────────

    @Test
    @DisplayName("§SEARCH-OK: results populated in model, hasResults=true")
    void searchResultsInModel() throws Exception {
        when(searchService.search(any())).thenReturn(response(
                List.of(result("Binary Search", "https://en.wikipedia.org/wiki/Binary_search")),
                1L, 1, 100L));

        mvc.perform(get("/").param("query", "binary search"))
                .andExpect(status().isOk())
                .andExpect(view().name("search/index"))
                .andExpect(model().attribute("hasQuery", true))
                .andExpect(model().attribute("hasResults", true))
                .andExpect(model().attribute("totalCount", 1L))
                .andExpect(model().attribute("tookMs", 100L));
    }

    @Test
    @DisplayName("§SEARCH-OK: query and page forwarded to model for form persistence")
    void queryForwardedToModel() throws Exception {
        when(searchService.search(any())).thenReturn(response(List.of(), 0L, 0, 5L));
        mvc.perform(get("/").param("query", "quantum").param("page", "2"))
                .andExpect(model().attribute("query", "quantum"));
    }

    // ── §SEARCH-EMPTY ─────────────────────────────────────────────────────

    @Test
    @DisplayName("§SEARCH-EMPTY: zero hits → hasResults=false, no error attribute")
    void emptyResults() throws Exception {
        when(searchService.search(any())).thenReturn(response(List.of(), 0L, 0, 3L));
        mvc.perform(get("/").param("query", "xyzzy nothing"))
                .andExpect(model().attribute("hasResults", false))
                .andExpect(model().attributeDoesNotExist("error"));
    }

    // ── §SEARCH-ERR ───────────────────────────────────────────────────────

    @Test
    @DisplayName("§SEARCH-ERR: IOException from service → error attribute, hasResults=false")
    void ioExceptionSetsError() throws Exception {
        when(searchService.search(any())).thenThrow(new IOException("ES down"));
        mvc.perform(get("/").param("query", "quantum physics"))
                .andExpect(model().attributeExists("error"))
                .andExpect(model().attribute("hasResults", false));
    }

    @Test
    @DisplayName("§SEARCH-ERR: RuntimeException from service → error attribute")
    void runtimeExceptionSetsError() throws Exception {
        when(searchService.search(any())).thenThrow(new RuntimeException("NPE"));
        mvc.perform(get("/").param("query", "binary search"))
                .andExpect(model().attributeExists("error"))
                .andExpect(model().attribute("hasResults", false));
    }

    // ── §VALIDATION ───────────────────────────────────────────────────────

    @Test
    @DisplayName("§VALIDATION: 1-char query → validation error, service not called")
    void singleCharQueryError() throws Exception {
        mvc.perform(get("/").param("query", "x"))
                .andExpect(model().attributeExists("error"))
                .andExpect(model().attribute("hasResults", false));
        verifyNoInteractions(searchService);
    }

    @Test
    @DisplayName("§VALIDATION: 2-char query passes validation, service is called")
    void twoCharQueryPasses() throws Exception {
        when(searchService.search(any())).thenReturn(response(List.of(), 0L, 0, 1L));
        mvc.perform(get("/").param("query", "AI"))
                .andExpect(model().attributeDoesNotExist("error"));
        verify(searchService).search(any());
    }

    @Test
    @DisplayName("§VALIDATION: page=0 → validation error, service not called")
    void zeroPageError() throws Exception {
        mvc.perform(get("/").param("query", "quantum").param("page", "0"))
                .andExpect(model().attributeExists("error"))
                .andExpect(model().attribute("hasResults", false));
        verifyNoInteractions(searchService);
    }

    // ── §PHRASE-BADGE ─────────────────────────────────────────────────────

    @Test
    @DisplayName("§PHRASE-BADGE: hasExactPhrases=true when query contains double quotes")
    void exactPhraseFlagTrue() throws Exception {
        when(searchService.search(any())).thenReturn(response(List.of(), 0L, 0, 1L));
        mvc.perform(get("/").param("query", "\"binary search\""))
                .andExpect(model().attribute("hasExactPhrases", true));
    }

    @Test
    @DisplayName("§PHRASE-BADGE: hasExactPhrases=false for plain query (no quotes)")
    void exactPhraseFlagFalse() throws Exception {
        when(searchService.search(any())).thenReturn(response(List.of(), 0L, 0, 1L));
        mvc.perform(get("/").param("query", "binary search"))
                .andExpect(model().attribute("hasExactPhrases", false));
    }

    // ── §PAIRWISE ─────────────────────────────────────────────────────────

    /**
     * Pairwise: (highlight, spellCheck) × page × queryType.
     * All 6 combinations reach the service without errors.
     */
    @ParameterizedTest(name = "highlight={0} spellCheck={1} page={2}")
    @CsvSource({
        "true,  true,  1",
        "true,  false, 1",
        "false, true,  1",
        "false, false, 1",
        "true,  true,  2",
        "false, false, 3",
    })
    @DisplayName("§PAIRWISE(highlight×spellCheck×page): all combos → service called, no error")
    void highlightSpellCheckPageCombinations(boolean hl, boolean sc, int page) throws Exception {
        when(searchService.search(any())).thenReturn(response(List.of(), 0L, 0, 1L));
        mvc.perform(get("/")
                        .param("query", "quantum mechanics")
                        .param("highlight",  String.valueOf(hl))
                        .param("spellCheck", String.valueOf(sc))
                        .param("page",       String.valueOf(page)))
                .andExpect(status().isOk())
                .andExpect(model().attributeDoesNotExist("error"));
        verify(searchService, atLeastOnce()).search(any());
        clearInvocations(searchService);
    }

    /**
     * Pairwise: queryType × size parameter combinations.
     */
    @ParameterizedTest(name = "query={0} size={1}")
    @CsvSource({
        "'quantum physics',        5",
        "'\"binary search\"',     10",
        "'kolmogorov equations',  25",
        "'machine learning',       1",
    })
    @DisplayName("§PAIRWISE(queryType×size): various query types and sizes → service called")
    void queryTypeSizeCombinations(String query, int size) throws Exception {
        when(searchService.search(any())).thenReturn(response(List.of(), 0L, 0, 1L));
        mvc.perform(get("/").param("query", query).param("size", String.valueOf(size)))
                .andExpect(status().isOk());
        verify(searchService, atLeastOnce()).search(any());
        clearInvocations(searchService);
    }

    // ── helpers ───────────────────────────────────────────────────────────

    private SearchResponse response(List<SearchResult> r, long total, int pages, long took) {
        return SearchResponse.builder()
                .results(r).totalCount(total).totalPages(pages)
                .currentPage(1).pageSize(10).tookMs(took).build();
    }

    private SearchResult result(String title, String url) {
        return SearchResult.builder()
                .title(title).url(url).abs("snippet")
                .readingTime(5).score(1f)
                .matchedQueries(Collections.emptyList()).build();
    }
}
