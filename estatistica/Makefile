# ==============================================================================
# Makefile Principal - Disciplina de Estatística em R
# ==============================================================================

# Executáveis do R (prioridade: sistema via APT — integração nativa com Cinnamon)
R_BIN   := $(shell which R 2>/dev/null || echo "./env/bin/R")
RSCRIPT := $(shell which Rscript 2>/dev/null || echo "./env/bin/Rscript")

.PHONY: help check-env gui rcmdr console r aula-01 run-all clean nova-aula graficos

help: ## Exibe o menu principal de comandos do repositório
	@echo "======================================================================"
	@echo " Workstation de Estatística em R - Repositório Principal"
	@echo "======================================================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo "======================================================================"

gui: ## Abre o RCommander em background — libera o terminal imediatamente
	@bash scripts/launch_rcmdr.sh

rcmdr: gui ## Atalho para 'make gui'

console: ## Abre o Console Interativo do R
	@$(R_BIN)

r: console ## Atalho para 'make console'

check-env: ## Verifica se a instalação do R e pacotes está funcionando
	@echo "Verificando ambiente R..."
	@$(RSCRIPT) -e 'cat("Versão do R:", R.version.string, "\nStatus: OK\n")'

aula-01: ## Executa todos os scripts da Aula 01
	@echo "=== Executando Aula 01 ==="
	@$(MAKE) -C aula_01_introducao_e_amostragem run-all

graficos: ## Geração de gráficos da Aula 01 (Histograma, Boxplot, ggplot2)
	@$(MAKE) -C aula_01_introducao_e_amostragem graficos

run-all: ## Executa todas as aulas existentes em sequência
	@for d in aula_*; do \
		if [ -d "$$d" ]; then \
			echo "========================================="; \
			echo " Rodando: $$d"; \
			echo "========================================="; \
			$(MAKE) -C "$$d" run-all || $(MAKE) -C "$$d" run || true; \
		fi; \
	done

nova-aula: ## Cria uma nova pasta de aula (Uso: make nova-aula N=02 NAME=probabilidade)
	@if [ -z "$(N)" ] || [ -z "$(NAME)" ]; then \
		echo "Erro: Forneça N e NAME. Exemplo: make nova-aula N=02 NAME=probabilidade"; \
		exit 1; \
	fi
	@TARGET="aula_$(N)_$(NAME)"; \
	if [ -d "$$TARGET" ]; then \
		echo "Erro: A pasta $$TARGET já existe!"; \
		exit 1; \
	fi; \
	cp -r templates "$$TARGET"; \
	echo "Pasta $$TARGET criada com sucesso a partir dos templates!"; \
	echo "Acesse 'cd $$TARGET' e execute 'make help' ou 'make run'."

clean: ## Limpa dados e relatórios de todas as aulas
	@for d in aula_*; do \
		if [ -d "$$d" ]; then \
			$(MAKE) -C "$$d" clean || true; \
		fi; \
	done
