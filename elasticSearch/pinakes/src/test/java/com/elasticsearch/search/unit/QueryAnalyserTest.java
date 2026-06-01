package com.elasticsearch.search.unit;

import com.elasticsearch.search.model.QueryAnalysisResult;
import com.elasticsearch.search.service.QueryAnalyser;
import org.junit.jupiter.api.*;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.params.provider.ValueSource;

import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;

import static org.assertj.core.api.Assertions.*;

/**
 * Unit tests for QueryAnalyser.
 *
 * §HOLISTIC        — full multi-word query corrected token-by-token
 * §CASE-SENSITIVE  — casing style (UPPER, Title, lower, mixed) preserved
 * §WHOLE-WORD      — oracle called once per token; hyphenated/apostrophe = 1 token
 * §QUOTED-PHRASE   — quoted segments never spell-checked; unclosed quote handled
 * §HTML-DIFF       — <strong>/<span> markup; HTML special chars escaped
 * §PASSTHROUGH     — LaTeX, numbers, punctuation emitted verbatim
 * §EXTRACT-PHRASES — extractQuotedPhrases returns phrase list; null-safe
 * §STRIP-PHRASES   — stripQuotedPhrases; space-collapse; null-safe
 * §RESULT-FIELDS   — wasCorrected / isQuotedPhrase / isPassthrough flags
 * §IDEMPOTENT      — already-correct query produces no corrections
 * §EDGE            — null, blank, very short words, oracle returning null/blank
 */
@DisplayName("QueryAnalyser Unit Tests")
class QueryAnalyserTest {

    private QueryAnalyser analyser;

    private static final Map<String, String> CORRECTIONS = Map.of(
            "einsin",       "einstein",
            "foula",        "formula",
            "revolutiozed", "revolutionized",
            "kolmogrov",    "kolmogorov",
            "serach",       "search",
            "binery",       "binary",
            "quantom",      "quantum",
            "phyics",       "physics"
    );

    private final QueryAnalyser.SpellOracle oracle =
            word -> CORRECTIONS.getOrDefault(word.toLowerCase(), word);

    @BeforeEach
    void setUp() { analyser = new QueryAnalyser(); }

    // ── §HOLISTIC ─────────────────────────────────────────────────────────

    @Test
    @DisplayName("§HOLISTIC: full sentence with multiple typos corrected")
    void holisticCorrection() throws Exception {
        var result = analyser.analyse("Einsin's foula, revolutiozed physics", oracle);
        assertThat(result.isHasCorrectedTokens()).isTrue();
        assertThat(result.getCorrectedQuery())
                .containsIgnoringCase("Einstein")
                .containsIgnoringCase("formula")
                .containsIgnoringCase("revolutionized")
                .contains("physics");
    }

    @Test
    @DisplayName("§HOLISTIC: uncorrected words preserved verbatim")
    void correctWordsUntouched() throws Exception {
        var result = analyser.analyse("binary search tree", oracle);
        assertThat(result.isHasCorrectedTokens()).isFalse();
        assertThat(result.getCorrectedQuery()).isEqualTo("binary search tree");
    }

    @Test
    @DisplayName("§HOLISTIC: single-word query corrected")
    void singleWordCorrection() throws Exception {
        var result = analyser.analyse("quantom", oracle);
        assertThat(result.isHasCorrectedTokens()).isTrue();
        assertThat(result.getCorrectedQuery()).isEqualToIgnoringCase("quantum");
    }

    @Test
    @DisplayName("§HOLISTIC: passthrough-only query returns unchanged")
    void passthroughOnlyQuery() throws Exception {
        var result = analyser.analyse("123 + 456", oracle);
        assertThat(result.isHasCorrectedTokens()).isFalse();
        assertThat(result.getCorrectedQuery()).isEqualTo("123 + 456");
    }

    // ── §CASE-SENSITIVE ───────────────────────────────────────────────────

