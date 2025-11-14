"""
BigQuery SQL queries for medication reports
"""

def get_edited_fields_query() -> str:
    """
    Query for field-specific medication edit metrics.
    Returns counts of specific fields that were edited.
    """
    return """
    WITH med_profile AS (
      SELECT
        COALESCE(JSON_EXTRACT_SCALAR(meds.data, '$.user_entered_medication.edit_type'), 'No Edit') AS edit_type,
        COALESCE(JSON_EXTRACT_ARRAY(meds.data, '$.extracted_medication_reference'), []) AS extracted_medications,

        -- Extracting user-entered values
        COALESCE(JSON_EXTRACT_SCALAR(meds.data, '$.user_entered_medication.medication.name'), '') AS user_entered_med_name,
        COALESCE(JSON_EXTRACT_SCALAR(meds.data, '$.user_entered_medication.medication.strength'), '') AS user_entered_strength,
        COALESCE(JSON_EXTRACT_SCALAR(meds.data, '$.user_entered_medication.medication.form'), '') AS user_entered_form,
        COALESCE(JSON_EXTRACT_SCALAR(meds.data, '$.user_entered_medication.medication.route'), '') AS user_entered_route,
        COALESCE(JSON_EXTRACT_SCALAR(meds.data, '$.user_entered_medication.medication.dosage'), '') AS user_entered_dose,
        COALESCE(JSON_EXTRACT_SCALAR(meds.data, '$.user_entered_medication.medication.instructions'), '') AS user_entered_instructions,
        COALESCE(JSON_EXTRACT_SCALAR(meds.data, '$.user_entered_medication.medication.start_date'), '') AS user_entered_start_date,
        COALESCE(JSON_EXTRACT_SCALAR(meds.data, '$.user_entered_medication.medication.discontinued_date'), '') AS user_entered_discontinue_date
      FROM `{project_id}.{dataset_id}.{medication_profile_table}`,
      UNNEST(medications) AS meds
      WHERE
        ARRAY_LENGTH(medications) > 0
        AND app_id = @app_id
        AND DATE(modified_at) >= @start_date
        AND DATE(modified_at) <= @end_date
    ),
    med_flags AS (
      SELECT
        edit_type,
        extracted_medications,
        user_entered_med_name,
        user_entered_strength,
        user_entered_form,
        user_entered_route,
        user_entered_dose,
        user_entered_instructions,
        user_entered_start_date,
        user_entered_discontinue_date,
        JSON_EXTRACT_SCALAR(JSON_EXTRACT(extracted_med,"$.extracted_medication_id")) as extracted_med_id,
        JSON_EXTRACT_SCALAR(JSON_EXTRACT(extracted_med,"$.document_operation_instance_id")) as doc_operation_instance_id
      FROM med_profile, UNNEST(extracted_medications) as extracted_med
    ),
    med_flags2 AS (
      SELECT
        edit_type,
        doc_meds.medication_name as original_med_name,
        user_entered_med_name,
        doc_meds.medication_strength as original_strength,
        user_entered_strength,
        doc_meds.medication_form as original_form,
        user_entered_form,
        doc_meds.medication_route as original_route,
        user_entered_route,
        doc_meds.medication_dosage as original_dose,
        user_entered_dose,
        doc_meds.medication_instructions as original_instructions,
        user_entered_instructions,
        doc_meds.medication_start_date as original_start_date,
        user_entered_start_date,
        doc_meds.medication_discontinued_date as original_discontinue_date,
        user_entered_discontinue_date
      FROM med_flags
      INNER JOIN `{project_id}.{dataset_id}.{doc_medications_table}` doc_meds
        ON doc_meds.id = med_flags.extracted_med_id
        AND doc_meds.document_operation_instance_id = med_flags.doc_operation_instance_id
    )
    SELECT
      COUNTIF(edit_type = 'updated' AND COALESCE(LOWER(user_entered_med_name), '') <> COALESCE(LOWER(original_med_name), '')) AS total_drug_edited,
      COUNTIF(edit_type = 'updated' AND COALESCE(LOWER(user_entered_strength), '') <> COALESCE(LOWER(original_strength), '')) AS total_strength_edited,
      COUNTIF(edit_type = 'updated' AND COALESCE(LOWER(user_entered_form), '') <> COALESCE(LOWER(original_form), '')) AS total_form_edited,
      COUNTIF(edit_type = 'updated' AND COALESCE(LOWER(user_entered_route), '') <> COALESCE(LOWER(original_route), '')) AS total_route_edited,
      COUNTIF(edit_type = 'updated' AND COALESCE(LOWER(user_entered_dose), '') <> COALESCE(LOWER(original_dose), '')) AS total_dose_edited,
      COUNTIF(edit_type = 'updated' AND COALESCE(LOWER(user_entered_instructions), '') <> COALESCE(LOWER(original_instructions), '')) AS total_instructions_edited,
      COUNTIF(edit_type = 'updated' AND COALESCE(LOWER(user_entered_start_date), '') <> COALESCE(LOWER(original_start_date), '')) AS total_start_date_edited,
      COUNTIF(edit_type = 'updated' AND COALESCE(LOWER(user_entered_discontinue_date), '') <> COALESCE(LOWER(original_discontinue_date), '')) AS total_discontinue_date_edited
    FROM med_flags2
    """

