package com.elasticsearch.search.service;

import co.elastic.clients.elasticsearch.core.SearchResponse;
import co.elastic.clients.elasticsearch.core.search.Hit;
import co.elastic.clients.elasticsearch.core.search.Suggestion;
import co.elastic.clients.elasticsearch.core.search.TermSuggestOption;
import com.elasticsearch.search.api.model.Result;
import com.elasticsearch.search.api.model.SuggestResponse;
import com.elasticsearch.search.domain.EsClient;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * Serviço de busca que processa resultados do Elasticsearch e constrói
 * os modelos de resposta da API.
 *
 * Responsabilidades:
 * - Mapear hits do ES para objetos Result (com highlight e fallback para abs)
 * - Expor metadados de paginação (totalHits, totalPages)
 * - Processar Term Suggest e construir SuggestResponse
 */
@Service
public class SearchService {

    private final EsClient esClient;

    public SearchService(EsClient esClient) {
        this.esClient = esClient;
    }

    /**
     * Realiza a busca no Elasticsearch e retorna um wrapper completo com resultados e metadados.
     * Centraliza a lógica de busca para evitar múltiplas chamadas ao cluster (aula 31/03).
     */
    public com.elasticsearch.search.api.model.SearchResponse search(String query, Integer page, Integer pageSize) {
        SearchResponse<ObjectNode> esResponse = esClient.search(query, page, pageSize);
        
        List<Result> results = esResponse.hits().hits().stream().map(h -> {
            String title   = getField(h, "title");
            String url     = getField(h, "url");
            String content = getField(h, "content");

            String abs = extractHighlight(h, "content");
            if (abs == null || abs.isBlank()) {
                abs = treatContent(content);
            }

            return new Result()
                .abs(abs)
                .title(title)
                .url(url);
        }).collect(Collectors.toList());

        long totalHits = 0L;
        if (esResponse.hits().total() != null) {
            totalHits = esResponse.hits().total().value();
        }

        long totalPages = (totalHits + pageSize - 1) / pageSize;

        com.elasticsearch.search.api.model.SearchResponse response = new com.elasticsearch.search.api.model.SearchResponse();
        response.setResults(results);
        response.setTotalCount((int) totalHits);
        response.setTotalPages((int) totalPages);
        response.setCurrentPage(page);
        response.setPageSize(pageSize);

        return response;
    }

    /**
     * Gera sugestões de correção ortográfica usando Term Suggest — aula 13/04.
     */
    public SuggestResponse getSuggestions(String query, Integer size) {
        SearchResponse<ObjectNode> response = esClient.suggest(query, size);

        Set<String> suggestions = new LinkedHashSet<>();
        Map<String, List<Suggestion<ObjectNode>>> suggestMap = response.suggest();

        if (suggestMap != null && suggestMap.containsKey("spell_check")) {
            for (Suggestion<ObjectNode> suggestion : suggestMap.get("spell_check")) {
                // Cada token da query tem suas opções de correção
                List<TermSuggestOption> options = suggestion.term().options();
                if (options != null && !options.isEmpty()) {
                    // Pega a melhor sugestão (primeira, maior score) para cada token
                    options.stream()
                        .findFirst()
                        .ifPresent(opt -> suggestions.add(opt.text()));
                }
            }
        }

        List<String> suggestionList = new ArrayList<>(suggestions);
        boolean hasSuggestion = !suggestionList.isEmpty();

        SuggestResponse resp = new SuggestResponse();
        resp.setOriginal(query);
        resp.setSuggestions(suggestionList);
        resp.setHasSuggestion(hasSuggestion);
        return resp;
    }

    // ── Helpers ──────────────────────────────────────────────────────────────

    private String getField(Hit<ObjectNode> hit, String field) {
        if (hit.source() == null || !hit.source().has(field)) return "";
        return hit.source().get(field).asText("");
    }

    /**
     * Extrai o primeiro fragmento de highlight do campo especificado.
     * O highlight usa tags <strong> conforme configurado no EsClient.
     */
    private String extractHighlight(Hit<ObjectNode> hit, String field) {
        if (hit.highlight() == null) return null;
        List<String> fragments = hit.highlight().get(field);
        if (fragments != null && !fragments.isEmpty()) {
            return fragments.get(0);
        }
        return null;
    }

    /**
     * Remove tags HTML e caracteres especiais do conteúdo bruto.
     * Usado como fallback quando não há highlight disponível.
     */
    private String treatContent(String content) {
        if (content == null) return "";
        content = content.replaceAll("</?\\w[^>]*>", "");
        content = content.replaceAll("[^A-Za-zÀ-ÿ\\s.,;:!?()-]+", " ");
        content = content.replaceAll("\\s+", " ");
        return content.trim();
    }
}
