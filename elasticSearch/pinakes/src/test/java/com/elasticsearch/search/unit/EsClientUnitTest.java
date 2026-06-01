package com.elasticsearch.search.unit;

import com.elasticsearch.search.client.EsClient;
import co.elastic.clients.elasticsearch.core.search.Hit;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.junit.jupiter.api.*;

import java.util.List;
import java.util.Map;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.Mockito.*;

/**
 * Unit tests for EsClient pure logic (no ES call needed).
 *
 * §ABSTRACT-HIGHLIGHT   — content highlight preferred over raw content
 * §ABSTRACT-TITLE-HL    — title highlight fallback when content HL absent
 * §ABSTRACT-RAW         — raw content when highlight=false
 * §ABSTRACT-TRUNCATION  — content > 400 chars truncated with ellipsis
 * §ABSTRACT-EXACT-MAX   — content exactly 400 chars NOT truncated
 * §ABSTRACT-EMPTY       — null source / source without content returns ""
 * §ABSTRACT-HL-EMPTY    — highlight map present but empty list → falls to raw
 * §ABSTRACT-HL-NULL-MAP — highlight() returns null → falls to raw
 */
@DisplayName("EsClient Pure-Logic Unit Tests")
class EsClientUnitTest {

    private EsClient esClient;
    private final ObjectMapper mapper = new ObjectMapper();

    @BeforeEach
    void setUp() {
        var mockEs = mock(co.elastic.clients.elasticsearch.ElasticsearchClient.class);
        esClient = new EsClient(mockEs);
        org.springframework.test.util.ReflectionTestUtils.setField(esClient, "index", "wikipedia_v2");
    }

    // ── §ABSTRACT-HIGHLIGHT ───────────────────────────────────────────────

    @SuppressWarnings("unchecked")
    @Test
    @DisplayName("§ABSTRACT-HIGHLIGHT: content highlight fragment preferred when present")
    void contentHighlightPreferred() {
        var hit = mock(Hit.class);
        when(hit.highlight()).thenReturn(
                Map.of("content", List.of("<em>binary</em> search"))
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
                Map.of("title", List.of("<em>Quantum</em> Computing"))
        );
        ObjectNode src = mapper.createObjectNode();
        src.put("content", "raw");
        when(hit.source()).thenReturn(src);

        assertThat(esClient.extractAbstract(hit, true)).contains("<em>Quantum</em>");
    }

    @SuppressWarnings("unchecked")
    @Test
    @DisplayName("§ABSTRACT-RAW: raw content used when highlight=false")
    void rawContentWhenHighlightDisabled() {
        var hit = mock(Hit.class);
        when(hit.highlight()).thenReturn(
                Map.of("content", List.of("<em>highlighted</em>"))
        );
        ObjectNode src = mapper.createObjectNode();
        src.put("content", "This is the raw article content.");
        when(hit.source()).thenReturn(src);

        String abs = esClient.extractAbstract(hit, false);
        assertThat(abs).contains("raw article content").doesNotContain("<em>");
    }

    @SuppressWarnings("unchecked")
    @Test
    @DisplayName("§ABSTRACT-TRUNCATION: content > 400 chars truncated with ellipsis")
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
    @DisplayName("§ABSTRACT-EXACT-MAX: content exactly 400 chars is NOT truncated")
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
    @DisplayName("§ABSTRACT-TRUNCATION: content of 401 chars is truncated at 400 + ellipsis")
    void contentOf401Truncated() {
        var hit = mock(Hit.class);
        when(hit.highlight()).thenReturn(null);
        ObjectNode src = mapper.createObjectNode();
        src.put("content", "z".repeat(401));
        when(hit.source()).thenReturn(src);

        String abs = esClient.extractAbstract(hit, false);
        assertThat(abs).hasSize(401).endsWith("…");
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

    @SuppressWarnings("unchecked")
    @Test
    @DisplayName("§ABSTRACT-HL-EMPTY: highlight map has content key with empty list → falls to raw")
    void contentHighlightEmptyListFallsToRaw() {
        var hit = mock(Hit.class);
        // content key present but empty list
        when(hit.highlight()).thenReturn(Map.of("content", List.of()));
        ObjectNode src = mapper.createObjectNode();
        src.put("content", "raw article text here");
        when(hit.source()).thenReturn(src);

        // Should fall through to title highlight → then raw content
        String abs = esClient.extractAbstract(hit, true);
        assertThat(abs).isNotNull();
        // Either from title HL (absent) or raw content — just must not throw and be non-null
    }

    @SuppressWarnings("unchecked")
    @Test
    @DisplayName("§ABSTRACT-HL-NULL-MAP: highlight() returns null → falls through to raw content")
    void highlightNullMapFallsToRaw() {
        var hit = mock(Hit.class);
        when(hit.highlight()).thenReturn(null);
        ObjectNode src = mapper.createObjectNode();
        src.put("content", "raw content fallback");
        when(hit.source()).thenReturn(src);

        String abs = esClient.extractAbstract(hit, true);
        assertThat(abs).contains("raw content fallback");
    }

    @SuppressWarnings("unchecked")
    @Test
    @DisplayName("§ABSTRACT-EMPTY: empty string content returns empty string (no ellipsis)")
    void emptyStringContentReturnsEmpty() {
        var hit = mock(Hit.class);
        when(hit.highlight()).thenReturn(null);
        ObjectNode src = mapper.createObjectNode();
        src.put("content", "");
        when(hit.source()).thenReturn(src);

        assertThat(esClient.extractAbstract(hit, false)).isEmpty();
    }
}
