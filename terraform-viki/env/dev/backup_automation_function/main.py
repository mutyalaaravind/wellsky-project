import os
import logging
import json
from typing import Dict, Any
from google.cloud import storage
from google.cloud import secretmanager
import functions_framework
from cloudevents.http import CloudEvent
from googleapiclient import discovery
from google.auth import default

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
PROJECT_ID = os.environ.get('PROJECT_ID')
CLOUDSQL_INSTANCE_ID = os.environ.get('CLOUDSQL_INSTANCE_ID')
REGION = os.environ.get('REGION')
BUCKET_NAME = os.environ.get('BUCKET_NAME')

def get_secret(secret_name: str) -> str:
    """Retrieve secret from Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_name}/versions/latest"
    
    try:
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        logger.error(f"Failed to retrieve secret {secret_name}: {e}")
        raise

def extract_database_name_from_path(file_path: str) -> str:
    """Extract database name from file path and append current date.
    
    Expected path formats: 
    - merative/landing/filename.bak
    - merative/landing-archive/filename.bak
    Database name will be 'merative-YYYYMMDD' (first component after bucket name + date suffix)
    """
    from datetime import datetime
    
    path_parts = file_path.strip('/').split('/')
    if len(path_parts) >= 2 and path_parts[0] and (path_parts[1] == 'landing' or path_parts[1] == 'landing-archive'):
        base_name = path_parts[0]  # Get 'merative'
        date_suffix = datetime.now().strftime('%Y%m%d')  # Get current date as YYYYMMDD
        return f"{base_name}-{date_suffix}"  # Return 'merative-20250718'
    else:
        raise ValueError(f"Invalid file path format: {file_path}. Expected: <db_name>/landing/<filename> or <db_name>/landing-archive/<filename>")

def move_file_to_archive(bucket_name: str, source_path: str, database_name: str) -> None:
    """Move file from landing to landing-archive folder."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    
    # Source blob
    source_blob = bucket.blob(source_path)
    
    # Destination path: replace 'landing' with 'landing-archive'
    destination_path = source_path.replace(f'{database_name}/landing/', f'{database_name}/landing-archive/')
    
    # Copy to archive location
    destination_blob = bucket.copy_blob(source_blob, bucket, destination_path)
    
    # Delete original file
    source_blob.delete()
    
    logger.info(f"File moved from {source_path} to {destination_path}")

def restore_backup_to_cloudsql(file_uri: str, database_name: str) -> str:
    """Restore backup file to Cloud SQL instance."""
    credentials, _ = default()
    service = discovery.build('sqladmin', 'v1', credentials=credentials)
    
    # Create import request for SQL Server BAK file
    import_request = {
        'importContext': {
            'uri': file_uri,
            'database': database_name,
            'fileType': 'BAK'
        }
    }
    
    try:
        # Execute import operation
        operation = service.instances().import_(
            project=PROJECT_ID,
            instance=CLOUDSQL_INSTANCE_ID,
            body=import_request
        ).execute()
        
        logger.info(f"Import operation started: {operation.get('name', 'unknown')}")
        return operation.get('name', 'unknown')
    except Exception as e:
        logger.error(f"Failed to start import operation: {e}")
        raise

def create_database_if_not_exists(database_name: str) -> None:
    """Create database if it doesn't exist."""
    credentials, _ = default()
    service = discovery.build('sqladmin', 'v1', credentials=credentials)
    
    try:
        # Check if database exists
        databases_response = service.databases().list(
            project=PROJECT_ID,
            instance=CLOUDSQL_INSTANCE_ID
        ).execute()
        
        existing_db_names = [db['name'] for db in databases_response.get('items', [])]
        
        if database_name not in existing_db_names:
            # Create database
            database_body = {
                'name': database_name,
                'charset': 'UTF8',
                'collation': 'SQL_Latin1_General_CP1_CI_AS'
            }
            
            operation = service.databases().insert(
                project=PROJECT_ID,
                instance=CLOUDSQL_INSTANCE_ID,
                body=database_body
            ).execute()
            
            logger.info(f"Database creation operation started: {operation.get('name', 'unknown')}")
        else:
            logger.info(f"Database {database_name} already exists")
            
    except Exception as e:
        logger.error(f"Failed to create database {database_name}: {e}")
        raise

