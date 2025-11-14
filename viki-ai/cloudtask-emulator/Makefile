.PHONY: install build run clean docker-build docker-run docker-compose logs lock sync test test-coverage install-test

# Package management
init:
	uv lock
	uv sync

install:
	uv pip install .

install-test:
	uv pip install .
	uv pip install ".[test]"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +

# Development
run:
	uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 30001

run-prod:
	uv run uvicorn src.main:app --host 0.0.0.0 --port 30001

# Testing
test: install-test
	uv run pytest tests/ -v

test-coverage: install-test
	uv run pytest tests/ -v --cov=src --cov-report=term-missing

# Docker commands
docker-build:
	docker build -t cloudtask-emulator .

# Docker Compose commands
up:
	docker-compose up --build

down:
	docker-compose down

logs:
	docker-compose logs -f

restart:
	docker-compose restart

# Development helpers
format:
	black .
	isort .

lint:
	flake8 .
	black . --check
	isort . --check

# Status and monitoring
status:
	curl -f http://localhost:30001/status || echo "Emulator not running"

clear-tasks:
	curl -X DELETE http://localhost:30001/tasks || echo "Emulator not running"

# Help command
help:
	@echo "Available commands:"
	@echo "  make init        - Initialize project with uv lock and sync"
	@echo "  make install     - Install dependencies using uv"
	@echo "  make install-test- Install test dependencies using uv"
	@echo "  make clean       - Clean Python cache files"
	@echo "  make run         - Run emulator locally with reload"
	@echo "  make run-prod    - Run emulator locally in production mode"
	@echo "  make test        - Run pytest test suite"
	@echo "  make test-coverage- Run tests with coverage report"
	@echo "  make docker-build- Build Docker image"
	@echo "  make up          - Start services with Docker Compose"
	@echo "  make down        - Stop services"
	@echo "  make logs        - View Docker Compose logs"
	@echo "  make restart     - Restart services"
	@echo "  make status      - Check emulator status"
	@echo "  make clear-tasks - Clear all tasks from emulator"
	@echo "  make format      - Format code with black and isort"
	@echo "  make lint        - Run linting checks"
