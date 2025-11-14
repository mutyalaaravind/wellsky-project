from google.cloud import firestore
import json
from typing import Dict, List, Any
import os
import argparse
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from datetime import datetime
from google.cloud.firestore_v1 import GeoPoint

def initialize_firestore(project_id: str, db_name: str = "(default)"):
    """Initialize Firestore client with project ID and database name"""
    return firestore.Client(project=project_id, database=db_name)

def get_field_type(value: Any) -> str:
    """Determine BigQuery field type from Firestore value"""
    if isinstance(value, bool):
        return "BOOLEAN"
    elif isinstance(value, int):
        return "INTEGER"
    elif isinstance(value, float):
        return "FLOAT"
    elif isinstance(value, str):
        return "STRING"
    elif isinstance(value, dict):
        return "RECORD"
    elif isinstance(value, list):
        if value:
            # Get type of first element for array
            return f"ARRAY<{get_field_type(value[0])}>"
        return "ARRAY<STRING>"  # default to string array if empty
    elif isinstance(value, GeoPoint):
        return "GEOGRAPHY"
    elif isinstance(value, datetime):
        return "TIMESTAMP"
    elif value is None:
        return "STRING"  # default to STRING for null values
    else:
        return "STRING"  # default case

def analyze_document_schema(document_dict: Dict) -> List[Dict[str, str]]:
    """Analyze document fields and generate schema"""
    schema = []
    
    def process_field(field_name: str, field_value: Any, parent_prefix: str = ""):
        full_field_name = f"{parent_prefix}{field_name}" if parent_prefix else field_name
        
        if isinstance(field_value, dict):
            # Handle nested objects
            for nested_name, nested_value in field_value.items():
                process_field(nested_name, nested_value, f"{full_field_name}.")
        else:
            field_type = get_field_type(field_value)
            schema.append({
                "name": full_field_name,
                "type": field_type
            })
    
    for field_name, field_value in document_dict.items():
        process_field(field_name, field_value)
    
    return schema

def get_collection_schema(db: firestore.Client, collection_name: str, sample_size: int = 100) -> List[Dict[str, str]]:
    """Get schema from a Firestore collection"""
    # Get sample documents from collection
    docs = db.collection(collection_name).limit(sample_size).stream()
    
    # Combine schemas from all documents
    all_fields = {}
    for doc in docs:
        doc_dict = doc.to_dict()
        doc_schema = analyze_document_schema(doc_dict)
        
        # Update all_fields with new fields and types
        for field in doc_schema:
            field_name = field["name"]
            field_type = field["type"]
            
            if field_name not in all_fields:
                all_fields[field_name] = field_type
            elif all_fields[field_name] != field_type:
                # If types conflict, use STRING as a safe default
                all_fields[field_name] = "STRING"
    
    # Convert to final schema format
    final_schema = [
        {"name": name, "type": type_}
        for name, type_ in sorted(all_fields.items())
    ]
    
    return final_schema

def main():
    parser = argparse.ArgumentParser(description='Generate BigQuery schema from Firestore collection')
    parser.add_argument('collection', help='Firestore collection name')
    parser.add_argument('--project', help='Google Cloud project ID', required=True)
    parser.add_argument('--db_name', help='Firestore database name', default="(default)")
    parser.add_argument('--output', help='Output JSON file path')
    parser.add_argument('--sample-size', type=int, default=100,
                      help='Number of documents to sample (default: 100)')
    
    args = parser.parse_args()
    
    # Initialize Firestore
    db = initialize_firestore(args.project, args.db_name)
    
    # Get schema
    schema = get_collection_schema(db, args.collection, args.sample_size)
    
    # Output schema
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(schema, f, indent=2)
    else:
        print(json.dumps(schema, indent=2))

if __name__ == "__main__":
    main()
