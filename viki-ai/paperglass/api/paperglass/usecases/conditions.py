import json
import re
import uuid
import datetime
from typing import List
import requests
import http.client

from fhir.resources.bundle import Bundle
from fhir.resources.bundle import BundleEntry
from fhir.resources.composition import Composition
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.reference import Reference
from fhir.resources.backboneelement import BackboneElement
from fhir.resources.narrative import Narrative

from paperglass.domain.models import DocumentOperation, ExtractedCondition, MedicalCodingRawData
from paperglass.infrastructure.ports import IQueryPort
from paperglass.domain.values import ConditionICD10Code, ConditionsEvidence, DocumentOperationType, PageText
from paperglass.domain.utils.auth_utils import GCPAuth

from paperglass.settings import MEDICAL_SUMMARIZATION_API_URL, MEDICAL_SUMMARIZATION_CONFIDENCE_THRESHOLD
from paperglass.usecases.commands import ExtractConditionsData

from kink import inject

SPAN_BASE: str = "APP:ConditionsService:"
from ..domain.utils.opentelemetry_utils import OpenTelemetryUtils
opentelemetry = OpenTelemetryUtils(SPAN_BASE)

from paperglass.log import getLogger
LOGGER = getLogger(__name__)



class ConditionsService():

    def __init__(self):
       pass

    async def extract_conditions(self, command: ExtractConditionsData):

        with await opentelemetry.getSpan("extract_conditions") as span:

            document_id = command.document_id
            page_texts = command.page_texts

            data = None
            ret = None
            if page_texts:
                LOGGER.debug("Extracting conditions from document %s page text %s", document_id, page_texts)
                
                payloads =  page_texts #[self.scrub_text(page_texts)]

                data = self.build_bundle(payloads)
                
                ret = self.retrieve_conditions(data)
                
                result = self.transform_result(ret,document_id)

                LOGGER.debug("Extracted conditions from document  %s: %s", document_id, data)
                
                return data,result
            else:
                LOGGER.warning("No page text provided to extract conditions")

            return data,ret

    def build_bundle(self, payloads: List[PageText] ):

        bundle = Bundle.construct(type="collection", id=uuid.uuid4().hex)
        bundle.entry = []

        type = CodeableConcept(
            coding=[
                {
                    "system": "https://g.co/fhir/us_dev/composition-type",
                    "code": "Discharge Summary",
                    "display": "Discharge Summary"
                },
                {
                    "system": "https://g.co/fhir/us_dev/composition-title",
                    "code": "Discharge Summary",
                    "display": "Discharge Summary"
                }
            ],
            text="Discharge Summary"
        )

        compostionType = CodeableConcept(
            coding=[
                {
                    "system": "http://loinc.org",
                    "code": "11503-0",
                    "display": "Medical records"
                }
            ]
        )

        category = CodeableConcept(
            coding=[
                {
                    "system": "https://g.co/fhir/us_dev/composition_class",
                    "code": "generic",
                    "display": "generic"
                }
            ]
        )

        patient = Reference(reference="Patient/pat-123")
        encounter = Reference(reference="Encounter/enc-456")
        practitioner = Reference(reference="Practitioner/prac-789")

        for payload in payloads:
            #print(payload)
            #print("=========================================================")
            narrative = Narrative(
                status = "additional",
                div = ''.join(filter(lambda x: x.isalnum() or x.isspace() or x in ['.', ',', '-', '/', ':', '#', '^', '@', '!', '(', ')', '&', '%', '$', '\'', '+', '_', '?', '<', '>', '=', '[', ']'], payload.text))) #Causing issue  *

                #div = re.sub("[^\x00-\x7F]"," ", payload)) #replace any non-ascii characters by space

                #div = "History of Present Illness: This is a 57-year-old man with a past medical history notable for coronary artery disease, diabetes, hypertension, and hyperlipidemia admitted with severe community acquired pneumonia complicated by sepsis and AKI. \\n\\nHe reported four to five days of progressive shortness of breath and subjective fevers. He reported ill contacts with his grandchildren, who live with him, and who had URI symptoms. His symptoms progressed, and on the day of admission, he noted that he was breathless with minimal exertion, with a temperature at home of 102. He was initially hypoxemic, and transiently hypotensive on presentation. Initial evaluation was notable for bilateral lower lung opacities consistent with pneumonia. He was also noted to be febrile with leukocytosis and new evidence of acute renal insufficiency.\\n\\nProcedures: \\nRight internal jugular triple lumen CVL placed on Jan 15, 2019\\n\\nHospital Course: The patient was stabilized in the emergency room and admitted to the medical floor. A central line was placed for fluid resuscitation. He responded well to several days of broad-spectrum antibiotic coverage, and an initial 3 L fluid resuscitation. Over the course of his hospitalization, his hemodynamic condition stabilized, and his renal insufficiency improved.\\n \\nAlthough the patient has a history of diabetes, his blood sugars have been well controlled with diet alone, and he did not require insulin coverage while hospitalized, even in the setting of acute intercurrent illness. His diuretics and antihypertensive meds were held for the first few days of his hospitalization; these have been reintroduced, and he is tolerating his usual home medication regimen.\\n \\nMedications on admission:\\nLipitor 40mg daily\\nAspirin 81mg daily\\nMetoprolol XL 50mg daily\\nAzilsartan/ Chlorthalidone 40mg/12.5 mg daily\\n\\nLab Results:\\nHba1c 7.4. Glucose 112.\\n\\nImaging Results:\\nCXR - bilateral lower-lobe predominant airspace disease with small effusions, consistent with pneumonia.\\n\\nDischarge Medications:\\nAtorvastatin 80mg daily\\nAspirin 81mg daily\\nMetoprolol XL 50mg daily\\nAzilsartan/ Chlorthalidone 40mg/12.5 mg daily \\n\\nDischarge Instructions:\\nYou were admitted with severe pneumonia that resulted in low blood pressure, low oxygen levels and mild kidney injury. You were treated with fluids and antibiotics, and medications for your chronic conditions. We conducted several studies which did not show any complications of the need for other procedures. You are improving but need to make sure of the following:\\nContinue to take all medications as prescribed\\nYou have completed the full course of antibiotics required for your infection\\nYou will resume all of your prior medications \\nYou should have follow up labs in the next two weeks to confirm your kidney function has returned to normal.\\nUntil then, avoid NSAIDS (medications like Advil and Aleve), as these can hurt your kidney function")
                #div = "History of Present Illness: This is a 57-year-old man with a past medical history notable for coronary artery disease, diabetes, hypertension, and hyperlipidemia admitted with severe community acquired pneumonia complicated by sepsis and AKI. \\n\\nHe reported four to five days of progressive shortness of breath and subjective fevers. He reported ill contacts with his grandchildren, who live with him, and who had URI symptoms. His symptoms progressed, and on the day of admission, he noted that he was breathless with minimal exertion, with a temperature at home of 102. He was initially hypoxemic, and transiently hypotensive on presentation. Initial evaluation was notable for bilateral lower lung opacities consistent with pneumonia. He was also noted to be febrile with leukocytosis and new evidence of acute renal insufficiency.\\n\\nProcedures: \\nRight internal jugular triple lumen CVL placed on Jan 15, 2019\\n\\nHospital Course: The patient was stabilized in the emergency room and admitted to the medical floor. A central line was placed for fluid resuscitation. He responded well to several days of broad-spectrum antibiotic coverage, and an initial 3 L fluid resuscitation. Over the course of his hospitalization, his hemodynamic condition stabilized, and his renal insufficiency improved.\\n \\nAlthough the patient has a history of diabetes, his blood sugars have been well controlled with diet alone, and he did not require insulin coverage while hospitalized, even in the setting of acute intercurrent illness. His diuretics and antihypertensive meds were held for the first few days of his hospitalization; these have been reintroduced, and he is tolerating his usual home medication regimen.\\n \\nMedications on admission:\\nLipitor 40mg daily\\nAspirin 81mg daily\\nMetoprolol XL 50mg daily\\nAzilsartan/ Chlorthalidone 40mg/12.5 mg daily\\n\\nLab Results:\\nHba1c 7.4. Glucose 112.\\n\\nImaging Results:\\nCXR - bilateral lower-lobe predominant airspace disease with small effusions, consistent with pneumonia.\\n\\nDischarge Medications:\\nAtorvastatin 80mg daily\\nAspirin 81mg daily\\nMetoprolol XL 50mg daily\\nAzilsartan/ Chlorthalidone 40mg/12.5 mg daily \\n\\nDischarge Instructions:\\nYou were admitted with severe pneumonia that resulted in low blood pressure, low oxygen levels and mild kidney injury. You were treated with fluids and antibiotics, and medications for your chronic conditions. We conducted several studies which did not show any complications of the need for other procedures. You are improving but need to make sure of the following:\\nContinue to take all medications as prescribed\\nYou have completed the full course of antibiotics required for your infection\\nYou will resume all of your prior medications \\nYou should have follow up labs in the next two weeks to confirm your kidney function has returned to normal.\\nUntil then, avoid NSAIDS (medications like Advil and Aleve), as these can hurt your kidney function\\nIt is OK to take tylenol as needed for pain\\n\\nFollow-up:\\nPrimary Care - please call to set up an appointment in the next two weeks\\nEndocrine - we have scheduled you for an endocrinologist appointment on June 12, 2019\\nPlease call your Primary Care provider if you develop any new or worsening symptoms related to your pneumonia, including shortness of breath, chest pain, wheezing, fever, or night sweats.\"}}]}},{\"resource\":{\"resourceType\":\"Composition\",\"id\":\"MT-4\",\"meta\":{\"extension\":[{\"url\":\"https://g.co/fhir/medicalrecords/sourceIdentifier\",\"valueIdentifier\":{\"system\":\"urn:google:health:source:us_dev\",\"value\":\"MT-4\"}}]},\"status\":\"final\",\"type\":{\"coding\":[{\"system\":\"https://g.co/fhir/us_dev/composition-type\",\"code\":\"Progress\",\"display\":\"Progress\"},{\"system\":\"https://g.co/fhir/us_dev/composition-title\",\"code\":\"Office Visit - Endocrinology\",\"display\":\"Office Visit - Endocrinology\"}],\"text\":\"Progress\"},\"category\":[{\"coding\":[{\"system\":\"https://g.co/fhir/us_dev/composition_class\",\"code\":\"generic\",\"display\":\"generic\"}],\"text\":\"generic\"}],\"subject\":{\"reference\":\"Patient/V-12345\"},\"encounter\":{\"reference\":\"Encounter/MT-2\"},\"date\":\"2019-06-12T09:15:00+00:00\",\"author\":[{\"reference\":\"Practitioner/5\"},{\"reference\":\"PractitionerRole/5\"}],\"title\":\"Office Visit - Endocrinology\",\"section\":[{\"text\":{\"status\":\"additional\",\"div\":\"Reason for visit: Diabetes management\\n\\nInterval update: 58-year-old man with past medical history notable for coronary artery disease status post non-ST elevation MI with BMS in LAD, diabetes mellitus type 2, hypertension, and hyperlipidemia presents for annual followup of diet-controlled DM2.\\n \\nPatient was hospitalized in January with severe CAP, resulting in AKI. His creatinine was 1.3 on discharge but this hasn’t been repeated. His glycemic control was initially poor in the setting of critical illness, but this improved within 24h and he was managed throughout his course with sliding scale insulin (no doses required).\\n \\nOverall, patient feels well. Denies visual changes, chest pain, shortness of breath, weight gain, edema, increased thirst, or change in urination. He reports walking 2-3x per week with wife, usually for 30-45 minutes on level ground. Diet has been consistent but has had some lapses while traveling this summer.\\n \\nPast Medical History:\\nCoronary artery disease - had NSTEMI in 2012 rx with BMS in LAD\\nDM2, not on insulin, diet-controlled\\nHypertension\\nHyperlipidemia\\n\\nMedications:\\nAspirin 81mg daily\\nMetoprolol XL 50mg daily\\nLipitor 60mg daily\\nAzilsartan/ Chlorthalidone 40mg/12.5 mg daily\\n\\nAllergies and Adverse Reactions:\\nLatex\\nBactrim\\nPeanuts\\n\\nSocial History:\\nDenies smoking, rare alcohol\\nLives with wife\\n\\nFamily History:\\nNo history of diabetes in immediate family members\\n\\nVital Signs: \\nHeart rate - 92\\nResp rate - 14\\nBP - 139/91\\nSpO2 - 99%\\nTemp - 36.3\\nWeight - 191 lbs\\nHeight - 5 ft 9 inches\\nBMI - 28.2\\n\\nPhysical Examination:\\nWell-developed man in NAD \\nPERRL, EOMI. Fundoscopic exam limited but within normal limits\\nO/p moist, no lesions\\nChest clear bilaterally \\nRRR s1s2s4, no murmurs\\nSoft, normoactive bowel sounds, no masses\\nWarm / well perfused B. \\nPulses are normal and symmetric, cap refill is not reduced.\\nFoot exam - no lesions, monofilament test normal, normal proprioception B\\n\\nLab Results:\\nGlucose 100, HgA1C 6.5\\n\\nReports\\nRetinopathy screening study - reviewed with patient, >12 months since this was obtained\\n\\nAssessment and Plan:\\n58-year-old man with a past medical history notable for coronary artery disease, hypertension, hyperlipidemia presents for longitudinal management of diabetes:\\n\\nDM2 - Well-controlled with diet alone, even during recent hospitalization. Encouraged the patient to continue to increase his regular physical exercise and continue to follow his heart health diet. He is due for his annual retinopathy screening, and should have a follow-up creatinine checked given his recent AKI. The remainder of his regimen was reviewed; agree with management and do not see other opportunities to optimize his diabetes care.\\n\\nThanks for involving me; I’ll plan to see him again next year, or sooner if needed.")

            composition = Composition(
                id = payload.pageNumber,
                status = "final",
                type = type,
                #subject = [patient],
                category = [category],
                encounter = encounter,
                date = datetime.datetime.now(datetime.timezone.utc), # 2019-01-20T06:45:00+00:00,
                author = [practitioner],  # Use a list of Reference objects
                title = "Medical Records",
                section = [{
                "text": narrative
                }])

            entry = BundleEntry.construct()
            entry.resource = composition
            bundle.entry.append(entry)
        
        data = {
            "fhirBundle": bundle.json(),
            "conditions_summary_config": {
                "confidence_threshold": MEDICAL_SUMMARIZATION_CONFIDENCE_THRESHOLD
            }
        }

        return data
    
    def transform_result(self, data: dict, document_id: str):
        
        def extract_evidence(json_snippet, document_id):
            """
            Extracts evidence snippet text, start position, and end position from a JSON snippet.

            Args:
                json_snippet: The JSON snippet containing the evidence data.

            Returns:
                A list of objects, each containing the extracted information.
            """
            start_position= -1
            end_position = -1
            evidence_snippet = 'N/A'
            evidence_reference = ''
            extracted_data = []
            
            if 'evidence' in json_snippet:
                for evidence_item in json_snippet['evidence']: # evidence array
                    if 'detail' in evidence_item:
                        for detail_item in evidence_item['detail']: # detail array
                            if 'reference' in detail_item:
                                evidence_reference =  detail_item['reference'].replace("Composition", "DocumentId/"+ document_id + "/Page")
                            if 'extension' in detail_item:
                                for extension_item in detail_item['extension']: # ext array
                                    if 'extension' in extension_item:
                                        for sub_extension in extension_item['extension']: # inner ext array
                                            if 'url' in sub_extension and sub_extension['url'] == 'evidenceSnippet':
                                                evidence_snippet = sub_extension.get('valueString', 'N/A')
                                            if 'url' in sub_extension and sub_extension['url'] == 'evidenceSnippetCharInterval':
                                                for int_extension in sub_extension['extension']: # inner inner ext  array
                                                    if 'url' in int_extension and int_extension['url'] == 'startPosition':
                                                        start_position = int_extension.get('valueInteger', -1)
                                                    if 'url' in int_extension and int_extension['url'] == 'endPosition':
                                                        end_position = int_extension.get('valueInteger', -1)
                                        extracted_data.append({
                                            "evidenceSnippet": evidence_snippet,
                                            "startPosition": start_position,
                                            "endPosition": end_position,
                                            "evidenceReference": evidence_reference
                                        })
            return extracted_data
        
        def extract_icd_codes(data, document_id):
            """
            Extracts ICD-10 codes from a dictionary containing a 'coding' key.

            Args:
                data: A dictionary containing a 'coding' key with a list of code dictionaries.

            Returns:
                A list of ICD-10 codes.
            """
            icd_codes = []
            category = data['code'].get('text')
            for coding in data['code']['coding']:
                if coding['system'] == 'http://hl7.org/fhir/sid/icd-10':
                    description = coding.get('display')
                    icd_codes.append({
                        "icdCode": coding['code'],
                        "description": description,
                        "category": category
                        })
            return icd_codes

        def extract_data(fhir_bundle_json,document_id):
            extracted_data = []
            #import pdb;pdb.set_trace()
            fhir_bundle_json = json.loads(fhir_bundle_json)

            if 'entry' not in fhir_bundle_json.keys():
                return extracted_data
            
            for entry in fhir_bundle_json['entry']:
                if 'resource' in entry and entry['resource']['resourceType'] != 'Condition':
                    continue
                condition = entry['resource']
                conditionId = condition['id']
                verificationStatus = condition['verificationStatus']['coding'][0]['code']
                category = condition['category'][0]['text']
                clinicalStatus = condition['clinicalStatus']['text']

                extracted_data.append({
                    "conditionId": conditionId,
                    "verificationStatus": verificationStatus,
                    "category": category,
                    "clinicalStatus": clinicalStatus,
                    "icd10Codes": extract_icd_codes(condition, document_id),
                    "evidences": extract_evidence(condition, document_id)
                    })
            return extracted_data

        return extract_data(data["fhirBundle"],document_id)

    def retrieve_conditions(self, data: dict):
        
        headers = {
            'Authorization': 'Bearer ' + self.get_token(),
            'Content-Type': 'application/json',
        }                

        response = requests.post(
            MEDICAL_SUMMARIZATION_API_URL,
            headers = headers,
            json = data
        )

        ret = response.json()
        return ret        

    def get_token(self):
        return GCPAuth().auth_token()

    def scrub_text(self, text: str):
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text
    
    @inject
    async def get_extracted_conditins(self, document_ids: List[str], query:IQueryPort):
        transformed_conditions = []
        for doc_id in document_ids:

            doc_operation:DocumentOperation = await query.get_document_operation_by_document_id(doc_id, 
                                                                                                DocumentOperationType.MEDICATION_EXTRACTION.value)
            
            if doc_operation:
                extracted_conditions: List[MedicalCodingRawData] =  await query.get_extracted_conditions_by_document_operation_instance(doc_id, 
                                                                                                                                    doc_operation.active_document_operation_instance_id)

                for extracted_condition in extracted_conditions:
                    for code_group in extracted_condition.medical_coding_data:

                        icd10_codes = [ConditionICD10Code(
                                    icd_code = x.get('icdCode', 'N/A'),
                                    description = x.get('description', 'N/A'),
                                    category = x.get('category', 'N/A')
                                ) for x in code_group.get("icd10Codes", [])]
                        
                        evidences = [ConditionsEvidence(
                                    evidence_snippet = x.get('evidenceSnippet', 'N/A'),
                                    start_position = x.get('startPosition', -1),
                                    end_position = x.get('endPosition', -1),
                                    evidence_reference = x.get('evidenceReference', []),
                                    document_id = x.get('evidenceReference',"").split("/")[1],
                                    page_number = int(x.get('evidenceReference',"").split("/")[3])
                                ) for x in code_group.get('evidences', [])]

                        transformed_conditions.append(
                            ExtractedCondition(
                                condition_id = icd10_codes[0].category,
                                category = icd10_codes[0].category,
                                icd10_codes = icd10_codes,
                                evidences = evidences,
                            )
                        )

        return transformed_conditions