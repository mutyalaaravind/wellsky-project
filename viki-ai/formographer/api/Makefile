PIPENV = pipenv

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

init: ## Init local dev environment with pipenv
	HNSWLIB_NO_NATIVE=1 PYDEVD_DISABLE_FILE_VALIDATION=1 $(PIPENV) sync --dev

uninstall: ## Remove local dev environment
	$(PIPENV) uninstall
