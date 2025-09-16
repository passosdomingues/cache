#!/bin/bash
# configJPA_safe.sh
# Não destrutivo. Usa $MYSQL_PASSWORD para configurar root e criar jpa_hands_on.
# Uso: export MYSQL_PASSWORD="root" ; sudo -E ./configJPA_safe.sh
set -euo pipefail

DB_NAME="jpa_hands_on"
ROOT_PASS="${MYSQL_PASSWORD:-}"

SOCKET="/var/run/mysqld/mysqld.sock"
TRIES=5
SLEEP=1

info(){ printf '\e[34m[INFO]\e[0m %s\n' "$*"; }
ok(){ printf '\e[32m[SUCCESS]\e[0m %s\n' "$*"; }
err(){ printf '\e[31m[ERROR]\e[0m %s\n' "$*\n" >&2; }

require_root(){
  if [[ $EUID -ne 0 ]]; then
    err "Execute o script como root (use sudo)."
    exit 1
  fi
}

check_env(){
  if [[ -z "$ROOT_PASS" ]]; then
    err "A variável de ambiente MYSQL_PASSWORD não está definida. Rode: export MYSQL_PASSWORD='sua_senha' e em seguida sudo -E ./configJPA_safe.sh"
    exit 1
  fi
}

ensure_mysql_running(){
  if systemctl is-active --quiet mysql; then
    info "MySQL service ativo."
    return 0
  fi
  info "MySQL não está ativo, tentando iniciar service..."
  systemctl start mysql || true
  local i=0
  while [[ $i -lt $TRIES ]]; do
    if systemctl is-active --quiet mysql; then
      ok "MySQL iniciado."
      return 0
    fi
    i=$((i+1)); sleep $SLEEP
  done
  err "Não foi possível iniciar o serviço MySQL via systemctl. Verifique: sudo journalctl -u mysql -n 200"
  exit 1
}

can_use_socket_mysql(){
  # tenta executar mysql via socket (como root do sistema). Retorna 0 se OK.
  if mysql -sNe "SELECT 1;" &>/dev/null; then
    return 0
  else
    return 1
  fi
}

get_root_plugin(){
  # executa query via socket e retorna plugin (p.ex. auth_socket, caching_sha2_password, mysql_native_password)
  mysql -N -B -e "SELECT plugin FROM mysql.user WHERE user='root' AND host='localhost' LIMIT 1;" 2>/dev/null || true
}

attempt_alter_root_via_socket(){
  info "Tentando alterar plugin/ senha do root via socket..."
  if ! can_use_socket_mysql; then
    info "Acesso via socket falhou."
    return 1
  fi

  local plugin
  plugin="$(get_root_plugin || true)"
  info "plugin atual do root: ${plugin:-(não detectado)}"

  if [[ "$plugin" == "mysql_native_password" || "$plugin" == "caching_sha2_password" ]]; then
    info "Root já usa plugin de senha ('$plugin'). Tentando autenticar com a senha fornecida..."
    if mysql -uroot -p"${ROOT_PASS}" -e "SELECT 1;" &>/dev/null; then
      ok "Autenticação com senha funcionando (root)."
      return 0
    else
      info "Senha fornecida não autentica, atualizando senha do root para o valor em \$MYSQL_PASSWORD..."
      mysql <<SQL
ALTER USER 'root'@'localhost' IDENTIFIED BY '${ROOT_PASS}';
FLUSH PRIVILEGES;
SQL
      if mysql -uroot -p"${ROOT_PASS}" -e "SELECT 1;" &>/dev/null; then
        ok "Senha root atualizada com sucesso."
        return 0
      else
        err "Falha ao autenticar mesmo após alterar senha."
        return 1
      fi
    fi
  else
    info "Root usa plugin '$plugin' (provavelmente auth_socket). Vai alterar para mysql_native_password com a senha fornecida."
    mysql <<SQL
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '${ROOT_PASS}';
FLUSH PRIVILEGES;
SQL
    if mysql -uroot -p"${ROOT_PASS}" -e "SELECT 1;" &>/dev/null; then
      ok "Plugin e senha do root atualizados com sucesso."
      return 0
    else
      err "Não foi possível autenticar com root após alteração do plugin. Verifique permissões e logs."
      return 1
    fi
  fi
}

attempt_login_with_password(){
  info "Testando login com root e a senha fornecida..."
  if mysql -uroot -p"${ROOT_PASS}" -e "SELECT 1;" &>/dev/null; then
    ok "Login com senha root bem-sucedido."
    return 0
  else
    return 1
  fi
}

create_db(){
  info "Criando banco ${DB_NAME} (se não existir)..."
  mysql -uroot -p"${ROOT_PASS}" -e "CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" || {
    err "Falha ao criar banco. Saída de erro: sudo journalctl -u mysql -n 60"
    exit 1
  }
  ok "Banco ${DB_NAME} pronto."
}

main(){
  require_root
  check_env
  ensure_mysql_running

  # 1) se já autentica com senha, só cria o banco
  if attempt_login_with_password; then
    create_db
    ok "Tudo pronto. Use root/root conforme \$MYSQL_PASSWORD."
    exit 0
  fi

  # 2) tenta alterar via socket (idempotente e seguro)
  if attempt_alter_root_via_socket; then
    create_db
    ok "Configuração concluída com sucesso sem alterar instalação existente."
    exit 0
  fi

  # 3) se ainda falhar, tenta reiniciar o serviço e repetir (não destrutivo)
  info "Tentando reiniciar serviço mysql e repetir tentativa..."
  systemctl restart mysql || true
  sleep 2

  if attempt_login_with_password; then
    create_db
    ok "Login por senha agora OK após restart."
    exit 0
  fi

  if attempt_alter_root_via_socket; then
    create_db
    ok "Alteração via socket bem-sucedida após restart."
    exit 0
  fi

  # 4) falha segura: apresenta logs e instruções manuais (sem destruir nada)
  err "Não foi possível garantir root/root automaticamente sem alterações destrutivas."
  echo
  echo "Saídas de diagnóstico recomendadas (cole aqui se quiser que eu analise):"
  echo "sudo journalctl -u mysql -n 200 --no-pager"
  echo "sudo ls -la /var/run/mysqld /var/lib/mysql /etc/mysql"
  echo "sudo tail -n 200 /var/log/mysql/error.log  (ou /var/log/syslog se não existir)"
  echo
  echo "Se quiser que eu tente um modo de recuperação (mais invasivo), diga e eu preparo um script separado."
  exit 1
}

main "$@"

