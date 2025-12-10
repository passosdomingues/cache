# @author Rafael Passos Domingues
# @lastUpdate 2025 December 10 (Wed)
# @brief Makefile for building and running the project using native Docker commands.

# Variables
NETWORK_NAME=bluevelvetmusicstore_app-network
VOLUME_NAME=bluevelvetmusicstore_uploads_data
BACKEND_IMAGE=bluevelvetmusicstore_backend
FRONTEND_IMAGE=bluevelvetmusicstore_frontend
BACKEND_CONTAINER=bluevelvetmusicstore_backend_1
FRONTEND_CONTAINER=bluevelvetmusicstore_frontend_1

# Default target
.PHONY: all
all: build up

# Show available commands
.PHONY: help
help:
	@echo "Blue Velvet Music Store - Docker Management"
	@echo "==========================================="
	@echo ""
	@echo "Available commands:"
	@echo "  make all          - Build and start the application (default)"
	@echo "  make build        - Build Docker images for backend and frontend"
	@echo "  make up           - Start the Docker containers"
	@echo "  make stop         - Stop containers (keeps them for restart)"
	@echo "  make down         - Stop and remove containers"
	@echo "  make restart      - Stop and restart the environment"
	@echo "  make status       - Show container status"
	@echo "  make logs         - View backend logs (live)"
	@echo "  make logs-frontend - View frontend logs (live)"
	@echo "  make logs-all     - View last 20 lines of both logs"
	@echo "  make clean        - Remove containers and images"
	@echo "  make deep-clean   - Remove everything (containers, images, network, volume)"
	@echo ""
	@echo "Quick tips:"
	@echo "  - Use 'make stop' to free ports for local development"
	@echo "  - Use 'make restart' to apply configuration changes"
	@echo "  - Use 'make deep-clean' for a complete reset"
	@echo ""

# Build the project
.PHONY: build
build:
	@echo "Building Backend..."
	docker build -t $(BACKEND_IMAGE) .
	@echo "Building Frontend..."
	docker build -t $(FRONTEND_IMAGE) ./blue-velvet-music-store-frontend

# Start the environment
.PHONY: up
up:
	@echo "Starting Docker environment..."
	# Create network if it doesn't exist
	docker network inspect $(NETWORK_NAME) >/dev/null 2>&1 || docker network create $(NETWORK_NAME)
	# Create volume if it doesn't exist
	docker volume inspect $(VOLUME_NAME) >/dev/null 2>&1 || docker volume create $(VOLUME_NAME)
	
	# Stop and remove existing containers if any
	-docker rm -f $(BACKEND_CONTAINER) $(FRONTEND_CONTAINER) 2>/dev/null
	
	# Run Backend
	docker run -d \
		--name $(BACKEND_CONTAINER) \
		--network $(NETWORK_NAME) \
		-p 8080:8080 \
		-e SPRING_PROFILES_ACTIVE=dev \
		-v $(VOLUME_NAME):/app/uploads \
		$(BACKEND_IMAGE)
		
	# Run Frontend
	docker run -d \
		--name $(FRONTEND_CONTAINER) \
		--network $(NETWORK_NAME) \
		-p 3000:80 \
		$(FRONTEND_IMAGE)
	
	@echo "Application started!"
	@echo "Backend: http://localhost:8080"
	@echo "Frontend: http://localhost:3000"

# Stop containers (without removing)
.PHONY: stop
stop:
	@echo "Stopping Docker containers..."
	-docker stop $(BACKEND_CONTAINER) $(FRONTEND_CONTAINER)

# Stop and remove containers
.PHONY: down
down:
	@echo "Stopping and removing Docker containers..."
	-docker rm -f $(BACKEND_CONTAINER) $(FRONTEND_CONTAINER)

# Restart the environment
.PHONY: restart
restart: stop up
	@echo "Environment restarted!"

# Show container status
.PHONY: status
status:
	@echo "Container Status:"
	@docker ps -a | grep bluevelvetmusicstore || echo "No containers found"

# View backend logs
.PHONY: logs
logs:
	docker logs -f $(BACKEND_CONTAINER)

# View frontend logs
.PHONY: logs-frontend
logs-frontend:
	docker logs -f $(FRONTEND_CONTAINER)

# View both logs
.PHONY: logs-all
logs-all:
	@echo "=== Backend Logs ==="
	@docker logs $(BACKEND_CONTAINER) 2>&1 | tail -n 20
	@echo ""
	@echo "=== Frontend Logs ==="
	@docker logs $(FRONTEND_CONTAINER) 2>&1 | tail -n 20

# Clean up images
.PHONY: clean
clean: down
	@echo "Cleaning up images..."
	-docker rmi $(BACKEND_IMAGE) $(FRONTEND_IMAGE)

# Deep clean (remove everything including network and volume)
.PHONY: deep-clean
deep-clean: clean
	@echo "Deep cleaning (removing network and volume)..."
	-docker network rm $(NETWORK_NAME)
	-docker volume rm $(VOLUME_NAME)
	@echo "Deep clean complete!"
