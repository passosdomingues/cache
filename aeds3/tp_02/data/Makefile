# ==============================================================================
# WRAPPER MAKEFILE - SETOR DE AUTOMAÇÃO E ANÁLISE (OPERAÇÃO DUPLA HÉLICE)
# ==============================================================================

# Definição de Cores Táticas para o Terminal
CYAN   := \033[36m
GREEN  := \033[32m
YELLOW := \033[33m
RED    := \033[31m
RESET  := \033[0m

# Caminhos do Virtual Environment e Interpretadores
VENV_DIR := venv
PYTHON   := $(VENV_DIR)/bin/python
PIP      := $(VENV_DIR)/bin/pip

# Declaração de alvos que não são arquivos físicos
.PHONY: all help setup run clean_venv create_gitignore

# Regra padrão: Se digitar apenas "make", exibe o painel de ajuda.
all: help

# Painel de Ajuda Tático
help:
	@echo "$(CYAN)======================================================================$(RESET)"
	@echo "$(CYAN)      TERMINAL DE CONTROLE - OPERACAO DUPLA HELICE (SETOR DATA)       $(RESET)"
	@echo "$(CYAN)======================================================================$(RESET)"
	@echo "Comandos de engajamento disponiveis:"
	@echo ""
	@echo "  $(YELLOW)make setup$(RESET)      : Prepara o ambiente de contencao (VENV) e camuflagem."
	@echo "  $(GREEN)make run$(RESET)        : Aciona o Orquestrador Bash para a bateria de testes."
	@echo "  $(RED)make clean_venv$(RESET) : Protocolo Terra Arrasada. Oblitera o ambiente virtual."
	@echo "  $(CYAN)make help$(RESET)       : Exibe este manual de operacoes."
	@echo "$(CYAN)======================================================================$(RESET)"

# Regra de Setup Estratégico (Depende da camuflagem e do touchfile)
setup: create_gitignore $(VENV_DIR)/touchfile
	@echo "$(GREEN)[OK] Ambiente isolado pronto e blindado para operacao.$(RESET)"

# Instalação Idempotente: O touchfile garante que o pip install rode apenas uma vez
$(VENV_DIR)/touchfile:
	@echo "$(CYAN)[SISTEMA] Iniciando protocolo de contencao (Construindo VENV)...$(RESET)"
	@python3 -m venv $(VENV_DIR)
	@echo "$(YELLOW)[SISTEMA] Instalando dependencias analiticas silenciosamente...$(RESET)"
	@$(PIP) install --upgrade pip --quiet
	@$(PIP) install numpy matplotlib seaborn --quiet
	@touch $(VENV_DIR)/touchfile

# Camuflagem: Injeta regras de ofuscação no .gitignore da raiz do projeto
create_gitignore:
	@echo "$(CYAN)[SISTEMA] Verificando protocolos de camuflagem (.gitignore)...$(RESET)"
	@if [ ! -f ../.gitignore ]; then \
		echo "Criando .gitignore na raiz da operacao..."; \
		echo "data/venv/" > ../.gitignore; \
		echo "data/resultados.csv" >> ../.gitignore; \
		echo "data/graficos/" >> ../.gitignore; \
		echo "data/__pycache__/" >> ../.gitignore; \
		echo "bla" >> ../.gitignore; \
		echo "codigo_base/base" >> ../.gitignore; \
		echo "codigo_base/*.o" >> ../.gitignore; \
		echo "$(GREEN)[OK] .gitignore forjado com sucesso.$(RESET)"; \
	else \
		grep -q "data/venv/" ../.gitignore || echo "data/venv/" >> ../.gitignore; \
		grep -q "bla" ../.gitignore || echo "bla" >> ../.gitignore; \
		echo "$(GREEN)[OK] .gitignore ativo e atualizado.$(RESET)"; \
	fi

# Aciona o Orquestrador Bash
run: setup
	@echo "$(CYAN)[SISTEMA] Transferindo controle para o Orquestrador Shell...$(RESET)"
	@bash testador.sh

# Protocolo de autodestruição do ambiente
clean_venv:
	@echo "$(RED)[ALERTA] Destruindo ambiente virtual e apagando rastros...$(RESET)"
	@rm -rf $(VENV_DIR)
	@echo "$(GREEN)[OK] Setor limpo.$(RESET)"
