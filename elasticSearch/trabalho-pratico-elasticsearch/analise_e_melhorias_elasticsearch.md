# Análise Técnica & Plano de Melhorias — Search Application
> Baseado no curso de Elasticsearch (mar–abr 2026) e nas classes `EsClient.java`, `SearchController.java`, `SearchApplication.java`

---

## 1. Estado Atual — O Que Já Está Bem

| O que existe | Por quê é bom |
|---|---|
| Boolean query (`must` + `should`) | Estrutura correta: o `must` garante relevância mínima, os `should` aumentam o score sem excluir resultados |
| Fuzziness `AUTO` | Tolera erros de digitação via distância de Levenshtein |
| `match_phrase` com boost no `should` | Promove frases exatas sem torná-las obrigatórias — boa prática de ranking |
| Highlight com `<strong>` e `fragment_size=400` | Mostra contexto suficiente para o usuário julgar a relevância |
| Term Suggest com `SuggestMode.Missing` | Só sugere correções para palavras ausentes do índice — evita ruído |
| Paginação com `from`/`size` | Implementação matematicamente correta |
| `CompletableFuture` no controller | Resposta assíncrona — boa base para escalabilidade |

---

## 2. Problemas Identificados e Melhorias no `EsClient.java`

### 2.1 Busca apenas no índice `wikipedia` (hardcoded)
**Problema:** `INDEX = "wikipedia"` está fixo. Quando o índice evoluir para `wikipedia_v2` (conforme o reindex da aula de 13/04), a aplicação não acompanha.

**Solução:** Externalizar para `application.properties` via `@Value`.

```java
@Value("${elasticsearch.index:wikipedia_v2}")
private String index;
```

---

### 2.2 `multi_match` ausente — busca só em `content`
**Problema:** O `must` atual busca apenas no campo `content`. Documentos muito relevantes pelo `title` só recebem um boost no `should`, mas nunca são obrigatórios.

**Melhoria:** Usar `multi_match` no `must` cobrindo `title^2` e `content`:

```java
// Antes
.must(m -> m.match(mq -> mq.field("content").query(query).fuzziness(fuzz)))

// Depois
.must(m -> m.multiMatch(mm -> mm
    .fields("title^2", "content")
    .query(query)
    .fuzziness(fuzz)
    .type(TextQueryType.BestFields)
))
```

Isso garante que um artigo cujo *título* seja exatamente o termo buscado sempre apareça no topo.

---

### 2.3 Ausência de `filter` para campos numéricos/data
**Problema:** Não existe nenhum mecanismo de filtragem por `reading_time` ou `dt_creation`. O filter não afeta o score (conforme aula de 30/03), logo é a ferramenta certa para refinamentos pós-busca.

**Adição recomendada ao `search()`:**

```java
// Parâmetros novos na assinatura
Integer maxReadingTime, String dateFrom, String dateTo

// Dentro do boolQuery
.filter(f -> {
    if (maxReadingTime != null)
        f.range(r -> r.field("reading_time").lte(JsonData.of(maxReadingTime)));
    if (dateFrom != null || dateTo != null)
        f.range(r -> {
            r.field("dt_creation");
            if (dateFrom != null) r.gte(JsonData.of(dateFrom));
            if (dateTo != null)   r.lte(JsonData.of(dateTo));
            return r;
        });
    return f;
})
```

---

### 2.4 `_source` retornando `content` inteiro
**Problema:** A linha `.source(src -> src.filter(f -> f.includes("title", "url", "content")))` puxa o campo `content` completo — que pode ter centenas de KB — mesmo quando o highlight já fornece o fragmento relevante.

**Solução:** Quando `highlight=true`, excluir `content` do `_source`:

```java
List<String> includes = hl
    ? List.of("title", "url")
    : List.of("title", "url", "content");

req.source(src -> src.filter(f -> f.includes(includes)));
```

Isso pode reduzir o payload de resposta em 10–50x dependendo do documento.

---

### 2.5 Suggest com vocabulário pós-analyzer
**Problema:** Conforme discutido na aula de 13/04, o suggest retorna termos do índice invertido *após* o analyzer (asciifolding + lowercase + snowball). Então "Schrödinger" vira "schroding" — inútil para exibir ao usuário.

**Solução:** Adicionar um subcampo `content.raw_suggest` com analyzer simples (sem snowball) apenas para o suggest:

