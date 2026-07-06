# Pinakes — Wikipedia Full-Text Search Engine

> Elasticsearch 8 · Spring Boot 3 · Thymeleaf · Docker · Python test suite
> Contributions: Marcos Vinicius de Paula

## Quick Start

```bash
# Start ES + app
make up

# Open browser
open http://localhost:8080

# Run full test suite + generate plots
make perf

# Stop everything
make down
```

---

## Architecture

```
SearchController  (MVC / Thymeleaf)
SearchApiController (REST JSON)
        │
        ▼
SearchService  ←──  QueryAnalyser
        │
        ▼
EsClient  ──────────────── ElasticSearch 8
  ├─ search()           boolean query + filters + sort
  ├─ suggestWord()      per-token spell correction (raw_suggest)
  ├─ autocomplete()     match_phrase_prefix on title
  └─ stats()            metric aggregations (size=0)
```

---

## Features & Improvements

### Bug fixes (from analysis document)

| # | Bug | Fix |
|---|-----|-----|
| §3.1 | `spellCheck` param silently discarded in controller | Now correctly wired through `SearchService` |
| §2.4 | `content` field (hundreds KB) always returned in `_source` | Excluded when `highlight=true`; payload reduced 10–50× |
| §2.5 | Suggest returned Snowball stems ("schroding") | Targets `content.raw_suggest` (standard analyser) |

### New capabilities

| Feature | Description |
|---------|-------------|
| **Exact phrase search** | Wrap terms in `"quotes"` → ES `match_phrase` MUST clause |
| **Holistic spell-check** | Per-token correction; casing preserved; HTML diff with `<strong class="correction">` on changed words |
| **Reading-time filter** | `?maxReadingTime=5` → filter clause (no score impact) |
| **Date range filter** | `?dateFrom=2020-01-01&dateTo=2022-12-31` |
| **Configurable sort** | `?sortField=reading_time&sortOrder=asc` |
| **Autocomplete** | `match_phrase_prefix` dropdown, quote-aware, 200ms debounce |
| **Stats endpoint** | `/api/stats` — aggregations: avg reading time, distribution, top labels |
| **Suggest endpoint** | `/api/suggest?query=...` — returns `correctedQueryHtml` |

---

## Spell-Check: Holistic Mode

**Problem** (original code): The suggest API returned stemmed roots from Snowball processing. "Schrödinger" → "schroding". Multi-word queries returned partial corrections.

**Solution** (this version):

1. `QueryAnalyser` tokenises the query into typed segments:
   - `WORD` — subject to spell-check
   - `QUOTED_PHRASE` — exact; never corrected
   - `PASSTHROUGH` — LaTeX, numbers, punctuation; emitted verbatim

2. For each `WORD` token, `EsClient.suggestWord()` issues **one ES request** against `content.raw_suggest` (no Snowball → real surface forms).

3. The original token's **casing style** is re-applied: `EINSIN` → `EINSTEIN`, `Einsin` → `Einstein`, `einsin` → `einstein`.

4. The response includes `correctedQueryHtml` — the full corrected query with each changed token in `<strong class="correction">`, so the UI can show exactly what changed.

**Example:**
```
Input:   Einsin's foula, \( E=mc^2 \), revolutiozed physics
Tokens:  [WORD:"Einsin's"] [PASS:","] [WORD:"foula"] [PASS:", \( E=mc^2 \),"] [WORD:"revolutiozed"] [WORD:"physics"]
Output:  Einstein's formula, \( E=mc^2 \), revolutionized physics
HTML:    <strong class="correction">Einstein's</strong> <strong class="correction">formula</strong>,
         \( E=mc^2 \), <strong class="correction">revolutionized</strong> physics
```

---

## Exact Phrase Search

Wrap any terms in double quotes to trigger `match_phrase`:

```
"binary search" tree         → exact "binary search" MUST, fuzzy "tree" SHOULD
"Treap" randomized           → exact "Treap" MUST, fuzzy "randomized" SHOULD
```

