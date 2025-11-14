import sys, os
import asyncio
import json
from typing import List
from kink import inject
from base64 import b64encode
import pandas as pd
import spacy


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from paperglass.entrypoints.utils.goldendataset_compare_utils import find_common_keys
from paperglass.domain.values import ResolvedReconcilledMedication
from paperglass.domain.models import Document, DocumentOperationInstanceLog
from paperglass.infrastructure.ports import IQueryPort
from paperglass.interface.ports import ICommandHandlingPort
from paperglass.usecases.medications import get_resolved_reconcilled_medications_v3
from paperglass.usecases.orchestrator import orchestrate
from paperglass.domain.model_testing import TestDataDetails, TestExpected
from paperglass.infrastructure.adapters.google import GoogleStorageAdapter
from paperglass.settings import GCP_PROJECT_ID, CLOUD_PROVIDER
from paperglass.tests.test_automation.dev.orchestration.test_data import test_data
from paperglass.domain.time import now_utc
from paperglass.usecases.commands import CreateGoldenDatasetTest

from paperglass.log import CustomLogger

LOGGER = CustomLogger(__name__)

nlp = spacy.load("en_core_web_md")

GCS_TEST_BUCKET = "viki-test"
report_file_name = f"medication_test_report_{now_utc()}.xlsx"
patient_id_pro = "6b40380207e04c1b95c896310faa0670"
patient_id_new = "cbc5d994c913451eb8ec9db880413811"
gsutil_uri = f"gs://viki-test/reports/"

def mktoken(app_id, tenant_id, patient_id):
    return b64encode(json.dumps({'app_id': app_id, 'tenant_id': tenant_id, 'patient_id': patient_id}).encode()).decode()


def is_medication_in_document(medication, document_id):
    if medication.get("extracted_medication_reference"):
        for extracted_reference in medication.get("extracted_medication_reference"):
            if extracted_reference.get("document_id") == document_id:
                return True
    return False


def extract_medication_info(medication_data):
    extracted_info = []

    for item in medication_data:
        medication = item.get('medication', {})
        extracted_medication_reference = item.get('extracted_medication_reference', [{}])[0]

        extracted_info.append(
            {
                'medispan_id': medication.get('medispan_id'),
                'name': medication.get('name'),
                'dosage': medication.get('dosage'),
                'form': medication.get('form'),
                'frequency': medication.get('frequency'),
                'instructions': medication.get('instructions'),
                'route': medication.get('route'),
                'start_date': medication.get('start_date'),
                'strength': medication.get('strength'),
                'document_id': extracted_medication_reference.get('document_id'),
                'document_operation_instance_id': extracted_medication_reference.get('document_operation_instance_id'),
                'extracted_medication_id': extracted_medication_reference.get('extracted_medication_id'),
                'page_number': extracted_medication_reference.get('page_number'),
            }
        )

    return extracted_info


@inject
async def get_medication_profile(document_id, patient_id, tenant_id, app_id, query: IQueryPort):
    return await get_resolved_reconcilled_medications_v3(document_id, patient_id, app_id, tenant_id, query)


@inject
async def get_document(document_id: str, query_adapter: IQueryPort):
    doc = await query_adapter.get_document(document_id=document_id)
    return Document(**doc)


@inject
async def run_test_orchestrator_with_def_id(document: Document, def_id: str, query: IQueryPort):
    await orchestrate(
        document_id=document.id, force_new_instance=True, priority="high", document_operation_def_id=def_id
    )
    if def_id == "4d3f0b2aa2c811ef9e0b3e3297f4bd07":
        await asyncio.sleep(10)
        doc_operation_instance_log: DocumentOperationInstanceLog = (
            await query.get_document_operation_instance_log_by_step_id_and_status(
                document_id=document.id, status="IN_PROGRESS", step_id="MEDICATION_PROFILE_CREATION"
            )
        )
        while doc_operation_instance_log:
            await asyncio.sleep(10)
            doc_operation_instance_log: DocumentOperationInstanceLog = (
                await query.get_document_operation_instance_log_by_step_id_and_status(
                    document_id=document.id, status="IN_PROGRESS", step_id="MEDICATION_PROFILE_CREATION"
                )
            )
    db_medication_profile = await get_medication_profile(
        document.id, document.patient_id, document.tenant_id, document.app_id, query
    )
    return db_medication_profile


