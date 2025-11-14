#!/usr/bin/env python3
"""
Local runner for the MedDB Load Automation function.

This script allows you to run the backup loading process locally against real GCP resources.
It simulates the Cloud Function trigger but runs locally with your credentials.

Usage:
    python run_local.py --bucket meddb-dev --file merative/landing/backup.bak
    python run_local.py --bucket meddb-dev --file merative/landing/backup.bak --dry-run
"""

import os
import sys
import argparse
import logging
from typing import Optional

# Add the current directory to Python path to import main
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_environment(project_id: str, instance_id: str, region: str, bucket_name: str):
    """Set up environment variables for the function."""
    os.environ.update({
        'PROJECT_ID': project_id,
        'CLOUDSQL_INSTANCE_ID': instance_id,
        'REGION': region,
        'BUCKET_NAME': bucket_name
    })
    logger.info(f"Environment configured:")
    logger.info(f"  PROJECT_ID: {project_id}")
    logger.info(f"  CLOUDSQL_INSTANCE_ID: {instance_id}")
    logger.info(f"  REGION: {region}")
    logger.info(f"  BUCKET_NAME: {bucket_name}")

def create_mock_cloud_event(bucket_name: str, file_name: str):
    """Create a mock CloudEvent for local testing."""
    class MockCloudEvent:
        def __init__(self, data):
            self.data = data
    
    return MockCloudEvent({
        'bucket': bucket_name,
        'name': file_name
    })

def check_file_exists(bucket_name: str, file_path: str) -> bool:
    """Check if the file exists in the GCS bucket."""
    try:
        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_path)
        return blob.exists()
    except Exception as e:
        logger.error(f"Failed to check if file exists: {e}")
        return False

def list_landing_files(bucket_name: str, prefix: str = "merative/landing/") -> list:
    """List files in the landing directory."""
    try:
        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=prefix)
        files = [blob.name for blob in blobs if not blob.name.endswith('/')]
        return files
    except Exception as e:
        logger.error(f"Failed to list files: {e}")
        return []

def run_backup_processing(bucket_name: str, file_path: str, dry_run: bool = False):
    """Run the backup processing function."""
    logger.info("=" * 60)
    logger.info("MedDB Load Automation - Local Execution")
    logger.info("=" * 60)
    
    if dry_run:
        logger.info("🔍 DRY RUN MODE - No actual changes will be made")
    else:
        logger.info("🚀 LIVE MODE - Real changes will be made to GCP resources")
    
    logger.info(f"Processing file: gs://{bucket_name}/{file_path}")
    
    # Check if file exists
    if not check_file_exists(bucket_name, file_path):
        logger.error(f"❌ File does not exist: gs://{bucket_name}/{file_path}")
        return False
    
    logger.info("✅ File exists in GCS bucket")
    
    # Import and run the main function
    try:
        from main import process_backup_file, extract_database_name_from_path
        
        # Extract database name for validation
        try:
            database_name = extract_database_name_from_path(file_path)
            logger.info(f"📊 Target database: {database_name}")
        except ValueError as e:
            logger.error(f"❌ Invalid file path: {e}")
            return False
        
        if dry_run:
            logger.info("🔍 DRY RUN: Would process the following:")
            logger.info(f"  - Create database '{database_name}' if not exists")
            logger.info(f"  - Restore backup from gs://{bucket_name}/{file_path}")
            logger.info(f"  - Move file to {file_path.replace('/landing/', '/landing-archive/')}")
            logger.info("🔍 DRY RUN: No actual changes made")
            return True
        
        # Create mock event and process
        mock_event = create_mock_cloud_event(bucket_name, file_path)
        
        logger.info("🔄 Starting backup processing...")
        process_backup_file(mock_event)
        
        logger.info("✅ Backup processing completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Backup processing failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Run MedDB Load Automation locally')
    parser.add_argument('--bucket', required=True, help='GCS bucket name (e.g., meddb-dev)')
    parser.add_argument('--file', required=True, help='File path in bucket (e.g., merative/landing/backup.bak)')
    parser.add_argument('--project-id', help='GCP project ID (default: from gcloud config)')
    parser.add_argument('--instance-id', help='Cloud SQL instance ID (default: viki-sqlserver-meddb-dev)')
    parser.add_argument('--region', default='us-east4', help='GCP region (default: us-east4)')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode - no actual changes')
    parser.add_argument('--list-files', action='store_true', help='List files in landing directory')
    
    args = parser.parse_args()
    
    # Get project ID from gcloud config if not provided
    if not args.project_id:
        try:
            import subprocess
            result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                                  capture_output=True, text=True, check=True)
            args.project_id = result.stdout.strip()
        except Exception as e:
            logger.error(f"Failed to get project ID from gcloud config: {e}")
            logger.error("Please provide --project-id or run 'gcloud config set project YOUR_PROJECT_ID'")
            return 1
    
    # Default instance ID
    if not args.instance_id:
        args.instance_id = f"viki-sqlserver-meddb-{args.bucket.split('-')[-1]}"  # Extract env from bucket name
    
    # Set up environment
    setup_environment(args.project_id, args.instance_id, args.region, args.bucket)
    
    # List files if requested
    if args.list_files:
        logger.info(f"📁 Files in gs://{args.bucket}/merative/landing/:")
        files = list_landing_files(args.bucket)
        if files:
            for file in files:
                logger.info(f"  - {file}")
        else:
            logger.info("  No files found")
        return 0
    
    # Validate authentication
    try:
        from google.auth import default
        credentials, project = default()
        logger.info(f"🔐 Authenticated as project: {project}")
        
        # Get service account email if available
        if hasattr(credentials, 'service_account_email'):
            logger.info(f"🔐 Service account email: {credentials.service_account_email}")
        elif hasattr(credentials, '_service_account_email'):
            logger.info(f"🔐 Service account email: {credentials._service_account_email}")
        else:
            logger.info(f"🔐 Using user credentials (not service account)")
            
    except Exception as e:
        logger.error(f"❌ Authentication failed: {e}")
        logger.error("Please run: gcloud auth application-default login")
        return 1
    
    # Run backup processing
    success = run_backup_processing(args.bucket, args.file, args.dry_run)
    
    if success:
        logger.info("=" * 60)
        logger.info("✅ Local execution completed successfully!")
        if not args.dry_run:
            logger.info("💡 Next steps:")
            logger.info("  1. Check Cloud SQL console for import operation status")
            logger.info("  2. Verify database was created/updated")
            logger.info(f"  3. Confirm file was moved to landing-archive")
        logger.info("=" * 60)
        return 0
    else:
        logger.error("=" * 60)
        logger.error("❌ Local execution failed!")
        logger.error("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
