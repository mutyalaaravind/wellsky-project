# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Terraform infrastructure repository for the VIKI healthcare application platform. It manages cloud resources across multiple environments (dev, qa, stage, prod) in Google Cloud Platform, with additional integrations to Okta, New Relic, and Azure DevOps.

## Architecture

### Environment Structure
- **env/{environment}/**: Environment-specific configurations
  - `dev/`: Development environment (viki-dev-app-wsky)
  - `qa/`: QA environment  
  - `stage/`: Staging environment
  - `prod/`: Production environment
- **env/{environment}/ai/**: AI/ML services and infrastructure within each environment
- **modules/**: Reusable Terraform modules
- **bq/**: BigQuery schemas, deduplication SQL, and Firebase extensions

### Key Components
- **AI Services**: Document AI, Vertex AI, autoscribe, extract & fill, NLP parsing
- **Storage**: AlloyDB, Cloud SQL, Firestore, Cloud Storage
- **Monitoring**: Comprehensive monitoring dashboards, alerts, and metrics
- **Authentication**: Okta integration for user management
- **Data Pipeline**: BigQuery data processing and Firebase extensions

## Common Development Commands

### Terraform Operations
```bash
# Initialize Terraform (run from environment directory)
cd env/{environment}
terraform init

# Plan changes
terraform plan

# Apply changes  
terraform apply

# Target specific resources
terraform apply -target=resource_type.resource_name
```

### Environment Promotion
Use the promotion script to sync configurations between environments:
```bash
# Promote from dev to qa
./promote.env.sh dev qa

# Promote from stage to prod  
./promote.env.sh stage prod
```

### BigQuery Schema Management
```bash
# Generate all schemas from Firestore collections
cd bq/source_schemas
./generate_all_schemas.sh

# Generate deduplication SQL files
./generate_env_dedup_sqls.sh
```

## Important Files and Patterns

### Environment Configuration
- `terraform.tfvars`: Environment-specific variables (not copied during promotion)
- `providers.tf`: Provider configurations for GCP, Okta, New Relic
- `variables.tf`: Variable definitions
- `locals.tf`: Local value calculations

### AI/ML Infrastructure  
- `env/{env}/ai/`: Contains all AI-related services and infrastructure
- `services_*.tf`: Cloud Run services for different AI capabilities
- `monitoring-*.tf`: Monitoring dashboards and metrics
- `vertex_ai_*.tf`: Vertex AI indexes and notebooks

### Monitoring Structure
- `monitoring-dashboard-*.tf`: Cloud Monitoring dashboards
- `monitoring-metric-*.tf`: Custom metrics definitions  
- `monitoring-alerts.tf`: Alerting policies

## Development Notes

### Provider Configuration
- Uses multiple aliased Google providers for different projects (mgmt vs app)
- Requires Okta API token for user management
- New Relic integration for observability

### File Exclusions During Promotion
The promotion script excludes:
- `*.tfvars` files (environment-specific)
- `*.tfstate` files
- `backend.tf` and `terraform.tf`
- Files prefixed with `_`
- `.terraform/` directories

### Environment Hierarchy
Promotion follows a strict hierarchy: dev → qa → stage → prod