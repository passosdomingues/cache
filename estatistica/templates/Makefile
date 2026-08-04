# ==============================================================================
# Makefile - Template para Aulas de Estatística em R
# ==============================================================================

RSCRIPT := $(shell if [ -f ../env/bin/Rscript ]; then echo "../env/bin/Rscript"; else echo "Rscript"; fi)

.PHONY: help check-env run clean

help: ## Exibe os comandos disponíveis nesta aula
	@echo "======================================================================"
	@echo " Comandos disponíveis:"
	@echo "======================================================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo "======================================================================"

check-env: ## Verifica a instalação do R
	@which $(RSCRIPT) || $(RSCRIPT) --version

run: ## Executa o script principal (src/main.R)
	@$(RSCRIPT) src/main.R

clean: ## Limpa dados e relatórios gerados
	rm -rf data/*.csv data/*.RData reports/*.pdf reports/*.html
	@echo "Limpeza concluída."
