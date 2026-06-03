package com.elasticsearch.search.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/**
 * Typed configuration bean for search defaults.
 * All values are overridable via application.properties or env vars.
 */
@Data
@Component
@ConfigurationProperties(prefix = "search.default")
public class SearchProperties {
    private int pageSize = 10;
    private int maxPageSize = 50;
    private int fragmentSize = 400;
    private int numFragments = 1;
    private String fuzziness = "AUTO";
    private float phraseBoost = 2.0f;
    private float titleBoost = 1.5f;
    private int slop = 0;
    private int minimumShouldMatch = 1;
}
