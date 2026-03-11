# ==============================================================================
# ROTEIRO DE AULA: EXPLORANDO CLUSTER, ÍNDICES E SHARDS
# ==============================================================================

# 1. Verificar os nós do cluster (formato simplificado)
GET /_cat/nodes

# 2. Verificar os nós com cabeçalhos detalhados (Verbose)
GET /_cat/nodes?v

# 3. Verificar a saúde do cluster (Green, Yellow ou Red)
GET /_cat/health?v

# --- OPERAÇÕES COM ÍNDICES ---

# 4. Criar o primeiro índice com configurações padrão (default)
PUT /wiki_documents1

# 5. Inspecionar as configurações e mapeamentos do índice criado
GET /wiki_documents1

# 6. Observar como os Shards foram distribuídos no disco
GET /_cat/shards?v

# 7. Listar todos os índices e comparar tamanhos e status
GET /_cat/indices?v

# --- CUSTOMIZAÇÃO DE ARQUITETURA ---

# 8. Criar um segundo índice definindo especificamente 2 Shards Primários
PUT /wiki_documents2
{
  "settings": {
    "number_of_shards": 2
  }
}

# 9. Validar se as configurações de 2 shards foram aplicadas
GET /wiki_documents2

# 10. Criar um terceiro índice com 1 Shard Primário e 3 Réplicas
# NOTA: Em um cluster de 1 nó (Docker), isso deixará o status em YELLOW.
PUT /wiki_documents3
{
  "settings": {
    "index": {
      "number_of_shards": 1,
      "number_of_replicas": 3
    }
  }
}

# 11. Verificar o impacto das 3 réplicas desalocadas nos Shards
GET /_cat/shards?v
