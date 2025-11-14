#!/usr/bin/env python3
"""
Local testing script for the MedDB Load Automation function.

This script simulates the Cloud Function behavior locally for testing purposes.
It allows you to test the function logic without deploying to GCP.

Usage:
    python test_local.py [--mock-mode] [--test-file path/to/test.bak]
"""

import os
import sys
import argparse
import logging
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Add the current directory to Python path to import main
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_mock_cloud_event(bucket_name: str, file_name: str) -> Mock:
    """Create a mock CloudEvent for testing."""
    mock_event = Mock()
    mock_event.data = {
        'bucket': bucket_name,
        'name': file_name
    }
    return mock_event

def mock_gcp_services():
    """Mock all GCP service calls for local testing."""
    
    # Mock Secret Manager
    mock_secret_client = Mock()
    mock_secret_response = Mock()
    mock_secret_response.payload.data.decode.return_value = "mock_password"
    mock_secret_client.access_secret_version.return_value = mock_secret_response
    
    # Mock Storage Client
    mock_storage_client = Mock()
    mock_bucket = Mock()
    mock_source_blob = Mock()
    mock_destination_blob = Mock()
    
    mock_storage_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_source_blob
    mock_bucket.copy_blob.return_value = mock_destination_blob
    
    # Mock SQL Clients
    mock_sql_instances_client = Mock()
    mock_sql_databases_client = Mock()
    
    # Mock database list response
    mock_db_list_response = Mock()
    mock_db_list_response.items = [Mock(name='existing_db')]
    mock_sql_databases_client.list.return_value = mock_db_list_response
    
    # Mock operation responses
    mock_operation = Mock()
    mock_operation.name = "mock_operation_123"
    mock_sql_instances_client.import_.return_value = mock_operation
    mock_sql_databases_client.insert.return_value = mock_operation
    
    return {
        'secret_client': mock_secret_client,
        'storage_client': mock_storage_client,
        'sql_instances_client': mock_sql_instances_client,
        'sql_databases_client': mock_sql_databases_client,
        'bucket': mock_bucket,
        'source_blob': mock_source_blob
    }

def test_extract_database_name():
    """Test the database name extraction logic."""
    from main import extract_database_name_from_path
    
    logger.info("Testing database name extraction...")
    
    test_cases = [
        ("merative/landing/backup.bak", "merative"),
        ("medispan/landing/test_backup.bak", "medispan"),
        ("custom_db/landing/file.bak", "custom_db"),
    ]
    
    for file_path, expected_db_name in test_cases:
        try:
            result = extract_database_name_from_path(file_path)
            assert result == expected_db_name, f"Expected {expected_db_name}, got {result}"
            logger.info(f"✓ {file_path} -> {result}")
        except Exception as e:
            logger.error(f"✗ {file_path} -> Error: {e}")
    
    # Test invalid paths
    invalid_paths = [
        "invalid/path/file.bak",
        "merative/file.bak",
        "file.bak"
    ]
    
    for invalid_path in invalid_paths:
        try:
            extract_database_name_from_path(invalid_path)
            logger.error(f"✗ {invalid_path} should have failed but didn't")
        except ValueError:
            logger.info(f"✓ {invalid_path} correctly rejected")
        except Exception as e:
            logger.error(f"✗ {invalid_path} -> Unexpected error: {e}")

