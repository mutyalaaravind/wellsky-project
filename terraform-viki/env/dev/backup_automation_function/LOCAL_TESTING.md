# Local Testing Guide for MedDB Load Automation

This guide explains how to test the backup loading functionality locally before deploying to the cloud.

## Prerequisites

1. **GCP Authentication**
   ```bash
   gcloud auth application-default login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Python Dependencies**
   ```bash
   cd env/dev/backup_automation_function
   uv pip install -r test_requirements.txt
   ```

3. **Cloud SQL Instance Running**
   - Ensure your Cloud SQL instance `viki-sqlserver-meddb-dev` is running
   - Verify you have the necessary IAM permissions

## Usage

### 1. List Files in Landing Directory

```bash
python run_local.py --bucket meddb-dev --list-files
```

This will show you what backup files are currently in the `merative/landing/` directory.

### 2. Dry Run (Recommended First)

```bash
python run_local.py --bucket meddb-dev --file merative/landing/your_backup.bak --dry-run
```

This will:
- ✅ Validate the file exists in GCS
- ✅ Extract the database name from the path
- ✅ Show what operations would be performed
- ❌ **NOT** make any actual changes

### 3. Live Run (Real Processing)

```bash
python run_local.py --bucket meddb-dev --file merative/landing/your_backup.bak
```

This will:
- ✅ Check if the file exists in GCS
- ✅ Create the database if it doesn't exist
- ✅ Start the backup restoration to Cloud SQL
- ✅ Move the file to the archive folder

### 4. Custom Configuration

```bash
python run_local.py \
  --bucket meddb-dev \
  --file merative/landing/backup.bak \
  --project-id your-project-id \
  --instance-id your-instance-id \
  --region us-east4
```

## Example Workflow

### Step 1: Upload a Test Backup File

```bash
# Upload your backup file to the landing directory
gsutil cp /path/to/your/backup.bak gs://meddb-dev/merative/landing/
```

### Step 2: List Files to Confirm Upload

```bash
python run_local.py --bucket meddb-dev --list-files
```

Expected output:
```
📁 Files in gs://meddb-dev/merative/landing/:
  - merative/landing/backup.bak
```

### Step 3: Test with Dry Run

```bash
python run_local.py --bucket meddb-dev --file merative/landing/backup.bak --dry-run
```

Expected output:
```
============================================================
MedDB Load Automation - Local Execution
============================================================
🔍 DRY RUN MODE - No actual changes will be made
Processing file: gs://meddb-dev/merative/landing/backup.bak
✅ File exists in GCS bucket
📊 Target database: merative
🔍 DRY RUN: Would process the following:
  - Create database 'merative' if not exists
  - Restore backup from gs://meddb-dev/merative/landing/backup.bak
  - Move file to merative/landing-archive/backup.bak
🔍 DRY RUN: No actual changes made
============================================================
✅ Local execution completed successfully!
============================================================
```

### Step 4: Run Live Processing

```bash
python run_local.py --bucket meddb-dev --file merative/landing/backup.bak
```

Expected output:
```
============================================================
MedDB Load Automation - Local Execution
============================================================
🚀 LIVE MODE - Real changes will be made to GCP resources
Processing file: gs://meddb-dev/merative/landing/backup.bak
✅ File exists in GCS bucket
📊 Target database: merative
🔄 Starting backup processing...
Processing file: merative/landing/backup.bak in bucket: meddb-dev
Extracted database name: merative
Database creation operation started: operation-123456789
Import operation started: operation-987654321
File moved from merative/landing/backup.bak to merative/landing-archive/backup.bak
Successfully processed backup file merative/landing/backup.bak. Restore operation: operation-987654321
✅ Backup processing completed successfully!
============================================================
✅ Local execution completed successfully!
💡 Next steps:
  1. Check Cloud SQL console for import operation status
  2. Verify database was created/updated
  3. Confirm file was moved to landing-archive
============================================================
```

## Verification Steps

### 1. Check Cloud SQL Operations

Go to the Cloud SQL console and check the "Operations" tab to see the import progress.

### 2. Verify Database Creation

Connect to your Cloud SQL instance and run:
```sql
SELECT name, create_date FROM sys.databases WHERE name = 'merative';
```

### 3. Check File Movement

```bash
# Verify file was moved to archive
gsutil ls gs://meddb-dev/merative/landing-archive/

# Verify file was removed from landing
gsutil ls gs://meddb-dev/merative/landing/
```

## Troubleshooting

### Authentication Issues

```bash
# Re-authenticate if needed
gcloud auth application-default login

# Check current project
gcloud config get-value project
```

### File Not Found

```bash
# List all files in bucket
gsutil ls -r gs://meddb-dev/

# Check if bucket exists
gsutil ls gs://meddb-dev/
```

### Permission Issues

Ensure your account has the following roles:
- `Cloud SQL Admin` (for database operations)
- `Storage Admin` (for file operations)
- `Secret Manager Secret Accessor` (for password access)

### Cloud SQL Instance Issues

```bash
# Check if instance is running
gcloud sql instances describe viki-sqlserver-meddb-dev

# Check instance status
gcloud sql instances list
```

## Testing Different Database Types

The system supports any database type based on the file path:

```bash
# For medispan database
python run_local.py --bucket meddb-dev --file medispan/landing/drugs.bak --dry-run

# For custom database
python run_local.py --bucket meddb-dev --file custom_db/landing/data.bak --dry-run
```

The database name will be extracted from the first part of the path (`medispan`, `custom_db`, etc.).
