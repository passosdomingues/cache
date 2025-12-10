# @author Rafael Passos Domingues
# @lastUpdate 2025 December 10 (Wed)
# @brief Makefile for orchestration of Docker Compose environments.
# @us US-0000 Project Configuration - Granularity: Build System

# Default target
.PHONY: all
all: build up

# Build the applications
.PHONY: build
build:
	@echo "Building Backend and Frontend via Docker Compose..."
	docker-compose build

# Start the environment
.PHONY: up
up:
	@echo "Starting Docker Compose..."
	docker-compose up -d

# Stop the environment
.PHONY: down
down:
	@echo "Stopping Docker Compose..."
	docker-compose down

# View logs
.PHONY: logs
logs:
	docker-compose logs -f

# Clean up
.PHONY: clean
clean:
	@echo "Cleaning up..."
	docker-compose down --rmi all --volumes --remove-orphans
	./gradlew clean

# Help command
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make all    - Build and start the application (default)"
	@echo "  make build  - Build Docker images"
	@echo "  make up     - Start containers in detached mode"
	@echo "  make down   - Stop containers"
	@echo "  make logs   - Follow container logs"
	@echo "  make clean  - Stop containers, remove volumes, and clean Gradle"
