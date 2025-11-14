import os
from typing import Dict, Any
from datetime import date, datetime
from pathlib import Path

from google.cloud import bigquery
from viki_shared.utils.logger import getLogger

from contracts.reports_contracts import ReportsPort, ReportParams, HostUpdateSummaryData, EditedFields
from settings import Settings
from reports_queries import get_host_update_summary_query, get_edited_fields_query, get_host_update_detail_query


class BigQueryReportsAdapter(ReportsPort):
    """BigQuery adapter implementing ReportsPort for medication reports"""

    def __init__(self, settings: Settings):
        """
        Initialize the BigQuery adapter.

        Args:
            settings: Application settings containing BigQuery configuration
        """
        self.logger = getLogger(__name__)
        self.logger.info("🔍 Initializing BigQuery Reports adapter")

        self.settings = settings
        self.project_id = settings.GCP_PROJECT_ID
        self.dataset_id = "firestore_sync"
        self.medication_profile_table = "pg_medications_medication_profile_deduped"
        self.doc_medications_table = "pg_doc_medications_deduped"

        # Initialize BigQuery client
        emulator_host = os.getenv("BIGQUERY_EMULATOR_HOST")
        if emulator_host:
            self.logger.info(f"🔍 Using BigQuery EMULATOR at {emulator_host}")
            # For emulator, we might use a different setup
            self.client = bigquery.Client(project=self.project_id)
        else:
            self.logger.info(f"🔍 Using PRODUCTION BigQuery - Project: {self.project_id}")
            self.client = bigquery.Client(project=self.project_id)

        self.logger.info("🔍 BigQuery Reports adapter initialized successfully")

    async def get_host_update_summary(self, params: ReportParams) -> HostUpdateSummaryData:
        """
        Get medication host update summary report from BigQuery.

        Args:
            params: Report parameters including app_id, start_date, end_date

        Returns:
            HostUpdateSummaryData with aggregated medication update statistics
        """
        self.logger.info(f"🔍 Generating host update summary for app_id: {params.app_id}, "
                        f"date range: {params.start_date} to {params.end_date}")

        # Use current date if end_date not provided
        end_date = params.end_date or date.today()

        try:
            job_config = self._get_query_config(params.app_id, params.start_date, end_date)

            # Execute summary query
            summary_query = self._build_summary_query()
            self.logger.debug(f"🔍 Executing summary query with parameters: app_id={params.app_id}, start_date={params.start_date}, end_date={end_date}")
            summary_job = self.client.query(summary_query, job_config=job_config)
            summary_results = summary_job.result()

            # Execute edited fields query
            edited_fields_query = self._build_edited_fields_query()
            self.logger.debug(f"🔍 Executing edited fields query")
            edited_fields_job = self.client.query(edited_fields_query, job_config=job_config)
            edited_fields_results = edited_fields_job.result()

            # Process combined results
            summary_data = self._process_combined_results(summary_results, edited_fields_results, params, end_date)

            self.logger.info(f"🔍 Successfully generated report with {summary_data.total} total medications")
            return summary_data

        except Exception as e:
            self.logger.error(f"🔍 Failed to generate host update summary: {str(e)}")
            raise Exception(f"Failed to generate medication report: {str(e)}")

    async def get_host_update_detail(self, params: ReportParams) -> list:
        """
        Get detailed medication host update report from BigQuery.

        Args:
            params: Report parameters including app_id, start_date, end_date

        Returns:
            List of dictionaries with detailed medication edit records
        """
        self.logger.info(f"🔍 Generating host update detail for app_id: {params.app_id}, "
                        f"date range: {params.start_date} to {params.end_date}")

        # Use current date if end_date not provided
        end_date = params.end_date or date.today()

        try:
            # Build the detail query
            query = self._build_detail_query()
            job_config = self._get_query_config(params.app_id, params.start_date, end_date)

            # Execute query
            self.logger.debug(f"🔍 Executing detail query with parameters: app_id={params.app_id}, start_date={params.start_date}, end_date={end_date}")
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()

            # Process results
            detail_data = self._process_detail_results(results)

            self.logger.info(f"🔍 Successfully generated detail report with {len(detail_data)} records")
            return detail_data

        except Exception as e:
            self.logger.error(f"🔍 Failed to generate host update detail: {str(e)}")
            raise Exception(f"Failed to generate detail medication report: {str(e)}")

    def _build_summary_query(self) -> str:
        """Build the BigQuery SQL query for summary report"""

        query_template = get_host_update_summary_query()

        return query_template.format(
            project_id=self.project_id,
            dataset_id=self.dataset_id,
            medication_profile_table=self.medication_profile_table
        )

    def _build_edited_fields_query(self) -> str:
        """Build the BigQuery SQL query for edited fields metrics"""

        query_template = get_edited_fields_query()

        return query_template.format(
            project_id=self.project_id,
            dataset_id=self.dataset_id,
            medication_profile_table=self.medication_profile_table,
            doc_medications_table=self.doc_medications_table
        )

    def _build_detail_query(self) -> str:
        """Build the BigQuery SQL query for detail report"""

        query_template = get_host_update_detail_query()

        return query_template.format(
            project_id=self.project_id,
            dataset_id=self.dataset_id,
            medication_profile_table=self.medication_profile_table,
            doc_medications_table=self.doc_medications_table
        )

    def _process_combined_results(self, summary_results, edited_fields_results, params: ReportParams, end_date: date) -> HostUpdateSummaryData:
        """Process combined BigQuery results into HostUpdateSummaryData"""

        # Convert summary results to list (should be single row)
        summary_rows = list(summary_results)
        edited_fields_rows = list(edited_fields_results)

        if not summary_rows:
            # No data found - return zeros
            self.logger.warning(f"🔍 No medication data found for app_id: {params.app_id}, "
                               f"date range: {params.start_date} to {end_date}")

            return HostUpdateSummaryData(
                params=ReportParams(
                    app_id=params.app_id,
                    start_date=params.start_date,
                    end_date=end_date
                ),
                total=0,
                total_user_added=0,
                total_user_accepted=0,
                total_user_edited=0,
                edited_fields=EditedFields(
                    drug=0,
                    strength=0,
                    form=0,
                    route=0,
                    dose=0,
                    instructions=0,
                    start_date=0,
                    discontinue_date=0
                )
            )

        # Process summary row
        summary_row = summary_rows[0]

        # Process edited fields row (may be empty if no edits)
        edited_fields = EditedFields(
            drug=0,
            strength=0,
            form=0,
            route=0,
            dose=0,
            instructions=0,
            start_date=0,
            discontinue_date=0
        )

        if edited_fields_rows:
            edited_row = edited_fields_rows[0]
            edited_fields = EditedFields(
                drug=int(edited_row.total_drug_edited or 0),
                strength=int(edited_row.total_strength_edited or 0),
                form=int(edited_row.total_form_edited or 0),
                route=int(edited_row.total_route_edited or 0),
                dose=int(edited_row.total_dose_edited or 0),
                instructions=int(edited_row.total_instructions_edited or 0),
                start_date=int(edited_row.total_start_date_edited or 0),
                discontinue_date=int(edited_row.total_discontinue_date_edited or 0)
            )

        return HostUpdateSummaryData(
            params=ReportParams(
                app_id=params.app_id,
                start_date=params.start_date,
                end_date=end_date
            ),
            total=int(summary_row.total_updated or 0),
            total_user_added=int(summary_row.total_user_added or 0),
            total_user_accepted=int(summary_row.total_user_accepted or 0),
            total_user_edited=int(summary_row.total_user_edited or 0),
            edited_fields=edited_fields
        )

    def _process_summary_results(self, results, params: ReportParams, end_date: date) -> HostUpdateSummaryData:
        """Process BigQuery results into HostUpdateSummaryData"""

        # Convert results to list (should be single row)
        rows = list(results)

        if not rows:
            # No data found - return zeros
            self.logger.warning(f"🔍 No medication data found for app_id: {params.app_id}, "
                               f"date range: {params.start_date} to {end_date}")

            return HostUpdateSummaryData(
                params=ReportParams(
                    app_id=params.app_id,
                    start_date=params.start_date,
                    end_date=end_date
                ),
                total=0,
                total_user_added=0,
                total_user_accepted=0,
                total_user_edited=0,
                edited_fields=EditedFields(
                    drug=0,
                    strength=0,
                    form=0,
                    route=0,
                    dose=0,
                    instructions=0,
                    start_date=0,
                    discontinue_date=0
                )
            )

        # Process first (and only) row
        row = rows[0]

        return HostUpdateSummaryData(
            params=ReportParams(
                app_id=params.app_id,
                start_date=params.start_date,
                end_date=end_date
            ),
            total=int(row.total_updated or 0),
            total_user_added=int(row.total_user_added or 0),
            total_user_accepted=int(row.total_user_accepted or 0),
            total_user_edited=int(row.total_user_edited or 0),
            edited_fields=EditedFields(
                drug=int(row.total_drug_edited or 0),
                strength=int(row.total_strength_edited or 0),
                form=int(row.total_form_edited or 0),
                route=int(row.total_route_edited or 0),
                dose=int(row.total_dose_edited or 0),
                instructions=int(row.total_instructions_edited or 0),
                start_date=int(row.total_start_date_edited or 0),
                discontinue_date=int(row.total_discontinue_date_edited or 0)
            )
        )

    def _get_query_config(self, app_id: str, start_date: date, end_date: date) -> bigquery.QueryJobConfig:
        """Get BigQuery job configuration with parameters"""
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("app_id", "STRING", app_id),
                bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
                bigquery.ScalarQueryParameter("end_date", "DATE", end_date),
            ]
        )
        return job_config

    def _process_detail_results(self, results) -> list:
        """Process BigQuery detail results into list of dictionaries"""

        detail_records = []

        for row in results:
            record = {
                "app_id": row.app_id,
                "tenant_id": row.tenant_id,
                "patient_id": row.patient_id,
                "document_id": row.document_id,
                "medispan_id": row.medispan_id or "",
                "field_edited": row.field_edited,
                "original_value": row.original_value or "",
                "modified_value": row.modified_value or "",
                "date_synced": row.date_synced
            }
            detail_records.append(record)

        return detail_records