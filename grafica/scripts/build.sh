#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${ROOT_DIR}/build"
BUILD_TYPE="${1:-Release}"

if [[ ! -f "${BUILD_DIR}/CMakeCache.txt" ]]; then
    echo "== Configurando (build type: ${BUILD_TYPE}) =="
    cmake -S "${ROOT_DIR}" -B "${BUILD_DIR}" -DCMAKE_BUILD_TYPE="${BUILD_TYPE}"
else
    # CMake já regenera sozinho quando algum CMakeLists.txt muda; não
    # precisamos reconfigurar do zero em toda chamada de build/test/bench.
    echo "== Build já configurado em ${BUILD_DIR} =="
fi

echo "== Compilando =="
# --no-print-directory evita o ruido de "Entering/Leaving directory" do
# make recursivo gerado pelo CMake (só afeta o gerador Makefiles; Ninja
# ignora a variável).
MAKEFLAGS="--no-print-directory ${MAKEFLAGS:-}" cmake --build "${BUILD_DIR}" -j"$(nproc)"

echo "== Build concluído: ${BUILD_DIR}/src/core/hello-engine =="
