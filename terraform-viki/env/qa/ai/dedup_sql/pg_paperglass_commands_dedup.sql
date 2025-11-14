--- query firestore_sync pg_paperglass_commands_raw table for last 1 hour using timestamp field and do a merge/upsert into a table "pg_paperglass_commands_deduped"
CREATE TABLE IF NOT EXISTS `viki-qa-app-wsky`.`firestore_sync`.`pg_paperglass_commands_deduped`
(
  `firestore_document_id` STRING,
  `modified_at` TIMESTAMP,
  `app_id` STRING,
  `created_by` STRING,
  `cross_transaction_error_strict_mode` BOOLEAN,
  `document_id` STRING,
  `execution_id` STRING,
  `force_new_instance` BOOLEAN,
  `id` STRING,
  `idempotent_key` STRING,
  `modified_by` STRING,
  `patient_id` STRING,
  `tenant_id` STRING,
  `token` STRING,
  `type` STRING
)
CLUSTER BY app_id, tenant_id, patient_id, modified_at;

MERGE INTO `viki-qa-app-wsky`.`firestore_sync`.`pg_paperglass_commands_deduped` AS target 

USING (
  SELECT * FROM (
    SELECT 
      timestamp,
      event_id,
      document_name,
      operation,
      JSON_EXTRACT_SCALAR(data, '$.app_id') as data_app_id,
      JSON_EXTRACT_SCALAR(data, '$.created_by') as data_created_by,
      CAST(JSON_EXTRACT(data, '$.cross_transaction_error_strict_mode') AS BOOLEAN) as data_cross_transaction_error_strict_mode,
      JSON_EXTRACT_SCALAR(data, '$.document_id') as data_document_id,
      JSON_EXTRACT_SCALAR(data, '$.execution_id') as data_execution_id,
      CAST(JSON_EXTRACT(data, '$.force_new_instance') AS BOOLEAN) as data_force_new_instance,
      JSON_EXTRACT_SCALAR(data, '$.id') as data_id,
      JSON_EXTRACT_SCALAR(data, '$.idempotent_key') as data_idempotent_key,
      JSON_EXTRACT_SCALAR(data, '$.modified_by') as data_modified_by,
      JSON_EXTRACT_SCALAR(data, '$.patient_id') as data_patient_id,
      JSON_EXTRACT_SCALAR(data, '$.tenant_id') as data_tenant_id,
      JSON_EXTRACT_SCALAR(data, '$.token') as data_token,
      JSON_EXTRACT_SCALAR(data, '$.type') as data_type,
      document_id,
      ROW_NUMBER() OVER (PARTITION BY document_id ORDER BY timestamp DESC) as rn
    FROM `viki-qa-app-wsky`.`firestore_sync`.`pg_paperglass_commands_raw_changelog`
    WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
  ) 
  WHERE rn = 1
) AS source 

ON target.firestore_document_id = source.document_id

WHEN MATCHED AND TIMESTAMP(target.modified_at) < TIMESTAMP(source.data_modified_at) THEN 
  UPDATE SET
      target.app_id = source.data_app_id,
      target.created_by = source.data_created_by,
      target.cross_transaction_error_strict_mode = source.data_cross_transaction_error_strict_mode,
      target.document_id = source.data_document_id,
      target.execution_id = source.data_execution_id,
      target.force_new_instance = source.data_force_new_instance,
      target.id = source.data_id,
      target.idempotent_key = source.data_idempotent_key,
      target.modified_by = source.data_modified_by,
      target.patient_id = source.data_patient_id,
      target.tenant_id = source.data_tenant_id,
      target.token = source.data_token,
      target.type = source.data_type

WHEN NOT MATCHED THEN 
  INSERT (
    firestore_document_id,
    app_id,
    created_by,
    cross_transaction_error_strict_mode,
    document_id,
    execution_id,
    force_new_instance,
    id,
    idempotent_key,
    modified_by,
    patient_id,
    tenant_id,
    token,
    type
  ) 
  VALUES (
    document_id,
    source.data_app_id,
    source.data_created_by,
    source.data_cross_transaction_error_strict_mode,
    source.data_document_id,
    source.data_execution_id,
    source.data_force_new_instance,
    source.data_id,
    source.data_idempotent_key,
    source.data_modified_by,
    source.data_patient_id,
    source.data_tenant_id,
    source.data_token,
    source.data_type
  );
