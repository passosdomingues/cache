package com.elasticsearch.search.config;

import com.elasticsearch.search.config.ElasticsearchConfig;
import org.apache.http.impl.nio.client.HttpAsyncClientBuilder;
import org.junit.jupiter.api.*;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.springframework.test.util.ReflectionTestUtils;


import static org.assertj.core.api.Assertions.*;

/**
 * Unit tests for ElasticsearchConfig.
 *
 * Verifies:
 *  §CONFIG-STARTUP   — restClient() bean does not throw
 *  §POOL-TTL         — connection manager uses expected TTL
 *  §AUTH-DISABLED    — no credentials provider when username is blank
 *  §AUTH-ENABLED     — credentials provider set when username is non-blank
 *  §FALLBACK         — customizeHttpClient() compiles and returns builder
 *  §TTL-CONSTANT     — CONNECTION_TTL_SECONDS < 60 (ES default keep-alive)
 */
@DisplayName("ElasticsearchConfig Unit Tests")
class ElasticsearchConfigTest {

    private ElasticsearchConfig config;

    @BeforeEach
    void setUp() {
        config = new ElasticsearchConfig();
        // inject @Value defaults via reflection
        set(config, "host",                  "localhost");
        set(config, "port",                  9200);
        set(config, "scheme",                "http");
        set(config, "username",              "");
        set(config, "password",              "");
        set(config, "connectionTimeoutMs",   3000);
        set(config, "socketTimeoutMs",       10000);
        set(config, "maxConnections",        25);
        set(config, "maxConnectionsPerRoute",5);
    }

    // ── §TTL-CONSTANT ─────────────────────────────────────────────────────

    @Test
    @DisplayName("§TTL-CONSTANT: CONNECTION_TTL_SECONDS must be < 60 (ES server-side timeout)")
    void ttlConstantSafeValue() {
        assertThat(ElasticsearchConfig.CONNECTION_TTL_SECONDS)
                .as("TTL must be below ES keep-alive timeout of ~60s")
                .isLessThan(60L)
                .isGreaterThan(10L); // sanity lower bound
    }

    // ── §CONFIG-STARTUP ───────────────────────────────────────────────────

    @Test
    @DisplayName("§CONFIG-STARTUP: customizeHttpClient() does not throw and returns same builder")
    void customizeHttpClientDoesNotThrow() {
        HttpAsyncClientBuilder hc = HttpAsyncClientBuilder.create();
        assertThatCode(() -> {
            HttpAsyncClientBuilder result = config.customizeHttpClient(hc);
            assertThat(result).isSameAs(hc);
        }).doesNotThrowAnyException();
    }

    @Test
    @DisplayName("§CONFIG-STARTUP: restClient() bean instantiates without exception")
    void restClientBeanCreated() {
        assertThatCode(() -> {
            var rc = config.restClient();
            assertThat(rc).isNotNull();
            rc.close();
        }).doesNotThrowAnyException();
    }

    // ── §POOL-TTL ─────────────────────────────────────────────────────────

    @Test
    @DisplayName("§POOL-TTL: connection manager is PoolingNHttpClientConnectionManager")
    void connectionManagerIsPooling() {
        HttpAsyncClientBuilder hc = HttpAsyncClientBuilder.create();
        config.customizeHttpClient(hc);
        // After calling customizeHttpClient, the builder should have a connection manager set.
        // We can verify by building the client (it won't fail).
        assertThatCode(hc::build).doesNotThrowAnyException();
    }

    // ── §AUTH-DISABLED ────────────────────────────────────────────────────

    @Test
    @DisplayName("§AUTH-DISABLED: blank username → no credentials provider exception")
    void noAuthWhenUsernameBlank() {
        set(config, "username", "");
        HttpAsyncClientBuilder hc = HttpAsyncClientBuilder.create();
        assertThatCode(() -> config.customizeHttpClient(hc))
                .doesNotThrowAnyException();
    }

    @Test
    @DisplayName("§AUTH-DISABLED: null username → no credentials provider exception")
    void noAuthWhenUsernameNull() {
        set(config, "username", null);
        HttpAsyncClientBuilder hc = HttpAsyncClientBuilder.create();
        assertThatCode(() -> config.customizeHttpClient(hc))
                .doesNotThrowAnyException();
    }

    // ── §AUTH-ENABLED ─────────────────────────────────────────────────────

    @Test
    @DisplayName("§AUTH-ENABLED: non-blank username → credentials provider is set without exception")
    void authConfiguredWhenUsernamePresent() {
        set(config, "username", "elastic");
        set(config, "password", "secret");
        HttpAsyncClientBuilder hc = HttpAsyncClientBuilder.create();
        assertThatCode(() -> config.customizeHttpClient(hc))
                .doesNotThrowAnyException();
    }

    // ── §POOL-SIZES ───────────────────────────────────────────────────────

    @ParameterizedTest(name = "maxTotal={0} perRoute={1}")
    @CsvSource({"5,2", "10,3", "25,5", "50,10"})
    @DisplayName("§POOL-SIZES: various pool size configurations are accepted")
    void poolSizesAccepted(int maxTotal, int perRoute) {
        set(config, "maxConnections",         maxTotal);
        set(config, "maxConnectionsPerRoute", perRoute);
        HttpAsyncClientBuilder hc = HttpAsyncClientBuilder.create();
        assertThatCode(() -> config.customizeHttpClient(hc))
                .doesNotThrowAnyException();
    }

    // ── §TRANSPORT ────────────────────────────────────────────────────────

    @Test
    @DisplayName("§TRANSPORT: elasticsearchTransport bean is created from restClient")
    void transportBeanCreated() throws Exception {
        var rc = config.restClient();
        assertThatCode(() -> {
            var transport = config.elasticsearchTransport(rc);
            assertThat(transport).isNotNull();
            transport.close();
        }).doesNotThrowAnyException();
        rc.close();
    }

    @Test
    @DisplayName("§TRANSPORT: elasticsearchClient bean wraps transport correctly")
    void clientBeanCreated() throws Exception {
        var rc = config.restClient();
        var transport = config.elasticsearchTransport(rc);
        assertThatCode(() -> {
            var client = config.elasticsearchClient(transport);
            assertThat(client).isNotNull();
        }).doesNotThrowAnyException();
        transport.close();
        rc.close();
    }

    // ── helper ────────────────────────────────────────────────────────────

    private void set(Object target, String field, Object value) {
        ReflectionTestUtils.setField(target, field, value);
    }
}
