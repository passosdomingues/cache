#!/usr/bin/env bash
# lamp_manager_strict.sh
# LAMP atomic, modular, robust + WordPress installer and tester
# Linux Mint 22.2 (Ubuntu 24.04 LTS)
# Autor: Capitão Nemo
# Last Update: 2025-09-08
set -euo pipefail
IFS=$'\n\t'

LOG_FILE="/var/log/lamp_manager_strict.log"
TMP_DIR="/tmp/lamp_manager_strict"
WP_URL="https://wordpress.org/latest.tar.gz"
WP_WEBPATH="/var/www/html/wordpress"

# -------------------------
# utilitários
# -------------------------
_init() {
  sudo mkdir -p "$(dirname "$LOG_FILE")" "$TMP_DIR"
  sudo touch "$LOG_FILE"
  sudo chown "$(whoami):$(whoami)" "$LOG_FILE"
  mkdir -p "$TMP_DIR"
  command -v apt >/dev/null 2>&1 || { echo "apt não encontrado"; exit 1; }
}

log() {
  local msg="$*"
  local ts; ts="$(date +'%F %T')"
  echo "[$ts] $msg" | tee -a "$LOG_FILE"
}

safe_run() {
  local cmd="$*"
  log "EXEC: $cmd"
  if ! bash -c "$cmd"; then
    log "ERRO: comando falhou: $cmd"
    return 1
  fi
  return 0
}

pkg_installed() {
  dpkg -s "$1" >/dev/null 2>&1
}

apt_update_once() {
  if [ ! -f "$TMP_DIR/apt_updated" ]; then
    log "apt update..."
    sudo apt update -y || { log "apt update falhou"; return 1; }
    touch "$TMP_DIR/apt_updated"
  fi
}

install_pkg_if_missing() {
  local pkg="$1"
  if pkg_installed "$pkg"; then
    log "pacote $pkg já instalado"
    return 0
  fi
  apt_update_once || return 1
  log "instalando $pkg"
  sudo apt install -y "$pkg" || { log "falha ao instalar $pkg"; return 1; }
  return 0
}

# -------------------------
# diagnóstico de Apache
# -------------------------
apache_config_test() {
  if command -v apachectl >/dev/null 2>&1; then
    if ! sudo apachectl configtest >/dev/null 2>&1; then
      log "apachectl configtest falhou - mostrando saída"
      sudo apachectl configtest || true
      return 1
    fi
    log "apachectl configtest: OK"
    return 0
  else
    log "apachectl não disponível"
    return 1
  fi
}

who_uses_port() {
  local port=$1
  echo "Processos escutando na porta $port:"
  sudo ss -ltnp "( sport = :$port )" 2>/dev/null || sudo lsof -i :"$port" 2>/dev/null || echo "Nenhum processo encontrado"
}

apache_journal_errors() {
  log "Últimas 200 linhas do journal do apache2:"
  sudo journalctl -u apache2 -n 200 --no-pager || true
}

attempt_resolve_port_conflict() {
  local port=$1
  local procs
  procs=$(sudo ss -ltnp "( sport = :$port )" 2>/dev/null || true)
  if [ -z "$procs" ]; then
    log "Nenhum processo identificado na porta $port"
    return 0
  fi
  echo "$procs"
  # tenta identificar serviços comuns
  if echo "$procs" | grep -q nginx; then
    read -rp "nginx parece ocupar a porta $port. Deseja parar nginx agora? [y/N]: " yn
    if [[ "$yn" =~ ^[Yy]$ ]]; then sudo systemctl stop nginx && log "nginx parado"; fi
  fi
  if echo "$procs" | grep -q snap; then
    echo "Serviço snapd ou snap-config pode estar usando a porta. Verifique manualmente."
  fi
  # sugere kill se o usuário aceitar
  if echo "$procs" | grep -Eo 'pid=[0-9]+' | head -n1 >/dev/null 2>&1; then
    local pid; pid=$(echo "$procs" | grep -Eo 'pid=[0-9]+' | head -n1 | cut -d= -f2)
    read -rp "Deseja tentar terminar o PID $pid que está usando a porta $port? [y/N]: " yn
    if [[ "$yn" =~ ^[Yy]$ ]]; then
      sudo kill -15 "$pid" && sleep 1
      if sudo kill -0 "$pid" >/dev/null 2>&1; then
        log "PID $pid ainda em execução; forçando kill -9"
        sudo kill -9 "$pid" || true
      fi
      log "PID $pid terminado"
    fi
  fi
}