def drop_database_if_exists(database_name: str) -> None:
    """Drop database if it exists (for reloading from archive)."""
    credentials, _ = default()
    service = discovery.build('sqladmin', 'v1', credentials=credentials)
    
    try:
        # Check if database exists
        databases_response = service.databases().list(
            project=PROJECT_ID,
            instance=CLOUDSQL_INSTANCE_ID
        ).execute()
        
        existing_db_names = [db['name'] for db in databases_response.get('items', [])]
        
        if database_name in existing_db_names:
            # Drop database
            operation = service.databases().delete(
                project=PROJECT_ID,
                instance=CLOUDSQL_INSTANCE_ID,
                database=database_name
            ).execute()
            
            logger.info(f"Database deletion operation started: {operation.get('name', 'unknown')}")
        else:
            logger.info(f"Database {database_name} does not exist, no need to drop")
            
    except Exception as e:
        logger.error(f"Failed to drop database {database_name}: {e}")
        raise

@functions_framework.cloud_event
def process_backup_file(cloud_event: CloudEvent) -> None:
    """Main function to process backup file uploads."""
    try:
        # Parse the CloudEvent
        data = cloud_event.data
        
        if not data:
            logger.error("No data in cloud event")
            return
            
        bucket_name = data.get('bucket')
        file_name = data.get('name')
        
        if not bucket_name or not file_name:
            logger.error(f"Missing bucket or file name in event data: {data}")
            return
            
        logger.info(f"Processing file: {file_name} in bucket: {bucket_name}")
        
        # Check if file is in a landing or landing-archive path
        is_landing = '/landing/' in file_name
        is_archive = '/landing-archive/' in file_name
        
        if not is_landing and not is_archive:
            logger.info(f"File {file_name} is not in a landing or landing-archive path, ignoring")
            return
            
        # Extract database name from path
        try:
            database_name = extract_database_name_from_path(file_name)
            logger.info(f"Extracted database name: {database_name}")
        except ValueError as e:
            logger.error(f"Failed to extract database name: {e}")
            return
            
        # Construct GCS URI for the backup file
        file_uri = f"gs://{bucket_name}/{file_name}"
        
        # Handle database preparation based on source
        if is_archive:
            # For archive files, drop database and let BAK file recreate it
            logger.info(f"Processing from archive - will drop database {database_name} and let BAK file recreate it")
            drop_database_if_exists(database_name)
            # Don't create database - let the BAK file create it with its internal structure
        else:
            # For landing files, just create if not exists
            create_database_if_not_exists(database_name)
        
        # Restore backup to Cloud SQL
        operation_name = restore_backup_to_cloudsql(file_uri, database_name)
        
        # Only move file to archive if it's from landing (not if it's already in archive)
        if is_landing:
            move_file_to_archive(bucket_name, file_name, database_name)
            logger.info(f"Successfully processed backup file {file_name}. Restore operation: {operation_name}. File moved to archive.")
        else:
            logger.info(f"Successfully processed backup file {file_name} from archive. Restore operation: {operation_name}. File left in archive.")
        
    except Exception as e:
        logger.error(f"Error processing backup file: {e}")
        raise

if __name__ == "__main__":
    # For local testing
    test_event_data = {
        "bucket": "meddb-dev",
        "name": "merative/landing/test_backup.bak"
    }
    
    # Create a mock CloudEvent for testing
    class MockCloudEvent:
        def __init__(self, data):
            self.data = data
    
    mock_event = MockCloudEvent(test_event_data)
    process_backup_file(mock_event)