```json
// No mapping do índice
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

E apontar o suggest para `content.raw_suggest` em vez de `content`.

---

### 2.6 Ausência de `sort` configurável
**Problema:** O ranking é sempre pelo score BM25. Conforme aula de 31/03, o usuário pode querer ordenar por `reading_time` ou por data.

**Adição:**

```java
// Parâmetro: String sortField, String sortOrder
if (sortField != null) {
    req.sort(s -> s.field(f -> f
        .field(sortField)
        .order("asc".equals(sortOrder) ? SortOrder.Asc : SortOrder.Desc)
    ));
}
```

---

### 2.7 `minimum_should_match` não configurado
**Problema:** Quando o usuário digita uma query longa (ex: "randomized binary search tree"), os `should` são todos opcionais. Documentos que casem com apenas 1 dos 4 termos podem aparecer.

**Melhoria:** Adicionar `minimumShouldMatch("1")` ao boolean query como fallback seguro.

---

### 2.8 Named Queries ausentes (debugging/analytics)
**Oportunidade:** Adicionar `_name` às cláusulas (aula de 30/03) permite ao backend logar *quais* cláusulas contribuíram para cada hit. Fundamental para tuning futuro do algoritmo de ranking.

```java
.must(m -> m.multiMatch(mm -> mm
    .fields("title^2", "content")
    .query(query)
    .fuzziness(fuzz)
    // não tem _name direto na Java API, mas pode ser feito via JSON nativo
))
```

---

### 2.9 Conexão sem pool / sem health check
**Problema:** `createConnection()` é chamado no construtor e nunca há reconexão automática. Se o ES cair e voltar, a aplicação precisa ser reiniciada.

**Solução:** Adicionar `@Bean` com `@ConditionalOnMissingBean`, externalizar configuração para um `ElasticsearchConfig`, e usar retry com `spring-retry`.

---

## 3. Melhorias no `SearchController.java`

### 3.1 `spellCheck` ignorado
**Bug:** O parâmetro `spellCheck` é recebido mas *nunca* passado ao `searchService.search(...)`. O suggest nunca é chamado automaticamente.

**Correção:**

```java
return CompletableFuture.supplyAsync(() -> {
    SearchResponse response = searchService.search(
        query, currentPage, pageSize, fuzziness,
        phraseBoost, titleBoost, slop, highlight
    );
    
    // Chamar suggest quando spellCheck=true E poucos resultados
    if (Boolean.TRUE.equals(spellCheck)) {
        response.setSuggestions(searchService.suggest(query, 3));
    }
    
    return ResponseEntity.ok(response);
});
```

### 3.2 Endpoint de suggest separado faltando
O `SearchApi` provavelmente expõe `/suggest` como endpoint próprio, mas o controller não o implementa. Adicionar:

```java
@Override
public CompletableFuture<ResponseEntity<SuggestResponse>> suggest(String query, Integer size) {
    return CompletableFuture.supplyAsync(() -> {
        SuggestResponse response = searchService.suggest(query, size);
        return ResponseEntity.ok(response);
    });
}
```

### 3.3 Validação de entrada ausente
Sem `@Valid` e `@NotBlank`, uma query vazia `""` ou `null` chega ao ES e gera um erro 500 em vez de um 400 claro.

```java
public CompletableFuture<ResponseEntity<SearchResponse>> search(
    @NotBlank @Size(min=2, max=500) String query, ...)
```

---

## 4. Novas Funcionalidades a Implementar

### 4.1 Endpoint de Agregações `/stats`
Conforme aula de 07/04, o ES possui agregações poderosas. Um endpoint `/stats` pode retornar:

```json
{
  "total_articles": 15420,
  "avg_reading_time": 7.3,
  "reading_time_distribution": { "rápido": 4200, "médio": 8100, "demorado": 3120 }
}
```

Query ES correspondente:
```json
GET /wikipedia_v2/_search
{
  "size": 0,
  "aggs": {
    "stats_reading": { "stats": { "field": "reading_time" } },
    "by_label": { "terms": { "field": "label" } }
  }
}
```

### 4.2 Endpoint `/autocomplete` com `match_phrase_prefix`
Para sugestões em tempo real enquanto o usuário digita (tipo Google Instant):

```java
Query autocompleteQuery = Query.of(q -> q.matchPhrasePrefix(mp -> mp
    .field("title")
    .query(partialQuery)
    .maxExpansions(10)
));
```

### 4.3 Highlight com `slop` customizado no bloco de highlight
Conforme aula de 06/04, o `highlight_query` pode ter critérios diferentes do `query` principal. Ideal para marcar frases próximas (com slop) mesmo quando a busca usa OR:

```java
req.highlight(h -> h
    .fields("content", hf -> hf
        .highlightQuery(hq -> hq.matchPhrase(mp -> mp
            .field("content")
            .query(query)
            .slop(s)
        ))
    )
);
```

---

## 5. Arquitetura Recomendada (Camadas)

```
SearchController
    └── SearchService (orquestra lógica de negócio)
            ├── EsClient.search()       → hits + highlight
            ├── EsClient.suggest()      → correções ortográficas
            ├── EsClient.autocomplete() → sugestões em tempo real
            └── EsClient.stats()        → agregações

SearchResponseMapper
    └── Converte ObjectNode do ES → DTOs tipados da API
