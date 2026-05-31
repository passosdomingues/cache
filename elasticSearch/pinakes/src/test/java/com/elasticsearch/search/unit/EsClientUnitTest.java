package com.elasticsearch.search.unit;

import com.elasticsearch.search.client.EsClient;
import co.elastic.clients.elasticsearch.core.search.Hit;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.*;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.Mockito.*;

/**
 * Unit tests for EsClient pure logic (no ES call needed):
 *  §ABSTRACT-HIGHLIGHT   — content highlight preferred over raw content
 *  §ABSTRACT-TITLE-HL    — title highlight used when content highlight absent
 *  §ABSTRACT-RAW         — raw content used when highlight=false
 *  §ABSTRACT-TRUNCATION  — long content truncated at 400 chars + ellipsis
 *  §ABSTRACT-EMPTY       — empty source returns empty string
 */
@DisplayName("EsClient Pure-Logic Unit Tests")
class EsClientUnitTest {

    private EsClient esClient;
    private final ObjectMapper mapper = new ObjectMapper();

    @BeforeEach
    void setUp() throws Exception {
        // EsClient requires an ElasticsearchClient — we don't test ES calls here,
        // so we inject a mock and only exercise extractAbstract (no IO).
        var mockEs = mock(co.elastic.clients.elasticsearch.ElasticsearchClient.class);
        esClient = new EsClient(mockEs);
        // inject index value
        org.springframework.test.util.ReflectionTestUtils.setField(esClient, "index", "wikipedia_v2");
    }

    // ── §ABSTRACT-HIGHLIGHT ───────────────────────────────────────────────

    @SuppressWarnings("unchecked")
    @Test
    @DisplayName("§ABSTRACT-HIGHLIGHT: content highlight fragment preferred when present")
    void contentHighlightPreferred() {
        var hit = mock(Hit.class);
        when(hit.highlight()).thenReturn(
                java.util.Map.of("content", java.util.List.of("<em>binary</em> search"))
        );
        ObjectNode src = mapper.createObjectNode();
        src.put("content", "raw content should not be used");
        when(hit.source()).thenReturn(src);

        String abs = esClient.extractAbstract(hit, true);
        assertThat(abs).contains("<em>binary</em>").doesNotContain("raw content");
    }

    @SuppressWarnings("unchecked")
    @Test
    @DisplayName("§ABSTRACT-TITLE-HL: title highlight used when content highlight absent")
    void titleHighlightFallback() {
        var hit = mock(Hit.class);
        when(hit.highlight()).thenReturn(
                java.util.Map.of("title", java.util.List.of("<em>Quantum</em> Computing"))
        );
        ObjectNode src = mapper.createObjectNode();
        src.put("content", "raw");
        when(hit.source()).thenReturn(src);

        String abs = esClient.extractAbstract(hit, true);
        assertThat(abs).contains("<em>Quantum</em>");
    }

    @SuppressWarnings("unchecked")
    @Test
    @DisplayName("§ABSTRACT-RAW: raw content used when highlight=false")
    void rawContentWhenHighlightDisabled() {
        var hit = mock(Hit.class);
        when(hit.highlight()).thenReturn(
                java.util.Map.of("content", java.util.List.of("<em>highlighted</em>"))
        );
        ObjectNode src = mapper.createObjectNode();
        src.put("content", "This is the raw article content.");
        when(hit.source()).thenReturn(src);

        String abs = esClient.extractAbstract(hit, false);
        assertThat(abs).contains("raw article content").doesNotContain("<em>");
    }

    @SuppressWarnings("unchecked")
    @Test
    @DisplayName("§ABSTRACT-TRUNCATION: content > 400 chars is truncated with ellipsis")
    void longContentTruncated() {
        var hit = mock(Hit.class);
        when(hit.highlight()).thenReturn(null);
        ObjectNode src = mapper.createObjectNode();
        src.put("content", "x".repeat(600));
        when(hit.source()).thenReturn(src);

        String abs = esClient.extractAbstract(hit, false);
        assertThat(abs).hasSize(401).endsWith("…");
    }

    @SuppressWarnings("unchecked")
    @Test
    @DisplayName("§ABSTRACT-TRUNCATION: content exactly 400 chars is NOT truncated")
    void exactlyMaxLengthNotTruncated() {
        var hit = mock(Hit.class);
        when(hit.highlight()).thenReturn(null);
        ObjectNode src = mapper.createObjectNode();
        src.put("content", "y".repeat(400));
        when(hit.source()).thenReturn(src);

        String abs = esClient.extractAbstract(hit, false);
        assertThat(abs).doesNotEndWith("…").hasSize(400);
    }

    @SuppressWarnings("unchecked")
    @Test
    @DisplayName("§ABSTRACT-EMPTY: null source returns empty string")
    void nullSourceReturnsEmpty() {
        var hit = mock(Hit.class);
        when(hit.highlight()).thenReturn(null);
        when(hit.source()).thenReturn(null);

        assertThat(esClient.extractAbstract(hit, false)).isEmpty();
    }

    @SuppressWarnings("unchecked")
    @Test
    @DisplayName("§ABSTRACT-EMPTY: source without content field returns empty string")
    void sourceWithoutContentReturnsEmpty() {
        var hit = mock(Hit.class);
        when(hit.highlight()).thenReturn(null);
        ObjectNode src = mapper.createObjectNode();
        src.put("title", "Title only");
        when(hit.source()).thenReturn(src);

        assertThat(esClient.extractAbstract(hit, false)).isEmpty();
    }
}
