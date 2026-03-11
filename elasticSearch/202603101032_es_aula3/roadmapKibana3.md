/**
 * FASE 1: GERENCIAMENTO E LIMPEZA (ADMINISTRAÇÃO)
 * Antes de iniciar a aula, o professor verifica o estado atual do cluster e limpa 
 * resíduos de exercícios anteriores. No Docker/Kibana, isso é essencial para 
 * garantir que o ambiente esteja "puro" para novos testes.
 */

# Lista todos os índices existentes. O '?v' (verbose) exibe o cabeçalho.
# Serve para monitorar saúde (health), status e número de documentos.
GET /_cat/indices?v

# Remoção de índices antigos. Deletar um índice apaga os dados E os mapeamentos (mappings).
DELETE wiki_documents1
DELETE wiki_documents2
# Repetido apenas para confirmar a limpeza total da aula anterior.
DELETE wiki_documents1

/**
 * FASE 2: CRIAÇÃO E INGESTÃO DE DADOS (SCHEMALESS)
 * Aqui vemos a flexibilidade do Elasticsearch frente ao SQL tradicional.
 * O ES permite que documentos com diferentes estruturas coexistam no mesmo índice.
 */

# Criação explícita do índice. Embora o ES possa criar no primeiro POST, 
# o PUT garante que o índice exista antes de começarmos a popular.
PUT /produtos

# Inserção de documento simples. O ES gera um ID aleatório (ex: g7j615wB...).
# Note que "preco" é enviado como string aqui ("50").
POST /produtos/_doc
{
    "nome": "cafeteira",
    "preco": "50",
    "estoque": 20
}

# Inserção de outro registro básico.
POST /produtos/_doc
{
    "nome": "misteira",
    "preco": "60",
    "estoque": 20
}

# DEMONSTRAÇÃO DE FLEXIBILIDADE:
# Inserimos o campo "origem", que não existia nos outros documentos.
# No MySQL isso exigiria um ALTER TABLE. No ES, ele apenas cria um novo mapping dinâmico.
POST /produtos/_doc
{
    "nome": "cafeteira",
    "preco": "50",
    "origem": "China"
}

/**
 * FASE 3: OPERAÇÕES EM MASSA (BULK API) E INSPEÇÃO
 * O professor introduz o conceito de performance. Em produção, não inserimos
 * um por um, mas sim em lotes para reduzir o overhead de rede.
 */

# O _bulk exige um formato específico: um JSON de metadado seguido de um JSON de dados.
# Isso é processado de forma muito mais rápida pelo motor de busca.
POST /_bulk
{"index":{"_index": "produtos"}}
{"nome":"máquina de café espresso", "preco": 300, "estoque": 10}
{"index":{"_index": "produtos"}}
{"nome":"moedor de café", "preco": 40, "estoque": 10}

# Inspeciona as configurações do índice. Aqui você verá os 'mappings' gerados 
# por inferência e o 'creation_date' em formato Unix Time (milissegundos).
GET /produtos

# Busca global (match_all). Mostra os 'hits', o 'max_score' e o conteúdo original (_source).
GET /produtos/_search

/**
 * FASE 4: NORMALIZAÇÃO E BUSCA FULL-TEXT
 * O professor insere dados com variações de caixa (MAIÚSCULA/minúscula) 
 * para testar o poder dos Analyzers.
 */

# Inserindo nomes com caps lock para testar a normalização do Analyzer.
POST /produtos/_doc
{
    "nome": "CAFÉ GOURMET",
    "preco": "50",
    "estoque": 10
}

POST /produtos/_doc
{
    "nome": "CAfé",
    "preco": "50",
    "estoque": 10
}

# Busca com Query DSL: O termo "café" passa pelo Standard Analyzer, vira "cafe" 
# e busca no índice invertido. Vai encontrar tanto "cafeteira" quanto "CAFÉ GOURMET".
GET /produtos/_search
{
    "query": {
        "match": {
            "nome": "café"
        }
    }
}

# Teste de tolerância a acentos: Graças ao ASCII Folding (implícito ou explícito), 
# buscar "cafe" (sem acento) deve retornar documentos com "café".
GET /produtos/_search
{
    "query": {
        "match": {
            "nome": "cafe"
        }
    }
}

# Busca via URI (Query String): Atalho rápido para buscas simples via URL.
GET /produtos/_search?q=nome:café

/**
 * FASE 5: ANÁLISE PROFUNDA (THE ANALYSIS PIPELINE)
 * O comando final serve para "ver" a mente do Elasticsearch.
 * Mostra como o Standard Analyzer limpa espaços, pontuação e normaliza o texto.
 */

# Analisa como a frase será quebrada em tokens.
# O Standard Analyzer vai remover os pontos (...), a exclamação (!), o emoji (:-)) 
# e os espaços extras, transformando "DUCKS" em "ducks".
POST /_analyze
{
  "analyzer": "standard",
  "text": "2 guys walk into    a bar, but the third...    DUCKS! :-)"
}

# EXEMPLO 2: HTML Strip Character Filter.
# Útil para dados vindos da web. O 'html_strip' remove as tags <p> e <b>
# e decodifica entidades como '&apos;' para o apóstrofo "'".
POST /_analyze
{
    "text": "<p>I&apos;m so <b>happy</b>!</p>",
    "char_filter": ["html_strip"],
    "tokenizer": "standard",
    "filter": ["lowercase"]
}

# EXEMPLO 3: Mapping Character Filter (Substituição Direta).
# Aqui configuramos um filtro de mapeamento para trocar uma string por outra 
# ANTES da tokenização. Neste caso, simulamos trocar "happy" por "sad".
# Nota: O 'mappings' precisa estar dentro de uma definição de filtro 'mapping'.
POST /_analyze
{
  "tokenizer": "standard",
  "char_filter": [
    {
      "type": "mapping",
      "mappings": [
        "happy => sad"
      ]
    }
  ],
  "filter": ["lowercase"],
  "text": "I am so happy!"
}
