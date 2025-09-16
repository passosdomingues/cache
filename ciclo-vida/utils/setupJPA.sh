#!/bin/bash
#
# Script idempotente de instalação do Apache, MySQL, PHP e phpMyAdmin
# Compatível com Linux Mint 22.2 (base Ubuntu 24.04)
#

set -euo pipefail

APACHE_SERVICE="apache2"
MYSQL_SERVICE="mysql"
PHPMYADMIN_CONF="/etc/phpmyadmin/apache.conf"
APACHE_CONF_ENABLED="/etc/apache2/conf-enabled/phpmyadmin.conf"

log_info()    { echo -e "\e[34m[INFO]\e[0m $*"; }
log_success() { echo -e "\e[32m[SUCCESS]\e[0m $*"; }
log_error()   { echo -e "\e[31m[ERROR]\e[0m $*" >&2; }
abort()       { log_error "$*"; exit 1; }

check_root() {
    if [[ $EUID -ne 0 ]]; then
        abort "Este script deve ser executado como root (use sudo)."
    fi
}

check_env() {
    if [[ -z "${MYSQL_PASSWORD:-}" ]]; then
        abort "A variável de ambiente MYSQL_PASSWORD não está definida."
    fi
}

is_installed() {
    dpkg -s "$1" &>/dev/null
}

update_system() {
    log_info "Atualizando pacotes do sistema..."
    apt update -y && apt upgrade -y || abort "Falha ao atualizar pacotes."
    log_success "Sistema atualizado."
}

install_package() {
    local pkg="$1"
    if is_installed "$pkg"; then
        log_info "Pacote $pkg já está instalado."
    else
        log_info "Instalando $pkg..."
        apt install -y "$pkg" || abort "Falha ao instalar $pkg."
        log_success "$pkg instalado."
    fi
}

install_stack() {
    install_package apache2
    install_package mysql-server
    install_package php
    install_package libapache2-mod-php
    install_package php-mysql
    install_package php-mbstring
    install_package php-zip
    install_package php-gd
    install_package php-json
    install_package php-curl
}

install_phpmyadmin() {
    if is_installed phpmyadmin; then
        log_info "phpMyAdmin já está instalado."
    else
        log_info "Instalando phpMyAdmin..."
        DEBIAN_FRONTEND=noninteractive apt install -y phpmyadmin || abort "Falha ao instalar phpMyAdmin."
        log_success "phpMyAdmin instalado."
    fi
}

enable_php_extensions() {
    log_info "Ativando extensões do PHP..."
    phpenmod mbstring || true
    systemctl restart "$APACHE_SERVICE" || abort "Falha ao reiniciar o Apache."
    log_success "Extensões verificadas e Apache reiniciado."
}

configure_apache_phpmyadmin() {
    log_info "Verificando configuração do Apache para phpMyAdmin..."
    if [[ -f "$PHPMYADMIN_CONF" && ! -f "$APACHE_CONF_ENABLED" ]]; then
        ln -s "$PHPMYADMIN_CONF" "$APACHE_CONF_ENABLED" || abort "Falha ao linkar configuração phpMyAdmin no Apache."
        systemctl reload "$APACHE_SERVICE"
        log_success "phpMyAdmin habilitado no Apache."
    else
        log_info "Configuração do phpMyAdmin já habilitada."
    fi
}

configure_mysql_root() {
    log_info "Verificando autenticação do MySQL..."
    local plugin
    plugin=$(sudo mysql -N -B -e "SELECT plugin FROM mysql.user WHERE user='root' AND host='localhost';" || true)

    if [[ "$plugin" == "auth_socket" ]]; then
        log_info "Root está com auth_socket, alterando para senha..."
        sudo mysql <<EOF
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '${MYSQL_PASSWORD}';
FLUSH PRIVILEGES;
EOF
        log_success "Root configurado com senha da variável de ambiente."
    else
        log_info "Root já usa senha, testando conexão..."
        if mysql -uroot -p"${MYSQL_PASSWORD}" -e "SELECT 1;" &>/dev/null; then
            log_success "Conexão MySQL com root bem-sucedida."
        else
            abort "Falha ao autenticar no MySQL com a senha fornecida em MYSQL_PASSWORD."
        fi
    fi
}

show_access_info() {
    echo
    log_success "Provisionamento concluído."
    echo "Acesse: http://localhost/phpmyadmin"
    echo "Usuário: root"
    echo "Senha: (valor em \$MYSQL_PASSWORD)"
    echo "Recomenda-se rodar: mysql_secure_installation"
}

main() {
    check_root
    check_env
    update_system
    install_stack
    install_phpmyadmin
    enable_php_extensions
    configure_apache_phpmyadmin
    configure_mysql_root
    show_access_info
}

main "$@"

