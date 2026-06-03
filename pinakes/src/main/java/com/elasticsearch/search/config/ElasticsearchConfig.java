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
import org.apache.http.impl.conn.SystemDefaultDnsResolver;
import org.apache.http.impl.conn.DefaultSchemePortResolver;
import org.apache.http.auth.UsernamePasswordCredentials;
import org.apache.http.config.Registry;
import org.apache.http.config.RegistryBuilder;
import org.apache.http.impl.client.BasicCredentialsProvider;
import org.apache.http.impl.nio.client.HttpAsyncClientBuilder;
import org.apache.http.impl.nio.conn.PoolingNHttpClientConnectionManager;
import org.apache.http.impl.nio.reactor.DefaultConnectingIOReactor;
import org.apache.http.impl.nio.reactor.IOReactorConfig;
import org.apache.http.nio.conn.NoopIOSessionStrategy;
import org.apache.http.nio.conn.SchemeIOSessionStrategy;
import org.apache.http.nio.reactor.IOReactorException;
import org.apache.http.conn.ssl.NoopHostnameVerifier;
import org.apache.http.nio.conn.ssl.SSLIOSessionStrategy;
import org.apache.http.ssl.SSLContextBuilder;
import org.apache.http.ssl.TrustStrategy;
import javax.net.ssl.SSLContext;
import org.elasticsearch.client.RestClient;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.util.StringUtils;

import java.util.concurrent.TimeUnit;

