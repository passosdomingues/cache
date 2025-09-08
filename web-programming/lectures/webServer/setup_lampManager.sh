#!/usr/bin/env bash
# setup_lampManager.sh
# LAMP manager final: detecção de porta 80, ServerName, mudar porta, instalar WP, testes
# Linux Mint 22.2 / Ubuntu 24.04 LTS
# Autor: Capitão Nemo
set -euo pipefail
IFS=$'\n\t'

LOG_DIR="$HOME/.lamp_manager"
LOG_FILE="$LOG_DIR/lamp_manager.log"
TMP_DIR="/tmp/lamp_manager"
WP_URL="https://wordpress.org/latest.tar.gz"
WP_WEBPATH="/var/www/html/wordpress"
APACHE_PORT_FILE="/etc/apache2/ports.conf"
BACKUP_DIR="$HOME/.lamp_manager/backups"

# util
_init() {
  mkdir -p "$LOG_DIR" "$TMP_DIR" "$BACKUP_DIR"
  touch "$LOG_FILE"
  chmod 600 "$LOG_FILE"
}

log() { local m="[$(date +'%F %T')] $*"; echo "$m" | tee -a "$LOG_FILE"; }

safe_run() {
  log "EXEC: $*"
  bash -c "$*"
}

# pacote
pkg_installed() { dpkg -s "$1" &>/dev/null; }

apt_update_once() {
  [ -f "$TMP_DIR/apt_updated" ] && return 0
  log "apt update..."
  sudo apt update -y
  touch "$TMP_DIR/apt_updated"
}

install_pkg_if_missing() {
  local pkg=$1
  if pkg_installed "$pkg"; then
    log "pkg $pkg: already installed"
    return 0
  fi
  apt_update_once
  log "Installing $pkg..."
  sudo apt install -y "$pkg"
}

# ServerName fix
ensure_servername() {
  log "Ensuring global ServerName (silence AH00558)..."
  local conf="/etc/apache2/conf-available/servername.conf"
  echo "ServerName 127.0.0.1" | sudo tee "$conf" >/dev/null
  sudo a2enconf servername || true
  # don't try reload if apache inactive; we will start/restart later
}

# show which process uses port 80 (uses ss/netstat/lsof)
who_uses_port() {
  log "Detecting process on port $1"
  sudo ss -ltnp "( sport = :$1 )" 2>/dev/null || sudo netstat -nlp 2>/dev/null | grep ":$1" || sudo lsof -i :"$1" 2>/dev/null || echo "none"
}

# parse process name and pid from ss output
parse_pid_from_port() {
  local port=$1
  local line
  line="$(sudo ss -ltnp "( sport = :$port )" 2>/dev/null | tr -s ' ' | tail -n +2 | head -n1 || true)"
  if [ -z "$line" ]; then
    echo ""
    return
  fi
  # line example suffix users:(("nginx",pid=125004,fd=12))
  local users_part
  users_part="$(echo "$line" | grep -oP 'users:\(\(.+\)\)')"
  if [ -z "$users_part" ]; then
    # fallback to lsof
    local l
    l="$(sudo lsof -i :"$port" -sTCP:LISTEN -n -P | awk 'NR==2{print $2":"$1}')"
    echo "${l%%:*}"
    return
  fi
  local pid
  pid="$(echo "$users_part" | grep -oP 'pid=\K[0-9]+' | head -n1 || true)"
  echo "$pid"
}

