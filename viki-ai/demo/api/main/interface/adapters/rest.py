from dataclasses import asdict
import os
from typing import List, Any, Dict, Optional
from main.domain.models import Patient
from pydantic import BaseModel, ValidationError
import pydantic
from uuid import uuid4

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, FileResponse
from starlette.routing import Mount, Route

from main.usecases.forms import get_form_instance, save_form_instance
from main.utils.logger import getLogger

# Initialize logger
logger = getLogger(__name__)


class EntityRequest(BaseModel):
    """Request model for entity endpoint."""
    app_id: str
    tenant_id: str
    patient_id: str
    document_id: str
    entity_schema_id: str
    run_id: Optional[str] = None
    data: List[Dict[str, Any]] = []


class DocumentProcessingCompleteRequest(BaseModel):
    """Request model for document processing complete callback."""
    app_id: str
    tenant_id: str
    patient_id: str
    document_id: str
    source_id: Optional[str] = None
    status: str = "completed"
    timestamp: str
    run_id: str
    metadata: Optional[Dict[str, Any]] = None
    data: Optional[List[Dict[str, Any]]] = None


class RestAdapter(Starlette):
    def __init__(self):
        super().__init__(
            debug=True,
            routes=[
                Route('/form-instances/{id}', self.get_form_instance, methods=['GET']),
                Route('/form-instances/{id}', self.save_form_instance, methods=['POST']),
                # patients
                Route('/patients', self.get_all_patients, methods=['GET']),
                Route('/patients/{id}', self.get_patient, methods=['GET']),
                Route('/create_patient', self.create_patient, methods=['POST']),
                Route('/data', self.get_data_file, methods=['GET']),
                Route('/tokens/{patient_id}', self.get_tokens, methods=['GET']),
                Route('/clients/{tenantId}/patients/{patientId}/medications', self.get_medications, methods=['GET']),
                Route('/clients/{tenantId}/patients/{patientId}/medications', self.save_medication, methods=['POST']),
                Route('/clients/{tenantId}/patients/{patientId}/attachments', self.get_attachments, methods=['GET']),
                Route('/entities/{entity_id}', self.save_entity, methods=['POST']),
                Route('/entities', self.process_document_complete_callback, methods=['POST']),
            ],
        )

    async def get_attachments(self, request: Request):
        tenantId = request.path_params['tenantId']
        patientId = request.path_params['patientId']
        
        from main.usecases.attachments import get_attach
        meds = await get_attach(tenantId, patientId)
        
        return JSONResponse([med.dict() for med in meds])

    async def save_medication(self, request: Request):
        try:
            tenantId = request.path_params['tenantId']
            patientId = request.path_params['patientId']

            data = await request.json()
            data['tenantId'] = tenantId
            data['patientId'] = patientId
            data['id'] = uuid4().hex
            
            from main.usecases.medications import save_med
            med = await save_med(tenantId, patientId, data)
            
            return JSONResponse(med.dict(), status_code=201)
        except ValidationError as e:
            return JSONResponse({
                "messageType": "VALIDATION_ERROR",
                "message": str(e),
                "relatedToKeys": []
            }, status_code=400)
        except Exception as e:
            return JSONResponse({
                "messageType": "ERROR",
                "message": str(e),
                "relatedToKeys": []
            }, status_code=400)
    
    async def get_medications(self, request: Request):
        tenantId = request.path_params['tenantId']
        patientId = request.path_params['patientId']
        
        from main.usecases.medications import get_meds
        meds = await get_meds(tenantId, patientId)
        
        return JSONResponse([med.dict() for med in meds])

    async def get_data_file(self, request: Request):
        filename = request.query_params.get('filename')
        if not filename:
            return JSONResponse({'error': 'Filename must be provided'}, status_code=400)

        file_path = os.path.join('main/data', filename)

        if not os.path.exists(file_path):
            return JSONResponse({'error': 'File not found'}, status_code=404)

        return FileResponse(file_path)

    async def get_form_instance(self, request: Request):
        id = request.path_params['id']
        data = await get_form_instance(id)
        if data:
            return JSONResponse(data)
        else:
            return JSONResponse({'error': 'Form instance not fond'}, status_code=404)

    async def save_form_instance(self, request: Request):
        id = request.path_params['id']
        data = await request.json()
        await save_form_instance(id, data)
        return Response(content='', status_code=204)

    async def get_all_patients(self, request: Request):
        from main.usecases.patients import get_all_patients
        patients = await get_all_patients()
        return JSONResponse([{"appId":patient.app_id,"tenantId":patient.tenant_id,"firstName": patient.first_name, "lastName": patient.last_name, "dob": patient.dob, "id": patient.id, "createdAt": patient.created_at, "updatedAt": patient.updated_at, "active": patient.active} for patient in patients])

    async def create_patient(self, request: Request):
        from main.usecases.patients import create_patient
        data = await request.json()
        try:
            patient = Patient.create(first_name=data['firstName'], last_name=data['lastName'], dob=data['dob'])
            patient = await create_patient(patient)
            return JSONResponse({"firstName": patient.first_name, "lastName": patient.last_name, "dob": patient.dob, "id": patient.id, "createdAt": patient.created_at, "updatedAt": patient.updated_at, "active": patient.active})
        except ValidationError as e:
            return JSONResponse({'error': str(e)}, status_code=400)
        
    async def get_patient(self, request: Request):
        from main.usecases.patients import get_patient_by_id
        id = request.path_params['id']
        patient = await get_patient_by_id(id)
        if patient:
            return JSONResponse({"appId":patient.app_id,"tenantId":patient.tenant_id,"firstName": patient.first_name, "lastName": patient.last_name, "dob": patient.dob, "id": patient.id, "createdAt": patient.created_at, "updatedAt": patient.updated_at, "active": patient.active})
        else:
            return JSONResponse({'error': 'Patient not fond'}, status_code=404)
        
    async def get_tokens(self, request: Request):
        import jwt,requests
        from main.settings import OKTA_PAPERGLASS_TOKEN_ISSUER_URL,OKTA_PAPERGLASS_SCOPE,OKTA_PAPERGLASS_CLIENT_ID,OKTA_PAPERGLASS_CLIENT_SECRET
        user_id = request.headers.get("userId")
        patient_id = request.path_params['patient_id']
        from main.usecases.patients import get_patient_by_id
        patient:Patient = await get_patient_by_id(patient_id)
        encoded_token = jwt.encode({'appId': patient.app_id, 'tenantId':patient.tenant_id,'patientId':patient_id,'amuserkey':user_id}, OKTA_PAPERGLASS_CLIENT_SECRET,algorithm='HS256')

        payload = {
            'grant_type':'client_credentials',
            'scope':OKTA_PAPERGLASS_SCOPE,
            'client_id':OKTA_PAPERGLASS_CLIENT_ID,
            'client_secret':OKTA_PAPERGLASS_CLIENT_SECRET
            }
        
        client_creds_token = requests.post(OKTA_PAPERGLASS_TOKEN_ISSUER_URL, headers={'Content-Type':'application/x-www-form-urlencoded'}, data=payload)
        
        if client_creds_token.status_code != 200:
            extra = {
                "status_code": client_creds_token.status_code,
                "response_text": client_creds_token.text,
                "url": OKTA_PAPERGLASS_TOKEN_ISSUER_URL,
                "payload": payload                
            }
            logger.error("Failed to get Okta client credentials token: URL: %s StatusCode: %s payload: %s responsetext: %s", OKTA_PAPERGLASS_TOKEN_ISSUER_URL, client_creds_token.status_code, payload, client_creds_token.text, extra=extra)
            return JSONResponse(
                {'error': 'Failed to get token'}
            )
        
        okta_token = client_creds_token.json().get('access_token')

        return JSONResponse(
                {'token': encoded_token,'oktaToken':okta_token,'ehrToken':'33F64030-0EBF-340C-D683B075A6B17F91'}
            )

    async def save_entity(self, request: Request):
        """
        Save entity endpoint - POST /entities/{entity_id}
        
        Accepts a request body with:
        - app_id: str
        - tenant_id: str  
        - patient_id: str
        - document_id: str
        - data: List[Dict[str, Any]] (list of entities)
        """
        try:
            entity_id = request.path_params['entity_id']
            request_data = await request.json()
            
            # Validate request body using Pydantic model
            entity_request = EntityRequest(**request_data)
            
            # Log the received entity data
            extra = {
                "entity_id": entity_id,
                "app_id": entity_request.app_id,
                "tenant_id": entity_request.tenant_id,
                "patient_id": entity_request.patient_id,
                "document_id": entity_request.document_id,
                "run_id": entity_request.run_id,
                "data_count": len(entity_request.data) if entity_request.data else 0
            }
            
            logger.info(f"Received entity data for entity_id: {entity_id}", extra=extra)
            
            # Save entities to Firestore using the infrastructure layer
            doc_ids = []
            if entity_request.data:
                from main.usecases.entities import save_entities
                doc_ids = await save_entities(
                    entity_id=entity_id,
                    entities_data=entity_request.data,
                    app_id=entity_request.app_id,
                    tenant_id=entity_request.tenant_id,
                    patient_id=entity_request.patient_id,
                    document_id=entity_request.document_id,
                    entity_schema_id=entity_request.entity_schema_id,
                    run_id=entity_request.run_id
                )
                logger.info(f"Saved {len(doc_ids)} entities to Firestore collection demo_entity_{entity_id}", extra={
                    **extra,
                    "saved_doc_ids": doc_ids
                })
            
            response_data = {
                "entity_id": entity_id,
                "app_id": entity_request.app_id,
                "tenant_id": entity_request.tenant_id,
                "patient_id": entity_request.patient_id,
                "document_id": entity_request.document_id,
                "status": "saved",
                "message": f"Entity {entity_id} data saved successfully to Firestore",
                "entities_saved": len(doc_ids),
                "document_ids": doc_ids
            }
            
            logger.info(f"Successfully processed and saved entity {entity_id}", extra=extra)
            
            return JSONResponse(response_data, status_code=201)
            
        except ValidationError as e:
            logger.error(f"Validation error for entity {entity_id}: {str(e)}")
            return JSONResponse({
                "messageType": "VALIDATION_ERROR",
                "message": str(e),
                "relatedToKeys": []
            }, status_code=400)
        except Exception as e:
            logger.error(f"Error processing entity {entity_id}: {str(e)}")
            return JSONResponse({
                "messageType": "ERROR", 
                "message": str(e),
                "relatedToKeys": []
            }, status_code=500)

    async def process_document_complete_callback(self, request: Request):
        """
        Process document processing complete callback - POST /api/entities
        
        Accepts the callback payload from invoke_document_processing_complete() and persists entities.
        
        Expected payload structure:
        {
            "app_id": str,
            "tenant_id": str,
            "patient_id": str,
            "document_id": str,
            "status": str,
            "timestamp": str,
            "run_id": str,
            "metadata": Optional[Dict[str, Any]],
            "data": Optional[List[Dict[str, Any]]]  # List of entities
        }
        """
        try:
            request_data = await request.json()
            
            # Validate request body using Pydantic model
            callback_request = DocumentProcessingCompleteRequest(**request_data)
            
            # Log the received callback data
            extra = {
                "app_id": callback_request.app_id,
                "tenant_id": callback_request.tenant_id,
                "patient_id": callback_request.patient_id,
                "document_id": callback_request.document_id,
                "source_id": callback_request.source_id,
                "status": callback_request.status,
                "run_id": callback_request.run_id,
                "timestamp": callback_request.timestamp,
                "entities_count": len(callback_request.data) if callback_request.data else 0,
                "data_is_none": callback_request.data is None,
                "data_is_empty": callback_request.data == [] if callback_request.data is not None else False
            }
            
            logger.info("Received document processing complete callback", extra=extra)
            
            # Log the actual data content for debugging
            if callback_request.data:
                logger.info(f"Callback contains {len(callback_request.data)} entities", extra={
                    **extra,
                    "first_entity_sample": callback_request.data[0] if callback_request.data else None
                })
            else:
                logger.info("Callback contains no entity data", extra={
                    **extra,
                    "data_value": callback_request.data
                })
            
            # Process and save entities if they exist in the callback data
            saved_entities_count = 0
            saved_doc_ids = []
            
            if callback_request.data and len(callback_request.data) > 0:
                # Group entities by entity_type to save them in separate collections
                entities_by_type = {}
                
                for entity in callback_request.data:
                    entity_type = entity.get('entity_type', 'unknown')
                    if entity_type not in entities_by_type:
                        entities_by_type[entity_type] = []
                    entities_by_type[entity_type].append(entity)
                
                logger.info(f"Grouped entities by type: {list(entities_by_type.keys())}", extra={
                    **extra,
                    "entity_types": list(entities_by_type.keys()),
                    "entity_counts": {k: len(v) for k, v in entities_by_type.items()}
                })
                
                # Save entities for each entity type
                for entity_type, entities_data in entities_by_type.items():
                    try:
                        # Use entity_type as the collection identifier
                        entity_schema_id = f"document_processing_callback_{entity_type}"
                        
                        from main.usecases.entities import save_entities
                        type_saved_doc_ids = await save_entities(
                            entity_id=entity_type,  # Use entity_type instead of generated ID
                            entities_data=entities_data,
                            app_id=callback_request.app_id,
                            tenant_id=callback_request.tenant_id,
                            patient_id=callback_request.patient_id,
                            document_id=callback_request.document_id,
                            source_id=callback_request.source_id,
                            entity_schema_id=entity_schema_id,
                            run_id=callback_request.run_id
                        )
                        saved_doc_ids.extend(type_saved_doc_ids)
                        saved_entities_count += len(type_saved_doc_ids)
                        
                        logger.info(f"Successfully saved {len(type_saved_doc_ids)} entities of type '{entity_type}' from callback", extra={
                            **extra,
                            "entity_type": entity_type,
                            "entity_schema_id": entity_schema_id,
                            "saved_doc_ids": type_saved_doc_ids,
                            "collection_name": f"demo_entity_{entity_type}"
                        })
                        
                    except Exception as save_error:
                        logger.error(f"Failed to save entities of type '{entity_type}' from callback: {str(save_error)}", extra={
                            **extra,
                            "entity_type": entity_type,
                            "error": str(save_error)
                        })
                        # Continue processing other entity types even if one fails
            
            # Prepare response
            response_data = {
                "app_id": callback_request.app_id,
                "tenant_id": callback_request.tenant_id,
                "patient_id": callback_request.patient_id,
                "document_id": callback_request.document_id,
                "source_id": callback_request.source_id,
                "status": "processed",
                "message": "Document processing complete callback processed successfully",
                "document_status": callback_request.status,
                "run_id": callback_request.run_id,
                "timestamp": callback_request.timestamp,
                "entities_received": len(callback_request.data) if callback_request.data else 0,
                "entities_saved": saved_entities_count,
                "entity_document_ids": saved_doc_ids
            }
            
            logger.info("Successfully processed document processing complete callback", extra={
                **extra,
                "entities_saved": saved_entities_count
            })
            
            return JSONResponse(response_data, status_code=200)
            
        except ValidationError as e:
            logger.error(f"Validation error in document processing callback: {str(e)}")
            return JSONResponse({
                "messageType": "VALIDATION_ERROR",
                "message": f"Invalid callback payload: {str(e)}",
                "relatedToKeys": []
            }, status_code=400)
        except Exception as e:
            logger.error(f"Error processing document complete callback: {str(e)}")
            return JSONResponse({
                "messageType": "ERROR",
                "message": f"Failed to process callback: {str(e)}",
                "relatedToKeys": []
            }, status_code=500)
