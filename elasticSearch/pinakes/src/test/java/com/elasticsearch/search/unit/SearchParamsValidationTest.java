package com.elasticsearch.search.unit;

import com.elasticsearch.search.model.SearchParams;
import jakarta.validation.ConstraintViolation;
import jakarta.validation.Validation;
import jakarta.validation.Validator;
import org.junit.jupiter.api.*;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.params.provider.NullAndEmptySource;
import org.junit.jupiter.params.provider.ValueSource;

import java.util.Set;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Unit tests for SearchParams bean validation.
 *
 * §VALID      — valid parameter combinations pass
 * §QUERY      — blank/null/too-short/too-long query rejected
 * §PAGE       — page < 1 rejected
 * §SIZE       — size < 1 or > 50 rejected
 * §BOOSTS     — phraseBoost and titleBoost outside [0.0, 10.0] rejected
 * §SLOP       — slop < 0 or > 50 rejected
 * §RT-FILTER  — maxReadingTime < 1 rejected
 * §SORT-ORDER — sortOrder is free text (no constraint), passes always
 * §PAIRWISE   — cross-field combinations that should all pass/fail
 */
@DisplayName("SearchParams Validation Tests")
class SearchParamsValidationTest {

    private static Validator validator;

    @BeforeAll
    static void buildValidator() {
        validator = Validation.buildDefaultValidatorFactory().getValidator();
    }

    private SearchParams valid() {
        var p = new SearchParams();
        p.setQuery("quantum physics");
        p.setPage(1);
        p.setSize(10);
        p.setFuzziness("AUTO");
        p.setPhraseBoost(2.0f);
        p.setTitleBoost(1.5f);
        p.setSlop(0);
        return p;
    }

    private Set<ConstraintViolation<SearchParams>> validate(SearchParams p) {
        return validator.validate(p);
    }

    // ── §VALID ────────────────────────────────────────────────────────────

    @Test
    @DisplayName("§VALID: all defaults are valid")
    void allDefaultsValid() {
        assertThat(validate(valid())).isEmpty();
    }

    // ── §QUERY ────────────────────────────────────────────────────────────

    @ParameterizedTest
    @NullAndEmptySource
    @ValueSource(strings = {"  ", "\t", "\n"})
    @DisplayName("§QUERY: blank/null query fails @NotBlank")
    void blankQueryFails(String q) {
        var p = valid();
        p.setQuery(q);
        assertThat(validate(p)).isNotEmpty();
    }

    @Test
    @DisplayName("§QUERY: 1-char fails @Size(min=2)")
    void singleCharFails() {
        var p = valid();
        p.setQuery("x");
        assertThat(validate(p)).isNotEmpty();
    }

    @Test
    @DisplayName("§QUERY: exactly 2 chars passes")
    void twoCharsPass() {
        var p = valid();
        p.setQuery("ok");
        assertThat(validate(p)).isEmpty();
    }

    @Test
    @DisplayName("§QUERY: 501 chars fails @Size(max=500)")
    void tooLongQueryFails() {
        var p = valid();
        p.setQuery("a".repeat(501));
        assertThat(validate(p)).isNotEmpty();
    }

    @Test
    @DisplayName("§QUERY: exactly 500 chars passes")
    void maxLengthQueryPasses() {
        var p = valid();
        p.setQuery("a".repeat(500));
        assertThat(validate(p)).isEmpty();
    }

    // ── §PAGE ─────────────────────────────────────────────────────────────

    @ParameterizedTest
    @ValueSource(ints = {0, -1, -100})
    @DisplayName("§PAGE: page < 1 fails @Min(1)")
    void invalidPageFails(int page) {
        var p = valid();
        p.setPage(page);
        assertThat(validate(p)).isNotEmpty();
    }

    @Test
    @DisplayName("§PAGE: page = 1 passes")
    void page1Passes() {
        var p = valid();
        p.setPage(1);
        assertThat(validate(p)).isEmpty();
    }

    // ── §SIZE ─────────────────────────────────────────────────────────────

    @ParameterizedTest
    @ValueSource(ints = {0, -1, 51, 100})
    @DisplayName("§SIZE: size outside [1,50] fails")
    void invalidSizeFails(int size) {
        var p = valid();
        p.setSize(size);
        assertThat(validate(p)).isNotEmpty();
    }

    @ParameterizedTest
    @ValueSource(ints = {1, 10, 25, 50})
    @DisplayName("§SIZE: boundary values pass")
    void validSizePasses(int size) {
        var p = valid();
        p.setSize(size);
        assertThat(validate(p)).isEmpty();
    }

    // ── §BOOSTS ───────────────────────────────────────────────────────────

    @ParameterizedTest(name = "phraseBoost={0}")
    @CsvSource({"-0.1", "10.1", "-5.0", "11.0"})
    @DisplayName("§BOOSTS: phraseBoost outside [0.0,10.0] fails")
    void invalidPhraseBoostFails(float boost) {
        var p = valid();
        p.setPhraseBoost(boost);
        assertThat(validate(p)).isNotEmpty();
    }

    @ParameterizedTest(name = "phraseBoost={0}")
    @CsvSource({"0.0", "1.0", "5.0", "10.0"})
    @DisplayName("§BOOSTS: phraseBoost boundary values pass")
    void validPhraseBoostPasses(float boost) {
        var p = valid();
        p.setPhraseBoost(boost);
        assertThat(validate(p)).isEmpty();
    }

    @ParameterizedTest(name = "titleBoost={0}")
    @CsvSource({"-0.1", "10.1", "-5.0", "11.0"})
    @DisplayName("§BOOSTS: titleBoost outside [0.0,10.0] fails")
    void invalidTitleBoostFails(float boost) {
        var p = valid();
        p.setTitleBoost(boost);
        assertThat(validate(p)).isNotEmpty();
    }

