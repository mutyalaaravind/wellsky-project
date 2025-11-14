# Deploying Extenstions
cd firebase_extensions
gcloud auth login
firebase login
firebase login --reauth
./deploy.sh {ENV} [ENV - dev,qa,stage or prod]

# BigQuery SQL Generation

This directory contains tools for generating BigQuery SQL files for different environments. The process involves two steps:

1. Generate SQL templates
2. Create environment-specific SQL files

## Directory Structure

- `/source_schemas/` - Contains schema definitions and generation scripts
- `/dedup_sql_template/` - Contains template SQL files (generated)
- `/dedup_sql/` - Contains environment-specific SQL files (generated)

## Prerequisites

- Python 3.x
- Access to schema files in `/source_schemas/schemas/`
- Access to environment configuration files in `/firebase_extensions/extensions_template/`

## Step 1: Generate SQL Templates

First, generate the template SQL files that will serve as the base for all environments:

```bash
cd source_schemas
python3 generate_dedup_sqls.py
```

This will:
- Read schema files from `/source_schemas/schemas/`
- Look up table IDs from corresponding .env files in `/firebase_extensions/extensions_template/`
- Generate SQL templates in `/dedup_sql_template/` with:
  - Proper type casting for all fields (BOOLEAN, INTEGER, STRING)
  - Correct ARRAY<STRUCT> syntax
  - Environment placeholder (viki-env-app-wsky)

## Step 2: Generate Environment-Specific SQL Files

After generating templates, create environment-specific SQL files using the shell script:

```bash
cd source_schemas
./generate_env_dedup_sqls.sh <env>
```

Where `<env>` can be:
- `dev` (for development)
- `qa` (for QA)
- `stage` (for staging)
- `prod` (for production)

For example:
```bash
# Generate SQL files for development environment
./generate_env_dedup_sqls.sh dev

# Generate SQL files for QA environment
./generate_env_dedup_sqls.sh qa
```

This will:
- Create a `/dedup_sql/` directory if it doesn't exist
- Copy SQL files from `/dedup_sql_template/`
- Replace 'viki-env-app-wsky' with the appropriate environment name (e.g., 'viki-dev-app-wsky')
- Maintain all type casting and table structures

## Output

The generated SQL files will be placed in:
- Templates: `/dedup_sql_template/`
- Environment-specific files: `/dedup_sql/`

Each SQL file includes:
- CREATE TABLE statement with proper field types
- MERGE operation for deduplication
- Proper type casting for all fields
- Environment-specific project names
