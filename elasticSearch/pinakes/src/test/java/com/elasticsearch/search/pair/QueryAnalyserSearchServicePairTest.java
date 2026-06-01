package com.elasticsearch.search.pair;

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
 * Pairwise tests: QueryAnalyser ↔ SearchService interaction.
 *
 * queryType × spellCheck matrix:
 *   fuzzy-only   × true/false
 *   exact-only   × true/false
 *   mixed        × true/false
 *   typo         × true  → suggestion populated
 *   all-quoted   × true  → no word tokens → suggestWord never called
 *   empty        × any   → no exception
 *
 * Additional:
 *   §CORRECTION-HTML   — correctedQueryHtml forwarded to SuggestResponse
 *   §SPARSE-EXACT      — sparse + exact-phrase: auto-suggest still skipped (no WORD tokens)
 *   §MULTI-PHRASE      — two quoted phrases both set in exactPhrases
 *   §FUZZY-REMAINDER   — mixed query: fuzzyRemainder contains only the unquoted part
 *   §PAIRWISE-SIZE     — queryType × pageSize variations
 *   §PAIRWISE-SORT     — queryType × sort combinations
 */
@DisplayName("Pairwise: QueryAnalyser × SearchService")
class QueryAnalyserSearchServicePairTest {

    @Mock private EsClient esClient;
    private SearchService searchService;
    private final ObjectMapper mapper = new ObjectMapper();

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        searchService = new SearchService(esClient, new QueryAnalyser(), new SearchProperties());
    }

    // ── fuzzy × true ──────────────────────────────────────────────────────

    @Test
    @DisplayName("fuzzy × spellCheck=true → suggestWord called, exactPhrases=null")
    void fuzzyQuerySpellCheckEnabled() throws IOException {
        mockDense(10);
        when(esClient.suggestWord(anyString())).thenReturn("word");

        var p = params("quantum physics"); // 2 tokens
        p.setSpellCheck(true);
        searchService.search(p);

        verify(esClient, times(2)).suggestWord(anyString());
        verify(esClient).search(argThat(sp -> sp.getExactPhrases() == null));
    }

    // ── fuzzy × false ─────────────────────────────────────────────────────

    @Test
    @DisplayName("fuzzy × spellCheck=false (dense) → no suggestWord, exactPhrases=null")
    void fuzzyQuerySpellCheckDisabledDense() throws IOException {
        mockDense(10);
        var p = params("quantum physics");
        p.setSpellCheck(false);
        searchService.search(p);

        verify(esClient, never()).suggestWord(anyString());
        verify(esClient).search(argThat(sp -> sp.getExactPhrases() == null));
    }

    // ── exact × true ─────────────────────────────────────────────────────

    @Test
    @DisplayName("exact × spellCheck=true → quoted part not checked, exactPhrases set")
    void exactQuerySpellCheckEnabled() throws IOException {
        mockDense(5);
        when(esClient.suggestWord(anyString())).thenReturn("word");

        var p = params("\"binary search\"");
        p.setSpellCheck(true);
        searchService.search(p);

        // Quoted phrase only → zero WORD tokens → suggestWord NOT called
        verify(esClient, never()).suggestWord(anyString());
        verify(esClient).search(argThat(sp ->
                sp.getExactPhrases() != null &&
                sp.getExactPhrases().contains("binary search")));
    }

    // ── exact × false ────────────────────────────────────────────────────

    @Test
    @DisplayName("exact × spellCheck=false → no suggestWord, exactPhrases set")
    void exactQuerySpellCheckDisabled() throws IOException {
        mockDense(5);
        var p = params("\"binary search\"");
        p.setSpellCheck(false);
        searchService.search(p);

        verify(esClient, never()).suggestWord(anyString());
        verify(esClient).search(argThat(sp ->
                sp.getExactPhrases() != null &&
                sp.getExactPhrases().contains("binary search")));
    }

    // ── mixed × true ─────────────────────────────────────────────────────

    @Test
    @DisplayName("mixed × spellCheck=true → suggestWord for unquoted only, exactPhrases set")
    void mixedQuerySpellCheckEnabled() throws IOException {
        mockDense(5);
        when(esClient.suggestWord(anyString())).thenReturn("tree");

        var p = params("\"binary search\" treee"); // 1 unquoted token
        p.setSpellCheck(true);
        searchService.search(p);

        verify(esClient, times(1)).suggestWord(anyString());
        verify(esClient).search(argThat(sp ->
                sp.getExactPhrases() != null &&
                sp.getExactPhrases().contains("binary search") &&
                sp.getFuzzyRemainder() != null));
    }

    // ── mixed × false ────────────────────────────────────────────────────

    @Test
    @DisplayName("mixed × spellCheck=false (dense) → no suggestWord, exactPhrases + remainder set")
    void mixedQuerySpellCheckDisabledDense() throws IOException {
        mockDense(10);
        var p = params("\"binary search\" tree");
        p.setSpellCheck(false);
        searchService.search(p);

        verify(esClient, never()).suggestWord(anyString());
        verify(esClient).search(argThat(sp ->
                sp.getExactPhrases() != null &&
                sp.getFuzzyRemainder() != null));
    }

    // ── typo × true ──────────────────────────────────────────────────────

    @Test
    @DisplayName("typo × spellCheck=true → suggestion populated when corrections found")
    void typoQueryProducesSuggestion() throws IOException {
        mockDense(2);
        when(esClient.suggestWord(eq("kolmogrov"))).thenReturn("kolmogorov");
        when(esClient.suggestWord(eq("equatons"))).thenReturn("equations");

        var p = params("kolmogrov equatons");
        p.setSpellCheck(true);
        var resp = searchService.search(p);

        assertThat(resp.getSuggestion()).isNotNull();
        assertThat(resp.getSuggestion().isHasSuggestion()).isTrue();
        assertThat(resp.getSuggestion().getSuggestions().get(0))
                .containsIgnoringCase("kolmogorov");
    }

    // ── all-quoted × true ────────────────────────────────────────────────

    @Test
    @DisplayName("all-quoted × spellCheck=true → suggestWord never called (zero WORD tokens)")
    void allQuotedSpellCheckEnabled() throws IOException {
        mockDense(5);
        when(esClient.suggestWord(anyString())).thenReturn("word");

        var p = params("\"binary search\" \"machine learning\"");
        p.setSpellCheck(true);
        searchService.search(p);

        verify(esClient, never()).suggestWord(anyString());
        verify(esClient).search(argThat(sp ->
                sp.getExactPhrases() != null &&
                sp.getExactPhrases().size() == 2));
    }

    // ── §CORRECTION-HTML ─────────────────────────────────────────────────

    @Test
    @DisplayName("§CORRECTION-HTML: correctedQueryHtml forwarded into SuggestResponse")
    void correctedHtmlForwardedToSuggestion() throws IOException {
        mockDense(2);
        when(esClient.suggestWord(eq("binery"))).thenReturn("binary");
        when(esClient.suggestWord(eq("serach"))).thenReturn("search");

        var p = params("binery serach");
        p.setSpellCheck(true);
        var resp = searchService.search(p);

        assertThat(resp.getSuggestion()).isNotNull();
        assertThat(resp.getSuggestion().getCorrectedQueryHtml())
                .contains("<strong class=\"correction\">");
    }

    // ── §SPARSE-EXACT ─────────────────────────────────────────────────────

    @Test
    @DisplayName("§SPARSE-EXACT: sparse results + all-quoted → auto-suggest has no WORD tokens to correct")
    void sparseResultsWithExactPhraseNoSuggestWord() throws IOException {
        // Total hits = 2 → sparse, but query is all-quoted → no WORD tokens
        mockWithTotal(2, 2);
        when(esClient.suggestWord(anyString())).thenReturn("corrected");

        var p = params("\"binary search\"");
        p.setSpellCheck(false); // disabled but sparse triggers auto-suggest

        searchService.search(p);

        // Even auto-suggest must call suggestWord per word token.
        // "binary search" has 2 words BUT they are in a quoted phrase → not spell-checked.
        // The auto-suggest path calls suggest() → analyse() → oracle for each WORD token.
        // But "\"binary search\"" → QUOTED_PHRASE token only → oracle never called.
        verify(esClient, never()).suggestWord(anyString());
    }

    // ── §MULTI-PHRASE ─────────────────────────────────────────────────────

    @Test
    @DisplayName("§MULTI-PHRASE: two quoted phrases both land in exactPhrases list")
    void multipleQuotedPhrasesExtracted() throws IOException {
        mockDense(5);
        var p = params("\"binary search\" \"machine learning\"");
        p.setSpellCheck(false);
        searchService.search(p);

        verify(esClient).search(argThat(sp ->
                sp.getExactPhrases() != null &&
                sp.getExactPhrases().contains("binary search") &&
                sp.getExactPhrases().contains("machine learning") &&
                sp.getExactPhrases().size() == 2));
    }

    // ── §FUZZY-REMAINDER ─────────────────────────────────────────────────

    @Test
    @DisplayName("§FUZZY-REMAINDER: mixed query → fuzzyRemainder is the unquoted part only")
    void fuzzyRemainderIsUnquotedPart() throws IOException {
        mockDense(5);
        var p = params("\"binary search\" tree algorithm");
        p.setSpellCheck(false);
        searchService.search(p);

        verify(esClient).search(argThat(sp ->
                sp.getFuzzyRemainder() != null &&
                sp.getFuzzyRemainder().contains("tree") &&
                sp.getFuzzyRemainder().contains("algorithm") &&
                !sp.getFuzzyRemainder().contains("binary") &&
                !sp.getFuzzyRemainder().contains("search")));
    }

    // ── §PAIRWISE-SIZE ────────────────────────────────────────────────────

    @ParameterizedTest(name = "query={0} size={1}")
    @CsvSource({
        "'quantum physics',        5",
        "'\"binary search\"',      10",
        "'\"binary search\" tree', 25",
        "'kolmogrov equatons',     10",
    })
    @DisplayName("§PAIRWISE(queryType×size): all query types work across page sizes")
    void queryTypePageSizeCombinations(String query, int size) throws IOException {
        mockDense(size);
        when(esClient.suggestWord(anyString())).thenReturn("corrected");

        var p = params(query);
        p.setSize(size);
        p.setSpellCheck(false);

        assertThatCode(() -> searchService.search(p)).doesNotThrowAnyException();
    }

    // ── §PAIRWISE-SORT ────────────────────────────────────────────────────

    @ParameterizedTest(name = "query={0} sortField={1} sortOrder={2}")
    @CsvSource({
        "'quantum physics',   reading_time, asc",
        "'\"binary search\"', reading_time, desc",
        "'machine learning',  '',           desc",
    })
    @DisplayName("§PAIRWISE(queryType×sort): sort combinations forwarded without error")
    void queryTypeSortCombinations(String query, String sortField, String sortOrder)
            throws IOException {
        mockDense(5);
        var p = params(query);
        p.setSpellCheck(false);
        p.setSortField(sortField.isBlank() ? null : sortField);
        p.setSortOrder(sortOrder);

        assertThatCode(() -> searchService.search(p)).doesNotThrowAnyException();
        verify(esClient, atLeastOnce()).search(any(SearchParams.class));
        clearInvocations(esClient);
    }

    // ── §PAIRWISE-HL ─────────────────────────────────────────────────────

    @ParameterizedTest(name = "query={0} highlight={1} spellCheck={2}")
    @CsvSource({
        "'quantum physics',   true,  true",
        "'quantum physics',   true,  false",
        "'quantum physics',   false, true",
        "'quantum physics',   false, false",
        "'\"binary search\"', true,  false",
        "'\"binary search\"', false, false",
    })
    @DisplayName("§PAIRWISE(query×highlight×spellCheck): all combos run without exception")
    void queryHighlightSpellCheckCombinations(String query, boolean hl, boolean sc)
            throws IOException {
        mockDense(5);
        when(esClient.suggestWord(anyString())).thenReturn("corrected");

        var p = params(query);
        p.setHighlight(hl);
        p.setSpellCheck(sc);

        assertThatCode(() -> searchService.search(p)).doesNotThrowAnyException();
        clearInvocations(esClient);
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
        p.setHighlight(false);
        return p;
    }

    @SuppressWarnings("unchecked")
    private void mockDense(int hitCount) throws IOException {
        mockWithTotal(hitCount, hitCount + 10);
    }

    @SuppressWarnings("unchecked")
    private void mockWithTotal(int hitCount, long total) throws IOException {
        var resp  = mock(SearchResponse.class);
        var meta  = mock(HitsMetadata.class);
        var tot   = mock(TotalHits.class);

        when(tot.value()).thenReturn(total);
        when(meta.total()).thenReturn(tot);
        when(resp.took()).thenReturn(5L);

        List<Hit<ObjectNode>> hits = new ArrayList<>();
        for (int i = 0; i < hitCount; i++) {
            var hit = mock(Hit.class);
            ObjectNode src = mapper.createObjectNode();
            src.put("title", "Hit " + i);
            src.put("url", "https://en.wikipedia.org/" + i);
            src.put("reading_time", 5);
            when(hit.source()).thenReturn(src);
            when(hit.score()).thenReturn(1.0);
            when(hit.highlight()).thenReturn(null);
            when(hit.matchedQueries()).thenReturn(null);
            when(esClient.extractAbstract(eq(hit), anyBoolean())).thenReturn("snippet");
            hits.add(hit);
        }
        when(meta.hits()).thenReturn(hits);
        when(resp.hits()).thenReturn(meta);
        when(esClient.search(any(SearchParams.class))).thenReturn(resp);
    }
}
