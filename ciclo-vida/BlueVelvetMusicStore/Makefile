# @author Rafael Passos Domingues
# @lastUpdate 2025 December 10 (Wed)
# @brief Makefile for building and running the project using Docker Compose.

# Variables
COMPOSE_FILE=docker-compose.yml
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8080

# Default target - Complete orchestration
.PHONY: all
all: clean-containers build up wait-backend open-browser
	@echo ""
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║  Blue Velvet Music Store - Ready!                          ║"
	@echo "╠════════════════════════════════════════════════════════════╣"
	@echo "║  Frontend: $(FRONTEND_URL)                           ║"
	@echo "║  Backend:  $(BACKEND_URL)                           ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""

# Show available commands
.PHONY: help
help:
	@echo "Blue Velvet Music Store - Docker Compose Management"
	@echo "===================================================="
	@echo ""
	@echo "Available commands:"
	@echo "  make all          - Complete setup: clean, build, start, and open browser"
	@echo "  make build        - Build Docker images for backend and frontend"
	@echo "  make up           - Start the Docker containers"
	@echo "  make stop         - Stop containers (keeps them for restart)"
	@echo "  make down         - Stop and remove containers"
	@echo "  make restart      - Restart the environment"
	@echo "  make status       - Show container status"
	@echo "  make logs         - View backend logs (live)"
	@echo "  make logs-frontend - View frontend logs (live)"
	@echo "  make logs-all     - View last 20 lines of both logs"
	@echo "  make open-browser - Open the application in browser"
	@echo "  make clean        - Remove containers and images"
	@echo "  make deep-clean   - Remove everything (containers, images, network, volume)"
	@echo ""
	@echo "Quick tips:"
	@echo "  - Use 'make all' for complete setup and auto-open browser"
	@echo "  - Use 'make stop' to free ports for local development"
	@echo "  - Use 'make restart' to apply configuration changes"
	@echo "  - Use 'make deep-clean' for a complete reset"
	@echo ""

# Clean existing containers (avoid port conflicts)
.PHONY: clean-containers
clean-containers:
	@echo "Cleaning existing containers..."
	-docker-compose -f $(COMPOSE_FILE) down 2>/dev/null
	@echo "Containers cleaned!"

# Build the project
.PHONY: build
build:
	@echo "Building images with Docker Compose..."
	docker-compose -f $(COMPOSE_FILE) build
	@echo "Build complete!"

# Start the environment
.PHONY: up
up:
	@echo "Starting services with Docker Compose..."
	docker-compose -f $(COMPOSE_FILE) up -d
	@echo "Services started!"

# Wait for backend to be healthy
.PHONY: wait-backend
wait-backend:
	@echo "Waiting for backend to be healthy..."
	@timeout=120; \
	elapsed=0; \
	while [ $$elapsed -lt $$timeout ]; do \
		if docker inspect bluevelvetmusicstore_backend 2>/dev/null | grep -q '"Status": "healthy"'; then \
			echo "Backend is healthy!"; \
			exit 0; \
		fi; \
		echo "Waiting... ($$elapsed/$$timeout seconds)"; \
		sleep 5; \
		elapsed=$$((elapsed + 5)); \
	done; \
	echo "Timeout waiting for backend to be healthy"; \
	exit 1

# Open browser to the application
.PHONY: open-browser
open-browser:
	@echo "Opening browser to $(FRONTEND_URL)..."
	@if command -v xdg-open > /dev/null; then \
		xdg-open $(FRONTEND_URL) 2>/dev/null & \
	elif command -v gnome-open > /dev/null; then \
		gnome-open $(FRONTEND_URL) 2>/dev/null & \
	elif command -v firefox > /dev/null; then \
		firefox $(FRONTEND_URL) 2>/dev/null & \
	elif command -v google-chrome > /dev/null; then \
		google-chrome $(FRONTEND_URL) 2>/dev/null & \
	else \
		echo "Could not detect browser. Please open $(FRONTEND_URL) manually."; \
	fi

# Stop containers (without removing)
.PHONY: stop
stop:
	@echo "Stopping Docker containers..."
	docker-compose -f $(COMPOSE_FILE) stop

# Stop and remove containers
.PHONY: down
down:
	@echo "Stopping and removing Docker containers..."
	docker-compose -f $(COMPOSE_FILE) down

# Restart the environment
.PHONY: restart
restart: stop up wait-backend
	@echo "Environment restarted!"

# Show container status
.PHONY: status
status:
	@echo "Container Status:"
	@docker-compose -f $(COMPOSE_FILE) ps

# View backend logs
.PHONY: logs
logs:
	docker-compose -f $(COMPOSE_FILE) logs -f backend

# View frontend logs
.PHONY: logs-frontend
logs-frontend:
	docker-compose -f $(COMPOSE_FILE) logs -f frontend

# View both logs
.PHONY: logs-all
logs-all:
	@echo "=== Backend Logs ==="
	@docker-compose -f $(COMPOSE_FILE) logs --tail=20 backend
	@echo ""
	@echo "=== Frontend Logs ==="
	@docker-compose -f $(COMPOSE_FILE) logs --tail=20 frontend

# Clean up images
.PHONY: clean
clean: down
	@echo "Cleaning up images..."
	docker-compose -f $(COMPOSE_FILE) down --rmi all

# Deep clean (remove everything including network and volume)
.PHONY: deep-clean
deep-clean:
	@echo "Deep cleaning (removing everything)..."
	docker-compose -f $(COMPOSE_FILE) down --rmi all --volumes --remove-orphans
	@echo "Deep clean complete!"
