package com.bluevelvet.controller;

import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.http.ResponseEntity;

import com.bluevelvet.payload.response.MessageResponse;

/**
 * Home controller for root and status endpoints
 *
 * @brief Provides basic API information and health status endpoints
 * @author Developer
 */
@CrossOrigin(origins = "*", maxAge = 3600)
@RestController
public class HomeController {

    /**
     * @brief Root endpoint providing API information
     * @return ResponseEntity with welcome message and API status
     */
    @GetMapping("/")
    public ResponseEntity<?> home() {
        return ResponseEntity.ok(new MessageResponse(
                "Blue Velvet Music Store API is running. Access /h2-console for database management."
        ));
    }

    /**
     * @brief API status check endpoint
     * @return ResponseEntity with current API status and timestamp
     */
    @GetMapping("/api/status")
    public ResponseEntity<?> status() {
        return ResponseEntity.ok(new MessageResponse("API Online - System Time: " + System.currentTimeMillis()));
    }
}