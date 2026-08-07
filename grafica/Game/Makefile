# ============================================================
# Makefile — As Águas de Apsu
# ============================================================
# Targets disponíveis:
#   make build        → Compila com Maven
#   make run          → Compila e roda via Maven (baixa JavaFX se necessário)
#   make run-local    → Roda usando JAVAFX_PATH local (sem Maven)
#   make package      → Gera fat JAR em target/
#   make docker-build → Cria imagem Docker
#   make docker-run   → Roda o jogo dentro do Docker (requer X11)
#   make mpi-demo     → Compila e roda o gerador de mapa paralelo (MPI)
#   make clean        → Remove arquivos de build
#   make help         → Exibe esta mensagem
# ============================================================

# --- Configurações ---
APP_NAME     := apsu-game
VERSION      := 0.2.0-SNAPSHOT
MAIN_CLASS   := ApsuGame
SRC_DIR      := src/main/java
RES_DIR      := src/main/resources
TARGET_DIR   := target
MPI_DIR      := mpi

# JavaFX local — pode sobrescrever na linha de comando:
#   JAVAFX_PATH=/outro/caminho make run-local
JAVAFX_PATH  ?= /opt/javafx-21/lib
JAVAFX_MODS  := javafx.controls,javafx.graphics,javafx.media

# JDK 21 Temurin — detectado automaticamente
# Maven usa JAVA_HOME, build-local usa JDK21 diretamente
JDK21        ?= /opt/java-temurin-21
JAVA         := $(JDK21)/bin/java
JAVAC        := $(JDK21)/bin/javac
MVN          := JAVA_HOME=$(JDK21) mvn

# Docker
DOCKER_IMG   := $(APP_NAME):$(VERSION)
DISPLAY      ?= :0

# MPI
MPICC        := mpicc
MPIRUN       := mpirun
MPI_CORES    := 8
MPI_SRC      := $(MPI_DIR)/MapGenerator.c
MPI_BIN      := $(MPI_DIR)/map_gen

