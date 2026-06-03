package com.elasticsearch.search.controller;

import com.elasticsearch.search.config.SearchProperties;
import com.elasticsearch.search.model.*;
import com.elasticsearch.search.service.QueryAnalyser;
import com.elasticsearch.search.service.SearchService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;

/**
 * MVC controller for the Thymeleaf UI.
 *
 * §3.1 fix: spellCheck correctly wired through to SearchService.
 * §3.3 fix: @Valid + BindingResult — invalid input returns 400-style error.
 * §EXACT-PHRASE: passes hasExactPhrases flag to model for UI indicator.
 */
@Slf4j
@Controller
@RequiredArgsConstructor
public class SearchController {

    private final SearchService searchService;
    private final QueryAnalyser queryAnalyser;
    private final SearchProperties props;

    @GetMapping("/")
    public String index(@Valid @ModelAttribute SearchParams params,
                        BindingResult bindingResult,
                        Model model) {

        boolean hasQuery = params.getQuery() != null && !params.getQuery().isBlank();

        if (params.getFuzziness() == null) params.setFuzziness(props.getFuzziness());

        model.addAttribute("params",      params);
        model.addAttribute("query",       params.getQuery());
        model.addAttribute("fuzziness",   params.getFuzziness());
        model.addAttribute("phraseBoost", params.getPhraseBoost());
        model.addAttribute("titleBoost",  params.getTitleBoost());
        model.addAttribute("slop",        params.getSlop());
        model.addAttribute("highlight",   params.isHighlight());
        model.addAttribute("spellCheck",  params.isSpellCheck());
        model.addAttribute("hasQuery",    hasQuery);

        // Exact phrase indicator for template
        boolean hasExactPhrases = hasQuery &&
                !queryAnalyser.extractQuotedPhrases(params.getQuery()).isEmpty();
        model.addAttribute("hasExactPhrases", hasExactPhrases);

        if (!hasQuery) return "search/index";

        if (bindingResult.hasErrors()) {
            String err = bindingResult.getFieldErrors().stream()
                    .map(fe -> fe.getField() + ": " + fe.getDefaultMessage())
                    .findFirst().orElse("Invalid search parameters");
            model.addAttribute("error", err);
            model.addAttribute("hasResults", false);
            return "search/index";
        }

        try {
            SearchResponse response = searchService.search(params);
            model.addAttribute("results",    response.getResults());
            model.addAttribute("totalCount", response.getTotalCount());
            model.addAttribute("totalPages", response.getTotalPages());
            model.addAttribute("page",       response.getCurrentPage());
            model.addAttribute("pageSize",   response.getPageSize());
            model.addAttribute("tookMs",     response.getTookMs());
            model.addAttribute("hasResults", !response.getResults().isEmpty());
            model.addAttribute("suggestion", response.getSuggestion());
        } catch (Exception e) {
            log.error("Search failed for '{}': {}", params.getQuery(), e.getMessage(), e);
            model.addAttribute("error", "Search service unavailable. Please try again.");
            model.addAttribute("hasResults", false);
        }

        return "search/index";
    }
}