/**
 * Elasticsearch connection configuration.
 *
 * ══ ROOT CAUSE: "Connection is closed" (ConnectionClosedException) ════════
 *
 * org.apache.http.ConnectionClosedException extends IllegalStateException
 * (not IOException), so the original retry-exceptions config did not cover it.
 * Additionally, the Apache NIO connection pool retained connections after
 * Elasticsearch closed them server-side (~60–75 s idle timeout), and the next
 * request received EOF on the stale channel → ConnectionClosedException.
 *
 * ══ FIX: PoolingNHttpClientConnectionManager with timeToLive = 50 s ════════
 *
 * When leasing a connection for a new request, the manager checks:
 *   if (connection_age > timeToLive) → close it, open a fresh one
 *
 * timeToLive = 50 s  <  ES keep-alive timeout (~60–75 s)
 * → stale connections are always evicted before ES closes them.
 *
 * ══ PREVIOUS CRASH: "I/O session factory registry may not be null" ═════════
 *
 * The 6-parameter constructor signature is:
 *   PoolingNHttpClientConnectionManager(
 *       ConnectingIOReactor,
 *       NHttpConnectionFactory,
 *       Lookup<SchemeIOSessionStrategy>,   ← NOT SchemeIOSessionStrategy
 *       DnsResolver, long, TimeUnit)
 *
 * Passing null for the third parameter triggers Args.notNull() → IAE.
 * Fix: build an explicit Registry<SchemeIOSessionStrategy> for HTTP.
 *
 * ══ RESILIENCE4J ═════════════════════════════════════════════════════════
 * ConnectionClosedException (RuntimeException) added explicitly to
 * retry-exceptions in application.properties (single line, no continuation).
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

    @Value("${elasticsearch.socket-timeout-ms:10000}")
    private int socketTimeoutMs;

    @Value("${elasticsearch.max-connections:25}")
    private int maxConnections;

    @Value("${elasticsearch.max-connections-per-route:5}")
    private int maxConnectionsPerRoute;

    /** Connection TTL in seconds — must be less than ES keep-alive timeout. */
    public static final long CONNECTION_TTL_SECONDS = 50L;

    @Bean
    public RestClient restClient() {
        log.info("Connecting to Elasticsearch at {}://{}:{}", scheme, host, port);
        return RestClient.builder(new HttpHost(host, port, scheme))
                .setRequestConfigCallback(this::customizeRequestConfig)
                .setHttpClientConfigCallback(this::customizeHttpClient)
                .build();
    }

    @Bean
    public ElasticsearchTransport elasticsearchTransport(RestClient restClient) {
        ObjectMapper mapper = new ObjectMapper().registerModule(new JavaTimeModule());
        return new RestClientTransport(restClient, new JacksonJsonpMapper(mapper));
    }

    @Bean
    public ElasticsearchClient elasticsearchClient(ElasticsearchTransport transport) {
        return new ElasticsearchClient(transport);
    }

    // ── private helpers ───────────────────────────────────────────────────

    private org.apache.http.client.config.RequestConfig.Builder customizeRequestConfig(
            org.apache.http.client.config.RequestConfig.Builder cfg) {
        return cfg
                .setConnectTimeout(connectionTimeoutMs)
                .setSocketTimeout(socketTimeoutMs);
    }

    /**
     * Configures the Apache HttpAsyncClient:
     *   1. PoolingNHttpClientConnectionManager with timeToLive = 50 s
     *      Fixes the "Connection is closed" stale-connection bug.
     *   2. Optional Basic Auth.
     *
     * The session strategy registry MUST be provided explicitly (not null).
     * We register only "http" → NoopIOSessionStrategy because this app
     * connects to Elasticsearch without TLS in development.
     */
    HttpAsyncClientBuilder customizeHttpClient(HttpAsyncClientBuilder hc) {
        try {
            IOReactorConfig ioConfig = IOReactorConfig.custom()
                    .setConnectTimeout(connectionTimeoutMs)
                    .setSoTimeout(socketTimeoutMs)
                    .build();

            DefaultConnectingIOReactor ioReactor = new DefaultConnectingIOReactor(ioConfig);

            // Trust all certificates SSLContext for development & docker clusters with self-signed certs
            SSLContext sslContext = new SSLContextBuilder()
                    .loadTrustMaterial(null, (TrustStrategy) (chain, authType) -> true)
                    .build();

            SSLIOSessionStrategy sslStrategy = new SSLIOSessionStrategy(
                    sslContext,
                    NoopHostnameVerifier.INSTANCE);

            // Build session strategy registry explicitly to support both HTTP and HTTPS
            Registry<SchemeIOSessionStrategy> sessionRegistry =
                    RegistryBuilder.<SchemeIOSessionStrategy>create()
                            .register("http", NoopIOSessionStrategy.INSTANCE)
                            .register("https", sslStrategy)
                            .build();

            PoolingNHttpClientConnectionManager cm =
                    new PoolingNHttpClientConnectionManager(
                            ioReactor,
                            null,                               // 2. connFactory
                            sessionRegistry,                    // 3. sessionRegistry
                            DefaultSchemePortResolver.INSTANCE, // 4. schemePortResolver (NOVO)
                            SystemDefaultDnsResolver.INSTANCE,  // 5. dnsResolver
                            CONNECTION_TTL_SECONDS, 
                            TimeUnit.SECONDS);

            cm.setMaxTotal(maxConnections);
            cm.setDefaultMaxPerRoute(maxConnectionsPerRoute);
            hc.setConnectionManager(cm);

            log.info("ES connection pool configured (maxTotal={}, perRoute={}, ttl={}s)",
                    maxConnections, maxConnectionsPerRoute, CONNECTION_TTL_SECONDS);

        } catch (Exception e) {
            log.warn("Could not create pooling connection manager ({}). " +
                    "Falling back to keep-alive strategy cap.", e.getMessage());
            hc.setKeepAliveStrategy((response, context) -> CONNECTION_TTL_SECONDS * 1_000L);
        }

        if (StringUtils.hasText(username)) {
            BasicCredentialsProvider cp = new BasicCredentialsProvider();
            cp.setCredentials(AuthScope.ANY,
                    new UsernamePasswordCredentials(username, password));
            hc.setDefaultCredentialsProvider(cp);
            log.info("Elasticsearch basic auth configured for user '{}'", username);
        }

        return hc;
    }
}
