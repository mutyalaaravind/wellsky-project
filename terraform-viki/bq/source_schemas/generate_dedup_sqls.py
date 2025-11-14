#!/usr/bin/env python3
import json
import os
from pathlib import Path

def get_bigquery_type(schema_type):
    """Convert schema type to BigQuery type."""
    type_mapping = {
        'STRING': 'STRING',
        'BOOLEAN': 'BOOLEAN',
        'INTEGER': 'INTEGER',
        'ARRAY<STRING>': 'ARRAY<STRING>',
        'ARRAY<RECORD>': 'ARRAY<STRUCT<data STRING>>',
        'TIMESTAMP': 'TIMESTAMP',
        'RECORD': 'RECORD'
    }
    return type_mapping.get(schema_type, 'STRING')

def get_json_extract(field_name, field_type):
    """Generate appropriate JSON extract expression based on field type."""
    json_path = field_name.replace('.', '.')  # Keep the dots for JSON path
    if field_type == 'BOOLEAN':
        return f"CAST(JSON_EXTRACT(data, '$.{json_path}') AS BOOLEAN) as data_{field_name.replace('.', '_')}"
    elif field_type == 'INTEGER':
        return f"CAST(JSON_EXTRACT(data, '$.{json_path}') AS INT64) as data_{field_name.replace('.', '_')}"
    elif field_type == 'TIMESTAMP':
        return f"TIMESTAMP(JSON_EXTRACT_SCALAR(data, '$.{json_path}')) as data_{field_name.replace('.', '_')}"
    elif field_type == 'ARRAY<STRUCT<data STRING>>':
        return f"ARRAY(SELECT STRUCT(med as data) FROM UNNEST(JSON_EXTRACT_ARRAY(data, '$.{json_path}')) as med) as data_{field_name.replace('.', '_')}"
    elif field_type.startswith('ARRAY'):
        return f"JSON_EXTRACT_ARRAY(data, '$.{json_path}') as data_{field_name.replace('.', '_')}"
    elif field_type == 'RECORD':
        field_type = 'STRING'
        return f"JSON_EXTRACT(data, '$.{json_path}') as data_{field_name.replace('.', '_')}"
    else:  # STRING and other types
        return f"JSON_EXTRACT_SCALAR(data, '$.{json_path}') as data_{field_name.replace('.', '_')}"

def get_table_id_from_env(schema_name):
    """Get TABLE_ID from corresponding .env file."""
    # Convert schema filename to env filename
    # e.g., fs-bq-medications-extracted-medications_schema.json -> fs-bq-medications-extracted-medications.env
    env_name = schema_name.replace('_schema.json', '.env')
    env_path = Path(__file__).parent.parent / 'firebase_extensions' / 'extensions_template' / env_name
    
    if not env_path.exists():
        print(f"Warning: No .env file found for {schema_name}")
        # Extract fallback table name from schema filename
        return schema_name.replace('fs-bq-', '').replace('_schema.json', '')
    
    # Read .env file and find TABLE_ID
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('TABLE_ID='):
                return line.strip().split('=')[1]
    
    # Fallback if TABLE_ID not found
    return schema_name.replace('fs-bq-', '').replace('_schema.json', '')

def generate_sql_for_schema(schema_path):
    """Generate dedup SQL for a given schema file."""
    # Read schema
    with open(schema_path, 'r') as f:
        schema = json.load(f)
    
    # Get table name from .env file
    schema_filename = os.path.basename(schema_path)
    table_name = get_table_id_from_env(schema_filename)
    
    # Generate CREATE TABLE fields
    create_fields = []
    json_extracts = []
    update_sets = []
    insert_fields = ['firestore_document_id']
    insert_values = ['document_id']
    
    create_fields.append('  `firestore_document_id` STRING')
    
    # Ensure required clustering fields exist
    clustering_fields = ['app_id', 'tenant_id', 'patient_id', 'modified_at']
    field_types = {
        'app_id': 'STRING',
        'tenant_id': 'STRING',
        'patient_id': 'STRING',
        'modified_at': 'TIMESTAMP'
    }
    
    # Add clustering fields if they don't exist in schema
    existing_fields = {field['name'] for field in schema}
    for field in clustering_fields:
        if field not in existing_fields:
            create_fields.append(f'  `{field}` {field_types[field]}')
    
    for field in schema:
        field_name = field['name']
        field_type = get_bigquery_type(field['type'])
        
        # For nested fields, use underscore in column name
        column_name = field_name.replace('.', '_')
        
        # Add to JSON extracts for all fields including arrays
        json_extracts.append(get_json_extract(field_name, field_type))
        
        if field_type == 'RECORD':
            field_type = 'STRING'
        
        # Add to CREATE TABLE
        create_fields.append(f'  `{column_name}` {field_type}')
            
        # Add to UPDATE SET for all fields
        update_sets.append(f"      target.{column_name} = source.data_{column_name}")
            
        # Add to INSERT
        insert_fields.append(column_name)
        insert_values.append(f'source.data_{column_name}')
    
    # Generate SQL with clustering
    sql = f"""--- query firestore_sync {table_name}_raw table for last 1 hour using timestamp field and do a merge/upsert into a table "{table_name}_deduped"
CREATE TABLE IF NOT EXISTS `viki-env-app-wsky`.`firestore_sync`.`{table_name}_deduped`
(
{',\n'.join(create_fields)}
)
CLUSTER BY app_id, tenant_id, patient_id, modified_at;

MERGE INTO `viki-env-app-wsky`.`firestore_sync`.`{table_name}_deduped` AS target 

USING (
  SELECT * FROM (
    SELECT 
      timestamp,
      event_id,
      document_name,
      operation,
      {',\n      '.join(json_extracts)},
      document_id,
      ROW_NUMBER() OVER (PARTITION BY document_id ORDER BY TIMESTAMP(JSON_EXTRACT_SCALAR(data, '$.modified_at')) DESC) as rn
    FROM `viki-env-app-wsky`.`firestore_sync`.`{table_name}_raw_changelog`
    WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
  ) 
  WHERE rn = 1
) AS source 

ON target.firestore_document_id = source.document_id

WHEN MATCHED AND TIMESTAMP(target.modified_at) < TIMESTAMP(source.data_modified_at) THEN 
  UPDATE SET
{',\n'.join(update_sets)}

WHEN NOT MATCHED THEN 
  INSERT (
    {',\n    '.join(insert_fields)}
  ) 
  VALUES (
    {',\n    '.join(insert_values)}
  );
"""
    
    # Create dedup_sql_template directory if it doesn't exist
    output_dir = Path(__file__).parent.parent / 'dedup_sql_template'
    output_dir.mkdir(exist_ok=True)
    
    # Write SQL file to dedup_sql_template directory
    output_path = output_dir / f'{table_name}_dedup.sql'
    with open(output_path, 'w') as f:
        f.write(sql)
    
    print(f"Generated {output_path}")

def main():
    # Get schema directory
    schema_dir = Path(__file__).parent / 'schemas'
    
    # Process each schema file
    for schema_file in schema_dir.glob('fs-bq-*_schema.json'):
        generate_sql_for_schema(schema_file)

if __name__ == '__main__':
    main()
