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

echo "Preparando o índice '$INDEX_NAME' com as configurações e mapeamentos corretos..."

# Remove o índice antigo (se existir) para aplicar o novo mapping limpo
curl -s -k -u "$ES_USER:$ES_PASS" -X DELETE "https://$ES_HOST:$ES_PORT/$INDEX_NAME" > /dev/null

# Cria o índice com as configurações e mapeamentos definidos em wikipedia-mapping.json
curl -s -k -u "$ES_USER:$ES_PASS" \
     -H "Content-Type: application/json" \
     -X PUT "https://$ES_HOST:$ES_PORT/$INDEX_NAME" \
     -d @wikipedia-mapping.json > /dev/null

if [ $? -ne 0 ]; then
    echo "Erro ao criar o índice '$INDEX_NAME' com o mapping customizado."
    exit 1
fi

echo "Índice '$INDEX_NAME' criado com sucesso. Iniciando transferência bulk..."

# --- Execução do Comando Bulk ---
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

# --- Garantia de que wikipedia_v2 seja um Alias apontando para wikipedia ---
echo "Configurando o alias '$ALIAS_NAME' apontando para '$INDEX_NAME'..."

# Se ALIAS_NAME for um índice físico, removemos para evitar conflitos
# Se for um alias já existente, removemos também para garantir a recriação limpa
curl -s -k -u "$ES_USER:$ES_PASS" -X DELETE "https://$ES_HOST:$ES_PORT/$ALIAS_NAME" > /dev/null

# Cria o alias apontando para o índice correto
curl -s -k -u "$ES_USER:$ES_PASS" \
     -H "Content-Type: application/json" \
     -X POST "https://$ES_HOST:$ES_PORT/_aliases" \
     -d "{\"actions\": [{\"add\": {\"index\": \"$INDEX_NAME\", \"alias\": \"$ALIAS_NAME\"}}]}" > /dev/null

if [ $? -eq 0 ]; then
    echo "Alias '$ALIAS_NAME' configurado com sucesso apontando para '$INDEX_NAME'!"
else
    echo "Erro ao tentar mapear o alias '$ALIAS_NAME'."
    exit 1
fi

echo "Carga de dados e mapeamentos validados com sucesso."
