package com.elasticsearch.search.controller;

import com.elasticsearch.search.api.facade.SuggestApi;
import com.elasticsearch.search.api.model.SuggestResponse;
import com.elasticsearch.search.service.SearchService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.RestController;

import java.util.concurrent.CompletableFuture;

/**
 * Controller REST para o endpoint /suggest.
 *
 * Implementa a interface gerada pelo OpenAPI Generator (SuggestApi).
 * Retorna sugestões de correção ortográfica baseadas no vocabulário
 * do índice Wikipedia usando Term Suggest do Elasticsearch — aula 13/04.
 */
@CrossOrigin
@RestController
public class SuggestController implements SuggestApi {

    private final SearchService searchService;

    public SuggestController(SearchService searchService) {
        this.searchService = searchService;
    }

    @Override
    public CompletableFuture<ResponseEntity<SuggestResponse>> suggest(
            String query, Integer size) {

        return CompletableFuture.supplyAsync(() -> {
            SuggestResponse response = searchService.getSuggestions(query, size);
            return ResponseEntity.ok(response);
        });
    }
}
