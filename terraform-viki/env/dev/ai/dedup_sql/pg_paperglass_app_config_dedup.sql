--- query firestore_sync pg_paperglass_app_config_raw table for last 1 hour using timestamp field and do a merge/upsert into a table "pg_paperglass_app_config_deduped"
CREATE TABLE IF NOT EXISTS `viki-dev-app-wsky`.`firestore_sync`.`pg_paperglass_app_config_deduped`
(
  `firestore_document_id` STRING,
  `tenant_id` STRING,
  `patient_id` STRING,
  `active` BOOLEAN,
  `app_id` STRING,
  `config_enable_ocr` BOOLEAN,
  `config_evidence_weak_matching_enabled` BOOLEAN,
  `config_evidence_weak_matching_firsttoken_enabled` BOOLEAN,
  `config_extract_allergies` BOOLEAN,
  `config_extract_conditions` BOOLEAN,
  `config_extract_immunizations` BOOLEAN,
  `config_extraction_persisted_to_medication_profile` BOOLEAN,
  `config_medispan_matching_version` STRING,
  `config_on_demand_external_files_config_enabled` BOOLEAN,
  `config_on_demand_external_files_config_uploaded_date_cut_off_window_in_days` INTEGER,
  `config_orchestration_confirm_evidence_linking_enabled` BOOLEAN,
  `config_retry_config` STRING,
  `config_tenant_allow_list` STRING,
  `config_use_extract_and_classify_strategy` BOOLEAN,
  `config_use_ordered_events` BOOLEAN,
  `config_use_pagination` BOOLEAN,
  `config_use_v3_orchestration_engine` BOOLEAN,
  `created_at` STRING,
  `created_by` STRING,
  `id` STRING,
  `modified_at` STRING,
  `modified_by` STRING
)
CLUSTER BY app_id, tenant_id, patient_id, modified_at;

MERGE INTO `viki-dev-app-wsky`.`firestore_sync`.`pg_paperglass_app_config_deduped` AS target 

USING (
  SELECT * FROM (
    SELECT 
      timestamp,
      event_id,
      document_name,
      operation,
      CAST(JSON_EXTRACT(data, '$.active') AS BOOLEAN) as data_active,
      JSON_EXTRACT_SCALAR(data, '$.app_id') as data_app_id,
      CAST(JSON_EXTRACT(data, '$.config.enable_ocr') AS BOOLEAN) as data_config_enable_ocr,
      CAST(JSON_EXTRACT(data, '$.config.evidence_weak_matching_enabled') AS BOOLEAN) as data_config_evidence_weak_matching_enabled,
      CAST(JSON_EXTRACT(data, '$.config.evidence_weak_matching_firsttoken_enabled') AS BOOLEAN) as data_config_evidence_weak_matching_firsttoken_enabled,
      CAST(JSON_EXTRACT(data, '$.config.extract_allergies') AS BOOLEAN) as data_config_extract_allergies,
      CAST(JSON_EXTRACT(data, '$.config.extract_conditions') AS BOOLEAN) as data_config_extract_conditions,
      CAST(JSON_EXTRACT(data, '$.config.extract_immunizations') AS BOOLEAN) as data_config_extract_immunizations,
      CAST(JSON_EXTRACT(data, '$.config.extraction_persisted_to_medication_profile') AS BOOLEAN) as data_config_extraction_persisted_to_medication_profile,
      JSON_EXTRACT_SCALAR(data, '$.config.medispan_matching_version') as data_config_medispan_matching_version,
      CAST(JSON_EXTRACT(data, '$.config.on_demand_external_files_config.enabled') AS BOOLEAN) as data_config_on_demand_external_files_config_enabled,
      CAST(JSON_EXTRACT(data, '$.config.on_demand_external_files_config.uploaded_date_cut_off_window_in_days') AS INT64) as data_config_on_demand_external_files_config_uploaded_date_cut_off_window_in_days,
      CAST(JSON_EXTRACT(data, '$.config.orchestration_confirm_evidence_linking_enabled') AS BOOLEAN) as data_config_orchestration_confirm_evidence_linking_enabled,
      JSON_EXTRACT_SCALAR(data, '$.config.retry_config') as data_config_retry_config,
      JSON_EXTRACT_SCALAR(data, '$.config.tenant_allow_list') as data_config_tenant_allow_list,
      CAST(JSON_EXTRACT(data, '$.config.use_extract_and_classify_strategy') AS BOOLEAN) as data_config_use_extract_and_classify_strategy,
      CAST(JSON_EXTRACT(data, '$.config.use_ordered_events') AS BOOLEAN) as data_config_use_ordered_events,
      CAST(JSON_EXTRACT(data, '$.config.use_pagination') AS BOOLEAN) as data_config_use_pagination,
      CAST(JSON_EXTRACT(data, '$.config.use_v3_orchestration_engine') AS BOOLEAN) as data_config_use_v3_orchestration_engine,
      JSON_EXTRACT_SCALAR(data, '$.created_at') as data_created_at,
      JSON_EXTRACT_SCALAR(data, '$.created_by') as data_created_by,
      JSON_EXTRACT_SCALAR(data, '$.id') as data_id,
      JSON_EXTRACT_SCALAR(data, '$.modified_at') as data_modified_at,
      JSON_EXTRACT_SCALAR(data, '$.modified_by') as data_modified_by,
      document_id,
      ROW_NUMBER() OVER (PARTITION BY document_id ORDER BY timestamp DESC) as rn
    FROM `viki-dev-app-wsky`.`firestore_sync`.`pg_paperglass_app_config_raw_changelog`
    WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
  ) 
  WHERE rn = 1
) AS source 

