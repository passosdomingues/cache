#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${ROOT_DIR}/build"
BUILD_TYPE="${1:-Release}"

echo "== Configurando (build type: ${BUILD_TYPE}) =="
cmake -S "${ROOT_DIR}" -B "${BUILD_DIR}" -DCMAKE_BUILD_TYPE="${BUILD_TYPE}"

echo "== Compilando =="
cmake --build "${BUILD_DIR}" -j"$(nproc)"

echo "== Build concluído: ${BUILD_DIR}/src/core/hello-engine =="