Autocomplete is suppressed while the cursor is inside a quoted phrase.

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Thymeleaf search UI |
| `GET` | `/api/search` | JSON search (all params) |
| `GET` | `/api/suggest` | Spell correction (holistic) |
| `GET` | `/api/autocomplete` | Prefix title suggestions |
| `GET` | `/api/stats` | Index aggregation statistics |
| `GET` | `/api/health` | Health check |

### Search parameters

| Param | Default | Description |
|-------|---------|-------------|
| `query` | required | Search query; use `"quotes"` for exact phrases |
| `page` | 1 | Page number |
| `size` | 10 | Results per page (max 50) |
| `fuzziness` | AUTO | Levenshtein distance (0, 1, 2, AUTO) |
| `phraseBoost` | 2.0 | Score multiplier for exact phrase hits |
| `titleBoost` | 1.5 | Score multiplier for title field hits |
| `slop` | 0 | Phrase slop (allowed word distance) |
| `highlight` | true | Include `<strong>` highlight fragments |
| `spellCheck` | true | Trigger holistic spell correction |
| `maxReadingTime` | — | Filter: articles ≤ N minutes |
| `dateFrom` / `dateTo` | — | Filter: date range (yyyy-MM-dd) |
| `sortField` | — | Sort by field (`reading_time`, `dt_creation`); null = BM25 |
| `sortOrder` | desc | `asc` or `desc` |

---

## Index Mapping

The ES index `wikipedia_v2` uses a custom analyser with:
- `standard` tokeniser
- `lowercase` + `asciifolding` + `english_snowball` filters

The key addition is the `content.raw_suggest` sub-field:
```json
"content": {
  "type": "text",
  "analyzer": "analyzer_for_content",
  "fields": {
    "raw_suggest": {
      "type": "text",
      "analyzer": "standard"
    }
  }
}
```
This sub-field retains real surface forms for the suggest vocabulary.

---

## Test Suite

### Unit tests (no Docker)
```bash
make test
```
Covers:
- `QueryAnalyserTest` — 15 tests: tokenisation, holistic correction, casing, quoted phrases, HTML diff, passthrough, edge cases
- `SearchParamsValidationTest` — 8 tests: bean validation constraints
- `SearchServiceTest` — 6 tests: spell-check wiring, pagination, graceful degradation

### Integration tests (requires Docker)
```bash
make integration
```
Spins up Elasticsearch 8 via Testcontainers, seeds 8 documents, and tests all search/suggest/autocomplete/stats/sort/filter paths against a real ES instance.

### Performance & quality suite
```bash
make perf
```
Python suite — runs against the live app and generates 10 publication-quality PNG figures (B&W, 300 dpi, serif font) plus a JSON report:

| Figure | Content |
|--------|---------|
| Fig 1 | Latency distribution + boxplot by tier |
| Fig 2 | Response time percentile curve |
| Fig 3 | nDCG@5, MRR, Precision@5 by query tier |
| Fig 4 | Payload size comparison (highlight on/off) |
| Fig 5 | Throughput vs. concurrency level |
| Fig 6 | Latency by query tier (Kruskal-Wallis) |
| Fig 7 | TF-IDF semantic similarity heatmap |
| Fig 8 | Classic spell-check evaluation |
| Fig 9 | Summary dashboard (paper-ready) |
| Fig 10 | Holistic spell-check (multi-word, HTML diff) |

Statistical methods used: Shapiro-Wilk / KS normality test, Wilcoxon signed-rank (payload), Kruskal-Wallis (tier comparison), TF-IDF cosine similarity (semantic proxy), nDCG@5, MRR, Precision@5.

---

## Make targets

```
make build         Compile JAR (skip tests)
make test          Unit tests only
make integration   Integration tests (Docker)
make test-all      All tests
make up            Start ES + app
make down          Stop containers
make perf          Full stack + Python test suite
make perf-docker   Performance suite in Docker (CI)
make logs          Tail all container logs
make clean         Remove everything
make ci            build + test + integration
```
