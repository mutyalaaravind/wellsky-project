PIPENV = pipenv

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

configure: ## Copy .npmrc files into each microfrontend dir
	@for frontend in `ls -d */`; do echo "Copying .npmrc to $$frontend"; cp ../.npmrc $$frontend/; done

run: ## Run in Docker
	docker-compose up --build
