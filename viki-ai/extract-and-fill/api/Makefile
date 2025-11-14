PIPENV = pipenv

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

init: ## Init local dev environment with pipenv
	HNSWLIB_NO_NATIVE=1 
	PYDEVD_DISABLE_FILE_VALIDATION=1 
	$(PIPENV) lock
	$(PIPENV) sync --dev

run-cli:
	$(PIPENV) run python extract_and_fill/entrypoints/cli.py

uninstall: ## Remove local dev environment
	$(PIPENV) uninstall

run-tests:
	$(PIPENV) run python -m pytest extract_and_fill/tests

run-prompt-runner:
	$(PIPENV) run python extract_and_fill/entrypoints/prompt_runner.py

run-medical-coder-tests:
	$(PIPENV) run python extract_and_fill/entrypoints/medical_coding_tests.py


run: ## Run app
	docker build -t eai-ai/extract_and_fill .
	docker run \
		--name eai-ai-extract_and_fill \
		--rm -it \
		--mount src=$$PWD/extract_and_fill,target=/app/extract_and_fill,type=bind \
		--mount src=$$HOME/.config/gcloud,target=/root/.config/gcloud,type=bind \
		-p 12000:12000 \
		-e SERVICE=extract_and_fill \
		-e STAGE=dev \
		-e VERSION=dev \
		-e DEBUG=true \
		-e GCS_BUCKET_NAME=viki-dev-eai \
		-e GCP_PROJECT_ID=viki-dev-app-wsky \
		-e GCP_PROJECT_LOCATION=us-central1 \
		-e PINECONE_API_KEY=64cadacf-4c6a-4ac3-b767-6398f874acb5 \
		-e PINECONE_ENV=gcp-starter \
		-e PINECONE_VECTOR_SEARCH_INDEX_NAME=extractor-vector-index \
		-e GCP_VECTOR_SEARCH_INDEX_GCS_URI=gs://extraction-index-dev/contents/ \
		-e GCP_VECTOR_SEARCH_INDEX_NAME=projects/145042810266/locations/us-east4/indexes/7823403463626194944 \
		-e GCP_VECTOR_SEARCH_INDEX_ENDPOINT=projects/145042810266/locations/us-east4/indexEndpoints/957208434862718976 \
		-e GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID=extraction_index_deployed__1699595619091 \
		-e FIRESTORE_DB=ai-dev \
		eai-ai/extract_and_fill

run-no-docker:
	pipenv run  uvicorn extract_and_fill.entrypoints.http:app --host 0.0.0.0 --port 12000 --reload

.EXPORT_ALL_VARIABLES:
SERVICE=extract_and_fill
STAGE=dev
VERSION=dev
DEBUG=true
GCS_BUCKET_NAME=viki-dev-eai
GCP_PROJECT_ID=viki-dev-app-wsky
GCP_PROJECT_LOCATION=us-east4
GCP_PROJECT_LOCATION_2=us-central1
PINECONE_API_KEY=64cadacf-4c6a-4ac3-b767-6398f874acb5
PINECONE_ENV=gcp-starter
PINECONE_VECTOR_SEARCH_INDEX_NAME=extractor-vector-index
GCP_VECTOR_SEARCH_INDEX_GCS_URI=gs://extraction-index-dev/contents/
GCP_VECTOR_SEARCH_INDEX_NAME=projects/145042810266/locations/us-east4/indexes/7823403463626194944
GCP_VECTOR_SEARCH_INDEX_ENDPOINT=projects/145042810266/locations/us-east4/indexEndpoints/957208434862718976
GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID=extraction_index_deployed__1699595619091
FIRESTORE_DB=ai-dev