# attempt safe resolution: stop known services, else kill pid, else change apache port
attempt_resolve_port80() {
  log "Attempting resolution for port 80 conflict"
  who_uses_port 80
  local pid
  pid="$(parse_pid_from_port 80 || true)"
  if [ -z "$pid" ]; then
    echo "Não foi possível identificar PID automaticamente."
    return 1
  fi
  local cmd
  cmd="$(ps -p "$pid" -o comm= 2>/dev/null || true)"
  echo "PID $pid: $cmd"
  if echo "$cmd" | grep -Eiq "nginx|caddy|traefik|haproxy|docker|containerd|snap"; then
    echo "Serviço identificado: $cmd"
    read -rp "Parar o serviço systemctl associado a $cmd se existir? [y/N]: " yn
    if [[ "$yn" =~ ^[Yy]$ ]]; then
      # try common service names
      for svc in nginx caddy traefik haproxy docker snapd; do
        if systemctl list-units --type=service --state=running | grep -qi "^$svc"; then
          sudo systemctl stop "$svc" && log "Stopped $svc" && return 0 || true
        fi
      done
      # fallback kill pid
      sudo kill -15 "$pid" && sleep 1 && sudo kill -0 "$pid" 2>/dev/null || { log "Killed $pid"; return 0; } || sudo kill -9 "$pid" && log "Force killed $pid" && return 0 || true
    fi
  fi
  # ask to kill pid directly
  read -rp "Deseja tentar terminar PID $pid? [y/N]: " yn2
  if [[ "$yn2" =~ ^[Yy]$ ]]; then
    sudo kill -15 "$pid" && sleep 1 || true
    if sudo kill -0 "$pid" >/dev/null 2>&1; then
      sudo kill -9 "$pid" || true
    fi
    log "PID $pid terminated (attempted)"
    return 0
  fi
  # offer change Apache port
  echo "Se não puder parar o processo, posso trocar Apache para outra porta (ex: 8080)."
  read -rp "Mudar Apache para porta 8080 agora? [y/N]: " yn3
  if [[ "$yn3" =~ ^[Yy]$ ]]; then
    change_apache_port 8080
    return 0
  fi
  return 1
}

# backup file
backup_file() {
  local f=$1
  [ -f "$f" ] && sudo cp -a "$f" "$BACKUP_DIR/$(basename "$f").bak.$(date +%s)" && log "Backup $f created"
}

