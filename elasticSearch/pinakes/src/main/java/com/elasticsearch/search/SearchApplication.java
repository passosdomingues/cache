package com.elasticsearch.search;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;

/**
 * Pinakes — Wikipedia full-text search engine.
 *
 * Architecture overview:
 *   SearchController  →  SearchService  →  EsClient
 *                    ↘  SuggestService  ↗
 *
 * Key design decisions:
 *   - All ES calls are encapsulated in EsClient; service layer is pure business logic.
 *   - @EnableAsync + CompletableFuture on the controllers for non-blocking HTTP.
 *   - Index name is externalized: never hard-coded; supports zero-downtime reindex via alias.
 */
@SpringBootApplication
@EnableAsync
public class SearchApplication {
    public static void main(String[] args) {
        SpringApplication.run(SearchApplication.class, args);
    }
}
