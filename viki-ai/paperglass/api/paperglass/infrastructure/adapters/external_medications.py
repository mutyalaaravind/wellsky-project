from datetime import datetime
import pytz
from typing import Dict, List
from uuid import uuid4
from paperglass.domain.values import HostAttachment, HostAttachmentMetadata, HostMedicationAddModel, HostFreeformMedicationAddModel, HostMedication, HostMedicationUpdateModel, MedicationValue
from paperglass.infrastructure.ports import IHHHAdapter
from paperglass.domain.values import ImportedMedication

from paperglass.domain.models_common import ReferenceCodes, Code, NotFoundException
from paperglass.domain.time import now_utc
from paperglass.domain.model_metric import Metric
from paperglass.domain.utils.exception_utils import exceptionToMap

import requests,aiohttp,json

from ...settings import EXTERNAL_API_CONNECT_TIMEOUT_SECONDS, EXTERNAL_API_SOCKET_CONNECT_TIMEOUT_SECONDS, EXTERNAL_API_SOCKET_READ_TIMEOUT_SECONDS, HHH_ATTACHMENTS_AUTH_SERVER, HHH_ATTACHMENTS_CLIENT_ID, HHH_ATTACHMENTS_CLIENT_SECRET

from ...log import getLogger
LOGGER = getLogger(__name__)

#OpenTelemetry instrumentation
SPAN_BASE: str = "INFRA:HHHAdapter:"
from ...domain.utils.opentelemetry_utils import OpenTelemetryUtils
opentelemetry = OpenTelemetryUtils(SPAN_BASE)

"""
https://wellsky.atlassian.net/wiki/spaces/HHH/pages/541556752/Medication+Profile+REST+API+V1+Documentation

HHH medication API sample response
{
        "medication": "Aspirin Oral Tablet 325 MG", -->
        "route": "",
        "startDate": "07/01/2024",
        "dateType": "Discontinued",
        "strength": "",
        "patientMedispanRegistryKey": 75165423,
        "generateOrder": false,
        "patientMedispanKey": 987655909,
        "medicationInstructions": "take every day",
        "orderDate": "",
        "amount": "",
        "medicationId": 1925,
        "isLongStanding": false,
        "unitPerDose": "",
        "isNew": false,
        "dose": "<Dose><DoseItem>5</DoseItem></Dose>",
        "saveToMedicationProfile": false,
        "discontinueDate": "07/01/2024",
        "isChange": true,
        "orderPhysicianKey": ""
}
"""


