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
DEPS_DIR    := $(shell dirname $(PROJECT_DIR))/deps
DOCKER_DIR  := $(shell dirname $(PROJECT_DIR))/docker

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

# ═══════════════════════════════════════════════════════════════
.PHONY: help deps clean compile run all java-install use-java-17 use-java-21 \
        java-version docs test-api postman-import infra-up infra-down

# ─── Ajuda ────────────────────────────────────────────────────
help:  ## Mostra este menu de ajuda
	@echo -e "\n$(C_BOLD)╔══════════════════════════════════════════════╗$(C_RESET)"
	@echo -e "$(C_BOLD)║       WikiSearch — Comandos Makefile         ║$(C_RESET)"
	@echo -e "$(C_BOLD)╚══════════════════════════════════════════════╝$(C_RESET)\n"
	@echo -e "$(C_CYAN)── Projeto ──────────────────────────────────$(C_RESET)"
	@printf "  ${C_GREEN}%-18s${C_RESET}  %s\n" "make deps"          "Prepara JDK 17 e Maven Wrapper"
	@printf "  ${C_GREEN}%-18s${C_RESET}  %s\n" "make compile"       "Compila o projeto com JDK 17"
	@printf "  ${C_GREEN}%-18s${C_RESET}  %s\n" "make run"           "Executa a aplicação Spring Boot (http://localhost:8080)"
	@printf "  ${C_GREEN}%-18s${C_RESET}  %s\n" "make clean"         "Remove artefatos de build"
	@printf "  ${C_GREEN}%-18s${C_RESET}  %s\n" "make all"           "infra-up + deps + compile (idempotente)"
	@echo ""
	@echo -e "$(C_CYAN)── Infraestrutura ───────────────────────────────$(C_RESET)"
	@printf "  ${C_GREEN}%-18s${C_RESET}  %s\n" "make infra-up"      "Sobe Elasticsearch + Kibana e aguarda health check"
	@printf "  ${C_GREEN}%-18s${C_RESET}  %s\n" "make infra-down"    "Para os containers graciosamente"
	@echo ""
	@echo -e "$(C_CYAN)── Java ─────────────────────────────────────$(C_RESET)"
	@printf "  ${C_GREEN}%-18s${C_RESET}  %s\n" "make java-install"  "Instala JDK 17 em ~/java com symlink ~/java/current"
	@printf "  ${C_GREEN}%-18s${C_RESET}  %s\n" "make use-java-17"   "Aponta ~/java/current → JDK 17 (para este projeto)"
	@printf "  ${C_GREEN}%-18s${C_RESET}  %s\n" "make use-java-21"   "Aponta ~/java/current → JDK 21 (Temurin)"
	@printf "  ${C_GREEN}%-18s${C_RESET}  %s\n" "make java-version"  "Exibe versão Java ativa (via symlink)"
	@echo ""
	@echo -e "$(C_CYAN)── Documentação ─────────────────────────────$(C_RESET)"
	@printf "  ${C_GREEN}%-18s${C_RESET}  %s\n" "make docs"          "Gera doc/architecture.png (Graphviz) + HTML da API"
	@printf "  ${C_GREEN}%-18s${C_RESET}  %s\n" "make test-api"      "Testa endpoints via curl (requer app rodando)"
	@printf "  ${C_GREEN}%-18s${C_RESET}  %s\n" "make postman-import" "Exibe URL para importar collection no Postman"
	@echo ""

# ─── Infraestrutura Docker ─────────────────────────────────────
infra-up:  ## Inicia e valida os containers do Elasticsearch
	@echo -e "$(C_BLUE)*** Iniciando infraestrutura via docker-compose... ***$(C_RESET)"
	@$(MAKE) -s -C $(DOCKER_DIR) up
	@echo -e "$(C_YELLOW)> Aguardando Elasticsearch ficar online...$(C_RESET)"
	@sleep 5
	@$(MAKE) -s -C $(DOCKER_DIR) health || (echo -e "$(C_YELLOW)> Ainda aguardando...$(C_RESET)" && sleep 15 && $(MAKE) -s -C $(DOCKER_DIR) health)
	@echo -e "$(C_GREEN)*** Infraestrutura Docker pronta! ***$(C_RESET)"

infra-down:  ## Para os containers do Elasticsearch graciosamente
	@echo -e "$(C_BLUE)*** Parando infraestrutura... ***$(C_RESET)"
	@$(MAKE) -s -C $(DOCKER_DIR) down
	@echo -e "$(C_GREEN)*** Infraestrutura Docker parada. ***$(C_RESET)"

# ─── Atalho principal ──────────────────────────────────────────
all: infra-up java-install deps compile  ## Instala JDK 17, sobe banco, instala deps e compila
	@echo ""
	@echo -e "$(C_GREEN)╔═══════════════════════════════════════════════════════╗$(C_RESET)"
	@echo -e "$(C_GREEN)║  ✓ Projeto compilado!                                 ║$(C_RESET)"
	@echo -e "$(C_GREEN)║  Execute 'make run' para iniciar a aplicação          ║$(C_RESET)"
	@echo -e "$(C_GREEN)║  Acesse: http://localhost:8080                        ║$(C_RESET)"
	@echo -e "$(C_GREEN)╚═══════════════════════════════════════════════════════╝$(C_RESET)"