# -------------------------
# gerenciamento de serviços
# -------------------------
enable_start() {
  local svc=$1
  sudo systemctl enable "$svc" 2>/dev/null || true
  if sudo systemctl start "$svc"; then
    log "$svc iniciado"
    return 0
  else
    log "Falha ao iniciar $svc"
    return 1
  fi
}

stop_service_safe() {
  local svc=$1
  if systemctl list-units --type=service --state=running | grep -q "$svc"; then
    sudo systemctl stop "$svc" && log "$svc parado" || log "Erro ao parar $svc"
  else
    log "$svc não estava rodando"
  fi
}

# -------------------------
# instalação LAMP modular
# -------------------------
install_lamp() {
  log "Iniciando instalação LAMP"
  install_pkg_if_missing "apache2" || return 1
  install_pkg_if_missing "mysql-server" || return 1
  install_pkg_if_missing "php" || return 1
  install_pkg_if_missing "libapache2-mod-php" || return 1
  install_pkg_if_missing "php-mysql" || return 1
  install_pkg_if_missing "curl" || return 1
  install_pkg_if_missing "wget" || return 1
  install_pkg_if_missing "unzip" || return 1
  install_pkg_if_missing "lsof" || return 1
  # ativar mod_rewrite e reiniciar
  sudo a2enmod rewrite 2>/dev/null || true
  if ! apache_config_test; then
    log "configtest falhou; abortando ativação do apache até correção"
    apache_journal_errors
    return 1
  fi
  enable_start "apache2" || { apache_journal_errors; return 1; }
  enable_start "mysql" || { log "MySQL não pôde ser iniciado"; return 1; }
  log "Instalação LAMP concluída"
}

# -------------------------
# MySQL / DB helpers
# -------------------------
create_mysql_db_user() {
  local db="$1" user="$2" pass="$3"
  # usa sudo mysql para contornar auth_socket
  sudo mysql -e "CREATE DATABASE IF NOT EXISTS \`${db}\` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" \
    && sudo mysql -e "CREATE USER IF NOT EXISTS '${user}'@'localhost' IDENTIFIED BY '${pass}';" \
    && sudo mysql -e "GRANT ALL PRIVILEGES ON \`${db}\`.* TO '${user}'@'localhost';" \
    && sudo mysql -e "FLUSH PRIVILEGES;" \
    && log "DB e USR criados: $db / $user" \
    || { log "Erro criando DB/USER"; return 1; }
}

# -------------------------
# WordPress installer (atomic)
# -------------------------
insert_wp_salts() {
  local conf="$1"
  local tmp_salts="$TMP_DIR/wp_salts.txt"
  if command -v curl >/dev/null 2>&1; then
    curl -s https://api.wordpress.org/secret-key/1.1/salt/ > "$tmp_salts" || return 1
    # usa sed/awk para substituir bloco de chaves no wp-config.php
    sudo awk -v salts="$(sed ':a;N;$!ba;s/\n/\\n/g' "$tmp_salts")" '
      BEGIN{ins=0}
      /AUTH_KEY/ {ins=1}
      { if(ins==1) next }
      { print }
    ' "$conf" > "$conf.tmp" || return 1
    # append salts
    cat "$tmp_salts" | sudo tee -a "$conf.tmp" >/dev/null
    sudo mv "$conf.tmp" "$conf"
    rm -f "$tmp_salts"
    return 0
  fi
  return 1
}

install_wordpress() {
  if [ -f "${WP_WEBPATH}/wp-config.php" ]; then
    log "WP já instalado em $WP_WEBPATH"
    echo "WordPress já instalado"
    return 0
  fi
  read -rp "DB name [wp_db]: " DBNAME; DBNAME=${DBNAME:-wp_db}
  read -rp "DB user [wp_user]: " DBUSER; DBUSER=${DBUSER:-wp_user}
  read -rsp "DB pass: " DBPASS; echo
  if [ -z "$DBPASS" ]; then echo "senha vazia inválida"; return 1; fi

  # download
  rm -rf "$TMP_DIR/wordpress" "$TMP_DIR/latest.tar.gz"
  safe_run "wget -q -O '$TMP_DIR/latest.tar.gz' '$WP_URL'"
  safe_run "tar -xzf '$TMP_DIR/latest.tar.gz' -C '$TMP_DIR'"

  # copy atomically
  sudo mkdir -p "$WP_WEBPATH"
  sudo rsync -a --delete "$TMP_DIR/wordpress/" "$WP_WEBPATH/" || { log "rsync falhou"; return 1; }

  create_mysql_db_user "$DBNAME" "$DBUSER" "$DBPASS" || return 1

  # configure wp-config
  if [ -f "${WP_WEBPATH}/wp-config-sample.php" ]; then
    sudo cp "${WP_WEBPATH}/wp-config-sample.php" "${WP_WEBPATH}/wp-config.php"
    sudo sed -i "s/database_name_here/${DBNAME}/" "${WP_WEBPATH}/wp-config.php"
    sudo sed -i "s/username_here/${DBUSER}/" "${WP_WEBPATH}/wp-config.php"
    sudo sed -i "s/password_here/${DBPASS}/" "${WP_WEBPATH}/wp-config.php"
    if insert_wp_salts "${WP_WEBPATH}/wp-config.php"; then
      log "Salts inseridos via API"
    else
      log "Falha ao inserir salts automaticamente; verifique manualmente"
    fi
  fi

  # permissões
  sudo chown -R www-data:www-data "$WP_WEBPATH"
  sudo find "$WP_WEBPATH" -type d -exec chmod 755 {} \;
  sudo find "$WP_WEBPATH" -type f -exec chmod 644 {} \;
  sudo chmod 640 "${WP_WEBPATH}/wp-config.php" 2>/dev/null || true

  sudo systemctl reload apache2 || true
  log "WP instalado em $WP_WEBPATH"
  echo "WordPress instalado. Complete via http://localhost/wordpress"
}