    @ParameterizedTest(name = "original={0} → expected={2}")
    @CsvSource({
        "EINSIN,   einstein,  EINSTEIN",
        "Einsin,   einstein,  Einstein",
        "einsin,   einstein,  einstein",
    })
    @DisplayName("§CASE: casing style of original applied to correction")
    void casingPreserved(String original, String oracleCorrected, String expected) throws Exception {
        QueryAnalyser.SpellOracle caseOracle = word -> oracleCorrected;
        var result = analyser.analyse(original, caseOracle);
        assertThat(result.getCorrectedQuery()).isEqualTo(expected);
    }

    @Test
    @DisplayName("§CASE-EDGE: Title-case start (Kolmogrov) → Kolmogorov")
    void titleCaseSingleUpperFirst() throws Exception {
        var result = analyser.analyse("Kolmogrov", oracle);
        assertThat(result.getCorrectedQuery()).isEqualTo("Kolmogorov");
    }

    @Test
    @DisplayName("§CASE-EDGE: mixed-case (not all-caps, not title, not lower) → oracle form returned")
    void mixedCasePreservesOracleForm() throws Exception {
        QueryAnalyser.SpellOracle caseOracle = word -> "einstein";
        var result = analyser.analyse("eInSin", caseOracle);
        assertThat(result.getCorrectedQuery()).isEqualTo("einstein");
    }

    // ── §WHOLE-WORD ───────────────────────────────────────────────────────

    @Test
    @DisplayName("§WHOLE-WORD: oracle called once per token")
    void oracleCalledPerToken() throws Exception {
        var calls = new java.util.ArrayList<String>();
        analyser.analyse("hello world foo", word -> { calls.add(word); return word; });
        assertThat(calls).containsExactlyInAnyOrder("hello", "world", "foo");
    }

    @Test
    @DisplayName("§WHOLE-WORD: hyphenated compound = 1 WORD token → 1 oracle call")
    void hyphenatedCompoundSingleToken() throws Exception {
        AtomicInteger count = new AtomicInteger();
        analyser.analyse("well-known", w -> { count.incrementAndGet(); return w; });
        assertThat(count.get()).isEqualTo(1);
    }

    @Test
    @DisplayName("§WHOLE-WORD: apostrophe contraction = 1 WORD token per word")
    void apostropheContractionSingleToken() throws Exception {
        AtomicInteger count = new AtomicInteger();
        analyser.analyse("Einstein's theory", w -> { count.incrementAndGet(); return w; });
        assertThat(count.get()).isEqualTo(2);
    }

    // ── §QUOTED-PHRASE ────────────────────────────────────────────────────

    @Test
    @DisplayName("§QUOTED-PHRASE: tokens inside quotes are NOT spell-checked")
    void quotedPhraseNotCorrected() throws Exception {
        var result = analyser.analyse("\"binery serach\" algorithm", oracle);
        assertThat(result.getCorrectedQuery())
                .contains("binery")
                .contains("serach");
    }

    @Test
    @DisplayName("§QUOTED-PHRASE: non-quoted typos corrected alongside quoted phrases")
    void mixedQueryQuotedAndFuzzy() throws Exception {
        var result = analyser.analyse("\"binary search\" kolmogrov", oracle);
        assertThat(result.getCorrectedQuery())
                .contains("\"binary search\"")
                .containsIgnoringCase("kolmogorov");
    }

    @Test
    @DisplayName("§QUOTED-PHRASE: unclosed quote consumed gracefully to end of input")
    void unclosedQuoteHandledGracefully() {
        assertThatCode(() -> analyser.analyse("\"unclosed phrase", oracle))
                .doesNotThrowAnyException();
        assertThatCode(() -> {
            var r = analyser.analyse("\"unclosed phrase", oracle);
            assertThat(r.getCorrectedQuery()).contains("unclosed").contains("phrase");
        }).doesNotThrowAnyException();
    }

