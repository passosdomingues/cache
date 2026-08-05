BUILD_DIR      := build
IMAGE_NAME     := mpi-didatico-cpp
NP             ?= 4

BOLD   := \033[1m
CYAN   := \033[36m
GREEN  := \033[32m
YELLOW := \033[33m
RED    := \033[31m
RESET  := \033[0m

.PHONY: all build run benchmark plot simulate clean docker-build docker-run docker-shell help

all: build

build:
	@echo "\n$(BOLD)$(GREEN)▶ Configurando e Compilando (C++17 + MPI)...$(RESET)"
	cmake -B $(BUILD_DIR) -DCMAKE_BUILD_TYPE=Release -Wno-dev
	cmake --build $(BUILD_DIR) -j$(shell nproc)
	@echo "\n$(BOLD)$(GREEN)✔ Binário pronto: $(BUILD_DIR)/mpi_didatico$(RESET)\n"

run: build
	@echo "\n$(BOLD)$(CYAN)▶ Executando Roteiro Didático MPI com NP=$(NP)...$(RESET)\n"
	mpirun --oversubscribe -np $(NP) ./$(BUILD_DIR)/mpi_didatico --all

benchmark: build
	@echo "\n$(BOLD)$(YELLOW)▶ Executando Benchmarks Didáticos com NP=$(NP)...$(RESET)\n"
	mpirun --oversubscribe -np $(NP) ./$(BUILD_DIR)/mpi_didatico --benchmark

plot:
	@echo "\n$(BOLD)$(CYAN)▶ Instalando dependências Python para gráficos...$(RESET)"
	python3 -m pip install -q --break-system-packages -r scripts/requirements.txt 2>/dev/null || true
	@echo "\n$(BOLD)$(CYAN)▶ Gerando gráficos didáticos...$(RESET)\n"
	python3 scripts/generate_charts.py
	@echo "\n$(BOLD)$(GREEN)✔ Gráficos salvos em plots/! Visualize com: xdg-open plots/mpi_performance.png$(RESET)\n"

simulate: run plot

docker-build:
	@echo "\n$(BOLD)$(CYAN)▶ Construindo imagem Docker: $(IMAGE_NAME)...$(RESET)\n"
	docker build -t $(IMAGE_NAME) .

docker-run: docker-build
	@echo "\n$(BOLD)$(CYAN)▶ Executando em Container Docker (NP=$(NP))...$(RESET)\n"
	docker run --rm -v "$(PWD)/plots:/app/plots" $(IMAGE_NAME) mpirun --allow-run-as-root --oversubscribe -np $(NP) ./build/mpi_didatico --all

docker-shell: docker-build
	docker run --rm -it -v "$(PWD)/plots:/app/plots" $(IMAGE_NAME) bash

clean:
	@echo "$(BOLD)$(RED)▶ Limpando artefatos de build...$(RESET)"
	rm -rf $(BUILD_DIR) plots/*.png data/output/*.csv
	@echo "$(BOLD)$(GREEN)✔ Limpeza concluída$(RESET)"

help:
	@echo ""
	@echo "$(BOLD)$(CYAN)Roteiro Didático MPI C++ — Comandos Disponíveis:$(RESET)"
	@echo "  make run        - Executa todas as lições didáticas (NP=4 por padrão)"
	@echo "  make benchmark  - Roda os testes de performance e latência"
	@echo "  make plot       - Gera os gráficos das medições em plots/"
	@echo "  make simulate   - Roda tudo (lições + benchmark + gráficos)"
	@echo "  make docker-run - Roda dentro do Docker"
	@echo ""
