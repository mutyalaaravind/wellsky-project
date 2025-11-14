--- query firestore_sync pg_medispan_meds_raw table for last 1 hour using timestamp field and do a merge/upsert into a table "pg_medispan_meds_deduped"
CREATE TABLE IF NOT EXISTS `viki-dev-app-wsky`.`firestore_sync`.`pg_medispan_meds_deduped`
(
  `firestore_document_id` STRING,
  `app_id` STRING,
  `tenant_id` STRING,
  `patient_id` STRING,
  `modified_at` TIMESTAMP,
  `Dosage_Form` STRING,
  `ExternalDrugId` STRING,
  `GenericName` STRING,
  `NameDescription` STRING,
  `Route` STRING,
  `Strength` STRING,
  `StrengthUnitOfMeasure` STRING,
  `med_embedding___type__` STRING,
  `med_embedding_value` STRING
)
CLUSTER BY app_id, tenant_id, patient_id, modified_at;

MERGE INTO `viki-dev-app-wsky`.`firestore_sync`.`pg_medispan_meds_deduped` AS target 

USING (
  SELECT * FROM (
    SELECT 
      timestamp,
      event_id,
      document_name,
      operation,
      JSON_EXTRACT_SCALAR(data, '$.Dosage_Form') as data_Dosage_Form,
      JSON_EXTRACT_SCALAR(data, '$.ExternalDrugId') as data_ExternalDrugId,
      JSON_EXTRACT_SCALAR(data, '$.GenericName') as data_GenericName,
      JSON_EXTRACT_SCALAR(data, '$.NameDescription') as data_NameDescription,
      JSON_EXTRACT_SCALAR(data, '$.Route') as data_Route,
      JSON_EXTRACT_SCALAR(data, '$.Strength') as data_Strength,
      JSON_EXTRACT_SCALAR(data, '$.StrengthUnitOfMeasure') as data_StrengthUnitOfMeasure,
      JSON_EXTRACT_SCALAR(data, '$.med_embedding.__type__') as data_med_embedding___type__,
      JSON_EXTRACT_SCALAR(data, '$.med_embedding.value') as data_med_embedding_value,
      document_id,
      ROW_NUMBER() OVER (PARTITION BY document_id ORDER BY timestamp DESC) as rn
    FROM `viki-dev-app-wsky`.`firestore_sync`.`pg_medispan_meds_raw_changelog`
    WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
  ) 
  WHERE rn = 1
) AS source 

ON target.firestore_document_id = source.document_id

WHEN MATCHED AND TIMESTAMP(target.modified_at) < TIMESTAMP(source.data_modified_at) THEN 
  UPDATE SET
      target.Dosage_Form = source.data_Dosage_Form,
      target.ExternalDrugId = source.data_ExternalDrugId,
      target.GenericName = source.data_GenericName,
      target.NameDescription = source.data_NameDescription,
      target.Route = source.data_Route,
      target.Strength = source.data_Strength,
      target.StrengthUnitOfMeasure = source.data_StrengthUnitOfMeasure,
      target.med_embedding___type__ = source.data_med_embedding___type__,
      target.med_embedding_value = source.data_med_embedding_value

WHEN NOT MATCHED THEN 
  INSERT (
    firestore_document_id,
    Dosage_Form,
    ExternalDrugId,
    GenericName,
    NameDescription,
    Route,
    Strength,
    StrengthUnitOfMeasure,
    med_embedding___type__,
    med_embedding_value
  ) 
  VALUES (
    document_id,
    source.data_Dosage_Form,
    source.data_ExternalDrugId,
    source.data_GenericName,
    source.data_NameDescription,
    source.data_Route,
    source.data_Strength,
    source.data_StrengthUnitOfMeasure,
    source.data_med_embedding___type__,
    source.data_med_embedding_value
  );
