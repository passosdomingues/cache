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

# Stop the environment
.PHONY: down
down:
	@echo "Stopping Docker environment..."
	-docker rm -f $(BACKEND_CONTAINER) $(FRONTEND_CONTAINER)

# View logs
.PHONY: logs
logs:
	docker logs -f $(BACKEND_CONTAINER)

# Clean up resources
.PHONY: clean
clean: down
	@echo "Cleaning up..."
	-docker rmi $(BACKEND_IMAGE) $(FRONTEND_IMAGE)
