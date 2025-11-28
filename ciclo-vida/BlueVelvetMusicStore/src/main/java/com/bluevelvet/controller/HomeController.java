package com.bluevelvet.controller;

import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.http.ResponseEntity;

import com.bluevelvet.payload.response.MessageResponse;

@CrossOrigin(origins = "*", maxAge = 3600)
@RestController
public class HomeController {

    @GetMapping("/")
    public ResponseEntity<?> home() {
        return ResponseEntity.ok(new MessageResponse(
                "Blue Velvet Music Store API está rodando! " +
                        "Acesse /h2-console para o banco de dados."
        ));
    }

    @GetMapping("/api/status")
    public ResponseEntity<?> status() {
        return ResponseEntity.ok(new MessageResponse("API Online - " + System.currentTimeMillis()));
    }
}