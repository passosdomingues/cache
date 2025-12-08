# Blue Velvet Music Store Makefile
# Orchestration for Docker Compose (Legacy Compatibility)

# Ensure legacy builder is used to prevent 'ContainerConfig' errors in docker-compose 1.29.x
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0

.PHONY: all build up run down logs clean help

# Default target
all: clean build up

# Run alias (user convenience)
run: up

# Build the applications
build:
	@echo "Building Backend..."
	./gradlew clean bootJar
	@echo "Building Frontend Docker Image (and Backend)..."
	docker-compose build

# Start the environment
up:
	@echo "Starting Docker Compose..."
	docker-compose up -d

# Stop the environment
down:
	@echo "Stopping Docker Compose..."
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Clean up
clean:
	@echo "Cleaning up..."
	docker-compose down --rmi all --volumes --remove-orphans
	./gradlew clean

# Help
help:
	@echo "Available commands:"
	@echo "  make all    - Build and start the application (default)"
	@echo "  make build  - Build artifacts and Docker images"
	@echo "  make up     - Start containers in detached mode"
	@echo "  make down   - Stop containers"
	@echo "  make logs   - Follow container logs"
	@echo "  make clean  - Stop containers, remove volumes, and clean Gradle"
