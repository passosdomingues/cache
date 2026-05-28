package com.elasticsearch.search.service;

import com.elasticsearch.search.model.QueryAnalysisResult;
import com.elasticsearch.search.model.QueryAnalysisResult.TokenCorrection;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * QueryAnalyser — holistic query analysis and spell-correction.
 *
 * ══════════════════════════════════════════════════════════════════
 * DESIGN DECISIONS (requirements §spell-check holistic, §case-sensitive,
 *                   §quoted-phrase exact, §strong-markup):
 *
 * 1. TOKENISATION (atomic, no side-effects):
 *    The raw query is split into a stream of typed segments:
 *      - QUOTED_PHRASE  → text inside "..." — never spell-checked
 *      - WORD           → [A-Za-z''-]+ — subject to spell-check
 *      - PASSTHROUGH    → everything else (numbers, LaTeX, punctuation, URLs)
 *
 *    Example: `Einsin's foula, \( E=mc^2 \), revolutiozed "physics"`
 *      → WORD("Einsin's"), PASSTHROUGH(", "), WORD("foula"),
 *        PASSTHROUGH(", \\( "), PASSTHROUGH("E=mc^2"),
 *        PASSTHROUGH(" \\), "), WORD("revolutiozed"),
 *        PASSTHROUGH(" "), QUOTED_PHRASE(""physics"")
 *
 * 2. SPELL-CHECK ORACLE (injected, async-ready):
 *    A {@code SpellOracle} functional interface allows the caller to inject
 *    the ES suggest call. This keeps QueryAnalyser unit-testable without ES.
 *
 * 3. CASE PRESERVATION (§case-sensitive requirement):
 *    After the oracle returns a correction (always lowercase from the
 *    standard analyser), we re-apply the original token's casing style:
 *      - ALL_CAPS      → CORRECTION
 *      - Title_Case    → Correction
 *      - lowercase     → correction
 *      - Mixed / Other → oracle casing kept as-is (most flexible)
 *
 * 4. WHOLE-WORD GUARANTEE (§iterate over word vector):
 *    The oracle is called once per WORD token.  The result is either the
 *    whole corrected word or the original — never a partial stem.  This
 *    fixes the "binary" → "binar" and "Schrödinger" → "schroding" bugs.
 *
 * 5. HTML DIFF OUTPUT:
 *    Corrected tokens are wrapped in <strong class="correction">...</strong>.
 *    Quoted phrases get <span class="exact-phrase">...</span>.
 *    Passthrough tokens are emitted verbatim.
 *    The HTML is safe to render via Thymeleaf th:utext.
 *
 * 6. EXACT PHRASE SEARCH (§busca exata):
 *    When the user wraps terms in quotes, the rewritten ES query uses a
 *    match_phrase clause instead of multi_match for those segments.
 *    The {@code extractedPhrases()} method returns quoted segments for
 *    use in EsClient.buildExactPhraseQuery().
 * ══════════════════════════════════════════════════════════════════
 */
@Slf4j
@Component
public class QueryAnalyser {

    // ── Token types ────────────────────────────────────────────────────────

    private enum TokenType { QUOTED_PHRASE, WORD, PASSTHROUGH }

    private record Segment(TokenType type, String text) {}

    /**
     * Functional interface for the spell-check oracle.
     * Receives one word, returns best correction (or the original if none found).
     * Declared as a checked-exception-capable SAM for IO compatibility.
     */
    @FunctionalInterface
    public interface SpellOracle {
        String correct(String word) throws Exception;
    }

    // ── Public API ─────────────────────────────────────────────────────────

