package com.elasticsearch.search.domain;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch._types.query_dsl.MatchQuery;
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
 * Cliente Elasticsearch responsável por executar queries no índice Wikipedia.
 *
 * Features implementadas baseadas nas aulas:
 * - Boolean query com must (match fuzziness:auto) + should (match_phrase boost)
 * - Multi-match nos campos content e title
 * - Highlight com tags <strong> e fragmento único de 400 chars
 * - Paginação com from/size e retorno do total de hits
 * - Term Suggest para correção ortográfica
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

        elasticsearchClient = new co.elastic.clients.elasticsearch.ElasticsearchClient(transport);
    }

    /**
     * Executa busca full-text com boolean query (must+should), fuzzy matching e highlight.
     *
     * Strategy (aula 30/03 + 06/04):
     *   must:   match fuzziness=AUTO em content (tolerante a erros de digitação)
     *   should: match_phrase em content e title (aumenta score de frases exatas)
     *   highlight: tags <strong>, 1 fragmento de 400 chars
     *
     * @param query    termo(s) de busca
     * @param page     página atual (1-indexed)
     * @param pageSize quantidade de resultados por página
     */
    public SearchResponse<ObjectNode> search(String query, Integer page, Integer pageSize) {
        int size = (pageSize != null && pageSize > 0) ? pageSize : DEFAULT_PAGE_SIZE;
        int from = ((page != null ? page : 1) - 1) * size;

        // Boolean query: must (fuzzy match) + should (phrase boost) — aula 30/03
        Query boolQuery = Query.of(q -> q.bool(b -> b
            .must(m -> m.match(mq -> mq
                .field("content")
                .query(query)
                .fuzziness("AUTO")               // Fuzzy match — aula 06/04
            ))
            .should(s -> s.matchPhrase(mp -> mp   // Phrase boost — aula 30/03
                .field("content")
                .query(query)
                .boost(2.0f)
            ))
            .should(s -> s.match(mq -> mq         // Title match boost — aula 23/03
                .field("title")
                .query(query)
                .boost(1.5f)
            ))
        ));

        try {
            return elasticsearchClient.search(s -> s
                .index(INDEX)
                .from(from)
                .size(size)
                .source(src -> src.filter(f -> f.includes("title", "url", "content")))
                .query(boolQuery)
                .highlight(h -> h                  // Highlight — aula 06/04
                    .preTags("<strong>")
                    .postTags("</strong>")
                    .numberOfFragments(1)
                    .fragmentSize(400)
                    .fields("content", hf -> hf)
                ),
                ObjectNode.class
            );
        } catch (IOException e) {
            throw new RuntimeException("Erro ao executar busca no Elasticsearch", e);
        }
    }

    /**
     * Executa Term Suggest para correção ortográfica — aula 13/04.
     *
     * @param query  texto com possíveis erros de digitação
     * @param size   número máximo de sugestões por termo
     */
    public co.elastic.clients.elasticsearch.core.SearchResponse<ObjectNode> suggest(
            String query, Integer size) {

        int suggestSize = (size != null && size > 0) ? size : 3;

        try {
            return elasticsearchClient.search(s -> s
                .index(INDEX)
                .size(0) // Não retorna documentos, apenas sugestões
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
            throw new RuntimeException("Erro ao executar suggest no Elasticsearch", e);
        }
    }
}
