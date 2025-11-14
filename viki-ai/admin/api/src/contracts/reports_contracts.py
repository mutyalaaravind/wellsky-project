from typing import Dict, Optional
from pydantic import BaseModel, Field
from datetime import date


class ReportParams(BaseModel):
    """Parameters for medication reports"""
    app_id: str = Field(..., description="Application ID")
    start_date: date = Field(..., description="Start date for the report")
    end_date: Optional[date] = Field(None, description="End date for the report (defaults to current date)")


class EditedFields(BaseModel):
    """Breakdown of edited medication fields"""
    drug: int = Field(..., description="Total medications where drug was edited")
    strength: int = Field(..., description="Total medications where strength was edited")
    form: int = Field(..., description="Total medications where form was edited")
    route: int = Field(..., description="Total medications where route was edited")
    dose: int = Field(..., description="Total medications where dose was edited")
    instructions: int = Field(..., description="Total medications where instructions were edited")
    start_date: int = Field(..., description="Total medications where start date was edited")
    discontinue_date: int = Field(..., description="Total medications where discontinue date was edited")


class HostUpdateSummaryData(BaseModel):
    """Medication host update summary data"""
    params: ReportParams = Field(..., description="Report parameters")
    total: int = Field(..., description="Total number of medications updated")
    total_user_added: int = Field(..., description="Total number of medications manually added by user")
    total_user_accepted: int = Field(..., description="Total number of medications accepted without changes")
    total_user_edited: int = Field(..., description="Total number of medications edited by user")
    edited_fields: EditedFields = Field(..., description="Breakdown of field edits")


class HostUpdateSummaryResponse(BaseModel):
    """Response for host update summary endpoint"""
    success: bool = Field(True, description="Whether the operation was successful")
    message: str = Field("Report generated successfully", description="Response message")
    data: HostUpdateSummaryData = Field(..., description="Report data")


class ReportsPort:
    """Port interface for reports data access"""

    async def get_host_update_summary(self, params: ReportParams) -> HostUpdateSummaryData:
        """Get medication host update summary report"""
        raise NotImplementedError

    async def get_host_update_detail(self, params: ReportParams) -> list:
        """Get detailed medication host update report"""
        raise NotImplementedError