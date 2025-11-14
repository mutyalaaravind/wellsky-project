--- query firestore_sync pg_medications_medication_profile_raw table for last 1 hour using timestamp field and do a merge/upsert into a table "pg_medications_medication_profile_deduped"
CREATE TABLE IF NOT EXISTS `viki-stage-app-wsky`.`firestore_sync`.`pg_medications_medication_profile_deduped`
(
  `firestore_document_id` STRING,
  `app_id` STRING,
  `created_at` STRING,
  `created_by` STRING,
  `document_operation_instance_id` STRING,
  `execution_id` STRING,
  `id` STRING,
  `medications` ARRAY<STRUCT<data STRING>>,
  `modified_at` STRING,
  `modified_by` STRING,
  `patient_id` STRING,
  `tenant_id` STRING
)
CLUSTER BY app_id, tenant_id, patient_id, modified_at;

MERGE INTO `viki-stage-app-wsky`.`firestore_sync`.`pg_medications_medication_profile_deduped` AS target 

USING (
  SELECT * FROM (
    SELECT 
      timestamp,
      event_id,
      document_name,
      operation,
      JSON_EXTRACT_SCALAR(data, '$.app_id') as data_app_id,
      JSON_EXTRACT_SCALAR(data, '$.created_at') as data_created_at,
      JSON_EXTRACT_SCALAR(data, '$.created_by') as data_created_by,
      JSON_EXTRACT_SCALAR(data, '$.document_operation_instance_id') as data_document_operation_instance_id,
      JSON_EXTRACT_SCALAR(data, '$.execution_id') as data_execution_id,
      JSON_EXTRACT_SCALAR(data, '$.id') as data_id,
      ARRAY(SELECT STRUCT(med as data) FROM UNNEST(JSON_EXTRACT_ARRAY(data, '$.medications')) as med) as data_medications,
      JSON_EXTRACT_SCALAR(data, '$.modified_at') as data_modified_at,
      JSON_EXTRACT_SCALAR(data, '$.modified_by') as data_modified_by,
      JSON_EXTRACT_SCALAR(data, '$.patient_id') as data_patient_id,
      JSON_EXTRACT_SCALAR(data, '$.tenant_id') as data_tenant_id,
      document_id,
      ROW_NUMBER() OVER (PARTITION BY document_id ORDER BY timestamp DESC) as rn
    FROM `viki-stage-app-wsky`.`firestore_sync`.`pg_medications_medication_profile_raw_changelog`
    WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
  ) 
  WHERE rn = 1
) AS source 

ON target.firestore_document_id = source.document_id

WHEN MATCHED AND TIMESTAMP(target.modified_at) < TIMESTAMP(source.data_modified_at) THEN 
  UPDATE SET
      target.app_id = source.data_app_id,
      target.created_at = source.data_created_at,
      target.created_by = source.data_created_by,
      target.document_operation_instance_id = source.data_document_operation_instance_id,
      target.execution_id = source.data_execution_id,
      target.id = source.data_id,
      target.medications = source.data_medications,
      target.modified_at = source.data_modified_at,
      target.modified_by = source.data_modified_by,
      target.patient_id = source.data_patient_id,
      target.tenant_id = source.data_tenant_id

WHEN NOT MATCHED THEN 
  INSERT (
    firestore_document_id,
    app_id,
    created_at,
    created_by,
    document_operation_instance_id,
    execution_id,
    id,
    medications,
    modified_at,
    modified_by,
    patient_id,
    tenant_id
  ) 
  VALUES (
    document_id,
    source.data_app_id,
    source.data_created_at,
    source.data_created_by,
    source.data_document_operation_instance_id,
    source.data_execution_id,
    source.data_id,
    source.data_medications,
    source.data_modified_at,
    source.data_modified_by,
    source.data_patient_id,
    source.data_tenant_id
  );
