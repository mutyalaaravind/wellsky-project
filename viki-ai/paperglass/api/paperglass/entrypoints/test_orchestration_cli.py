import sys, os
import asyncio
import uuid
from typing import List
import jwt, json
from datetime import datetime, timedelta
import traceback
from kink import inject
from base64 import b64encode, b64decode
import pandas as pd
from openpyxl import load_workbook

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from paperglass.domain.time import now_utc
from paperglass.settings import (
    GCP_PROJECT_ID, 
    CLOUD_PROVIDER,
    E2E_TEST_SAMPLE_SIZE
)
from paperglass.infrastructure.adapters.google import GoogleStorageAdapter       
from paperglass.domain.util_json import DateTimeEncoder
from paperglass.domain.values import ( DocumentOperationStatus)
from paperglass.domain.model_testing import ( 
    TestCase, 
    TestCaseType, 
    TestResults, 
    TestResultStage, 
    TestCaseInputsOrchestration, 
    TestConditions )

from paperglass.domain.models import Document


from paperglass.usecases.documents import get_document_status
from paperglass.usecases.medications import get_resolved_reconcilled_medications_v3, get_resolved_reconcilled_medications
from paperglass.entrypoints.utils.goldendataset_compare_utils import find_common_keys

from paperglass.interface.ports import ICommandHandlingPort
from paperglass.usecases.commands import (
    Orchestrate,
    SaveTestResults,
    CreateTestDocument
)

from paperglass.infrastructure.ports import (IQueryPort, 
                                             IStoragePort)

from paperglass.tests.test_automation.testcase_repository import list_test_cases

from paperglass.domain.utils.opentelemetry_utils import bootstrap_opentelemetry

bootstrap_opentelemetry(__name__)

from paperglass.log import CustomLogger

from paperglass.usecases.configuration import get_golden_data

LOGGER = CustomLogger(__name__)

GCS_TEST_BUCKET = "viki-test"
report_file_name = f"medication_test_report_{now_utc()}.xlsx"

class TimeoutException(Exception):
    pass


# TODO:  This should be integrated with the @decode_token decorator code. Do not want to duplicate this code, but for now we are avoiding making deep changes to the app
def decode_token(token: str):
    try:
        # need to remove this once demo dashboard app is refactored to use signed tokens
        decoded_token = b64decode(token).decode('utf-8')
    except Exception as e:
        decoded_token = jwt.decode(token, key='', algorithms=['HS256'], options={"verify_signature": False})
    # # Perform any additional validation or processing here
    # decoded_token = token # ToDo: Decode the JWT token
    # app_id = decoded_token.get("app_id")
    # tenant_id = decoded_token.get("tenant_id")
    # until we implement this, we will return some dummy value
    if isinstance(decoded_token, str):
        decoded_token = json.loads(decoded_token)

    response = {
        "app_id": decoded_token.get("appId"),
        "tenant_id": decoded_token.get("tenantId"),
        "patient_id": decoded_token.get("patientId"),
        "user_id": decoded_token.get("userId") or decoded_token.get("amuserkey"),
        "decoded_token": decoded_token,
        "token": token,
    }
    return response

def mktoken(app_id, tenant_id, patient_id):
    return b64encode(json.dumps({'app_id': app_id, 'tenant_id': tenant_id, 'patient_id': patient_id}).encode()).decode()


# Level 1 test is simply checking to see if the orchestration job status has changed to "completed" within the specified timeout window
async def pass_level_1_test(test_case, start_date: datetime, user_info: dict):
    LOGGER.debug("Starting level 1 test")
    status = None

    document_id = test_case.input_data.document_id
    timeout_seconds = test_case.test_conditions.max_duration_of_test_execution

    # Wait for the orchestration to start and complete
    while True:
        await asyncio.sleep(1)

        elapsed_time = (now_utc() - start_date).total_seconds()

        if elapsed_time > timeout_seconds:
            # Failed level one test for overall completion of the orchestration
            LOGGER.error(
                "Timeout exceeded (%s) waiting for orchestration job of document %s to complete",
                timeout_seconds,
                document_id,
            )
            raise TimeoutException("Timeout exceeded waiting for orchestration job to complete")

        # Check if the orchestration is complete
        allstatus = await get_document_status(
            user_info.get("app_id"), user_info.get("tenant_id"), user_info.get("patient_id"), document_id
        )

        if allstatus:
            medication_extraction_status = next(
                (
                    status
                    for status in allstatus.get("pipelineStatuses")
                    if status.get("type") == "MEDICATION_EXTRACTION"
                ),
                None,
            )
            LOGGER.debug("Medication extraction status: %s", medication_extraction_status)

            job_start_date = datetime.fromisoformat(medication_extraction_status.get("start_date"))

            # Subtracting 5 minutes from the start date to account for clock differences in local environment with GCP.
            if job_start_date > (start_date - timedelta(minutes=5)):
                # This is (likely) the one we are waiting for.  Check if it is complete
                # Here we only care about final states
                if medication_extraction_status.get("status") == "COMPLETED":
                    LOGGER.debug("Orchestration job completed")
                    status = DocumentOperationStatus.COMPLETED
                    return status
                elif medication_extraction_status.get("status") == "FAILED":
                    LOGGER.debug("Orchestration job failed")
                    status = DocumentOperationStatus.FAILED
                    return status
                else:
                    LOGGER.debug(
                        "Orchestration job still in progress: %s  Elapsed Time: %ss",
                        medication_extraction_status.get("status"),
                        elapsed_time,
                    )
                    # Around the horn again
            else:
                LOGGER.debug(
                    "Job start time '%s' is earlier than the test start time '%s'",
                    job_start_date.isoformat(),
                    start_date.isoformat(),
                )
                # This condition, the job hasn't yet started so around the horn again

    return status