async def get_extracted_medication_list(doc_id: str):
    list_of_medication_profiles_expected = []
    list_of_medication_profiles_actual = []
    document = await get_document(doc_id)
    LOGGER.debug(f"Old Orchestrator start for : {doc_id}")
    expected_medication_profiles = await run_test_orchestrator_with_def_id(
        document, def_id="bda2081860f611ef91b73e3297f4bd07"
    )
    LOGGER.debug(f"Old Orchestrator end for : for {doc_id}_{expected_medication_profiles}")
    list_of_medication_profiles_expected.extend(extract_medication_info(expected_medication_profiles))
    actual_medication_profiles = await run_test_orchestrator_with_def_id(
        document, def_id="4d3f0b2aa2c811ef9e0b3e3297f4bd07"
    )
    LOGGER.debug(f"Old Orchestrator end for : for {doc_id}_{expected_medication_profiles}")
    list_of_medication_profiles_actual.extend(extract_medication_info(actual_medication_profiles))
    return list_of_medication_profiles_expected, list_of_medication_profiles_actual


async def get_extracted_medication_From_doc(golden_data_set_doc_id, target_data_set_doc_id):
    extracted_expected_medication: List[ResolvedReconcilledMedication] = await get_medication_profile(
        golden_data_set_doc_id, patient_id_pro, "54321", "007"
    )
    target_medication: List[ResolvedReconcilledMedication] = await get_medication_profile(
        target_data_set_doc_id, patient_id_new, "54321", "007"
    )
    (
        element_check,
        no_match_count_total,
        medispan_blank_total,
        medispan_mismatch_total,
        no_expected_medications,
        no_actual_medications,
        medication_different_count_total,
        missing_in_expected_total,
        missing_in_actual_total,
        field_mismatch_counts,
        list_of_medispan_ids, 
        element_new
    ) = await compare_medication_profiles_3(extracted_expected_medication, target_medication)
    return (
        element_check,
        no_match_count_total,
        medispan_blank_total,
        medispan_mismatch_total,
        no_expected_medications,
        no_actual_medications,
        medication_different_count_total,
        missing_in_expected_total,
        missing_in_actual_total,
        field_mismatch_counts,
        list_of_medispan_ids, 
        element_new
    )


