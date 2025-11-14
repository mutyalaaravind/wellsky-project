--- query firestore_sync pg_paperglass_page_operation_raw table for last 1 hour using timestamp field and do a merge/upsert into a table "pg_paperglass_page_operation_deduped"
CREATE TABLE IF NOT EXISTS `viki-prod-app-wsky`.`firestore_sync`.`pg_paperglass_page_operation_deduped`
(
  `firestore_document_id` STRING,
  `app_id` STRING,
  `created_at` STRING,
  `created_by` STRING,
  `document_id` STRING,
  `document_operation_instance_id` STRING,
  `execution_id` STRING,
  `extraction_status` STRING,
  `extraction_type` STRING,
  `id` STRING,
  `modified_at` STRING,
  `modified_by` STRING,
  `page_id` STRING,
  `page_number` INTEGER,
  `patient_id` STRING,
  `tenant_id` STRING
)
CLUSTER BY app_id, tenant_id, patient_id, modified_at;

MERGE INTO `viki-prod-app-wsky`.`firestore_sync`.`pg_paperglass_page_operation_deduped` AS target 

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
      JSON_EXTRACT_SCALAR(data, '$.document_operation_instance_id') as data_document_operation_instance_id,
      JSON_EXTRACT_SCALAR(data, '$.execution_id') as data_execution_id,
      JSON_EXTRACT_SCALAR(data, '$.extraction_status') as data_extraction_status,
      JSON_EXTRACT_SCALAR(data, '$.extraction_type') as data_extraction_type,
      JSON_EXTRACT_SCALAR(data, '$.id') as data_id,
      JSON_EXTRACT_SCALAR(data, '$.modified_at') as data_modified_at,
      JSON_EXTRACT_SCALAR(data, '$.modified_by') as data_modified_by,
      JSON_EXTRACT_SCALAR(data, '$.page_id') as data_page_id,
      CAST(JSON_EXTRACT(data, '$.page_number') AS INT64) as data_page_number,
      JSON_EXTRACT_SCALAR(data, '$.patient_id') as data_patient_id,
      JSON_EXTRACT_SCALAR(data, '$.tenant_id') as data_tenant_id,
      document_id,
      ROW_NUMBER() OVER (PARTITION BY document_id ORDER BY timestamp DESC) as rn
    FROM `viki-prod-app-wsky`.`firestore_sync`.`pg_paperglass_page_operation_raw_changelog`
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
      target.document_operation_instance_id = source.data_document_operation_instance_id,
      target.execution_id = source.data_execution_id,
      target.extraction_status = source.data_extraction_status,
      target.extraction_type = source.data_extraction_type,
      target.id = source.data_id,
      target.modified_at = source.data_modified_at,
      target.modified_by = source.data_modified_by,
      target.page_id = source.data_page_id,
      target.page_number = source.data_page_number,
      target.patient_id = source.data_patient_id,
      target.tenant_id = source.data_tenant_id

WHEN NOT MATCHED THEN 
  INSERT (
    firestore_document_id,
    app_id,
    created_at,
    created_by,
    document_id,
    document_operation_instance_id,
    execution_id,
    extraction_status,
    extraction_type,
    id,
    modified_at,
    modified_by,
    page_id,
    page_number,
    patient_id,
    tenant_id
  ) 
  VALUES (
    document_id,
    source.data_app_id,
    source.data_created_at,
    source.data_created_by,
    source.data_document_id,
    source.data_document_operation_instance_id,
    source.data_execution_id,
    source.data_extraction_status,
    source.data_extraction_type,
    source.data_id,
    source.data_modified_at,
    source.data_modified_by,
    source.data_page_id,
    source.data_page_number,
    source.data_patient_id,
    source.data_tenant_id
  );
