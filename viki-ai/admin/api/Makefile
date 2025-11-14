.PHONY: install build run clean docker-build docker-run docker-compose logs lock sync test test-coverage install-test test-unit test-unit-coverage run-compute-tokens

.EXPORT_ALL_VARIABLES:
VERSION= dev
SERVICE= admin
STAGE= dev
DEBUG= true
CLOUD_PROVIDER= gcp
GCP_PROJECT_ID= viki-dev-app-wsky
GCP_PUBSUB_PROJECT_ID= viki-dev-app-wsky
GCS_BUCKET_NAME= viki-ai-provisional-dev
GCP_LOCATION= us
GCP_LOCATION_2= us-east4
GCP_LOCATION_3= us-central1
GCP_MULTI_REGION_FIRESTORE_LOCATON= nam5
GCP_FIRESTORE_DB= viki-dev
SERVICE_ACCOUNT_EMAIL= viki-ai-dev-sa@viki-dev-app-wsky.iam.gserviceaccount.com
SELF_API_URL= http://admin-api:14000

configure: ## Configure development environment
	uv lock
	uv sync

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

# Testing
test: install-test
	uv run pytest tests/ -v

test-coverage: install-test
	uv run pytest tests/ -v --cov=src --cov-report=term-missing

test-unit: install-test
	uv run pytest tests/unit/ -v

test-unit-coverage: install-test
	uv run pytest tests/unit/ -v --cov=src --cov-report=term-missing

run-compute-tokens:
	uv run pytest tests/integration/test_token_estimation.py -v -s

# Docker commands
docker-build:
	docker build -t admin-api .

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

# Help command
help:
	@echo "Available commands:"
	@echo "  make init        - Initialize dependencies with uv"
	@echo "  make install     - Install dependencies using uv"
	@echo "  make install-test- Install test dependencies using uv"
	@echo "  make clean       - Clean Python cache files"
	@echo "  make test        - Run pytest test suite"
	@echo "  make test-coverage- Run tests with coverage report"
	@echo "  make test-unit   - Run unit tests only"
	@echo "  make test-unit-coverage - Run unit tests with coverage report"
	@echo "  make run-compute-tokens - Run token estimation integration tests"
	@echo "  make docker-build- Build Docker image"
	@echo "  make up          - Start services with Docker Compose"
	@echo "  make down        - Stop services"
	@echo "  make logs        - View Docker Compose logs"
	@echo "  make restart     - Restart services"
	@echo "  make format      - Format code with black and isort"
	@echo "  make lint        - Run linting checks"