# ─── JDK 17 — Instalação com symlink ──────────────────────────
java-install: java.ready
	@echo -e "$(C_GREEN)*** JDK 17 pronto em ~/java/current ***$(C_RESET)"

java.ready: $(JAVA_CURRENT)/bin/java
	@touch java.ready

$(JAVA_CURRENT)/bin/java:
	@echo -e "$(C_YELLOW)> Iniciando configuração do JDK 17...$(C_RESET)"
	@if [ ! -f "$(JDK_TARBALL)" ]; then \
		echo -e "$(C_RED)[ERRO] Tarball não encontrado: $(JDK_TARBALL)$(C_RESET)"; \
		echo -e "$(C_DIM)  Coloque o arquivo em: $(DEPS_DIR)/$(C_RESET)"; \
		exit 1; \
	fi
	@if [ -d "$(JDK_DIR)" ]; then \
		echo -e "$(C_DIM)  - JDK 17 já extraído em $(JDK_DIR), ignorando.$(C_RESET)"; \
	else \
		echo -e "$(C_BLUE)  - Extraindo para ~/java/ ...$(C_RESET)"; \
		mkdir -p $(HOME)/java; \
		tar -xzf $(JDK_TARBALL) -C $(HOME)/java/; \
		echo -e "$(C_GREEN)    Extração concluída.$(C_RESET)"; \
	fi
	@echo -e "$(C_BLUE)  - Criando symlink: ~/java/current → $(JDK_DIR)$(C_RESET)"
	@ln -sfn $(JDK_DIR) $(JAVA_CURRENT)
	@echo -e "$(C_GREEN)    Symlink configurado.$(C_RESET)"
	@echo -e "$(C_DIM)  - Versão ativa:$(C_RESET)"
	@"$(JAVA_CURRENT)/bin/java" -version 2>&1 | sed 's/^/    /'
	@echo -e "$(C_DIM)  - Para trocar de versão: make use-java-17 | make use-java-21$(C_RESET)"

# ─── Troca de versão Java ──────────────────────────────────────
use-java-17:  ## Aponta ~/java/current para o JDK 17
	@if [ ! -d "$(JDK_DIR)" ]; then \
		echo -e "$(C_YELLOW)JDK 17 não encontrado. Execute: make java-install$(C_RESET)"; \
		exit 1; \
	fi
	@ln -sfn $(JDK_DIR) $(JAVA_CURRENT)
	@echo -e "$(C_GREEN)✓ Agora usando JDK 17:$(C_RESET)"
	@"$(JAVA_CURRENT)/bin/java" -version 2>&1

use-java-21:  ## Aponta ~/java/current para o JDK 21 (Temurin)
	@if [ ! -d "$(JDK_21_DIR)" ]; then \
		echo -e "$(C_RED)[ERRO] JDK 21 não encontrado em $(JDK_21_DIR)$(C_RESET)"; \
		exit 1; \
	fi
	@ln -sfn $(JDK_21_DIR) $(JAVA_CURRENT)
	@echo -e "$(C_GREEN)✓ Agora usando JDK 21:$(C_RESET)"
	@"$(JAVA_CURRENT)/bin/java" -version 2>&1

java-version:  ## Exibe versão Java ativa pelo symlink
	@echo -e "$(C_BLUE)Symlink: $(JAVA_CURRENT) → $(shell readlink $(JAVA_CURRENT) 2>/dev/null || echo 'não configurado')$(C_RESET)"
	@"$(JAVA_CURRENT)/bin/java" -version 2>&1 || echo -e "$(C_RED)Execute 'make java-install' primeiro$(C_RESET)"

# ─── Dependências Maven ────────────────────────────────────────
deps: java.ready mvnw.ready
	@echo -e "$(C_GREEN)*** Todas as dependências estão prontas. ***$(C_RESET)"

mvnw.ready: $(MVNW_JAR) $(MVNW_PROPS)
	@echo -e "$(C_GREEN)*** Maven Wrapper verificado/configurado. ***$(C_RESET)"

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
	@echo -e "$(C_GREEN)  Download concluído: $(MVNW_JAR)$(C_RESET)"

$(MVNW_PROPS):
	@echo "distributionUrl=$(MAVEN_DIST_URL)" > $@
	@echo "wrapperUrl=$(MVNW_JAR_URL)" >> $@

# ─── Compilação ───────────────────────────────────────────────
compile: deps
	@echo -e "$(C_BLUE)*** Compilando com JDK 17... ***$(C_RESET)"
	@$(MVNW_SCRIPT) compile -q
	@echo -e "$(C_GREEN)*** Compilação concluída. ***$(C_RESET)"

