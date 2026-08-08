#!/usr/bin/env bash
# Empacota o projeto em dist/blender-compiler-<versao>.zip, excluindo
# artefatos gerados (output, logs, caches) para manter a release limpa.
set -euo pipefail

cd "$(dirname "$0")/.."

VERSION="${1:-0.1.0}"
DIST_DIR="dist"
STAGE_NAME="blender-compiler-${VERSION}"
STAGE_DIR="${DIST_DIR}/${STAGE_NAME}"
ZIP_PATH="${DIST_DIR}/${STAGE_NAME}.zip"

rm -rf "${STAGE_DIR}" "${ZIP_PATH}"
mkdir -p "${STAGE_DIR}"

EXCLUDE_REGEX='(^\./\.git/|/__pycache__/|\.pyc$|^\./\.pytest_cache/|^\./\.mypy_cache/|^\./\.ruff_cache/|^\./dist/|^\./output/[^.]|^\./logs/[^.])'

find . -type f | grep -Ev "${EXCLUDE_REGEX}" | while IFS= read -r f; do
    dest="${STAGE_DIR}/${f#./}"
    mkdir -p "$(dirname "${dest}")"
    cp "${f}" "${dest}"
done

mkdir -p "${STAGE_DIR}/output" "${STAGE_DIR}/logs" "${STAGE_DIR}/input"
touch "${STAGE_DIR}/output/.gitkeep" "${STAGE_DIR}/logs/.gitkeep" "${STAGE_DIR}/input/.gitkeep"

(cd "${DIST_DIR}" && zip -qr "${STAGE_NAME}.zip" "${STAGE_NAME}")

echo "Release criada: ${ZIP_PATH}"
du -h "${ZIP_PATH}"