    /**
     * Analyses the query holistically:
     *   1. Tokenises preserving structure
     *   2. Calls oracle for each WORD token
     *   3. Reapplies original casing to corrections
     *   4. Builds corrected query string and HTML diff
     *
     * @param rawQuery  the user's raw query string
     * @param oracle    spell-check function (usually wraps EsClient.suggest)
     * @return          populated QueryAnalysisResult
     */
    public QueryAnalysisResult analyse(String rawQuery, SpellOracle oracle) {
        if (rawQuery == null || rawQuery.isBlank()) {
            return emptyResult(rawQuery);
        }

        List<Segment> segments = tokenise(rawQuery);
        List<TokenCorrection> tokenCorrections = new ArrayList<>();
        StringBuilder correctedQuery = new StringBuilder();
        StringBuilder correctedHtml  = new StringBuilder();
        boolean anyCorrected = false;

        for (Segment seg : segments) {
            switch (seg.type()) {

                case QUOTED_PHRASE -> {
                    // Quoted phrases are exact — pass verbatim, no spell-check
                    TokenCorrection tc = TokenCorrection.builder()
                            .original(seg.text())
                            .corrected(seg.text())
                            .wasCorrected(false)
                            .isQuotedPhrase(true)
                            .isPassthrough(false)
                            .build();
                    tokenCorrections.add(tc);
                    correctedQuery.append(seg.text());
                    correctedHtml.append("<span class=\"exact-phrase\">")
                                 .append(escapeHtml(seg.text()))
                                 .append("</span>");
                }

                case PASSTHROUGH -> {
                    // Punctuation, LaTeX, numbers — emit as-is
                    TokenCorrection tc = TokenCorrection.builder()
                            .original(seg.text())
                            .corrected(seg.text())
                            .wasCorrected(false)
                            .isQuotedPhrase(false)
                            .isPassthrough(true)
                            .build();
                    tokenCorrections.add(tc);
                    correctedQuery.append(seg.text());
                    correctedHtml.append(escapeHtml(seg.text()));
                }

                case WORD -> {
                    String original  = seg.text();
                    String corrected = original; // default: no change

                    try {
                        String oracleResult = oracle.correct(original);
                        if (oracleResult != null && !oracleResult.isBlank()) {
                            // Re-apply original casing style to the oracle correction
                            corrected = reapplyCasing(original, oracleResult);
                        }
                    } catch (Exception e) {
                        log.warn("SpellOracle failed for token '{}': {}", original, e.getMessage());
                    }

                    boolean changed = !corrected.equalsIgnoreCase(original);
                    if (changed) anyCorrected = true;

                    tokenCorrections.add(TokenCorrection.builder()
                            .original(original)
                            .corrected(corrected)
                            .wasCorrected(changed)
                            .isQuotedPhrase(false)
                            .isPassthrough(false)
                            .build());

                    correctedQuery.append(corrected);

                    if (changed) {
                        // Wrap corrected token in <strong> for visual diff
                        correctedHtml.append("<strong class=\"correction\">")
                                     .append(escapeHtml(corrected))
                                     .append("</strong>");
                    } else {
                        correctedHtml.append(escapeHtml(corrected));
                    }
                }
            }
        }

        return QueryAnalysisResult.builder()
                .originalQuery(rawQuery)
                .correctedQuery(correctedQuery.toString())
                .correctedQueryHtml(correctedHtml.toString())
                .hasCorrectedTokens(anyCorrected)
                .tokens(tokenCorrections)
                .build();
    }

    /**
     * Extracts quoted phrases from a query for use in exact-phrase ES clauses.
     * "binary search" tree → ["binary search"]
     */
    public List<String> extractQuotedPhrases(String rawQuery) {
        if (rawQuery == null) return Collections.emptyList();
        List<String> phrases = new ArrayList<>();
        Matcher m = QUOTED_PHRASE_PATTERN.matcher(rawQuery);
        while (m.find()) {
            phrases.add(m.group(1)); // capture group inside quotes
        }
        return phrases;
    }

    /**
     * Returns the query with quoted-phrase segments stripped out,
     * leaving only the fuzzy-search portion.
     *
     * "binary search" tree algorithm → "tree algorithm"
     */
    public String stripQuotedPhrases(String rawQuery) {
        if (rawQuery == null) return "";
        return QUOTED_PHRASE_PATTERN.matcher(rawQuery).replaceAll("").trim()
                .replaceAll("\\s{2,}", " ");
    }

    // ── Private helpers ────────────────────────────────────────────────────

    /** Pattern: "..." or '...' including the quotes */
    private static final Pattern QUOTED_PHRASE_PATTERN =
            Pattern.compile("\"([^\"]+)\"");

