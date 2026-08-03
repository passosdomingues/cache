#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN="${ROOT_DIR}/build/src/core/hello-engine"

if [[ ! -x "${BIN}" ]]; then
    echo "Executável não encontrado. Rodando build primeiro..."
    "${ROOT_DIR}/scripts/build.sh"
fi

exec "${BIN}"
