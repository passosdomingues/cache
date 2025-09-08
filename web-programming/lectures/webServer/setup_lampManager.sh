#!/usr/bin/env bash
# Linux Mint 22.2 / Ubuntu 24.04 LTS

# Autor: Capitão Nemo
# Last Update: 2025 Sep 8 (Mon)

set -euo pipefail
IFS=$'\n\t'

LOG_DIR="$HOME/.lamp_manager"
LOG_FILE="$LOG_DIR/lamp.log"
TMP_DIR="/tmp/lamp_manager"
BACKUP_DIR="$LOG_DIR/backups"
WP_URL="https://wordpress.org/latest.tar.gz"
WP_WEBPATH="/var/www/html/wordpress"
APACHE_CONF="/etc/apache2/apache2.conf"
PORTS_CONF="/etc/apache2/ports.conf"
SITES_ENABLED="/etc/apache2/sites-enabled"

init_env() {
  mkdir -p "$LOG_DIR" "$TMP_DIR" "$BACKUP_DIR"
  touch "$LOG_FILE"
  chmod 600 "$LOG_FILE"
}

log() { echo "[$(date +'%F %T')] $*" | tee -a "$LOG_FILE"; }

safe_run() { log "EXEC: $*"; bash -c "$*"; }

pkg_installed() { dpkg -s "$1" &>/dev/null; }

apt_update_once() {
  [ -f "$TMP_DIR/apt_updated" ] && return
  log "apt update..."
  sudo apt update -y
  touch "$TMP_DIR/apt_updated"
}

install_pkg() {
  local pkg="$1"
  pkg_installed "$pkg" && { log "pkg $pkg já." ; return; }
  apt_update_once
  log "Instalando $pkg..."
  sudo apt install -y "$pkg"
}

ensure_servername() {
  log "Configurando ServerName global armado"
  if ! grep -q '^ServerName' "$APACHE_CONF"; then
    sudo cp "$APACHE_CONF" "$BACKUP_DIR/apache2.conf.bak.$(date +%s)"
    echo "ServerName 127.0.0.1" | sudo tee -a "$APACHE_CONF" >/dev/null
    log "ServerName adicionado a $APACHE_CONF"
  else
    log "ServerName já presente em $APACHE_CONF"
  fi
}

who_uses_port() {
  log "Cheque processos na porta $1"
  sudo ss -ltnp "( sport = :$1 )" 2>/dev/null || sudo netstat -nlp 2>/dev/null | grep ":$1" || sudo lsof -i :"$1" 2>/dev/null || echo "livre"
}

parse_pid() {
  local port=$1
  sudo ss -ltnp "( sport = :$port )" 2>/dev/null | awk -F 'pid=' '/pid/ {print $2}' | cut -d',' -f1 | head -n1 || true
}

backup_file() {
  local f=$1
  [ -f "$f" ] && sudo cp -a "$f" "$BACKUP_DIR/$(basename "$f").bak.$(date +%s)" && log "Backup: $f"
}

