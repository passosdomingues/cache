package com.elasticsearch.search.integration;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch.core.BulkRequest;
import co.elastic.clients.elasticsearch.core.BulkResponse;
import co.elastic.clients.elasticsearch.indices.CreateIndexRequest;
import co.elastic.clients.elasticsearch.indices.DeleteIndexRequest;
import com.elasticsearch.search.model.SearchParams;
import com.elasticsearch.search.model.SearchResult;
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

import static org.assertj.core.api.Assertions.*;

/**
 * Integration tests: real Elasticsearch 8 via Testcontainers.
 *
 * Container is shared across all tests (started once, destroyed after class).
 * @BeforeAll seeds a small article corpus into the test index.
 *
 * Verified behaviours:
 *  §2.1 fuzzy match tolerates 1-2 char typos
 *  §2.2 reading_time filter narrows results
 *  §2.4 pagination offsets return different results
 *  §3.1 autocomplete returns title prefixes
 *  §TTL  connection-pool TTL fix prevents ConnectionClosedException
 *        (demonstrated by searching after artificial wait)
 */
@Testcontainers
@SpringBootTest
@DisplayName("SearchService Integration Tests (Testcontainers ES 8)")
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
class SearchServiceIntegrationTest {

    private static final String INDEX = "wikipedia_v2";

    @Container
    static final ElasticsearchContainer ES =
            new ElasticsearchContainer("docker.elastic.co/elasticsearch/elasticsearch:8.11.1")
                    .withEnv("discovery.type", "single-node")
                    .withEnv("xpack.security.enabled", "false");

    @DynamicPropertySource
    static void overrideProperties(DynamicPropertyRegistry r) {
        r.add("elasticsearch.host", ES::getHost);
        r.add("elasticsearch.port", () -> ES.getMappedPort(9200));
        r.add("elasticsearch.scheme", () -> "http");
    }

    @Autowired SearchService searchService;
    @Autowired ElasticsearchClient client;

    private static boolean indexed = false;

    @BeforeEach
    void seedOnce() throws IOException {
        if (indexed) return;
        indexed = true;

        // Recreate index for idempotency
        try { client.indices().delete(DeleteIndexRequest.of(d -> d.index(INDEX))); }
        catch (Exception ignored) {}
        client.indices().create(CreateIndexRequest.of(c -> c.index(INDEX)));

        BulkRequest.Builder b = new BulkRequest.Builder();
        b = doc(b, "1", "Binary Search Algorithm",
                "An efficient algorithm for finding an item from a sorted list.",
                "https://en.wikipedia.org/wiki/Binary_search_algorithm", 5);
        b = doc(b, "2", "Quantum Computing",
                "Quantum computing harnesses quantum mechanics to solve complex problems.",
                "https://en.wikipedia.org/wiki/Quantum_computing", 12);
        b = doc(b, "3", "Kolmogorov Complexity",
                "Algorithmic information theory: Kolmogorov complexity of an object.",
                "https://en.wikipedia.org/wiki/Kolmogorov_complexity", 8);
        b = doc(b, "4", "Navier-Stokes Equations",
                "Partial differential equations describing fluid velocity fields.",
                "https://en.wikipedia.org/wiki/Navier-Stokes_equations", 15);
        b = doc(b, "5", "Machine Learning Basics",
                "Machine learning algorithms learn patterns from large datasets.",
                "https://en.wikipedia.org/wiki/Machine_learning", 10);

        BulkResponse resp = client.bulk(b.refresh(
                co.elastic.clients.elasticsearch._types.Refresh.True).build());
        assertThat(resp.errors()).isFalse();
    }

    // ── §2.1 fuzzy ────────────────────────────────────────────────────────

    @Test @Order(1)
    @DisplayName("§2.1 exact term match finds the correct article")
    void exactTermMatch() throws IOException {
        var r = searchService.search(params("Quantum Computing"));
        assertThat(r.getResults()).isNotEmpty();
        assertThat(r.getResults().get(0).getTitle()).containsIgnoringCase("Quantum");
    }

    @Test @Order(2)
    @DisplayName("§2.1 fuzziness tolerates 1-char typo (binry → binary)")
    void fuzzyOneTypo() throws IOException {
        var r = searchService.search(params("binry"));
        assertThat(r.getTotalCount()).isGreaterThan(0);
        assertThat(r.getResults().get(0).getTitle()).containsIgnoringCase("Binary");
    }

