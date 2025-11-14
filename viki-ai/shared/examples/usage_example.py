#!/usr/bin/env python
"""
Example demonstrating how to use the viki_shared package.
"""

from datetime import datetime
from typing import Optional

from viki_shared.models.base import AggBase
from viki_shared.models.common import BaseJob, JobStatus, Metric
from viki_shared.utils.json_utils import JsonUtil
from viki_shared.utils.date_utils import now_utc
from viki_shared.utils.logger import getLogger, set_application_context
from viki_shared.utils.exceptions import JobException


# Example domain model extending AggBase
class Patient(AggBase):
    """Example patient model using shared base."""
    name: str
    age: int
    medical_record_number: str
    notes: Optional[str] = None


def main():
    """Demonstrate shared package functionality."""
    
    # Set up logging context
    set_application_context(
        app_id="example_app",
        tenant_id="tenant_123",
        user_id="user_456"
    )
    
    # Get logger with context
    logger = getLogger(__name__)
    logger.info("Starting example application")
    
    # Create a patient using shared base model
    patient = Patient(
        name="John Doe",
        age=45,
        medical_record_number="MRN123456",
        notes="Regular checkup scheduled"
    )
    
    logger.info("Created patient", extra={
        "patient_id": patient.id,
        "patient_name": patient.name
    })
    
    # Create a job using shared job model
    job = BaseJob(
        name="Process Patient Records",
        status=JobStatus.IN_PROGRESS,
        metadata={"patient_id": patient.id}
    )
    
    # Use shared JSON utilities
    patient_json = JsonUtil.dumps(patient.model_dump())
    logger.info("Serialized patient data", extra={
        "json_length": len(patient_json)
    })
    
    # Create metrics
    processing_time = Metric(
        name="patient_processing_time",
        value=1.23,
        unit="seconds",
        timestamp=now_utc(),
        labels={"patient_type": "regular"}
    )
    
    # Demonstrate exception handling
    try:
        if patient.age < 0:
            raise JobException("Invalid patient age")
        
        job.status = JobStatus.COMPLETED
        job.completed_at = now_utc()
        
        logger.info("Job completed successfully", extra={
            "job_id": job.id,
            "job_status": job.status.value,
            "processing_metric": processing_time.model_dump()
        })
        
    except JobException as e:
        logger.error("Job failed", extra={
            "job_id": job.id,
            "error": str(e)
        })
        job.status = JobStatus.FAILED
        job.error_message = str(e)
    
    # Clean and serialize complex data
    complex_data = {
        "patient": patient,
        "job": job,
        "metrics": [processing_time],
        "timestamp": now_utc()
    }
    
    cleaned_data = JsonUtil.clean(complex_data)
    
    logger.info("Application completed", extra={
        "total_objects_processed": 1,
        "final_status": job.status.value
    })
    
    print(f"Example completed successfully!")
    print(f"Patient ID: {patient.id}")
    print(f"Job Status: {job.status.value}")
    print(f"Processing Time: {processing_time.value} {processing_time.unit}")


if __name__ == "__main__":
    main()