package com.elasticsearch.search.model;

import lombok.Builder;
import lombok.Data;

import java.util.List;

/**
 * Result of a holistic query analysis pass.
 *
 * Design rationale (requirements §spell-check holistic):
 * ──────────────────────────────────────────────────────
 * The original suggest pipeline corrected tokens one at a time and returned
 * only the Snowball-stemmed vocabulary — so "Schrödinger" became "schroding"
 * and multi-word corrections were not case-sensitive.
 *
 * This model supports the new approach:
 *   1. Each token in the original query is analysed independently.
 *   2. Corrections preserve casing from the suggest vocabulary (raw_suggest field).
 *   3. Tokens that were corrected are marked with {@code wasCorrected=true} so
 *      the UI can wrap them in <strong> tags for visual diff.
 *   4. The {@code correctedQuery} field is the full recomposed query, ready to
 *      be used as an href in "Did you mean: <a>correctedQuery</a>?".
 *   5. Phrase tokens (surrounded by quotes in the original) are preserved verbatim
 *      and NOT spell-checked — exact phrase intent must be respected.
 *
 * Example:
 *   Input:  "Einsin's foula, \( E=mc^2 \), revolutiozed physics"
 *   Tokens: ["Einsin's", "foula", "E=mc^2", "revolutiozed", "physics"]
 *   Output correctedTokens:
 *     { original: "Einsin's",    corrected: "Einstein's",   wasCorrected: true  }
 *     { original: "foula",       corrected: "formula",      wasCorrected: true  }
 *     { original: "E=mc^2",      corrected: "E=mc^2",       wasCorrected: false }
 *     { original: "revolutiozed",corrected: "revolutionized",wasCorrected: true  }
 *     { original: "physics",     corrected: "physics",      wasCorrected: false }
 *   correctedQuery: "Einstein's formula, \( E=mc^2 \), revolutionized physics"
 *   htmlDiff: "**Einstein's** **formula**, \( E=mc^2 \), **revolutionized** physics"
 *             (where ** = <strong> wrapping of corrected tokens)
 */
@Data
@Builder
public class QueryAnalysisResult {

    /** The raw query string as submitted by the user */
    private String originalQuery;

    /**
     * Corrected query string — space-joined corrected tokens, preserving
     * original non-word characters (commas, parens, LaTeX, etc.).
     */
    private String correctedQuery;

    /**
     * HTML rendering of the corrected query: corrected tokens are wrapped
     * in &lt;strong class="correction"&gt;...&lt;/strong&gt; so the UI can
     * show exactly which words changed.
     */
    private String correctedQueryHtml;

    /** True when at least one token was corrected */
    private boolean hasCorrectedTokens;

    /** Per-token analysis result (in original order) */
    private List<TokenCorrection> tokens;

    @Data
    @Builder
    public static class TokenCorrection {
        /** Original token text exactly as typed */
        private String original;
        /** Best correction from ES suggest (same as original if no correction) */
        private String corrected;
        /** True when corrected ≠ original (ignoring case-only differences) */
        private boolean wasCorrected;
        /**
         * True when this token is a quoted phrase — quoted tokens are never
         * spell-checked; their exact-match intent is preserved.
         */
        private boolean isQuotedPhrase;
        /**
         * True for non-word tokens (punctuation, LaTeX, URLs, numbers) which
         * are passed through verbatim without spell-checking.
         */
        private boolean isPassthrough;
    }
}
