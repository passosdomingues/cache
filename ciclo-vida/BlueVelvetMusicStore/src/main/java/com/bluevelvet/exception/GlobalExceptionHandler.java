/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025-12-08
 * @brief Global exception handler for the application.
 * @us US-0000 Shared - Granularity: Exception Handling
 */
package com.bluevelvet.exception;

import jakarta.persistence.EntityNotFoundException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;

/**
 * @brief Handles exceptions globally across the application.
 */
@ControllerAdvice
public class GlobalExceptionHandler {

    /**
     * @brief Handles EntityNotFoundException.
     * @param ex The exception instance.
     * @return A ResponseEntity containing the error message and HTTP status
     *         NOT_FOUND.
     */
    @ExceptionHandler(EntityNotFoundException.class)
    public ResponseEntity<String> handleEntityNotFoundException(EntityNotFoundException ex) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(ex.getMessage());
    }
}
