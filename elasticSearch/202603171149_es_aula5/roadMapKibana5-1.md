/* PASSO 1: Preparação do ambiente original.
   Aqui o índice pode ter sido criado com ou sem coerce, 
   mas queremos movê-lo para uma estrutura mais rigorosa.
*/
POST /coercion_test/_doc/1
{
  "nome": "Cafeteira Expressa",
  "preco": 150.50,         /* Float real */
  "quantidade": "10"       /* String que o coerce aceitou anteriormente */
}

/* PASSO 2: Criação do índice de destino com mapeamento rigoroso.
   Objetivo: Garantir que 'preco' e 'quantidade' sejam números puros
   e que 'nome' tenha uma versão estável para agregações.
*/
PUT /coercion_test_v2
{
  "settings": {
    "index.mapping.coerce": false /* Bloqueia conversões automáticas a partir de agora */
  },
  "mappings": {
    "properties": {
      "nome": { 
        "type": "text",
        "fields": { "raw": { "type": "keyword" } } /* Campo duplo para busca e métricas */
      },
      "preco": { "type": "float" },
      "quantidade": { "type": "integer" }
    }
  }
}

/* PASSO 3: Execução do Reindex com tratamento de dados.
   Usamos um script simples para garantir que a 'quantidade' 
   seja convertida para inteiro durante a viagem entre índices.
*/
POST /_reindex
{
  "source": {
    "index": "coercion_test"
  },
  "dest": {
    "index": "coercion_test_v2"
  },
  "script": {
    "inline": """
      if (ctx._source.quantidade instanceof String) {
        ctx._source.quantidade = Integer.parseInt(ctx._source.quantidade);
      }
    """
  }
}

/* PASSO 4: Troca de ponteiros (Alias).
   Removemos o nome 'produtos' do índice velho e apontamos para o novo.
   Isso permite manutenção sem downtime.
*/
POST /_aliases
{
  "actions": [
    { "remove_index": { "index": "coercion_test" } }, /* Cuidado: isso deleta o antigo! */
    { "add": { "index": "coercion_test_v2", "alias": "produtos_vendas" } }
  ]
}
