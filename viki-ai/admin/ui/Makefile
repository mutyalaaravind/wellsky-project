.PHONY: help configure install build start clean docker-build docker-run dev

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

configure: ## Configure development environment
	cp ../../.npmrc ./
	npm install

install: ## Install dependencies
	npm install

build: ## Build production bundle
	npm run build

start: ## Start development server
	npm run dev

dev: ## Start development server (alias for start)
	npm run dev

clean: ## Clean build artifacts and dependencies
	rm -rf node_modules dist

docker-build: ## Build Docker image
	docker build -t admin-ui .

docker-run: ## Run Docker container
	docker run -p 14001:80 admin-ui