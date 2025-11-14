--- query firestore_sync pg_paperglass_events_processed_raw table for last 1 hour using timestamp field and do a merge/upsert into a table "pg_paperglass_events_processed_deduped"
CREATE TABLE IF NOT EXISTS `viki-env-app-wsky`.`firestore_sync`.`pg_paperglass_events_processed_deduped`
(
  `firestore_document_id` STRING,
  `modified_at` TIMESTAMP,
  `app_id` STRING,
  `created` STRING,
  `document_id` STRING,
  `document_operation_definition_id` STRING,
  `document_operation_instance_id` STRING,
  `id` STRING,
  `labels` ARRAY<STRUCT<data STRING>>,
  `page_id` STRING,
  `page_number` INTEGER,
  `patient_id` STRING,
  `storage_uri` STRING,
  `tenant_id` STRING,
  `token` STRING,
  `type` STRING
)
CLUSTER BY app_id, tenant_id, patient_id, modified_at;

MERGE INTO `viki-env-app-wsky`.`firestore_sync`.`pg_paperglass_events_processed_deduped` AS target 

USING (
  SELECT * FROM (
    SELECT 
      timestamp,
      event_id,
      document_name,
      operation,
      JSON_EXTRACT_SCALAR(data, '$.app_id') as data_app_id,
      JSON_EXTRACT_SCALAR(data, '$.created') as data_created,
      JSON_EXTRACT_SCALAR(data, '$.document_id') as data_document_id,
      JSON_EXTRACT_SCALAR(data, '$.document_operation_definition_id') as data_document_operation_definition_id,
      JSON_EXTRACT_SCALAR(data, '$.document_operation_instance_id') as data_document_operation_instance_id,
      JSON_EXTRACT_SCALAR(data, '$.id') as data_id,
      ARRAY(SELECT STRUCT(med as data) FROM UNNEST(JSON_EXTRACT_ARRAY(data, '$.labels')) as med) as data_labels,
      JSON_EXTRACT_SCALAR(data, '$.page_id') as data_page_id,
      CAST(JSON_EXTRACT(data, '$.page_number') AS INT64) as data_page_number,
      JSON_EXTRACT_SCALAR(data, '$.patient_id') as data_patient_id,
      JSON_EXTRACT_SCALAR(data, '$.storage_uri') as data_storage_uri,
      JSON_EXTRACT_SCALAR(data, '$.tenant_id') as data_tenant_id,
      JSON_EXTRACT_SCALAR(data, '$.token') as data_token,
      JSON_EXTRACT_SCALAR(data, '$.type') as data_type,
      document_id,
      ROW_NUMBER() OVER (PARTITION BY document_id ORDER BY timestamp DESC) as rn
    FROM `viki-env-app-wsky`.`firestore_sync`.`pg_paperglass_events_processed_raw_changelog`
    WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
  ) 
  WHERE rn = 1
) AS source 

ON target.firestore_document_id = source.document_id

WHEN MATCHED AND TIMESTAMP(target.modified_at) < TIMESTAMP(source.data_modified_at) THEN 
  UPDATE SET
      target.app_id = source.data_app_id,
      target.created = source.data_created,
      target.document_id = source.data_document_id,
      target.document_operation_definition_id = source.data_document_operation_definition_id,
      target.document_operation_instance_id = source.data_document_operation_instance_id,
      target.id = source.data_id,
      target.labels = source.data_labels,
      target.page_id = source.data_page_id,
      target.page_number = source.data_page_number,
      target.patient_id = source.data_patient_id,
      target.storage_uri = source.data_storage_uri,
      target.tenant_id = source.data_tenant_id,
      target.token = source.data_token,
      target.type = source.data_type

WHEN NOT MATCHED THEN 
  INSERT (
    firestore_document_id,
    app_id,
    created,
    document_id,
    document_operation_definition_id,
    document_operation_instance_id,
    id,
    labels,
    page_id,
    page_number,
    patient_id,
    storage_uri,
    tenant_id,
    token,
    type
  ) 
  VALUES (
    document_id,
    source.data_app_id,
    source.data_created,
    source.data_document_id,
    source.data_document_operation_definition_id,
    source.data_document_operation_instance_id,
    source.data_id,
    source.data_labels,
    source.data_page_id,
    source.data_page_number,
    source.data_patient_id,
    source.data_storage_uri,
    source.data_tenant_id,
    source.data_token,
    source.data_type
  );