# Cores do terminal
RED    := \033[0;31m
GREEN  := \033[0;32m
YELLOW := \033[1;33m
CYAN   := \033[0;36m
BOLD   := \033[1m
RESET  := \033[0m

# ============================================================
.PHONY: all build run run-local package docker-build docker-run \
        mpi-demo mpi-build mpi-run clean help check-java check-docker check-mpi

# Target padrão
all: run

# ============================================================
# BUILD & RUN
# ============================================================

## Compila o projeto com Maven
build: check-java
	@echo "$(CYAN)$(BOLD)▶ Compilando com Maven...$(RESET)"
	$(MVN) compile -q
	@echo "$(GREEN)✓ Compilação concluída$(RESET)"

## Compila e executa via Maven (baixa JavaFX automaticamente se necessário)
run: check-java
	@echo "$(CYAN)$(BOLD)▶ Iniciando As Águas de Apsu via Maven...$(RESET)"
	$(MVN) javafx:run

## Executa usando JavaFX local em JAVAFX_PATH (sem Maven, mais rápido)
run-local: check-java build-local
	@echo "$(CYAN)$(BOLD)▶ Iniciando com JavaFX local: $(JAVAFX_PATH)$(RESET)"
	$(JAVA) \
		--module-path "$(JAVAFX_PATH)" \
		--add-modules $(JAVAFX_MODS) \
		-cp "$(TARGET_DIR)/classes:$(RES_DIR)" \
		$(MAIN_CLASS)

## Compila diretamente com javac + JAVAFX_PATH (sem Maven)
build-local: check-java
	@echo "$(CYAN)▶ Compilando com javac + JavaFX local...$(RESET)"
	@mkdir -p $(TARGET_DIR)/classes
	@cp -r $(RES_DIR)/* $(TARGET_DIR)/classes/ 2>/dev/null || true
	$(JAVAC) \
		--module-path "$(JAVAFX_PATH)" \
		--add-modules $(JAVAFX_MODS) \
		-d $(TARGET_DIR)/classes \
		$(SRC_DIR)/$(MAIN_CLASS).java
	@echo "$(GREEN)✓ Compilação local concluída$(RESET)"

## Gera fat JAR executável em target/
package: check-java
	@echo "$(CYAN)$(BOLD)▶ Gerando fat JAR...$(RESET)"
	$(MVN) package -q -DskipTests
	@echo "$(GREEN)✓ JAR gerado: target/$(APP_NAME)-$(VERSION).jar$(RESET)"
	@echo "$(YELLOW)  Para executar: java -jar target/$(APP_NAME)-$(VERSION).jar$(RESET)"
	@ls -lh $(TARGET_DIR)/$(APP_NAME)-$(VERSION).jar 2>/dev/null || true

# ============================================================
# DOCKER
# ============================================================

## Verifica se Docker está disponível
check-docker:
	@docker info > /dev/null 2>&1 || \
		(echo "$(RED)✗ Docker não está rodando. Inicie o Docker daemon primeiro.$(RESET)" && exit 1)

## Constrói a imagem Docker
docker-build: check-docker
	@echo "$(CYAN)$(BOLD)▶ Construindo imagem Docker: $(DOCKER_IMG)$(RESET)"
	docker build -t $(DOCKER_IMG) .
	@echo "$(GREEN)✓ Imagem criada: $(DOCKER_IMG)$(RESET)"

## Roda o jogo dentro do Docker (via X11 forwarding)
docker-run: check-docker
	@echo "$(CYAN)$(BOLD)▶ Iniciando container Docker...$(RESET)"
	@echo "$(YELLOW)  Configurando X11 forwarding...$(RESET)"
	xhost +local:docker > /dev/null 2>&1 || true
	docker run --rm \
		-e DISPLAY=$(DISPLAY) \
		-v /tmp/.X11-unix:/tmp/.X11-unix:rw \
		--name $(APP_NAME) \
		$(DOCKER_IMG)

## Para container em execução
docker-stop:
	@docker stop $(APP_NAME) 2>/dev/null || echo "$(YELLOW)Container não está rodando$(RESET)"

# ============================================================
# MPI — Demo de geração paralela de mapa
# ============================================================

## Verifica se OpenMPI está disponível
check-mpi:
	@command -v $(MPICC) > /dev/null 2>&1 || \
		(echo "$(YELLOW)⚠ OpenMPI não encontrado. Instalando...$(RESET)" && \
		 sudo apt-get install -y openmpi-bin libopenmpi-dev -q && \
		 echo "$(GREEN)✓ OpenMPI instalado$(RESET)")

## Compila o gerador de mapa MPI
mpi-build: check-mpi
	@echo "$(CYAN)▶ Compilando MapGenerator.c com MPI...$(RESET)"
	@mkdir -p $(MPI_DIR)
	$(MPICC) -O2 -Wall -o $(MPI_BIN) $(MPI_SRC)
	@echo "$(GREEN)✓ Compilado: $(MPI_BIN)$(RESET)"

## Executa a demo MPI com 8 processos (aproveitando os 8 cores do i7-8565U)
mpi-run: mpi-build
	@echo "$(CYAN)$(BOLD)▶ Rodando gerador de mapa paralelo com $(MPI_CORES) processos...$(RESET)"
	$(MPIRUN) --oversubscribe -np $(MPI_CORES) $(MPI_BIN)

## Alias conveniente
mpi-demo: mpi-run

# ============================================================
# UTILITÁRIOS
# ============================================================

## Verifica se Java 21 está disponível
check-java:
	@$(JAVA) -version 2>&1 | grep -E "version \"(21|22|23|24|25)" > /dev/null || \
		(echo "$(RED)✗ JDK 21+ necessário. Java encontrado:$(RESET)" && \
		 $(JAVA) -version && \
		 echo "$(YELLOW)  Fix: export JDK21=/opt/java-temurin-21$(RESET)" && exit 1)

## Para containers e processos remanescentes (Docker, MPI, Java)
stop:
	@echo "$(YELLOW)🛑 Parando containers Docker e processos do ApsuGame...$(RESET)"
	@docker stop $(DOCKER_CONTAINER) 2>/dev/null || true
	@pkill -f "apsu-game" 2>/dev/null || true
	@pkill -f "MapGenerator" 2>/dev/null || true
	@echo "$(GREEN)✓ Todos os processos parados.$(RESET)"

## Remove arquivos de build e limpa a memória
clean: stop
	@echo "$(YELLOW)🧹 Limpando diretórios de build (target/ e binários MPI)...$(RESET)"
	@rm -rf $(TARGET_DIR) $(MPI_DIR)/map_gen $(MPI_DIR)/*.o
	@echo "$(GREEN)✓ Limpeza concluída.$(RESET)"

## Exibe ajuda com todos os targets
help:
	@echo ""
	@echo "$(BOLD)╔══════════════════════════════════════════════╗$(RESET)"
	@echo "$(BOLD)║      As Águas de Apsu — Makefile Help        ║$(RESET)"
	@echo "$(BOLD)╚══════════════════════════════════════════════╝$(RESET)"
	@echo ""
	@echo "$(BOLD)BUILD & RUN:$(RESET)"
	@echo "  $(GREEN)make build$(RESET)         Compila com Maven"
	@echo "  $(GREEN)make run$(RESET)           Compila e executa via Maven"
	@echo "  $(GREEN)make run-local$(RESET)     Executa com JAVAFX_PATH=$(JAVAFX_PATH)"
	@echo "  $(GREEN)make package$(RESET)       Gera fat JAR em target/"
	@echo ""
	@echo "$(BOLD)DOCKER:$(RESET)"
	@echo "  $(CYAN)make docker-build$(RESET)  Constrói imagem Docker"
	@echo "  $(CYAN)make docker-run$(RESET)    Executa jogo em container Docker"
	@echo "  $(CYAN)make docker-stop$(RESET)   Para container em execução"
	@echo ""
	@echo "$(BOLD)MPI:$(RESET)"
	@echo "  $(YELLOW)make mpi-demo$(RESET)      Compila e roda gerador de mapa paralelo"
	@echo "  $(YELLOW)make mpi-build$(RESET)     Apenas compila o MapGenerator.c"
	@echo "  $(YELLOW)make mpi-run$(RESET)       Apenas executa ($(MPI_CORES) processos)"
	@echo ""
	@echo "$(BOLD)UTILITÁRIOS:$(RESET)"
	@echo "  $(RED)make clean$(RESET)         Remove arquivos de build"
	@echo "  make help          Exibe esta mensagem"
	@echo ""
	@echo "$(BOLD)VARIÁVEIS CONFIGURÁVEIS:$(RESET)"
	@echo "  JAVAFX_PATH=$(JAVAFX_PATH)"
	@echo "  MPI_CORES=$(MPI_CORES)"
	@echo "  DISPLAY=$(DISPLAY)"
	@echo ""
	@echo "$(BOLD)EXEMPLO:$(RESET)"
	@echo "  JAVAFX_PATH=/opt/javafx-21/lib make run-local"
	@echo "  MPI_CORES=4 make mpi-demo"
	@echo ""
