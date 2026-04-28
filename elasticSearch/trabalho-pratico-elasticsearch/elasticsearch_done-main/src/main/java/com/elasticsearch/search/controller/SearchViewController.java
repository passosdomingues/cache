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
 * @brief MVC controller that serves the Thymeleaf search interface.
 *
 * Handles the root route "/" and populates the Spring Model with search
 * results, pagination metadata, and spelling suggestions for template
 * rendering. Delegates all Elasticsearch interaction to {@link SearchService}.
 */
@Controller
public class SearchViewController {

    private final SearchService searchService;

    public SearchViewController(SearchService searchService) {
        this.searchService = searchService;
    }

    /**
     * @brief Serves the main search page.
     *
     * When no query is provided, renders an empty search form (hero mode).
     * When a query is submitted, executes the search and populates the model
     * with results, pagination data, and optional spelling suggestions.
     *
     * @param query The search terms (optional, defaults to empty string).
     * @param page  The current page number (optional, defaults to 1).
     * @param size  The number of results per page (optional, defaults to 10).
     * @param model The Spring MVC Model to populate for the Thymeleaf template.
     * @return The template path "search/index".
     */
    @GetMapping("/")
    public String index(
            @RequestParam(value = "query", required = false, defaultValue = "") String query,
            @RequestParam(value = "page",  required = false, defaultValue = "1") Integer page,
            @RequestParam(value = "size",  required = false, defaultValue = "10") Integer size,
            @RequestParam(value = "fuzziness", required = false, defaultValue = "AUTO") String fuzziness,
            @RequestParam(value = "phraseBoost", required = false, defaultValue = "2.0") Float phraseBoost,
            @RequestParam(value = "titleBoost", required = false, defaultValue = "1.5") Float titleBoost,
            @RequestParam(value = "slop", required = false, defaultValue = "0") Integer slop,
            @RequestParam(value = "highlight", required = false, defaultValue = "true") Boolean highlight,
            @RequestParam(value = "spellCheck", required = false, defaultValue = "true") Boolean spellCheck,
            Model model) {

        model.addAttribute("query", query);
        model.addAttribute("page", page);
        model.addAttribute("size", size);
        model.addAttribute("hasQuery", !query.isBlank());
        
        // Tuning attributes for the sidebar form
        model.addAttribute("fuzziness", fuzziness);
        model.addAttribute("phraseBoost", phraseBoost);
        model.addAttribute("titleBoost", titleBoost);
        model.addAttribute("slop", slop);
        model.addAttribute("highlight", highlight);
        model.addAttribute("spellCheck", spellCheck);

        if (!query.isBlank()) {
            try {
                SearchResponse response = searchService.search(
                    query, page, size, fuzziness, phraseBoost, titleBoost, slop, highlight
                );

                SuggestResponse suggestion = null;
                if (spellCheck) {
                    try {
                        suggestion = searchService.getSuggestions(query, 3);
                    } catch (Exception e) {
                        /* Suggest is non-critical -- fail silently */
                    }
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
                model.addAttribute("error", "Failed to connect to Elasticsearch or invalid query parameters. " + e.getMessage());
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
