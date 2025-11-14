.PHONY: help api ui build up down logs clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

configure: ## Configure development environment
	make -C ./api configure
	make -C ./ui configure

api: ## Build and run API
	cd api && make init && make docker-build

ui: ## Build and run UI
	cd ui && npm ci && npm run build

build: ## Build both API and UI
	make api
	make ui

up: ## Start services with Docker Compose
	docker-compose up --build

down: ## Stop services
	docker-compose down

logs: ## View Docker Compose logs
	docker-compose logs -f

clean: ## Clean all build artifacts
	cd api && make clean
	cd ui && rm -rf node_modules build