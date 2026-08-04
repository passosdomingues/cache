# ==============================================================================
# Makefile - Aula 01: Introdução ao R e Técnicas de Amostragem
# ==============================================================================

# Detectar executável do Rscript (env local compartilhado -> PATH)
RSCRIPT := $(shell if [ -f ../env/bin/Rscript ]; then echo "../env/bin/Rscript"; else echo "Rscript"; fi)

.PHONY: help check-env hello basico estatistica amostragem banco run-all clean

help: ## Exibe a lista de comandos da Aula 01
	@echo "======================================================================"
	@echo " Aula 01: Introdução e Amostragem - Comandos Makefile"
	@echo "======================================================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo "======================================================================"

check-env: ## Verifica a instalação do R
	@echo "Verificando Rscript..."
	@which $(RSCRIPT) || $(RSCRIPT) --version

hello: ## Executa o script Hello World
	@$(RSCRIPT) src/00_hello_world.R

basico: ## Operadores aritméticos, lógicos e funções
	@$(RSCRIPT) src/01_operacoes_basicas.R

estatistica: ## Medidas descritivas (média, mediana, sd, var)
	@$(RSCRIPT) src/02_estatistica_descritiva.R

amostragem: ## Técnicas de amostragem (Acaso, Estratificada, Sistemática)
	@$(RSCRIPT) src/03_rotina_amostragem.R

banco: ## Criação e salvamento do banco de dados (fármacos)
	@$(RSCRIPT) src/04_banco_de_dados.R

run-all: hello basico estatistica amostragem banco ## Executa todos os scripts da Aula 01

clean: ## Limpa arquivos temporários da Aula 01
	rm -rf data/*.csv data/*.RData reports/*.pdf reports/*.html
	@echo "Arquivos temporários da Aula 01 limpos."
