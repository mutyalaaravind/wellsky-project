PIPENV = pipenv

# Import environment variables if an .env is present for local development.  Upper environment secrets will be set through a secrets manager
ifneq (,$(wildcard ../../.env))
    include ../../.env
    export
endif

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

init: ## Init local dev environment with pipenv
	HNSWLIB_NO_NATIVE=1 
	PYDEVD_DISABLE_FILE_VALIDATION=1 
	$(PIPENV) lock
	$(PIPENV) sync --dev

install:
	$(PIPENV) install
	$(PIPENV) run python -m spacy download en_core_web_md

uninstall: ## Remove local dev environment
	$(PIPENV) uninstall

cli:
	$(PIPENV) run python paperglass/entrypoints/cli.py

run-tests:
		$(PIPENV) run pytest -v -s paperglass/tests/test_rest.py

run-orchestrator:
	$(PIPENV) run python paperglass/entrypoints/orchestrator.py --mode single --documentId $(DOCUMENT_ID)

run-app-integration:
	$(PIPENV) run python paperglass/entrypoints/app_integration_launcher.py

run-doc-processor:
	$(PIPENV) run python paperglass/entrypoints/process_docs.py $(REPROCESS_PIPELINE) $(REPROCESS_DOC_ID)

run-doc-ai:
	$(PIPENV) run python paperglass/entrypoints/doc_ai.py

run-migrations:
	$(PIPENV) run python paperglass/entrypoints/migrate.py

run-medispan-search:
	$(PIPENV) run python paperglass/entrypoints/medispan_search.py  "$(SEARCH_TERM)"

run-medispan-vector-search:
	$(PIPENV) run python paperglass/entrypoints/medispan_vector_search_cli.py  "$(SEARCH_TERM)"

run-medispan-firestore-vector-search:
	$(PIPENV) run python paperglass/entrypoints/medispan_firestore_vector_search_cli.py  "$(SEARCH_TERM)"

run-normalize-medications:
	$(PIPENV) run python paperglass/entrypoints/normalize_medications_cli.py  

run-medispan_matching:
	$(PIPENV) run python paperglass/entrypoints/medispan_matching_cli.py  

run-poc:
	$(PIPENV) run python paperglass/entrypoints/poc.py

run-medication-profile:
	$(PIPENV) run python paperglass/entrypoints/hhh_medication_profile.py

run-test-orchestration:
	$(PIPENV) run python paperglass/entrypoints/test_orchestration_cli_experiment.py

run-goldenset-assessment:
	$(PIPENV) run python paperglass/entrypoints/goldenset_assessment_cli.py

run-e2e-tests:
	$(PIPENV) run python paperglass/entrypoints/e2e_test_cli.py

run-e2e-test-create:
	$(PIPENV) run python paperglass/entrypoints/e2e_test_create_cli.py

run-current-test:
	$(PIPENV) run python paperglass/entrypoints/current_test.py

run-report-prompt-rate:
	$(PIPENV) run python paperglass/entrypoints/report_prompt_rate.py

run-document-medication-grader:
	$(PIPENV) run python paperglass/entrypoints/orchestrate_document_medication_grader.py

run-document-medication-grader-cli:
	$(PIPENV) run python paperglass/entrypoints/orchestrate_document_medication_grader_cli.py

run-get-document-medication-grade:
	$(PIPENV) run python paperglass/entrypoints/get_document_medication_grade_cli.py

run-okta-verification:
	$(PIPENV) run python paperglass/entrypoints/okta_verifier.py

run-clinical-data-extraction:
	$(PIPENV) run python paperglass/entrypoints/clinical_data_extractions.py

run-orchestrate-conditions:
	$(PIPENV) run python paperglass/entrypoints/orchestrate_conditions_cli.py

run-orchestrator_v3:
	$(PIPENV) run python paperglass/entrypoints/orchestrate_v3.py --documentId $(DOCUMENT_ID)

run-stats:
	$(PIPENV) run python paperglass/entrypoints/stats.py

run-test-metadata-api:
	$(PIPENV) run python paperglass/entrypoints/test_hhh_metadata_api.py

run-test-condition-orchestrator:
	$(PIPENV) run python paperglass/entrypoints/orchestrate_healthconditions_api_cli.py
		
run-load-test:
	$(PIPENV) run python paperglass/entrypoints/load_test.py

run-load-test-throughput:
	$(PIPENV) run python paperglass/entrypoints/load_test_throughput.py

run-pubsub-test:
	$(PIPENV) run python paperglass/entrypoints/pubsub_test.py

run-recover:
	$(PIPENV) run python paperglass/entrypoints/recover.py

run-error-assessment:
	$(PIPENV) run python paperglass/entrypoints/error_assessment_cli.py

run-test-orchestrator-flash:	
	$(PIPENV) run python paperglass/entrypoints/test_orchestrator_flash.py	
