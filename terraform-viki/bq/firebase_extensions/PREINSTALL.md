Use this extension to export the documents in a Cloud Firestore collection to BigQuery. Exports are realtime and incremental, so the data in BigQuery is a mirror of your content in Cloud Firestore.

The extension creates and updates a [dataset](https://cloud.google.com/bigquery/docs/datasets-intro) containing the following two BigQuery resources:

- A [table](https://cloud.google.com/bigquery/docs/tables-intro) of raw data that stores a full change history of the documents within your collection. This table includes a number of metadata fields so that BigQuery can display the current state of your data. The principle metadata fields are `timestamp`, `document_name`, and the `operation` for the document change.
- A [view](https://cloud.google.com/bigquery/docs/views-intro) which represents the current state of the data within your collection. It also shows a log of the latest `operation` for each document (`CREATE`, `UPDATE`, or `IMPORT`).

*Warning*: A BigQuery table corresponding to your configuration will be automatically generated upon installing or updating this extension. Manual table creation may result in discrepancies with your configured settings.

If you create, update, or delete a document in the specified collection, this extension sends that update to BigQuery. You can then run queries on this mirrored dataset.

#### Non-Interactive Installation

To install the extension non-interactively, use the Firebase CLI with a params file:

1. Create a params.env file with your configuration:
```
DATASET_LOCATION=us-central1
BIGQUERY_PROJECT_ID=your-project-id
COLLECTION_PATH=your-collection-path
DATABASE_ID=(default)
DATASET_ID=your-dataset-id
TABLE_ID=your-table-prefix
TABLE_PARTITIONING=DAY
CLUSTERING=data,document_id,timestamp
MAX_DISPATCHES_PER_SECOND=100
MAX_ENQUEUE_ATTEMPTS=3
BACKUP_TO_GCS=no
USE_NEW_SNAPSHOT_QUERY_SYNTAX=yes
EXCLUDE_OLD_DATA=no
```

2. Install using Firebase CLI:
```bash
firebase ext:install firebase/firestore-anydb-bigquery-export --params-file=params.env --project=your-project-id
```

Required parameters:
- DATASET_LOCATION: BigQuery dataset location (e.g., us-central1)
- BIGQUERY_PROJECT_ID: Project ID for BigQuery instance
- COLLECTION_PATH: Firestore collection path to export
- DATABASE_ID: Firestore database ID (default is "(default)")
- DATASET_ID: BigQuery dataset ID
- TABLE_ID: Prefix for BigQuery table and view names

Optional parameters:
- TABLE_PARTITIONING: Time partitioning type (HOUR, DAY, MONTH, YEAR, or NONE)
- TIME_PARTITIONING_FIELD: Column name for time partitioning
- TIME_PARTITIONING_FIRESTORE_FIELD: Firestore field for time partitioning
- TIME_PARTITIONING_FIELD_TYPE: Field type for time partitioning (TIMESTAMP, DATETIME, DATE)
- CLUSTERING: Comma-separated fields for clustering (max 4 fields)
- MAX_DISPATCHES_PER_SECOND: Sync rate limit (1-500, default 100)
- MAX_ENQUEUE_ATTEMPTS: Maximum retry attempts (1-10, default 3)
- BACKUP_TO_GCS: Enable GCS backup (yes/no)
- BACKUP_GCS_BUCKET: GCS bucket for backups
- BACKUP_COLLECTION: Firestore collection for failed updates
- TRANSFORM_FUNCTION: URL for transform function
- USE_NEW_SNAPSHOT_QUERY_SYNTAX: Use new query syntax (yes/no)
- EXCLUDE_OLD_DATA: Exclude old data payloads (yes/no)
- KMS_KEY_NAME: Cloud KMS key name for encryption

#### Non-Interactive Sync Support

This extension supports both interactive and non-interactive sync modes with automatic fallback to Cloud Tasks for reliability. The non-interactive mode provides:

- **Reliable Async Processing**: Uses Cloud Tasks to handle document syncs asynchronously, ensuring reliability even with large data volumes or temporary service interruptions
- **Configurable Sync Rate**: Control throughput with MAX_DISPATCHES_PER_SECOND (1-500, default 100)
- **Automatic Retries**: Configure MAX_ENQUEUE_ATTEMPTS (1-10, default 3) for automatic retry of failed syncs
- **Multiple Backup Options**:
  - Backup failed syncs to Cloud Storage (BACKUP_TO_GCS)
  - Write failed updates to a backup Firestore collection (BACKUP_COLLECTION)
- **Transform Support**: Optional HTTP function to transform data before BigQuery writes

For optimal non-interactive sync:
1. Set MAX_DISPATCHES_PER_SECOND based on your BigQuery quotas and system load
2. Configure MAX_ENQUEUE_ATTEMPTS for your reliability needs
3. Enable BACKUP_TO_GCS or set BACKUP_COLLECTION for failed sync recovery
4. Use the transform function for any necessary data processing

Note that this extension only listens for _document_ changes in the collection, but not changes in any _subcollection_. You can, though, install additional instances of this extension to specifically listen to a subcollection or other collections in your database. Or if you have the same subcollection across documents in a given collection, you can use `{wildcard}` notation to listen to all those subcollections (for example: `chats/{chatid}/posts`). 

Enabling wildcard references will provide an additional STRING based column. The resulting JSON field value references any wildcards that are included in ${param:COLLECTION_PATH}. You can extract them using [JSON_EXTRACT_SCALAR](https://cloud.google.com/bigquery/docs/reference/standard-sql/json_functions#json_extract_scalar).


`Partition` settings cannot be updated on a pre-existing table, if these options are required then a new table must be created.

Note: To enable partitioning for a Big Query database, the following fields are required:

 - Time Partitioning option type
 - Time partitioning column name
 - Time partiitioning table schema
 - Firestore document field name

`Clustering` will not need to create or modify a table when adding clustering options, this will be updated automatically.

#### Additional setup

Before installing this extension, you'll need to:

- [Set up Cloud Firestore in your Firebase project.](https://firebase.google.com/docs/firestore/quickstart)
- [Link your Firebase project to BigQuery.](https://support.google.com/firebase/answer/6318765)


#### Import existing documents

There are two ways to import existing Firestore documents into BigQuery - the backfill feature and the import script.

To import documents that already exist at installation time into BigQuery, answer **Yes** when the installer asks "Import existing Firestore documents into BigQuery?" The extension will export existing documents as part of the installation and update processes.

Alternatively, you can run the external [import script](https://github.com/firebase/extensions/blob/master/firestore-bigquery-export/guides/IMPORT_EXISTING_DOCUMENTS.md) to backfill existing documents. If you plan to use this script, answer **No** when prompted to import existing documents.

**Important:** Run the external import script over the entire collection _after_ installing this extension, otherwise all writes to your database during the import might be lost.

If you don't either enable automatic import or run the import script, the extension only exports the content of documents that are created or changed after installation.

#### Transform function

Prior to sending the document change to BigQuery, you have an opportunity to transform the data with an HTTP function. The payload will contain the following:

```
{ 
  data: [{
    insertId: int;
    json: {
      timestamp: int;
      event_id: int;
      document_name: string;
      document_id: int;
      operation: ChangeType;
      data: string;
    },
  }]
}
```

The response should be indentical in structure.

#### Using Customer Managed Encryption Keys

By default, BigQuery encrypts your content stored at rest. BigQuery handles and manages this default encryption for you without any additional actions on your part.

If you want to control encryption yourself, you can use customer-managed encryption keys (CMEK) for BigQuery. Instead of Google managing the key encryption keys that protect your data, you control and manage key encryption keys in Cloud KMS.

For more general information on this, see [the docs](https://cloud.google.com/bigquery/docs/customer-managed-encryption).

To use CMEK and the Key Management Service (KMS) with this extension
1. [Enable the KMS API in your Google Cloud Project](https://console.cloud.google.com/apis/enableflow?apiid=cloudkms.googleapis.com).
2. Create a keyring and keychain in the KMS. Note that the region of the keyring and key *must* match the region of your bigquery dataset
3. Grant the BigQuery service account permission to encrypt and decrypt using that key. The Cloud KMS CryptoKey Encrypter/Decrypter role grants this permission. First find your project number. You can find this for example on the cloud console dashboard `https://console.cloud.google.com/home/dashboard?project={PROJECT_ID}`. The service account which needs the Encrypter/Decrypter role is then `bq-PROJECT_NUMBER@bigquery-encryption.iam.gserviceaccount.com`. You can grant this role through the credentials service in the console, or through the CLI:
```
gcloud kms keys add-iam-policy-binding \
--project=KMS_PROJECT_ID \
--member serviceAccount:bq-PROJECT_NUMBER@bigquery-encryption.iam.gserviceaccount.com \
--role roles/cloudkms.cryptoKeyEncrypterDecrypter \
--location=KMS_KEY_LOCATION \
--keyring=KMS_KEY_RING \
KMS_KEY
```
4. When installing this extension, enter the resource name of your key. It will look something like the following:
```
projects/<YOUR PROJECT ID>/locations/<YOUR REGION>/keyRings/<YOUR KEY RING NAME>/cryptoKeys/<YOUR KEY NAME>
```
If you follow these steps, your changelog table should be created using your customer-managed encryption.

#### Generate schema views

After your data is in BigQuery, you can run the [schema-views script](https://github.com/firebase/extensions/blob/master/firestore-bigquery-export/guides/GENERATE_SCHEMA_VIEWS.md) (provided by this extension) to create views that make it easier to query relevant data. You only need to provide a JSON schema file that describes your data structure, and the schema-views script will create the views.

#### Billing
To install an extension, your project must be on the [Blaze (pay as you go) plan](https://firebase.google.com/pricing)

- This extension uses other Firebase and Google Cloud Platform services, which have associated charges if you exceed the service's no-cost tier:
  - BigQuery (this extension writes to BigQuery with [streaming inserts](https://cloud.google.com/bigquery/pricing#streaming_pricing))
  - Cloud Firestore
  - Cloud Functions (Node.js 10+ runtime. [See FAQs](https://firebase.google.com/support/faq#extensions-pricing))
