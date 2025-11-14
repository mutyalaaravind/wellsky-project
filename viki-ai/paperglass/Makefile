PIPENV = pipenv

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

run: ## Run in Docker
	docker-compose up --build

configure:
	cp ../.npmrc ./widget/

exec: ## Run command in Docker
	@# e. g.
	@# make exec CMD='python3 -m paperglass.entrypoints.document_labeling 0'
ifndef CMD
	$(error CMD is not set)
endif
	docker-compose -p eai-ai exec paperglass-api $(CMD)