async def compare_medication_profiles_3(
    expected_medications: List[ResolvedReconcilledMedication], actual_medications: List[ResolvedReconcilledMedication]
):
    element_check = []
    elements_list = []
    no_match_count_total = 0
    medispan_blank_total = 0
    medispan_mismatch_total = 0
    matched_actual_medication_tracker = []
    missing_in_actual_total = 0
    missing_in_expected_total = 0
    medication_different_count_total = 0
    field_mismatch_counts = {}
    list_of_medispan_ids = []  # New list to store non-blank medispan IDs
    element_new = []

    # Collect non-blank medispan IDs from actual medications
    for actual_med in actual_medications:
        if actual_med.medication.medispan_id and actual_med.medication.medispan_id not in list_of_medispan_ids:
            list_of_medispan_ids.append(actual_med.medication.medispan_id)

    for expected_med in expected_medications:
        matched_actual_med = [x for x in actual_medications if x.medication.matches(expected_med.medication)]

        # Another pass to check if we can match by ignoring the medispanId
        if not matched_actual_med and expected_med.medispan_id is not None:
            matched_actual_med = [
                x for x in actual_medications if x.medication.match_ignore_medispanid(expected_med.medication)
            ]

        if matched_actual_med:
            matched_actual_medication_tracker.extend([x.id for x in matched_actual_med])
            expected_medication = expected_med.medication.dict()
            expected_medication["page_number"] = ",".join(
                [str(x.page_number) for x in expected_med.extracted_medication_reference]
            )

            actual_medication = matched_actual_med[0].medication.dict()
            actual_medication["page_number"] = ",".join(
                [str(x.page_number) for x in matched_actual_med[0].extracted_medication_reference]
            )

            common_key_result = find_common_keys(expected_medication, actual_medication)

            elements_list = common_key_result["common_list"]
            no_match_count_total += common_key_result["no_match_count"]
            medispan_blank_total += common_key_result["medispan_blank"]
            medispan_mismatch_total += common_key_result["medispan_mismatch"]
            missing_in_actual_total += len(common_key_result["missing_in_actual"])
            missing_in_expected_total += len(common_key_result["missing_in_expected"])
            medication_different_count_total += common_key_result["medication_different_count"]

            # Capture field mismatch counts
            for field, count in common_key_result.items():
                if field.endswith('_mismatch'):
                    if field not in field_mismatch_counts:
                        field_mismatch_counts[field] = 0
                    field_mismatch_counts[field] += count

            element_dict = {}
            for element in elements_list:
                LOGGER.debug(f"Element : {element}")
                if element['Key'] == "medispan_id" and element['match'] == False:
                    element_check.append(
                        {
                            "field_name": element['Key'],
                            "expected_value": element['expected'],
                            'actual_value': element['actual'],
                            "match": element['match'],
                            "unmatched_expected_name": expected_med.medication.name,
                            "unmatched_actual_name": matched_actual_med[0].medication.name,
                        }
                    )
                else:
                    element_check.append(
                        {
                            "field_name": element['Key'],
                            "expected_value": element['expected'],
                            'actual_value': element['actual'],
                            "match": element['match'],
                        }
                    )
                element_dict[element['Key']] = element['actual']    
            element_new.append(element_dict)   
        else:
            common_key_result = {
                "common_list": [
                    {"Key": "name", "expected": expected_med.medication.name, "actual": "", "match": False},
                    {
                        "Key": "medispan_id",
                        "expected": expected_med.medication.medispan_id,
                        "actual": "",
                        "match": False,
                    },
                    {"Key": "dosage", "expected": expected_med.medication.dosage, "actual": "", "match": False},
                    {"Key": "form", "expected": expected_med.medication.form, "actual": "", "match": False},
                    {"Key": "frequency", "expected": expected_med.medication.frequency, "actual": "", "match": False},
                    {
                        "Key": "instructions",
                        "expected": expected_med.medication.instructions,
                        "actual": "",
                        "match": False,
                    },
                    {"Key": "start_date", "expected": expected_med.medication.start_date, "actual": "", "match": False},
                    {"Key": "route", "expected": expected_med.medication.route, "actual": "", "match": False},
                    {"Key": "strength", "expected": expected_med.medication.strength, "actual": "", "match": False},
                    {
                        "Key": "page_number",
                        "expected": ",".join([str(x.page_number) for x in expected_med.extracted_medication_reference]),
                        "actual": "",
                        "match": False,
                    },
                ],
                "no_match_count": 1,
                "medispan_blank": 1,
                "medispan_mismatch": 0,
            }

            elements_list = common_key_result["common_list"]
            missing_in_actual_total += 1
            medication_different_count_total += 1
            for element in elements_list:
                no_match_count_total += 1
                element_check.append(
                    {
                        "field_name": element['Key'],
                        "expected_value": element['expected'],
                        'actual_value': "",
                        "match": element['match'],
                    }
                )

    for actual_med in actual_medications:
        if actual_med.id not in matched_actual_medication_tracker:
            common_key_result = {
                "common_list": [
                    {"Key": "name", "expected": "", "actual": actual_med.medication.name, "match": False},
                    {"Key": "medispan_id", "expected": "", "actual": actual_med.medication.medispan_id, "match": False},
                    {"Key": "dosage", "expected": "", "actual": actual_med.medication.dosage, "match": False},
                    {"Key": "form", "expected": "", "actual": actual_med.medication.form, "match": False},
                    {"Key": "frequency", "expected": "", "actual": actual_med.medication.frequency, "match": False},
                    {
                        "Key": "instructions",
                        "expected": "",
                        "actual": actual_med.medication.instructions,
                        "match": False,
                    },
                    {"Key": "start_date", "expected": "", "actual": actual_med.medication.start_date, "match": False},
                    {"Key": "route", "expected": "", "actual": actual_med.medication.route, "match": False},
                    {"Key": "strength", "expected": "", "actual": actual_med.medication.strength, "match": False},
                    {
                        "Key": "page_number",
                        "expected": "",
                        "actual": ",".join([str(x.page_number) for x in actual_med.extracted_medication_reference]),
                        "match": False,
                    },
                ],
                "no_match_count": 1,
                "medispan_blank": 1,
                "medispan_mismatch": 0,
            }

            elements_list = common_key_result["common_list"]
            missing_in_expected_total += 1
            medication_different_count_total += 1
            element_dict = {}
            for element in elements_list:
                no_match_count_total += 1
                element_check.append(
                    {
                        "field_name": element['Key'],
                        "expected_value": "",
                        'actual_value': element['actual'],
                        "match": element['match'],
                    }
                )
                element_dict[element['Key']] = element['actual']
            element_new.append(element_dict)

    return (
        element_check,
        no_match_count_total,
        medispan_blank_total,
        medispan_mismatch_total,
        len(expected_medications),
        len(actual_medications),
        medication_different_count_total,
        missing_in_expected_total,
        missing_in_actual_total,
        field_mismatch_counts,
        list_of_medispan_ids,
        element_new
    )


