#!/bin/bash

# ----------------------------
# Configurações gerais
# ----------------------------
DB_NAME="hostelapp_jdbc"
DB_USER="florentino"
DB_PASS="123456"
MYSQL_ROOT_PASS="$MYSQL_PASSWORD"  # Variável de ambiente com senha do root

BASE_DIR="$(pwd)"
SQL_SCRIPT="$BASE_DIR/SQL_Scripts/Hostel_App_SQL_Script_MySQL.sql"
EXAMPLE1_DIR="$BASE_DIR/Source_Code/MySQLConnectionTestJDBCDriverWithoutBuildTool"
EXAMPLE2_DIR="$BASE_DIR/Source_Code/MySQLConnectionTestJDBCDriverWithMaven"
EXAMPLE3_DIR="$BASE_DIR/Source_Code/MySQLConnectionTestJDBCDriverWithGradle"

MAIN_CLASS="xyz.pagliares.jdbc.Main"

# ----------------------------
# Função de log
# ----------------------------
log() { echo "[$(date +'%H:%M:%S')] $1"; }

# ----------------------------
# Adiciona dependência MySQL ao pom.xml
# ----------------------------
add_mysql_dependency() {
    local POM_FILE="$1/pom.xml"
    if [ ! -f "$POM_FILE" ]; then
        log "pom.xml não encontrado em $1, pulando dependência."
        return
    fi

    grep -q "<artifactId>mysql-connector-java</artifactId>" "$POM_FILE"
    if [ $? -eq 0 ]; then
        log "Dependência mysql-connector-java já presente em $POM_FILE"
    else
        log "Adicionando dependência mysql-connector-java em $POM_FILE"
        sed -i '/<\/dependencies>/ i\
        <dependency>\
            <groupId>mysql</groupId>\
            <artifactId>mysql-connector-java</artifactId>\
            <version>8.0.30</version>\
        </dependency>' "$POM_FILE"
        log "Dependência adicionada com sucesso."
    fi
}

# ----------------------------
# Setup inicial: banco, usuário, SQL, Maven
# ----------------------------
setup() {
    if [ -z "$MYSQL_ROOT_PASS" ]; then
        log "Erro: variável de ambiente MYSQL_PASSWORD não definida."
        return
    fi

    log "Criando banco $DB_NAME e usuário $DB_USER (caso não existam)..."
    mysql -u root -p"$MYSQL_ROOT_PASS" -e "
CREATE DATABASE IF NOT EXISTS $DB_NAME;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;" 2>/dev/null

    if [ $? -eq 0 ]; then
        log "Banco e usuário criados/verificados com sucesso."
    else
        log "Erro ao criar/verificar banco ou usuário. Verifique a senha do root."
        return
    fi

    if [ ! -f "$SQL_SCRIPT" ]; then
        log "Arquivo SQL não encontrado: $SQL_SCRIPT"
        return
    fi

    log "Verificando tabelas existentes..."
    EXISTING_TABLES=$(mysql -u "$DB_USER" -p"$DB_PASS" -D "$DB_NAME" -sse "SHOW TABLES;")
    if [ -n "$EXISTING_TABLES" ]; then
        read -rp "Tabelas já existem. Deseja mesclar dados (ignorar duplicatas)? [s/N]: " choice
        if [[ "$choice" =~ ^[Ss]$ ]]; then
            log "Importando SQL com merge (ignorando duplicatas)..."
            sed 's/INSERT INTO/INSERT IGNORE INTO/g' "$SQL_SCRIPT" | mysql -u "$DB_USER" -p"$DB_PASS" "$DB_NAME"
            log "Importação concluída com merge."
        else
            log "Importação cancelada pelo usuário."
        fi
    else
        log "Nenhuma tabela encontrada. Importando SQL completo..."
        mysql -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" < "$SQL_SCRIPT"
        if [ $? -eq 0 ]; then
            log "Importação de SQL concluída com sucesso."
        else
            log "Erro ao importar SQL. Verifique permissões ou conteúdo do arquivo."
        fi
    fi

    # Adiciona dependência MySQL nos projetos Maven
    add_mysql_dependency "$EXAMPLE2_DIR"
}

# ----------------------------
# Rodar exemplos
# ----------------------------
run_example1() {
    if [ -d "$EXAMPLE1_DIR" ]; then
        log "Rodando JDBC sem build tool..."
        cd "$EXAMPLE1_DIR" || return

        mkdir -p bin
        # Compila todos os arquivos .java e coloca os .class em bin/
        find . -name "*.java" > sources.txt
        javac -d bin -cp "lib/*:." @sources.txt
        rm sources.txt

        # Roda a classe principal a partir do diretório bin
        java -cp "bin:lib/*" "$MAIN_CLASS"
        if [ $? -eq 0 ]; then
            log "Exemplo 01 executado com sucesso."
        else
            log "Erro ao executar Exemplo 01."
        fi
    else
        log "Diretório do Exemplo 01 não encontrado."
    fi
}

run_example2() {
    if [ -d "$EXAMPLE2_DIR" ]; then
        log "Rodando JDBC com Maven..."
        cd "$EXAMPLE2_DIR" || return
        mvn clean compile exec:java -Dexec.mainClass="$MAIN_CLASS"
        if [ $? -eq 0 ]; then
            log "Exemplo 02 executado com sucesso."
        else
            log "Erro ao executar Exemplo 02."
        fi
    else
        log "Diretório do Exemplo 02 não encontrado."
    fi
}

run_example3() {
    if [ -d "$EXAMPLE3_DIR" ]; then
        log "Rodando JDBC com Gradle..."
        cd "$EXAMPLE3_DIR" || return
        ./gradlew build && ./gradlew run
        if [ $? -eq 0 ]; then
            log "Exemplo 03 executado com sucesso."
        else
            log "Erro ao executar Exemplo 03."
        fi
    else
        log "Diretório do Exemplo 03 não encontrado."
    fi
}

# ----------------------------
# Menu interativo
# ----------------------------
while true; do
    echo ""
    echo "===== Menu JDBC Hands-on ====="
    echo "1) Setup inicial (banco, usuário, tabelas, dependência Maven)"
    echo "2) Rodar JDBC sem build tool"
    echo "3) Rodar JDBC com Maven"
    echo "4) Rodar JDBC com Gradle"
    echo "5) Sair"
    echo "==============================="
    read -rp "Escolha uma opção: " opt

    case $opt in
        1) setup ;;
        2) run_example1 ;;
        3) run_example2 ;;
        4) run_example3 ;;
        5) log "Saindo..."; exit 0 ;;
        *) log "Opção inválida" ;;
    esac
done

