-- Create temporary test tables
CREATE TEMP TABLE test_pg_documents_raw_changelog (
  timestamp TIMESTAMP,
  event_id STRING,
  document_name STRING,
  operation STRING,
  data STRING,
  document_id STRING
);

CREATE TEMP TABLE test_pg_documents_deduped (
  firestore_document_id STRING,
  id STRING,
  file_name STRING,
  modified_at TIMESTAMP
);

-- Insert test data

-- Test Case 1: Basic insert for new document
INSERT INTO test_pg_documents_raw_changelog 
VALUES (
  CURRENT_TIMESTAMP(),
  'event1',
  'doc1',
  'create',
  '{"id": "id1", "file_name": "file1.pdf", "modified_at": "2024-01-01T10:00:00Z"}',
  'doc1'
);

-- Test Case 2: Multiple versions of same document (should pick latest)
INSERT INTO test_pg_documents_raw_changelog 
VALUES 
  (
    CURRENT_TIMESTAMP(),
    'event2a',
    'doc2',
    'update',
    '{"id": "id2", "file_name": "file2_v1.pdf", "modified_at": "2024-01-01T10:00:00Z"}',
    'doc2'
  ),
  (
    CURRENT_TIMESTAMP(),
    'event2b',
    'doc2',
    'update',
    '{"id": "id2", "file_name": "file2_v2.pdf", "modified_at": "2024-01-01T11:00:00Z"}',
    'doc2'
  );

-- Test Case 3: Update with older version (should not update)
INSERT INTO test_pg_documents_deduped
VALUES ('doc3', 'id3', 'file3_v2.pdf', TIMESTAMP '2024-01-01T11:00:00Z');

INSERT INTO test_pg_documents_raw_changelog
VALUES (
  CURRENT_TIMESTAMP(),
  'event3',
  'doc3',
  'update',
  '{"id": "id3", "file_name": "file3_v1.pdf", "modified_at": "2024-01-01T10:00:00Z"}',
  'doc3'
);

-- Test Case 4: Update with newer version
INSERT INTO test_pg_documents_deduped
VALUES ('doc4', 'id4', 'file4_v1.pdf', TIMESTAMP '2024-01-01T10:00:00Z');

INSERT INTO test_pg_documents_raw_changelog
VALUES (
  CURRENT_TIMESTAMP(),
  'event4',
  'doc4',
  'update',
  '{"id": "id4", "file_name": "file4_v2.pdf", "modified_at": "2024-01-01T11:00:00Z"}',
  'doc4'
);

-- Run the merge operation
MERGE INTO test_pg_documents_deduped AS target 
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
    FROM test_pg_documents_raw_changelog
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

-- Assert results
WITH assertions AS (
  SELECT 
    CASE 
      -- Test Case 1: Should be inserted
      WHEN EXISTS (
        SELECT 1 FROM test_pg_documents_deduped 
        WHERE firestore_document_id = 'doc1' 
        AND file_name = 'file1.pdf'
        AND modified_at = TIMESTAMP '2024-01-01T10:00:00Z'
      ) THEN 'Test Case 1 Passed: New document inserted correctly'
      ELSE 'Test Case 1 Failed: New document not inserted correctly'
    END AS test1,
    
    CASE 
      -- Test Case 2: Should have latest version
      WHEN EXISTS (
        SELECT 1 FROM test_pg_documents_deduped 
        WHERE firestore_document_id = 'doc2' 
        AND file_name = 'file2_v2.pdf'
        AND modified_at = TIMESTAMP '2024-01-01T11:00:00Z'
      ) THEN 'Test Case 2 Passed: Latest version selected correctly'
      ELSE 'Test Case 2 Failed: Latest version not selected'
    END AS test2,
    
    CASE 
      -- Test Case 3: Should not update with older version
      WHEN EXISTS (
        SELECT 1 FROM test_pg_documents_deduped 
        WHERE firestore_document_id = 'doc3' 
        AND file_name = 'file3_v2.pdf'
        AND modified_at = TIMESTAMP '2024-01-01T11:00:00Z'
      ) THEN 'Test Case 3 Passed: Older version did not override newer version'
      ELSE 'Test Case 3 Failed: Older version incorrectly updated the record'
    END AS test3,
    
    CASE 
      -- Test Case 4: Should update with newer version
      WHEN EXISTS (
        SELECT 1 FROM test_pg_documents_deduped 
        WHERE firestore_document_id = 'doc4' 
        AND file_name = 'file4_v2.pdf'
        AND modified_at = TIMESTAMP '2024-01-01T11:00:00Z'
      ) THEN 'Test Case 4 Passed: Newer version updated correctly'
      ELSE 'Test Case 4 Failed: Newer version did not update correctly'
    END AS test4
)
SELECT * FROM assertions;
