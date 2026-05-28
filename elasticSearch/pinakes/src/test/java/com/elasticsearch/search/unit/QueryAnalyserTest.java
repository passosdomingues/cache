package com.elasticsearch.search.unit;

import com.elasticsearch.search.model.QueryAnalysisResult;
import com.elasticsearch.search.service.QueryAnalyser;
import org.junit.jupiter.api.*;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import java.util.List;
import java.util.Map;

import static org.assertj.core.api.Assertions.*;

/**
 * Unit tests for QueryAnalyser.
 *
 * Tests:
 *   §TOKENISATION    — correct segmentation of query into WORD/PASSTHROUGH/QUOTED_PHRASE
 *   §HOLISTIC        — full multi-word query corrected token-by-token
 *   §CASE-SENSITIVE  — casing style (UPPER, Title, lower) preserved in corrections
 *   §WHOLE-WORD      — oracle returns full word not a stem
 *   §QUOTED-PHRASE   — quoted segments are never spell-checked
 *   §HTML-DIFF       — corrected tokens wrapped in <strong class="correction">
 *   §PASSTHROUGH     — LaTeX, numbers, punctuation emitted verbatim
 *   §EXTRACT-PHRASES — extractQuotedPhrases returns phrase list
 *   §STRIP-PHRASES   — stripQuotedPhrases removes quoted segments
 */
@DisplayName("QueryAnalyser Unit Tests")
class QueryAnalyserTest {

    private QueryAnalyser analyser;

    /** Simple oracle: reverses lookup in a fixed correction map */
    private static final Map<String, String> CORRECTIONS = Map.of(
            "einsin",      "einstein",
            "foula",       "formula",
            "revolutiozed","revolutionized",
            "kolmogrov",   "kolmogorov",
            "serach",      "search",
            "binery",      "binary"
    );

    /** Oracle that corrects from the map, returns original if not found */
    private final QueryAnalyser.SpellOracle oracle =
            word -> CORRECTIONS.getOrDefault(word.toLowerCase(), word);

    @BeforeEach
    void setUp() { analyser = new QueryAnalyser(); }

    // ── §HOLISTIC ─────────────────────────────────────────────────────────

    @Test
    @DisplayName("§HOLISTIC: full sentence with multiple typos corrected")
    void holisticCorrection() throws Exception {
        String input = "Einsin's foula, revolutiozed physics";
        var result = analyser.analyse(input, oracle);

        assertThat(result.isHasCorrectedTokens()).isTrue();
        assertThat(result.getCorrectedQuery())
                .containsIgnoringCase("Einstein")
                .containsIgnoringCase("formula")
                .containsIgnoringCase("revolutionized")
                .contains("physics"); // correct — unchanged
    }

    @Test
    @DisplayName("§HOLISTIC: uncorrected words preserved verbatim")
    void correctWordsUntouched() throws Exception {
        var result = analyser.analyse("binary search tree", oracle);
        // None of these words are in the correction map
        assertThat(result.isHasCorrectedTokens()).isFalse();
        assertThat(result.getCorrectedQuery()).isEqualTo("binary search tree");
    }

    // ── §CASE-SENSITIVE ───────────────────────────────────────────────────

    @ParameterizedTest(name = "original={0} → corrected should match style {2}")
    @CsvSource({
        "EINSIN,   einstein,  EINSTEIN",    // all-caps preserved
        "Einsin,   einstein,  Einstein",    // title-case preserved
        "einsin,   einstein,  einstein",    // lowercase preserved
    })
    @DisplayName("§CASE: casing style of original applied to correction")
    void casingPreserved(String original, String oracleCorrected, String expected) throws Exception {
        QueryAnalyser.SpellOracle caseOracle = word -> oracleCorrected;
        var result = analyser.analyse(original, caseOracle);
        assertThat(result.getCorrectedQuery()).isEqualTo(expected);
    }

    // ── §WHOLE-WORD ───────────────────────────────────────────────────────

    @Test
    @DisplayName("§WHOLE-WORD: oracle is called once per token, never per substring")
    void oracleCalledPerToken() throws Exception {
        java.util.List<String> calls = new java.util.ArrayList<>();
        QueryAnalyser.SpellOracle trackingOracle = word -> { calls.add(word); return word; };

        analyser.analyse("hello world foo", trackingOracle);

        // Exactly 3 WORD tokens
        assertThat(calls).containsExactlyInAnyOrder("hello", "world", "foo");
    }

    // ── §QUOTED-PHRASE ────────────────────────────────────────────────────

    @Test
    @DisplayName("§QUOTED-PHRASE: tokens inside quotes are NOT spell-checked")
    void quotedPhraseNotCorrected() throws Exception {
        // "binery serach" — both words would be corrected if unquoted
        var result = analyser.analyse("\"binery serach\" algorithm", oracle);

        // The quoted part should be returned unchanged
        assertThat(result.getCorrectedQuery())
                .contains("binery")   // NOT corrected — was quoted
                .contains("serach");  // NOT corrected — was quoted
    }

