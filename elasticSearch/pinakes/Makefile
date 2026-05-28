SHELL := /bin/bash

# ─── Paleta de cores ──────────────────────────────────────────
C_RESET   := \033[0m
C_BOLD    := \033[1m
C_DIM     := \033[2m
C_ITALIC  := \033[3m
C_RED     := \033[0;31m
C_GREEN   := \033[0;32m
C_YELLOW  := \033[0;33m
C_BLUE    := \033[0;34m
C_MAGENTA := \033[0;35m
C_CYAN    := \033[0;36m

# ─── Caminhos ─────────────────────────────────────────────────
PROJECT_DIR := $(shell pwd)
DEPS_DIR    := $(PROJECT_DIR)/deps
DOCKER_DIR  := $(PROJECT_DIR)/deps/docker

# JDK 17 — armazenado em ~/java com symlink ~/java/current
JDK_TARBALL  := $(DEPS_DIR)/jdk-17.0.12_linux-x64_bin.tar.gz
JDK_DIR      := $(HOME)/java/jdk-17.0.12
JAVA_CURRENT := $(HOME)/java/current

# JDK 21 (Temurin já instalado no sistema)
JDK_21_DIR   := /opt/java-temurin-21

# ─── Arquivos do Maven Wrapper ─────────────────────────────────
MVNW_SCRIPT   := ./mvnw
MVNW_DIR      := .mvn/wrapper
MVNW_JAR      := $(MVNW_DIR)/maven-wrapper.jar
MVNW_PROPS    := $(MVNW_DIR)/maven-wrapper.properties
MVNW_JAR_URL  := https://repo.maven.apache.org/maven2/org/apache/maven/wrapper/maven-wrapper/3.2.0/maven-wrapper-3.2.0.jar
MAVEN_DIST_URL := https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/3.9.6/apache-maven-3.9.6-bin.zip

# ─── Ambiente Java (JDK 17 via symlink) ────────────────────────
export JAVA_HOME := $(JAVA_CURRENT)
export PATH      := $(JAVA_HOME)/bin:$(PATH)

# ─── Ferramentas de download ───────────────────────────────────
WGET := $(shell which wget 2>/dev/null)
CURL := $(shell which curl 2>/dev/null)

# ─── Resultado de performance ─────────────────────────────────
RESULTS_DIR := results

# ═══════════════════════════════════════════════════════════════
.PHONY: help all deps clean \
        compile build run \
        test test-all integration \
        infra-up infra-down up down down-v \
        logs logs-app \
        java-install use-java-17 use-java-21 java-version \
        docs test-api postman-import \
        seed perf perf-docker results fmt ci

# ─── Ajuda ────────────────────────────────────────────────────
help:
	@echo -e "\n$(C_BOLD)╔══════════════════════════════════════════════╗$(C_RESET)"
	@echo -e "$(C_BOLD)║       Pinakes — Comandos Makefile            ║$(C_RESET)"
	@echo -e "$(C_BOLD)╚══════════════════════════════════════════════╝$(C_RESET)\n"
	@echo -e "$(C_CYAN)── Projeto ──────────────────────────────────$(C_RESET)"
	@printf "  ${C_GREEN}%-20s${C_RESET}  %s\n" "make all"            "infra-up + deps + compile (idempotente)"
	@printf "  ${C_GREEN}%-20s${C_RESET}  %s\n" "make deps"           "Prepara JDK 17 e Maven Wrapper"
	@printf "  ${C_GREEN}%-20s${C_RESET}  %s\n" "make compile"        "Compila o projeto com JDK 17"
	@printf "  ${C_GREEN}%-20s${C_RESET}  %s\n" "make build"          "Empacota .jar (skips tests)"
	@printf "  ${C_GREEN}%-20s${C_RESET}  %s\n" "make run"            "Sobe infra + app (http://localhost:8080)"
	@printf "  ${C_GREEN}%-20s${C_RESET}  %s\n" "make clean"          "Remove artefatos de build e para containers"
	@echo ""
	@echo -e "$(C_CYAN)── Testes ───────────────────────────────────$(C_RESET)"
	@printf "  ${C_GREEN}%-20s${C_RESET}  %s\n" "make test"           "Testes unitários (sem Docker, sem ES)"
	@printf "  ${C_GREEN}%-20s${C_RESET}  %s\n" "make test-all"       "Todos os testes, incluindo integração (Docker)"
	@printf "  ${C_GREEN}%-20s${C_RESET}  %s\n" "make integration"    "Testes de integração via Testcontainers"
	@printf "  ${C_GREEN}%-20s${C_RESET}  %s\n" "make ci"             "Pipeline completa: build + unit + integration"
	@printf "  ${C_GREEN}%-20s${C_RESET}  %s\n" "make test-api"       "Testa endpoints via curl (requer app rodando)"
	@echo ""
	@echo -e "$(C_CYAN)── Infraestrutura ───────────────────────────$(C_RESET)"
	@printf "  ${C_GREEN}%-20s${C_RESET}  %s\n" "make infra-up"       "Sobe Elasticsearch + aguarda health check"
	@printf "  ${C_GREEN}%-20s${C_RESET}  %s\n" "make infra-down"     "Para os containers graciosamente"
	@printf "  ${C_GREEN}%-20s${C_RESET}  %s\n" "make up"             "Alias de infra-up (app + ES em Docker)"
	@printf "  ${C_GREEN}%-20s${C_RESET}  %s\n" "make down"           "Para containers (dados preservados no volume)"
	@printf "  ${C_GREEN}%-20s${C_RESET}  %s\n" "make down-v"         "Para containers E remove volumes (apaga dados!)"
	@printf "  ${C_GREEN}%-20s${C_RESET}  %s\n" "make logs"           "Tail de todos os logs dos containers"
	@printf "  ${C_GREEN}%-20s${C_RESET}  %s\n" "make logs-app"       "Tail dos logs somente da aplicação"
	@echo ""
	@echo -e "$(C_CYAN)── Java ─────────────────────────────────────$(C_RESET)"
	@printf "  ${C_GREEN}%-20s${C_RESET}  %s\n" "make java-install"   "Instala JDK 17 em ~/java com symlink"
	@printf "  ${C_GREEN}%-20s${C_RESET}  %s\n" "make use-java-17"    "Aponta ~/java/current → JDK 17"
	@printf "  ${C_GREEN}%-20s${C_RESET}  %s\n" "make use-java-21"    "Aponta ~/java/current → JDK 21 (Temurin)"
	@printf "  ${C_GREEN}%-20s${C_RESET}  %s\n" "make java-version"   "Exibe versão Java ativa"
	@echo ""
	@echo -e "$(C_CYAN)── Dados & Qualidade ────────────────────────$(C_RESET)"
	@printf "  ${C_GREEN}%-20s${C_RESET}  %s\n" "make seed"           "Popula o ES com o dataset Wikipedia"
	@printf "  ${C_GREEN}%-20s${C_RESET}  %s\n" "make perf"           "Sobe stack + suite de testes Python"
	@printf "  ${C_GREEN}%-20s${C_RESET}  %s\n" "make perf-docker"    "Testes de performance dentro do Docker (CI)"
	@printf "  ${C_GREEN}%-20s${C_RESET}  %s\n" "make results"        "Lista arquivos de resultado gerados"
	@echo ""
	@echo -e "$(C_CYAN)── Documentação ─────────────────────────────$(C_RESET)"
	@printf "  ${C_GREEN}%-20s${C_RESET}  %s\n" "make docs"           "Gera doc/architecture.png + HTML da API"
	@printf "  ${C_GREEN}%-20s${C_RESET}  %s\n" "make postman-import" "Instruções para importar no Postman"
	@printf "  ${C_GREEN}%-20s${C_RESET}  %s\n" "make fmt"            "Formata código Java (google-java-format)"
	@echo ""

# ─── Atalho principal ──────────────────────────────────────────
all: infra-up java-install deps compile
	@echo ""
	@echo -e "$(C_GREEN)╔═══════════════════════════════════════════════════════╗$(C_RESET)"
	@echo -e "$(C_GREEN)║  ✓ Projeto compilado!                                 ║$(C_RESET)"
	@echo -e "$(C_GREEN)║  Execute 'make run' para iniciar a aplicação          ║$(C_RESET)"
	@echo -e "$(C_GREEN)║  Acesse: http://localhost:8080                        ║$(C_RESET)"
	@echo -e "$(C_GREEN)╚═══════════════════════════════════════════════════════╝$(C_RESET)"

# ─── Infraestrutura Docker ─────────────────────────────────────
infra-up:
	@echo -e "$(C_BLUE)[infra-up] Iniciando Elasticsearch...$(C_RESET)"
	@$(MAKE) -s -C $(DOCKER_DIR) up
	@echo -e "$(C_YELLOW)> Aguardando Elasticsearch ficar online...$(C_RESET)"
	@sleep 5
	@$(MAKE) -s -C $(DOCKER_DIR) health || (echo -e "$(C_YELLOW)> Ainda aguardando...$(C_RESET)" && sleep 15 && $(MAKE) -s -C $(DOCKER_DIR) health)
	@echo -e "$(C_GREEN)[infra-up] Infraestrutura pronta!$(C_RESET)"

infra-down:
	@echo -e "$(C_BLUE)[infra-down] Parando infraestrutura...$(C_RESET)"
	@$(MAKE) -s -C $(DOCKER_DIR) down
	@echo -e "$(C_GREEN)[infra-down] Containers parados.$(C_RESET)"

# aliases modernos
up: infra-up

down:
	@echo -e "$(C_BLUE)[down] Parando containers (dados preservados)...$(C_RESET)"
	@docker compose -f $(DOCKER_DIR)/docker-compose.yml down
	@echo -e "$(C_GREEN)[down] Containers parados.$(C_RESET)"

down-v:
	@echo -e "$(C_RED)[down-v] Parando containers E removendo volumes!$(C_RESET)"
	@docker compose -f $(DOCKER_DIR)/docker-compose.yml down -v
	@echo -e "$(C_GREEN)[down-v] Feito.$(C_RESET)"

logs:
	@docker compose -f $(DOCKER_DIR)/docker-compose.yml logs -f

logs-app:
	@docker compose -f $(DOCKER_DIR)/docker-compose.yml logs -f app

# ─── JDK 17 — Instalação com symlink ──────────────────────────
java-install: java.ready
	@echo -e "$(C_GREEN)[java-install] JDK 17 pronto em ~/java/current$(C_RESET)"

java.ready: $(JAVA_CURRENT)/bin/java
	@touch java.ready

$(JAVA_CURRENT)/bin/java:
	@echo -e "$(C_YELLOW)> Configurando JDK 17...$(C_RESET)"
	@if [ ! -f "$(JDK_TARBALL)" ]; then \
		echo -e "$(C_RED)[ERRO] Tarball não encontrado: $(JDK_TARBALL)$(C_RESET)"; \
		echo -e "$(C_DIM)  Coloque o arquivo em: $(DEPS_DIR)/$(C_RESET)"; \
		exit 1; \
	fi
	@if [ -d "$(JDK_DIR)" ]; then \
		echo -e "$(C_DIM)  JDK 17 já extraído, ignorando.$(C_RESET)"; \
	else \
		echo -e "$(C_BLUE)  Extraindo para ~/java/ ...$(C_RESET)"; \
		mkdir -p $(HOME)/java; \
		tar -xzf $(JDK_TARBALL) -C $(HOME)/java/; \
		echo -e "$(C_GREEN)  Extração concluída.$(C_RESET)"; \
	fi
	@echo -e "$(C_BLUE)  Criando symlink ~/java/current → $(JDK_DIR)$(C_RESET)"
	@ln -sfn $(JDK_DIR) $(JAVA_CURRENT)
	@"$(JAVA_CURRENT)/bin/java" -version 2>&1 | sed 's/^/  /'

use-java-17:
	@if [ ! -d "$(JDK_DIR)" ]; then \
		echo -e "$(C_YELLOW)JDK 17 não encontrado. Execute: make java-install$(C_RESET)"; \
		exit 1; \
	fi
	@ln -sfn $(JDK_DIR) $(JAVA_CURRENT)
	@echo -e "$(C_GREEN)✓ Usando JDK 17:$(C_RESET)"
	@"$(JAVA_CURRENT)/bin/java" -version 2>&1

use-java-21:
	@if [ ! -d "$(JDK_21_DIR)" ]; then \
		echo -e "$(C_RED)[ERRO] JDK 21 não encontrado em $(JDK_21_DIR)$(C_RESET)"; \
		exit 1; \
	fi
	@ln -sfn $(JDK_21_DIR) $(JAVA_CURRENT)
	@echo -e "$(C_GREEN)✓ Usando JDK 21:$(C_RESET)"
	@"$(JAVA_CURRENT)/bin/java" -version 2>&1

java-version:
	@echo -e "$(C_BLUE)Symlink: $(JAVA_CURRENT) → $(shell readlink $(JAVA_CURRENT) 2>/dev/null || echo 'não configurado')$(C_RESET)"
	@"$(JAVA_CURRENT)/bin/java" -version 2>&1 || echo -e "$(C_RED)Execute 'make java-install' primeiro$(C_RESET)"

# ─── Dependências Maven ────────────────────────────────────────
deps: java.ready mvnw.ready
	@echo -e "$(C_GREEN)[deps] Todas as dependências prontas.$(C_RESET)"

mvnw.ready: $(MVNW_JAR) $(MVNW_PROPS)
	@touch mvnw.ready

$(MVNW_DIR):
	@mkdir -p $@

$(MVNW_JAR): | $(MVNW_DIR)
	@echo -e "$(C_YELLOW)> Maven Wrapper JAR ausente. Baixando...$(C_RESET)"
	@if [ -n "$(WGET)" ]; then \
		$(WGET) -q -O $@ $(MVNW_JAR_URL); \
	elif [ -n "$(CURL)" ]; then \
		$(CURL) -sL -o $@ $(MVNW_JAR_URL); \
	else \
		echo -e "$(C_RED)[ERRO] wget ou curl não encontrados.$(C_RESET)"; exit 1; \
	fi
	@echo -e "$(C_GREEN)  Maven Wrapper baixado.$(C_RESET)"

$(MVNW_PROPS):
	@echo "distributionUrl=$(MAVEN_DIST_URL)" > $@
	@echo "wrapperUrl=$(MVNW_JAR_URL)" >> $@

# ─── Compilação ───────────────────────────────────────────────
compile: deps
	@echo -e "$(C_BLUE)[compile] Compilando com JDK 17...$(C_RESET)"
	@$(MVNW_SCRIPT) compile -q
	@echo -e "$(C_GREEN)[compile] Concluído.$(C_RESET)"

build:
	@echo -e "$(C_BLUE)[build] Compilando…$(C_RESET)"
	@$(MVNW_SCRIPT) package -DskipTests -q
	@echo -e "$(C_GREEN)[build] Build concluído.$(C_RESET)"

# ─── Execução ─────────────────────────────────────────────────
run: infra-up compile
	@echo -e "$(C_MAGENTA)"
	@echo "  ╔═══════════════════════════════════════╗"
	@echo "  ║   Pinakes iniciando...                ║"
	@echo "  ║   http://localhost:8080/v1/           ║"
	@echo "  ║   API: http://localhost:8080/v1/search║"
	@echo "  ║   CTRL+C para parar                   ║"
	@echo "  ╚═══════════════════════════════════════╝"
	@echo -e "$(C_RESET)"
	@( \
		while ! curl -s http://localhost:8080/v1/ > /dev/null; do \
			sleep 2; \
		done; \
		echo -e "$(C_GREEN)*** Aplicação pronta! Abrindo navegador...$(C_RESET)"; \
		if command -v xdg-open > /dev/null; then xdg-open http://localhost:8080/v1/; \
		elif command -v open > /dev/null; then open http://localhost:8080/v1/; \
		else python3 -m webbrowser "http://localhost:8080/v1/"; fi \
	) &
	@$(MVNW_SCRIPT) spring-boot:run

# ─── Testes ───────────────────────────────────────────────────
test:
	@echo -e "$(C_BLUE)[test] Rodando testes unitários…$(C_RESET)"
	@$(MVNW_SCRIPT) test -q \
		-Dtest="SearchServiceTest,SearchParamsValidationTest,QueryAnalyserTest" \
		-DfailIfNoTests=false
	@echo -e "$(C_GREEN)[test] Testes unitários OK.$(C_RESET)"

test-all:
	@echo -e "$(C_BLUE)[test-all] Rodando TODOS os testes (Docker obrigatório)…$(C_RESET)"
	@$(MVNW_SCRIPT) verify -q
	@echo -e "$(C_GREEN)[test-all] Concluído.$(C_RESET)"

integration:
	@echo -e "$(C_BLUE)[integration] Rodando testes de integração…$(C_RESET)"
	@$(MVNW_SCRIPT) failsafe:integration-test failsafe:verify -q
	@echo -e "$(C_GREEN)[integration] Testes de integração concluídos.$(C_RESET)"

ci: build test integration
	@echo -e "$(C_GREEN)╔══════════════════════════════╗$(C_RESET)"
	@echo -e "$(C_GREEN)║  ✓ Pipeline CI concluída!    ║$(C_RESET)"
	@echo -e "$(C_GREEN)╚══════════════════════════════╝$(C_RESET)"

# ─── Performance ──────────────────────────────────────────────
perf: infra-up build
	@echo -e "$(C_BLUE)[perf] Iniciando suite de performance...$(C_RESET)"
	@mkdir -p $(RESULTS_DIR)
	@docker compose -f $(DOCKER_DIR)/docker-compose.yml up -d
	@sleep 5
	@cd tests/performance && pip install -q -r requirements.txt && python run_tests.py
	@echo -e "$(C_GREEN)[perf] Suite concluída. Veja $(RESULTS_DIR)/$(C_RESET)"

perf-docker:
	@echo -e "$(C_BLUE)[perf-docker] Testes de performance no Docker (CI)...$(C_RESET)"
	@docker compose -f $(DOCKER_DIR)/docker-compose.yml \
		run --rm perf python run_tests.py
	@echo -e "$(C_GREEN)[perf-docker] Concluído.$(C_RESET)"

results:
	@echo -e "$(C_CYAN)[results] Arquivos gerados:$(C_RESET)"
	@ls -lh $(RESULTS_DIR)/ 2>/dev/null || echo "  Nenhum resultado ainda. Execute 'make perf'."

# ─── Limpeza ──────────────────────────────────────────────────
clean:
	@echo -e "$(C_YELLOW)[clean] Limpando artefatos e parando containers...$(C_RESET)"
	@$(MVNW_SCRIPT) clean -q 2>/dev/null || true
	@docker compose -f $(DOCKER_DIR)/docker-compose.yml down 2>/dev/null || true
	@rm -f java.ready mvnw.ready
	@rm -rf $(RESULTS_DIR)
	@echo -e "$(C_GREEN)[clean] Feito.$(C_RESET)"

# ─── Dados ────────────────────────────────────────────────────
seed:
	@echo -e "$(C_BLUE)[seed] Populando Elasticsearch com dataset Wikipedia...$(C_RESET)"
	@if [ -d "../datasets" ] && [ -f "../datasets/importWiki.sh" ]; then \
		cd ../datasets && chmod +x importWiki.sh && ./importWiki.sh; \
	else \
		echo -e "$(C_RED)[ERRO] Diretório datasets ou importWiki.sh não encontrado em ../datasets$(C_RESET)"; \
		exit 1; \
	fi
	@echo -e "$(C_GREEN)[seed] Carga de dados concluída.$(C_RESET)"

# ─── Documentação ─────────────────────────────────────────────
docs:
	@echo -e "$(C_BLUE)[docs] Gerando documentação...$(C_RESET)"
	@mkdir -p doc
	@if command -v dot &>/dev/null; then \
		dot -Tpng doc/api.dot -o doc/architecture.png && \
		echo -e "$(C_GREEN)  ✓ doc/architecture.png gerado$(C_RESET)"; \
	else \
		echo -e "$(C_YELLOW)  ⚠ Graphviz não encontrado (sudo apt install graphviz)$(C_RESET)"; \
	fi
	@if command -v npx &>/dev/null; then \
		npx --yes @redocly/cli@latest build-docs src/main/resources/api.yml \
			--output doc/api.html --title "Pinakes API" 2>/dev/null && \
		echo -e "$(C_GREEN)  ✓ doc/api.html gerado$(C_RESET)"; \
	else \
		echo -e "$(C_YELLOW)  ⚠ npx não encontrado. HTML da API não gerado.$(C_RESET)"; \
	fi
	@echo -e "$(C_GREEN)[docs] Documentação em doc/$(C_RESET)"

test-api:
	@echo -e "\n$(C_BOLD)=== Testando Pinakes API ===$(C_RESET)\n"
	@echo -e "$(C_CYAN)[1] GET /v1/search?query=computador$(C_RESET)"
	@curl -s -w "\n  HTTP: %{http_code} | Tempo: %{time_total}s\n" \
		"http://localhost:8080/v1/search?query=computador&page=1" \
		-H "Accept: application/json" | python3 -c \
		"import sys,json; data=sys.stdin.read(); \
		 parts=data.rsplit('\n',1); \
		 parsed=json.loads(parts[0]); \
		 print(f'  Resultados: {len(parsed)}'); \
		 [print(f'  [{i+1}] {r.get(\"title\",\"?\")} | {r.get(\"url\",\"?\")}') for i,r in enumerate(parsed[:3])]; \
		 print(parts[1])"
	@echo ""
	@echo -e "$(C_CYAN)[2] GET /v1/search — cabeçalhos de paginação$(C_RESET)"
	@curl -sI "http://localhost:8080/v1/search?query=linux&page=1" \
		| grep -E "X-Total|x-total|HTTP/"
	@echo ""
	@echo -e "$(C_CYAN)[3] GET /v1/suggest?query=equaton$(C_RESET)"
	@curl -s "http://localhost:8080/v1/suggest?query=equaton&size=3" \
		| python3 -m json.tool
	@echo ""
	@echo -e "$(C_CYAN)[4] Frontend Thymeleaf$(C_RESET)"
	@curl -s -o /dev/null -w "  HTTP: %{http_code} | Tamanho: %{size_download} bytes\n" \
		"http://localhost:8080/"
	@echo ""
	@echo -e "$(C_GREEN)=== Testes concluídos ===$(C_RESET)\n"

postman-import:
	@echo -e "\n$(C_BOLD)=== Importando Pinakes API no Postman ===$(C_RESET)\n"
	@echo -e "$(C_BLUE)Opção 1 — Swagger UI (requer app rodando):$(C_RESET)"
	@echo "  http://localhost:8080/v1/swagger-ui.html"
	@echo ""
	@echo -e "$(C_BLUE)Opção 2 — Importar api.yml no Postman:$(C_RESET)"
	@echo "  1. Abra o Postman → Import → File"
	@echo "  2. Selecione: $(PROJECT_DIR)/src/main/resources/api.yml"
	@echo "  3. Configure base_url = http://localhost:8080/v1"
	@echo ""
	@echo -e "$(C_BLUE)Opção 3 — Visualizar online:$(C_RESET)"
	@echo "  https://editor.swagger.io/ → File → Import URL"
	@echo ""
	@echo -e "$(C_BLUE)Opção 4 — Editor local (Redocly):$(C_RESET)"
	@echo "  npx @redocly/cli preview-docs src/main/resources/api.yml"
	@echo ""

fmt:
	@echo -e "$(C_BLUE)[fmt] Formatando Java com google-java-format...$(C_RESET)"
	@if command -v google-java-format &>/dev/null; then \
		find src -name "*.java" | xargs google-java-format -i; \
		echo -e "$(C_GREEN)[fmt] Feito.$(C_RESET)"; \
	else \
		echo -e "$(C_YELLOW)  ⚠ google-java-format não encontrado.$(C_RESET)"; \
		echo    "  Instale: https://github.com/google/google-java-format/releases"; \
	fi
