#!/usr/bin/env bash
# Demonstração completa do Blender Compiler:
# 1) gera imagens sintéticas de exemplo
# 2) roda o pipeline completo (images -> .blend)
# 3) imprime um resumo dos artefatos gerados
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== [1/3] Gerando imagens de exemplo (examples/input/) ==="
python3 scripts/generate_example_images.py --out examples/input

echo ""
echo "=== [2/3] Rodando pipeline completo (compile) ==="
PYTHONPATH=src python3 cli.py compile examples/input \
    --output examples/output \
    --name demo_character

echo ""
echo "=== [3/3] Resumo dos artefatos gerados ==="
find examples/output -maxdepth 2 -type d | sort
echo ""
echo "Arquivos de export:"
ls -la examples/output/04_export/ 2>/dev/null || echo "(nenhum artefato de export encontrado)"

echo ""
echo "Demo concluída. Abra o .blend gerado em examples/output/04_export/ no Blender."
