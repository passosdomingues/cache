.PHONY: build test lint format typecheck docs run clean release demo shell docker-build docker-run help

PYTHON ?= python3
PIP ?= pip3
IMAGE_NAME ?= blender-compiler
INPUT_DIR ?= examples/input
OUTPUT_DIR ?= output
OBJECT_NAME ?= object
VERSION := $(shell grep -m1 version pyproject.toml | cut -d '"' -f2)

help:
	@echo "Alvos disponiveis:"
	@echo "  make build          - instala dependencias (venv/pip local)"
	@echo "  make test           - roda pytest com cobertura"
	@echo "  make lint           - roda ruff + black --check + mypy"
	@echo "  make format         - aplica black + ruff --fix"
	@echo "  make docs           - valida diagramas mermaid e gera indice de docs"
	@echo "  make run            - roda o pipeline completo em examples/input"
	@echo "  make demo           - roda scripts/demo.sh (gera imagens + pipeline + resumo)"
	@echo "  make clean          - remove artefatos gerados (output/, logs/, caches)"
	@echo "  make release        - empacota o projeto inteiro em dist/blender-compiler-<versao>.zip"
	@echo "  make docker-build   - constroi a imagem Docker (com Blender real)"
	@echo "  make docker-run     - roda o pipeline dentro do container"

build:
	$(PIP) install --break-system-packages -r requirements-dev.txt

test:
	PYTHONPATH=src $(PYTHON) -m pytest tests/ -v --cov=src/blender_compiler --cov-report=term-missing

lint:
	ruff check src/ cli.py tests/
	black --check src/ cli.py tests/
	mypy src/blender_compiler --ignore-missing-imports || true

format:
	ruff check --fix src/ cli.py tests/
	black src/ cli.py tests/

docs:
	@echo "Verificando presenca dos documentos obrigatorios..."
	@test -f docs/architecture.md && echo "  [ok] docs/architecture.md"
	@test -f docs/api.md && echo "  [ok] docs/api.md"
	@test -f docs/contributing.md && echo "  [ok] docs/contributing.md"
	@echo "Documentacao OK."

run:
	PYTHONPATH=src $(PYTHON) cli.py compile $(INPUT_DIR) --output $(OUTPUT_DIR) --name $(OBJECT_NAME)

demo:
	bash scripts/demo.sh

clean:
	rm -rf output/*  logs/*.log .pytest_cache **/__pycache__ .mypy_cache .ruff_cache dist build
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "Limpo."

release: test
	mkdir -p dist
	bash scripts/make_release.sh "$(VERSION)"

docker-build:
	docker build -t $(IMAGE_NAME):latest -f Dockerfile .

docker-run:
	docker compose run --rm blender-compiler \
		compile /app/input --output /app/output --name $(OBJECT_NAME)

shell:
	docker compose run --rm --entrypoint /bin/bash blender-compiler
