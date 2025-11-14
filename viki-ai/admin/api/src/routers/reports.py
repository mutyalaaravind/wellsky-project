import csv
import io
from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Depends, Request
from fastapi.responses import Response

from contracts.reports_contracts import ReportsPort, ReportParams, HostUpdateSummaryResponse
from infrastructure.bindings import get_reports_service

router = APIRouter()


async def get_reports_adapter() -> ReportsPort:
    """Dependency to get reports adapter instance."""
    return get_reports_service()


@router.get("/host-update-summary")
async def get_host_update_summary(
    request: Request,
    app_id: str = Query(..., description="Application ID (e.g., 'hhh')"),
    start_date: date = Query(..., description="Start date for the report (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date for the report (YYYY-MM-DD). Defaults to current date if not provided"),
    reports_service: ReportsPort = Depends(get_reports_adapter)
):
    """
    Get medication host update summary report.

    This endpoint provides a summary of medication extraction accuracy metrics,
    including total updates, user edits, and field-specific edit breakdowns.

    Args:
        app_id: Application ID (currently only "hhh" but will have more in the future)
        start_date: Start date for the report (required)
        end_date: End date for the report (optional, defaults to current date)

    Returns:
        JSON or CSV format based on Accept header:
        - application/json: Returns structured JSON response
        - text/csv: Returns CSV formatted data
    """
    try:
        # Validate app_id (currently only "hhh" is supported)
        if app_id not in ["hhh", "007", "ltc"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid app_id '{app_id}'. Currently supported: 'hhh'"
            )

        # Create report parameters
        params = ReportParams(
            app_id=app_id,
            start_date=start_date,
            end_date=end_date
        )

        # Get report data
        report_data = await reports_service.get_host_update_summary(params)

        # Check content type preference
        accept_header = request.headers.get("accept", "application/json").lower()
        content_type = request.headers.get("content-type", "application/json").lower()

        # Determine response format based on headers
        if "text/csv" in accept_header or "text/csv" in content_type:
            return _format_csv_response(report_data)
        else:
            # Default to JSON response
            return HostUpdateSummaryResponse(
                success=True,
                message="Report generated successfully",
                data=report_data
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate host update summary: {str(e)}"
        )


@router.get("/host-update-detail")
async def get_host_update_detail(
    request: Request,
    app_id: str = Query(..., description="Application ID (e.g., 'hhh')"),
    start_date: date = Query(..., description="Start date for the report (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date for the report (YYYY-MM-DD). Defaults to current date if not provided"),
    reports_service: ReportsPort = Depends(get_reports_adapter)
):
    """
    Get detailed medication host update report.

    This endpoint provides detailed row-level data for each medication field that was edited,
    showing original values, modified values, and sync dates.

    Args:
        app_id: Application ID (currently only "hhh" and "007" supported)
        start_date: Start date for the report (required)
        end_date: End date for the report (optional, defaults to current date)

    Returns:
        JSON or CSV format based on Accept header:
        - application/json: Returns structured JSON response with array of edit records
        - text/csv: Returns CSV formatted data
    """
    try:
        # Validate app_id
        if app_id not in ["hhh", "007", "ltc"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid app_id '{app_id}'. Currently supported: 'hhh', '007'"
            )

        # Create report parameters
        params = ReportParams(
            app_id=app_id,
            start_date=start_date,
            end_date=end_date
        )

        # Get report data
        report_data = await reports_service.get_host_update_detail(params)

        # Check content type preference
        accept_header = request.headers.get("accept", "application/json").lower()
        content_type = request.headers.get("content-type", "application/json").lower()

        # Determine response format based on headers
        if "text/csv" in accept_header or "text/csv" in content_type:
            return _format_detail_csv_response(report_data)
        else:
            # Default to JSON response
            return {
                "success": True,
                "message": "Detail report generated successfully",
                "data": report_data
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate host update detail: {str(e)}"
        )


def _format_csv_response(report_data) -> Response:
    """Format report data as CSV response"""

    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        "app_id",
        "start_date",
        "end_date",
        "total_updated",
        "total_user_added",
        "total_user_accepted",
        "total_user_edited",
        "total_drug_edited",
        "total_strength_edited",
        "total_form_edited",
        "total_route_edited",
        "total_dose_edited",
        "total_instructions_edited",
        "total_start_date_edited",
        "total_discontinue_date_edited"
    ])

    # Write data row
    writer.writerow([
        report_data.params.app_id,
        report_data.params.start_date.isoformat(),
        report_data.params.end_date.isoformat() if report_data.params.end_date else "",
        report_data.total,
        report_data.total_user_added,
        report_data.total_user_accepted,
        report_data.total_user_edited,
        report_data.edited_fields.drug,
        report_data.edited_fields.strength,
        report_data.edited_fields.form,
        report_data.edited_fields.route,
        report_data.edited_fields.dose,
        report_data.edited_fields.instructions,
        report_data.edited_fields.start_date,
        report_data.edited_fields.discontinue_date
    ])

    csv_content = output.getvalue()
    output.close()

    # Generate filename
    filename = f"medication_report_{report_data.params.app_id}_{report_data.params.start_date}_{report_data.params.end_date or date.today()}.csv"

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


def _format_detail_csv_response(report_data) -> Response:
    """Format detail report data as CSV response"""

    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        "app_id",
        "tenant_id",
        "patient_id",
        "document_id",
        "medispan_id",
        "field_edited",
        "original_value",
        "modified_value",
        "date_synced"
    ])

    # Write data rows
    for record in report_data:
        writer.writerow([
            record.get("app_id", ""),
            record.get("tenant_id", ""),
            record.get("patient_id", ""),
            record.get("document_id", ""),
            record.get("medispan_id", ""),
            record.get("field_edited", ""),
            record.get("original_value", ""),
            record.get("modified_value", ""),
            record.get("date_synced", "")
        ])

    csv_content = output.getvalue()
    output.close()

    # Generate filename
    filename = f"medication_detail_report_{date.today().isoformat()}.csv"

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )