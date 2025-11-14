# MedDB Backup Automation System

## Overview

This system provides automated backup restoration for the MedDB project. It monitors a Google Cloud Storage bucket for backup files and automatically restores them to a Cloud SQL SQL Server instance.

## Architecture

```
GCS Bucket (meddb-dev)
├── merative/
│   ├── landing/           # Drop backup files here
│   └── landing-archive/   # Processed files moved here
└── [other paths for future expansion]

Cloud Function (backup-automation-dev)
├── Triggered by GCS object creation
├── Validates file path
├── Creates database if needed
├── Restores backup to Cloud SQL
└── Archives processed file

Cloud SQL Instance (viki-sqlserver-meddb-dev)
├── SQL Server 2019 Standard
├── Databases created dynamically
└── Backup restoration target
```

## Components

### 1. Infrastructure (Terraform)

**Files:**
- `env/dev/meddb_load_automation.tf` - Main infrastructure
- `env/dev/meddb_load_automation_outputs.tf` - Output values

**Resources Created:**
- GCS bucket: `meddb-dev`
- Cloud Function: `backup-automation-dev`
- Service Account: `backup-automation-sa`
- IAM permissions for automation
- Required API enablement

### 2. Cloud Function

**Files:**
- `env/dev/backup_automation_function/main.py` - Function code
- `env/dev/backup_automation_function/requirements.txt` - Dependencies
- `env/dev/backup_automation_function/README.md` - Function documentation

**Functionality:**
- Monitors GCS bucket for new files in `merative/landing/`
- Extracts database name from file path
- Creates database if it doesn't exist
- Restores SQL Server backup (.bak) files
- Moves processed files to archive folder

### 3. Cloud SQL Integration

**Target Instance:** `viki-sqlserver-meddb-dev`
- SQL Server 2019 Standard
- Configured in `env/dev/cloudsql.tf`
- Databases created dynamically based on file path

## Usage Workflow

### 1. Upload Backup File

Upload your SQL Server backup file to the landing folder:

```bash
gsutil cp your_backup.bak gs://meddb-dev/merative/landing/
```

### 2. Automatic Processing

The system will automatically:

1. **Detect** the new file via Cloud Storage trigger
2. **Validate** the file path format
3. **Extract** database name ("merative" from path)
4. **Create** database if it doesn't exist
5. **Restore** the backup to Cloud SQL
6. **Archive** the file to `merative/landing-archive/`

### 3. Monitor Progress

Monitor the process through:

- **Cloud Functions Console:** Check function execution logs
- **Cloud SQL Console:** Monitor import operations
- **Cloud Storage Console:** Verify file movement to archive

## File Path Convention

The system uses the file path to determine the target database name:

```
Format: {database_name}/landing/{backup_file}
Example: merative/landing/backup_20240118.bak
Result: Database named "merative"
```

## Security

### Service Account Permissions

The `backup-automation-sa` service account has minimal required permissions:

- `roles/cloudsql.admin` - Database operations
- `roles/storage.admin` - File operations
- `roles/secretmanager.secretAccessor` - Password access
- `roles/logging.logWriter` - Function logging

### Secret Management

Database passwords are stored in Google Secret Manager:
- `sqlserver-root-password` - SQL Server root password
- `sqlserver-user-password` - Application user password

## Deployment

### Prerequisites

1. Cloud SQL instance must be running
2. Required APIs must be enabled
3. Terraform state must be properly configured

### Deploy with Terraform

```bash
cd env/dev
terraform init
terraform plan
terraform apply
```

### Verify Deployment

```bash
# Check if bucket exists
gsutil ls gs://meddb-dev/

# Check if function is deployed
gcloud functions list --filter="name:backup-automation-dev"

# Test with a sample file
echo "test" | gsutil cp - gs://meddb-dev/merative/landing/test.txt
```

## Monitoring and Troubleshooting

### Cloud Function Logs

```bash
gcloud functions logs read backup-automation-dev --limit=50
```

### Common Issues

1. **File not processed:**
   - Check file is in correct path: `merative/landing/`
   - Verify function has proper permissions
   - Check function logs for errors

2. **Database creation fails:**
   - Verify Cloud SQL instance is running
   - Check service account has `cloudsql.admin` role
   - Review SQL instance configuration

3. **Backup restoration fails:**
   - Ensure backup file is valid SQL Server .bak format
   - Check Cloud SQL instance has sufficient storage
   - Verify backup file is accessible from Cloud SQL

### Monitoring Queries

```sql
-- Check database creation
SELECT name, create_date FROM sys.databases WHERE name = 'merative';

-- Check recent restore operations
SELECT * FROM msdb.dbo.restorehistory 
WHERE restore_date > DATEADD(day, -1, GETDATE());
```

## Extending the System

### Adding New Database Types

To support additional database types (e.g., "medispan"):

1. Upload files to: `gs://meddb-dev/medispan/landing/`
2. The system will automatically create a "medispan" database
3. No code changes required

### Customizing Processing

To modify the processing logic:

1. Edit `env/dev/backup_automation_function/main.py`
2. Update the function with Terraform:
   ```bash
   terraform apply
   ```

## Cost Considerations

- **Cloud Function:** Pay per invocation and execution time
- **Cloud Storage:** Standard storage costs for backup files
- **Cloud SQL:** Instance running costs (already existing)
- **Data Transfer:** Minimal costs for GCS to Cloud SQL transfers

## Backup and Recovery

- **Function Code:** Stored in Terraform and version control
- **Infrastructure:** Defined as code in Terraform
- **Backup Files:** Archived in `landing-archive/` folders
- **Database Backups:** Cloud SQL automated backups enabled

## Support

For issues or questions:

1. Check function logs in Cloud Console
2. Review this documentation
3. Contact the infrastructure team
4. Create issues in the project repository
