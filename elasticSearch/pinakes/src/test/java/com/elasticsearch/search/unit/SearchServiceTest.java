package com.elasticsearch.search.unit;

import co.elastic.clients.elasticsearch.core.SearchResponse;
import co.elastic.clients.elasticsearch.core.search.*;
import com.elasticsearch.search.client.EsClient;
import com.elasticsearch.search.config.SearchProperties;
import com.elasticsearch.search.model.*;
import com.elasticsearch.search.service.QueryAnalyser;
import com.elasticsearch.search.service.SearchService;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.*;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.mockito.*;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

/**
 * Unit tests for SearchService — EsClient mocked, no ES instance needed.
 *
 * §SPELL-WIRING      — suggestWord() called per token when spellCheck=true
 * §SPELL-DISABLED    — suggestWord() NOT called when spellCheck=false + dense results
 * §SPELL-SPARSE      — auto-suggest triggered on sparse (≤5) results
 * §SPELL-GRACEFUL    — suggestWord() failure does not propagate as search error
 * §PAGINATION        — totalPages calculated for various total/size combos
 * §MAPPING           — ES hits mapped to SearchResult DTOs correctly
 * §PHRASE-EXTRACT    — exact phrases extracted + set on params before ES call
 * §FUZZY-REMAINDER   — fuzzyRemainder null when query all-quoted
 * §TOOK              — tookMs propagated from ES response
 * §AUTOCOMPLETE      — titles extracted from hits
 * §SUGGEST-API       — suggest() returns hasSuggestion=true on corrections
 * §SUGGEST-NO-OP     — suggest() returns hasSuggestion=false when no corrections
 * §SORT              — sortField/sortOrder forwarded to ES call
 * §FILTER-RT         — maxReadingTime set on params forwarded to ES
 * §FILTER-DATE       — dateFrom/dateTo forwarded to ES call
 * §SUGGESTION-MODEL  — SearchResponse.suggestion populated when corrections found
 * §SUGGESTION-NULL   — SearchResponse.suggestion null when spellCheck=false + dense
 */
@DisplayName("SearchService Unit Tests")
class SearchServiceTest {

    @Mock private EsClient esClient;
    private SearchService searchService;

