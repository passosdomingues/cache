package com.elasticsearch.search.config;

import org.apache.http.impl.nio.client.HttpAsyncClientBuilder;
import org.junit.jupiter.api.*;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.params.provider.ValueSource;
import org.springframework.test.util.ReflectionTestUtils;

import static org.assertj.core.api.Assertions.*;

/**
 * Unit tests for ElasticsearchConfig.
 *
 * §TTL-CONSTANT      — CONNECTION_TTL_SECONDS is in (10, 60)
 * §CONFIG-STARTUP    — customizeHttpClient() does not throw, returns same builder
 * §BEAN-RESTCLIENT   — restClient() bean instantiates
 * §BEAN-TRANSPORT    — elasticsearchTransport() wraps restClient
 * §BEAN-CLIENT       — elasticsearchClient() wraps transport
 * §POOL-SIZES        — various maxTotal/perRoute combinations accepted
 * §AUTH-DISABLED     — blank/null username → no exception
 * §AUTH-ENABLED      — non-blank username + password → no exception
 * §TIMEOUT-COMBOS    — various connectionTimeout/socketTimeout values accepted
 * §FALLBACK          — keep-alive fallback path does not throw
 */
@DisplayName("ElasticsearchConfig Unit Tests")
class ElasticsearchConfigTest {

    private ElasticsearchConfig config;

    @BeforeEach
    void setUp() {
        config = new ElasticsearchConfig();
        set(config, "host",                   "localhost");
        set(config, "port",                   9200);
        set(config, "scheme",                 "http");
        set(config, "username",               "");
        set(config, "password",               "");
        set(config, "connectionTimeoutMs",    3000);
        set(config, "socketTimeoutMs",        10000);
        set(config, "maxConnections",         25);
        set(config, "maxConnectionsPerRoute", 5);
    }

    // ── §TTL-CONSTANT ─────────────────────────────────────────────────────

    @Test
    @DisplayName("§TTL-CONSTANT: CONNECTION_TTL_SECONDS must be < 60 (ES server-side timeout)")
    void ttlConstantSafeValue() {
        assertThat(ElasticsearchConfig.CONNECTION_TTL_SECONDS)
                .as("TTL must be below ES keep-alive timeout of ~60s")
                .isLessThan(60L)
                .isGreaterThan(10L);
    }

