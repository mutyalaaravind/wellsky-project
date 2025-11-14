--- query firestore_sync pg_paperglass_document_operation_instance_raw table for last 1 hour using timestamp field and do a merge/upsert into a table "pg_paperglass_document_operation_instance_deduped"
CREATE TABLE IF NOT EXISTS `viki-stage-app-wsky`.`firestore_sync`.`pg_paperglass_document_operation_instance_deduped`
(
  `firestore_document_id` STRING,
  `app_id` STRING,
  `created_at` STRING,
  `created_by` STRING,
  `document_id` STRING,
  `document_operation_definition_id` STRING,
  `document_operation_instance_id` STRING,
  `end_date` STRING,
  `execution_id` STRING,
  `id` STRING,
  `modified_at` STRING,
  `modified_by` STRING,
  `patient_id` STRING,
  `priority` STRING,
  `start_date` STRING,
  `status` STRING,
  `tenant_id` STRING
)
CLUSTER BY app_id, tenant_id, patient_id, modified_at;

MERGE INTO `viki-stage-app-wsky`.`firestore_sync`.`pg_paperglass_document_operation_instance_deduped` AS target 

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
      JSON_EXTRACT_SCALAR(data, '$.document_id') as data_document_id,
      JSON_EXTRACT_SCALAR(data, '$.document_operation_definition_id') as data_document_operation_definition_id,
      JSON_EXTRACT_SCALAR(data, '$.document_operation_instance_id') as data_document_operation_instance_id,
      JSON_EXTRACT_SCALAR(data, '$.end_date') as data_end_date,
      JSON_EXTRACT_SCALAR(data, '$.execution_id') as data_execution_id,
      JSON_EXTRACT_SCALAR(data, '$.id') as data_id,
      JSON_EXTRACT_SCALAR(data, '$.modified_at') as data_modified_at,
      JSON_EXTRACT_SCALAR(data, '$.modified_by') as data_modified_by,
      JSON_EXTRACT_SCALAR(data, '$.patient_id') as data_patient_id,
      JSON_EXTRACT_SCALAR(data, '$.priority') as data_priority,
      JSON_EXTRACT_SCALAR(data, '$.start_date') as data_start_date,
      JSON_EXTRACT_SCALAR(data, '$.status') as data_status,
      JSON_EXTRACT_SCALAR(data, '$.tenant_id') as data_tenant_id,
      document_id,
      ROW_NUMBER() OVER (PARTITION BY document_id ORDER BY timestamp DESC) as rn
    FROM `viki-stage-app-wsky`.`firestore_sync`.`pg_paperglass_document_operation_instance_raw_changelog`
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
      target.document_id = source.data_document_id,
      target.document_operation_definition_id = source.data_document_operation_definition_id,
      target.document_operation_instance_id = source.data_document_operation_instance_id,
      target.end_date = source.data_end_date,
      target.execution_id = source.data_execution_id,
      target.id = source.data_id,
      target.modified_at = source.data_modified_at,
      target.modified_by = source.data_modified_by,
      target.patient_id = source.data_patient_id,
      target.priority = source.data_priority,
      target.start_date = source.data_start_date,
      target.status = source.data_status,
      target.tenant_id = source.data_tenant_id

WHEN NOT MATCHED THEN 
  INSERT (
    firestore_document_id,
    app_id,
    created_at,
    created_by,
    document_id,
    document_operation_definition_id,
    document_operation_instance_id,
    end_date,
    execution_id,
    id,
    modified_at,
    modified_by,
    patient_id,
    priority,
    start_date,
    status,
    tenant_id
  ) 
  VALUES (
    document_id,
    source.data_app_id,
    source.data_created_at,
    source.data_created_by,
    source.data_document_id,
    source.data_document_operation_definition_id,
    source.data_document_operation_instance_id,
    source.data_end_date,
    source.data_execution_id,
    source.data_id,
    source.data_modified_at,
    source.data_modified_by,
    source.data_patient_id,
    source.data_priority,
    source.data_start_date,
    source.data_status,
    source.data_tenant_id
  );