    private final ObjectMapper mapper = new ObjectMapper();

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        searchService = new SearchService(esClient, new QueryAnalyser(), new SearchProperties());
    }

    // ── §SPELL-WIRING ─────────────────────────────────────────────────────

    @Test
    @DisplayName("§SPELL-WIRING: suggestWord() called once per word token")
    void spellCheckCallsPerToken() throws IOException {
        mockSearch(10, 50);
        when(esClient.suggestWord(anyString())).thenReturn("word");

        var p = params("kolmogrov equatons");
        p.setSpellCheck(true);
        searchService.search(p);

        verify(esClient, times(2)).suggestWord(anyString());
    }

    @Test
    @DisplayName("§SPELL-DISABLED: suggestWord() not called when spellCheck=false + dense")
    void spellCheckSkippedWhenDisabledAndDense() throws IOException {
        mockSearch(10, 100);
        var p = params("binary search");
        p.setSpellCheck(false);
        searchService.search(p);

        verify(esClient, never()).suggestWord(anyString());
    }

    // ── §SPELL-SPARSE ─────────────────────────────────────────────────────

    @Test
    @DisplayName("§SPELL-SPARSE: auto-suggest triggered when totalHits ≤ 5, spellCheck=false")
    void autoSuggestOnSparseResults() throws IOException {
        mockSearch(2, 2);
        when(esClient.suggestWord(anyString())).thenReturn("test");

        var p = params("kolmogrov equatons");
        p.setSpellCheck(false);
        searchService.search(p);

        verify(esClient, atLeastOnce()).suggestWord(anyString());
    }

    @Test
    @DisplayName("§SPELL-SPARSE: auto-suggest NOT triggered when totalHits > 5, spellCheck=false")
    void noAutoSuggestWhenDenseAndDisabled() throws IOException {
        mockSearch(10, 100);
        var p = params("quantum physics");
        p.setSpellCheck(false);
        searchService.search(p);

        verify(esClient, never()).suggestWord(anyString());
    }

    // ── §SPELL-GRACEFUL ───────────────────────────────────────────────────

    @Test
    @DisplayName("§SPELL-GRACEFUL: suggestWord() IOException does not fail the search")
    void spellCheckIoExceptionGraceful() throws IOException {
        mockSearch(10, 50);
        when(esClient.suggestWord(anyString())).thenThrow(new IOException("ES timeout"));

        var p = params("quantum physics");
        p.setSpellCheck(true);

        assertThatCode(() -> searchService.search(p)).doesNotThrowAnyException();
    }

    @Test
    @DisplayName("§SPELL-GRACEFUL: suggestWord() RuntimeException does not fail the search")
    void spellCheckRuntimeExceptionGraceful() throws IOException {
        mockSearch(10, 50);
        when(esClient.suggestWord(anyString())).thenThrow(new RuntimeException("unexpected"));

        var p = params("quantum physics");
        p.setSpellCheck(true);

        assertThatCode(() -> searchService.search(p)).doesNotThrowAnyException();
    }

    // ── §PAGINATION ───────────────────────────────────────────────────────

    @ParameterizedTest(name = "total={0}, size={1}, page={2} → pages={3}")
    @CsvSource({
        "100, 10, 1,  10",
        "101, 10, 1,  11",
        "10,  10, 1,   1",
        "0,   10, 1,   0",
        "1,   10, 1,   1",
        "50,   7, 1,   8",
        "500, 50, 2,  10",
    })
    @DisplayName("§PAGINATION: totalPages math covers boundary and off-by-one cases")
    void paginationMath(long total, int size, int page, int expected) throws IOException {
        mockSearch(Math.min(size, (int) total), total);
        var p = params("test");
        p.setSize(size);
        p.setPage(page);
        p.setSpellCheck(false);

        var resp = searchService.search(p);

        assertThat(resp.getTotalPages()).isEqualTo(expected);
        assertThat(resp.getCurrentPage()).isEqualTo(page);
        assertThat(resp.getTotalCount()).isEqualTo(total);
        assertThat(resp.getPageSize()).isEqualTo(size);
    }

    // ── §MAPPING ─────────────────────────────────────────────────────────

    @Test
    @DisplayName("§MAPPING: hits mapped to SearchResult with title, url, score")
    void hitsAreMappedCorrectly() throws IOException {
        mockSearch(3, 3);
        var p = params("binary search");
        p.setSpellCheck(false);
        p.setHighlight(false);

        var resp = searchService.search(p);

        assertThat(resp.getResults()).hasSize(3);
        for (int i = 0; i < 3; i++) {
            assertThat(resp.getResults().get(i).getTitle()).isEqualTo("Hit " + i);
            assertThat(resp.getResults().get(i).getUrl())
                    .isEqualTo("https://en.wikipedia.org/" + i);
            assertThat(resp.getResults().get(i).getScore()).isEqualTo(1.0f);
        }
    }

    @Test
    @DisplayName("§MAPPING: empty result set maps to empty list, not null")
    void emptyHitsMapsToEmptyList() throws IOException {
        mockSearch(0, 0);
        var p = params("nothing");
        p.setSpellCheck(false);

        var resp = searchService.search(p);
        assertThat(resp.getResults()).isNotNull().isEmpty();
    }

    // ── §PHRASE-EXTRACT ───────────────────────────────────────────────────

    @Test
    @DisplayName("§PHRASE-EXTRACT: quoted phrases extracted and set on params before ES call")
    void exactPhrasesExtracted() throws IOException {
        mockSearch(5, 5);
        when(esClient.suggestWord(anyString())).thenReturn("word");

        var p = params("\"binary search\" tree");
        p.setSpellCheck(false);
        searchService.search(p);

        verify(esClient).search(argThat(sp ->
                sp.getExactPhrases() != null &&
                sp.getExactPhrases().contains("binary search") &&
                "tree".equals(sp.getFuzzyRemainder())
        ));
    }

    @Test
    @DisplayName("§PHRASE-EXTRACT: no quotes → exactPhrases null, fuzzyRemainder null")
    void noQuotesNoPhrases() throws IOException {
        mockSearch(5, 5);
        var p = params("binary search tree");
        p.setSpellCheck(false);
        searchService.search(p);

        verify(esClient).search(argThat(sp ->
                sp.getExactPhrases() == null &&
                sp.getFuzzyRemainder() == null
        ));
    }

    // ── §FUZZY-REMAINDER ─────────────────────────────────────────────────

    @Test
    @DisplayName("§FUZZY-REMAINDER: all-quoted query has fuzzyRemainder null")
    void allQuotedFuzzyRemainderNull() throws IOException {
        mockSearch(3, 3);
        var p = params("\"binary search\"");
        p.setSpellCheck(false);
        searchService.search(p);

        verify(esClient).search(argThat(sp ->
                sp.getExactPhrases() != null &&
                sp.getFuzzyRemainder() == null
        ));
    }

    // ── §TOOK ─────────────────────────────────────────────────────────────

    @Test
    @DisplayName("§TOOK: tookMs from ES response propagated to SearchResponse")
    void tookMsPropagated() throws IOException {
        mockSearchWithTook(10, 42L, 42L);
        var p = params("test");
        p.setSpellCheck(false);

        assertThat(searchService.search(p).getTookMs()).isEqualTo(42L);
    }

    // ── §AUTOCOMPLETE ─────────────────────────────────────────────────────

    @Test
    @DisplayName("§AUTOCOMPLETE: titles extracted from autocomplete hits")
    void autocompleteExtractsTitles() throws IOException {
        var mockResp = buildSearchResponse(3, 3L, 5L);
        when(esClient.autocomplete(anyString(), anyInt())).thenReturn(mockResp);

        var titles = searchService.autocomplete("bin", 5);
        assertThat(titles).hasSize(3);
        assertThat(titles.get(0)).isEqualTo("Hit 0");
    }

    @Test
    @DisplayName("§AUTOCOMPLETE: empty hits → empty list returned")
    void autocompleteEmptyHits() throws IOException {
        var mockResp = buildSearchResponse(0, 0L, 1L);
        when(esClient.autocomplete(anyString(), anyInt())).thenReturn(mockResp);

        assertThat(searchService.autocomplete("xyzzy", 5)).isEmpty();
    }

    // ── §SUGGEST-API ──────────────────────────────────────────────────────

    @Test
    @DisplayName("§SUGGEST-API: suggest() returns hasSuggestion=true when corrections exist")
    void suggestApiReturnsSuggestion() throws IOException {
        when(esClient.suggestWord(eq("kolmogrov"))).thenReturn("kolmogorov");
        when(esClient.suggestWord(eq("equatons"))).thenReturn("equations");

        var resp = searchService.suggest("kolmogrov equatons", 3);
        assertThat(resp.isHasSuggestion()).isTrue();
        assertThat(resp.getSuggestions()).isNotEmpty();
        assertThat(resp.getSuggestions().get(0)).containsIgnoringCase("kolmogorov");
    }

    @Test
    @DisplayName("§SUGGEST-NO-OP: suggest() returns hasSuggestion=false when no corrections")
    void suggestApiNoSuggestionWhenCorrect() throws IOException {
        when(esClient.suggestWord(anyString())).thenAnswer(inv -> inv.getArgument(0));

        var resp = searchService.suggest("binary search", 3);
        assertThat(resp.isHasSuggestion()).isFalse();
        assertThat(resp.getSuggestions()).isEmpty();
    }

    // ── §SORT ─────────────────────────────────────────────────────────────

    @Test
    @DisplayName("§SORT: sortField and sortOrder forwarded to EsClient.search params")
    void sortFieldForwarded() throws IOException {
        mockSearch(5, 5);
        var p = params("test");
        p.setSpellCheck(false);
        p.setSortField("reading_time");
        p.setSortOrder("asc");
        searchService.search(p);

        verify(esClient).search(argThat(sp ->
                "reading_time".equals(sp.getSortField()) &&
                "asc".equals(sp.getSortOrder())
        ));
    }

    // ── §FILTER-RT ────────────────────────────────────────────────────────

    @Test
    @DisplayName("§FILTER-RT: maxReadingTime forwarded to EsClient.search params")
    void readingTimeFilterForwarded() throws IOException {
        mockSearch(5, 5);
        var p = params("test");
        p.setSpellCheck(false);
        p.setMaxReadingTime(5);
        searchService.search(p);

        verify(esClient).search(argThat(sp -> Integer.valueOf(5).equals(sp.getMaxReadingTime())));
    }

    // ── §FILTER-DATE ──────────────────────────────────────────────────────

    @Test
    @DisplayName("§FILTER-DATE: dateFrom/dateTo forwarded to EsClient.search params")
    void dateFilterForwarded() throws IOException {
        mockSearch(5, 5);
        var p = params("test");
        p.setSpellCheck(false);
        p.setDateFrom("2020-01-01");
        p.setDateTo("2023-12-31");
        searchService.search(p);

        verify(esClient).search(argThat(sp ->
                "2020-01-01".equals(sp.getDateFrom()) &&
                "2023-12-31".equals(sp.getDateTo())
        ));
    }

    // ── §SUGGESTION-MODEL ─────────────────────────────────────────────────

    @Test
    @DisplayName("§SUGGESTION-MODEL: SearchResponse.suggestion set when spellCheck=true + corrections")
    void suggestionPopulatedWhenCorrectionFound() throws IOException {
        mockSearch(10, 50);
        when(esClient.suggestWord(eq("kolmogrov"))).thenReturn("kolmogorov");
        when(esClient.suggestWord(eq("equatons"))).thenReturn("equations");

        var p = params("kolmogrov equatons");
        p.setSpellCheck(true);
        var resp = searchService.search(p);

        assertThat(resp.getSuggestion()).isNotNull();
        assertThat(resp.getSuggestion().isHasSuggestion()).isTrue();
    }

    @Test
    @DisplayName("§SUGGESTION-NULL: SearchResponse.suggestion null when spellCheck=false + dense")
    void suggestionNullWhenDisabledAndDense() throws IOException {
        mockSearch(10, 100);
        var p = params("quantum physics");
        p.setSpellCheck(false);
        var resp = searchService.search(p);

        // No correction triggered — suggestion should be null or hasSuggestion=false
        assertThat(resp.getSuggestion() == null ||
                   !resp.getSuggestion().isHasSuggestion()).isTrue();
    }

    // ── helpers ───────────────────────────────────────────────────────────

    private SearchParams params(String query) {
        var p = new SearchParams();
        p.setQuery(query);
        p.setPage(1);
        p.setSize(10);
        p.setFuzziness("AUTO");
        p.setPhraseBoost(2.0f);
        p.setTitleBoost(1.5f);
        p.setSlop(0);
        p.setHighlight(true);
        return p;
    }

    private void mockSearch(int hitCount, long total) throws IOException {
        var resp = buildSearchResponse(hitCount, total, 5L);
        when(esClient.search(any(SearchParams.class))).thenReturn(resp);
        when(esClient.extractAbstract(any(), anyBoolean())).thenReturn("snippet");
    }

    private void mockSearchWithTook(int hitCount, long total, long tookMs) throws IOException {
        var resp = buildSearchResponse(hitCount, total, tookMs);
        when(esClient.search(any(SearchParams.class))).thenReturn(resp);
        when(esClient.extractAbstract(any(), anyBoolean())).thenReturn("snippet");
    }

    @SuppressWarnings("unchecked")
    private SearchResponse<ObjectNode> buildSearchResponse(int hitCount, long total, long tookMs)
            throws IOException {
        var mockResp     = mock(SearchResponse.class);
        var hitsMetadata = mock(HitsMetadata.class);
        var totalHits    = mock(TotalHits.class);

        when(totalHits.value()).thenReturn(total);
        when(hitsMetadata.total()).thenReturn(totalHits);
        when(mockResp.took()).thenReturn(tookMs);

        List<Hit<ObjectNode>> hits = new ArrayList<>();
        for (int i = 0; i < hitCount; i++) {
            var hit = mock(Hit.class);
            ObjectNode src = mapper.createObjectNode();
            src.put("title", "Hit " + i);
            src.put("url",   "https://en.wikipedia.org/" + i);
            src.put("reading_time", 5);
            when(hit.source()).thenReturn(src);
            when(hit.score()).thenReturn(1.0);
            when(hit.highlight()).thenReturn(null);
            when(hit.matchedQueries()).thenReturn(null);
            hits.add(hit);
        }

        when(hitsMetadata.hits()).thenReturn(hits);
        when(mockResp.hits()).thenReturn(hitsMetadata);
        return mockResp;
    }
}
