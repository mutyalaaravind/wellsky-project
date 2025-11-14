# MedDB Load Automation

This Cloud Function automates the process of loading backup files from Google Cloud Storage into a Cloud SQL SQL Server instance.

## Overview

The system monitors the GCS bucket `meddb-dev` for new backup files uploaded to the `merative/landing/` path. When a backup file is detected, it:

1. Extracts the database name from the file path (first component: "merative")
2. Creates the database if it doesn't exist
3. Restores the backup file to the Cloud SQL instance
4. Moves the file to the `merative/landing-archive/` path

## File Structure

- `main.py` - Main Cloud Function code
- `requirements.txt` - Python dependencies
- `README.md` - This documentation

## Function Flow

1. **Trigger**: Cloud Storage object finalization event for files in `merative/landing/*`
2. **Validation**: Check if file is in the correct path format
3. **Database Creation**: Create target database if it doesn't exist
4. **Backup Restoration**: Import the .bak file into Cloud SQL
5. **File Archival**: Move processed file to archive folder

## Environment Variables

The function uses these environment variables (set by Terraform):

- `PROJECT_ID` - GCP project ID
- `CLOUDSQL_INSTANCE_ID` - Cloud SQL instance name
- `REGION` - GCP region
- `BUCKET_NAME` - GCS bucket name

## Dependencies

- `google-cloud-storage` - GCS operations
- `google-cloud-sql` - Cloud SQL operations
- `google-cloud-secret-manager` - Secret access
- `functions-framework` - Cloud Functions runtime
- `cloudevents` - Event handling

## Usage

1. Upload a SQL Server backup file (.bak) to: `gs://meddb-dev/merative/landing/`
2. The function will automatically process the file
3. Monitor Cloud Function logs for processing status
4. Processed files will be moved to: `gs://meddb-dev/merative/landing-archive/`

## Error Handling

The function includes comprehensive error handling and logging:

- Invalid file paths are logged and ignored
- Database creation failures are logged and re-raised
- Backup restoration failures are logged and re-raised
- File movement failures are logged and re-raised

## Monitoring

Monitor the function through:

- Cloud Console > Cloud Functions > backup-automation-dev
- Cloud Logging for detailed execution logs
- Cloud SQL operations console for restore progress

## Security

The function uses a dedicated service account with minimal required permissions:

- Cloud SQL Admin (for database operations)
- Storage Admin (for file operations)
- Secret Manager Secret Accessor (for password access)
- Logging Log Writer (for function logs)
