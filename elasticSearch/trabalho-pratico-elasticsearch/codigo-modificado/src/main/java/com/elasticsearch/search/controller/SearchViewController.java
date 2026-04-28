package com.elasticsearch.search.controller;

import com.elasticsearch.search.api.model.SearchResponse;
import com.elasticsearch.search.api.model.SuggestResponse;
import com.elasticsearch.search.service.SearchService;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

import java.util.Collections;

/**
 * Controller MVC Thymeleaf para a interface de busca.
 *
 * Rota principal "/" serve o template search.html.
 * Quando uma query é submetida, realiza a busca chamando o backend REST,
 * e popula o Model com todos os dados necessários para o template.
 */
@Controller
public class SearchViewController {

    private final SearchController searchController;
    private final SearchService searchService;

    public SearchViewController(SearchController searchController, SearchService searchService) {
        this.searchController = searchController;
        this.searchService = searchService;
    }

    /**
     * Página inicial — sem query, exibe apenas a barra de busca centralizada.
     */
    @GetMapping("/")
    public String index(
            @RequestParam(value = "query", required = false, defaultValue = "") String query,
            @RequestParam(value = "page",  required = false, defaultValue = "1") Integer page,
            @RequestParam(value = "size",  required = false, defaultValue = "10") Integer size,
            Model model) {

        model.addAttribute("query", query);
        model.addAttribute("page", page);
        model.addAttribute("size", size);
        model.addAttribute("hasQuery", !query.isBlank());

        if (!query.isBlank()) {
            try {
                // Refactor: consumindo o serviço diretamente para maior eficiência
                SearchResponse response = searchService.search(query, page, size);
                
                // Sugestão de correção ortográfica — aula 13/04
                SuggestResponse suggestion = null;
                try {
                    suggestion = searchService.getSuggestions(query, 3);
                } catch (Exception e) {
                    // Suggest é best-effort; não bloqueia a busca principal
                }

                model.addAttribute("results", response.getResults());
                model.addAttribute("totalCount", response.getTotalCount());
                model.addAttribute("totalPages", response.getTotalPages());
                model.addAttribute("hasResults", response.getResults() != null && !response.getResults().isEmpty());
                model.addAttribute("suggestion", suggestion);
                model.addAttribute("error", null);

            } catch (Exception e) {
                model.addAttribute("results", Collections.emptyList());
                model.addAttribute("totalCount", 0L);
                model.addAttribute("totalPages", 0L);
                model.addAttribute("hasResults", false);
                model.addAttribute("suggestion", null);
                model.addAttribute("error", "Não foi possível conectar ao Elasticsearch. Verifique se os containers Docker estão rodando.");
            }
        } else {
            model.addAttribute("results", Collections.emptyList());
            model.addAttribute("totalCount", 0L);
            model.addAttribute("totalPages", 0L);
            model.addAttribute("hasResults", false);
            model.addAttribute("suggestion", null);
            model.addAttribute("error", null);
        }

        return "search/index";
    }
}
