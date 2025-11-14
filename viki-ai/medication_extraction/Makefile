.PHONY: install build run clean docker-build docker-run docker-compose logs lock sync test test-coverage install-test

# Package management
init:
	uv lock
	uv sync

login:
	gcloud auth application-default login

login-impersonate:
	gcloud auth application-default login --impersonate-service-account=viki-ai-qa-sa@viki-qa-app-wsky.iam.gserviceaccount.com

run-evaluation:
	gcloud compute ssh hhh-proxy \
	--tunnel-through-iap \
	--zone=us-east4-a \
	--ssh-flag="-L 5433:10.203.132.192:5432" \
	--ssh-flag="-N" \
	--ssh-flag="-f"
	set -a && . ./.env.qa && set +a && uv run evaluation/evaluation.py

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
	set -a && . ./.env.local && set +a && uv run pytest tests/unit -v

test-integration: install-test
	set -a && . ./.env.dev && set +a && uv run pytest tests/integration/ -v

test-functional: install-test	
	set -a && . ./.env.dev && set +a && \
	export PGVECTOR_HOST="localhost" && \
	export PGVECTOR_PORT="5433" && \
	export PGVECTOR_USER="postgres" && \
	export PGVECTOR_PASSWORD="DummyPasswordForTesting@2025" && \
	export PGVECTOR_DATABASE="postgres" && \
	export PGVECTOR_SSL_MODE="require" && \
	export PGVECTOR_TABLE_MEDISPAN="medispan_drugs_gcp_768_2" && \
	export PGVECTOR_TABLE_MERATIVE="merative_drugs_gcp_768_2" && \
	export PGVECTOR_SEARCH_FUNCTION_MEDISPAN="medispan_search_gcp_768_2" && \
	export PGVECTOR_SEARCH_FUNCTION_MERATIVE="merative_search_gcp_768_2" && \
	export PGVECTOR_FORCE_ONLY_EMBEDDING_SEARCH="true" && \
	export FIRESTOREVECTOR_COLLECTION_MEDISPAN="meddb_medispan" && \
	export FIRESTOREVECTOR_COLLECTION_MERATIVE="meddb_merative" && \
	export GCP_EMBEDDING_MODEL="text-embedding-005" && \
	uv run pytest tests/functional/ -v

test-functional2: install-test
	set -a && . ./.env.dev && set +a && \
	export PGVECTOR_HOST="localhost" && \
	export PGVECTOR_PORT="5433" && \
	export PGVECTOR_USER="postgres" && \
	export PGVECTOR_PASSWORD="DummyPasswordForTesting@2025" && \
	export PGVECTOR_DATABASE="postgres" && \
	export PGVECTOR_SSL_MODE="require" && \
	export PGVECTOR_TABLE_MEDISPAN="medispan_drugs_gcp_768_2" && \
	export PGVECTOR_TABLE_MERATIVE="merative_drugs_gcp_768_2" && \
	export PGVECTOR_SEARCH_FUNCTION_MEDISPAN="medispan_search_gcp_768_2" && \
	export PGVECTOR_SEARCH_FUNCTION_MERATIVE="merative_search_gcp_768_2" && \
	export PGVECTOR_FORCE_ONLY_EMBEDDING_SEARCH="true" && \
	export FIRESTOREVECTOR_COLLECTION_MEDISPAN="meddb_medispan" && \
	export FIRESTOREVECTOR_COLLECTION_MERATIVE="meddb_merative" && \
	export GCP_EMBEDDING_MODEL="text-embedding-005" && \
	PYTHONPATH=src uv run tests/functional/vector_search.py
	
test-coverage: install-test
	set -a && . ./.env.local && set +a && pytest tests/ -v --cov=src --cov-report=term-missing

# Docker commands
docker-build:
	docker build -t medication-extraction .

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
	@echo "  make lock        - Generate requirements.lock from pyproject.toml"
	@echo "  make sync        - Install dependencies from requirements.lock"
	@echo "  make install     - Install dependencies using uv"
	@echo "  make install-test- Install test dependencies using uv"
	@echo "  make clean       - Clean Python cache files"
	@echo "  make test        - Run pytest test suite"
	@echo "  make test-integration - Run integration tests"
	@echo "  make test-functional  - Run functional tests"
	@echo "  make test-coverage- Run tests with coverage report"
	@echo "  make docker-build- Build Docker image"
	@echo "  make up          - Start services with Docker Compose"
	@echo "  make down        - Stop services"
	@echo "  make logs        - View Docker Compose logs"
	@echo "  make restart     - Restart services"
	@echo "  make format      - Format code with black and isort"
	@echo "  make lint        - Run linting checks"
