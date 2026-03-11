#!/bin/bash

# ==============================================================================
# SCRIPT DE LIMPEZA COMPLETA DO DOCKER (Debian/Ubuntu)
# ------------------------------------------------------------------------------
# Descrição: Este script remove todos os containers, imagens, redes e volumes.
# Uso: Recomendado apenas para ambientes de DESENVOLVIMENTO ou TESTES.
# Cuidado: Esta ação é irreversível e apagará todos os dados de volumes!
# ==============================================================================

echo "Iniciando a limpeza do ambiente Docker..."

# ------------------------------------------------------------------------------
# 1. PARAR CONTAINERS EM EXECUÇÃO
# O comando 'docker ps -q' lista apenas os IDs dos containers ativos.
# Se houver algo rodando, o script envia o sinal de parada.
# ------------------------------------------------------------------------------
if [ "$(docker ps -q)" ]; then
    echo "Parando containers em execução..."
    docker stop $(docker ps -q)
else
    echo "Nenhum container em execução para parar."
fi

# ------------------------------------------------------------------------------
# 2. REMOVER TODOS OS CONTAINERS
# O comando 'docker ps -aq' captura todos os IDs (ativos e inativos).
# ------------------------------------------------------------------------------
if [ "$(docker ps -aq)" ]; then
    echo "Removendo todos os containers..."
    docker rm $(docker ps -aq)
else
    echo "Nenhum container encontrado para remover."
fi

# ------------------------------------------------------------------------------
# 3. LIMPEZA DE SISTEMA (PRUNE)
# O parâmetro '-a' remove imagens não utilizadas (não apenas as 'dangling').
# O parâmetro '--volumes' garante a remoção de volumes anônimos.
# O parâmetro '-f' (force) pula a confirmação manual do terminal.
# ------------------------------------------------------------------------------
echo "Removendo imagens, redes e cache não utilizados..."
docker system prune -a --volumes -f

# ------------------------------------------------------------------------------
# 4. REMOVER VOLUMES NOMEADOS
# Como o 'system prune' às vezes mantém volumes nomeados específicos,
# este comando força a exclusão de absolutamente todos os volumes listados.
# ------------------------------------------------------------------------------
if [ "$(docker volume ls -q)" ]; then
    echo "Removendo volumes restantes..."
    docker volume rm $(docker volume ls -q)
else
    echo "Nenhum volume encontrado para remover."
fi

echo "---"
echo "Limpeza concluída com sucesso!"
docker ps -a
docker volume ls
