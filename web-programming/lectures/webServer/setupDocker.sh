#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

readonly DOCKER_HUB_USERNAME="rafaelpassosdomingues"
readonly DOCKER_IMAGE_NAME="nginx-hello-app"
readonly DOCKER_CONTAINER_NAME="nginx-hello-test"
readonly DOCKER_HOST_PORT="8080"
readonly DOCKER_CONTAINER_PORT="80"
readonly APPLICATION_DIRECTORY="${HOME}/docker-nginx-app"
readonly DOCKERFILE_NAME="Dockerfile"
readonly HTML_FILE_NAME="hello-cruel-world.html"
readonly IMAGE_TAG="latest"

if [ -t 1 ]; then
  COLOR_RED='\033[0;31m'
  COLOR_GREEN='\033[0;32m'
  COLOR_BLUE='\033[0;34m'
  COLOR_NC='\033[0m'
else
  COLOR_RED='' ; COLOR_GREEN='' ; COLOR_BLUE='' ; COLOR_NC=''
fi

log() { printf "%b\n" "${COLOR_BLUE}ℹ $*${COLOR_NC}"; }
ok()  { printf "%b\n" "${COLOR_GREEN}✓ $*${COLOR_NC}"; }
err() { printf "%b\n" "${COLOR_RED}✗ ERROR: $*${COLOR_NC}" >&2; }
fail() { err "$*"; exit 1; }

require_cmds() {
  local miss=()
  for c in "$@"; do
    if ! command -v "$c" >/dev/null 2>&1; then
      miss+=("$c")
    fi
  done
  [ "${#miss[@]}" -eq 0 ] || fail "Comandos ausentes: ${miss[*]}"
}

mask_token() {
  local t="$1"
  local n=${#t}
  if [ "$n" -le 8 ]; then
    printf '%s' "****"
    return
  fi
  local head="${t:0:4}"
  local tail="${t: -4}"
  printf '%s' "${head}...${tail}"
}

validate_env() {
  log "Validando ambiente"
  if [ "${EUID:-0}" -eq 0 ]; then
    fail "Não execute como root"
  fi

  if [ -z "${DOCKER_HUB_TOKEN:-}" ]; then
    fail "Variável DOCKER_HUB_TOKEN não encontrada. Exporte-a antes de rodar."
  fi

  require_cmds docker curl awk mkdir printf grep || true
  ok "Ambiente validado"
}

setup_application_dir() {
  log "Preparando diretório ${APPLICATION_DIRECTORY}"
  mkdir -p "${APPLICATION_DIRECTORY}"
  cd "${APPLICATION_DIRECTORY}"
  ok "Diretório pronto"
}

create_html() {
  log "Criando ${HTML_FILE_NAME}"
  cat > "${HTML_FILE_NAME}" <<'HTML'
<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Hello, Cruel World!</title>
<style>body{font-family:Arial, sans-serif;margin:40px;background:#f0f0f0;text-align:center}.container{background:#fff;padding:30px;border-radius:10px;max-width:600px;margin:0 auto;box-shadow:0 0 10px rgba(0,0,0,.1)}h1{color:#333}</style>
</head>
<body><div class="container"><h1>Hello, Cruel World!</h1><p>Served by NGINX in a Docker container.</p></div></body>
</html>
HTML
  [ -f "${HTML_FILE_NAME}" ] || fail "Falha ao criar HTML"
  ok "HTML criado"
}

create_dockerfile() {
  log "Criando ${DOCKERFILE_NAME}"
  cat > "${DOCKERFILE_NAME}" <<DOCKER
FROM nginx:alpine
COPY ${HTML_FILE_NAME} /usr/share/nginx/html/index.html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
DOCKER
  [ -f "${DOCKERFILE_NAME}" ] || fail "Falha ao criar Dockerfile"
  ok "Dockerfile criado"
}

docker_login() {
  log "Logando no Docker Hub como ${DOCKER_HUB_USERNAME}"
  local token="${DOCKER_HUB_TOKEN}"
  local masked
  masked=$(mask_token "$token")
  printf "Usando DOCKER_HUB_TOKEN: %s\n" "${masked}"

  local out
  out=$(printf "%s" "${token}" | docker login --username "${DOCKER_HUB_USERNAME}" --password-stdin 2>&1) || true

  if echo "${out}" | grep -qi 'unauthorized\|incorrect username or password'; then
    err "Credenciais incorretas ou token inválido"
    err "Mensagem do docker: ${out}"
    fail "Login falhou"
  fi

  if echo "${out}" | grep -qi 'error'; then
    err "Mensagem do docker: ${out}"
    fail "Login falhou"
  fi

  ok "Login efetuado"
}

build_image() {
  log "Construindo imagem ${DOCKER_HUB_USERNAME}/${DOCKER_IMAGE_NAME}:${IMAGE_TAG}"
  docker build -t "${DOCKER_HUB_USERNAME}/${DOCKER_IMAGE_NAME}:${IMAGE_TAG}" . || fail "Build falhou"
  ok "Imagem construída"
}

push_image() {
  log "Fazendo push para hub.docker.com"
  docker push "${DOCKER_HUB_USERNAME}/${DOCKER_IMAGE_NAME}:${IMAGE_TAG}" || fail "Push falhou"
  ok "Imagem enviada"
}

test_container() {
  log "Testando container em http://localhost:${DOCKER_HOST_PORT}"
  if docker ps -a --filter "name=${DOCKER_CONTAINER_NAME}" --format '{{.Names}}' | grep -qx "${DOCKER_CONTAINER_NAME}"; then
    docker rm -f "${DOCKER_CONTAINER_NAME}" >/dev/null 2>&1 || true
  fi

  docker run -d --name "${DOCKER_CONTAINER_NAME}" -p "${DOCKER_HOST_PORT}:${DOCKER_CONTAINER_PORT}" "${DOCKER_HUB_USERNAME}/${DOCKER_IMAGE_NAME}:${IMAGE_TAG}" >/dev/null
  sleep 2

  if curl -s "http://localhost:${DOCKER_HOST_PORT}" | grep -q "Hello, Cruel World!"; then
    ok "Aplicação respondeu"
    docker rm -f "${DOCKER_CONTAINER_NAME}" >/dev/null 2>&1 || true
    return
  fi

  docker logs "${DOCKER_CONTAINER_NAME}" || true
  docker rm -f "${DOCKER_CONTAINER_NAME}" >/dev/null 2>&1 || true
  fail "Teste do container falhou"
}

cleanup() { true; }

on_exit() {
  local rc=$?
  if [ "$rc" -ne 0 ]; then
    err "Script finalizado com código ${rc}"
  fi
}
trap on_exit EXIT

main() {
  validate_env
  setup_application_dir
  create_html
  create_dockerfile
  docker_login
  build_image
  push_image
  test_container
  cleanup
  ok "Fluxo concluído"
}

main "$@"