async def check_medications(medications):
    medispan_ids = []
    medispan_match_count = 0
    unlisted_count = 0
    other_count = 0
    for medication in medications:
        LOGGER.debug("Medication: %s", medication)
        if medication.medispan_id:
            medispan_match_count += 1
            medispan_ids.append(medication.medication.medispan_id)
        else:
            unlisted_count += 1

    return {
        "total_medication_count": len(medications),
        "medispan_match_count": medispan_match_count,
        "unlisted_count": unlisted_count,
        "other_count": other_count,
        "medispan_ids": medispan_ids,
    }


def validate_test_conditions(results, test_conditions):

    passed = True
    errors = []

    if results["total_medication_count"] != test_conditions.total_count:
        passed = False
        errors.append(
            "Total medication count of document (%s) does not match expected count (%s)"
            % (results["total_medication_count"], test_conditions.total_count)
        )

    if results["medispan_match_count"] != test_conditions.medispan_matched_count:
        passed = False
        errors.append(
            "Medispan matched count of document (%s) does not match expected count (%s)"
            % (results["medispan_match_count"], test_conditions.medispan_matched_count)
        )

    if results["unlisted_count"] != test_conditions.unlisted_count:
        passed = False
        errors.append(
            "Unlisted count of document (%s) does not match expected count (%s)"
            % (results["unlisted_count"], test_conditions.unlisted_count)
        )

    return {"passed": passed, "errors": errors}


def is_medication_in_document(medication, document_id):
    if medication.get("extracted_medication_reference"):
        for extracted_reference in medication.get("extracted_medication_reference"):
            if extracted_reference.get("document_id") == document_id:
                return True
    return False


def get_medispan_ids(medications: List):
    medispan_ids = []
    for medication in medications:
        if medication.medispan_id:
            medispan_ids.append(medication.medispan_id)
    return medispan_ids


@inject
async def get_medication_profile(document_id, patient_id, tenant_id, app_id, query: IQueryPort):
    medispan_ids = []
    document_ids = document_id
    ret = [
        x.dict()
        for x in await get_resolved_reconcilled_medications_v3(document_ids, patient_id, app_id, tenant_id, query)
    ]

    filtered_medications = []

    for medication in ret:
        if is_medication_in_document(medication, document_id):
            filtered_medications.append(medication)

    return json.loads(json.dumps(filtered_medications, indent=4, sort_keys=True, default=str))


@inject
async def pass_level_2_test(test_case: TestCase, user_info: dict, query: IQueryPort):
    LOGGER.debug("Starting level 2 test")
    document_id = test_case.input_data.document_id
    conditions = test_case.test_conditions

    validation_results = None

    document = await query.get_document(document_id)
    if document:
        app_id = document.get("app_id")
        tenant_id = document.get("tenant_id")
        patient_id = document.get("patient_id")
        # db_medication_profile = await get_medications_by_document(document_id, patient_id, user_info.get("app_id"), user_info.get("tenant_id"))
        db_medication_profile = await get_medication_profile(document_id, patient_id, tenant_id, app_id, query)
        LOGGER.debug("Medication profile found for patient %s: %s", patient_id, db_medication_profile)

        if db_medication_profile:
            LOGGER.debug("Medication profile found for patient %s", patient_id)
            results = await check_medications(db_medication_profile)

            validation_results = validate_test_conditions(results, conditions)

        else:
            LOGGER.error("No medication profile found for patient %s", patient_id)
            validation_results = {
                "passed": False,
                "errors": ["No medication profile found for patient %s" % patient_id],
            }

    else:
        LOGGER.error("Document %s not found", document_id)
        validation_results = {"passed": False, "errors": ["Document %s not found" % document_id]}

    return validation_results


async def pass_level_3_test(test_case: TestCase, medications: List):
    LOGGER.debug("Starting level 3 test")
    target_medispan_list = test_case.test_conditions.list_of_medispan_ids
    test_medispan_list = get_medispan_ids(medications)

    target_set = set(target_medispan_list)
    test_set = set(test_medispan_list)

    if target_set == test_set:
        return {"passed": True, "errors": []}

    else:
        errors = []
        errors.append("Medispan IDs do not match")

        missing_from_test_set = target_set - test_set
        unexpected_in_test_set = test_set - target_set

        if missing_from_test_set:
            errors.append("Missing matched medispan_ids: %s" % missing_from_test_set)

        if unexpected_in_test_set:
            errors.append("Unexpected matched medispan_ids: %s" % unexpected_in_test_set)

        return {"passed": False, "errors": errors}