# -------------------------
# testes automatizados (unitarios básicos)
# -------------------------
test_apache_start() {
  log "Teste: iniciar apache"
  if enable_start "apache2"; then
    apache_config_test || { echo "configtest falhou"; return 1; }
    local http_status; http_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ || true)
    if [ "$http_status" = "200" ] || [ "$http_status" = "403" ] || [ "$http_status" = "404" ]; then
      log "Apache responde HTTP $http_status"
      return 0
    else
      log "Apache HTTP resposta inesperada $http_status"
      apache_journal_errors
      return 1
    fi
  else
    apache_journal_errors
    return 1
  fi
}

test_php_processing() {
  local f="/var/www/html/info_test.php"
  echo "<?php phpinfo(); ?>" | sudo tee "$f" >/dev/null
  sudo chown www-data:www-data "$f"; sudo chmod 644 "$f"
  local code; code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/info_test.php || echo "000")
  sudo rm -f "$f"
  if [ "$code" = "200" ]; then
    log "PHP processado via Apache (HTTP 200)"
    return 0
  else
    log "PHP não processado (HTTP $code)"
    return 1
  fi
}

test_mysql_connection() {
  if sudo mysql -e "SELECT 1;" >/dev/null 2>&1; then
    log "MySQL responde"
    return 0
  else
    log "MySQL não responde via sudo mysql"
    return 1
  fi
}

run_tests() {
  echo "Executando bateria de testes automatizados..."
  test_mysql_connection || echo "MySQL falhou"
  # tenta resolver conflito de porta 80 se apache não iniciar
  if ! systemctl is-active --quiet apache2; then
    who_uses_port 80
    attempt_resolve_port_conflict 80
  fi
  test_apache_start || echo "Apache falhou nos testes"
  test_php_processing || echo "Processamento PHP falhou"
  echo "Testes concluídos. Consulte log em $LOG_FILE"
}

# -------------------------
# menu simples
# -------------------------
_main_menu() {
  cat <<EOF
Gerenciador LAMP estrito - opções:
1 instalar LAMP
2 iniciar serviços
3 parar serviços
4 status rápido
5 instalar WordPress
6 rodar testes automatizados
7 diagnosticar por que apache não inicia (configtest + journal)
8 ver quem usa porta 80/3306
9 ver logs
0 sair
EOF
}

_show_status() {
  echo "Apache: $(systemctl is-active apache2 2>/dev/null || echo 'não instalado/inativo')"
  echo "MySQL:  $(systemctl is-active mysql 2>/dev/null || echo 'não instalado/inativo')"
  echo "PHP:    $(php -v 2>/dev/null | head -n1 || echo 'não encontrado')"
  who_uses_port 80
  who_uses_port 3306
}

# -------------------------
# execução
# -------------------------
_init
log "Script iniciado por $(whoami) em $(hostname)"

while true; do
  _main_menu
  read -rp "Escolha: " opt
  case "$opt" in
    1) install_lamp ;;
    2) enable_start "apache2"; enable_start "mysql" ;;
    3) stop_service_safe "apache2"; stop_service_safe "mysql" ;;
    4) _show_status ;;
    5) install_wordpress ;;
    6) run_tests ;;
    7) apache_config_test || apache_journal_errors ;;
    8) who_uses_port 80; who_uses_port 3306 ;;
    9) sudo tail -n 200 "$LOG_FILE" ;;
    0) log "Finalizando"; exit 0 ;;
    *) echo "opção inválida" ;;
  esac
  echo
  read -rp "pressione Enter para continuar..." _
done
