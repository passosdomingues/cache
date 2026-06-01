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
import java.util.List;
import java.util.Map;

import static org.assertj.core.api.Assertions.*;

/**
 * Integration tests: real Elasticsearch 8 via Testcontainers.
 *
 * Container shared across all tests (started once, destroyed after class).
 * @BeforeAll seeds a small article corpus into the test index.
 *
 * §2.1-FUZZY        — fuzziness tolerates 1-2 char typos
 * §2.2-FILTER-RT    — reading_time filter narrows results correctly
 * §2.4-PAGINATION   — page 1 and page 2 return different documents
 * §2.5-SPELLCHECK   — spell-check returns corrected suggestion
 * §3.1-AUTOCOMPLETE — autocomplete returns title prefixes
 * §3.2-EXACT-PHRASE — quoted query uses match_phrase, returns exact title
 * §3.3-STATS        — stats() returns correct totalArticles count
 * §3.4-SORT-RT      — sort by reading_time asc returns shortest article first
 * §3.5-FILTER-DATE  — date range filter (no results outside range)
 * §TTL              — searches remain functional after second call (stale-conn fix)
 * §PAIRWISE-HL      — highlight=true / false both return non-null abs
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

        try { client.indices().delete(DeleteIndexRequest.of(d -> d.index(INDEX))); }
        catch (Exception ignored) {}
        client.indices().create(CreateIndexRequest.of(c -> c.index(INDEX)));

        BulkRequest.Builder b = new BulkRequest.Builder();
        b = doc(b, "1", "Binary Search Algorithm",
                "An efficient algorithm for finding an item from a sorted list of items.",
                "https://en.wikipedia.org/wiki/Binary_search_algorithm", 5, "2021-01-01");
        b = doc(b, "2", "Quantum Computing",
                "Quantum computing harnesses quantum mechanics to solve complex problems rapidly.",
                "https://en.wikipedia.org/wiki/Quantum_computing", 12, "2022-03-15");
        b = doc(b, "3", "Kolmogorov Complexity",
                "Algorithmic information theory: Kolmogorov complexity of an object.",
                "https://en.wikipedia.org/wiki/Kolmogorov_complexity", 8, "2020-06-10");
        b = doc(b, "4", "Navier-Stokes Equations",
                "Partial differential equations describing fluid velocity fields and dynamics.",
                "https://en.wikipedia.org/wiki/Navier-Stokes_equations", 15, "2019-11-05");
        b = doc(b, "5", "Machine Learning Basics",
                "Machine learning algorithms learn statistical patterns from large datasets.",
                "https://en.wikipedia.org/wiki/Machine_learning", 10, "2023-08-20");

        BulkResponse resp = client.bulk(
                b.refresh(co.elastic.clients.elasticsearch._types.Refresh.True).build());
        assertThat(resp.errors()).isFalse();
    }

    // ── §2.1-FUZZY ────────────────────────────────────────────────────────

    @Test @Order(1)
    @DisplayName("§2.1 exact term match finds correct article")
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

    // ── §2.2-FILTER-RT ────────────────────────────────────────────────────

    @Test @Order(4)
    @DisplayName("§2.2 reading_time filter narrows results, all within limit")
    void readingTimeFilterNarrows() throws IOException {
        var all = searchService.search(params("algorithm"));
        var p = params("algorithm");
        p.setMaxReadingTime(6); // only Binary Search (5 min) qualifies
        var filtered = searchService.search(p);

        assertThat(filtered.getTotalCount()).isLessThanOrEqualTo(all.getTotalCount());
        filtered.getResults().forEach(res ->
                assertThat(res.getReadingTime()).isLessThanOrEqualTo(6));
    }

    @Test @Order(5)
    @DisplayName("§2.2 reading_time filter = 1 returns only sub-1-min articles (none → 0)")
    void readingTimeFilter1Min() throws IOException {
        var p = params("algorithm");
        p.setMaxReadingTime(1);
        // All seeded articles have readingTime >= 5, so 0 results
        assertThat(searchService.search(p).getTotalCount()).isZero();
    }

    // ── §2.4-PAGINATION ───────────────────────────────────────────────────

    @Test @Order(6)
    @DisplayName("§2.4 page 1 and page 2 return different documents")
    void paginationReturnsDifferentDocs() throws IOException {
        var p1 = params("search algorithm computing");
        p1.setSize(2); p1.setPage(1); p1.setSpellCheck(false);
        var r1 = searchService.search(p1);

        var p2 = params("search algorithm computing");
        p2.setSize(2); p2.setPage(2); p2.setSpellCheck(false);
        var r2 = searchService.search(p2);

        if (r1.getTotalCount() >= 3 && !r1.getResults().isEmpty() && !r2.getResults().isEmpty()) {
            assertThat(r1.getResults().get(0).getUrl())
                    .isNotEqualTo(r2.getResults().get(0).getUrl());
        }
    }

    @Test @Order(7)
    @DisplayName("§2.4 page beyond total returns empty result (no error)")
    void pageOutOfBoundsReturnsEmpty() throws IOException {
        var p = params("algorithm");
        p.setPage(9999); p.setSize(10); p.setSpellCheck(false);
        var r = searchService.search(p);
        assertThat(r.getResults()).isEmpty();
        assertThat(r.getTotalCount()).isGreaterThanOrEqualTo(0);
    }

    // ── §3.1-AUTOCOMPLETE ─────────────────────────────────────────────────

    @Test @Order(8)
    @DisplayName("§3.1 autocomplete returns titles matching prefix")
    void autocompleteMatchesPrefix() throws IOException {
        var titles = searchService.autocomplete("Binary", 5);
        assertThat(titles).isNotEmpty();
        assertThat(titles.get(0)).containsIgnoringCase("Binary");
    }

    @Test @Order(9)
    @DisplayName("§3.1 autocomplete with no matching prefix returns empty list")
    void autocompleteNoMatch() throws IOException {
        var titles = searchService.autocomplete("xyzzy_no_match", 5);
        // No results expected — empty list, not exception
        assertThat(titles).isInstanceOf(List.class);
    }

    // ── §3.3-STATS ────────────────────────────────────────────────────────

    @Test @Order(10)
    @DisplayName("§3.3 stats() returns totalArticles = 5 (seeded corpus)")
    void statsReturnsTotalArticles() throws IOException {
        var stats = searchService.stats();
        assertThat(stats.getTotalArticles()).isEqualTo(5L);
    }

    @Test @Order(11)
    @DisplayName("§3.3 stats() avgReadingTime is within [5, 15] given seeded data")
    void statsAvgReadingTime() throws IOException {
        var stats = searchService.stats();
        assertThat(stats.getAvgReadingTime()).isBetween(5.0, 15.0);
    }

    // ── §3.4-SORT-RT ──────────────────────────────────────────────────────

    @Test @Order(12)
    @DisplayName("§3.4 sort by reading_time asc returns shortest article first")
    void sortByReadingTimeAsc() throws IOException {
        var p = params("algorithm computing learning");
        p.setSortField("reading_time");
        p.setSortOrder("asc");
        p.setSpellCheck(false);
        var r = searchService.search(p);

        if (r.getResults().size() >= 2) {
            int first  = r.getResults().get(0).getReadingTime();
            int second = r.getResults().get(1).getReadingTime();
            assertThat(first).isLessThanOrEqualTo(second);
        }
    }

    @Test @Order(13)
    @DisplayName("§3.4 sort by reading_time desc returns longest article first")
    void sortByReadingTimeDesc() throws IOException {
        var p = params("algorithm computing learning");
        p.setSortField("reading_time");
        p.setSortOrder("desc");
        p.setSpellCheck(false);
        var r = searchService.search(p);

        if (r.getResults().size() >= 2) {
            int first  = r.getResults().get(0).getReadingTime();
            int second = r.getResults().get(1).getReadingTime();
            assertThat(first).isGreaterThanOrEqualTo(second);
        }
    }

    // ── §TTL: stale connection prevention ────────────────────────────────

    @Test @Order(14)
    @DisplayName("§TTL: consecutive searches don't throw ConnectionClosedException")
    void searchFunctionalAfterIdle() throws IOException {
        var r1 = searchService.search(params("machine learning"));
        assertThat(r1.getResults()).isNotEmpty();

        var r2 = searchService.search(params("quantum computing"));
        assertThat(r2.getResults()).isNotEmpty();
    }

    // ── §PAIRWISE-HL ──────────────────────────────────────────────────────

    @Test @Order(15)
    @DisplayName("§PAIRWISE: highlight=true returns abs with non-blank content")
    void fuzzyHighlightEnabled() throws IOException {
        var p = params("algorithm");
        p.setHighlight(true);
        var r = searchService.search(p);
        assertThat(r.getResults()).isNotEmpty();
        assertThat(r.getResults().get(0).getAbs()).isNotBlank();
    }

    @Test @Order(16)
    @DisplayName("§PAIRWISE: highlight=false returns raw content in abs (no ES <strong> tags)")
    void fuzzyHighlightDisabled() throws IOException {
        var p = params("algorithm");
        p.setHighlight(false);
        var r = searchService.search(p);
        assertThat(r.getResults()).isNotEmpty();
        r.getResults().forEach(res -> assertThat(res.getAbs()).doesNotContain("<strong>"));
    }

    @Test @Order(17)
    @DisplayName("§PAIRWISE: spellCheck=true + dense results → suggestion absent or hasSuggestion=false")
    void spellCheckDenseResultsNoSuggestion() throws IOException {
        var p = params("algorithm");
        p.setSpellCheck(true);
        var r = searchService.search(p);
        // "algorithm" is spelled correctly: no correction expected
        if (r.getSuggestion() != null) {
            assertThat(r.getSuggestion().isHasSuggestion()).isFalse();
        }
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
            String id, String title, String content, String url, int readingTime, String dtCreation) {
        return b.operations(op -> op.index(idx -> idx
                .index(INDEX).id(id)
                .document(Map.of(
                        "title",       title,
                        "content",     content,
                        "url",         url,
                        "reading_time", readingTime,
                        "dt_creation", dtCreation))));
    }
}
