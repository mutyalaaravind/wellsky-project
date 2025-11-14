#!/bin/bash

# Check if environment parameter is provided
if [ -z "$1" ]; then
    echo "Error: Environment parameter is required"
    echo "Usage: ./generate_env_dedup_sqls.sh <env>"
    echo "Example: ./generate_env_dedup_sqls.sh dev"
    exit 1
fi

ENV=$1
TEMPLATE_DIR="../dedup_sql_template"
OUTPUT_DIR="../../env/$ENV/ai/dedup_sql"

SCHEMA_DIR="../schema_changes"
SCHEMA_OUTPUT_DIR="../../env/$ENV/ai/bq_schema_changes"

# Check if template directory exists
if [ ! -d "$TEMPLATE_DIR" ]; then
    echo "Error: Template directory $TEMPLATE_DIR not found"
    exit 1
fi

if [ ! -d "$SCHEMA_DIR" ]; then
    echo "Error: Schema Changes directory $SCHEMA_DIR not found"
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"
mkdir -p "$SCHEMA_OUTPUT_DIR"

# Copy and modify each SQL file
for template_file in "$TEMPLATE_DIR"/*.sql; do
    if [ -f "$template_file" ]; then
        filename=$(basename "$template_file")
        output_file="$OUTPUT_DIR/$filename"
        
        # Copy and replace environment in the file
        sed "s/viki-env-app-wsky/viki-$ENV-app-wsky/g" "$template_file" > "$output_file"
        
        echo "Generated $output_file with $ENV environment"
    fi
done

for schema_file in "$SCHEMA_DIR"/*.sql; do
    if [ -f "$schema_file" ]; then
        filename=$(basename "$schema_file")
        output_file="$SCHEMA_OUTPUT_DIR/$filename"
        
        # Copy and replace environment in the file
        sed "s/viki-env-app-wsky/viki-$ENV-app-wsky/g" "$schema_file" > "$output_file"
        
        echo "Generated $output_file with $ENV environment"
    fi
done



echo "Successfully generated environment-specific SQL files in $OUTPUT_DIR"
