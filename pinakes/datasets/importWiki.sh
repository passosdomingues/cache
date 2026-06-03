#!/bin/bash

# --- Configurações ---
ES_USER="elastic"
ES_PASS="user123"
ES_HOST="localhost"
ES_PORT="9200"
INDEX_NAME="wikipedia"
ALIAS_NAME="wikipedia_v2"
FILE_NAME="wiki.json"

# --- Verificação de Arquivo ---
if [ ! -f "$FILE_NAME" ]; then
    echo "Erro: O arquivo '$FILE_NAME' nao foi encontrado no diretorio atual."
    echo "Certifique-se de que o arquivo existe antes de rodar o script."
    exit 1
fi

echo "Arquivo '$FILE_NAME' localizado. Iniciando transferencia para o Elasticsearch..."

# --- Execução do Comando Bulk ---
# Os IDs dentro do wiki.json garantem idempotência nativa no comando _bulk (sobrescreve se já existir)
curl -s -u "$ES_USER:$ES_PASS" \
     -k \
     -H "Content-Type: application/x-ndjson" \
     -X POST "https://$ES_HOST:$ES_PORT/$INDEX_NAME/_bulk" \
     --data-binary "@$FILE_NAME" > /dev/null

if [ $? -ne 0 ]; then
    echo "Erro ao tentar se comunicar com o Elasticsearch durante a carga bulk."
    exit 1
fi

echo "Comando bulk concluído com sucesso para o índice '$INDEX_NAME'."

# --- Garantia de Idempotência para o wikipedia_v2 ---
echo "Verificando a existência do índice ou alias '$ALIAS_NAME'..."
HTTP_STATUS=$(curl -s -k -u "$ES_USER:$ES_PASS" -o /dev/null -w "%{http_code}" "https://$ES_HOST:$ES_PORT/$ALIAS_NAME")

if [ "$HTTP_STATUS" -eq 200 ]; then
    echo "O índice ou alias '$ALIAS_NAME' já existe perfeitamente. Nenhuma ação necessária."
else
    echo "'$ALIAS_NAME' não encontrado (Status $HTTP_STATUS). Configurando apontamento automático..."
    
    # OPÇÃO A: Criar um Alias (Recomendado - Instantâneo e não duplica espaço em disco)
    curl -s -k -u "$ES_USER:$ES_PASS" \
         -H "Content-Type: application/json" \
         -X POST "https://$ES_HOST:$ES_PORT/_aliases" \
         -d "{\"actions\": [{\"add\": {\"index\": \"$INDEX_NAME\", \"alias\": \"$ALIAS_NAME\"}}]}" > /dev/null

    # OPÇÃO B: Se você preferir um Reindex físico em vez de Alias, comente a Opção A e descomente as linhas abaixo:
    # curl -s -k -u "$ES_USER:$ES_PASS" \
    #      -H "Content-Type: application/json" \
    #      -X POST "https://$ES_HOST:$ES_PORT/_reindex" \
    #      -d "{\"source\": {\"index\": \"$INDEX_NAME\"}, \"dest\": {\"index\": \"$ALIAS_NAME\"}}" > /dev/null

    if [ $? -eq 0 ]; then
        echo "Apontamento para '$ALIAS_NAME' estabelecido com sucesso!"
    else
        echo "Erro ao tentar mapear o índice '$ALIAS_NAME'."
        exit 1
    fi
fi

echo "Carga de dados e mapeamentos validados com sucesso."
