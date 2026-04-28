package com.elasticsearch.search.domain;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch._types.query_dsl.Query;
import co.elastic.clients.elasticsearch.core.SearchResponse;
import co.elastic.clients.json.jackson.JacksonJsonpMapper;
import co.elastic.clients.transport.ElasticsearchTransport;
import co.elastic.clients.transport.rest_client.RestClientTransport;
import com.fasterxml.jackson.databind.node.ObjectNode;
import nl.altindag.ssl.SSLFactory;
import org.apache.http.HttpHost;
import org.apache.http.auth.AuthScope;
import org.apache.http.auth.UsernamePasswordCredentials;
import org.apache.http.client.CredentialsProvider;
import org.apache.http.impl.client.BasicCredentialsProvider;
import org.apache.http.impl.nio.client.HttpAsyncClientBuilder;
import org.elasticsearch.client.RestClient;
import org.springframework.stereotype.Component;

import java.io.IOException;

/**
 * @brief Low-level Elasticsearch client responsible for query execution.
 *
 * Encapsulates the connection setup (HTTPS + basic auth) and provides
 * two query methods against the Wikipedia index:
 * <ul>
 *   <li>{@link #search} -- Boolean query with fuzzy match, phrase boost, and highlighting</li>
 *   <li>{@link #suggest} -- Term Suggest for spelling correction</li>
 * </ul>
 *
 * Query strategy implements techniques covered in the Elasticsearch course:
 * boolean queries (must + should), fuzziness AUTO, match_phrase boost,
 * multi-field matching, highlight with configurable fragment size, and
 * Term Suggest with SuggestMode.Missing.
 */
@Component
public class EsClient {

    private static final String INDEX = "wikipedia";
    private static final int DEFAULT_PAGE_SIZE = 10;
    private static final String USER = "elastic";
    private static final String PWD  = "user123";

    private ElasticsearchClient elasticsearchClient;

    public EsClient() {
        createConnection();
    }

    /**
     * @brief Establishes an HTTPS connection to the Elasticsearch cluster.
     *
     * Uses basic authentication and an unsafe SSL context suitable for
     * local development with self-signed certificates.
     */
    private void createConnection() {
        CredentialsProvider credentialsProvider = new BasicCredentialsProvider();
        credentialsProvider.setCredentials(AuthScope.ANY,
            new UsernamePasswordCredentials(USER, PWD));

        SSLFactory sslFactory = SSLFactory.builder()
            .withUnsafeTrustMaterial()
            .withUnsafeHostnameVerifier()
            .build();

        RestClient restClient = RestClient.builder(
                new HttpHost("localhost", 9200, "https"))
            .setHttpClientConfigCallback((HttpAsyncClientBuilder httpClientBuilder) ->
                httpClientBuilder
                    .setDefaultCredentialsProvider(credentialsProvider)
                    .setSSLContext(sslFactory.getSslContext())
                    .setSSLHostnameVerifier(sslFactory.getHostnameVerifier())
            ).build();

        ElasticsearchTransport transport = new RestClientTransport(
            restClient, new JacksonJsonpMapper());

        elasticsearchClient = new ElasticsearchClient(transport);
    }

    /**
     * @brief Executes a full-text search with boolean query, fuzzy matching, and highlighting.
     *
     * Query structure:
     * <pre>
     *   must:   match on "content" with fuzziness=AUTO (tolerates typos)
     *   should: match_phrase on "content" with boost=2.0 (promotes exact phrases)
     *   should: match on "title" with boost=1.5 (promotes title matches)
     * </pre>
     *
     * Highlighting returns a single fragment of up to 400 characters with
     * {@code <strong>} tags around matched terms.
     *
     * @param query    The user's search terms.
     * @param page     The current page number (1-indexed).
     * @param pageSize The number of results per page.
     * @return The raw Elasticsearch SearchResponse containing hits and metadata.
     */
    public SearchResponse<ObjectNode> search(
            String query, Integer page, Integer pageSize,
            String fuzziness, Float phraseBoost, Float titleBoost,
            Integer slop, Boolean highlight) {
            
        int size = (pageSize != null && pageSize > 0) ? pageSize : DEFAULT_PAGE_SIZE;
        int from = ((page != null ? page : 1) - 1) * size;

        String fuzz = (fuzziness != null && !fuzziness.isBlank()) ? fuzziness : "AUTO";
        float pb = (phraseBoost != null) ? phraseBoost : 2.0f;
        float tb = (titleBoost != null) ? titleBoost : 1.5f;
        int s = (slop != null) ? slop : 0;
        boolean hl = (highlight != null) ? highlight : true;

        Query boolQuery = Query.of(q -> q.bool(b -> b
            .must(m -> m.match(mq -> mq
                .field("content")
                .query(query)
                .fuzziness(fuzz)
            ))
            .should(sh -> sh.matchPhrase(mp -> mp
                .field("content")
                .query(query)
                .boost(pb)
                .slop(s)
            ))
            .should(sh -> sh.match(mq -> mq
                .field("title")
                .query(query)
                .boost(tb)
            ))
        ));

        try {
            return elasticsearchClient.search(req -> {
                req.index(INDEX)
                   .from(from)
                   .size(size)
                   .source(src -> src.filter(f -> f.includes("title", "url", "content")))
                   .query(boolQuery);
                   
                if (hl) {
                    req.highlight(h -> h
                        .preTags("<strong>")
                        .postTags("</strong>")
                        .numberOfFragments(1)
                        .fragmentSize(400)
                        .fields("content", hf -> hf)
                    );
                }
                
                return req;
            }, ObjectNode.class);
        } catch (IOException e) {
            throw new RuntimeException("Failed to execute search query against Elasticsearch", e);
        }
    }

    /**
     * @brief Executes a Term Suggest query for spelling correction.
     *
     * Analyzes the query tokens against the inverted index vocabulary and returns
     * correction options for tokens with low match frequency. Uses SuggestMode.Missing
     * to only suggest corrections for words not found in the index.
     *
     * @param query The user input potentially containing misspelled words.
     * @param size  Maximum number of suggestions per token.
     * @return The raw Elasticsearch SearchResponse containing suggest data.
     */
    public SearchResponse<ObjectNode> suggest(String query, Integer size) {
        int suggestSize = (size != null && size > 0) ? size : 3;

        try {
            return elasticsearchClient.search(s -> s
                .index(INDEX)
                .size(0)
                .suggest(sg -> sg
                    .suggesters("spell_check", sug -> sug
                        .text(query)
                        .term(t -> t
                            .field("content")
                            .size(suggestSize)
                            .suggestMode(
                                co.elastic.clients.elasticsearch._types.SuggestMode.Missing
                            )
                        )
                    )
                ),
                ObjectNode.class
            );
        } catch (IOException e) {
            throw new RuntimeException("Failed to execute suggest query against Elasticsearch", e);
        }
    }
}
