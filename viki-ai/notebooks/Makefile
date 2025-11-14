PIPENV = pipenv

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

init: ## Init local dev environment with pipenv
	HNSWLIB_NO_NATIVE=1 
	PYDEVD_DISABLE_FILE_VALIDATION=1
	$(PIPENV) lock
	$(PIPENV) sync --dev
	
	

uninstall: ## Remove local dev environment
	$(PIPENV) uninstall

run-locally: ## Run notebooks locally
	$(PIPENV) run jupyter notebook

run: ## Run notebooks in Docker
	docker build -t eai-ai/notebooks .
	docker run \
		--name eai-ai-notebooks \
		--rm -it \
		--mount src=$$PWD/src,target=/notebooks/src,type=bind \
		--mount src=$$HOME/.config/gcloud,target=/root/.config/gcloud,type=bind \
		-p 8888:8888 \
		eai-ai/notebooks