@inject
async def pass_grader_test(test_case: TestCase):
    LOGGER.debug("Starting grader test")
    minimum_overall_score = test_case.test_conditions.minimum_overall_score

    document_id = test_case.input_data.document_id
    from paperglass.entrypoints.orchestrate_document_medication_grader import GraderOrchestrationAgent
    agent = GraderOrchestrationAgent()    

    results = await agent.orchestrate(document_id)

    LOGGER.debug("Grader results: %s", results)

    overall_score = 0
    if results:
        overall_score_sum = 0
        for med_score in results:
            this_score = med_score.score.overall
            overall_score_sum += this_score

        overall_score = overall_score_sum / len(results)

    LOGGER.debug("Overall score: %s", overall_score)

    # Assess if the test passed or failed
    errors = []
    passed = True
    if overall_score < minimum_overall_score:
        passed = False
        errors.append(f"Overall score of {overall_score} is below the minimum_overall_score of {minimum_overall_score}")

    metadata = {"overall_score": overall_score, "individual": results}

    ret = TestResultStage(passed=passed, errors=errors, metadata=metadata)

    return ret


@inject
async def test_orchestration(test_case: TestCase, commands: ICommandHandlingPort):
    LOGGER.debug("Running test orchestration for document %s", test_case.input_data.document_id)
    starttime = now_utc()
    input_data = test_case.input_data
    document_id = input_data.document_id

    level1_results = None
    level2_results = None
    level3_results = None
    grader_results = None

    # Call API Integration to start the orchestration pipeline
    LOGGER.debug("Starting App Integration orchestration for document %s", test_case.input_data.document_id)

    user_info = decode_token(test_case.input_data.token)
    status = None
    isTimeout = False
    try:
        status = await pass_level_1_test(test_case, starttime, user_info)
    except TimeoutException as e:
        level1_results = {
            "passed": False,
            "errors": [
                "Orchestration test failed level 1 for document due to test timeout of "
                + str(test_case.test_conditions.max_duration_of_test_execution)
                + " seconds waiting for orchestration to complete.  Error: "
                + str(e)
            ],
        }
        isTimeout = True
    except Exception as e:
        level1_results = {
            "passed": False,
            "errors": ["Orchestration test failed level 1 for document due to " + str(e)],
        }
        LOGGER.error(traceback.format_exc())

    if status and status == DocumentOperationStatus.COMPLETED:
        LOGGER.info("Orchestration test passed level 1 test for document %s", document_id)
        level1_results = {"passed": True}
    elif status:
        LOGGER.error("Orchestration test failed level 1 for document %s", document_id)
        level1_results = {
            "passed": False,
            "errors": ["Orchestration test failed level 1 for document %s with a status of %s" % (document_id, status)],
        }

    if level1_results and level1_results.get("passed"):
        level2_results = await pass_level_2_test(test_case, user_info)

        if level2_results and level2_results.get("passed"):
            LOGGER.info("Orchestration test passed level 2 test for document %s", document_id)
        else:
            LOGGER.error("Orchestration test failed level 2 for document %s", document_id)

    if level2_results and level2_results.get("passed"):
        medications = await get_medication_profile(
            document_id, user_info.get("patient_id"), user_info.get("tenant_id"), user_info.get("app_id")
        )
        level3_results = await pass_level_3_test(test_case, medications)

        if level3_results and level3_results.get("passed"):
            LOGGER.info("Orchestration test passed level 3 test for document %s", document_id)
        else:
            LOGGER.error("Orchestration test failed level 3 for document %s", document_id)

    grader_results = await pass_grader_test(test_case)
    grader_results_dict = grader_results.dict()

    overall_passed = (
        (level1_results.get("passed") if level1_results else False)
        and (level2_results.get("passed") if level2_results else False)
        and (level3_results.get("passed") if level3_results else False)
    )

    assessment = {
        "overall_passed": overall_passed,
        "level1_results": level1_results,
        "level2_results": level2_results,
        "level3_results": level3_results,
        "grader_results": grader_results_dict,
    }

    test_results = TestResults.create(app_id="", tenant_id="", patient_id="", test_case=test_case, results=assessment)

    test_results_command: SaveTestResults = SaveTestResults(
        app_id=user_info.get("app_id"),
        tenant_id=user_info.get("tenant_id"),
        patient_id=user_info.get("patient_id"),
        test_results=test_results,
    )
    await commands.handle_command(test_results_command)

    elapsed_time = (now_utc() - starttime).total_seconds()
    extra = {
        "document_id": document_id,
        "testcase_name": test_case.name,
        "elapsed_time": elapsed_time,
    }
    if overall_passed:
        LOGGER.info("E2E orchestration test passed", extra=extra)
    elif isTimeout:
        extra["error_type"] = "timeout"
        LOGGER.error("E2E orchestration test timeout", extra=extra)
    else:
        extra["error_type"] = "assertion"
        LOGGER.error("E2E orchestration test failed", extra=extra)

    LOGGER.debug("Assessment: %s", json.dumps(assessment, indent=4, cls=DateTimeEncoder))

    return assessment