ON target.firestore_document_id = source.document_id

WHEN MATCHED AND TIMESTAMP(target.modified_at) < TIMESTAMP(source.data_modified_at) THEN 
  UPDATE SET
      target.active = source.data_active,
      target.app_id = source.data_app_id,
      target.config_enable_ocr = source.data_config_enable_ocr,
      target.config_evidence_weak_matching_enabled = source.data_config_evidence_weak_matching_enabled,
      target.config_evidence_weak_matching_firsttoken_enabled = source.data_config_evidence_weak_matching_firsttoken_enabled,
      target.config_extract_allergies = source.data_config_extract_allergies,
      target.config_extract_conditions = source.data_config_extract_conditions,
      target.config_extract_immunizations = source.data_config_extract_immunizations,
      target.config_extraction_persisted_to_medication_profile = source.data_config_extraction_persisted_to_medication_profile,
      target.config_medispan_matching_version = source.data_config_medispan_matching_version,
      target.config_on_demand_external_files_config_enabled = source.data_config_on_demand_external_files_config_enabled,
      target.config_on_demand_external_files_config_uploaded_date_cut_off_window_in_days = source.data_config_on_demand_external_files_config_uploaded_date_cut_off_window_in_days,
      target.config_orchestration_confirm_evidence_linking_enabled = source.data_config_orchestration_confirm_evidence_linking_enabled,
      target.config_retry_config = source.data_config_retry_config,
      target.config_tenant_allow_list = source.data_config_tenant_allow_list,
      target.config_use_extract_and_classify_strategy = source.data_config_use_extract_and_classify_strategy,
      target.config_use_ordered_events = source.data_config_use_ordered_events,
      target.config_use_pagination = source.data_config_use_pagination,
      target.config_use_v3_orchestration_engine = source.data_config_use_v3_orchestration_engine,
      target.created_at = source.data_created_at,
      target.created_by = source.data_created_by,
      target.id = source.data_id,
      target.modified_at = source.data_modified_at,
      target.modified_by = source.data_modified_by

WHEN NOT MATCHED THEN 
  INSERT (
    firestore_document_id,
    active,
    app_id,
    config_enable_ocr,
    config_evidence_weak_matching_enabled,
    config_evidence_weak_matching_firsttoken_enabled,
    config_extract_allergies,
    config_extract_conditions,
    config_extract_immunizations,
    config_extraction_persisted_to_medication_profile,
    config_medispan_matching_version,
    config_on_demand_external_files_config_enabled,
    config_on_demand_external_files_config_uploaded_date_cut_off_window_in_days,
    config_orchestration_confirm_evidence_linking_enabled,
    config_retry_config,
    config_tenant_allow_list,
    config_use_extract_and_classify_strategy,
    config_use_ordered_events,
    config_use_pagination,
    config_use_v3_orchestration_engine,
    created_at,
    created_by,
    id,
    modified_at,
    modified_by
  ) 
  VALUES (
    document_id,
    source.data_active,
    source.data_app_id,
    source.data_config_enable_ocr,
    source.data_config_evidence_weak_matching_enabled,
    source.data_config_evidence_weak_matching_firsttoken_enabled,
    source.data_config_extract_allergies,
    source.data_config_extract_conditions,
    source.data_config_extract_immunizations,
    source.data_config_extraction_persisted_to_medication_profile,
    source.data_config_medispan_matching_version,
    source.data_config_on_demand_external_files_config_enabled,
    source.data_config_on_demand_external_files_config_uploaded_date_cut_off_window_in_days,
    source.data_config_orchestration_confirm_evidence_linking_enabled,
    source.data_config_retry_config,
    source.data_config_tenant_allow_list,
    source.data_config_use_extract_and_classify_strategy,
    source.data_config_use_ordered_events,
    source.data_config_use_pagination,
    source.data_config_use_v3_orchestration_engine,
    source.data_created_at,
    source.data_created_by,
    source.data_id,
    source.data_modified_at,
    source.data_modified_by
  );
