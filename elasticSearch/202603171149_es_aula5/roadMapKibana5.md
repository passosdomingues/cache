# 1.1 Testando o analisador Keyword (Saída: um único termo idêntico ao original)
POST /_analyze
{
   "text": "2 guys walk into     a bar, but the third...   DUCKS! :-)",
   "analyzer":"keyword"
}

# 1.2 Comparando com o analisador Standard (Saída: termos separados, minúsculos e sem símbolos)
POST /_analyze
{
   "text": "2 guys walk into     a bar, but the third...   DUCKS! :-)",
   "analyzer":"standard"
}

# 2.1 Analisando uma string única
POST /_analyze
{
 "text": "Strings são concatenadas juntas.",
 "analyzer": "standard"
}

# 2.2 Analisando um vetor (Note que a lista de tokens gerada é a mesma!)
POST /_analyze
{
 "text": ["Strings são", "concatenadas juntas."],
 "analyzer": "standard"
}

# 3.1 Criando um índice restritivo
PUT /coercion_test
{
 "settings": {
   "index.mapping.coerce": "false" # Desabilita conversão automática de tipos
 },
 "mappings": {
   "dynamic": "strict",           # Bloqueia a criação de campos novos (imagem enviada)
   "properties": {
     "preco": { "type": "float" }
   }
 }
}

# 3.2 TESTE A: Isso vai falhar (Tentativa de inserir string num campo float com coerce: false)
POST /coercion_test/_doc
{
 "preco": "7.4"
}

# 3.3 TESTE B: Isso também vai falhar (Tentativa de inserir campo 'quantidade' não mapeado com dynamic: strict)
POST /coercion_test/_doc
{
 "preco": 7.4,
 "quantidade": 10
}


