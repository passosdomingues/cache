\
# Atalhos de conveniência sobre CMake/CTest. Nenhuma lógica de build vive
# aqui — apenas encaminha para scripts/ e para o build gerado pelo CMake.

BUILD_DIR  ?= build
BUILD_TYPE ?= Release

.PHONY: all build run test bench clean rebuild help

all: build

## Configura e compila o projeto (CMake + Ninja/Make, conforme disponível).
build:
	@./scripts/build.sh $(BUILD_TYPE)

## Compila (se preciso) e roda o hello-engine (Sprint 0).
run: build
	@./scripts/run.sh

## Compila e roda todos os testes registrados via CTest.
test: build
	@ctest --test-dir $(BUILD_DIR) --output-on-failure

## Compila e roda o benchmark do Job System (Sprint 2): 100.000 jobs.
bench: build
	@$(BUILD_DIR)/src/jobs/job-benchmark

## Roda o exemplo do assetc (Sprint 3): compila o manifesto de exemplo,
## roda de novo pra mostrar cache hit, e inspeciona o pacote gerado.
assetc-example: build
	@$(BUILD_DIR)/tools/assetc/assetc build \
		--manifest=tools/assetc/examples/assets.manifest \
		--out=$(BUILD_DIR)/example.pkg
	@$(BUILD_DIR)/tools/assetc/assetc build \
		--manifest=tools/assetc/examples/assets.manifest \
		--out=$(BUILD_DIR)/example.pkg
	@$(BUILD_DIR)/tools/assetc/assetc inspect $(BUILD_DIR)/example.pkg

## Roda o exemplo de atlas do assetc (Sprint 4): pipeline de imagem +
## Sprite Compiler. Requer ImageMagick (sudo apt install imagemagick).
atlas-example: build
	@$(BUILD_DIR)/tools/assetc/assetc build \
		--manifest=tools/assetc/examples/atlas.manifest \
		--out=$(BUILD_DIR)/atlas-example.pkg
	@$(BUILD_DIR)/tools/assetc/assetc inspect $(BUILD_DIR)/atlas-example.pkg

## Remove o diretório de build inteiro.
clean:
	@rm -rf $(BUILD_DIR)

## Build limpo do zero.
rebuild: clean build

help:
	@echo "Alvos disponíveis:"
	@echo "  make build    - configura e compila (BUILD_TYPE=$(BUILD_TYPE))"
	@echo "  make run      - compila e roda o hello-engine"
	@echo "  make test     - compila e roda todos os testes (CTest)"
	@echo "  make bench    - compila e roda o job-benchmark (100.000 jobs)"
	@echo "  make assetc-example - roda o exemplo do assetc (build + cache hit + inspect)"
	@echo "  make atlas-example  - roda o exemplo de atlas/image pipeline (Sprint 4)"
	@echo "  make clean    - remove o diretório de build"
	@echo "  make rebuild  - clean + build"
