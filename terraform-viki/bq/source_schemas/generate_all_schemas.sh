#!/bin/bash

# Set project and database
PROJECT_ID="viki-dev-app-wsky"
DB_NAME="viki-dev"

# Create output directory if it doesn't exist
mkdir -p "$(dirname "$0")/schemas"

# Function to extract collection path from env file
get_collection_path() {
    local env_file="$1"
    grep "COLLECTION_PATH=" "$env_file" | cut -d'=' -f2 | tr -d '"' | tr -d "'"
}

# Process each .env file
for env_file in ../firebase_extensions/extensions_template/*.env; do
    if [ -f "$env_file" ]; then
        # Get collection path
        collection_path=$(get_collection_path "$env_file")
        
        if [ ! -z "$collection_path" ]; then
            # Generate output filename from env filename
            base_name=$(basename "$env_file" .env)
            output_file="schemas/${base_name}_schema.json"
            
            echo "Generating schema for $collection_path"
            python generate_schema.py "$collection_path" \
                --project "$PROJECT_ID" \
                --db_name "$DB_NAME" \
                --output "$output_file"
        fi
    fi
done

echo "Schema generation complete. Check the schemas directory for output files."