    @ParameterizedTest(name = "titleBoost={0}")
    @CsvSource({"0.0", "1.0", "5.0", "10.0"})
    @DisplayName("§BOOSTS: titleBoost boundary values pass")
    void validTitleBoostPasses(float boost) {
        var p = valid();
        p.setTitleBoost(boost);
        assertThat(validate(p)).isEmpty();
    }

    // ── §SLOP ─────────────────────────────────────────────────────────────

    @ParameterizedTest
    @ValueSource(ints = {-1, 51, 100})
    @DisplayName("§SLOP: slop outside [0,50] fails")
    void invalidSlopFails(int slop) {
        var p = valid();
        p.setSlop(slop);
        assertThat(validate(p)).isNotEmpty();
    }

    @ParameterizedTest
    @ValueSource(ints = {0, 1, 25, 50})
    @DisplayName("§SLOP: slop boundary values pass")
    void validSlopPasses(int slop) {
        var p = valid();
        p.setSlop(slop);
        assertThat(validate(p)).isEmpty();
    }

    // ── §RT-FILTER ────────────────────────────────────────────────────────

    @Test
    @DisplayName("§RT-FILTER: maxReadingTime=0 fails @Min(1)")
    void zeroReadingTimeFails() {
        var p = valid();
        p.setMaxReadingTime(0);
        assertThat(validate(p)).isNotEmpty();
    }

    @Test
    @DisplayName("§RT-FILTER: maxReadingTime=-1 fails @Min(1)")
    void negativeReadingTimeFails() {
        var p = valid();
        p.setMaxReadingTime(-1);
        assertThat(validate(p)).isNotEmpty();
    }

    @Test
    @DisplayName("§RT-FILTER: maxReadingTime=1 passes")
    void oneReadingTimePasses() {
        var p = valid();
        p.setMaxReadingTime(1);
        assertThat(validate(p)).isEmpty();
    }

    @Test
    @DisplayName("§RT-FILTER: null maxReadingTime passes (filter is optional)")
    void nullReadingTimePasses() {
        var p = valid();
        p.setMaxReadingTime(null);
        assertThat(validate(p)).isEmpty();
    }

    // ── §SORT-ORDER ───────────────────────────────────────────────────────

    @ParameterizedTest
    @ValueSource(strings = {"asc", "desc", "ASC", "DESC", "random"})
    @DisplayName("§SORT-ORDER: sortOrder is unconstrained, any value passes")
    void sortOrderNoConstraint(String order) {
        var p = valid();
        p.setSortOrder(order);
        assertThat(validate(p)).isEmpty();
    }

    @Test
    @DisplayName("§SORT-ORDER: null sortOrder passes (no @NotBlank on sortOrder)")
    void nullSortOrderPasses() {
        var p = valid();
        p.setSortOrder(null);
        assertThat(validate(p)).isEmpty();
    }

    // ── §PAIRWISE ─────────────────────────────────────────────────────────

    @ParameterizedTest(name = "page={0}, size={1}")
    @CsvSource({
        "1,  1",  "1,  10", "1,  50",
        "10, 1",  "10, 10", "10, 50",
        "100,1",  "100,10", "100,50"
    })
    @DisplayName("§PAIRWISE(page×size): all valid boundary pairs pass")
    void pairwisePageSizeValid(int page, int size) {
        var p = valid();
        p.setPage(page);
        p.setSize(size);
        assertThat(validate(p)).isEmpty();
    }

    @ParameterizedTest(name = "phraseBoost={0}, titleBoost={1}")
    @CsvSource({
        "0.0,0.0", "0.0,5.0", "0.0,10.0",
        "5.0,0.0", "5.0,5.0", "5.0,10.0",
        "10.0,0.0","10.0,5.0","10.0,10.0"
    })
    @DisplayName("§PAIRWISE(phraseBoost×titleBoost): all valid boundary pairs pass")
    void pairwiseBoostsValid(float pb, float tb) {
        var p = valid();
        p.setPhraseBoost(pb);
        p.setTitleBoost(tb);
        assertThat(validate(p)).isEmpty();
    }

    @ParameterizedTest(name = "highlight={0}, spellCheck={1}, page={2}, size={3}")
    @CsvSource({
        "true,  true,  1,  10",
        "true,  false, 1,  10",
        "false, true,  1,  10",
        "false, false, 1,  10",
        "true,  true,  2,  25",
        "false, false, 2,  25",
    })
    @DisplayName("§PAIRWISE(highlight×spellCheck×page×size): boolean flag combos pass")
    void pairwiseFlagCombinations(boolean hl, boolean sc, int page, int size) {
        var p = valid();
        p.setHighlight(hl);
        p.setSpellCheck(sc);
        p.setPage(page);
        p.setSize(size);
        assertThat(validate(p)).isEmpty();
    }

    @ParameterizedTest(name = "phraseBoost={0}, titleBoost={1} → invalid")
    @CsvSource({
        "-1.0,  5.0",   // phraseBoost invalid
        "5.0,  -1.0",   // titleBoost invalid
        "-1.0, -1.0",   // both invalid
        "11.0,  5.0",   // phraseBoost too high
        "5.0,  11.0",   // titleBoost too high
    })
    @DisplayName("§PAIRWISE(phraseBoost×titleBoost): invalid boost pairs rejected")
    void pairwiseBoostsInvalid(float pb, float tb) {
        var p = valid();
        p.setPhraseBoost(pb);
        p.setTitleBoost(tb);
        assertThat(validate(p)).isNotEmpty();
    }
}