    @Test
    @DisplayName("§QUOTED-PHRASE: empty quoted segment handled gracefully")
    void emptyQuotedSegmentHandled() {
        assertThatCode(() -> analyser.analyse("\"\" hello", oracle))
                .doesNotThrowAnyException();
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

    @Test
    @DisplayName("§HTML-DIFF: & in passthrough escaped to &amp;")
    void htmlDiffEscapesAmpersand() throws Exception {
        var result = analyser.analyse("hello & world", oracle);
        assertThat(result.getCorrectedQueryHtml())
                .contains("&amp;")
                .doesNotContain(" & ");
    }

    @Test
    @DisplayName("§HTML-DIFF: < and > in passthrough escaped")
    void htmlDiffEscapesAngledBrackets() throws Exception {
        var result = analyser.analyse("a < b > c", oracle);
        assertThat(result.getCorrectedQueryHtml())
                .contains("&lt;").contains("&gt;");
    }

    // ── §PASSTHROUGH ──────────────────────────────────────────────────────

    @Test
    @DisplayName("§PASSTHROUGH: LaTeX notation emitted verbatim")
    void latexPassthrough() throws Exception {
        var result = analyser.analyse("Einsin's foula, \\( E=mc^2 \\), revolutiozed physics", oracle);
        assertThat(result.getCorrectedQuery()).contains("\\( E=mc^2 \\)");
    }

    @Test
    @DisplayName("§PASSTHROUGH: punctuation preserved")
    void punctuationPassthrough() throws Exception {
        var result = analyser.analyse("hello, world! (test)", oracle);
        assertThat(result.getCorrectedQuery())
                .contains(",").contains("!").contains("(").contains(")");
    }

    @Test
    @DisplayName("§PASSTHROUGH: numbers never sent to oracle")
    void numbersNotSpellChecked() throws Exception {
        AtomicInteger calls = new AtomicInteger();
        analyser.analyse("123 456 789", w -> { calls.incrementAndGet(); return w; });
        assertThat(calls.get()).isZero();
    }

    @Test
    @DisplayName("§PASSTHROUGH: passthrough-only query reconstructed identically")
    void reconstructionEqualsOriginalPassthrough() throws Exception {
        String input = "123, (x+y)^2 = z";
        assertThat(analyser.analyse(input, oracle).getCorrectedQuery()).isEqualTo(input);
    }

    // ── §EXTRACT-PHRASES ──────────────────────────────────────────────────

    @Test
    @DisplayName("§EXTRACT: returns all quoted segments in order")
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

    @Test
    @DisplayName("§EXTRACT: null input returns empty list without throwing")
    void extractPhrasesNullSafe() {
        assertThatCode(() -> analyser.extractQuotedPhrases(null))
                .doesNotThrowAnyException();
        assertThat(analyser.extractQuotedPhrases(null)).isEmpty();
    }

    @Test
    @DisplayName("§EXTRACT: single-word phrase extracted correctly")
    void extractSingleWordPhrase() {
        assertThat(analyser.extractQuotedPhrases("\"quantum\" computing"))
                .containsExactly("quantum");
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
        assertThat(analyser.stripQuotedPhrases("\"binary search\"")).isBlank();
    }

    @Test
    @DisplayName("§STRIP: null input returns empty string without throwing")
    void stripPhrasesNullSafe() {
        assertThatCode(() -> analyser.stripQuotedPhrases(null)).doesNotThrowAnyException();
        assertThat(analyser.stripQuotedPhrases(null)).isEmpty();
    }

    @Test
    @DisplayName("§STRIP: adjacent spaces collapsed after stripping")
    void stripPhrasesCollapsesSpaces() {
        String result = analyser.stripQuotedPhrases("tree \"binary search\" algorithm");
        assertThat(result).doesNotContain("  ");
    }

    // ── §RESULT-FIELDS ────────────────────────────────────────────────────

    @Test
    @DisplayName("§RESULT-FIELDS: corrected token has wasCorrected=true")
    void correctedTokenFlagTrue() throws Exception {
        var result = analyser.analyse("binery", oracle);
        assertThat(result.getTokens())
                .filteredOn(QueryAnalysisResult.TokenCorrection::isWasCorrected)
                .isNotEmpty();
    }

    @Test
    @DisplayName("§RESULT-FIELDS: correct token has wasCorrected=false")
    void uncorrectedTokenFlagFalse() throws Exception {
        var result = analyser.analyse("binary", oracle);
        assertThat(result.getTokens())
                .filteredOn(t -> !t.isWasCorrected())
                .isNotEmpty();
    }

    @Test
    @DisplayName("§RESULT-FIELDS: quoted phrase token has isQuotedPhrase=true")
    void quotedPhraseTokenFlag() throws Exception {
        var result = analyser.analyse("\"binary search\"", oracle);
        assertThat(result.getTokens())
                .filteredOn(QueryAnalysisResult.TokenCorrection::isQuotedPhrase)
                .isNotEmpty();
    }

    @Test
    @DisplayName("§RESULT-FIELDS: punctuation token has isPassthrough=true")
    void passthroughTokenFlag() throws Exception {
        var result = analyser.analyse("hello, world", oracle);
        assertThat(result.getTokens())
                .filteredOn(QueryAnalysisResult.TokenCorrection::isPassthrough)
                .isNotEmpty();
    }

    // ── §IDEMPOTENT ───────────────────────────────────────────────────────

    @Test
    @DisplayName("§IDEMPOTENT: re-analysing a correct query produces no corrections")
    void idempotentOnCorrectQuery() throws Exception {
        var first  = analyser.analyse("binary search algorithm", oracle);
        var second = analyser.analyse(first.getCorrectedQuery(), oracle);
        assertThat(second.isHasCorrectedTokens()).isFalse();
        assertThat(second.getCorrectedQuery()).isEqualTo(first.getCorrectedQuery());
    }

    // ── §EDGE ─────────────────────────────────────────────────────────────

    @Test
    @DisplayName("§EDGE: null query returns empty result without throwing")
    void nullQuerySafe() {
        assertThatCode(() -> analyser.analyse(null, oracle)).doesNotThrowAnyException();
    }

    @Test
    @DisplayName("§EDGE: blank query returns hasCorrectedTokens=false")
    void blankQuerySafe() throws Exception {
        assertThat(analyser.analyse("   ", oracle).isHasCorrectedTokens()).isFalse();
    }

    @Test
    @DisplayName("§EDGE: oracle IOException caught — original token preserved, no rethrow")
    void oracleExceptionHandled() throws Exception {
        QueryAnalyser.SpellOracle failingOracle = word -> { throw new java.io.IOException("ES down"); };
        var result = analyser.analyse("binery serach", failingOracle);
        assertThat(result.getCorrectedQuery()).isEqualTo("binery serach");
        assertThat(result.isHasCorrectedTokens()).isFalse();
    }

    @Test
    @DisplayName("§EDGE: oracle returning null uses original token")
    void oracleNullResultUsesOriginal() throws Exception {
        var result = analyser.analyse("hello world", word -> null);
        assertThat(result.getCorrectedQuery()).isEqualTo("hello world");
    }

    @Test
    @DisplayName("§EDGE: oracle returning blank string uses original token")
    void oracleBlankResultUsesOriginal() throws Exception {
        var result = analyser.analyse("hello world", word -> "   ");
        assertThat(result.getCorrectedQuery()).isNotBlank();
    }

    @ParameterizedTest
    @ValueSource(strings = {"a", "ab", "abc"})
    @DisplayName("§EDGE: very short words processed without exception")
    void veryShortWordsHandled(String word) {
        assertThatCode(() -> analyser.analyse(word, oracle)).doesNotThrowAnyException();
    }
}
