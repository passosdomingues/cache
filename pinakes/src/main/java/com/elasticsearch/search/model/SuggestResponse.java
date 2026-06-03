package com.elasticsearch.search.model;

import lombok.Builder;
import lombok.Data;
import java.util.List;

/**
 * Spell-correction response.
 *
 * §2.5 fix: suggestions come from content.raw_suggest (standard analyser,
 * no Snowball) so real surface forms are preserved.
 *
 * New field correctedQueryHtml: the corrected query with misspelled tokens
 * wrapped in <strong class="correction">...</strong> for visual diff in the UI.
 *
 * Example:
 *   original:           "Einsin's foula, revolutiozed physics"
 *   suggestions[0]:     "Einstein's formula, revolutionized physics"
 *   correctedQueryHtml: "<strong class=\"correction\">Einstein's</strong>
 *                        <strong class=\"correction\">formula</strong>,
 *                        <strong class=\"correction\">revolutionized</strong> physics"
 */
@Data
@Builder
public class SuggestResponse {
    private String original;
    private List<String> suggestions;
    /**
     * HTML-safe corrected query with changed tokens in &lt;strong class="correction"&gt;.
     * Safe for Thymeleaf th:utext rendering.
     */
    private String correctedQueryHtml;
    private boolean hasSuggestion;
}
