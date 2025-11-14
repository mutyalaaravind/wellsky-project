PIPENV = pipenv
ENV = dev

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

configure: ## Initialize settings
	make -C ./autoscribe/ configure
	make -C ./demo/ configure
	make -C ./extract-and-fill/ configure
	make -C ./nlparse/ configure
	make -C ./paperglass/ configure
	make -C ./admin/ configure

	make -C ./frontends/ configure

run: ## Run in Docker
	HOST_IP=$$(hostname -I | awk '{print $$1}') docker-compose up --build

login: ## gcp auth + tunnelling to qa alloydb for vector db
	gcloud auth login
	gcloud config set project viki-$(ENV)-app-wsky
	gcloud auth application-default login --impersonate-service-account=viki-ai-$(ENV)-sa@viki-$(ENV)-app-wsky.iam.gserviceaccount.com

auth-tunnel:
	gcloud compute ssh hhh-proxy \
        --tunnel-through-iap \
        --zone=us-east4-a \
        --ssh-flag="-L 0.0.0.0:5433:10.203.132.192:5432" \
        --ssh-flag="-N" \
        --ssh-flag="-f"
