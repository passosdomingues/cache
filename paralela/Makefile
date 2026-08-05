# ═══════════════════════════════════════════════════════════════════════════════
# Makefile — AGN Parallel N-Body Simulation
# Targets: build, run, benchmark, docker-build, docker-run, docker-shell, clean
# ═══════════════════════════════════════════════════════════════════════════════

# ── Variables ──────────────────────────────────────────────────────────────────
BUILD_DIR      := build
IMAGE_NAME     := agn-simulation
CONTAINER_NAME := agn_sim

# Number of MPI processes (override with: make run NP=4)
NP ?= 8

# Number of particles (override with: make run N=2000)
N  ?= 1000

# Number of simulation steps
STEPS ?= 500

NCPUS := $(shell nproc)

# ── Colors ─────────────────────────────────────────────────────────────────────
BOLD   := \033[1m
CYAN   := \033[36m
GREEN  := \033[32m
YELLOW := \033[33m
RED    := \033[31m
RESET  := \033[0m

.PHONY: all build run benchmark clean fclean \
        docker-build docker-run docker-shell docker-clean \
        help info

# ── Default target ─────────────────────────────────────────────────────────────
all: build

# ── Info ───────────────────────────────────────────────────────────────────────
info:
	@echo "$(BOLD)$(CYAN)══════════════════════════════════════════════════$(RESET)"
	@echo "$(BOLD)   🌌 AGN N-Body Simulation — Build Info$(RESET)"
	@echo "$(BOLD)$(CYAN)══════════════════════════════════════════════════$(RESET)"
	@echo "  CPU cores available : $(NCPUS)"
	@echo "  MPI processes (NP)  : $(NP)"
	@echo "  Particles (N)       : $(N)"
	@echo "  Steps               : $(STEPS)"
	@echo "  Build directory     : $(BUILD_DIR)"
	@echo "  Docker image        : $(IMAGE_NAME)"
	@echo "$(BOLD)$(CYAN)══════════════════════════════════════════════════$(RESET)"

# ── Local build ────────────────────────────────────────────────────────────────
build: info
	@echo "\n$(BOLD)$(GREEN)▶ Configuring CMake (Release + march=native)...$(RESET)"
	cmake -B $(BUILD_DIR) \
		-DCMAKE_BUILD_TYPE=Release \
		-DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
		-Wno-dev
	@echo "\n$(BOLD)$(GREEN)▶ Compiling with $(NCPUS) threads...$(RESET)"
	cmake --build $(BUILD_DIR) -j$(NCPUS)
	@echo "\n$(BOLD)$(GREEN)✔ Binary ready: $(BUILD_DIR)/agn_simulation$(RESET)\n"

# ── Local run ──────────────────────────────────────────────────────────────────
run: build
	@echo "\n$(BOLD)$(CYAN)▶ Running with NP=$(NP) processes, N=$(N) particles...$(RESET)\n"
	mpirun --oversubscribe -np $(NP) \
		./$(BUILD_DIR)/agn_simulation \
		--particles $(N) \
		--steps $(STEPS)

# ── Speedup benchmark ──────────────────────────────────────────────────────────
benchmark: build
	@echo "\n$(BOLD)$(YELLOW)╔══════════════════════════════════════════╗$(RESET)"
	@echo "$(BOLD)$(YELLOW)║      🚀 MPI Speedup Benchmark            ║$(RESET)"
	@echo "$(BOLD)$(YELLOW)║  i7-8565U — 4 cores / 8 threads          ║$(RESET)"
	@echo "$(BOLD)$(YELLOW)╚══════════════════════════════════════════╝$(RESET)\n"
	@for np in 1 2 4 8; do \
		echo "$(BOLD)── NP=$$np ─────────────────────────────────$(RESET)"; \
		mpirun --oversubscribe -np $$np \
			./$(BUILD_DIR)/agn_simulation \
			--particles $(N) \
			--steps 100 \
			--benchmark; \
		echo ""; \
	done

# ── Generate plots from simulation output ──────────────────────────────────────
plot:
	@echo "\n$(BOLD)$(CYAN)▶ Installing Python dependencies...$(RESET)"
	python3 -m pip install -q --break-system-packages -r scripts/requirements.txt 2>/dev/null || true
	@echo "\n$(BOLD)$(CYAN)▶ Generating plots...$(RESET)\n"
	python3 scripts/plot_simulation.py --data data/output --plots plots
	@echo "\n$(BOLD)$(GREEN)✔ Open plots with: xdg-open plots/galaxy_evolution.png$(RESET)\n"

# ── Run + plot in one command ──────────────────────────────────────────────────
simulate: run plot


# ── Clean ──────────────────────────────────────────────────────────────────────
clean:
	@echo "$(BOLD)$(RED)▶ Removing build artifacts...$(RESET)"
	rm -rf $(BUILD_DIR)
	rm -f data/output/*.csv
	@echo "$(BOLD)$(GREEN)✔ Clean done$(RESET)"

fclean: clean docker-clean

# ═══════════════════════════════════════════════════════════════════════════════
# Docker targets
# ═══════════════════════════════════════════════════════════════════════════════

# ── Build Docker image ─────────────────────────────────────────────────────────
docker-build:
	@echo "\n$(BOLD)$(CYAN)▶ Building Docker image: $(IMAGE_NAME)...$(RESET)\n"
	docker build -t $(IMAGE_NAME) .
	@echo "\n$(BOLD)$(GREEN)✔ Image built: $(IMAGE_NAME)$(RESET)\n"

# ── Run simulation inside Docker ───────────────────────────────────────────────
docker-run: docker-build
	@echo "\n$(BOLD)$(CYAN)▶ Running AGN simulation in Docker (NP=$(NP))...$(RESET)\n"
	docker run --rm \
		--name $(CONTAINER_NAME) \
		-v "$(PWD)/data/output:/agn_sim/data/output" \
		$(IMAGE_NAME) \
		mpirun --allow-run-as-root --oversubscribe -np $(NP) \
			./build/agn_simulation \
			--particles $(N) \
			--steps $(STEPS)

# ── Interactive shell inside Docker ────────────────────────────────────────────
docker-shell: docker-build
	@echo "\n$(BOLD)$(CYAN)▶ Opening interactive shell in Docker...$(RESET)\n"
	docker run --rm -it \
		--name $(CONTAINER_NAME)_shell \
		-v "$(PWD)/data/output:/agn_sim/data/output" \
		$(IMAGE_NAME) bash

# ── Run multi-node cluster with docker-compose ─────────────────────────────────
docker-cluster:
	@echo "\n$(BOLD)$(CYAN)▶ Starting MPI cluster (docker-compose)...$(RESET)\n"
	docker compose up --build
	docker compose down

# ── Remove Docker image ────────────────────────────────────────────────────────
docker-clean:
	@echo "$(BOLD)$(RED)▶ Removing Docker image...$(RESET)"
	docker rmi -f $(IMAGE_NAME) 2>/dev/null || true
	docker compose down --rmi local 2>/dev/null || true

# ── Help ───────────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "$(BOLD)$(CYAN)🌌 AGN Simulation — Available targets:$(RESET)"
	@echo ""
	@echo "  $(BOLD)build$(RESET)          — Compile (Release, -O3 -march=native)"
	@echo "  $(BOLD)run$(RESET)            — Build + run locally (NP=8 default)"
	@echo "  $(BOLD)benchmark$(RESET)      — Speedup test: 1,2,4,8 processes"
	@echo "  $(BOLD)clean$(RESET)          — Remove build/ and output CSVs"
	@echo "  $(BOLD)fclean$(RESET)         — clean + remove Docker image"
	@echo ""
	@echo "  $(BOLD)docker-build$(RESET)   — Build Docker image"
	@echo "  $(BOLD)docker-run$(RESET)     — Run simulation inside Docker"
	@echo "  $(BOLD)docker-shell$(RESET)   — Interactive bash inside Docker"
	@echo "  $(BOLD)docker-cluster$(RESET) — Multi-node cluster via docker-compose"
	@echo ""
	@echo "$(BOLD)Variables:$(RESET)"
	@echo "  NP=<n>    Number of MPI processes (default: 8)"
	@echo "  N=<n>     Number of particles     (default: 1000)"
	@echo "  STEPS=<n> Simulation steps        (default: 500)"
	@echo ""
	@echo "$(BOLD)Examples:$(RESET)"
	@echo "  make run NP=4 N=2000 STEPS=1000"
	@echo "  make benchmark N=500"
	@echo "  make docker-run NP=8"
	@echo ""