run-prompt-test:
	$(PIPENV) run python paperglass/entrypoints/prompt_medication_extraction.py
run-ops-definition:
	$(PIPENV) run python paperglass/entrypoints/create_doc_ops_definition.py

run-update-doc-ops-definition:
	$(PIPENV) run python paperglass/entrypoints/document_operation_definition_updater.py

# To run a workbench, use the following command format:  make run-workbench WORKBENCH="{NAME_OF_THE_WORKBENCH}"
run-workbench:
	$(PIPENV) run python paperglass/entrypoints/run_workbench.py --workbench $(WORKBENCH)

run-firestore-load-test:
	$(PIPENV) run python paperglass/entrypoints/load_test_firestore.py

run-tenant-config:
	$(PIPENV) run python paperglass/entrypoints/create_tenant_config.py

run-test-rulesengine:
	$(PIPENV) run pytest paperglass/tests/test_rules_engine.py -s -vvvv

.EXPORT_ALL_VARIABLES:
SERVICE= paperglass
STAGE= qa
VERSION= $(STAGE)
DEBUG= 'true'
GCP_PROJECT_ID= viki-$(STAGE)-app-wsky

GCP_PUBSUB_PROJECT_ID= viki-$(STAGE)-app-wsky # Emulator off
#GCP_PUBSUB_PROJECT_ID = google-cloud-firestore-emulator # Emulator on
#FIRESTORE_EMULATOR_HOST= localhost:8080 # Emulator on
#PUBSUB_EMULATOR_HOST=localhost:8085 #Emulator on

GCS_BUCKET_NAME= viki-ai-provisional-$(STAGE)
GCP_LOCATION= us
GCP_LOCATION_2= us-east4
GCP_LOCATION_3= us-central1
GCP_MULTI_REGION_FIRESTORE_LOCATON= nam5
GCP_FIRESTORE_DB= viki-$(STAGE)
GCP_DOCAI_HCC_PROCESSOR_ID= 7359477870825dbb
GCP_DOCAI_HCC_PROCESSOR_VERSION= pretrained
GCP_DOCAI_SUMMARIZER_PROCESSOR_ID= fcaac0296ec91273
GCP_DOCAI_SUMMARIZER_PROCESSOR_VERSION= pretrained-foundation-model-v1.0-2023-08-22
GCP_DOCAI_DOC_PROCESSOR_ID= 621fe166d8f57278#dev: 621fe166d8f57278  qa: c26eeb8f2087542e
GCP_DOCAI_DOC_PROCESSOR_VERSION= pretrained
PYTHONUNBUFFERED= "1"  # Flush `print`s immediately
CLOUD_PROVIDER= local# Must be "google" when deployed
GCP_SEARCH_AND_CONVERSATION_DATA_SOURCE_ID= patient-charts-4_1709757625813
GCP_SEARCH_AND_CONVERSATION_FHIR_DATA_SOURCE_ID= fhir-store-search
GCP_VECTOR_SEARCH_INDEX_GCS_URI= gs://viki-ai-provisional-dev/icd10-search-balki/
GCP_VECTOR_SEARCH_INDEX_NAME= projects/145042810266/locations/us-east4/indexes/7823403463626194944
GCP_VECTOR_SEARCH_INDEX_ENDPOINT= projects/145042810266/locations/us-east4/indexEndpoints/957208434862718976
GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID= extraction_index_deployed__1699595619091
GCP_VECTOR_SEARCH_INDEX_NAME_2= projects/145042810266/locations/us-east4/indexes/7823403463626194944
GCP_VECTOR_SEARCH_INDEX_ENDPOINT_2= projects/145042810266/locations/us-east4/indexEndpoints/957208434862718976
GCP_VECTOR_SEARCH_DEPLOYED_INDEX_ID_2= extraction_index_deployed__1699595619091
FHIR_SERVER_URL= https://healthcare.googleapis.com/v1/projects/viki-$(STAGE)-app-wsky/locations/us-central1/datasets/viki-dataset/fhirStores
FHIR_DATA_STORE= viki-fhir-store
FHIR_DATA_SET= viki-dataset
FHIR_SEARCH_STORE_ID = fhir-store-search
INTEGRATION_PROJECT_NAME= MedicationExtractionPipeline
SELF_API= https://ai-paperglass-api-zqftmopgsq-uk.a.run.app/api  #DEV
#SELF_API= https://ai-paperglass-api-p32qledfyq-uk.a.run.app/api # QA
CLOUD_TASK_QUEUE_NAME= paperglass-extraction-queue
CLOUD_TASK_QUEUE_NAME_PRIORITY= paperglass-extraction-priority-queue
CLOUD_TASK_QUEUE_NAME_2= paperglass-classification-queue
CLOUD_TASK_QUEUE_NAME_PRIORITY_2= paperglass-classification-priority-queue
CLOUD_TASK_QUEUE_NAME_QUARANTINE= paperglass-quarantine-queue
CLOUD_TASK_QUEUE_NAME_QUARANTINE_2 = paperglass-quarantine-queue
CLOUD_TASK_PUBLISH_CALLBACK_QUEUE_NAME = paperglass-host-publish-callback-queue