def test_function_with_mock_event(mock_mode: bool = True):
    """Test the main function with a mock event."""
    logger.info("Testing main function with mock event...")
    
    # Set up environment variables
    os.environ.update({
        'PROJECT_ID': 'test-project',
        'CLOUDSQL_INSTANCE_ID': 'test-instance',
        'REGION': 'us-east4',
        'BUCKET_NAME': 'meddb-dev'
    })
    
    if mock_mode:
        mocks = mock_gcp_services()
        
        with patch('main.secretmanager.SecretManagerServiceClient', return_value=mocks['secret_client']), \
             patch('main.storage.Client', return_value=mocks['storage_client']), \
             patch('main.discovery.build', return_value=mocks['sql_instances_client']), \
             patch('main.default', return_value=(None, None)):
            
            from main import process_backup_file
            
            # Test with valid file
            test_event = create_mock_cloud_event('meddb-dev', 'merative/landing/test_backup.bak')
            
            try:
                process_backup_file(test_event)
                logger.info("✓ Function executed successfully with valid file")
            except Exception as e:
                logger.error(f"✗ Function failed with valid file: {e}")
            
            # Test with invalid file path
            test_event_invalid = create_mock_cloud_event('meddb-dev', 'invalid/path/test.bak')
            
            try:
                process_backup_file(test_event_invalid)
                logger.info("✓ Function handled invalid file path correctly")
            except Exception as e:
                logger.error(f"✗ Function failed with invalid file path: {e}")
    else:
        logger.warning("Real mode testing requires actual GCP credentials and resources")
        logger.info("To test with real GCP services, ensure you have:")
        logger.info("1. Valid GCP credentials (gcloud auth application-default login)")
        logger.info("2. Cloud SQL instance running")
        logger.info("3. Storage bucket exists")
        logger.info("4. Proper IAM permissions")

def test_individual_functions():
    """Test individual functions in isolation."""
    logger.info("Testing individual functions...")
    
    # Test database name extraction
    test_extract_database_name()
    
    # Test with mocked services
    mocks = mock_gcp_services()
    
    with patch('main.secretmanager.SecretManagerServiceClient', return_value=mocks['secret_client']):
        from main import get_secret
        try:
            secret = get_secret('test-secret')
            logger.info(f"✓ get_secret returned: {secret}")
        except Exception as e:
            logger.error(f"✗ get_secret failed: {e}")
    
    with patch('main.storage.Client', return_value=mocks['storage_client']):
        from main import move_file_to_archive
        try:
            move_file_to_archive('test-bucket', 'merative/landing/test.bak', 'merative')
            logger.info("✓ move_file_to_archive executed successfully")
        except Exception as e:
            logger.error(f"✗ move_file_to_archive failed: {e}")

def main():
    """Main testing function."""
    parser = argparse.ArgumentParser(description='Test MedDB Load Automation function locally')
    parser.add_argument('--mock-mode', action='store_true', default=True,
                       help='Use mock GCP services (default: True)')
    parser.add_argument('--real-mode', action='store_true',
                       help='Use real GCP services (requires credentials)')
    parser.add_argument('--test-file', type=str,
                       help='Specific test file path to simulate')
    
    args = parser.parse_args()
    
    # If real-mode is specified, disable mock-mode
    if args.real_mode:
        args.mock_mode = False
    
    logger.info("=" * 60)
    logger.info("MedDB Load Automation - Local Testing")
    logger.info("=" * 60)
    
    if args.mock_mode:
        logger.info("Running in MOCK mode (safe for local testing)")
    else:
        logger.info("Running in REAL mode (requires GCP credentials)")
    
    # Test individual functions
    test_individual_functions()
    
    # Test main function
    test_function_with_mock_event(args.mock_mode)
    
    # Test with custom file if provided
    if args.test_file:
        logger.info(f"Testing with custom file: {args.test_file}")
        if args.mock_mode:
            mocks = mock_gcp_services()
            with patch('main.secretmanager.SecretManagerServiceClient', return_value=mocks['secret_client']), \
                 patch('main.storage.Client', return_value=mocks['storage_client']), \
                 patch('main.discovery.build', return_value=mocks['sql_instances_client']), \
                 patch('main.default', return_value=(None, None)):
                
                from main import process_backup_file
                test_event = create_mock_cloud_event('meddb-dev', args.test_file)
                
                try:
                    process_backup_file(test_event)
                    logger.info(f"✓ Custom file test successful: {args.test_file}")
                except Exception as e:
                    logger.error(f"✗ Custom file test failed: {e}")
    
    logger.info("=" * 60)
    logger.info("Testing completed!")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
