#!/bin/bash

# --- Configurações ---
ES_USER="elastic"
ES_PASS="user123"
ES_HOST="localhost"
ES_PORT="9200"
INDEX_NAME="wikipedia"
FILE_NAME="wiki.json"

# --- Verificação de Arquivo ---
if [ ! -f "$FILE_NAME" ]; then
    echo "Erro: O arquivo '$FILE_NAME' nao foi encontrado no diretorio atual."
    echo "Certifique-se de que o arquivo existe antes de rodar o script."
    exit 1
fi

echo "Arquivo '$FILE_NAME' localizado. Iniciando transferencia para o Elasticsearch..."

# --- Execução do Comando ---
# -u: Autenticação básica
# -k: Ignora verificação de certificado SSL (insecure)
# -H: Define o header para NDJSON
# -XPOST: Método de envio para a API _bulk
# --data-binary: Envia o conteúdo preservando quebras de linha

RESPONSE=$(curl -s -u "$ES_USER:$ES_PASS" \
     -k \
     -H "Content-Type: application/x-ndjson" \
     -X POST "https://$ES_HOST:$ES_PORT/$INDEX_NAME/_bulk" \
     --data-binary "@$FILE_NAME")

# --- Verificação de Resposta ---
if [ $? -eq 0 ]; then
    echo "Comando enviado com sucesso."
    echo "Verifique o status da indexacao no Kibana ou via API de contagem."
else
    echo "Erro ao tentar se comunicar com o Elasticsearch."
    exit 1
fi
