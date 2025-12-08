# Blue Velvet Music Store Makefile

.PHONY: all build up down logs clean help

# Default target
all: build up

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
	docker-compose down -v
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