class HHHAdapter(IHHHAdapter):
    def __init__(self,external_medications_url:str, attachments_api_url:str):
        self.external_medications_url = external_medications_url
        self.default_timeout = aiohttp.ClientTimeout(connect=EXTERNAL_API_CONNECT_TIMEOUT_SECONDS, sock_connect=EXTERNAL_API_SOCKET_CONNECT_TIMEOUT_SECONDS, sock_read=EXTERNAL_API_SOCKET_READ_TIMEOUT_SECONDS, )
        self.attachments_api_url = attachments_api_url

    async def get_medications(self,  patient_id: str, token:str) -> List[ImportedMedication]:
        thisSpanName = "get_medications"
        start_time = now_utc()
        with await opentelemetry.getSpan(thisSpanName) as span:
            url = f"{self.external_medications_url}rest/V1/MedicationProfile/Patient/{patient_id}"
            headers = {"token":token}

            tags = {
                "request": {
                    "url": url,
                    "headers": headers
                }
            }

            try:
                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False), timeout=self.default_timeout) as session:
                    async with session.get(url, headers=headers) as response:
                        end_time = now_utc()

                        response_text = await response.text()

                        tags.update({                            
                            "status": response.status,
                            "elapsed_time": (end_time - start_time).total_seconds(),
                            "response": {
                                "body": response_text
                            }
                        })

                        LOGGER.info("Response from external medication profile: status: %s response: %s", response.status, response_text, extra=tags)
                        if response.status==200 and response_text:
                            response_text = response_text.replace("//","").replace("<*>","")                            
                            response_data = json.loads(response_text)
                            
                            Metric.send(Metric.MetricType.HHH_MEDICATIONS_GET, tags=tags, branch="success")

                            return [HostMedication(
                                patient_id=patient_id,
                                medication=MedicationValue(name=medication.get("medication"),
                                            dosage=medication.get("dose").replace("<Dose><DoseItem>","").replace("</DoseItem></Dose>","").replace("<Dose/>", ""),
                                            route=medication.get("route"),
                                            frequency=None,
                                            instructions=medication.get("medicationInstructions"),
                                            start_date=medication.get("startDate"),
                                            discontinued_date=medication.get("discontinueDate")),
                                host_medication_id=medication.get("patientMedispanRegistryKey"),
                                medispan_id=medication.get("medicationId"),
                                original_payload=medication
                            ) for medication in response_data]
                        else:
                            LOGGER.error("External get medications returned no results: status: %s response: %s", response.status, response_text, extra=tags)
                            
                            Metric.send(Metric.MetricType.HHH_MEDICATIONS_GET, tags=tags, branch="error")

                            raise Exception(f"External get medications returned no results: status: {response.status} response: {response_text}")
            except Exception as e:
                 end_time = now_utc()

                 tags.update({
                     "error": exceptionToMap(e),
                     "elapsed_time": (end_time - start_time).total_seconds()
                 })

                 Metric.send(Metric.MetricType.HHH_MEDICATIONS_GET, tags=tags, branch="internalerror")

                 LOGGER.error("Exception getting external medication profile: %s", str(e), extra=tags)
                 raise e

    async def create_medication(self,  patient_id: str,token: str, user_id:str, medication:HostMedicationAddModel):
        thisSpanName = "create_medications"
        start_time = now_utc()
        with await opentelemetry.getSpan(thisSpanName) as span:
            LOGGER.debug("Medication being created in external system: %s", medication)

            dose:str = medication.dose
            if not dose or dose.strip()=="":
                dose = "N/A"

            url = f"{self.external_medications_url}rest/V1/MedicationProfile/Patient/{patient_id}"
            headers = {"token":token}
            payload = {
                "amuserkey": user_id,
                "medicationId": medication.medispan_id,
                "medicationInstructions": medication.medicationInstructions or "N/A",
                "medicationName": medication.medicationName,
                # VIKI-393 : Always sending the dose either it is empty or a value
                "dose": "" if not dose else f"{dose}",
                # "startDate": medication.startDate if medication.startDate else "",
                "discontinueDate": medication.discontinueDate, #ToDo,
                "LSFlag": 1 if medication.is_long_standing else -1,
                "isNonStandardDose": medication.is_nonstandard_dose,
            }

            if not medication.is_long_standing:
                payload["startDate"]= medication.startDate

            tags = {
                "request": {
                    "url": url,
                    "headers": headers,
                    "payload": payload
                }
            }

            LOGGER.debug("Calling create medication with  url: %s payload: %s  headers: %s", url, payload, headers, extra=tags)
            try:
                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False), timeout=self.default_timeout) as session:
                    async with session.post(url, headers=headers, data=payload ) as response:
                        end_time = now_utc()
                        
                        response_text = await response.text()

                        tags.update({
                            "status": response.status,
                            "elapsed_time": (end_time - start_time).total_seconds(),
                            "response": {
                                "body": response_text
                            }
                        })

                        if response.status==200 and response_text:                        
                            LOGGER.debug("Create medication response from external host: %s", response_text, extra=tags)
                            response_text = response_text.replace("//","").replace("<*>","")

                            Metric.send(Metric.MetricType.HHH_MEDICATIONS_ADD, tags=tags, branch="success")

                            return json.loads(response_text)
                        else:
                            LOGGER.error("Error invoking create medication request: status: %s response: %s", response.status, response_text, extra=tags)

                            Metric.send(Metric.MetricType.HHH_MEDICATIONS_ADD, tags=tags, branch="error")

                            raise Exception(f"Error invoking create medication request: status: {response.status} response: {response_text}")
            except Exception as e:
                end_time = now_utc()
                tags.update({
                    "error": exceptionToMap(e),
                    "elapsed_time": (end_time - start_time).total_seconds()
                })
                LOGGER.error("Exception creating medication in external system: %s", str(e), extra=tags)
                Metric.send(Metric.MetricType.HHH_MEDICATIONS_ADD, tags=tags, branch="internalerror")

                raise e



    async def create_freeform_medication(self, patient_id: str, token: str, user_id: str, medication:HostFreeformMedicationAddModel):
        with await opentelemetry.getSpan("create_medications_freeform") as span:
            LOGGER.debug("Freeform medication being created in external system: %s", medication)

            start_time = now_utc()

            dose:str = medication.dose
            if not dose or dose.strip()=="":
                dose = "N/A"

            medication_name = medication.medicationName

            url = f"{self.external_medications_url}rest/V1/MedicationProfile/Freeform/Patient/{patient_id}"
            headers = {"token":token}
            payload = {
                "amuserkey": user_id,
                "medication": medication_name,
                "classificationId": medication.classification_id,
                "newStartDate": medication.startDate,
                "newDiscontinueDate": medication.discontinueDate,
                "LSFlag": 1 if medication.is_long_standing else -1
            }

            tags = {
                "request": {
                    "url": url,
                    "headers": headers,
                    "payload": payload
                }
            }

            try:
                LOGGER.debug("Calling create freeform medication with  url: %s payload: %s  headers: %s", url, payload, headers, extra=tags)
                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False), timeout=self.default_timeout) as session:
                    async with session.post(url, headers=headers, data=payload ) as response:
                        end_time = now_utc()
                        response_text = await response.text()
                        tags.update({
                            "status": response.status,
                            "elapsed_time": (end_time - start_time).total_seconds(),
                            "response": {
                                "body": response_text
                            }
                        })
                        if response.status==200 and response_text:
                            LOGGER.debug("Create freeform medication response from external host: %s", response_text, extra=tags)

                            Metric.send(Metric.MetricType.HHH_MEDICATIONS_FREEFORM_ADD, tags=tags, branch="success")

                            # Cleanup response
                            response_text = self.clean_response(response_text)

                            return json.loads(response_text)
                        else:
                            LOGGER.error("Error invoking create freeform medication request: status: %s response: %s", response.status, response_text, extra=tags)

                            Metric.send(Metric.MetricType.HHH_MEDICATIONS_FREEFORM_ADD, tags=tags, branch="error")

                            raise Exception(f"Error invoking create freeform medication request: status: {response.status} response: {response_text}")
            except Exception as e:
                end_time = now_utc()
                tags.update({
                    "error": exceptionToMap(e),
                    "elapsed_time": (end_time - start_time).total_seconds()
                })
                LOGGER.error("Exception creating freeform medication in external system: %s", str(e), extra=tags)
                Metric.send(Metric.MetricType.HHH_MEDICATIONS_FREEFORM_ADD, tags=tags, branch="internalerror")
                raise e


    async def update_medication(self,  patient_id: str,token: str, user_id:str, medication:HostMedicationUpdateModel):
        thisSpanName = "update_medication"
        with await opentelemetry.getSpan(thisSpanName) as span:
            start_time = now_utc()

            url = f"{self.external_medications_url}rest/V1/MedicationProfile/Patient/{patient_id}"
            headers = {"token":token}
            payload = {
                "patientMedispanRegistryKey": medication.host_medication_id,
                "amuserkey": medication.modified_by,
                "medicationId": medication.medispan_id,
                "medicationInstructions": medication.medicationInstructions or "N/A",
                "medicationName": medication.medicationName,
                # "dose": f"{medication.dose}",
                "oldStartDate": medication.oldStartDate if medication.oldStartDate else "",
                #"newStartDate": medication.newStartDate if medication.newStartDate else "",
                "oldDiscontinueDate": medication.oldDiscontinueDate,#ToDo
                "newDiscontinueDate": medication.newDiscontinueDate, #ToDo
                "LSFlag": 1 if medication.is_long_standing else -1
            }

            if not medication.is_long_standing:
                payload["newStartDate"] = medication.newStartDate

            if not medication.is_nonstandard_dose:
                payload["dose"]= f"{medication.dose}"

            tags = {
                "request": {
                    "url": url,
                    "headers": headers,
                    "payload": payload
                }
            }

            try:
                LOGGER.debug("Calling external update medication with url: %s payload: %s  headers: %s", url, payload, headers, extra=tags)
                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False), timeout=self.default_timeout) as session:
                    async with session.put(url, headers=headers, data=payload ) as response:
                        end_time = now_utc()
                        response_text = await response.text()

                        tags.update({
                            "status": response.status,
                            "elapsed_time": (end_time - start_time).total_seconds(),
                            "response": {
                                "body": response_text
                            }
                        })

                        if response.status==200 and response_text:
                            LOGGER.debug("Create medication response from external host: %s", response_text, extra=tags)

                            Metric.send(Metric.MetricType.HHH_MEDICATIONS_UPDATE, tags=tags, branch="success")

                            response_text = response_text.replace("//","").replace("<*>","")
                            return json.loads(response_text)
                        else:
                            LOGGER.error("Error invoking update medication request: status: %s response: %s", response.status, response_text, extra=tags)
                            Metric.send(Metric.MetricType.HHH_MEDICATIONS_UPDATE, tags=tags, branch="error")
                            raise Exception(f"Error invoking update medication request: status: {response.status} response: {response_text}")
            except Exception as e:
                end_time = now_utc()
                tags.update({
                    "error": exceptionToMap(e),
                    "elapsed_time": (end_time - start_time).total_seconds()
                })
                LOGGER.error("Exception updating medication in external system: %s", str(e), extra=tags)
                Metric.send(Metric.MetricType.HHH_MEDICATIONS_UPDATE, tags=tags, branch="internalerror")
                raise e

    async def delete_medication(self, patient_id: str, token: str, user_id: str, host_medication_id: str ):
        with await opentelemetry.getSpan("delete_medication") as span:
            start_time = now_utc()

            url = f"{self.external_medications_url}rest/V1/MedicationProfile/Patient/{patient_id}"
            headers = {"token": token}
            payload = {
                "patientMedispanRegistryKey": host_medication_id,
                "amuserkey": user_id
            }

            tags = {
                "request": {
                    "url": url,
                    "headers": headers,
                    "payload": payload
                }
            }

            try:
                LOGGER.debug("Calling external delete medication with url: %s payload: %s  headers: %s", url, payload, headers, extra=tags)
                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False), timeout=self.default_timeout) as session:
                    async with session.delete(url, headers=headers, data=payload ) as response:
                        end_time = now_utc()
                        response_text = await response.text()

                        tags.update({
                            "status": response.status,
                            "elapsed_time": (end_time - start_time).total_seconds(),
                            "response": {
                                "body": response_text
                            }
                        })

                        if response.status==200 and response_text:
                            LOGGER.debug("Delete medication response from external host: %s", response_text, extra=tags)

                            Metric.send(Metric.MetricType.HHH_MEDICATIONS_DELETE, tags=tags, branch="success")

                            response_text = response_text.removeprefix("//")
                            return json.loads(response_text)
                        else:
                            LOGGER.error("Error invoking delete medication request: status: %s response: %s", response.status, response_text, extra=tags)

                            Metric.send(Metric.MetricType.HHH_MEDICATIONS_DELETE, tags=tags, branch="error")

                            raise Exception(f"Error invoking delete medication request: status: {response.status} response: {response_text}")
            except Exception as e:
                end_time = now_utc()
                tags.update({
                    "error": exceptionToMap(e),
                    "elapsed_time": (end_time - start_time).total_seconds()
                })
                LOGGER.error("Exception deleting medication in external system: %s", str(e), extra=tags)
                Metric.send(Metric.MetricType.HHH_MEDICATIONS_DELETE, tags=tags, branch="internalerror")
                raise e

    async def get_attachments(self,  tenant_id:str, patient_id: str, token:str,uploaded_date_cut_off_window_in_days:int) -> List[HostAttachment]:
        thisSpanName = "get_attachments"
        with await opentelemetry.getSpan(thisSpanName) as span:
            start_time = now_utc()

            url = f"{self.external_medications_url}rest/V1/Attachment/clinic/{tenant_id}/patient/{patient_id}"
            headers = {"token":token}

            tags = {
                "request": {
                    "url": url,
                    "headers": headers
                }
            }

            try:
                LOGGER.debug("Getting attachements from API: %s", url, extra=tags)
                #return [HostAttachment(host_attachment_id="abc",storage_uri="gs://wsh-monolith_attachment-dev/AMDocuments2/9381/20240716103314big_adult2.png",file_name="test.png")]
                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False), timeout=self.default_timeout) as session:
                    async with session.get(url, headers=headers) as response:
                        end_time = now_utc()
                        response_text = await response.text()

                        tags.update({
                            "status": response.status,
                            "elapsed_time": (end_time - start_time).total_seconds(),
                            "response": {
                                "body": response_text
                            }
                        })

                        LOGGER.debug("Get Attachments response text: %s",response_text, extra=tags)
                        if response.status==200 and response_text:
                            
                            Metric.send(Metric.MetricType.HHH_ATTACHMENTS_GET, tags=tags, branch="success")
                            
                            if response_text.startswith("//"):
                                response_text = response_text[2:]
                            response_text = response_text.replace("<*>","")
                            attachments = json.loads(response_text)
                            LOGGER.debug("Get Attachments response deserialized: %s",attachments, extra=tags)
                            host_attachments:HostAttachment = []
                            for k,v in attachments.items():
                                file_name = v.get("PATH").split("/")[-1]

                                if file_name[:14].isdigit():
                                    file_name = file_name[14:]
                                    file_date = file_name[:14]

                                if v.get("CLINICKEY") == tenant_id and v.get("PATIENTKEY") == patient_id:
                                    LOGGER.debug("Attachment added: %s, %s", k, v.get("PATH"), extra=tags)
                                    uploaded_date = v.get("UPLOADDATE")
                                    if uploaded_date:
                                        date_object = datetime.strptime(uploaded_date, "%B, %d %Y %H:%M:%S")
                                        iso_format_date = date_object.isoformat()
                                        cst_timezone = pytz.timezone("US/Central")  # CST timezone
                                        localized_dt = cst_timezone.localize(date_object)
                                        # Step 4: Convert to UTC
                                        utc_dt = localized_dt.astimezone(pytz.utc)
                                        today = datetime.utcnow()
                                        utc_timezone = pytz.timezone("UTC")  # CST timezone
                                        localized_utc_dt = utc_timezone.localize(today)
                                        difference_in_hours = (localized_utc_dt - utc_dt).total_seconds()/3600
                                        LOGGER.debug("Uploaded date: %s, UTC date: %s, difference in hours: %s", iso_format_date, localized_utc_dt, difference_in_hours, extra=tags)
                                        LOGGER.debug("Uploaded date cut off window in days: %s", uploaded_date_cut_off_window_in_days, extra=tags)

                                        attachment_tags = {
                                            "attachment": {
                                                "host_attachment_id": k,
                                                "storage_uri": v.get("PATH"),
                                                "file_name": file_name,
                                                "active": False if v.get("ACTIVE") == 0 else True
                                            },
                                            "upload_window": {
                                                "difference_in_hours": difference_in_hours,
                                                "uploaded_date_cutoff_window": uploaded_date_cut_off_window_in_days * 24
                                            }
                                        }
                                        attachment_tags.update(tags)

                                        if difference_in_hours <= uploaded_date_cut_off_window_in_days*24:
                                            host_attachments.append(HostAttachment(
                                            host_attachment_id=k,
                                            storage_uri=v.get("PATH"),
                                            file_name=file_name,
                                            active = False if v.get("ACTIVE") == 0 else True,
                                            ))
                                            Metric.send(Metric.MetricType.HHH_ATTACHMENT_ACCEPTED, tags=attachment_tags)
                                        else:
                                            LOGGER.warn("Attachment (%s) discarded.  Uploaded date (%s) is older than cut off window (%s)", v.get("PATH"), iso_format_date, uploaded_date_cut_off_window_in_days, extra=attachment_tags)                                                                                        
                                            Metric.send(Metric.MetricType.HHH_ATTACHMENT_SKIPPED, tags=attachment_tags, branch="uploaded_date_outside_window")
                                    else:
                                        LOGGER.warn("Attachment (%s) discarded.  Uploaded date is missing", v.get("PATH"), extra=tags)
                                        Metric.send(Metric.MetricType.HHH_ATTACHMENT_SKIPPED, tags=tags, branch="uploaded_date_missing")
                                else:
                                     LOGGER.warn("Attachment discarded.  ClinicKey (%s != %s) or patientKey (%s != %s) did not match", v.get("CLINICKEY"), tenant_id, v.get("PATIENTKEY"), patient_id, extra=tags)
                                     Metric.send(Metric.MetricType.HHH_ATTACHMENT_SKIPPED, tags=tags, branch="clinic_or_patient_key_mismatch")
                            LOGGER.debug("Get Attachments response: %s", host_attachments, extra=tags)
                            return host_attachments
                        else:
                            LOGGER.error("Error invoking get attachments request: status: %s response: %s", response.status, response_text, extra=tags)
                            Metric.send(Metric.MetricType.HHH_ATTACHMENTS_GET, tags=tags, branch="error")
                            raise Exception(f"Error invoking get attachments request: status: {response.status} response: {response_text}")
            except Exception as e:
                end_time = now_utc()
                tags.update({
                    "error": exceptionToMap(e),
                    "elapsed_time": (end_time - start_time).total_seconds()
                })
                LOGGER.error("Exception getting attachments from external system: %s", str(e), extra=tags)
                Metric.send(Metric.MetricType.HHH_ATTACHMENTS_GET, tags=tags, branch="internalerror")
                raise e

    async def get_classifications(self, token: str):
        with await opentelemetry.getSpan("getClassifications") as span:
            start_time = now_utc()

            url = f"{self.external_medications_url}rest/V1/MedicationProfile/ClassificationIds"
            headers = {"token":token}

            tags = {
                "request": {
                    "url": url,
                    "headers": headers
                }
            }

            LOGGER.debug("Getting classifications from API: %s", url, extra=tags)

            try:
                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False), timeout=self.default_timeout) as session:
                    async with session.get(url, headers=headers) as response:
                        end_time = now_utc()
                        response_text = await response.text()

                        tags.update({
                            "status": response.status,
                            "elapsed_time": (end_time - start_time).total_seconds(),
                            "response": {
                                "body": response_text
                            }
                        })

                        LOGGER.debug("Get classifications response text: %s", response_text, extra=tags)
                        if response.status==200 and response_text:
                            response_text = self.clean_response(response_text)

                            ret = json.loads(response_text)

                        else:
                            LOGGER.error("Error invoking get classifications request: status: %s response: %s", response.status, response_text, extra=tags)
                            Metric.send(Metric.MetricType.HHH_CLASSIFICATION_GET, tags=tags, branch="error")
                            raise Exception(f"Error invoking get classifications request: status: {response.status} response: {response_text}")
            except Exception as e:
                end_time = now_utc()
                tags.update({
                    "error": exceptionToMap(e),
                    "elapsed_time": (end_time - start_time).total_seconds()
                })
                LOGGER.error("Exception getting classifications from external system: %s", str(e), extra=tags)
                Metric.send(Metric.MetricType.HHH_CLASSIFICATION_GET, tags=tags, branch="internalerror")

                raise e

            if ret.get("SUCCESS"):

                codes = []
                classifications = ret.get("CLASSIFICATIONIDS")
                for key, value in classifications.items():
                    code = Code.create(codekey=key, value=value)
                    codes.append(code)

                codes.sort(key=lambda x: x.value)

                response = ReferenceCodes.create(category="external", list="classification", codes=codes)

                Metric.send(Metric.MetricType.HHH_CLASSIFICATION_GET, tags=tags, branch="success")

                return response
            else:
                LOGGER.error("Error retrieving classifications.  200 returned but payload did not have SUCCESS=true", extra=tags)
                Metric.send(Metric.MetricType.HHH_CLASSIFICATION_GET, tags=tags, branch="error")
                raise Exception("Error retrieving classifications")

    async def get_attachment_metadata(self, tenant_id:str, file_name:str,external_storage_file:str) -> HostAttachmentMetadata:
        thisSpanName = "get_attachment_metadata"
        with await opentelemetry.getSpan(thisSpanName) as span:
            start_time = now_utc()

            url = f"{self.attachments_api_url}api/v1/clinics/{tenant_id}/attachments/metadata/{file_name}"

            headers = {"Authorization":'Bearer '+await self.get_client_credentials_token(HHH_ATTACHMENTS_AUTH_SERVER,HHH_ATTACHMENTS_CLIENT_ID,HHH_ATTACHMENTS_CLIENT_SECRET)}

            tags = {
                "request": {
                    "url": url,
                    "headers": headers
                }
            }

            try:
                LOGGER.debug("Getting attachement metadata from API: %s", url, extra=tags)
                #return [HostAttachment(host_attachment_id="abc",storage_uri="gs://wsh-monolith_attachment-dev/AMDocuments2/9381/20240716103314big_adult2.png",file_name="test.png")]
                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False), timeout=self.default_timeout) as session:
                    async with session.get(url, headers=headers) as response:
                        end_time = now_utc()                        

                        response_text = await response.text()

                        tags.update({
                            "status": response.status,
                            "elapsed_time": (end_time - start_time).total_seconds(),
                            "response": {
                                "body": response_text
                            }
                        })

                        LOGGER.debug("Get Attachment metadata response text: %s", response_text, extra=tags)
                        if response.status==200 and response_text:
                            if response_text.startswith("//"):
                                response_text = response_text[2:]
                            response_text = response_text.replace("<*>","")
                            attachment_metadata = json.loads(response_text)
                            attachment_metadata = attachment_metadata.get("result")
                            
                            tags.update({
                                "attachment_metadata": attachment_metadata
                            })

                            LOGGER.debug("Get Attachment metadata response deserialized: %s", attachment_metadata, extra=tags)
                            host_attachment_metadata:HostAttachmentMetadata = None
                            parsed_file_name = file_name

                            if file_name and file_name[:14].isdigit():
                                parsed_file_name = file_name[14:]
                                file_date = file_name[:14]

                            host_attachment = HostAttachment(
                                host_attachment_id=uuid4().hex,
                                storage_uri=external_storage_file,
                                file_name=parsed_file_name,
                                active = False if attachment_metadata.get("active") == 0 else True,
                            )

                            host_attachment_metadata = HostAttachmentMetadata(
                                host_attachment=host_attachment,
                                patient_id=attachment_metadata.get("patientKey"),
                                tenant_id=attachment_metadata.get("clinicKey"),
                            )

                            LOGGER.debug("Get Attachment metadata response: %s", host_attachment_metadata, extra=tags)

                            Metric.send(Metric.MetricType.HHH_ATTACHMENT_METADATA_GET, tags=tags, branch="success")

                            return host_attachment_metadata
                        elif response.status==404 or response.status==403:
                            LOGGER.info("Attachment metadata not found: %s", response_text, extra=tags)
                            Metric.send(Metric.MetricType.HHH_ATTACHMENT_METADATA_MISSING, tags=tags, branch="missing")
                            raise NotFoundException("Attachment metadata not found")
                        else:
                            LOGGER.error("Error invoking get attachments metadata request: status: %s response: %s", response.status, response_text, extra=tags)
                            Metric.send(Metric.MetricType.HHH_ATTACHMENT_METADATA_GET, tags=tags, branch="error")
                            raise Exception(f"Error invoking get attachments metadata request: status: {response.status} response: {response_text}")
            except NotFoundException as e:
                raise
            except Exception as e:
                end_time = now_utc()
                tags.update({
                    "error": exceptionToMap(e),
                    "elapsed_time": (end_time - start_time).total_seconds()
                })
                LOGGER.error("Exception getting attachments metadata from external system: %s", str(e), extra=tags)
                Metric.send(Metric.MetricType.HHH_ATTACHMENT_METADATA_GET, tags=tags, branch="internalerror")
                raise e

    async def get_client_credentials_token(self,auth_server_url:str,client_id:str, client_secret:str):
        start_time = now_utc()
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False), timeout=self.default_timeout) as session:
            payload = {"client_id": client_id, "client_secret": client_secret, "grant_type": "client_credentials"}
            tags = {
                "request": {
                    "url": auth_server_url,
                    "payload": "**SENSITIVE**"
                }
            }

            try:

                async with session.post(auth_server_url,
                                        data=payload,
                                        ) as response:
                    end_time = now_utc()
                    response_text = await response.text()

                    tags.update({
                        "status": response.status,
                        "elapsed_time": (end_time - start_time).total_seconds(),
                        "response": {
                            "body": "**SENSITIVE**"
                        }
                    })

                    LOGGER.debug("Get attachments api token: %s", response_text, extra=tags)
                    Metric.send(Metric.MetricType.HHH_AUTH, tags=tags, branch="success")
                    response = json.loads(response_text)
                    return response.get("access_token")
            
            except Exception as e:
                end_time = now_utc()
                tags.update({
                    "error": exceptionToMap(e),
                    "elapsed_time": (end_time - start_time)
                })
                LOGGER.error("Exception getting attachments api token: %s", str(e), extra=tags)
                Metric.send(Metric.MetricType.HHH_AUTH, tags=tags, branch="internalerror")
                raise e

    def clean_response(self, response_text):
        if response_text.startswith("//"):
            response_text = response_text[2:]
        response_text = response_text.replace("<*>","")
        return response_text
