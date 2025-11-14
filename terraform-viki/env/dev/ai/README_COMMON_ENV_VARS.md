# Common Environment Variables for AI Services

This document explains how to use the centralized environment variables system for AI services.

## Overview

The `services_common_env.tf` file provides a centralized way to manage environment variables that are shared across multiple AI services. This approach:

1. **Reduces duplication** - Common environment variables are defined once
2. **Ensures consistency** - All services use the same base configuration
3. **Allows overrides** - Services can override specific variables when needed
4. **Simplifies maintenance** - Changes to common variables only need to be made in one place

## How It Works

### Common Environment Variables

The `local.common_env` block in `services_common_env.tf` contains all the environment variables that are shared across AI services, including:

- Core service configuration (STAGE, DEBUG, CLOUD_PROVIDER)
- GCP configuration (project IDs, regions, Firestore settings)
- Document AI configuration
- Vector Search configuration
- FHIR configuration
- Okta configuration
- OpenTelemetry configuration
- Medispan configuration
- New Relic configuration
- And many more...

### Common Secrets

The `local.common_secrets` block contains the standard secrets that most AI services need:

- MEDISPAN_CLIENT_ID/SECRET
- OKTA_CLIENT_SECRET
- HHH_ATTACHMENTS_CLIENT_SECRET
- SHAREPOINT_CLIENT_ID/SECRET

## Usage Examples

### Basic Usage (No Overrides)

For a service that uses all common environment variables without any changes:

```hcl
module "my_service" {
  source = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name   = "ai-my-service"
  # ... other configuration ...
  
  env = local.common_env
  secrets = toset(local.common_secrets)
}
```

### Usage with Overrides

For a service that needs to override or add specific environment variables:

```hcl
module "paperglass_api" {
  source = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name   = "ai-paperglass-api"
  # ... other configuration ...
  
  env = merge(local.common_env, {
    # Service-specific overrides
    SERVICE                = "paperglass"
    VERSION                = var.paperglass_version
    SELF_API               = "https://ai-paperglass-api-zqftmopgsq-uk.a.run.app/api"
    OTEL_SERVICE_NAME      = "viki.paperglass.api"
    NEW_RELIC_APP_NAME     = "Viki Paperglass API (${var.env})"
  })
  secrets = toset(local.common_secrets)
}
```

### Usage with Additional Secrets

If a service needs additional secrets beyond the common ones:

```hcl
module "my_service" {
  source = "git@github.com:mediwareinc/terraform-gcp-cloudrun.git?ref=v0.7.5"
  name   = "ai-my-service"
  # ... other configuration ...
  
  env = merge(local.common_env, {
    SERVICE = "my_service"
    VERSION = var.my_service_version
  })
  
  secrets = toset(concat(local.common_secrets, [
    {
      key     = "MY_CUSTOM_SECRET",
      name    = module.secret["my_custom_secret"].name,
      version = "latest",
    }
  ]))
}
```

## Benefits

### Before (Duplicated Configuration)

```hcl
# In service A
env = {
  STAGE = var.env
  DEBUG = (var.env == "dev" || var.env == "qa") ? "true" : "false"
  GCP_PROJECT_ID = var.app_project_id
  # ... 50+ more variables ...
  SERVICE = "service_a"
}

# In service B  
env = {
  STAGE = var.env
  DEBUG = (var.env == "dev" || var.env == "qa") ? "true" : "false"
  GCP_PROJECT_ID = var.app_project_id
  # ... 50+ more variables (duplicated!) ...
  SERVICE = "service_b"
}
```

### After (Centralized with Overrides)

```hcl
# In service A
env = merge(local.common_env, {
  SERVICE = "service_a"
})

# In service B
env = merge(local.common_env, {
  SERVICE = "service_b"
})
```

## Maintenance

### Adding a New Common Variable

To add a new environment variable that should be available to all services:

1. Add it to the `common_env` block in `services_common_env.tf`
2. All services will automatically inherit this variable

### Modifying an Existing Common Variable

1. Update the variable in the `common_env` block
2. All services will automatically use the updated value
3. Services with overrides will continue to use their override values

### Environment-Specific Values

Some variables in the common configuration are already environment-aware:

```hcl
DEBUG = (var.env == "dev" || var.env == "qa") ? "true" : "false"
GCP_FIRESTORE_DB = "viki-${var.env}"
MEDICAL_SUMMARIZATION_API_URL = "https://healthcare.googleapis.com/v1alpha2/projects/viki-${var.env}-app-wsky/..."
```

## Migration Guide

To migrate an existing service to use common environment variables:

1. **Identify common variables**: Look at the service's current `env` block and identify which variables are also present in `common_env`

2. **Identify service-specific variables**: Note which variables are unique to this service

3. **Replace the env block**:
   ```hcl
   # Before
   env = {
     # 50+ variables including many common ones
   }
   
   # After
   env = merge(local.common_env, {
     # Only service-specific variables and overrides
   })
   ```

4. **Update secrets** (if using common secrets):
   ```hcl
   # Before
   secrets = toset([
     # List of individual secrets
   ])
   
   # After
   secrets = toset(local.common_secrets)
   # or if you need additional secrets:
   secrets = toset(concat(local.common_secrets, [
     # additional secrets
   ]))
   ```

5. **Test**: Ensure the service still works correctly with the new configuration

## Best Practices

1. **Use descriptive override names**: When overriding variables, use clear names that indicate the purpose
2. **Document service-specific overrides**: Add comments explaining why certain variables are overridden
3. **Keep overrides minimal**: Only override what's truly different for the service
4. **Test thoroughly**: Always test services after migrating to the common variables system
5. **Update all environments**: Apply the same pattern to dev, qa, stage, and prod environments
