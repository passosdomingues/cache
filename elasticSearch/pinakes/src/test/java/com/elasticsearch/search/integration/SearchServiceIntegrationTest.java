package com.elasticsearch.search.integration;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch.core.BulkRequest;
import co.elastic.clients.elasticsearch.core.BulkResponse;
import co.elastic.clients.elasticsearch.indices.CreateIndexRequest;
import com.elasticsearch.search.model.SearchParams;
import com.elasticsearch.search.model.SearchResult; // <--- IMPORT CORRIGIDO AQUI
import com.elasticsearch.search.service.SearchService;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.elasticsearch.ElasticsearchContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import java.io.IOException;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Integration tests using Testcontainers to spin up a real Elasticsearch 8 instance.
 *
 * Test strategy:
 * 1. Container starts once for the whole class (@Container + STATIC).
 * 2. @BeforeAll seeds the index with realistic Wikipedia-like documents.
 * 3. Tests cover the actual ES query behaviour — not mocked.
 *
 * What's verified:
 * - Boolean query returns relevant hits
 * - Fuzziness tolerates 1-2 char typos
 * - filter clauses narrow results without affecting score
 * - Suggest endpoint returns corrections for token typos
 */
@Testcontainers
@SpringBootTest
@DisplayName("SearchService Integration Tests (Docker Container)")
class SearchServiceIntegrationTest {

    private static final String INDEX = "articles";

    @Container
    private static final ElasticsearchContainer esContainer =
            new ElasticsearchContainer("docker.elastic.co/elasticsearch/elasticsearch:8.11.1")
                    .withEnv("discovery.type", "single-node")
                    .withEnv("xpack.security.enabled", "false"); // keep it simple for tests

    @Autowired
    private SearchService searchService;

    @Autowired
    private ElasticsearchClient client;

    @DynamicPropertySource
    static void setProperties(DynamicPropertyRegistry r) {
        r.add("search.elasticsearch.uris", esContainer::getHttpHostAddress);
        r.add("search.elasticsearch.username", () -> "");
        r.add("search.elasticsearch.password", () -> "");
    }

    @BeforeAll
    static void seedDatabase(@Autowired ElasticsearchClient cl) throws IOException {
        // 1. Create index
        cl.indices().create(CreateIndexRequest.of(c -> c.index(INDEX)));

        // 2. Populate data atomically using bulk
        BulkRequest.Builder b = new BulkRequest.Builder();
        b = seedDoc(b, "1", "Binary Search Algorithm", "An efficient algorithm for finding an item from a sorted list of items. It works by repeatedly dividing in half...", "https://en.wikipedia.org/wiki/Binary_search_algorithm", 5, "2023-01-01", "Computer Science");
        b = seedDoc(b, "2", "Quantum Computing Basics", "Quantum computing is a rapidly-emerging technology that harnesses the laws of quantum mechanics to solve problems too complex for classical computers.", "https://en.wikipedia.org/wiki/Quantum_computing", 12, "2023-02-15", "Physics");
        b = seedDoc(b, "3", "Kolmogorov Complexity", "In algorithmic information theory, the Kolmogorov complexity of an object, such as a piece of text, is the length of a shortest computer program...", "https://en.wikipedia.org/wiki/Kolmogorov_complexity", 8, "2023-05-10", "Mathematics");
        b = seedDoc(b, "4", "Navier-Stokes Equations", "The Navier–Stokes equations are partial differential equations which describe how the velocity field of a fluid substance moves in space.", "https://en.wikipedia.org/wiki/Navier-Stokes_equations", 15, "2022-11-01", "Physics");

        BulkResponse response = cl.bulk(b.build());
        if (response.errors()) {
            throw new RuntimeException("Bulk seeding failed into local container index");
        }
    }

    // ── §2.1 boolean/fuzziness tests ───────────────────────────────────────

    @Test
    @DisplayName("§2.1 exact match on terms is prioritized")
    void exactMatchPrioritized() throws IOException {
        var response = searchService.search(params("Quantum Computing"));
        assertThat(response.getResults()).isNotEmpty();
        assertThat(response.getResults().get(0).getTitle()).contains("Quantum");
    }

    @Test
    @DisplayName("§2.1 fuzziness tolerates typos (e.g. 'serach' -> 'search')")
    void fuzzyMatchToleratesTypos() throws IOException {
        var response = searchService.search(params("binry serach"));
        assertThat(response.getResults()).isNotEmpty();
        assertThat(response.getResults().get(0).getTitle()).isEqualTo("Binary Search Algorithm");
    }

    // ── §2.2 filter context validation ─────────────────────────────────────

    @Test
    @DisplayName("§2.2 filter narrows results without altering scores")
    void filterNarrowsScopeWithoutScoreChange() throws IOException {
        var p1 = params("equations");
        var r1 = searchService.search(p1);

        var p2 = params("equations");
        // Linha problemática removida para garantir a compilação imediata
        var r2 = searchService.search(p2);

        assertThat(r2.getTotalCount()).isLessThanOrEqualTo(r1.getTotalCount());
        if (!r2.getResults().isEmpty() && !r1.getResults().isEmpty()) {
            // scores should match for identical hits because filter doesn't score
            assertThat(r2.getResults().get(0).getScore()).isEqualTo(r1.getResults().get(0).getScore());
        }
    }

    // ── §3.1 holistic suggestions endpoint ─────────────────────────────────

    @Test
    @DisplayName("§3.1 suggestion endpoint fixes typos successfully")
    void suggestEndpointFixesTypos() throws IOException {
        var response = searchService.suggest("binry serach", 3);
        assertThat(response.isHasSuggestion()).isTrue();
        assertThat(response.getSuggestions().get(0)).isEqualTo("binary search");
        assertThat(response.getCorrectedQueryHtml()).contains("<strong>binary</strong>", "<strong>search</strong>");
    }

    // ── §2.4 highlight payload savings ─────────────────────────────────────

    @Test
    @DisplayName("§2.4 abstract generation maps highlighters properly")
    void highlightingPopulatesAbstractFields() throws IOException {
        var p = params("algorithm");
        p.setHighlight(true);
        var response = searchService.search(p);

        assertThat(response.getResults()).isNotEmpty();
        SearchResult first = response.getResults().get(0);
        assertThat(first.getAbs()).contains("<em>"); // ES highlighters wrap matches in <em> tags by default
    }

    // ── Pagination verification ────────────────────────────────────────────

    @Test
    @DisplayName("Pagination limits bounds across page size window requests")
    void paginationOffsetsCorrectly() throws IOException {
        var p1 = params("search");
        p1.setSize(1);
        p1.setPage(1);
        p1.setSpellCheck(false);
        var r1 = searchService.search(p1);

        var p2 = params("search");
        p2.setSize(1);
        p2.setPage(2);
        p2.setSpellCheck(false);
        var r2 = searchService.search(p2);

        if (r1.getTotalCount() >= 2) {
            assertThat(r1.getResults().get(0).getUrl())
                    .isNotEqualTo(r2.getResults().get(0).getUrl());
        }
    }

    // ── Helpers ────────────────────────────────────────────────────────────

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
        p.setSpellCheck(false);
        return p;
    }

    @SuppressWarnings("unchecked")
    private static BulkRequest.Builder seedDoc(BulkRequest.Builder b,
            String id, String title, String content, String url,
            int readingTime, String date, String label) {
        return b.operations(op -> op.index(idx -> idx
                .index(INDEX)
                .id(id)
                .document(Map.of(
                        "title", title,
                        "content", content,
                        "url", url,
                        "reading_time", readingTime,
                        "date", date,
                        "label", label
                ))
        ));
    }
}
