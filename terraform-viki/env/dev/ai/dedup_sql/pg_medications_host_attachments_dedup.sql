--- query firestore_sync pg_medications_host_attachments_raw table for last 1 hour using timestamp field and do a merge/upsert into a table "pg_medications_host_attachments_deduped"
CREATE TABLE IF NOT EXISTS `viki-dev-app-wsky`.`firestore_sync`.`pg_medications_host_attachments_deduped`
(
  `firestore_document_id` STRING,
  `app_id` STRING,
  `created_at` STRING,
  `created_by` STRING,
  `document_operation_instance_id` STRING,
  `execution_id` STRING,
  `file_name` STRING,
  `id` STRING,
  `modified_at` STRING,
  `modified_by` STRING,
  `patient_id` STRING,
  `storage_uri` STRING,
  `tenant_id` STRING,
  `token` STRING
)
CLUSTER BY app_id, tenant_id, patient_id, modified_at;

MERGE INTO `viki-dev-app-wsky`.`firestore_sync`.`pg_medications_host_attachments_deduped` AS target 

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
      JSON_EXTRACT_SCALAR(data, '$.file_name') as data_file_name,
      JSON_EXTRACT_SCALAR(data, '$.id') as data_id,
      JSON_EXTRACT_SCALAR(data, '$.modified_at') as data_modified_at,
      JSON_EXTRACT_SCALAR(data, '$.modified_by') as data_modified_by,
      JSON_EXTRACT_SCALAR(data, '$.patient_id') as data_patient_id,
      JSON_EXTRACT_SCALAR(data, '$.storage_uri') as data_storage_uri,
      JSON_EXTRACT_SCALAR(data, '$.tenant_id') as data_tenant_id,
      JSON_EXTRACT_SCALAR(data, '$.token') as data_token,
      document_id,
      ROW_NUMBER() OVER (PARTITION BY document_id ORDER BY timestamp DESC) as rn
    FROM `viki-dev-app-wsky`.`firestore_sync`.`pg_medications_host_attachments_raw_changelog`
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
      target.file_name = source.data_file_name,
      target.id = source.data_id,
      target.modified_at = source.data_modified_at,
      target.modified_by = source.data_modified_by,
      target.patient_id = source.data_patient_id,
      target.storage_uri = source.data_storage_uri,
      target.tenant_id = source.data_tenant_id,
      target.token = source.data_token

WHEN NOT MATCHED THEN 
  INSERT (
    firestore_document_id,
    app_id,
    created_at,
    created_by,
    document_operation_instance_id,
    execution_id,
    file_name,
    id,
    modified_at,
    modified_by,
    patient_id,
    storage_uri,
    tenant_id,
    token
  ) 
  VALUES (
    document_id,
    source.data_app_id,
    source.data_created_at,
    source.data_created_by,
    source.data_document_operation_instance_id,
    source.data_execution_id,
    source.data_file_name,
    source.data_id,
    source.data_modified_at,
    source.data_modified_by,
    source.data_patient_id,
    source.data_storage_uri,
    source.data_tenant_id,
    source.data_token
  );