```

---

## 6. Plano de UX/UI para o Frontend

### Filosofia: "Encontre em segundos, entenda em minutos"
Inspiração: Perplexity AI + Google Scholar + Wikiwand

---

### 6.1 Página Principal (Search Home)

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│              [ LOGO / NOME DA FERRAMENTA ]              │
│                                                         │
│   ┌───────────────────────────────────────────┐  [🔍]  │
│   │  Busque artigos da Wikipédia...            │        │
│   └───────────────────────────────────────────┘        │
│                                                         │
│   Sugestões: [matematica]  [binary search]  [physics]   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Comportamentos:**
- Autocomplete aparece após 2 caracteres (chama `/autocomplete`)
- Sugestões de trending (top buscas) exibidas antes de digitar
- Enter ou clique no ícone submete a busca

---

### 6.2 Página de Resultados (SERP)

```
┌─────────────────────────────────────────────────────────┐
│  [Logo]  [binary search___________] [🔍]                │
├─────────────────────────┬───────────────────────────────┤
│  FILTROS                │  RESULTADOS                   │
│                         │                               │
│  Tempo de leitura       │  ✅ "Você quis dizer: binary  │
│  ○ Rápido (≤5 min)      │     search tree?"             │
│  ○ Médio  (≤10 min)     │                               │
│  ○ Demorado             │  1 of 137 results (47ms)      │
│                         │                               │
│  Data de criação        │  ┌─────────────────────────┐ │
│  [De: ____] [Até: ____] │  │ Binary search algorithm  │ │
│                         │  │ en.wikipedia.org/wiki/.. │ │
│  Ordenar por            │  │ ...uses a <strong>binary  │ │
│  ○ Relevância (BM25)    │  │ search</strong> strategy │ │
│  ○ Mais recente         │  │ to locate the target...  │ │
│  ○ Menor tempo leitura  │  │ ⏱ 8 min  📅 2021-03-14  │ │
│                         │  └─────────────────────────┘ │
│  Opções avançadas ▼     │                               │
│  Fuzziness: [AUTO ▾]    │  ┌─────────────────────────┐ │
│  Phrase boost: [2.0]    │  │ Treap                    │ │
│  Title boost: [1.5]     │  │ ...                      │ │
│  Slop: [0]              │  └─────────────────────────┘ │
│                         │                               │
│                         │  [← 1  2  3 ... 14  →]       │
└─────────────────────────┴───────────────────────────────┘
```

---

### 6.3 Componentes UX Críticos

| Componente | Comportamento | Endpoint |
|---|---|---|
| **Barra de busca** | Autocomplete após 200ms de debounce | `GET /autocomplete?q=...` |
| **Spell check** | Banner amarelo "Você quis dizer: X?" com link | `GET /suggest?query=...` |
| **Highlight** | Termos em negrito no snippet, cor de destaque | Retornado pelo `/search` |
| **Filtro tempo leitura** | Chips clicáveis (Rápido / Médio / Demorado) | `?maxReadingTime=5` |
| **Filtro data** | Date picker range | `?dateFrom=...&dateTo=...` |
| **Ordenação** | Dropdown (Relevância / Mais recente / Menor tempo) | `?sortField=dt_creation&sortOrder=desc` |
| **Paginação** | Numérica + setas, exibe "X resultados (Yms)" | `?page=2&size=10` |
| **Painel avançado** | Collapsible, para tuning de hyperparâmetros | Todos os params do `/search` |
| **Stats sidebar** | Total de artigos, média de leitura | `GET /stats` |

---

### 6.4 Fluxo "Did You Mean?" (Correção ortográfica)

```
Usuário digita: "kolmogrov equatins"
         │
         ▼
GET /search?query=kolmogrov+equatins&spellCheck=true
         │
         ├── ES retorna 0 ou poucos hits (must não casou)
         │
         └── Suggest retorna: ["kolmogorov", "equations"]
                   │
                   ▼
         Frontend exibe: 🔍 "Você quis dizer: kolmogorov equations?"
         [Clique] → nova busca com termo corrigido
```

---

### 6.5 Métricas de Qualidade a Monitorar

Com o campo `matched_queries` (Named Queries) nos logs:

- **CTR por posição**: qual resultado o usuário clicou
- **Taxa de uso do spell check**: % de buscas que ativaram sugestão
- **Tempo médio de resposta** por tipo de query
- **Queries com 0 resultados**: candidatas para melhoria do índice

---

## 7. Resumo das Prioridades

| Prioridade | Item | Impacto |
|---|---|---|
| 🔴 **Crítico** | Bug: `spellCheck` ignorado no controller | Funcionalidade quebrada |
| 🔴 **Crítico** | `_source` retornando `content` completo | Performance / payload |
| 🟠 **Alto** | `multi_match` no `must` (title + content) | Qualidade de ranking |
| 🟠 **Alto** | Filtros por `reading_time` e `dt_creation` | UX + relevância percebida |
| 🟠 **Alto** | Suggest apontando para subcampo sem snowball | Qualidade das sugestões |
| 🟡 **Médio** | Endpoint `/autocomplete` com `match_phrase_prefix` | UX (Google-like) |
| 🟡 **Médio** | Endpoint `/stats` com agregações | Dashboard / UX |
| 🟡 **Médio** | Validação de entrada (`@NotBlank`, `@Size`) | Robustez |
| 🟢 **Baixo** | `minimum_should_match` configurável | Tuning de precisão |
| 🟢 **Baixo** | Configuração externalizada (`application.properties`) | Manutenibilidade |