# ─── Execução ─────────────────────────────────────────────────
run: infra-up compile  ## Inicia a aplicação e abre no navegador automaticamente
	@echo -e "$(C_MAGENTA)"
	@echo "  ╔═══════════════════════════════════════╗"
	@echo "  ║   WikiSearch iniciando...             ║"
	@echo "  ║   http://localhost:8080/v1/           ║"
	@echo "  ║   API: http://localhost:8080/v1/search║"
	@echo "  ║   CTRL+C para parar                   ║"
	@echo "  ╚═══════════════════════════════════════╝"
	@echo -e "$(C_RESET)"
	@echo -e "$(C_BLUE)> Aguardando Spring Boot iniciar para abrir o navegador...$(C_RESET)"
	@( \
		while ! curl -s http://localhost:8080/v1/ > /dev/null; do \
			sleep 2; \
		done; \
		echo -e "$(C_GREEN)*** Aplicação pronta! Abrindo navegador... ***$(C_RESET)"; \
		if command -v xdg-open > /dev/null; then xdg-open http://localhost:8080/v1/; \
		elif command -v open > /dev/null; then open http://localhost:8080/v1/; \
		elif command -v start > /dev/null; then start http://localhost:8080/v1/; \
		else python3 -m webbrowser "http://localhost:8080/v1/"; fi \
	) &
	@$(MVNW_SCRIPT) spring-boot:run

# ─── Limpeza ──────────────────────────────────────────────────
clean:  ## Remove artefatos de build
	@echo -e "$(C_YELLOW)*** Limpando artefatos... ***$(C_RESET)"
	@$(MVNW_SCRIPT) clean -q
	@rm -f java.ready
	@echo -e "$(C_GREEN)*** Limpeza concluída. ***$(C_RESET)"

# ─── Documentação ─────────────────────────────────────────────
docs:  ## Gera diagrama de arquitetura PNG e HTML da API
	@echo -e "$(C_BLUE)*** Gerando documentação... ***$(C_RESET)"
	@mkdir -p doc
	@# Diagrama de arquitetura via Graphviz
	@if command -v dot &>/dev/null; then \
		dot -Tpng doc/api.dot -o doc/architecture.png && \
		echo -e "$(C_GREEN)  ✓ doc/architecture.png gerado$(C_RESET)"; \
	else \
		echo -e "$(C_YELLOW)  ⚠ Graphviz não encontrado. Instale com: sudo apt install graphviz$(C_RESET)"; \
	fi
	@# HTML interativo da API via Redocly (Node.js)
	@if command -v npx &>/dev/null; then \
		npx --yes @redocly/cli@latest build-docs src/main/resources/api.yml \
			--output doc/api.html --title "WikiSearch API" 2>/dev/null && \
		echo -e "$(C_GREEN)  ✓ doc/api.html gerado$(C_RESET)"; \
	else \
		echo -e "$(C_YELLOW)  ⚠ npx não encontrado. A documentação HTML não foi gerada.$(C_RESET)"; \
	fi
	@echo -e "$(C_GREEN)*** Documentação gerada em doc/ ***$(C_RESET)"
# ─── Dados ────────────────────────────────────────────────────
seed:  ## Popula o Elasticsearch com o dataset Wikipedia
	@echo -e "$(C_BLUE)*** Iniciando carga de dados no Elasticsearch... ***$(C_RESET)"
	@if [ -d "../datasets" ] && [ -f "../datasets/importWiki.sh" ]; then \
		cd ../datasets && chmod +x importWiki.sh && ./importWiki.sh; \
	else \
		echo -e "$(C_RED)[ERRO] Diretório datasets ou importWiki.sh não encontrado em ../datasets$(C_RESET)"; \
		exit 1; \
	fi
	@echo -e "$(C_GREEN)*** Carga de dados concluída. ***$(C_RESET)"


# ─── Testes via curl ──────────────────────────────────────────
test-api:  ## Testa os endpoints da API (requer 'make run' ativo)
	@echo -e "\n$(C_BOLD)=== Testando WikiSearch API ===$(C_RESET)\n"
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
	@echo -e "$(C_CYAN)[2] GET /v1/search — com cabeçalhos de paginação$(C_RESET)"
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

postman-import:  ## Exibe instruções para importar a API no Postman
	@echo -e "\n$(C_BOLD)=== Importando WikiSearch API no Postman ===$(C_RESET)\n"
	@echo -e "$(C_BLUE)Opção 1 — Swagger UI (requer app rodando):$(C_RESET)"
	@echo "  http://localhost:8080/v1/swagger-ui.html"
	@echo ""
	@echo -e "$(C_BLUE)Opção 2 — Importar api.yml diretamente no Postman:$(C_RESET)"
	@echo "  1. Abra o Postman → Import → File"
	@echo "  2. Selecione: $(PROJECT_DIR)/src/main/resources/api.yml"
	@echo "  3. Configure a variável base_url = http://localhost:8080/v1"
	@echo ""
	@echo -e "$(C_BLUE)Opção 3 — Visualizar online:$(C_RESET)"
	@echo "  https://editor.swagger.io/ → File → Import URL"
	@echo ""
	@echo -e "$(C_BLUE)Opção 4 — Editor local (Redocly):$(C_RESET)"
	@echo "  npx @redocly/cli preview-docs src/main/resources/api.yml"
	@echo ""