CLOUD_TASK_COMMAND_SCHEDULE_QUEUE_NAME= paperglass-command-schedule-queue
SERVICE_ACCOUNT_EMAIL= viki-ai-$(STAGE)-sa@viki-$(STAGE)-app-wsky.iam.gserviceaccount.com
APPLICATION_INTEGRATION_TRIGGER_ID= api_trigger/MedicationExtractionPipeline_API_2
MEDISPAN_API_URL = https://ct.dev.wellsky.io/api/v1/drug/information/search
MEDISPAN_CLIENT_ID= $(S__MEDISPAN_CLIENT_ID)
MEDISPAN_CLIENT_SECRET= $(S__MEDISPAN_CLIENT_SECRET)
MEDISPAN_CACHE_ENABLE = false
MEDISPAN_PAGE_SIZE = 100
MEDISPAN_FILTER_ENABLED = true
MEDISPAN_LLM_SCORING_ENABLED = true

MEDISPAN_VECTOR_SEARCH_PROJECT_ID = viki-qa-app-wsky
MEDISPAN_VECTOR_SEARCH_REGION = us-central1
MEDISPAN_VECTOR_SEARCH_DEPLOYMENT_ID = medsearch_1723187204068
MEDISPAN_VECTOR_SEARCH_ENDPOINT_ID = 7990947045466701824

MEDISPAN_STRATEGY = firestore#vector-search

HHH_MEDICATION_PROFILE_BASE_URL= https://qa.kinnser.net/
HHH_ATTACHMENTS_API= https://api.qa-wsh.hhh-dev-app.prj.gcp.wellsky.io/
HHH_ATTACHMENTS_AUTH_SERVER= https://auth.stable.wellsky.io/connect/token
HHH_ATTACHMENTS_CLIENT_ID= client.hhh.patient.demographics.qa
HHH_ATTACHMENTS_CLIENT_SECRET= ${S__HHH_ATTACHMENTS_CLIENT_SECRET}

OKTA_CLIENT_ID=$(S__OKTA_CLIENT_ID)
OKTA_CLIENT_SECRET=$(S__OKTA_CLIENT_SECRET)
OKTA_AUDIENCE=viki.prod.wellsky.io# dev: "viki.prod.wellsky.io", qa: "viki.prod.wellsky.io", stage: "viki.prod.wellsky.io", prod: "viki.dev.wellsky.io"
OKTA_VERIFY=true
OKTA_TOKEN_ISSUER_URL=https://wellsky-ciam.oktapreview.com/oauth2/ausajt8hv1B8S7hkh1d7/v1/token #dev/qa
# OKTA_TOKEN_ISSUER_URL= "https://wellsky-ciam.okta.com/oauth2/aushirk9h5LbqrTwi5d7/v1/token" #stage
# OKTA_TOKEN_ISSUER_URL= "https://wellsky-ciam.okta.com/oauth2/ausf79o4jdnCkJlOy5d7/v1/token" #prod
OKTA_SERVICE_ISSUER_URL=
OKTA_SERVICE_AUDIENCE=

OTEL_SDK_DISABLED= true

NEW_RELIC_LICENSE_KEY= ""

REPROCESS_PIPELINE=default
REPROCESS_DOC_ID=442ec7b224f811ef8a5542004e494300
EXTRACTION_PUBSUB_TOPIC_NAME=extraction_ordered_events_topic

SHAREPOINT_CLIENT_ID=$(S__SHAREPOINT_CLIENT_ID)
SHAREPOINT_CLIENT_SECRET=$(S__SHAREPOINT_CLIENT_SECRET)

ENTITY_EXTRACTION_API_URL = http://entity-extraction-api:18000
ENTITY_EXTRACTION_LAUNCH_QUEUE_NAME = entity-extraction-launch-queue

MEDICATION_EXTRACTION_V4_API_DEFAULT_URL =
MEDICATION_EXTRACTION_V4_API_HIGH_URL =
MEDICATION_EXTRACTION_V4_API_QUARANTINE_URL =
MEDICATION_EXTRACTION_V4_TOPIC=medication_extraction_v4_topic
MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME=
MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME_PRIORITY=
MEDICATION_EXTRACTION_V4_CLOUD_TASK_QUEUE_NAME_QUARANTINE=
MEDICATION_EXTRACTION_V4_API_URL=

CLOUD_TASK_COMMAND_QUEUE_NAME=
CLOUD_TASK_COMMAND_EXTERNAL_CREATE_DOCUMENT_TASK_QUEUE_NAME=