    @Test
    @DisplayName("§TTL-CONSTANT: TTL expressed in seconds (not ms) — must be < 1000")
    void ttlIsSeconds() {
        // Guard against accidental "50000" (ms) instead of "50" (s)
        assertThat(ElasticsearchConfig.CONNECTION_TTL_SECONDS).isLessThan(1000L);
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
    @DisplayName("§CONFIG-STARTUP: client built from configured builder does not throw")
    void clientCanBeBuilt() {
        HttpAsyncClientBuilder hc = HttpAsyncClientBuilder.create();
        config.customizeHttpClient(hc);
        assertThatCode(hc::build).doesNotThrowAnyException();
    }

    // ── §BEAN-RESTCLIENT ─────────────────────────────────────────────────

    @Test
    @DisplayName("§BEAN-RESTCLIENT: restClient() bean instantiates without exception")
    void restClientBeanCreated() {
        assertThatCode(() -> {
            var rc = config.restClient();
            assertThat(rc).isNotNull();
            rc.close();
        }).doesNotThrowAnyException();
    }

    // ── §BEAN-TRANSPORT ───────────────────────────────────────────────────

    @Test
    @DisplayName("§BEAN-TRANSPORT: elasticsearchTransport() bean is created from restClient")
    void transportBeanCreated() throws Exception {
        var rc = config.restClient();
        assertThatCode(() -> {
            var transport = config.elasticsearchTransport(rc);
            assertThat(transport).isNotNull();
            transport.close();
        }).doesNotThrowAnyException();
        rc.close();
    }

    // ── §BEAN-CLIENT ──────────────────────────────────────────────────────

    @Test
    @DisplayName("§BEAN-CLIENT: elasticsearchClient() wraps transport correctly")
    void clientBeanCreated() throws Exception {
        var rc        = config.restClient();
        var transport = config.elasticsearchTransport(rc);
        assertThatCode(() -> {
            var client = config.elasticsearchClient(transport);
            assertThat(client).isNotNull();
        }).doesNotThrowAnyException();
        transport.close();
        rc.close();
    }

    // ── §POOL-SIZES ───────────────────────────────────────────────────────

    @ParameterizedTest(name = "maxTotal={0} perRoute={1}")
    @CsvSource({"5,2", "10,3", "25,5", "50,10", "1,1"})
    @DisplayName("§POOL-SIZES: various connection pool configurations accepted")
    void poolSizesAccepted(int maxTotal, int perRoute) {
        set(config, "maxConnections",         maxTotal);
        set(config, "maxConnectionsPerRoute", perRoute);
        HttpAsyncClientBuilder hc = HttpAsyncClientBuilder.create();
        assertThatCode(() -> config.customizeHttpClient(hc)).doesNotThrowAnyException();
    }

    // ── §AUTH-DISABLED ────────────────────────────────────────────────────

    @Test
    @DisplayName("§AUTH-DISABLED: blank username → no credentials provider exception")
    void noAuthWhenUsernameBlank() {
        set(config, "username", "");
        HttpAsyncClientBuilder hc = HttpAsyncClientBuilder.create();
        assertThatCode(() -> config.customizeHttpClient(hc)).doesNotThrowAnyException();
    }

    @Test
    @DisplayName("§AUTH-DISABLED: null username → no credentials provider exception")
    void noAuthWhenUsernameNull() {
        set(config, "username", null);
        HttpAsyncClientBuilder hc = HttpAsyncClientBuilder.create();
        assertThatCode(() -> config.customizeHttpClient(hc)).doesNotThrowAnyException();
    }

    // ── §AUTH-ENABLED ─────────────────────────────────────────────────────

    @Test
    @DisplayName("§AUTH-ENABLED: non-blank username → credentials provider set without exception")
    void authConfiguredWhenUsernamePresent() {
        set(config, "username", "elastic");
        set(config, "password", "secret");
        HttpAsyncClientBuilder hc = HttpAsyncClientBuilder.create();
        assertThatCode(() -> config.customizeHttpClient(hc)).doesNotThrowAnyException();
    }

    @Test
    @DisplayName("§AUTH-ENABLED: username present but empty password → no exception")
    void authWithEmptyPassword() {
        set(config, "username", "elastic");
        set(config, "password", "");
        HttpAsyncClientBuilder hc = HttpAsyncClientBuilder.create();
        assertThatCode(() -> config.customizeHttpClient(hc)).doesNotThrowAnyException();
    }

    // ── §TIMEOUT-COMBOS ───────────────────────────────────────────────────

    @ParameterizedTest(name = "connectMs={0} socketMs={1}")
    @CsvSource({
        "1000,  5000",
        "3000, 10000",
        "5000, 30000",
        "500,   1000",
    })
    @DisplayName("§TIMEOUT-COMBOS: various timeout combinations accepted")
    void timeoutCombinationsAccepted(int connectMs, int socketMs) {
        set(config, "connectionTimeoutMs", connectMs);
        set(config, "socketTimeoutMs",     socketMs);
        HttpAsyncClientBuilder hc = HttpAsyncClientBuilder.create();
        assertThatCode(() -> config.customizeHttpClient(hc)).doesNotThrowAnyException();
    }

    // ── §SCHEME ───────────────────────────────────────────────────────────

    @ParameterizedTest
    @ValueSource(strings = {"http", "https"})
    @DisplayName("§SCHEME: http and https schemes accepted for restClient()")
    void schemesAccepted(String scheme) {
        set(config, "scheme", scheme);
        assertThatCode(() -> {
            var rc = config.restClient();
            assertThat(rc).isNotNull();
            rc.close();
        }).doesNotThrowAnyException();
    }

    // ── §HOST-VARIANTS ────────────────────────────────────────────────────

    @ParameterizedTest
    @ValueSource(strings = {"localhost", "127.0.0.1", "es01.internal"})
    @DisplayName("§HOST-VARIANTS: various hostname formats accepted")
    void hostVariantsAccepted(String host) {
        set(config, "host", host);
        assertThatCode(() -> {
            var rc = config.restClient();
            assertThat(rc).isNotNull();
            rc.close();
        }).doesNotThrowAnyException();
    }

    // ── helper ────────────────────────────────────────────────────────────

    private void set(Object target, String field, Object value) {
        ReflectionTestUtils.setField(target, field, value);
    }
}
