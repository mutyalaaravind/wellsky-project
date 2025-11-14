--- query firestore_sync pg_paperglass_classified_pages_raw table for last 1 hour using timestamp field and do a merge/upsert into a table "pg_paperglass_classified_pages_deduped"
CREATE TABLE IF NOT EXISTS `viki-env-app-wsky`.`firestore_sync`.`pg_paperglass_classified_pages_deduped`
(
  `firestore_document_id` STRING,
  `app_id` STRING,
  `created_at` STRING,
  `created_by` STRING,
  `document_id` STRING,
  `document_operation_instance_id` STRING,
  `execution_id` STRING,
  `id` STRING,
  `labels` ARRAY<STRUCT<data STRING>>,
  `modified_at` STRING,
  `modified_by` STRING,
  `page_id` STRING,
  `page_number` INTEGER,
  `page_text` STRING,
  `patient_id` STRING,
  `tenant_id` STRING
)
CLUSTER BY app_id, tenant_id, patient_id, modified_at;

MERGE INTO `viki-env-app-wsky`.`firestore_sync`.`pg_paperglass_classified_pages_deduped` AS target 

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
      JSON_EXTRACT_SCALAR(data, '$.id') as data_id,
      ARRAY(SELECT STRUCT(med as data) FROM UNNEST(JSON_EXTRACT_ARRAY(data, '$.labels')) as med) as data_labels,
      JSON_EXTRACT_SCALAR(data, '$.modified_at') as data_modified_at,
      JSON_EXTRACT_SCALAR(data, '$.modified_by') as data_modified_by,
      JSON_EXTRACT_SCALAR(data, '$.page_id') as data_page_id,
      CAST(JSON_EXTRACT(data, '$.page_number') AS INT64) as data_page_number,
      JSON_EXTRACT_SCALAR(data, '$.page_text') as data_page_text,
      JSON_EXTRACT_SCALAR(data, '$.patient_id') as data_patient_id,
      JSON_EXTRACT_SCALAR(data, '$.tenant_id') as data_tenant_id,
      document_id,
      ROW_NUMBER() OVER (PARTITION BY document_id ORDER BY timestamp DESC) as rn
    FROM `viki-env-app-wsky`.`firestore_sync`.`pg_paperglass_classified_pages_raw_changelog`
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
      target.id = source.data_id,
      target.labels = source.data_labels,
      target.modified_at = source.data_modified_at,
      target.modified_by = source.data_modified_by,
      target.page_id = source.data_page_id,
      target.page_number = source.data_page_number,
      target.page_text = source.data_page_text,
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
    id,
    labels,
    modified_at,
    modified_by,
    page_id,
    page_number,
    page_text,
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
    source.data_id,
    source.data_labels,
    source.data_modified_at,
    source.data_modified_by,
    source.data_page_id,
    source.data_page_number,
    source.data_page_text,
    source.data_patient_id,
    source.data_tenant_id
  );
