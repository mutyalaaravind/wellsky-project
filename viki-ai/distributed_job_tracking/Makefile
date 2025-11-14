.PHONY: help build run stop clean test lint format install dev logs

# Default target
help:
	@echo "Available commands:"
	@echo "  build    - Build the Docker image"
	@echo "  run      - Run the service with docker-compose"
	@echo "  stop     - Stop the service"
	@echo "  clean    - Clean up containers and volumes"
	@echo "  test     - Run tests"
	@echo "  lint     - Run linting"
	@echo "  format   - Format code"
	@echo "  install  - Install dependencies"
	@echo "  dev      - Run in development mode"
	@echo "  logs     - Show logs"

# Build the Docker image
build:
	docker-compose build

# Run the service
run:
	docker-compose up -d

# Stop the service
stop:
	docker-compose down

# Clean up containers and volumes
clean:
	docker-compose down -v
	docker system prune -f

# Run tests
test:
	cd src && uv run pytest

# Run linting
lint:
	cd src && uv run ruff check .

# Format code
format:
	cd src && uv run ruff format .

# Install dependencies
install:
	uv sync

# Run in development mode
dev:
	docker-compose up

# Show logs
logs:
	docker-compose logs -f distributed-job-tracking-api

# Generate lock file
lock:
	uv lock

# Update dependencies
update:
	uv sync --upgrade
