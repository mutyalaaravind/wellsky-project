.PHONY: init install sync clean test run help

# Initialize the project - install dependencies and set up environment
init:
	@echo "Initializing Python project with uv..."
	uv sync
	@echo "Project initialized successfully!"

# Alias for init
install: init

# Sync dependencies (same as init but more explicit name)
sync:
	@echo "Syncing dependencies..."
	uv sync

# Clean up build artifacts and cache
clean:
	@echo "Cleaning up..."
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf *.egg-info/
	rm -rf build/
	rm -rf dist/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

# Run tests (if you have any)
test:
	@echo "Running tests..."
	uv run pytest

# Run the main application
run:
	@echo "Running application..."
	uv run python main.py

# Docker commands
docker-build:
	@echo "Building Docker image..."
	docker build -t demo-mcp-server .

docker-run:
	@echo "Running Docker container..."
	docker run --rm -it demo-mcp-server

docker-shell:
	@echo "Opening shell in Docker container..."
	docker run --rm -it demo-mcp-server /bin/bash

# Docker Compose commands
compose-up:
	@echo "Starting services with Docker Compose..."
	docker-compose up -d

compose-down:
	@echo "Stopping services with Docker Compose..."
	docker-compose down

compose-build:
	@echo "Building services with Docker Compose..."
	docker-compose build

compose-logs:
	@echo "Showing logs from Docker Compose services..."
	docker-compose logs -f

compose-restart:
	@echo "Restarting services with Docker Compose..."
	docker-compose restart

# Show help
help:
	@echo "Available commands:"
	@echo "  init           - Initialize the project and install dependencies"
	@echo "  install        - Alias for init"
	@echo "  sync           - Sync dependencies"
	@echo "  clean          - Clean up build artifacts and cache"
	@echo "  test           - Run tests"
	@echo "  run            - Run the main application"
	@echo "  docker-build   - Build Docker image"
	@echo "  docker-run     - Run Docker container"
	@echo "  docker-shell   - Open shell in Docker container"
	@echo "  compose-up     - Start services with Docker Compose"
	@echo "  compose-down   - Stop services with Docker Compose"
	@echo "  compose-build  - Build services with Docker Compose"
	@echo "  compose-logs   - Show logs from Docker Compose services"
	@echo "  compose-restart- Restart services with Docker Compose"
	@echo "  help           - Show this help message"
