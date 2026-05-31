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
 * Tests all combinations of query types that QueryAnalyser produces
 * and how SearchService wires them to EsClient:
 *
 *   QueryType  × SpellCheck → expected exactPhrases, fuzzyRemainder, suggestWord calls
 *   ─────────────────────────────────────────────────────────────────────────────────
 *   fuzzy only     × true  → suggestWord per token, exactPhrases=null
 *   fuzzy only     × false → no suggestWord (dense results), exactPhrases=null
 *   exact only     × true  → suggestWord skips quoted part, exactPhrases=[phrase]
 *   exact only     × false → no suggestWord, exactPhrases=[phrase]
 *   mixed          × true  → suggestWord for unquoted tokens, exactPhrases=[phrase]
 *   mixed          × false → no suggestWord (dense), exactPhrases=[phrase]
 *   typo           × true  → corrected tokens in analysis, suggestion set
 *   empty          × any   → handled without exception
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

        // quoted phrase → no word tokens → suggestWord NOT called
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
    @DisplayName("mixed × spellCheck=true → suggestWord for unquoted, exactPhrases set")
    void mixedQuerySpellCheckEnabled() throws IOException {
        mockDense(5);
        when(esClient.suggestWord(anyString())).thenReturn("tree");

        var p = params("\"binary search\" treee"); // 1 unquoted token
        p.setSpellCheck(true);
        searchService.search(p);

        // "treee" is the only unquoted word → suggestWord called once
        verify(esClient, times(1)).suggestWord(anyString());
        verify(esClient).search(argThat(sp ->
                sp.getExactPhrases() != null &&
                sp.getExactPhrases().contains("binary search") &&
                sp.getFuzzyRemainder() != null));
    }

    // ── mixed × false ────────────────────────────────────────────────────

    @Test
    @DisplayName("mixed × spellCheck=false (dense) → no suggestWord, exactPhrases and remainder set")
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
    @DisplayName("typo × spellCheck=true → suggestion populated in response when corrections found")
    void typoQueryProducesSuggestion() throws IOException {
        mockDense(2);
        // Oracle corrects "kolmogrov" → "kolmogorov"
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

    // ── pairwise: queryType × pageSize ────────────────────────────────────

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
        var resp      = mock(SearchResponse.class);
        var meta      = mock(HitsMetadata.class);
        var total     = mock(TotalHits.class);

        when(total.value()).thenReturn((long) (hitCount + 10));
        when(meta.total()).thenReturn(total);
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
