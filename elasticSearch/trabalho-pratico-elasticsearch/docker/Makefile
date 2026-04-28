# ==============================================================================
# MAKEFILE: ELASTICSEARCH & KIBANA (AUTENTICADO)
# ==============================================================================

# Variáveis de Conexão
USER=elastic
PASS=user123
ES_URL=http://localhost:9200
KIBANA_URL=http://localhost:5601

# Flag do Curl para ignorar mensagens de progresso e incluir usuário/senha
CURL_OPTS=-s -u $(USER):$(PASS)

.PHONY: help up down clean nodes health indices-v

help: ## Lista todos os comandos disponíveis
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# --- COMANDOS DE AMBIENTE ---

up: ## Sobe o ambiente (Docker Compose)
	docker compose up -d

down: ## Para o ambiente sem apagar dados
	docker compose down

clean: ## Limpeza total (Containers, Volumes e Imagens)
	chmod +x ./limpar_docker.sh && ./limpar_docker.sh

# --- COMANDOS ELASTICSEARCH (_CAT API) ---

nodes: ## Lista nós ativos (formato curto)
	curl $(CURL_OPTS) -X GET "$(ES_URL)/_cat/nodes"

nodes-v: ## Lista nós ativos (formato detalhado com cabeçalhos)
	curl $(CURL_OPTS) -X GET "$(ES_URL)/_cat/nodes?v"

health: ## Verifica saúde do cluster (status, nodes, shards)
	curl $(CURL_OPTS) -X GET "$(ES_URL)/_cat/health?v"

indices: ## Lista todos os índices e o estado de saúde de cada um
	curl $(CURL_OPTS) -X GET "$(ES_URL)/_cat/indices?v"

shards: ## Verifica a distribuição de shards entre os nós
	curl $(CURL_OPTS) -X GET "$(ES_URL)/_cat/shards?v"

# --- INTERAÇÃO COM KIBANA ---

kibana-status: ## Checa se o Kibana já terminou de subir
	@echo "Verificando status do Kibana..."
	curl -I -u $(USER):$(PASS) $(KIBANA_URL)/api/status

links: ## Exibe os links úteis de acesso
	@echo "---------------------------------------------------"
	@echo "Kibana Home:    $(KIBANA_URL)"
	@echo "Dev Tools:      $(KIBANA_URL)/app/dev_tools#/console"
	@echo "Elastic API:    $(ES_URL)"
	@echo "Credenciais:    $(USER) / $(PASS)"
	@echo "---------------------------------------------------"

# --- UTILITÁRIOS ---

logs: ## Acompanha os logs dos containers
	docker compose logs -f
