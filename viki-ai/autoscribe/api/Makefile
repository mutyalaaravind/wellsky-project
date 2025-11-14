PIPENV = pipenv

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

init: ## Init local dev environment with pipenv
	HNSWLIB_NO_NATIVE=1 PYDEVD_DISABLE_FILE_VALIDATION=1 $(PIPENV) sync --dev

uninstall: ## Remove local dev environment
	$(PIPENV) uninstall

run: ## Run app
	docker build -t eai-ai/autoscribe .
	docker run \
		--name eai-ai-autoscribe \
		--rm -it \
		--mount src=$$PWD/autoscribe,target=/app/autoscribe,type=bind \
		--mount src=$$HOME/.config/gcloud,target=/root/.config/gcloud,type=bind \
		-p 11000:11000 \
		-e SERVICE=autoscribe \
		-e STAGE=dev \
		-e VERSION=dev \
		-e DEBUG=true \
		-e GCS_BUCKET_NAME=viki-dev-eai \
		-e GCP_PROJECT_ID=viki-dev-app-wsky \
		-e GOOGLE_SPEECH_API_VERSION=v1 \
		-e OKTA_DISABLE='true' \
		-e OKTA_ISSUER='https://wellsky-ciam.oktapreview.com/oauth2/ausajt8hv1B8S7hkh1d7' \
      	-e OKTA_AUDIENCE=viki.dev.wellsky.io \
      	-e OKTA_SCOPE=api.wellsky.viki.ai.transcription \
		eai-ai/autoscribe
