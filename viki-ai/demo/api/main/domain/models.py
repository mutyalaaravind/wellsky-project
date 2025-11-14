import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, Extra, Field


class Patient(BaseModel):
    id:str
    first_name: str
    last_name: str
    dob: str
    created_at: str
    updated_at: str
    active: bool = True
    app_id: str = "007"
    tenant_id: str = "54321"

    @classmethod
    def create(cls, first_name: str, last_name: str, dob: str):
        created_at = datetime.datetime.now().isoformat()
        updated_at = created_at
        active=True
        return cls(id=uuid.uuid4().hex, first_name=first_name, last_name=last_name, dob=dob, created_at=created_at, updated_at=updated_at, active=active)


class Medication(BaseModel):
    tenantId: str
    patientId: str
    id: str
    catalogType: str
    catalogId: str
    name: str
    strength: str
    dosage: str
    form: str
    route: str
    frequency: str
    instructions: str
    startDate: str
    discontinueDate: Optional[str] = None
    isLongstanding: bool = False
    isNonStandardDose: bool = False

    @classmethod
    def create(cls, tenantId: str, patientId: str, catalogType: str, catalogId: str,
               name: str, strength: str, dosage: str, form: str, route: str, id: str,
               frequency: str, instructions: str, startDate: str,
               discontinueDate: Optional[str] = None,
               isLongstanding: bool = False,
               isNonStandardDose: bool = False):
        return cls(
            tenant_id=tenantId,
            patient_id=patientId,
            id=id,
            catalog_type=catalogType,
            catalog_id=catalogId,
            name=name,
            strength=strength,
            dosage=dosage,
            form=form,
            route=route,
            frequency=frequency,
            instructions=instructions,
            start_date=startDate,
            discontinue_date=discontinueDate,
            is_longstanding=isLongstanding,
            is_non_standard_dose=isNonStandardDose
        )

class Attachment(BaseModel):
    appId: str
    tenantId: str
    patientId: str
    hostFileId: str
    fileId: str
    fileName: str
    fileType: str
    createdOn: str
    updatedOn: str
    sha256: str
    metadata: dict
    active: bool
    repositoryType: str
    api: dict
    
    @classmethod
    def create(cls, appId: str, tenantId: str, patientId: str, hostFileId: str, fileId: str,
               fileName: str, fileType: str, createdOn: str, updatedOn: str, sha256: str, metadata: dict,
               active: bool, repositoryType: str, api: dict):
        return cls(
            appId=appId,
            tenantId=tenantId,
            patientId=patientId,
            hostFileId=hostFileId,
            fileId=fileId,
            fileName=fileName,
            fileType=fileType,
            createdOn=createdOn,
            updatedOn=updatedOn,
            sha256=sha256,
            metadata=metadata,
            active=active,
            repositoryType=repositoryType,
            api=api
        )
