#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

APACHE_USER="www-data"
APACHE_GROUP="www-data"
WEB_ROOT_BASE="/var/www/html"
SITES=("primeiro_site" "segundo_site")
WP_TARBALL_URL="https://br.wordpress.org/latest-pt_BR.tar.gz"
APACHE_SITES_DIR="/etc/apache2/sites-available"
APACHE_DEFAULT_SITE="000-default.conf"

log() { printf '%s\n' "[INFO] $*"; }
die() { printf '%s\n' "[ERROR] $*" >&2; exit 1; }

TMP_FILES=()
cleanup() { for f in "${TMP_FILES[@]:-}"; do [[ -e $f ]] && shred -u "$f" 2>/dev/null || true; done; }
trap cleanup EXIT INT TERM

check_root() { [[ $EUID -eq 0 ]] || die "Este script deve ser executado como root."; }
check_command() { command -v "$1" >/dev/null 2>&1 || die "Comando necessário não encontrado: $1"; }
check_dependencies() { check_command wget; check_command tar; check_command mysql; check_command apache2ctl; check_command systemctl; }

safe_mkdir() {
    local dir="$1"
    if [[ -d $dir ]]; then
        local bak="${dir}.bak.$(date +%s)"
        mv "$dir" "$bak"
        log "Backup de $dir em $bak"
    fi
    mkdir -p "$dir"
    chown -R "${APACHE_USER}:${APACHE_GROUP}" "$dir"
    chmod -R 755 "$dir"
}

download_and_extract_wp() {
    local target_dir="$1"
    local tmpfile
    tmpfile="$(mktemp)"
    TMP_FILES+=("$tmpfile")
    log "Baixando WordPress para $target_dir"
    wget -q -O "$tmpfile" "$WP_TARBALL_URL" || die "Falha ao baixar $WP_TARBALL_URL"
    tar -xzf "$tmpfile" -C "$target_dir" --strip-components=1
    rm -f "$tmpfile"
}

mysql_exec_with_defaults() {
    local defaults_file="$1"
    local sql="$2"
    mysql --defaults-extra-file="$defaults_file" --batch --silent -e "$sql"
}

create_mysql_defaults_file() {
    local user="$1"
    local password="$2"
    local file
    file="$(mktemp)"
    TMP_FILES+=("$file")
    chmod 600 "$file"
    cat >"$file" <<EOF
[client]
user=${user}
password=${password}
host=localhost
EOF
    printf '%s' "$file"
}

create_databases_and_users() {
    local root_pass="$1"
    local defaults
    defaults="$(create_mysql_defaults_file "root" "$root_pass")"

    for db in "${SITES[@]}"; do
        local dbname="$db"
        local dbuser="usuario_${db}"
        local dbpass="$root_pass"
        log "Criando database e usuário para $dbname"
        local sql="
CREATE DATABASE IF NOT EXISTS \`${dbname}\` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${dbuser}'@'localhost' IDENTIFIED BY '${dbpass}';
GRANT ALL PRIVILEGES ON \`${dbname}\`.* TO '${dbuser}'@'localhost';
FLUSH PRIVILEGES;"
        mysql_exec_with_defaults "$defaults" "$sql" || die "Erro criando database $dbname"
        write_wp_config "${WEB_ROOT_BASE}/${dbname}" "${dbname}" "${dbuser}" "${dbpass}"
    done
}

write_wp_config() {
    local site_dir="$1"
    local dbname="$2"
    local dbuser="$3"
    local dbpass="$4"
    local wp_config="${site_dir}/wp-config.php"

    [[ -f $wp_config ]] && mv "$wp_config" "${wp_config}.bak.$(date +%s)"
    cp "$site_dir/wp-config-sample.php" "$wp_config"
    perl -i -pe "s/database_name_here/$dbname/; s/username_here/$dbuser/; s/password_here/$dbpass/;" "$wp_config"

    local salts
    salts="$(wget -qO- https://api.wordpress.org/secret-key/1.1/salt/ || true)"
    if [[ -n $salts ]]; then
        awk -v salt="$salts" 'BEGIN{p=0} /AUTH_KEY/{p=1} {if(p==1 && /.*define.*/){next} if(p==1 && /.*\);/){print salt; p=2; next} } {print}' "$wp_config" > "${wp_config}.tmp"
        mv "${wp_config}.tmp" "$wp_config"
    fi

    chown "${APACHE_USER}:${APACHE_GROUP}" "$wp_config"
    chmod 640 "$wp_config"
}

backup_if_exists() {
    local f="$1"
    [[ -e $f ]] && mv "$f" "$f.bak.$(date +%s)" && log "Backup de $f criado."
}

configure_apache_for_site() {
    local site="$1"
    local site_dir="${WEB_ROOT_BASE}/${site}"
    local server_name="${site}.local"
    local conf_file="${APACHE_SITES_DIR}/${site}.conf"

    backup_if_exists "$conf_file"

    cat >"$conf_file" <<EOF
<VirtualHost *:80>
    ServerAdmin webmaster@localhost
    ServerName ${server_name}
    DocumentRoot ${site_dir}
    <Directory ${site_dir}>
        Require all granted
        AllowOverride All
    </Directory>
    ErrorLog \${APACHE_LOG_DIR}/${site}_error.log
    CustomLog \${APACHE_LOG_DIR}/${site}_access.log combined
</VirtualHost>
EOF

    a2ensite "${site}.conf"
    grep -q "${server_name}" /etc/hosts || echo "127.0.0.1 ${server_name}" >> /etc/hosts
}

restart_apache() {
    apache2ctl configtest >/dev/null || die "Configuração do Apache inválida."
    systemctl restart apache2
    systemctl is-active --quiet apache2 || die "Falha ao iniciar Apache"
    log "Apache reiniciado com sucesso"
}

prepare_environment() {
    for site in "${SITES[@]}"; do
        safe_mkdir "${WEB_ROOT_BASE}/${site}"
    done
}

install_wordpress_sites() {
    for site in "${SITES[@]}"; do
        local dir="${WEB_ROOT_BASE}/${site}"
        if [[ -n "$(ls -A "$dir" 2>/dev/null || true)" ]]; then
            mv "$dir" "$dir.bak.$(date +%s)"
            mkdir -p "$dir"
        fi
        download_and_extract_wp "$dir"
        chown -R "${APACHE_USER}:${APACHE_GROUP}" "$dir"
    done
}

configure_databases() {
    local root_pass="$MYSQL_PASSWORD"
    create_databases_and_users "$root_pass"
}

configure_apache() {
    for site in "${SITES[@]}"; do
        configure_apache_for_site "$site"
    done
    a2dissite "${APACHE_DEFAULT_SITE}" >/dev/null 2>&1 || true
    restart_apache
}

print_final_instructions() {
    for site in "${SITES[@]}"; do
        echo "Acesse: http://${site}.local para completar a instalação via navegador."
    done
}

main() {
    check_root
    check_dependencies
    [[ -n "${MYSQL_PASSWORD:-}" ]] || die "Defina a variável de ambiente MYSQL_PASSWORD antes de rodar."
    prepare_environment
    install_wordpress_sites
    configure_databases
    configure_apache
    print_final_instructions
}

main "$@"
