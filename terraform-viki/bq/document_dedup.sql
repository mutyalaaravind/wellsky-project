--- query firestore_sync pg_documents_raw table for last 1 hour using timestamp field and do a merge/upsert into a table "pg_documents_deduped"
---DROP TABLE `viki-dev-app-wsky`.`firestore_sync`.`pg_documents_deduped`;
CREATE TABLE IF NOT EXISTS `viki-dev-app-wsky`.`firestore_sync`.`pg_documents_deduped`
(
  `firestore_document_id` string,
  `id` string,
  `file_name` string,
  `modified_at` timestamp
);

MERGE INTO `viki-dev-app-wsky`.`firestore_sync`.`pg_documents_deduped` AS target 

USING (
  SELECT * FROM (
    SELECT 
      timestamp,
      event_id,
      document_name,
      operation,
      JSON_EXTRACT_SCALAR(data, '$.id') as data_id,
      JSON_EXTRACT_SCALAR(data, '$.file_name') as data_file_name,
      TIMESTAMP(JSON_EXTRACT_SCALAR(data, '$.modified_at')) as data_modified_at,
      document_id,
      ROW_NUMBER() OVER (PARTITION BY document_id ORDER BY TIMESTAMP(JSON_EXTRACT_SCALAR(data, '$.modified_at')) DESC) as rn
    FROM `viki-dev-app-wsky`.`firestore_sync`.`pg_documents_raw_changelog`
    WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
  ) 
  WHERE rn = 1
) AS source 

ON target.firestore_document_id = source.document_id

WHEN MATCHED AND target.modified_at < source.data_modified_at THEN 
  UPDATE SET target.file_name = source.data_file_name,
             target.modified_at = source.data_modified_at

WHEN NOT MATCHED THEN 
  INSERT (firestore_document_id, id, file_name, modified_at) 
  VALUES (document_id, source.data_id, source.data_file_name, source.data_modified_at);
