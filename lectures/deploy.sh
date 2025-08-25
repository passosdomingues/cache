#!/bin/bash

SITE_ROOT="/var/www/nautilus.com/html"
PROJECT_PATH="$PWD"   # pasta onde estão os projetos
PROJECT_NAME="$1"     # nome da pasta do projeto a ser implantado

if [ -z "$PROJECT_NAME" ]; then
    echo "Use: ./deploy.sh nome_da_pasta_do_projeto"
    exit 1
fi

SOURCE="$PROJECT_PATH/$PROJECT_NAME"
if [ ! -d "$SOURCE" ]; then
    echo "Pasta do projeto '$PROJECT_NAME' não existe."
    exit 1
fi

# Gera timestamp YYYYMMDDHHMMSS
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
TARGET="$SITE_ROOT/${TIMESTAMP}_$PROJECT_NAME"

# Copia o projeto inteiro para a subpasta do Nginx
sudo cp -r "$SOURCE" "$TARGET"

# Testa e reinicia Nginx
sudo nginx -t && sudo systemctl restart nginx

echo "Projeto '$PROJECT_NAME' implantado em $TARGET"
echo "Acesse http://localhost/$(basename $TARGET)/"
