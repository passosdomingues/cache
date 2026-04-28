package com.elasticsearch.search.controller;

import com.elasticsearch.search.api.facade.SearchApi;
import com.elasticsearch.search.api.model.Result;
import com.elasticsearch.search.api.model.SearchResponse;
import com.elasticsearch.search.service.SearchService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.concurrent.CompletableFuture;

/**
 * Controller REST para o endpoint /search.
 *
 * Implementa a interface gerada pelo OpenAPI Generator (SearchApi).
 * Adiciona cabeçalhos HTTP de paginação conforme definido na api.yml:
 *   X-Total-Count  — total de documentos que correspondem à query
 *   X-Total-Pages  — total de páginas (ceil(total / size)) — aula 31/03
 *   X-Current-Page — página atual
 *   X-Page-Size    — tamanho da página
 */
@CrossOrigin
@RestController
public class SearchController implements SearchApi {

    private final SearchService searchService;

    public SearchController(SearchService searchService) {
        this.searchService = searchService;
    }

    @Override
    public CompletableFuture<ResponseEntity<SearchResponse>> search(
            String query, Integer page, Integer size) {

        int currentPage = (page != null) ? page : 1;
        int pageSize    = (size != null) ? size : 10;

        return CompletableFuture.supplyAsync(() -> {
            SearchResponse response = searchService.search(query, currentPage, pageSize);
            return ResponseEntity.ok(response);
        });
    }
}