# Let's kick off the reextraction for each of the test cases before the test begins
@inject
async def reextract_documents(test_cases: List[TestCase], commands: ICommandHandlingPort):
    for test_case in test_cases:
        LOGGER.info(
            "Automated test case:  Initiating a medication-extraction orchestration for document %s",
            test_case.input_data.document_id,
        )

        user_info = decode_token(test_case.input_data.token)
        LOGGER.debug("User info: %s", json.dumps(user_info))

        command = Orchestrate(
            app_id=user_info.get("app_id"),
            tenant_id=user_info.get("tenant_id"),
            patient_id=user_info.get("patient_id"),
            document_id=test_case.input_data.document_id,
            token=test_case.input_data.token,
            force_new_instance=True,
            document_operation_def_id=None
        )

        await commands.handle_command(command)


async def run():
    LOGGER.info("Running test orchestration suite")
    testcases = list_test_cases(TestCaseType.ORCHESTRATION)
    if not testcases or len(testcases) == 0:
        LOGGER.info("No test cases found for E2E test")
        return
    testcases = [TestCase(**x) for x in testcases]
    await reextract_documents(testcases)

    count_passed = 0
    count_failed = 0
    test_cases_failed = []
    test_results_failed = []

    for test_case in testcases:
        results = await test_orchestration(test_case)
        if results.get("overall_passed") == False:
            count_failed += 1
            test_cases_failed.append(test_case)
            test_results_failed.append(results)
        else:
            count_passed += 1

    extra = {"count_passed": count_passed, "count_failed": count_failed}

    LOGGER.info(
        "Test orchestration suite completed with %s passed and %s failed", count_passed, count_failed, extra=extra
    )
    if count_failed > 0:
        LOGGER.error("Test orchestration suite failed", extra=extra)

        idx = 0
        for test_case in test_cases_failed:
            LOGGER.error("Test case failed: %s", test_case.name)
            LOGGER.info("Failed test case details: %s", json.dumps(test_case.dict(), indent=4, cls=DateTimeEncoder))
            LOGGER.info(
                "Failed test case results: %s", json.dumps(test_results_failed[idx], indent=4, cls=DateTimeEncoder)
            )
            idx += 1
    else:
        LOGGER.info("Test orchestration suite passed all tests", extra=extra)


@inject
async def run_orchestration_test(
    commands: ICommandHandlingPort, query: IQueryPort, storage: IStoragePort,
    filename:str=None,
):
    LOGGER.info("Running Medication orchestration suite")
    config_tests = None
    # If filename was provided, filter the test cases to only run the test for the specified filename
    if filename:
        LOGGER.info("Running test for specified filename: %s", filename)
        config_tests = await get_golden_data(2000)  # FIXME  Need a way to just retrieve the test case for the specified filename
        config_tests = [item for item in config_tests if item["test_document"] == filename]
    else:
        LOGGER.info("Running test for test case sample size of: %s", E2E_TEST_SAMPLE_SIZE)
        config_tests = await get_golden_data(E2E_TEST_SAMPLE_SIZE)

    aggregated_results = []
    count_passed = 0
    count_failed = 0
    aggregated_medication_results = []

    if not config_tests or len(config_tests) == 0:
        LOGGER.info("No test cases found for E2E test")
        return


    testrun_id = str(uuid.uuid4())

    superextra = {
        "testrun_id": testrun_id,
        "test_case_infos": [],
    }
    

    for data in config_tests:
        document_id = data['document_id']
        doc = await query.get_document(document_id)        

        storage_uri = doc['storage_uri']
        app_id = data['app_id']
        tenant_id = data['tenant_id']
        patient_id = data['patient_id']

        expected_condition= data['test_expected']
        expected_medispan_ids = expected_condition['list_of_medispan_ids']
        medispan_matched_count = expected_condition['medispan_matched_count']
        expected_medications = expected_condition['medication']
        filename = data['test_document']
        unlisted_count = expected_condition['unlisted_count']
        total_count = expected_condition['total_count']
        
        token = mktoken(app_id, tenant_id, patient_id)

        test_startdate = now_utc()

        metadata = {
            "e2e_test": {
                "source": {
                    "document_id": document_id,
                    "storage_uri": storage_uri,
                    "filename": filename,
                },
                "testrun_id": testrun_id,
                "test_startdate": test_startdate.isoformat(),
            }
        }

        extra = {}
        extra.update(metadata)
        superextra["test_case_infos"].append(extra)

        LOGGER.debug("Creating test document for orchestration test: %s", filename, extra=extra)

        create_doc = CreateTestDocument(
            app_id=app_id, tenant_id=tenant_id, patient_id=patient_id, storage_uri=storage_uri, token=token, metadata=metadata
        )
        document = await commands.handle_command(create_doc)
        extra.update({
            "test_document_id": document.id,
            "test_document": document.dict()
        })

        await asyncio.sleep(2) #wait for eventarc to complete medication profile creation.  TODO:  Red flag.  Why are we waiting for 2 seconds?  Are we assured that 2s will always suffice?

        new_document_id = document.id        
        
        LOGGER.debug("Run E2E orchestration suite for test case: %s", filename, extra=extra)
        inputDoc: TestCaseInputsOrchestration = TestCaseInputsOrchestration(document_id=new_document_id, token=token)
        extracted_test_conditions: TestConditions = TestConditions(list_of_medispan_ids=expected_medispan_ids, max_duration_of_test_execution=360, medispan_matched_count=medispan_matched_count, unlisted_count=unlisted_count,
                                                                   total_count=total_count, minimum_overall_score=0.9)  #TODO:  No magic numbers.  These values should be constants

        test_case: TestCase = TestCase(
            name=filename,
            id=str(uuid.uuid4()),
            test_type="orchestration",
            input_data=inputDoc,
            test_conditions=extracted_test_conditions,
        )
    
        results, assessment, compare_results_medication = await test_orchestration_new(test_case, document, expected_medications)
        extra["e2e_test"].update({
            "results": results,
            "assessment": assessment
        })

        if assessment.get("overall_passed") == False:
            count_failed += 1
        else:
            count_passed += 1
        aggregated_results.append(results)
        aggregated_medication_results.append(compare_results_medication)
    aggregated_summary = {"total_tests": len(aggregated_results), "details": aggregated_results}    
    
    LOGGER.debug("Creating report for orchestration test", extra=superextra)
    await create_report(aggregated_summary, aggregated_medication_results)    
    extra = {
        "count_passed": count_passed,
        "count_failed": count_failed
        }
    LOGGER.info("Test orchestration suite completed with %s passed and %s failed", count_passed, count_failed, extra=extra)
    idx = 0
    if count_failed > 0:
        LOGGER.error("Test orchestration suite failed", extra=extra)
        LOGGER.error("Test case failed: %s", test_case.name)
        LOGGER.info("Failed test case details: %s", json.dumps(test_case.dict(), indent=4, cls=DateTimeEncoder))        
        idx += 1
    else:
        LOGGER.info("Test orchestration suite passed all tests", extra=extra)    

