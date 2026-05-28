package com.elasticsearch.search.config;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.json.jackson.JacksonJsonpMapper;
import co.elastic.clients.transport.ElasticsearchTransport;
import co.elastic.clients.transport.rest_client.RestClientTransport;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import lombok.extern.slf4j.Slf4j;
import org.apache.http.HttpHost;
import org.apache.http.auth.AuthScope;
import org.apache.http.auth.UsernamePasswordCredentials;
import org.apache.http.impl.client.BasicCredentialsProvider;
import org.apache.http.impl.nio.client.HttpAsyncClientBuilder;
import org.elasticsearch.client.RestClient;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.util.StringUtils;

/**
 * Elasticsearch client configuration.
 *
 * ── FIX: org.apache.http.ConnectionClosedException: Connection is closed ──
 *
 * ROOT CAUSE:
 *   Elasticsearch closes idle HTTP keep-alive connections server-side after
 *   ~75 seconds. The Apache HttpAsyncClient pools those connections and tries
 *   to reuse them, resulting in ConnectionClosedException.
 *
 *   NOTE: evictIdleConnections() and evictExpiredConnections() exist only on
 *   the *synchronous* HttpClientBuilder — they are NOT available on
 *   HttpAsyncClientBuilder (httpasyncclient-4.1.5). Using them causes a
 *   compilation error.
 *
 * SOLUTION (two layers, both available in HttpAsyncClientBuilder 4.1.5):
 *
 *   1. setConnectionReuseStrategy(→ false)
 *      Disables HTTP keep-alive connection reuse entirely. Each request gets
 *      a fresh connection that is closed after the response. This eliminates
 *      the stale-connection problem at the cost of a TCP handshake per
 *      request — acceptable for low-to-medium search volumes.
 *
 *   2. setKeepAliveStrategy(→ 55_000 ms)
 *      Belt-and-suspenders: even if keep-alive is somehow negotiated, the
 *      client will not hold the connection beyond 55 s (well under ES's ~75 s
 *      server-side timeout).
 *
 *   3. Resilience4j @Retry(name="esClient") on every EsClient method retries
 *      up to 3× on IOException — catches any transient connection error that
 *      slips through.
 *      (see application.properties: resilience4j.retry.instances.esClient.*)
 */
@Slf4j
@Configuration
public class ElasticsearchConfig {

    @Value("${elasticsearch.host:localhost}")
    private String host;

    @Value("${elasticsearch.port:9200}")
    private int port;

    @Value("${elasticsearch.scheme:http}")
    private String scheme;

    @Value("${elasticsearch.username:}")
    private String username;

    @Value("${elasticsearch.password:}")
    private String password;

    @Value("${elasticsearch.connection-timeout-ms:3000}")
    private int connectionTimeoutMs;

    @Value("${elasticsearch.socket-timeout-ms:15000}")
    private int socketTimeoutMs;

    @Bean
    public RestClient restClient() {
        log.info("Connecting to Elasticsearch at {}://{}:{}", scheme, host, port);

        return RestClient.builder(new HttpHost(host, port, scheme))
            .setRequestConfigCallback(cfg -> cfg
                .setConnectTimeout(connectionTimeoutMs)
                .setSocketTimeout(socketTimeoutMs))
            .setHttpClientConfigCallback(this::configureHttpClient)
            .build();
    }

    /**
     * Configures HttpAsyncClientBuilder (httpasyncclient-4.1.5) to avoid
     * stale-connection errors.
     *
     * Only methods actually present in HttpAsyncClientBuilder are used here.
     * Do NOT call evictIdleConnections() or evictExpiredConnections() — those
     * belong to the synchronous HttpClientBuilder and will not compile.
     */
    private HttpAsyncClientBuilder configureHttpClient(HttpAsyncClientBuilder hc) {

        // Layer 1: disable keep-alive reuse — prevents stale connections entirely.
        // (response, context) -> false  ≡  NoConnectionReuseStrategy.INSTANCE
        hc.setConnectionReuseStrategy((response, context) -> false);

        // Layer 2: even if layer 1 is somehow bypassed, cap keep-alive to 55 s.
        hc.setKeepAliveStrategy((response, context) -> 55_000L);

        // Optional Basic Auth
        if (StringUtils.hasText(username)) {
            var cp = new BasicCredentialsProvider();
            cp.setCredentials(AuthScope.ANY,
                new UsernamePasswordCredentials(username, password));
            hc.setDefaultCredentialsProvider(cp);
            log.info("Elasticsearch basic auth enabled for user '{}'", username);
        }

        return hc;
    }

    @Bean
    public ElasticsearchTransport elasticsearchTransport(RestClient restClient) {
        var mapper = new ObjectMapper().registerModule(new JavaTimeModule());
        return new RestClientTransport(restClient, new JacksonJsonpMapper(mapper));
    }

    @Bean
    public ElasticsearchClient elasticsearchClient(ElasticsearchTransport transport) {
        return new ElasticsearchClient(transport);
    }
}