def get_host_update_detail_query() -> str:
    """
    Query for detailed host update report.
    Returns row-level data for each field that was edited.
    """
    return """
    WITH med_profile AS (
      SELECT
        app_id,
        tenant_id,
        patient_id,
        id AS document_id,
        COALESCE(JSON_EXTRACT_SCALAR(meds.data, '$.host_medication_sync_status.last_synced_at'), 'NA') AS date_synced,
        COALESCE(JSON_EXTRACT_SCALAR(meds.data, '$.user_entered_medication.edit_type'), 'No Edit') AS edit_type,
        COALESCE(JSON_EXTRACT_ARRAY(meds.data, '$.extracted_medication_reference'), []) AS extracted_medications,

        -- Extracting user-entered values
        COALESCE(JSON_EXTRACT_SCALAR(meds.data, '$.user_entered_medication.medication.name'), '') AS user_entered_med_name,
        COALESCE(JSON_EXTRACT_SCALAR(meds.data, '$.user_entered_medication.medication.strength'), '') AS user_entered_strength,
        COALESCE(JSON_EXTRACT_SCALAR(meds.data, '$.user_entered_medication.medication.form'), '') AS user_entered_form,
        COALESCE(JSON_EXTRACT_SCALAR(meds.data, '$.user_entered_medication.medication.route'), '') AS user_entered_route,
        COALESCE(JSON_EXTRACT_SCALAR(meds.data, '$.user_entered_medication.medication.dosage'), '') AS user_entered_dose,
        COALESCE(JSON_EXTRACT_SCALAR(meds.data, '$.user_entered_medication.medication.instructions'), '') AS user_entered_instructions,
        COALESCE(JSON_EXTRACT_SCALAR(meds.data, '$.user_entered_medication.medication.start_date'), '') AS user_entered_start_date,
        COALESCE(JSON_EXTRACT_SCALAR(meds.data, '$.user_entered_medication.medication.discontinued_date'), '') AS user_entered_discontinue_date
      FROM `{project_id}.{dataset_id}.{medication_profile_table}`,
      UNNEST(medications) AS meds
      WHERE
        ARRAY_LENGTH(medications) > 0
        AND app_id = @app_id
        AND DATE(modified_at) >= @start_date
        AND DATE(modified_at) <= @end_date
    ),
    med_flags AS (
      SELECT
        app_id,
        tenant_id,
        patient_id,
        document_id,
        edit_type,
        extracted_medications,
        user_entered_med_name,
        user_entered_strength,
        user_entered_form,
        user_entered_route,
        user_entered_dose,
        user_entered_instructions,
        user_entered_start_date,
        user_entered_discontinue_date,
        date_synced,
        JSON_EXTRACT_SCALAR(JSON_EXTRACT(extracted_med,"$.extracted_medication_id")) as extracted_med_id,
        JSON_EXTRACT_SCALAR(JSON_EXTRACT(extracted_med,"$.document_operation_instance_id")) as doc_operation_instance_id
      FROM med_profile, UNNEST(extracted_medications) as extracted_med
    ),
    med_flags2 AS (
      SELECT
        med_flags.app_id,
        med_flags.tenant_id,
        med_flags.patient_id,
        med_flags.document_id,
        med_flags.edit_type,
        med_flags.date_synced,
        doc_meds.medication_name as original_med_name,
        med_flags.user_entered_med_name,
        doc_meds.medication_strength as original_strength,
        med_flags.user_entered_strength,
        doc_meds.medication_form as original_form,
        med_flags.user_entered_form,
        doc_meds.medication_route as original_route,
        med_flags.user_entered_route,
        doc_meds.medication_dosage as original_dose,
        med_flags.user_entered_dose,
        doc_meds.medication_instructions as original_instructions,
        med_flags.user_entered_instructions,
        doc_meds.medication_start_date as original_start_date,
        med_flags.user_entered_start_date,
        doc_meds.medication_discontinued_date as original_discontinue_date,
        med_flags.user_entered_discontinue_date,
        doc_meds.medispan_id as medispan_id
      FROM med_flags
      INNER JOIN `{project_id}.{dataset_id}.{doc_medications_table}` doc_meds
        ON doc_meds.id = med_flags.extracted_med_id
        AND doc_meds.document_operation_instance_id = med_flags.doc_operation_instance_id
    )

    -- Generating separate rows for each field change
    SELECT
      app_id,
      tenant_id,
      patient_id,
      document_id,
      medispan_id,
      'name' AS field_edited,
      original_med_name AS original_value,
      user_entered_med_name AS modified_value,
      date_synced
    FROM med_flags2
    WHERE edit_type = 'updated' AND COALESCE(LOWER(user_entered_med_name), '') <> COALESCE(LOWER(original_med_name), '')

    UNION ALL

    SELECT
      app_id,
      tenant_id,
      patient_id,
      document_id,
      medispan_id,
      'strength' AS field_edited,
      original_strength AS original_value,
      user_entered_strength AS modified_value,
      date_synced
    FROM med_flags2
    WHERE edit_type = 'updated' AND COALESCE(LOWER(user_entered_strength), '') <> COALESCE(LOWER(original_strength), '')

    UNION ALL

    SELECT
      app_id,
      tenant_id,
      patient_id,
      document_id,
      medispan_id,
      'form' AS field_edited,
      original_form AS original_value,
      user_entered_form AS modified_value,
      date_synced
    FROM med_flags2
    WHERE edit_type = 'updated' AND COALESCE(LOWER(user_entered_form), '') <> COALESCE(LOWER(original_form), '')

    UNION ALL

    SELECT
      app_id,
      tenant_id,
      patient_id,
      document_id,
      medispan_id,
      'route' AS field_edited,
      original_route AS original_value,
      user_entered_route AS modified_value,
      date_synced
    FROM med_flags2
    WHERE edit_type = 'updated' AND COALESCE(LOWER(user_entered_route), '') <> COALESCE(LOWER(original_route), '')

    UNION ALL

    SELECT
      app_id,
      tenant_id,
      patient_id,
      document_id,
      medispan_id,
      'dose' AS field_edited,
      original_dose AS original_value,
      user_entered_dose AS modified_value,
      date_synced
    FROM med_flags2
    WHERE edit_type = 'updated' AND COALESCE(LOWER(user_entered_dose), '') <> COALESCE(LOWER(original_dose), '')

    UNION ALL

    SELECT
      app_id,
      tenant_id,
      patient_id,
      document_id,
      medispan_id,
      'instructions' AS field_edited,
      original_instructions AS original_value,
      user_entered_instructions AS modified_value,
      date_synced
    FROM med_flags2
    WHERE edit_type = 'updated' AND COALESCE(LOWER(user_entered_instructions), '') <> COALESCE(LOWER(original_instructions), '')

    UNION ALL

    SELECT
      app_id,
      tenant_id,
      patient_id,
      document_id,
      medispan_id,
      'start_date' AS field_edited,
      original_start_date AS original_value,
      user_entered_start_date AS modified_value,
      date_synced
    FROM med_flags2
    WHERE edit_type = 'updated' AND COALESCE(LOWER(user_entered_start_date), '') <> COALESCE(LOWER(original_start_date), '')

    UNION ALL

    SELECT
      app_id,
      tenant_id,
      patient_id,
      document_id,
      medispan_id,
      'discontinued_date' AS field_edited,
      original_discontinue_date AS original_value,
      user_entered_discontinue_date AS modified_value,
      date_synced
    FROM med_flags2
    WHERE edit_type = 'updated' AND COALESCE(LOWER(user_entered_discontinue_date), '') <> COALESCE(LOWER(original_discontinue_date), '')

    ORDER BY document_id DESC
    """