# change apache listen port and adapt vhosts
change_apache_port() {
  local newport=${1:-8080}
  log "Changing Apache Listen port to $newport"
  sudo mkdir -p "$BACKUP_DIR"
  backup_file "$APACHE_PORT_FILE"
  # update ports.conf
  sudo sed -i.bak -E "s/Listen[[:space:]]+[0-9]+/Listen $newport/g" "$APACHE_PORT_FILE" || true
  # update sites-enabled vhosts that listen on :80
  for vf in /etc/apache2/sites-enabled/*.conf; do
    [ -f "$vf" ] || continue
    backup_file "$vf"
    sudo sed -i -E "s/<VirtualHost[[:space:]]+\*:80/<VirtualHost *:$newport/g" "$vf" || true
  done
  sudo systemctl restart apache2 || { log "Restart failed after port change"; show_apache_journal; return 1; }
  log "Apache now listening on $newport"
  echo "Apache alterado para porta $newport. Acesse em http://localhost:$newport/"
}

show_apache_journal() {
  log "Apache journal tail"
  sudo journalctl -u apache2 -n 200 --no-pager || true
}

install_lamp() {
  log "Starting LAMP install"
  for pkg in apache2 mysql-server php libapache2-mod-php php-mysql wget curl unzip lsof net-tools; do
    install_pkg_if_missing "$pkg"
  done
  sudo a2enmod rewrite || true
  ensure_servername
  # check for port conflict before starting
  if sudo ss -ltnp "( sport = :80 )" 2>/dev/null | grep -q LISTEN; then
    log "Port 80 currently in use before starting Apache"
    attempt_resolve_port80 || log "User declined or resolution failed"
  fi
  # configtest then start
  if sudo apachectl configtest; then
    sudo systemctl restart apache2 || { log "apache restart failed"; show_apache_journal; attempt_resolve_port80 || true; }
  else
    log "apachectl configtest failed"
    show_apache_journal
    return 1
  fi
  # ensure mysql
  sudo systemctl enable --now mysql || log "mysql enable/start failed"
  log "LAMP install completed"
}

install_wordpress() {
  if [ -f "$WP_WEBPATH/wp-config.php" ]; then
    echo "WordPress already installed"
    log "WP already installed"
    return 0
  fi
  read -rp "DB name [wp_db]: " DBNAME; DBNAME=${DBNAME:-wp_db}
  read -rp "DB user [wp_user]: " DBUSER; DBUSER=${DBUSER:-wp_user}
  read -rsp "DB pass: " DBPASS; echo
  rm -rf "$TMP_DIR/wordpress" "$TMP_DIR/latest.tar.gz"
  safe_run "wget -q -O '$TMP_DIR/latest.tar.gz' '$WP_URL'"
  safe_run "tar -xzf '$TMP_DIR/latest.tar.gz' -C '$TMP_DIR'"
  sudo mkdir -p "$WP_WEBPATH"
  sudo rsync -a --delete "$TMP_DIR/wordpress/" "$WP_WEBPATH/"
  sudo mysql -e "CREATE DATABASE IF NOT EXISTS \`${DBNAME}\` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
  sudo mysql -e "CREATE USER IF NOT EXISTS '${DBUSER}'@'localhost' IDENTIFIED BY '${DBPASS}';"
  sudo mysql -e "GRANT ALL PRIVILEGES ON \`${DBNAME}\`.* TO '${DBUSER}'@'localhost'; FLUSH PRIVILEGES;"
  sudo cp "$WP_WEBPATH/wp-config-sample.php" "$WP_WEBPATH/wp-config.php"
  sudo sed -i "s/database_name_here/${DBNAME}/; s/username_here/${DBUSER}/; s/password_here/${DBPASS}/" "$WP_WEBPATH/wp-config.php"
  # add salts
  if command -v curl >/dev/null 2>&1; then
    curl -s https://api.wordpress.org/secret-key/1.1/salt/ | sudo tee -a "$WP_WEBPATH/wp-config.php" >/dev/null || true
  fi
  sudo chown -R www-data:www-data "$WP_WEBPATH"
  sudo find "$WP_WEBPATH" -type d -exec chmod 755 {} \;
  sudo find "$WP_WEBPATH" -type f -exec chmod 644 {} \;
  sudo chmod 640 "$WP_WEBPATH/wp-config.php" || true
  safe_run "sudo systemctl reload apache2" || true
  log "WordPress installed to $WP_WEBPATH"
  echo "Open http://localhost/$( [ -f /etc/apache2/ports.conf ] && grep -q 'Listen 8080' /etc/apache2/ports.conf && echo 'wordpress on custom port' || echo 'wordpress' )"
}

test_stack() {
  log "Running stack tests"
  if sudo systemctl is-active --quiet mysql; then echo "MySQL OK"; else echo "MySQL inactive"; fi
  # test Apache start
  if sudo systemctl is-active --quiet apache2; then echo "Apache running"; else
    echo "Apache not running; trying to start"
    sudo systemctl restart apache2 || { echo "Failed to start apache2"; show_apache_journal; return 1; }
  fi
  # test HTTP
  local code
  code="$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ || true)"
  echo "HTTP status for / : $code"
  echo "<?php phpinfo();" | sudo tee /var/www/html/test.php >/dev/null
  code="$(curl -s -o /dev/null -w "%{http_code}" http://localhost/test.php || echo "000")"
  sudo rm -f /var/www/html/test.php
  echo "PHP processing test http status: $code"
}

show_status() {
  echo "Apache: $(sudo systemctl is-active apache2 2>/dev/null || echo inactive)"
  echo "MySQL:  $(sudo systemctl is-active mysql 2>/dev/null || echo inactive)"
  php -v 2>/dev/null | head -n1 || echo "PHP missing"
  who_uses_port 80
}

menu() {
  cat <<EOF
1 instalar LAMP
2 status rápido
3 who uses port 80
4 resolver conflito porta 80 (parar serviço / kill / mudar porta)
5 instalar WordPress
6 testar stack
7 ver logs
0 sair
EOF
}

_init
log "Script started by $(whoami)@$(hostname)"

while true; do
  menu
  read -rp "Escolha: " opt
  case "$opt" in
    1) install_lamp ;;
    2) show_status ;;
    3) who_uses_port 80 ;;
    4) attempt_resolve_port80 ;;
    5) install_wordpress ;;
    6) test_stack ;;
    7) tail -n 200 "$LOG_FILE" ;;
    0) log "Exiting"; exit 0 ;;
    *) echo "Opção inválida" ;;
  esac
  read -rp "Pressione Enter para continuar..." _
done
