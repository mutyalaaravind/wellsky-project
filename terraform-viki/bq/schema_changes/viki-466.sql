DECLARE column_exists INT64;

-- Check if the column exists
SET column_exists = (
  SELECT COUNT(*) 
  FROM `firestore_sync`.INFORMATION_SCHEMA.COLUMNS 
  WHERE table_name = 'pg_documents_deduped' 
    AND column_name = 'operation_status'
);

-- Add the column if it does not exist
IF column_exists = 0 THEN
  ALTER TABLE `viki-env-app-wsky.firestore_sync.pg_documents_deduped`
  ADD COLUMN `operation_status` STRING;
END IF;

-- Repeat for other columns

SET column_exists = (
  SELECT COUNT(*) 
  FROM `firestore_sync`.INFORMATION_SCHEMA.COLUMNS 
  WHERE table_name = 'pg_documents_deduped' 
    AND column_name = 'medication_extraction_status'
);

IF column_exists = 0 THEN
  ALTER TABLE `viki-env-app-wsky.firestore_sync.pg_documents_deduped`
  ADD COLUMN `medication_extraction_status` STRING;
END IF;

SET column_exists = (
  SELECT COUNT(*) 
  FROM `firestore_sync`.INFORMATION_SCHEMA.COLUMNS 
  WHERE table_name = 'pg_documents_deduped' 
    AND column_name = 'medication_extraction_start_time'
);

IF column_exists = 0 THEN
  ALTER TABLE `viki-env-app-wsky.firestore_sync.pg_documents_deduped`
  ADD COLUMN `medication_extraction_start_time` STRING;
END IF;

SET column_exists = (
  SELECT COUNT(*) 
  FROM `firestore_sync`.INFORMATION_SCHEMA.COLUMNS 
  WHERE table_name = 'pg_documents_deduped' 
    AND column_name = 'medication_extraction_end_time'
);

IF column_exists = 0 THEN
  ALTER TABLE `viki-env-app-wsky.firestore_sync.pg_documents_deduped`
  ADD COLUMN `medication_extraction_end_time` STRING;
END IF;

SET column_exists = (
  SELECT COUNT(*) 
  FROM `firestore_sync`.INFORMATION_SCHEMA.COLUMNS 
  WHERE table_name = 'pg_documents_deduped' 
    AND column_name = 'medication_extraction_orchestration_engine_version'
);

IF column_exists = 0 THEN
  ALTER TABLE `viki-env-app-wsky.firestore_sync.pg_documents_deduped`
  ADD COLUMN `medication_extraction_orchestration_engine_version` STRING;
END IF;