    @Test
    @DisplayName("§QUOTED-PHRASE: non-quoted typos ARE corrected alongside quoted phrases")
    void mixedQueryQuotedAndFuzzy() throws Exception {
        // "binary search" is exact; kolmogrov is a typo
        var result = analyser.analyse("\"binary search\" kolmogrov", oracle);

        assertThat(result.getCorrectedQuery())
                .contains("\"binary search\"")   // unchanged — quoted
                .containsIgnoringCase("kolmogorov"); // corrected — unquoted
    }

    // ── §HTML-DIFF ────────────────────────────────────────────────────────

    @Test
    @DisplayName("§HTML-DIFF: corrected tokens wrapped in <strong class=\"correction\">")
    void htmlDiffMarkup() throws Exception {
        var result = analyser.analyse("binery serach", oracle);

        assertThat(result.getCorrectedQueryHtml())
                .contains("<strong class=\"correction\">")
                .contains("</strong>");
    }

    @Test
    @DisplayName("§HTML-DIFF: unchanged tokens have no <strong> wrapper")
    void htmlDiffNoMarkupForCorrectWords() throws Exception {
        var result = analyser.analyse("binary search", oracle);
        // No corrections → no strong tags
        assertThat(result.getCorrectedQueryHtml())
                .doesNotContain("<strong class=\"correction\">");
    }

    @Test
    @DisplayName("§HTML-DIFF: quoted phrases get <span class=\"exact-phrase\">")
    void htmlDiffQuotedPhraseSpan() throws Exception {
        var result = analyser.analyse("\"binary search\"", oracle);
        assertThat(result.getCorrectedQueryHtml())
                .contains("<span class=\"exact-phrase\">");
    }

    // ── §PASSTHROUGH ──────────────────────────────────────────────────────

    @Test
    @DisplayName("§PASSTHROUGH: LaTeX notation emitted verbatim")
    void latexPassthrough() throws Exception {
        String input = "Einsin's foula, \\( E=mc^2 \\), revolutiozed physics";
        var result = analyser.analyse(input, oracle);

        // LaTeX segment preserved unchanged
        assertThat(result.getCorrectedQuery())
                .contains("\\( E=mc^2 \\)");
    }

    @Test
    @DisplayName("§PASSTHROUGH: punctuation and special chars preserved")
    void punctuationPassthrough() throws Exception {
        var result = analyser.analyse("hello, world! (test)", oracle);
        assertThat(result.getCorrectedQuery()).contains(",").contains("!").contains("(").contains(")");
    }

    // ── §EXTRACT-PHRASES ──────────────────────────────────────────────────

    @Test
    @DisplayName("§EXTRACT: extractQuotedPhrases returns all quoted segments")
    void extractPhrasesMultiple() {
        List<String> phrases = analyser.extractQuotedPhrases(
                "\"binary search\" tree \"randomized algorithm\"");
        assertThat(phrases)
                .hasSize(2)
                .containsExactly("binary search", "randomized algorithm");
    }

    @Test
    @DisplayName("§EXTRACT: empty list when no quotes")
    void extractPhrasesNone() {
        assertThat(analyser.extractQuotedPhrases("binary search tree")).isEmpty();
    }

    // ── §STRIP-PHRASES ────────────────────────────────────────────────────

    @Test
    @DisplayName("§STRIP: quoted segments removed, remainder trimmed")
    void stripPhrases() {
        String result = analyser.stripQuotedPhrases("\"binary search\" tree algorithm");
        assertThat(result).isEqualTo("tree algorithm");
        assertThat(result).doesNotContain("\"");
    }

    @Test
    @DisplayName("§STRIP: all-quoted query returns empty remainder")
    void stripPhrasesAllQuoted() {
        String result = analyser.stripQuotedPhrases("\"binary search\"");
        assertThat(result).isBlank();
    }

    // ── §EDGE-CASES ───────────────────────────────────────────────────────

    @Test
    @DisplayName("Null query returns empty result without throwing")
    void nullQuerySafe() throws Exception {
        assertThatCode(() -> analyser.analyse(null, oracle)).doesNotThrowAnyException();
    }

    @Test
    @DisplayName("Blank query returns empty result without throwing")
    void blankQuerySafe() throws Exception {
        var result = analyser.analyse("   ", oracle);
        assertThat(result.isHasCorrectedTokens()).isFalse();
    }

    @Test
    @DisplayName("Oracle exception is caught gracefully — original token preserved")
    void oracleExceptionHandled() throws Exception {
        QueryAnalyser.SpellOracle failingOracle = word -> { throw new RuntimeException("ES down"); };
        var result = analyser.analyse("binery serach", failingOracle);
        // Should not throw; words remain uncorrected
        assertThat(result.getCorrectedQuery()).isEqualTo("binery serach");
        assertThat(result.isHasCorrectedTokens()).isFalse();
    }
}
