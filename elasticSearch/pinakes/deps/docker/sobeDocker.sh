#!/bin/bash

# ==============================================================================
# SCRIPT DE DEPLOY/INICIALIZAÇÃO DOCKER COMPOSE
# ------------------------------------------------------------------------------
# Descrição: Valida, constrói e levanta os serviços definidos no Compose.
# Uso: Ideal para após a limpeza ou para atualizar o ambiente de dev.
# ==============================================================================

# ------------------------------------------------------------------------------
# BLOCO DE VERIFICAÇÃO DE PRÉ-REQUISITOS
# Verifica se o arquivo docker-compose.yml (ou .yaml) existe no diretório atual.
# ------------------------------------------------------------------------------
if [[ ! -f "docker-compose.yml" && ! -f "docker-compose.yaml" ]]; then
    echo "ERRO: Arquivo docker-compose.yml não encontrado no diretório atual."
    exit 1
fi

echo "--- Iniciando a subida do ambiente ---"

# ------------------------------------------------------------------------------
# VALIDAÇÃO DE SINTAXE (OPCIONAL MAS PERTINENTE)
# O comando 'config' verifica se o arquivo YAML está bem formatado e se as 
# propriedades do Docker Compose são válidas antes de tentar o deploy.
# ------------------------------------------------------------------------------
echo "Validando arquivo de configuração..."
docker compose config -q || { echo "Falha na validação do YAML!"; exit 1; }

# ------------------------------------------------------------------------------
# CONSTRUÇÃO E SUBIDA (O CORAÇÃO DO SCRIPT)
# --build: Garante que as imagens locais sejam reconstruídas (evita usar cache antigo).
# -d: Modo 'detached' (em segundo plano).
# --remove-orphans: Remove containers que não estão mais definidos no arquivo atual.
# ------------------------------------------------------------------------------
echo "Executando: docker compose up -d --build --remove-orphans"

docker compose up -d --build --remove-orphans

# ------------------------------------------------------------------------------
# VERIFICAÇÃO DE SAÚDE (HEALTH CHECK)
# Após o comando, é útil listar o que realmente ficou de pé.
# ------------------------------------------------------------------------------
echo "---"
echo "Status atual dos serviços:"
docker compose ps

echo "---"
echo "DICA: Para acompanhar os logs em tempo real, use: docker compose logs -f"