"""
This function is used for testing the test criteria part of the e2e test withouth requiring a new orchestration.  Simply pass in the test document_id and 
the function will find the associated test case and run the test criteria against the medications extracted from the document.
"""
@inject
async def confirm_test_results(document_id, query: IQueryPort):    
    doc = await query.get_document(document_id)
    document = Document(**doc)

    token = mktoken(document.app_id, document.tenant_id, document.patient_id)

    # Now pull all of the test cases
    config_tests = await get_golden_data(2000)     

    # Filter the test cases for only those for the test_document is the same as the document_id
    filtered_test_cases = [item for item in config_tests if item["test_document"] == document.metadata["e2e_test"]["source"]["filename"] ]
    
    LOGGER.debug("Filtered test cases: %s", len(filtered_test_cases))

    test_case = None
    if len(filtered_test_cases) > 0:
        test_case = filtered_test_cases[0]
    else:
        raise Exception("No test case found for document %s" % document_id)
    
    expected_condition= test_case['test_expected']
    expected_medications = expected_condition['medication']
    expected_medispan_ids = expected_condition['list_of_medispan_ids']
    medispan_matched_count = expected_condition['medispan_matched_count']
    unlisted_count = expected_condition['unlisted_count']
    total_count = expected_condition['total_count']
    
    inputDoc: TestCaseInputsOrchestration = TestCaseInputsOrchestration(document_id=document.id, token=token)
    extracted_test_conditions: TestConditions = TestConditions(list_of_medispan_ids=expected_medispan_ids,max_duration_of_test_execution = 360,medispan_matched_count=medispan_matched_count, unlisted_count=unlisted_count,
                                                                total_count=total_count, minimum_overall_score=0.9)

    test_case: TestCase = TestCase(
        name=test_case['test_document'],
        id=str(uuid.uuid4()),
        test_type="orchestration",
        input_data=inputDoc,
        test_conditions=extracted_test_conditions,
    )

    # Call the method to run the test criteria against the medications extracted from the document    
    results, assessment, compare_results_medication = await test_orchestration_new(test_case, document, expected_medications)

    output = {
        "results": results,
        "assessment": assessment,
        "compare_results_medication": compare_results_medication
    }        

    # Return the results
    return output


