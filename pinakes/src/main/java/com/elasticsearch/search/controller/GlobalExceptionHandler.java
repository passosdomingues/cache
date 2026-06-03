package com.elasticsearch.search.controller;

import jakarta.validation.ConstraintViolationException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/**
 * Global exception handler for REST controllers.
 *
 * Maps validation exceptions (from @Validated @RequestParam and @Valid @ModelAttribute)
 * to HTTP 400, preventing the default 500 leak for client-side input errors.
 *
 * ConstraintViolationException — thrown when @NotBlank / @Size etc. fail on
 *   @RequestParam parameters of a @Validated controller.
 * MethodArgumentNotValidException — thrown when @Valid @ModelAttribute or
 *   @RequestBody fails bean validation.
 * MissingServletRequestParameterException — missing required @RequestParam.
 */
@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ConstraintViolationException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ProblemDetail handleConstraintViolation(ConstraintViolationException ex) {
        log.debug("Constraint violation: {}", ex.getMessage());
        var pd = ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, ex.getMessage());
        pd.setTitle("Validation Error");
        return pd;
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ProblemDetail handleMethodArgumentNotValid(MethodArgumentNotValidException ex) {
        String detail = ex.getBindingResult().getFieldErrors().stream()
                .map(fe -> fe.getField() + ": " + fe.getDefaultMessage())
                .findFirst()
                .orElse("Invalid request parameters");
        log.debug("Method argument not valid: {}", detail);
        var pd = ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, detail);
        pd.setTitle("Validation Error");
        return pd;
    }

    @ExceptionHandler(MissingServletRequestParameterException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ProblemDetail handleMissingParam(MissingServletRequestParameterException ex) {
        log.debug("Missing request parameter: {}", ex.getParameterName());
        var pd = ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST,
                "Required parameter '" + ex.getParameterName() + "' is missing");
        pd.setTitle("Missing Parameter");
        return pd;
    }
}