def get_host_update_summary_query() -> str:
    """
    Query for medication host update summary report.
    Returns total updated medications and accuracy metrics.
    """
    return """
    WITH med_profile AS (
      SELECT
        COALESCE(JSON_EXTRACT_SCALAR(meds.data, '$.host_medication_sync_status'), 'NA') AS host_medication_sync_status,
        COALESCE(JSON_EXTRACT(meds.data, '$.user_entered_medication'), '{{}}') AS user_entered_medication_json,
        COALESCE(JSON_EXTRACT_SCALAR(meds.data, '$.user_entered_medication.edit_type'), 'No Edit') AS edit_type
      FROM `{project_id}.{dataset_id}.{medication_profile_table}`,
      UNNEST(medications) AS meds
      WHERE
        ARRAY_LENGTH(medications) > 0
        AND app_id = @app_id
        AND DATE(modified_at) >= @start_date
        AND DATE(modified_at) <= @end_date
    ),
    med_flags AS (
      SELECT
        host_medication_sync_status,
        user_entered_medication_json,
        edit_type
      FROM med_profile
    )
    SELECT
      COUNTIF(host_medication_sync_status = 'NA') AS total_updated,
      COUNTIF(user_entered_medication_json = '{{}}' OR edit_type = 'No Edit') AS total_user_accepted,
      COUNTIF(user_entered_medication_json != '{{}}' AND edit_type = 'added') AS total_user_added,
      COUNTIF(user_entered_medication_json != '{{}}' AND edit_type = 'updated') AS total_user_edited
    FROM med_flags
    """