    /**
     * Word pattern: Unicode letters plus apostrophe/hyphen for contractions
     * and hyphenated compounds (Einstein's, well-known, E=mc²).
     * We deliberately exclude digits so "E=mc^2" is PASSTHROUGH.
     */
    private static final Pattern WORD_PATTERN =
            Pattern.compile("[\\p{L}][\\p{L}'\\-]*");

    /**
     * Tokenises the raw query into an ordered list of typed segments.
     *
     * Algorithm:
     *   - Scan left-to-right.
     *   - If we see a quote → consume everything until the closing quote as QUOTED_PHRASE.
     *   - If we see a word char → consume the word as WORD.
     *   - Everything else → PASSTHROUGH.
     *
     * This guarantees the concatenation of all segment texts equals the original query.
     */
    private List<Segment> tokenise(String query) {
        List<Segment> segments = new ArrayList<>();
        int i = 0;
        int len = query.length();

        while (i < len) {
            char ch = query.charAt(i);

            // ── Quoted phrase ──────────────────────────────────────────────
            if (ch == '"') {
                int close = query.indexOf('"', i + 1);
                if (close == -1) close = len - 1; // unclosed quote → to end
                segments.add(new Segment(TokenType.QUOTED_PHRASE,
                        query.substring(i, close + 1)));
                i = close + 1;

            // ── Word (Unicode letter start) ────────────────────────────────
            } else if (Character.isLetter(ch)) {
                Matcher m = WORD_PATTERN.matcher(query.substring(i));
                if (m.find() && m.start() == 0) {
                    segments.add(new Segment(TokenType.WORD, m.group()));
                    i += m.end();
                } else {
                    segments.add(new Segment(TokenType.PASSTHROUGH, String.valueOf(ch)));
                    i++;
                }

            // ── Passthrough ────────────────────────────────────────────────
            } else {
                // Accumulate consecutive passthrough chars for efficiency
                int start = i;
                while (i < len && query.charAt(i) != '"' && !Character.isLetter(query.charAt(i))) {
                    i++;
                }
                segments.add(new Segment(TokenType.PASSTHROUGH, query.substring(start, i)));
            }
        }
        return segments;
    }

    /**
     * Reapplies the casing style of {@code original} to {@code correction}.
     *
     * Rules (in priority order):
     *   1. ALL_CAPS (ALL)        → CORRECTION
     *   2. Title_Case (Abc)      → Correction
     *   3. lower_case            → correction
     *   4. Mixed / Other         → correction as returned by oracle (preserve it)
     *
     * We do NOT do character-level case mirroring (e.g. "aBcDeF") because
     * that pattern never occurs in natural language and would produce
     * unreadable output.
     */
    private String reapplyCasing(String original, String correction) {
        if (original == null || original.isEmpty() || correction == null) return correction;

        // Strip leading apostrophes / hyphens for style detection
        String core = original.replaceAll("^['-]+|['-]+$", "");
        if (core.isEmpty()) return correction;

        boolean allUpper  = core.equals(core.toUpperCase());
        boolean allLower  = core.equals(core.toLowerCase());
        boolean titleCase = Character.isUpperCase(core.charAt(0))
                            && core.substring(1).equals(core.substring(1).toLowerCase());

        if (allUpper && !allLower) {
            return correction.toUpperCase();
        } else if (titleCase) {
            return capitalise(correction);
        } else if (allLower) {
            return correction.toLowerCase();
        } else {
            // Mixed case (e.g. "McDonalds", "iPhone") — return oracle form
            return correction;
        }
    }

    private String capitalise(String s) {
        if (s == null || s.isEmpty()) return s;
        return Character.toUpperCase(s.charAt(0)) + s.substring(1).toLowerCase();
    }

    private String escapeHtml(String s) {
        if (s == null) return "";
        return s.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("\"", "&quot;");
    }

    private QueryAnalysisResult emptyResult(String query) {
        return QueryAnalysisResult.builder()
                .originalQuery(query == null ? "" : query)
                .correctedQuery(query == null ? "" : query)
                .correctedQueryHtml(query == null ? "" : escapeHtml(query))
                .hasCorrectedTokens(false)
                .tokens(Collections.emptyList())
                .build();
    }
}
