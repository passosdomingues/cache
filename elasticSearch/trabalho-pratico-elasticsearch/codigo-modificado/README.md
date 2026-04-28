# Pinakes -- Full-text Search Engine

Full-text search engine built on Elasticsearch 8, Spring Boot 3, and Thymeleaf.
Implements distributed search techniques including boolean queries, fuzzy matching,
term highlighting, spelling suggestions, and paginated results over a Wikipedia dataset.

## Architecture

| Layer | Technology |
|---|---|
| Search Engine | Elasticsearch 8.17 (2-node cluster) |
| Backend | Spring Boot 3.1.0 / Java 17 |
| ES Client | Elasticsearch Java API Client 8.8.0 |
| API Contract | OpenAPI 3.0 (`api.yml`) + Generator Plugin |
| Frontend | Thymeleaf + Vanilla JS (ES Modules) |
| Infrastructure | Docker Compose (Elasticsearch + Kibana) |

## Prerequisites

- Docker and Docker Compose
- JDK 17 (configured automatically via `make java-install`)

## Quick Start

```bash
# 1. Build and compile
make all

# 2. Seed the index with Wikipedia data
make seed

# 3. Run the application
make run
```

The application will be available at `http://localhost:8080/v1/`.

## Makefile Commands

| Command | Description |
|---|---|
| `make all` | Infrastructure + JDK setup + compile |
| `make run` | Start the application and open the browser |
| `make compile` | Compile the project with JDK 17 |
| `make seed` | Load the Wikipedia dataset into Elasticsearch |
| `make clean` | Remove build artifacts |
| `make test-api` | Run functional endpoint tests via curl |
| `make docs` | Generate architecture diagram and API docs |
| `make infra-up` | Start Elasticsearch and Kibana containers |
| `make infra-down` | Stop containers gracefully |

## API Endpoints

Base path: `http://localhost:8080/v1`

### GET /search

Full-text search with fuzzy matching, highlighting, and pagination.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `query` | string | yes | -- | Search terms |
| `page` | integer | no | 1 | Page number (1-indexed) |
| `size` | integer | no | 10 | Results per page |

### GET /suggest

Spelling correction via Elasticsearch Term Suggest.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `query` | string | yes | -- | Text with potential misspellings |
| `size` | integer | no | 3 | Suggestions per token |

## Frontend Features

- Dark / Light theme toggle with system preference detection
- Accessibility controls: font scaling and high contrast mode
- Sidebar menu with Elasticsearch course concepts reference
- Autocomplete with debounced suggestions from the suggest API
- Keyboard navigation for autocomplete dropdown
- Staggered card animations on search results
- "Did you mean?" banner for spelling corrections

## Elasticsearch Techniques Implemented

- Boolean query with `must` + `should` clauses
- Fuzzy matching via `fuzziness: AUTO` (Levenshtein distance)
- Match phrase with boost for exact sequence promotion
- Title field boost for multi-field relevance
- Highlighting with `<strong>` tags and configurable fragment size
- Source filtering to reduce response payload
- Pagination via `from`/`size` with total page computation
- Term Suggest for spelling correction
- Custom analyzers (asciifolding, lowercase, snowball)
- Bulk import via NDJSON format
- Metric aggregations (sum, avg, max, min, cardinality, stats)
- Reindex with ingest pipelines for computed fields

## Project Structure

```
src/main/java/com/elasticsearch/search/
  controller/
    SearchController.java       # REST /search (implements SearchApi)
    SuggestController.java      # REST /suggest (implements SuggestApi)
    SearchViewController.java   # MVC / (Thymeleaf)
  service/
    SearchService.java          # Business logic and ES response mapping
  domain/
    EsClient.java               # Low-level Elasticsearch client

src/main/resources/
  api.yml                       # OpenAPI 3.0 contract (source of truth)
  application.yml               # Spring Boot configuration
  templates/
    layout/base.html            # Root layout with header, footer, sidebar
    fragments/                  # Atomic Thymeleaf components
    search/index.html           # Main search page
  static/
    css/                        # Modular CSS (tokens, base, components)
    js/                         # ES Modules (services, components, hooks)
    favicon.svg                 # Application icon
```
