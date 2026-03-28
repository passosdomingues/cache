/* =============================================================================
   PARTE 1: O ERRO CLÁSSICO (MAPPING PADRÃO / FLATTENED)
   ============================================================================= */

/* 1.1: Criamos o índice com um mapeamento explícito, mas sem o tipo 'nested'.
   Note que 'avaliacao' aqui é apenas um objeto comum. */
PUT /produtos
{
  "mappings": {
    "properties": {
      "nome": { "type": "text" },
      "avaliacao": {
        "properties": {
          "nota": { "type": "integer" },
          "autor": { "type": "text" },
          "descricao": { "type": "text" }
        }
      }
    }
  }
}

/* 1.2: Inserimos uma cafeteira com DUAS avaliações distintas.
   - Flavio: Nota 5
   - Jose: Nota 3
*/
POST /produtos/_doc/1
{
  "nome": "cafeteira",
  "avaliacao": [
    { "nota": 5, "autor": "Flavio", "descricao": "otimo produto" },
    { "nota": 3, "autor": "Jose", "descricao": "veio com defeito" }
  ]
}

/* 1.3: O PROBLEMA (Falso Positivo)
   A query abaixo busca "Jose" COM "nota >= 4". 
   LOGICAMENTE, não deveria retornar nada, pois Jose deu nota 3.
   RESULTADO: O documento SERÁ RETORNADO. Por quê?
   Porque o ES achata o vetor: ele vê [Flavio, Jose] e [5, 3]. 
   Como 'Jose' existe e '5' (>=4) também, ele dá o Match. */
GET /produtos/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "avaliacao.autor": "Jose" } },
        { "range": { "avaliacao.nota": { "gte": 4 } } }
      ]
    }
  }
}

/* =============================================================================
   PARTE 2: A SOLUÇÃO (TIPO NESTED)
   ============================================================================= */

/* 2.1: Deletamos o índice antigo. 
   Lembre-se: em produção (2bi de docs), mudar mapping exige Reindex. */
DELETE /produtos

/* 2.2: Recriamos com 'type': 'nested'. 
   Dica de Escala: Em cenários reais, usamos 'byte' para nota e 'keyword' para autor
   para economizar RAM em clusters gigantescos. */
PUT /produtos
{
  "mappings": {
    "properties": {
      "nome": { "type": "text" },
      "avaliacao": {
        "type": "nested", /* <-- A MAGIA: Isola cada objeto do vetor */
        "properties": {
          "nota": { "type": "integer" },
          "autor": { "type": "text" },
          "descricao": { "type": "text" }
        }
      }
    }
  }
}

/* 2.3: Re-inserimos os mesmos dados. 
   Agora o ES armazena o 'Jose' e a 'nota 3' em um documento oculto vinculado. */
POST /produtos/_doc/1
{
  "nome": "cafeteira",
  "avaliacao": [
    { "note": 5, "autor": "Flavio", "descricao": "otimo produto" },
    { "nota": 3, "autor": "Jose", "descricao": "veio com defeito" }
  ]
}

/* =============================================================================
   PARTE 3: A BUSCA PRECISA (WRAPPER NESTED)
   ============================================================================= */

/* 3.1: Agora a query usa o wrapper 'nested'. 
   Ele força o Elasticsearch a validar as condições DENTRO de cada 
   sub-documento isoladamente. */
GET /produtos/_search
{
  "query": {
    "nested": {
      "path": "avaliacao",
      "query": {
        "bool": {
          "must": [
            /* Agora o ES garante que o autor 'Jose' deve estar 
               no mesmo objeto que a nota > 4. */
            { "match": { "avaliacao.autor": "Jose" } },
            { "range": { "avaliacao.nota": { "gt": 4 } } }
          ]
        }
      }
    }
  }
}

/* RESULTADO DA QUERY ACIMA: 0 hits (Correto!).
   O Jose não tem nota maior que 4. A integridade foi mantida. */
