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

# ─── Caminhos da sua estrutura ─────────────────────────────────
HOME          := $(shell echo $$HOME)
JDK_TARBALL   := $(HOME)/nemo/ElasticSearch/deps/jdk-17.0.12_linux-x64_bin.tar.gz
JDK_DIR       := $(HOME)/java/jdk-17.0.12
JAVA_CURRENT  := $(HOME)/java/current

# ─── Arquivos do Maven Wrapper ─────────────────────────────────
MVNW_SCRIPT   := ./mvnw
MVNW_DIR      := .mvn/wrapper
MVNW_JAR      := $(MVNW_DIR)/maven-wrapper.jar
MVNW_PROPS    := $(MVNW_DIR)/maven-wrapper.properties
MVNW_JAR_URL  := https://repo.maven.apache.org/maven2/org/apache/maven/wrapper/maven-wrapper/3.2.0/maven-wrapper-3.2.0.jar
MAVEN_DIST_URL := https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/3.9.6/apache-maven-3.9.6-bin.zip

# ─── Ambiente Java usado apenas pelos comandos do make ─────────
export JAVA_HOME := $(JAVA_CURRENT)
export PATH      := $(JAVA_HOME)/bin:$(PATH)

# ─── Ferramentas de download ───────────────────────────────────
WGET := $(shell which wget 2>/dev/null)
CURL := $(shell which curl 2>/dev/null)

# ═══════════════════════════════════════════════════════════════
# Alvos
# ═══════════════════════════════════════════════════════════════
.PHONY: help deps clean compile run all

help:  ## Mostra este menu de ajuda
	@echo -e "$(C_BOLD)Comandos disponiveis:$(C_RESET)"
	@echo ""
	@printf "  ${C_GREEN}%-12s${C_RESET}  %s\n" "make deps"     "Prepara JDK 17 e Maven Wrapper"
	@printf "  ${C_GREEN}%-12s${C_RESET}  %s\n" "make compile"  "Compila o projeto com JDK 17"
	@printf "  ${C_GREEN}%-12s${C_RESET}  %s\n" "make run"      "Executa a aplicacao Spring Boot"
	@printf "  ${C_GREEN}%-12s${C_RESET}  %s\n" "make clean"    "Remove artefatos de build"
	@printf "  ${C_GREEN}%-12s${C_RESET}  %s\n" "make all"      "deps + compile (idempotente)"
	@echo ""

all: deps compile  ## Instala dependencias e compila
	@echo ""
	@echo -e "$(C_GREEN)*** Projeto compilado. Execute 'make run' para iniciar a aplicacao. ***$(C_RESET)"

# ─── Dependencias ─────────────────────────────────────────────
deps: java.ready mvnw.ready
	@echo -e "$(C_GREEN)*** Todas as dependencias estao prontas. ***$(C_RESET)"

# ─── Java 17 ──────────────────────────────────────────────────
java.ready: $(JAVA_CURRENT)/bin/java
	@echo -e "$(C_GREEN)*** JDK 17 verificado/instalado. ***$(C_RESET)"

$(JAVA_CURRENT)/bin/java: $(JDK_TARBALL)
	@echo -e "$(C_YELLOW)> Iniciando configuração do JDK 17...$(C_RESET)"
	@if [ -d "$(JDK_DIR)" ]; then \
		echo -e "$(C_DIM)  - O diretorio $(JDK_DIR) ja existe, ignorando extracao.$(C_RESET)"; \
	else \
		echo -e "$(C_BLUE)  - Extraindo $(JDK_TARBALL) para ~/java/ ...$(C_RESET)"; \
		mkdir -p $(HOME)/java; \
		tar -xzf $(JDK_TARBALL) -C $(HOME)/java/; \
		echo -e "$(C_GREEN)    Extracao concluida.$(C_RESET)"; \
	fi
	@echo -e "$(C_BLUE)  - Criando (ou atualizando) symlink: ~/java/current -> $(JDK_DIR)$(C_RESET)"
	@ln -sfn $(JDK_DIR) $(JAVA_CURRENT)
	@echo -e "$(C_GREEN)    Symlink configurado.$(C_RESET)"
	@echo -e "$(C_DIM)  - Versao ativa do Java:$(C_RESET)"
	@"$(JAVA_CURRENT)/bin/java" -version 2>&1 | sed 's/^/    /'

# ─── Maven Wrapper ────────────────────────────────────────────
mvnw.ready: $(MVNW_JAR) $(MVNW_PROPS)
	@echo -e "$(C_GREEN)*** Maven Wrapper verificado/configurado. ***$(C_RESET)"

$(MVNW_DIR):
	@echo -e "$(C_BLUE)  - Criando diretorio .mvn/wrapper ...$(C_RESET)"
	@mkdir -p $@

$(MVNW_JAR): | $(MVNW_DIR)
	@echo -e "$(C_YELLOW)> Maven Wrapper JAR ausente. Iniciando download...$(C_RESET)"
	@if [ -n "$(WGET)" ]; then \
		echo -e "$(C_BLUE)  - Usando wget para baixar $(MVNW_JAR_URL)$(C_RESET)"; \
		$(WGET) -O $@ $(MVNW_JAR_URL); \
	elif [ -n "$(CURL)" ]; then \
		echo -e "$(C_BLUE)  - Usando curl para baixar $(MVNW_JAR_URL)$(C_RESET)"; \
		$(CURL) -L -o $@ $(MVNW_JAR_URL); \
	else \
		echo -e "$(C_RED)[ERRO] wget ou curl nao encontrados. Instale um deles.$(C_RESET)"; \
		exit 1; \
	fi
	@echo -e "$(C_GREEN)  - Download concluido: $(MVNW_JAR)$(C_RESET)"

$(MVNW_PROPS):
	@echo -e "$(C_YELLOW)> Arquivo maven-wrapper.properties ausente. Criando...$(C_RESET)"
	@echo -e "$(C_BLUE)  - Definindo distributionUrl: $(MAVEN_DIST_URL)$(C_RESET)"
	@echo "distributionUrl=$(MAVEN_DIST_URL)" > $@
	@echo "wrapperUrl=$(MVNW_JAR_URL)" >> $@
	@echo -e "$(C_GREEN)  - Arquivo criado: $(MVNW_PROPS)$(C_RESET)"

# ─── Compilação ───────────────────────────────────────────────
compile: deps
	@echo -e "$(C_BLUE)*** Compilando o projeto com JDK 17... ***$(C_RESET)"
	@echo -e "$(C_DIM)  (O Maven Wrapper baixara o Maven automaticamente se necessario.)$(C_RESET)"
	@$(MVNW_SCRIPT) compile
	@echo -e "$(C_GREEN)*** Compilacao concluida com sucesso. ***$(C_RESET)"

# ─── Execução ─────────────────────────────────────────────────
run: compile
	@echo -e "$(C_MAGENTA)*** Iniciando a aplicacao Spring Boot... ***$(C_RESET)"
	@$(MVNW_SCRIPT) spring-boot:run

# ─── Limpeza ──────────────────────────────────────────────────
clean:
	@echo -e "$(C_YELLOW)*** Limpando artefatos de build... ***$(C_RESET)"
	@$(MVNW_SCRIPT) clean
	@echo -e "$(C_GREEN)*** Limpeza concluida. ***$(C_RESET)"