def convert_to_serializable(obj):
    """Helper function to convert non-serializable objects to serializable ones."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, set):
        return list(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


@inject
async def create_report(aggregated_results: dict, compare_results_medication: list, storage: IStoragePort):
    total_tests = aggregated_results.get("total_tests")
    details = aggregated_results.get("details", [])

    total_tests_df = pd.DataFrame([{"Total Tests": total_tests}])
    
    extracted_results = []
    for idx, detail in enumerate(details):
        input_json = detail.get('input')
        expected = detail.get('expected')
        actual = detail.get('actual')
        metadata = detail.get('metadata')
        error = detail.get('errors')
        test_status = detail.get('status')
        grader_results = detail.get('grader_results')
        grader = {'passed': grader_results.get('passed'), 'error': grader_results.get('errors')}

        extracted_results.append(
            {
                'Test ID': f'Test_{idx + 1}',
                'Input Document ID': input_json.get('document_id'),
                'Original Doc Path': input_json.get('original_doc_path'),
                'Test Doc Path': input_json.get('test_doc_path'),
                'Test Doc File Name': input_json.get('test_doc_file_name'),
                'Expected Max Duration': expected.get('max_duration_of_test_execution'),
                'Expected Medispan Matched Count': expected.get('medispan_matched_count'),
                'Expected Unlisted Count': expected.get('unlisted_count'),
                'Expected Total Count': expected.get('total_count'),
                'Expected Medispan IDs': ', '.join(expected.get('list_of_medispan_ids', [])),
                'Expected Minimum Overall Score': expected.get('minimum_overall_score'),
                'Actual Documentation Operation Status': actual.get('Documentation Operation Status'),
                'Actual Elapsed Time': actual.get('Elapsed Time'),
                'Actual Total Medication Count': actual.get('Medication Profile', {}).get('total_medication_count'),
                'Actual Medispan Match Count': actual.get('Medication Profile', {}).get('medispan_match_count'),
                'Actual Unlisted Count': actual.get('Medication Profile', {}).get('unlisted_count'),
                'Actual Other Count': actual.get('Medication Profile', {}).get('other_count'),
                'Actual Medispan IDs': ', '.join(actual.get('Medication Profile', {}).get('medispan_ids', [])),
                'Metadata Document ID': metadata.get('document_id'),
                'Metadata Testcase Name': metadata.get('testcase_name'),
                'Metadata Elapsed Time': metadata.get('elapsed_time'),
                'Errors': error,
                'Test Status': test_status,
                'Grader Passed': grader.get('passed'),
                'Grader Errors': ', '.join(grader.get('error', [])),
            }
        )

    details_df = pd.DataFrame(extracted_results)    
    report_df = pd.concat([total_tests_df, details_df], ignore_index=True)
    compare_results_list = []
    for med_comparison in compare_results_medication:
        for med in med_comparison:
            for result in med:
                compare_results_list.append({
                    'Key': result.get('Key'),
                    'Expected Value': result.get('expected'),
                    'Actual Value': result.get('actual'),
                    'Match Status': result.get('match')
                })
    compare_med_df = pd.DataFrame(compare_results_list, columns=['Key', 'Expected Value', 'Actual Value', 'Match Status'])
    
    with pd.ExcelWriter(report_file_name, engine='openpyxl') as writer:
        report_df.to_excel(writer, sheet_name='Details', index=False)
        compare_med_df.to_excel(writer, sheet_name='Compare Results Medication', index=False)
        
    test_storage = lambda _: GoogleStorageAdapter(GCP_PROJECT_ID, GCS_TEST_BUCKET, CLOUD_PROVIDER)
    adapter_test = test_storage(None)
    content = None
    with open(report_file_name, "rb") as f:
        content = f.read()
    await adapter_test.put_report(content, f"e2e/{now_utc().strftime('%B-%d')}", report_file_name)


@inject
async def test_orchestration_new(test_case: TestCase, document: Document, expected_medications: List, commands: ICommandHandlingPort):
    starttime = now_utc()
    input_data = test_case.input_data
    document_id = input_data.document_id
    original_doc_path = document.source_storage_uri
    test_doc_path = document.storage_uri
    test_doc_file_name = document.file_name

    result = {'input': {}, 'expected': {}, 'actual': {}, 'result': {}, 'errors': {}}

    result["input"]["document_id"] = document_id
    result["input"]["original_doc_path"] = original_doc_path
    result["input"]["test_doc_path"] = test_doc_path
    result["input"]["test_doc_file_name"] = test_doc_file_name
    result["expected"] = test_case.test_conditions.dict()
    isTimeout = False
    level1_results = None
    grader_results = None
    level2_results = None
    level3_results = None
    compare_results_medication = []
    
    user_info = decode_token(test_case.input_data.token)
    status = None
    try:
        result = await test_suite_1(test_case, starttime, user_info, result)
        status = result.get("actual").get("Documentation Operation Status")
    except TimeoutException as e:
        level1_results = {
            "passed": False,
            "errors": [
                "Orchestration test failed level 1 for document due to test timeout of "
                + str(test_case.test_conditions.max_duration_of_test_execution)
                + " seconds waiting for orchestration to complete.  Error: "
                + str(e)
            ],
        }
        isTimeout = True
        result["reason"] = level1_results["errors"]
        result["status"] = "Failed"
    except Exception as e:
        level1_results = {
            "passed": False,
            "errors": ["Orchestration test failed level 1 for document due to " + str(e)],
        }
        LOGGER.error(traceback.format_exc())
        result["reason"] = level1_results["errors"]
        result["status"] = "Failed"
    if status and status == DocumentOperationStatus.COMPLETED:
        LOGGER.info("Orchestration test passed level 1 test for document %s", document_id)
        level1_results = {"passed": True}
    elif status:
        LOGGER.error("Orchestration test failed level 1 for document %s", document_id)
        level1_results = {"passed": False,
                          "errors": ["Orchestration test failed level 1 for document %s with a status of %s" % (document_id, status)]}
    
    if level1_results and level1_results.get("passed"):
        result, level2_results, level3_results, compare_results_medication = await test_suite_2(result, test_case, expected_medications)


    if level3_results and level3_results.get("passed"):
            LOGGER.info("Orchestration test passed level 3 test for document %s", document_id)
    else:
            LOGGER.error("Orchestration test failed level 3 for document %s", document_id)    
        
    grader_results = await pass_grader_test(test_case)
    grader_results_dict = grader_results.dict()
    overall_passed = (level1_results.get("passed") if level1_results else False) and (level2_results.get("passed") if level2_results else False) and (level3_results.get("passed") if level3_results else False)
    assessment = {
        "overall_passed": overall_passed,
        "level1_results": level1_results,
        "level2_results": level2_results,
        "level3_results": level3_results,
        "grader_results": grader_results_dict
    }

    result["grader_results"] = grader_results_dict
    test_results = TestResults.create(app_id="", tenant_id="", patient_id="", test_case=test_case, results=assessment)

    test_results_command: SaveTestResults = SaveTestResults(
        app_id="007",
        tenant_id="54321",
        patient_id="",
        test_results=test_results,
    )
    await commands.handle_command(test_results_command)
    extra = {        
        "document_id": document_id,
        "testcase_name": test_case.name,        
    }
    if overall_passed:        
        LOGGER.info("E2E orchestration test passed", extra=extra)
    elif isTimeout:
        extra["error_type"] = "timeout"
        LOGGER.error("E2E orchestration test timeout", extra=extra)    
    else:        
        LOGGER.error("E2E orchestration test failed", extra=extra)

    LOGGER.debug("Assessment: %s", json.dumps(assessment, indent=4, cls=DateTimeEncoder))

    elapsed_time = (now_utc() - starttime).total_seconds()
    metadata = {
        "document_id": document_id,
        "testcase_name": test_case.name,
        "elapsed_time": elapsed_time,
    }
    result["metadata"] = metadata

    return result, assessment, compare_results_medication


@inject
async def test_suite_1(test_case, start_date: datetime, user_info: dict, result: dict):
    LOGGER.debug("Starting test Suite")
    status = None
    document_id = test_case.input_data.document_id
    timeout_seconds = test_case.test_conditions.max_duration_of_test_execution

    while True:
        await asyncio.sleep(1)
        elapsed_time = (now_utc() - start_date).total_seconds()

        if elapsed_time > timeout_seconds:
            # Failed level one test for overall completion of the orchestration
            LOGGER.error(
                "Timeout exceeded (%s) waiting for orchestration job of document %s to complete",
                timeout_seconds,
                document_id,
            )
            raise TimeoutException("Timeout exceeded waiting for orchestration job to complete")
        allstatus = await get_document_status(
            user_info.get("app_id"), user_info.get("tenant_id"), user_info.get("patient_id"), document_id
        )

        LOGGER.debug("All status: %s", allstatus)

        if allstatus:
            if isinstance(allstatus.get("pipelineStatuses"), list):
                medication_extraction_status = next(
                    (
                        status
                        for status in allstatus.get("pipelineStatuses")
                        if status.get("type") == "MEDICATION_EXTRACTION"
                    ),
                    None,
                )
            else:
                medication_extraction_status = allstatus.get("pipelineStatuses")

            LOGGER.debug("Medication extraction status: %s", medication_extraction_status)
            job_start_date = datetime.fromisoformat(medication_extraction_status.get("start_date"))
            if True or job_start_date > (start_date - timedelta(minutes=5)):  #TODO:  Don't assess by job_start_date as the new job status is tied directly to the documment.  Clean this up.
                # This is (likely) the one we are waiting for.  Check if it is complete
                # Here we only care about final states
                if medication_extraction_status.get("status") == "COMPLETED":
                    LOGGER.debug("Orchestration job completed")
                    status = DocumentOperationStatus.COMPLETED
                    result["actual"]["Documentation Operation Status"] = status
                    result["actual"]["Elapsed Time"] = elapsed_time
                    return result
                elif medication_extraction_status.get("status") == "FAILED":
                    LOGGER.debug("Orchestration job failed")
                    status = DocumentOperationStatus.FAILED
                    result["actual"]["Documentation Operation Status"] = status
                    result["actual"]["Elapsed Time"] = elapsed_time
                    return result
                else:
                    LOGGER.debug(
                        "Orchestration job still in progress: %s  Elapsed Time: %ss",
                        medication_extraction_status.get("status"),
                        elapsed_time,
                    )
                    # Around the horn again
            else:
                LOGGER.debug(
                    "Job start time '%s' is earlier than the test start time '%s'",
                    job_start_date.isoformat(),
                    start_date.isoformat(),
                )
                # This condition, the job hasn't yet started so around the horn again
    return result


@inject
async def test_suite_2(result: dict, test_case: TestCase, expected_medications: List, query: IQueryPort):
    document_id = test_case.input_data.document_id
    conditions = test_case.test_conditions
    target_medispan_list = conditions.list_of_medispan_ids
    validation_results = None
    document = await query.get_document(document_id)
    comparision_result = []

    if document:
        app_id = document.get("app_id")
        tenant_id = document.get("tenant_id")
        patient_id = document.get("patient_id")

        from paperglass.usecases.v4.medications import get_resolved_reconcilled_medications as get_resolved_reconcilled_medications_v4
        from paperglass.domain.values import Configuration
        from paperglass.usecases.configuration import get_config

        config:Configuration = Configuration()            
        config = await get_config(app_id, tenant_id, query)

        doc = Document(**document)
        document_id_with_orchestration_engine_version = {document_id: doc.operation_status["medication_extraction"].orchestration_engine_version}

        db_medication_profile = await get_resolved_reconcilled_medications_v4(document_id_with_orchestration_engine_version, patient_id, app_id, tenant_id, config, query)
        #db_medication_profile = await get_medication_profile(document_id, patient_id, tenant_id, app_id, query)
        
        LOGGER.debug("Medication profile found for patient %s: %s", patient_id, db_medication_profile)

        if db_medication_profile:
            LOGGER.debug("Medication profile found for patient %s", patient_id)
            results = await check_medications(db_medication_profile)
            result["actual"]["Medication Profile"] = results
            validation_results = validate_test_conditions(results, conditions)
        else:
            LOGGER.error("No medication profile found for patient %s", patient_id)
            validation_results = {
                "passed": False,
                "errors": ["No medication profile found for patient %s" % patient_id],
            }

    else:
        LOGGER.error("Document %s not found", document_id)
        validation_results = {"passed": False, "errors": ["Document %s not found" % document_id]}
  
    level2_results =  validation_results
    
    if level2_results and level2_results.get("passed"):
            LOGGER.info("Orchestration test passed level 2 test for document %s", document_id)
    else:
            LOGGER.error("Orchestration test failed level 2 for document %s", document_id)
    errors = []
    comparision_result = await compare_results_medication(db_medication_profile, expected_medications)
    if validation_results:
        if comparision_result:
            test_medispan_list = get_medispan_ids(db_medication_profile)
            target_set = set(target_medispan_list)
            test_set = set(test_medispan_list)
            if target_set == test_set:
                level3_results={"passed": True, "errors": []}
                return result , level2_results, level3_results, comparision_result
            else:
                errors.append("Medispan IDs do not match")
                result["status"] = "Failed Test Suite 2"
                missing_from_test_set = target_set - test_set
                unexpected_in_test_set = test_set - target_set

                if missing_from_test_set:
                    errors.append("Missing matched medispan_ids: %s" % missing_from_test_set)
                    result["actual"]["Missing Medispan ID"] = missing_from_test_set
                    result["errors"] = errors

                if unexpected_in_test_set:
                    errors.append("Unexpected matched medispan_ids: %s" % unexpected_in_test_set)
                    result["actual"]["Unexpected Medispan ID"] = unexpected_in_test_set

    else:
        result["status"] = "Failed Test Suite 2"
    return result , level2_results, {"passed": False, "errors": errors}, comparision_result


async def compare_results_medication(db_medication_profile, expected_medications):
    keys_to_compare = ["dosage", "form", "frequency", "instructions", "name", "start_date", "route", "strength"]
    comparison_results = []
    # Removed breakpoint()
    for expected_med in expected_medications:
        expected_med_info = {key: expected_med.get(key) for key in keys_to_compare}
        medispan_id = expected_med.get("medispan_id")
        # Find the actual medication in db_medication_profile
        actual_med = next((med for med in db_medication_profile if med.medispan_id == medispan_id), None)
        
        if actual_med:
            actual_med_dict = actual_med.dict()
            actual_med_info = {key: actual_med_dict.get("medication", {}).get(key) for key in keys_to_compare}
            comparison = find_common_keys(expected_med_info, actual_med_info)
            comparison_results.append(comparison["common_list"])
        else:
            # Removed medispan_id comparison
            pass

    return comparison_results


def medication_db_profile(db_medication_profile):
    result = {"actual": {"Medications": []}}

    # Assuming db_medication_profile is a list of dictionaries
    if db_medication_profile and isinstance(db_medication_profile, list):
        for profile in db_medication_profile:
            # Ensure each element is a dictionary
            if isinstance(profile, dict):
                medication = profile.get("medication")
                if medication:
                    result["actual"]["Medications"].append(medication)
            else:
                raise TypeError("Expected a dictionary in the list")
    else:
        raise TypeError("Expected a list of dictionaries")

    return result


def main():
    asyncio.run(run_orchestration_test())


if __name__ == "__main__":
    main()