@inject
async def updateGoldenDataSet(
    element_new, list_of_medispan_ids, ex_document_id, expected_no_of_medication, report_file_name, query: IQueryPort, commands: ICommandHandlingPort
):
    extracted_data = element_new
    # extracted_data = [{'field_name': item['field_name'], 'expected_value': item['actual_value']} for item in results]
    listed = len(list_of_medispan_ids)
    unlisted = int(expected_no_of_medication) - listed
    test_details = TestExpected(total_count=expected_no_of_medication, medispan_matched_count=listed, unlisted_count=unlisted,list_of_medispan_ids= list_of_medispan_ids, medication=extracted_data)
    test_data_new = TestDataDetails.create(
        app_id="007",
        tenant_id="54321",
        patient_id=patient_id_pro,
        document_id=ex_document_id,
        test_document=report_file_name,
        test_expected=test_details,
    )
    test_data_create_command: CreateGoldenDatasetTest = CreateGoldenDatasetTest(test_data=test_data_new)
    await commands.handle_command(test_data_create_command)


@inject
async def save_results_to_file(
    results,
    element_new,
    no_match_count,
    ex_document_id,
    actual_doc_id,
    medispan_blank,
    medispan_mismatch,
    expected_no_of_medication,
    actual_no_of_medication,
    report_file_name,
    medication_different_count_total,
    missing_in_expected_total,
    missing_in_actual_total,
    field_mismatch_counts,
    list_of_medispan_ids,  # New parameter
    query: IQueryPort,
):
    columns = [
        'filename',
        'expected_document_id',
        'actual_document_id',
        'field_name',
        'expected_value',
        'actual_value',
        'match',
        'unmatched_expected_name',
        'unmatched_actual_name',
    ]
    new_df = pd.DataFrame(results, columns=columns)
    new_df['expected_document_id'] = ex_document_id
    new_df['actual_document_id'] = actual_doc_id
    document: Document = Document(**await query.get_document(actual_doc_id))
    filename = document.file_name
    new_df['filename'] = filename
    await updateGoldenDataSet(element_new,list_of_medispan_ids, actual_doc_id, actual_no_of_medication, filename) # always commented unless adding new data to golden dataset
    
    if os.path.exists(report_file_name):
        if report_file_name.endswith('.xlsx'):
            with pd.ExcelWriter(report_file_name, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                # Read existing data
                existing_df = pd.read_excel(report_file_name, sheet_name='Results')
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                combined_df.to_excel(writer, sheet_name='Results', index=False)

                # Add or update the worksheet for "Summary"
                if 'Summary' in writer.book.sheetnames:
                    summary_df = pd.read_excel(report_file_name, sheet_name='Summary')
                else:
                    summary_df = pd.DataFrame(
                        columns=[
                            'filename',
                            'expected_document_id',
                            'actual_document_id',
                            'field_match_failed_count',
                            'medispan_blank',
                            'medispan_mismatch',
                            'expected_no_of_medication',
                            'actual_no_of_medication',
                            'medication_different_count_total',
                            'missing_in_expected_total',
                            'missing_in_actual_total',
                            *field_mismatch_counts.keys()
                        ]
                    )
                new_summary_df = pd.DataFrame(
                    [
                        {
                            'filename': filename,
                            'expected_document_id': ex_document_id,
                            'actual_document_id': actual_doc_id,
                            'field_match_failed_count': no_match_count,
                            'medispan_blank': medispan_blank,
                            'medispan_mismatch': medispan_mismatch,
                            'expected_no_of_medication': expected_no_of_medication,
                            'actual_no_of_medication': actual_no_of_medication,
                            'medication_different_count_total': medication_different_count_total,
                            'missing_in_expected_total': missing_in_expected_total,
                            'missing_in_actual_total': missing_in_actual_total,
                            **field_mismatch_counts
                        }
                    ]
                )
                summary_df = pd.concat([summary_df, new_summary_df], ignore_index=True)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)

                # Reorder sheets to make "Summary" the first sheet
                writer.book._sheets = [writer.book['Summary']] + [
                    sheet for sheet in writer.book._sheets if sheet.title != 'Summary'
                ]
        else:
            raise ValueError("Unsupported file format. Please use .xlsx")
    else:
        combined_df = new_df

        # Save the combined DataFrame to the file
        if report_file_name.endswith('.xlsx'):
            with pd.ExcelWriter(report_file_name, engine='openpyxl') as writer:
                combined_df.to_excel(writer, sheet_name='Results', index=False)
                # Add a new worksheet for "Summary"
                summary_df = pd.DataFrame(
                    [
                        {
                            'filename': filename,
                            'expected_document_id': ex_document_id,
                            'actual_document_id': actual_doc_id,
                            'field_match_failed_count': no_match_count,
                            'medispan_blank': medispan_blank,
                            'medispan_mismatch': medispan_mismatch,
                            'expected_no_of_medication': expected_no_of_medication,
                            'actual_no_of_medication': actual_no_of_medication,
                            'medication_different_count_total': medication_different_count_total,
                            'missing_in_expected_total': missing_in_expected_total,
                            'missing_in_actual_total': missing_in_actual_total,
                            **field_mismatch_counts
                        }
                    ]
                )
                summary_df.to_excel(writer, sheet_name='Summary', index=False)

                # Reorder sheets to make "Summary" the first sheet
                writer.book._sheets = [writer.book['Summary']] + [
                    sheet for sheet in writer.book._sheets if sheet.title != 'Summary'
                ]
        else:
            raise ValueError("Unsupported file format. Please use .xlsx")
    
    test_storage = lambda _: GoogleStorageAdapter(GCP_PROJECT_ID, GCS_TEST_BUCKET, CLOUD_PROVIDER)
    adapter_test = test_storage(None)
    content = None
    with open(report_file_name, "rb") as f:
        content = f.read()
    await adapter_test.put_report(content,now_utc().strftime("%B-%d"), report_file_name)
    # os.remove(report_file_name)
    
    

async def run():
    LOGGER.info("Running test_orchestrator_flash")
    for key, value in test_data.items():
        golden_data_set_doc_id = value['golden_data_set_doc_id']
        target_data_set_doc_id = value['target_data_set_doc_id']
        (
            element_check,
            no_match_count_total,
            medispan_blank_total,
            medispan_mismatch_total,
            no_expected_medications,
            no_actual_medications,
            medication_different_count_total,
            missing_in_expected_total,
            missing_in_actual_total,
            field_mismatch_counts,
            list_of_medispan_ids,  # New field
            element_new
        ) = await get_extracted_medication_From_doc(golden_data_set_doc_id, target_data_set_doc_id)
        await save_results_to_file(
            element_check,
            element_new,
            no_match_count_total,
            golden_data_set_doc_id,
            target_data_set_doc_id,
            medispan_blank_total,
            medispan_mismatch_total,
            no_expected_medications,
            no_actual_medications,
            report_file_name,
            medication_different_count_total,
            missing_in_expected_total,
            missing_in_actual_total,
            field_mismatch_counts,
            list_of_medispan_ids  # New field
        )


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
