package com.elasticsearch.search.unit;

import co.elastic.clients.elasticsearch.core.SearchResponse;
import co.elastic.clients.elasticsearch.core.search.*;
import com.elasticsearch.search.client.EsClient;
import com.elasticsearch.search.config.SearchProperties;
import com.elasticsearch.search.model.*;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.*;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.*;
import org.mockito.*;

import java.io.IOException;
import java.util.List;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

/**
 * Unit tests for SearchService.
 *
 * Strategy: mock EsClient so we test only business logic (mapping, pagination,
 * spell-check wiring) without needing a live ES instance.
 */
@DisplayName("SearchService Unit Tests")
class SearchServiceTest {

    @Mock private EsClient esClient;
    @InjectMocks private com.elasticsearch.search.service.SearchService searchService;

    private SearchProperties props;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        props = new SearchProperties();
    }

    // ── §3.1 spellCheck wiring ─────────────────────────────────────────────

    @Test
    @DisplayName("§3.1 suggest is called when spellCheck=true")
    void suggestCalledWhenSpellCheckEnabled() throws IOException {
        var params = paramsWithQuery("binary serach");
        params.setSpellCheck(true);

        mockSearchResponse(10, 100); // healthy result count
        mockSuggestResponse("binary search");

        searchService.search(params);

        // Ajustado para o método correto que o SearchService consome internamente
        verify(esClient, atLeastOnce()).suggestWord(anyString());
    }

    @Test
    @DisplayName("§3.1 suggest is auto-triggered when results are sparse (≤5)")
    void suggestAutoTriggeredOnSparseResults() throws IOException {
        var params = paramsWithQuery("kolmogrov equatins");
        params.setSpellCheck(false); // explicitly disabled

        mockSearchResponse(2, 2); // only 2 hits → sparse
        mockSuggestResponse("kolmogorov equations");

        var response = searchService.search(params);

        // Mesmo com spellCheck=false, resultados escassos ativam o corretor atômico por token
        verify(esClient, atLeastOnce()).suggestWord(anyString());
    }

    @Test
    @DisplayName("§3.1 suggest failure does NOT propagate as search error")
    void suggestFailureIsGraceful() throws IOException {
        var params = paramsWithQuery("quantum physics");
        params.setSpellCheck(true);

        mockSearchResponse(15, 150);
        when(esClient.suggestWord(anyString())).thenThrow(new IOException("ES timeout"));

        // Não deve estourar exceção; o fluxo deve degradar graciosamente
        assertThatCode(() -> {
            var resp = searchService.search(params);
            assertThat(resp.getSuggestion()).isNull();
        }).doesNotThrowAnyException();
    }

    // ── Pagination math ────────────────────────────────────────────────────

    @ParameterizedTest(name = "total={0}, pageSize={1}, page={2} → expectedPages={3}")
    @CsvSource({
        "100, 10, 1,  10",
        "101, 10, 1,  11",
        "10,  10, 1,  1",
        "0,   10, 1,  0",
        "1,   10, 1,  1",
        "50,  7,  1,  8",
    })
    @DisplayName("Pagination: total pages calculation is correct")
    void paginationMath(long total, int pageSize, int page, int expectedPages)
            throws IOException {
        var params = paramsWithQuery("test");
        params.setSize(pageSize);
        params.setPage(page);
        params.setSpellCheck(false);

        mockSearchResponse(pageSize, total);

        var response = searchService.search(params);
        assertThat(response.getTotalPages()).isEqualTo(expectedPages);
        assertThat(response.getCurrentPage()).isEqualTo(page);
        assertThat(response.getTotalCount()).isEqualTo(total);
    }

    // ── Response mapping ────────────────────────────────────────────────────

    @Test
    @DisplayName("Results are correctly mapped from ES hits")
    void resultsAreMappedCorrectly() throws IOException {
        var params = paramsWithQuery("binary search");
        params.setSpellCheck(false);
        params.setHighlight(false);

        mockSearchResponse(2, 2);

        var response = searchService.search(params);
        assertThat(response.getResults()).hasSize(2);
        assertThat(response.getResults().get(0).getTitle()).isEqualTo("Hit 0");
        assertThat(response.getResults().get(0).getUrl()).isEqualTo("https://en.wikipedia.org/0");
    }

    // ── Helper builders ────────────────────────────────────────────────────

    private SearchParams paramsWithQuery(String query) {
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

    @SuppressWarnings("unchecked")
    private void mockSearchResponse(int hitCount, long totalCount) throws IOException {
        var mockResp = mock(SearchResponse.class);
        var hitsMetadata = mock(HitsMetadata.class);
        var totalHits = mock(TotalHits.class);

        when(totalHits.value()).thenReturn(totalCount);
        when(hitsMetadata.total()).thenReturn(totalHits);
        when(mockResp.took()).thenReturn(5L);

        List<Hit<ObjectNode>> hits = new java.util.ArrayList<>();
        for (int i = 0; i < hitCount; i++) {
            var hit = mock(Hit.class);
            var source = new com.fasterxml.jackson.databind.ObjectMapper().createObjectNode();
            source.put("title", "Hit " + i);
            source.put("url", "https://en.wikipedia.org/" + i);
            source.put("reading_time", 5);
            when(hit.source()).thenReturn(source);
            when(hit.score()).thenReturn(1.0);
            when(hit.highlight()).thenReturn(null);
            when(hit.matchedQueries()).thenReturn(null);
            when(esClient.extractAbstract(eq(hit), anyBoolean())).thenReturn("snippet " + i);
            hits.add(hit);
        }

        when(hitsMetadata.hits()).thenReturn(hits);
        when(mockResp.hits()).thenReturn(hitsMetadata);
        when(esClient.search(any(SearchParams.class))).thenReturn(mockResp);
    }

    private void mockSuggestResponse(String corrected) throws IOException {
        // Mocka a resposta da palavra individualizada
        when(esClient.suggestWord(anyString())).thenReturn(corrected);
        
        var suggestResp = SuggestResponse.builder()
                .original("test")
                .suggestions(List.of(corrected))
                .hasSuggestion(true)
                .build();
        
        var spySvc = Mockito.spy(searchService);
        doReturn(suggestResp).when(spySvc).suggest(anyString(), anyInt());
    }
}
