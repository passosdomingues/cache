package com.elasticsearch.search.unit;

import com.elasticsearch.search.model.SearchParams;
import jakarta.validation.ConstraintViolation;
import jakarta.validation.Validation;
import jakarta.validation.Validator;
import org.junit.jupiter.api.*;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

import java.util.Set;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Validates that SearchParams bean-validation constraints work correctly.
 * These prevent the §3.3 bug where invalid inputs reached ES and caused 500s.
 */
@DisplayName("SearchParams Validation Tests")
class SearchParamsValidationTest {

    private static Validator validator;

    @BeforeAll
    static void setupValidator() {
        validator = Validation.buildDefaultValidatorFactory().getValidator();
    }

    @Test
    @DisplayName("Valid params produce no violations")
    void validParamsPassValidation() {
        var p = new SearchParams();
        p.setQuery("binary search tree");
        Set<ConstraintViolation<SearchParams>> violations = validator.validate(p);
        assertThat(violations).isEmpty();
    }

    @Test
    @DisplayName("Blank query produces violation")
    void blankQueryFails() {
        var p = new SearchParams();
        p.setQuery("  ");
        var violations = validator.validate(p);
        assertThat(violations).isNotEmpty();
        assertThat(violations).anyMatch(v -> v.getPropertyPath().toString().equals("query"));
    }

    @Test
    @DisplayName("Null query produces violation")
    void nullQueryFails() {
        var p = new SearchParams();
        p.setQuery(null);
        var violations = validator.validate(p);
        assertThat(violations).isNotEmpty();
    }

    @ParameterizedTest
    @ValueSource(ints = {0, -1, -100})
    @DisplayName("Page ≤ 0 produces violation")
    void invalidPageFails(int page) {
        var p = new SearchParams();
        p.setQuery("test query");
        p.setPage(page);
        var violations = validator.validate(p);
        assertThat(violations).anyMatch(v -> v.getPropertyPath().toString().equals("page"));
    }

    @ParameterizedTest
    @ValueSource(ints = {51, 100, 1000})
    @DisplayName("Size > 50 produces violation")
    void oversizedPageFails(int size) {
        var p = new SearchParams();
        p.setQuery("test query");
        p.setSize(size);
        var violations = validator.validate(p);
        assertThat(violations).anyMatch(v -> v.getPropertyPath().toString().equals("size"));
    }

    @Test
    @DisplayName("Single character query fails min-length validation")
    void tooShortQueryFails() {
        var p = new SearchParams();
        p.setQuery("x");
        var violations = validator.validate(p);
        assertThat(violations).isNotEmpty();
    }

    @Test
    @DisplayName("Query at max boundary (500 chars) passes")
    void queryAtMaxBoundaryPasses() {
        var p = new SearchParams();
        p.setQuery("a".repeat(500));
        var violations = validator.validate(p);
        assertThat(violations).isEmpty();
    }

    @Test
    @DisplayName("Query exceeding max (501 chars) fails")
    void queryBeyondMaxFails() {
        var p = new SearchParams();
        p.setQuery("a".repeat(501));
        var violations = validator.validate(p);
        assertThat(violations).isNotEmpty();
    }

    @ParameterizedTest
    @ValueSource(floats = {-0.1f, 10.1f, 100f})
    @DisplayName("Out-of-range phraseBoost produces violation")
    void invalidPhraseBoostFails(float boost) {
        var p = new SearchParams();
        p.setQuery("valid query");
        p.setPhraseBoost(boost);
        var violations = validator.validate(p);
        assertThat(violations).isNotEmpty();
    }
}
