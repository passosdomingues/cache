/* =============================================================================
   PASSO 1: RESET DO AMBIENTE
   Para sistemas de PI, a consistência é tudo. Deletamos para reconfigurar.
   ============================================================================= */
DELETE /patentes

/* =============================================================================
   PASSO 2: MAPPING ESTRUTURADO (Foco em Escalabilidade e Precisão)
   No mundo real, uma patente tem múltiplos inventores e classificações (IPC).
   ============================================================================= */
PUT /patentes
{
  "settings": {
    "index": {
      "number_of_shards": 5,      /* Dividimos o índice para suportar bilhões de docs */
      "number_of_replicas": 1     /* Alta disponibilidade para buscas jurídicas */
    }
  },
  "mappings": {
    "dynamic": "strict",          /* Bloqueamos campos lixo para evitar Mapping Explosion */
    "properties": {
      "titulo": { "type": "text" },
      "resumo": { "type": "text" },
      "numero_registro": { "type": "keyword" }, /* IDs sempre como keyword */
      
      /* NESTED: Crucial para relacionar o Inventor à sua respectiva cota/parte */
      "inventores": {
        "type": "nested",
        "properties": {
          "nome": { "type": "keyword" },        /* Keyword para evitar confusão de nomes */
          "nacionalidade": { "type": "keyword" },
          "percentual_detencao": { "type": "byte" } /* Byte economiza espaço (0-100%) */
        }
      },
      
      "data_deposito": { "type": "date" }
    }
  }
}

/* =============================================================================
   PASSO 3: INDEXAÇÃO DE UM ATIVO COMPLEXO
   Aqui temos um sistema de "IA para Saúde" com dois inventores brasileiros.
   ============================================================================= */
POST /patentes/_doc/1001
{
  "titulo": "Algoritmo de Detecção Precoce de Glaucoma",
  "resumo": "Sistema baseado em redes neurais convolucionais para análise de retina.",
  "numero_registro": "BR1020260001-5",
  "data_deposito": "2026-03-16",
  "inventores": [
    {
      "nome": "Dr. Arnaldo Souza",
      "nacionalidade": "Brasileira",
      "percentual_detencao": 60
    },
    {
      "nome": "Eng. Beatriz Rocha",
      "nacionalidade": "Brasileira",
      "percentual_detencao": 40
    }
  ]
}

/* =============================================================================
   PASSO 4: A BUSCA JURÍDICA (QUERY NESTED)
   Cenário: Queremos encontrar patentes onde o "Dr. Arnaldo Souza" detenha
   pelo menos 50% dos direitos. 
   ============================================================================= */
GET /patentes/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "nested": {
            "path": "inventores",
            "query": {
              "bool": {
                "must": [
                  { "term": { "inventores.nome": "Dr. Arnaldo Souza" } }
                ],
                "filter": [
                  { "range": { "inventores.percentual_detencao": { "gte": 50 } } }
                ]
              }
            }
          }
        }
      ]
    }
  }
}

/* =============================================================================
   PASSO 5: OTIMIZAÇÃO DE MEMÓRIA (Disabling Indexing)
   ============================================================================= */

/* 5.1: Resetando o índice para aplicar a otimização */
DELETE /patentes

/* 5.2: Criando o Mapping com campos "Cegos" para o motor de busca */
PUT /patentes
{
  "mappings": {
    "dynamic": "strict", 
    "properties": {
      "titulo": { "type": "text" },
      "numero_registro": { "type": "keyword" },
      
      /* OTIMIZAÇÃO CHAVE: 
         'index': false diz ao Elasticsearch: "Guarde o dado no _source (disco),
         mas NÃO crie um Índice Invertido para ele". 
         Isso economiza MUITA RAM, pois não gera termos para o Heap gerenciar. */
      "texto_juridico_longo": { 
        "type": "text", 
        "index": false 
      },

      "inventores": {
        "type": "nested",
        "properties": {
          "nome": { "type": "keyword" },
          "nacionalidade": { "type": "keyword" },
          /* Doc Values são usados para agregações e ordenação. 
             Se você nunca for ordenar por percentual, poderia desabilitar também. */
          "percentual_detencao": { "type": "byte" }
        }
      }
    }
  }
}

/* 5.3: Inserindo um documento pesado */
POST /patentes/_doc/1002
{
  "titulo": "Processo Químico de Refino X",
  "numero_registro": "BR555",
  "texto_juridico_longo": "Um texto de 50.000 palavras que ninguém nunca vai pesquisar...",
  "inventores": [
    { "nome": "Maria Silva", "nacionalidade": "Portuguesa", "percentual_detencao": 100 }
  ]
}

/* 5.4: TESTE DE BUSCA (Vai falhar!)
   A query abaixo retornará erro ou 0 resultados porque o campo não está indexado. */
GET /patentes/_search
{
  "query": {
    "match": {
      "texto_juridico_longo": "palavras"
    }
  }
}
