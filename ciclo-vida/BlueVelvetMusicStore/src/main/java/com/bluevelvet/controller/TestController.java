/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Test controller for access level validation and endpoint testing
 * @us US-0000 Shared - Granularity: Testing Endpoint
 */
package com.bluevelvet.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.bluevelvet.payload.response.MessageResponse;

/**
 * @brief Provides endpoints to verify different authorization levels and public
 *        access
 */
@CrossOrigin(origins = "*", maxAge = 3600)
@RestController
@RequestMapping("/api/test")
public class TestController {

    /**
     * @brief Public access test endpoint
     * @return ResponseEntity confirming public endpoint functionality
     */
    @GetMapping("/public")
    public ResponseEntity<?> publicAccess() {
        return ResponseEntity.ok(new MessageResponse("Public endpoint is operational"));
    }

    /**
     * @brief Authenticated user access test endpoint
     * @return ResponseEntity confirming user-level access
     */
    @GetMapping("/user")
    @PreAuthorize("hasRole('EDITOR') or hasRole('ASSISTANT') or hasRole('SALES_MANAGER') or hasRole('SHIPPING_MANAGER')")
    public ResponseEntity<?> userAccess() {
        return ResponseEntity.ok(new MessageResponse("User content access confirmed"));
    }

    /**
     * @brief Administrator access test endpoint
     * @return ResponseEntity confirming administrator-level access
     */
    @GetMapping("/admin")
    @PreAuthorize("hasRole('ADMINISTRATOR')")
    public ResponseEntity<?> adminAccess() {
        return ResponseEntity.ok(new MessageResponse("Administrator content access confirmed"));
    }

    /**
     * @brief Sales manager access test endpoint
     * @return ResponseEntity confirming sales manager-level access
     */
    @GetMapping("/sales")
    @PreAuthorize("hasRole('SALES_MANAGER')")
    public ResponseEntity<?> salesAccess() {
        return ResponseEntity.ok(new MessageResponse("Sales manager content access confirmed"));
    }
}