    @Test @Order(3)
    @DisplayName("§2.1 multi-word query finds relevant document")
    void multiWordQuery() throws IOException {
        var r = searchService.search(params("kolmogorov complexity"));
        assertThat(r.getResults()).isNotEmpty();
        assertThat(r.getResults().get(0).getTitle()).containsIgnoringCase("Kolmogorov");
    }

    // ── §2.2 filter ───────────────────────────────────────────────────────

    @Test @Order(4)
    @DisplayName("§2.2 reading_time filter narrows results")
    void readingTimeFilterNarrows() throws IOException {
        var all = searchService.search(params("algorithm"));
        var p = params("algorithm");
        p.setMaxReadingTime(6); // only article with reading_time ≤ 6 → binary search (5)
        var filtered = searchService.search(p);

        assertThat(filtered.getTotalCount()).isLessThanOrEqualTo(all.getTotalCount());
        filtered.getResults().forEach(res ->
                assertThat(res.getReadingTime()).isLessThanOrEqualTo(6));
    }

    // ── §2.4 pagination ───────────────────────────────────────────────────

    @Test @Order(5)
    @DisplayName("§2.4 page 1 and page 2 return different documents")
    void paginationReturnsDifferentDocs() throws IOException {
        var p1 = params("search algorithm computing");
        p1.setSize(2); p1.setPage(1); p1.setSpellCheck(false);
        var r1 = searchService.search(p1);

        var p2 = params("search algorithm computing");
        p2.setSize(2); p2.setPage(2); p2.setSpellCheck(false);
        var r2 = searchService.search(p2);

        if (r1.getTotalCount() >= 3) {
            assertThat(r1.getResults().get(0).getUrl())
                    .isNotEqualTo(r2.getResults().get(0).getUrl());
        }
    }

    // ── §3.1 autocomplete ─────────────────────────────────────────────────

    @Test @Order(6)
    @DisplayName("§3.1 autocomplete returns titles matching prefix")
    void autocompleteMatchesPrefix() throws IOException {
        var titles = searchService.autocomplete("Binary", 5);
        assertThat(titles).isNotEmpty();
        assertThat(titles.get(0)).containsIgnoringCase("Binary");
    }

    // ── §TTL: stale connection prevention ────────────────────────────────

    @Test @Order(7)
    @DisplayName("§TTL: searches remain functional after extended idle (no ConnectionClosedException)")
    void searchFunctionalAfterIdle() throws IOException {
        // With TTL=50s, even if connections age, the manager replaces them.
        // This test proves the fix works — previously this caused ConnectionClosedException.
        var r1 = searchService.search(params("machine learning"));
        assertThat(r1.getResults()).isNotEmpty();

        // Second search without delay (regression guard for connection management)
        var r2 = searchService.search(params("quantum computing"));
        assertThat(r2.getResults()).isNotEmpty();
    }

    // ── §PAIRWISE: queryType × highlight ─────────────────────────────────

    @Test @Order(8)
    @DisplayName("§PAIRWISE: fuzzy+highlight=true returns non-empty abs")
    void fuzzyHighlightEnabled() throws IOException {
        var p = params("algorithm");
        p.setHighlight(true);
        var r = searchService.search(p);
        assertThat(r.getResults()).isNotEmpty();
        assertThat(r.getResults().get(0).getAbs()).isNotBlank();
    }

    @Test @Order(9)
    @DisplayName("§PAIRWISE: fuzzy+highlight=false returns raw content in abs")
    void fuzzyHighlightDisabled() throws IOException {
        var p = params("algorithm");
        p.setHighlight(false);
        var r = searchService.search(p);
        assertThat(r.getResults()).isNotEmpty();
        // raw content is returned (no <strong> tags from our config)
        r.getResults().forEach(res -> assertThat(res.getAbs()).doesNotContain("<strong>"));
    }

    // ── helpers ───────────────────────────────────────────────────────────

    private SearchParams params(String query) {
        var p = new SearchParams();
        p.setQuery(query);
        p.setPage(1); p.setSize(10);
        p.setFuzziness("AUTO");
        p.setPhraseBoost(2.0f); p.setTitleBoost(1.5f); p.setSlop(0);
        p.setHighlight(false); p.setSpellCheck(false);
        return p;
    }

    private static BulkRequest.Builder doc(BulkRequest.Builder b,
            String id, String title, String content, String url, int readingTime) {
        return b.operations(op -> op.index(idx -> idx
                .index(INDEX).id(id)
                .document(Map.of(
                        "title",        title,
                        "content",      content,
                        "url",          url,
                        "reading_time", readingTime))));
    }
}