change_apache_port() {
  local newport=$1
  log "Mudando Apache para porta $newport"
  backup_file "$PORTS_CONF"
  sudo sed -i -E "s/Listen[[:space:]]+[0-9]+/Listen $newport/g" "$PORTS_CONF"
  for vf in "$SITES_ENABLED"/*.conf; do
    [ -f "$vf" ] || continue
    backup_file "$vf"
    sudo sed -i -E "s/<VirtualHost[[:space:]]+\*:80/<VirtualHost *:$newport/g" "$vf"
  done
  safe_run "sudo systemctl restart apache2"
  echo "Apache agora na porta $newport"
}

resolve_port_conflict() {
  who_uses_port 80
  local pid; pid=$(parse_pid 80)
  [ -z "$pid" ] && return
  local proc; proc=$(ps -p "$pid" -o comm= || echo "desconhecido")
  echo "PID $pid: $proc"
  if echo "$proc" | grep -Eiq "nginx|caddy|traefik|docker"; then
    read -rp "Parar serviço $proc? [y/N]: " yn
    if [[ "$yn" =~ ^[Yy]$ ]]; then
      sudo systemctl stop "$proc" 2>/dev/null && return
    fi
  fi
  read -rp "Kill PID $pid? [y/N]: " yn2
  if [[ "$yn2" =~ ^[Yy]$ ]]; then
    sudo kill "$pid" && return
  fi
  read -rp "Mudar Apache para porta 8080? [y/N]: " yn3
  [[ "$yn3" =~ ^[Yy]$ ]] && change_apache_port 8080
}

install_lamp() {
  log "Iniciando LAMP..."
  for pkg in apache2 mysql-server php libapache2-mod-php php-mysql wget curl unzip lsof net-tools; do
    install_pkg "$pkg"
  done
  sudo a2enmod rewrite || true
  ensure_servername
  if sudo ss -ltnp "( sport = :80 )" 2>/dev/null | grep -q LISTEN; then
    log "Porta 80 ocupada"
    resolve_port_conflict
  fi
  if sudo apachectl configtest; then
    safe_run "sudo systemctl restart apache2" || { log "Falha Apache"; sudo journalctl -u apache2 -n 50; resolve_port_conflict; }
  else
    log "configtest falhou"; sudo journalctl -u apache2 -n 50
  fi
  sudo systemctl enable --now mysql
  log "LAMP instalado."
}

install_wp() {
  [ -f "$WP_WEBPATH/wp-config.php" ] && { log "WP já instalado"; return; }
  read -rp "DB [wp_db]: " dn; dn=${dn:-wp_db}
  read -rp "User [wp_user]: " un; un=${un:-wp_user}
  read -rsp "Pass: " pw; echo; [[ -z "$pw" ]] && { echo "Senha inválida"; return; }
  rm -rf "$TMP_DIR/wordpress" "$TMP_DIR/latest.tar.gz"
  safe_run "wget -q -O '$TMP_DIR/latest.tar.gz' '$WP_URL'"
  safe_run "tar -xzf '$TMP_DIR/latest.tar.gz' -C '$TMP_DIR'"
  sudo mkdir -p "$WP_WEBPATH"
  sudo rsync -a --delete "$TMP_DIR/wordpress/" "$WP_WEBPATH/"
  sudo mysql -e "CREATE DATABASE IF NOT EXISTS \`${dn}\`; CREATE USER IF NOT EXISTS '${un}'@'localhost' IDENTIFIED BY '${pw}'; GRANT ALL ON \`${dn}\`.* TO '${un}'@'localhost'; FLUSH PRIVILEGES;"
  sudo cp "$WP_WEBPATH/wp-config-sample.php" "$WP_WEBPATH/wp-config.php"
  sudo sed -i "s/database_name_here/$dn/; s/username_here/$un/; s/password_here/$pw/" "$WP_WEBPATH/wp-config.php"
  curl -s https://api.wordpress.org/secret-key/1.1/salt/ | sudo tee -a "$WP_WEBPATH/wp-config.php" >/dev/null
  sudo chown -R www-data:www-data "$WP_WEBPATH"
  sudo chmod -R 755 "$WP_WEBPATH"
  sudo chmod 640 "$WP_WEBPATH/wp-config.php" || true
  safe_run "sudo systemctl reload apache2"
  log "WordPress instalado."
}

test_stack() {
  log "Testando stack"
  sudo systemctl is-active mysql && echo "MySQL OK" || echo "MySQL INATIVO"
  if sudo systemctl is-active apache2; then echo "Apache OK"; else
    echo "Tentando iniciar Apache"
    sudo systemctl restart apache2 || { log "Falha ao start Apache"; sudo journalctl -u apache2 -n 50; return; }
  fi
  code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/)
  echo "HTTP / status: $code"
  echo "<?php phpinfo();" | sudo tee /var/www/html/test.php >/dev/null
  code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/test.php || echo "000")
  sudo rm -f /var/www/html/test.php
  echo "PHP test status: $code"
}

show_status() {
  echo "Apache: $(sudo systemctl is-active apache2||echo inactive)"
  echo "MySQL:  $(sudo systemctl is-active mysql||echo inactive)"
  php -v 2>/dev/null | head -n1 || echo "PHP missing"
  who_uses_port 80
}

menu() {
  cat <<EOF
1 instalar LAMP
2 status
3 quem usa porta 80
4 resolver conflito porta 80
5 instalar WordPress
6 testar stack
7 ver logs
0 sair
EOF
}

_init_env() { init_env; log "Script iniciado por $(whoami)"; }

_init_env
while true; do
  menu
  read -rp "Escolha: " o
  case "$o" in
    1) install_lamp ;;
    2) show_status ;;
    3) who_uses_port 80 ;;
    4) resolve_port_conflict ;;
    5) install_wp ;;
    6) test_stack ;;
    7) tail -n 200 "$LOG_FILE" ;;
    0) log "Saindo"; exit 0 ;;
    *) echo "Inválido" ;;
  esac
  read -rp "Enter para continuar..." _
done
