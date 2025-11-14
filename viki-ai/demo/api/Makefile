PIPENV = pipenv

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

init: ## Init local dev environment with pipenv
	HNSWLIB_NO_NATIVE=1 PYDEVD_DISABLE_FILE_VALIDATION=1 $(PIPENV) sync --dev

uninstall: ## Remove local dev environment
	$(PIPENV) uninstall

run: ## Run app
	docker build -t eai-ai/demo-api .
	docker run \
		--name demo-api \
		--rm -it \
		--mount src=$$PWD/demo,target=/app/demo,type=bind \
		--mount src=$$HOME/.config/gcloud,target=/root/.config/gcloud,type=bind \
		-p 12000:12000 \
		-e SERVICE=demo \
		-e STAGE=dev \
		-e VERSION=dev \
		-e DEBUG=true \
		-e GCS_BUCKET_NAME=viki-dev-eai \
		-e GCP_PROJECT_ID=viki-dev-app-wsky \
		eai-ai/extract_and_fill
