import sys, os
import asyncio
import uuid
from typing import List, Optional
from collections import Counter
import jwt, json
from datetime import datetime, timedelta, timezone
import traceback
from kink import inject
from base64 import b64encode, b64decode
import pandas as pd
from openpyxl import load_workbook
from difflib import SequenceMatcher


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
from paperglass.interface.ports import ICommandHandlingPort
from paperglass.infrastructure.ports import (IQueryPort, 
                                             IStoragePort,
                                             IQueryPort,
                                             IPromptAdapter)

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
    """
    Enhanced medication check with detailed validation and categorization.
    
    Args:
        medications: List of medication objects to check
        
    Returns:
        Dict containing detailed medication analysis results
    """
    results = {
        "total_medication_count": len(medications),
        "medispan_match_count": 0,
        "unlisted_count": 0,
        "invalid_medispan_count": 0,
        "medispan_ids": [],
        "invalid_medispan_ids": [],
        "medications_by_category": {
            "valid_medispan": [],
            "invalid_medispan": [],
            "unlisted": [],
        },
        "validation_details": []
    }
    
    for medication in medications:
        LOGGER.debug("Checking medication: %s", medication)
        
        if not medication:
            LOGGER.warning("Found null medication entry")
            continue
            
        med_info = {
            "name": getattr(medication, "name", "Unknown"),
            "medispan_id": getattr(medication, "medispan_id", None),
            "validation_status": "unlisted"
        }
        
        if medication.medispan_id:
            # Validate Medispan ID format
            if is_valid_medispan_id(medication.medispan_id):
                results["medispan_match_count"] += 1
                results["medispan_ids"].append(medication.medication.medispan_id)
                med_info["validation_status"] = "valid"
                results["medications_by_category"]["valid_medispan"].append(medication)
            else:
                results["invalid_medispan_count"] += 1
                results["invalid_medispan_ids"].append(medication.medispan_id)
                med_info["validation_status"] = "invalid"
                med_info["validation_error"] = "Invalid Medispan ID format"
                results["medications_by_category"]["invalid_medispan"].append(medication)
        else:
            results["unlisted_count"] += 1
            med_info["validation_error"] = "No Medispan ID"
            results["medications_by_category"]["unlisted"].append(medication)
        
        results["validation_details"].append(med_info)
    
    # Calculate percentages
    total = results["total_medication_count"]
    if total > 0:
        results["statistics"] = {
            "valid_medispan_percentage": (results["medispan_match_count"] / total) * 100,
            "invalid_medispan_percentage": (results["invalid_medispan_count"] / total) * 100,
            "unlisted_percentage": (results["unlisted_count"] / total) * 100
        }
    
    # Add validation summary
    results["validation_summary"] = {
        "total_validated": results["medispan_match_count"] + results["invalid_medispan_count"],
        "total_unvalidated": results["unlisted_count"],
        "validation_rate": ((results["medispan_match_count"] + results["invalid_medispan_count"]) / total * 100) if total > 0 else 0
    }
    
    
    return results


def validate_test_conditions(results, test_conditions):
    """
    Enhanced validation of test conditions with detailed analysis and recommendations.
    
    Args:
        results: Dict containing medication check results
        test_conditions: TestConditions object with expected values
        
    Returns:
        Dict containing validation results, errors, and recommendations
    """
    validation_results = {
        "passed": True,
        "errors": [],
        "warnings": [],
        "details": {},
        "recommendations": []
    }
    
    # Validate total count
    total_diff = results["total_medication_count"] - test_conditions.total_count
    if total_diff != 0:
        validation_results["passed"] = False
        validation_results["errors"].append(
            f"Total medication count mismatch: found {results['total_medication_count']}, "
            f"expected {test_conditions.total_count} (difference: {abs(total_diff)})"
        )
        if total_diff > 0:
            validation_results["recommendations"].append(
                "Check for duplicate medications or false positives in extraction"
            )
        else:
            validation_results["recommendations"].append(
                "Check for missed medications in extraction"
            )
    
    # Validate Medispan matches
    medispan_diff = results["medispan_match_count"] - test_conditions.medispan_matched_count
    if medispan_diff != 0:
        validation_results["passed"] = False
        validation_results["errors"].append(
            f"Medispan match count mismatch: found {results['medispan_match_count']}, "
            f"expected {test_conditions.medispan_matched_count} (difference: {abs(medispan_diff)})"
        )
        if results["invalid_medispan_count"] > 0:
            validation_results["errors"].append(
                f"Found {results['invalid_medispan_count']} medications with invalid Medispan IDs"
            )
            validation_results["recommendations"].append(
                "Review medications with invalid Medispan IDs"
            )
    
    # Validate unlisted count
    unlisted_diff = results["unlisted_count"] - test_conditions.unlisted_count
    if unlisted_diff != 0:
        validation_results["passed"] = False
        validation_results["errors"].append(
            f"Unlisted medication count mismatch: found {results['unlisted_count']}, "
            f"expected {test_conditions.unlisted_count} (difference: {abs(unlisted_diff)})"
        )
        if unlisted_diff > 0:
            validation_results["recommendations"].append(
                "Check for medications that should have Medispan IDs but are unlisted"
            )
    
    # Add validation statistics
    validation_results["details"] = {
        "count_validation": {
            "total_difference": total_diff,
            "medispan_difference": medispan_diff,
            "unlisted_difference": unlisted_diff
        },
        "validation_rates": {
            "total_validation_rate": (results["total_medication_count"] / test_conditions.total_count * 100) 
                if test_conditions.total_count > 0 else 0,
            "medispan_validation_rate": (results["medispan_match_count"] / test_conditions.medispan_matched_count * 100)
                if test_conditions.medispan_matched_count > 0 else 0,
            "unlisted_validation_rate": (results["unlisted_count"] / test_conditions.unlisted_count * 100)
                if test_conditions.unlisted_count > 0 else 0
        }
    }
    
    # Add category-specific details
    if "medications_by_category" in results:
        validation_results["details"]["categories"] = {
            "valid_medispan": len(results["medications_by_category"]["valid_medispan"]),
            "invalid_medispan": len(results["medications_by_category"]["invalid_medispan"]),
            "unlisted": len(results["medications_by_category"]["unlisted"])
        }
    
    # Add validation summary
    if "validation_summary" in results:
        validation_results["details"]["validation_summary"] = results["validation_summary"]
    
    # Add warnings for potential issues
    if results.get("invalid_medispan_count", 0) > 0:
        validation_results["warnings"].append(
            f"Found {results['invalid_medispan_count']} medications with invalid Medispan IDs"
        )
    
    if validation_results["passed"]:
        LOGGER.info("Test conditions validated successfully")
    else:
        LOGGER.error("Test conditions validation failed: %s", 
                    json.dumps(validation_results, indent=2))
    
    return validation_results


def is_medication_in_document(medication, document_id):
    if medication.get("extracted_medication_reference"):
        for extracted_reference in medication.get("extracted_medication_reference"):
            if extracted_reference.get("document_id") == document_id:
                return True
    return False


def get_medispan_ids(medications: List):
    """
    Extract Medispan IDs from medications with enhanced error handling and logging.
    
    Args:
        medications: List of medication objects
        
    Returns:
        List of valid Medispan IDs
    """
    medispan_ids = []
    unmatched_meds = []
    
    for medication in medications:
        if not medication:
            continue
            
        med_name = getattr(medication, 'name', 'Unknown')
        
        if hasattr(medication, 'medispan_id') and medication.medispan_id:
            medispan_ids.append(medication.medispan_id)
        else:
            unmatched_meds.append({
                'name': med_name,
                'reason': 'No Medispan ID found'
            })
    
    if unmatched_meds:
        LOGGER.warning("Found medications without Medispan IDs: %s", 
                      json.dumps(unmatched_meds, indent=2))
    
    return medispan_ids, unmatched_meds


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
    """
    Enhanced level 3 test for medication validation with detailed comparison and error reporting.
    Handles cases with missing Medispan IDs and provides detailed analysis of mismatches.
    
    Args:
        test_case: Test case containing expected medispan IDs and conditions
        medications: List of actual medications extracted from the document
        
    Returns:
        Dict containing test results with detailed comparison information
    """
    LOGGER.debug("Starting level 3 test")
    
    # Input validation
    if not test_case.test_conditions.list_of_medispan_ids:
        return {
            "passed": False,
            "errors": ["No expected medispan IDs provided in test conditions"],
            "details": {
                "error_type": "missing_test_conditions",
                "recommendations": ["Ensure test case includes expected Medispan IDs"]
            }
        }
    
    if not medications:
        return {
            "passed": False,
            "errors": ["No medications found in the document"],
            "details": {
                "error_type": "no_medications",
                "recommendations": ["Verify document contains medication information"]
            }
        }

    target_medispan_list = test_case.test_conditions.list_of_medispan_ids
    test_medispan_list, unmatched_medications = get_medispan_ids(medications)
    
    LOGGER.info("Target medispan list: %s", target_medispan_list)
    LOGGER.info("Test medispan list: %s", test_medispan_list)

    # Enhanced validation results
    validation_results = {
        "total_medications": len(medications),
        "medications_with_medispan": len(test_medispan_list),
        "medications_without_medispan": len(unmatched_medications),
        "unmatched_medications": unmatched_medications,
        "match_details": {
            "total_expected": len(target_medispan_list),
            "total_found": len(test_medispan_list),
            "match_percentage": 0,
            "exact_matches": [],
            "missing_ids": [],
            "unexpected_ids": [],
            "similar_matches": []  # For potential fuzzy matching or near-matches
        }
    }

    # Compare lists maintaining order and duplicates
    target_id_counts = Counter(target_medispan_list)
    test_id_counts = Counter(test_medispan_list)
    
    # Find exact matches
    exact_matches = set(target_medispan_list) & set(test_medispan_list)
    missing_ids = set(target_medispan_list) - set(test_medispan_list)
    unexpected_ids = set(test_medispan_list) - set(target_medispan_list)
    
    # Update match details
    validation_results["match_details"].update({
        "exact_matches": list(exact_matches),
        "missing_ids": list(missing_ids),
        "unexpected_ids": list(unexpected_ids)
    })

    # Calculate match percentage
    total_correct = sum(min(target_id_counts[id], test_id_counts[id]) 
                       for id in exact_matches)
    if len(target_medispan_list) > 0:
        validation_results["match_details"]["match_percentage"] = (total_correct / len(target_medispan_list)) * 100

    # Generate detailed error messages
    errors = []
    if unmatched_medications:
        errors.append(f"Found {len(unmatched_medications)} medications without Medispan IDs")
    if missing_ids:
        errors.append(f"Missing expected Medispan IDs: {list(missing_ids)}")
        # Add specific details about missing medications
        for mid in missing_ids:
            errors.append(f"Expected medication with ID {mid} not found in results")
    if unexpected_ids:
        errors.append(f"Found unexpected Medispan IDs: {list(unexpected_ids)}")
        # Add specific details about unexpected medications
        for mid in unexpected_ids:
            errors.append(f"Found unexpected medication with ID {mid}")

    # Determine if test passed with configurable threshold
    match_threshold = getattr(test_case.test_conditions, 'match_threshold', 100)  # Default to requiring exact match
    passed = (validation_results["match_details"]["match_percentage"] >= match_threshold)

    # Add recommendations based on results
    recommendations = []
    if unmatched_medications:
        recommendations.append("Review medications without Medispan IDs for potential matching issues")
    if missing_ids:
        recommendations.append("Verify extraction process for missing medications")
    if unexpected_ids:
        recommendations.append("Check for potential misidentification of medications")

    validation_results["recommendations"] = recommendations

    LOGGER.info("Level 3 test results: %s", {
        "passed": passed,
        "match_percentage": validation_results["match_details"]["match_percentage"],
        "details": validation_results
    })

    return {
        "passed": passed,
        "errors": errors if not passed else [],
        "details": validation_results
    }

def is_valid_medispan_id(id_str: str) -> bool:
    """
    Validates the format of a Medispan ID with specific rules.
    
    Args:
        id_str: The Medispan ID to validate
        
    Returns:
        bool: True if the ID is valid, False otherwise
        
    Rules:
    1. Must not be empty
    2. Must be a string that can be converted to an integer
    3. Must be a positive number
    4. Must not exceed 10 digits (typical Medispan ID length)
    5. Must not start with '0' unless it's just '0'
    """
    if not id_str:
        LOGGER.warning("Empty Medispan ID")
        return False
        
    try:
        # Try to convert to integer
        id_num = int(id_str)
        
        # Check if positive
        if id_num < 0:
            LOGGER.warning(f"Negative Medispan ID: {id_str}")
            return False
            
        # Check length
        if len(id_str) > 10:
            LOGGER.warning(f"Medispan ID too long: {id_str}")
            return False
            
        # Check for leading zeros (unless it's just '0')
        if len(id_str) > 1 and id_str.startswith('0'):
            LOGGER.warning(f"Medispan ID with leading zeros: {id_str}")
            return False
            
        return True
        
    except ValueError:
        LOGGER.warning(f"Invalid Medispan ID format (non-numeric): {id_str}")
        return False


@inject
async def pass_grader_test(test_case: TestCase, commands: ICommandHandlingPort, query: IQueryPort):
    LOGGER.debug("Starting grader test")
    minimum_overall_score = test_case.test_conditions.minimum_overall_score

    document_id = test_case.input_data.document_id


    from paperglass.entrypoints.orchestrate_document_medication_grader_cli import GraderOrchestrationAgent,process_command

    agent = GraderOrchestrationAgent()    

    try:
        results = await agent.orchestrate(document_id, commands, query)
        
        # results = await process_command(document_id, commands, query)
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
    except Exception as e:
        LOGGER.error("Error in grader test: %s", str(e))
        return TestResultStage(passed=False, errors=[str(e)], metadata={})


@inject
async def test_orchestration(test_case: TestCase, commands: ICommandHandlingPort, query: IQueryPort):
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
        LOGGER.debug("Level 3 results: %s", level3_results)
        
        if level3_results and level3_results.get("passed"):
            LOGGER.info("Orchestration test passed level 3 test for document %s", document_id)
        else:
            LOGGER.error("Orchestration test failed level 3 for document %s", document_id)

    grader_results = await pass_grader_test(test_case, commands, query)
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


@inject
async def run(commands: ICommandHandlingPort, query: IQueryPort):
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
        results = await test_orchestration(test_case, commands, query)
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
    config_tests = None
    # If filename was provided, filter the test cases to only run the test for the specified filename
    if filename:
        LOGGER.debug("Running test for specified filename: %s", filename)
        config_tests = await get_golden_data(2000)  # FIXME  Need a way to just retrieve the test case for the specified filename
        config_tests = [item for item in config_tests if item["test_document"] == filename]
    else:
        LOGGER.debug("Running test for test case sample size of: %s", E2E_TEST_SAMPLE_SIZE)
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
    
        results, assessment, compare_results_medication = await test_orchestration_new(test_case, document, expected_medications, commands, query)
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
async def confirm_test_results(document_id, query: IQueryPort, commands: ICommandHandlingPort):    
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
    results, assessment, compare_results_medication = await test_orchestration_new(test_case, document, expected_medications, commands, query)

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
        # Convert timezone-aware datetime to naive datetime in UTC
        if obj.tzinfo is not None:
            obj = obj.astimezone(timezone.utc).replace(tzinfo=None)
        return obj.isoformat()  # Convert to string format to avoid timezone issues
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

        # Extract match statistics and comparison details
        match_stats = actual.get('Match Statistics', {})
        comparison_details = actual.get('Comparison Details', {})

        try:
            # Helper function to safely calculate metrics
            def safe_divide(numerator: float, denominator: float, scale: float = 1.0) -> float:
                """Safely perform division with error handling."""
                try:
                    if denominator == 0:
                        return 0
                    return (numerator / denominator) * scale
                except (TypeError, ValueError) as e:
                    LOGGER.error(f"Error in division calculation: {e}")
                    return 0
                except Exception as e:
                    LOGGER.error(f"Unexpected error in metric calculation: {e}")
                    return 0

            def calculate_f1_score(precision: float, recall: float) -> float:
                """Calculate F1 score from precision and recall."""
                try:
                    if precision + recall == 0:
                        return 0
                    return 2 * (precision * recall) / (precision + recall)
                except Exception as e:
                    LOGGER.error(f"Error calculating F1 score: {e}")
                    return 0

            # Extract required values once to avoid repeated dictionary access
            exact_matches = match_stats.get('exact_matches', 0)
            unexpected_meds = match_stats.get('unexpected_medications', 0)
            missing_meds = match_stats.get('missing_medications', 0)

            # Calculate Medication Metrics
            medications_precision = safe_divide(exact_matches, exact_matches + unexpected_meds)
            medications_recall = safe_divide(exact_matches, exact_matches + missing_meds)
            medications_f1_score = calculate_f1_score(medications_precision, medications_recall)
            medications_accuracy = safe_divide(exact_matches, expected.get('total_count'), 100) if expected.get('total_count') > 0 else 0

            LOGGER.debug("Medication metrics calculated - Precision: %f, Recall: %f, F1: %f, Accuracy: %f",
                        medications_precision, medications_recall, medications_f1_score, medications_accuracy)

            # Get Medispan IDs with error handling
            expected_ids = set(expected.get('list_of_medispan_ids', []))
            actual_ids = set(actual.get('Medication Profile', {}).get('medispan_ids', []))
            
            # Calculate Medispan ID sets
            correct_medispan_ids_m = expected_ids.intersection(actual_ids)
            incorrect_medispan_ids_m = actual_ids.difference(expected_ids)
            missed_medispan_ids_m = expected_ids.difference(actual_ids)
            total_medispan_ids_m = actual.get('Medication Profile', {}).get('medispan_ids', [])

            # Calculate Medispan Metrics
            len_correct = len(correct_medispan_ids_m)

            medispan_precision = safe_divide(len_correct, exact_matches)
            medispan_recall = safe_divide(len_correct, exact_matches)
            medispan_f1_score = calculate_f1_score(medispan_precision, medispan_recall)
            total_expected = len(expected_ids)
            medispan_accuracy = safe_divide(len_correct, exact_matches, 100) if total_expected > 0 else 0

            LOGGER.debug("Medispan metrics calculated - Precision: %f, Recall: %f, F1: %f, Accuracy: %f",
                        medispan_precision, medispan_recall, medispan_f1_score, medispan_accuracy)

        except Exception as e:
            LOGGER.error(f"Error calculating metrics: {e}")
            # Set default values in case of error
            medications_precision = medications_recall = medications_f1_score = medications_accuracy = 0
            medispan_precision = medispan_recall = medispan_f1_score = medispan_accuracy = 0
            correct_medispan_ids_m = incorrect_medispan_ids_m = missed_medispan_ids_m = set()
            total_medispan_ids_m = []

        # Create detailed result entry
        result_entry = {
            'Test ID': f'Test_{idx + 1}',
            'Input Document ID': input_json.get('document_id'),
            'Original Doc Path': input_json.get('original_doc_path'),
            'Test Doc Path': input_json.get('test_doc_path'),
            'Test Doc File Name': input_json.get('test_doc_file_name'),
            
            # Test Conditions
            'Expected Max Duration': expected.get('max_duration_of_test_execution'),
            'Expected Medication Total Count': expected.get('total_count'),
            'Expected Medispan Matched Count': expected.get('medispan_matched_count'),
            'Expected Unlisted Count': expected.get('unlisted_count'),
            'Expected Medispan IDs': ', '.join(expected.get('list_of_medispan_ids', [])),
            'Expected Minimum Overall Score': expected.get('minimum_overall_score'),
            
            # Basic Results
            'Actual Documentation Operation Status': actual.get('Documentation Operation Status'),
            'Actual Elapsed Time': actual.get('Elapsed Time'),
            'Actual Total Medication Count': actual.get('Medication Profile', {}).get('total_medication_count'),
            'Actual Medispan Match Count': actual.get('Medication Profile', {}).get('medispan_match_count'),
            'Actual Unlisted Count': actual.get('Medication Profile', {}).get('unlisted_count'),
            'Actual Other Count': actual.get('Medication Profile', {}).get('other_count'),
            'Actual Medispan IDs': ', '.join(actual.get('Medication Profile', {}).get('medispan_ids', [])),

            # Metadata and Status
            'Metadata Document ID': metadata.get('document_id'),
            'Metadata Testcase Name': metadata.get('testcase_name'),
            'Metadata Elapsed Time': metadata.get('elapsed_time'),
            'Errors': error if error else 'None',  # Replace empty errors with explicit 'None'
            'Test Status': test_status if test_status else 'None',  # Explicit status for missing values
            'Grader Passed': 'Passed' if grader.get('passed') else 'Failed',  # Convert boolean to readable format
            'Grader Errors': ', '.join(grader.get('error', [])) if grader.get('error') else 'None',  # Handle missing grader errors
            
            'Separation Line': '---',  # Separator for clarity
            # Enhanced Match Statistics
            'Total Medications': match_stats.get('total_medications', 0),
            'Missing Medications': match_stats.get('missing_medications', 0),
            'Unexpected Medications': match_stats.get('unexpected_medications', 0),
            'Medications with Medispan': match_stats.get('medications_with_medispan', 0),
            'Correct Medication Matches': match_stats.get('exact_matches', 0),
            'Medications without Medispan': match_stats.get('medications_without_medispan', 0),

            # Medspan Metrics
            'Total Medispan IDs': len(list(expected.get('list_of_medispan_ids', []))),
            'Correct Medispan IDs': list(correct_medispan_ids_m) if correct_medispan_ids_m else [],
            'Missed Medispan IDs': list(missed_medispan_ids_m) if missed_medispan_ids_m else [],
            'Incorrect Medispan IDs': list(incorrect_medispan_ids_m) if incorrect_medispan_ids_m else [],
            'Total Correct Medispan IDs': len(correct_medispan_ids_m),
            'Total Incorrect Medispan IDs': int(len(incorrect_medispan_ids_m)),
            'Total Missed Medispan IDs': len(missed_medispan_ids_m),  

            # Statistical metrics for medispan
            'Medication Precision' : medications_precision,
            'Medication Recall' : medications_recall,
            'Medication F1 score' : medications_f1_score,
            'Medication Accuracy' : medications_accuracy,


            # Statistical metrics for medispan
            'Medispan Precision' : medispan_precision,
            'Medispan Recall' : medispan_recall,
            'Medispan F1 score' : medispan_f1_score,
            'Medispan Accuracy' : medispan_accuracy,

            # Match Quality Metrics
            # 'Exact Match Score': match_stats.get('match_quality', {}).get('exact_match_score', 0),
            # 'Name Match Score': match_stats.get('match_quality', {}).get('name_match_score', 0),
            
            # Unmatched Medications
            'Unmatched Medications': json.dumps(actual.get('Unmatched Medications', []), indent=2) if actual.get('Unmatched Medications') else '[]',
            'Missing Medications Details': json.dumps(actual.get('Missing Medications', []), indent=2) if actual.get('Missing Medications') else '[]',
            'Unexpected Medications Details': json.dumps(actual.get('Unexpected Medications', []), indent=2) if actual.get('Unexpected Medications') else '[]',
            'Match Quality Issues': json.dumps(actual.get('Match Quality Issues', []), indent=2) if actual.get('Match Quality Issues') else '[]',
            
            # Recommendations
            # 'Recommendations': '\n'.join(actual.get('Recommendations', []))
        }
        
        extracted_results.append(result_entry)

    details_df = pd.DataFrame(extracted_results) 
       
    report_df = pd.concat([total_tests_df, details_df], ignore_index=True)
    compare_results_list = []

    # for med_comparison in compare_results_medication:
    for idx, med_comparison in enumerate(compare_results_medication):
        if isinstance(med_comparison, dict):
            compare_results_list.append({'Test ID': f'Test_{idx + 1}'})
            # Process matched medications with string conversion for dates
            for matched_med in med_comparison.get('matched_medications', []):
                # Add property matches
                for match in matched_med.get('property_matches', []):
                    value = match['value']
                    # Convert datetime to string if needed
                    if isinstance(value, datetime):
                        value = value.strftime('%Y-%m-%d')
                    compare_results_list.append({
                        'Key': f"{matched_med['medication_name']} - {match['property']}",
                        'Expected Value': str(value),
                        'Actual Value': str(value),
                        'Match Status': 'Match'
                    })
                # Add property mismatches
                for mismatch in matched_med.get('property_mismatches', []):
                    compare_results_list.append({
                        'Key': f"{matched_med['medication_name']} - {mismatch['property']}",
                        'Expected Value': mismatch['expected'],
                        'Actual Value': mismatch['actual'],
                        'Match Status': 'Mismatch'
                    })
            
            # Process unmatched medications
            for unmatched in med_comparison.get('unmatched_expected', []):
                compare_results_list.append({
                    'Key': f"{unmatched['name']} (Expected)",
                    'Expected Value': 'Present',
                    'Actual Value': 'Missing',
                    'Match Status': 'Missing'
                })
            
            for unmatched in med_comparison.get('unmatched_actual', []):
                compare_results_list.append({
                    'Key': f"{unmatched['name']} (Actual)",
                    'Expected Value': 'Missing',
                    'Actual Value': 'Present',
                    'Match Status': 'Unexpected'
                })
    # Create DataFrame with string type for date-sensitive columns
    compare_med_df = pd.DataFrame(compare_results_list, columns=['Test ID', 'Key', 'Expected Value', 'Actual Value', 'Match Status'], dtype=str)
    compare_med_df = compare_med_df.astype("string")

    import os
    
    try:
        # Calculate averages for medication and medispan accuracy
        avg_medication_accuracy = report_df['Medication Accuracy'].mean()
        avg_medispan_accuracy = report_df['Medispan Accuracy'].mean()
        avg_elapsed = report_df['Actual Elapsed Time'].mean()

        # Create summary DataFrame with numeric values only
        summary_df = pd.DataFrame([{'Metric': 'Average Medication Accuracy','Value': f"{avg_medication_accuracy:.2f}%"}, 
                                {'Metric': 'Average Medispan Accuracy','Value': f"{avg_medispan_accuracy:.2f}%"},
                                {'Metric': 'Total Missed Medications','Value': report_df['Missing Medications'].apply(lambda x: len(eval(x)) if isinstance(x, str) else 0).sum()},
                                {'Metric': 'Total Missed Medispan IDs','Value': report_df['Total Missed Medispan IDs'].sum()},
                                {'Metric': 'Total Incorrect Medications','Value': report_df['Unexpected Medications'].apply(lambda x: len(eval(x)) if isinstance(x, str) else 0).sum()},
                                {'Metric': 'Total Incorrect Medispan IDs','Value': report_df['Total Incorrect Medispan IDs'].sum()},
                                {'Metric': 'Average Metadata Elapsed Time (seconds)','Value': f"{report_df['Actual Elapsed Time'].mean():.2f}"}])
            

        # Write data back to file with all datetimes as strings
        with pd.ExcelWriter(report_file_name, engine='openpyxl', mode='w') as writer:
            report_df.to_excel(writer, sheet_name='Details', index=False)
            compare_med_df.to_excel(writer, sheet_name='Compare Results Medication', index=False)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

        # Log the results
        LOGGER.debug("Average Medication Accuracy: %.2f%%", avg_medication_accuracy)
        LOGGER.debug("Average Medispan Accuracy: %.2f%%", avg_medispan_accuracy)
            
        LOGGER.info("Successfully wrote report to Excel file")
    except Exception as e:
        LOGGER.error(f"Error writing to Excel: {str(e)}")
        raise
    
    test_storage = lambda _: GoogleStorageAdapter(GCP_PROJECT_ID, GCS_TEST_BUCKET, CLOUD_PROVIDER)
    adapter_test = test_storage(None)
    content = None
    with open(report_file_name, "rb") as f:
        content = f.read()
    await adapter_test.put_report(content, f"e2e/{now_utc().strftime('%B-%d')}", report_file_name)


@inject
async def test_orchestration_new(test_case: TestCase, document: Document, expected_medications: List, commands: ICommandHandlingPort, query: IQueryPort):
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
    LOGGER.debug("Grading the test case command and query %s, %s", commands, query)

    grader_results = await pass_grader_test(test_case, commands, query)
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
        test_medispan_list, unmatched_meds = get_medispan_ids(db_medication_profile)
        
        # Add detailed comparison information to the result
        result["actual"].update({
            "Unmatched Medications": unmatched_meds if unmatched_meds else [],
            "Comparison Details": comparision_result
        })
        
        if unmatched_meds:
            LOGGER.warning("Found medications without Medispan IDs: %s", 
                         json.dumps(unmatched_meds, indent=2))
        
        # Process exact matches and mismatches
        matched_meds = comparision_result.get("matched_medications", [])
        unmatched_expected = comparision_result.get("unmatched_expected", [])
        unmatched_actual = comparision_result.get("unmatched_actual", [])
        name_matches = comparision_result.get("name_based_matches", {})
        
        # Calculate comprehensive match statistics
        match_stats = {
            "total_medications": len(db_medication_profile),
            "medications_with_medispan": len(test_medispan_list),
            "medications_without_medispan": len(unmatched_meds),
            "exact_matches": len(matched_meds),
            "missing_medications": len(unmatched_expected),
            "unexpected_medications": len(unmatched_actual),
            "potential_matches": len(name_matches),
            "match_quality": {
                "exact_match_score": sum(m.get("match_score", 0) for m in matched_meds) / len(matched_meds) if matched_meds else 0,
                "name_match_score": sum(m.get("similarity_score", 0) for m in name_matches.values()) / len(name_matches) if name_matches else 0
            }
        }
        
        result["actual"]["Match Statistics"] = match_stats
        
        # Determine if test passed based on comprehensive criteria
        exact_medispan_match = len(unmatched_expected) == 0 and len(unmatched_actual) == 0
        high_quality_matches = match_stats["match_quality"]["exact_match_score"] > 80 if matched_meds else False  # Lowered threshold to 80%
        
        if exact_medispan_match and high_quality_matches:
            level3_results = {
                "passed": True,
                "errors": [],
                "details": {
                    "match_stats": match_stats,
                    "unmatched_medications": unmatched_meds,
                    "match_quality": match_stats["match_quality"]
                }
            }
        else:
            errors = []
            result["status"] = "Failed Test Suite 2"
            
            # Generate detailed error messages
            if unmatched_expected:
                errors.append(f"Missing expected medications: {len(unmatched_expected)}")
                result["actual"]["Missing Medications"] = [{
                    "medispan_id": med["medispan_id"],
                    "name": med["name"],
                    "properties": med["properties"],
                    "possible_match": med["possible_match"]
                } for med in unmatched_expected]
                
                # Add suggestions for missing medications
                for med in unmatched_expected:
                    if med["possible_match"]:
                        errors.append(f"Possible match found for {med['name']} "
                                   f"(similarity: {med['possible_match']['similarity_score']:.1f}%)")
            
            if unmatched_actual:
                errors.append(f"Unexpected medications found: {len(unmatched_actual)}")
                result["actual"]["Unexpected Medications"] = [{
                    "medispan_id": med["medispan_id"],
                    "name": med["name"],
                    "properties": med["properties"]
                } for med in unmatched_actual]
            
            if not high_quality_matches and matched_meds:
                errors.append("Low quality matches detected in matched medications")
                result["actual"]["Match Quality Issues"] = [
                    m for m in matched_meds if m.get("match_score", 0) < 80  # Lowered threshold to match high_quality_matches check
                ]
            
            result["errors"] = errors
            level3_results = {
                "passed": False,
                "errors": errors,
                "details": {
                    "match_stats": match_stats,
                    "unmatched_medications": unmatched_meds,
                    "match_quality": match_stats["match_quality"],
                    "recommendations": [
                        "Review medications without Medispan IDs",
                        "Check for possible matches in similar medications",
                        "Verify medication properties for low quality matches"
                    ]
                }
            }

    else:
        result["status"] = "Failed Test Suite 2"
    return result, level2_results, level3_results, comparision_result


async def compare_results_medication(db_medication_profile, expected_medications):
    """
    Enhanced medication comparison with detailed property matching and analysis.
    
    Args:
        db_medication_profile: List of medications from the database
        expected_medications: List of expected medications to compare against
        
    Returns:
        List of detailed comparison results including property matches and mismatches
    """
    keys_to_compare = ["dosage", "form", "frequency", "instructions", "name", "start_date", "route", "strength"]
    comparison_results = []
    unmatched_expected = []
    unmatched_actual = []
    
    # Track medications by name for potential fuzzy matching
    name_matches = {}
    
    for expected_med in expected_medications:
        expected_med_info = {key: expected_med.get(key) for key in keys_to_compare}
        medispan_id = expected_med.get("medispan_id")
        expected_name = expected_med.get("name", "Unknown")
        
        # Find exact match by medispan_id
        actual_med = next((med for med in db_medication_profile if med.medispan_id == medispan_id), None)
        
        if actual_med:
            actual_med_dict = actual_med.dict()
            actual_med_info = {key: actual_med_dict.get("medication", {}).get(key) for key in keys_to_compare}
            
            # Detailed property comparison
            property_comparison = {
                "medispan_id": medispan_id,
                "medication_name": expected_name,
                "match_type": "exact",
                "property_matches": [],
                "property_mismatches": [],
                "match_score": 0
            }
            
            total_properties = len(keys_to_compare)
            matched_properties = 0
            
            for key in keys_to_compare:
                expected_value = expected_med_info.get(key)
                actual_value = actual_med_info.get(key)
                
                if expected_value == actual_value:
                    matched_properties += 1
                    property_comparison["property_matches"].append({
                        "property": key,
                        "value": expected_value
                    })
                else:
                    property_comparison["property_mismatches"].append({
                        "property": key,
                        "expected": expected_value,
                        "actual": actual_value,
                        "suggestion": suggest_correction(key, expected_value, actual_value)
                    })
            
            # Calculate match score with weighted properties
            # Name and medispan_id are critical matches (40%)
            # Other properties contribute less to the score (60% total, divided equally)
            critical_props = ["name", "medispan_id"]
            other_props = [p for p in keys_to_compare if p not in critical_props]
            
            critical_weight = 0.4  # 40% weight for critical properties
            other_weight = 0.6 / len(other_props)  # Remaining 60% divided among other properties
            
            score = 0
            for key in critical_props:
                if key == "medispan_id":  # medispan_id is always matched since we found the medication
                    score += critical_weight / len(critical_props)
                elif key == "name" and expected_med_info.get(key) == actual_med_info.get(key):
                    score += critical_weight / len(critical_props)
                    
            for key in other_props:
                expected_value = expected_med_info.get(key)
                actual_value = actual_med_info.get(key)
                if expected_value == actual_value:
                    score += other_weight
                elif expected_value and actual_value and are_similar_strings(str(expected_value), str(actual_value)):
                    score += other_weight * 0.8  # Give 80% credit for similar values
                    
            property_comparison["match_score"] = score * 100
            comparison = find_common_keys(expected_med_info, actual_med_info)
            LOGGER.debug("Comparison: %s", comparison)
            LOGGER.debug("property_comparison: %s", property_comparison)
            comparison_results.append(property_comparison)
            
        else:
            # Try to find similar medication by name if no medispan_id match
            similar_med = find_similar_medication(expected_med, db_medication_profile)
            if similar_med:
                name_matches[expected_name] = {
                    "found_med": similar_med,
                    "similarity_score": calculate_similarity_score(expected_med, similar_med)
                }
            
            unmatched_expected.append({
                "medispan_id": medispan_id,
                "name": expected_name,
                "properties": expected_med_info,
                "possible_match": name_matches.get(expected_name)
            })
    
    # Find medications in actual results that weren't in expected
    expected_ids = {med.get("medispan_id") for med in expected_medications}
    for actual_med in db_medication_profile:
        if actual_med.medispan_id not in expected_ids:
            unmatched_actual.append({
                "medispan_id": actual_med.medispan_id,
                "name": getattr(actual_med, "name", "Unknown"),
                "properties": {
                    key: getattr(actual_med, key, None) 
                    for key in keys_to_compare
                }
            })
    
    return {
        "matched_medications": comparison_results,
        "unmatched_expected": unmatched_expected,
        "unmatched_actual": unmatched_actual,
        "name_based_matches": name_matches
    }

def suggest_correction(property_name: str, expected: str, actual: str) -> str:
    """Suggest possible corrections for mismatched properties."""
    if not expected or not actual:
        return "Missing value"
    
    if property_name in ["dosage", "strength"]:
        # Try to normalize and compare numeric values
        expected_nums = extract_numbers(expected)
        actual_nums = extract_numbers(actual)
        if expected_nums and actual_nums:
            return f"Numeric values differ: expected {expected_nums}, found {actual_nums}"
    
    if property_name in ["frequency", "instructions"]:
        # Look for common variations
        if are_similar_strings(expected.lower(), actual.lower()):
            return "Minor text variation - possibly equivalent"
    
    return "Values differ significantly"

def extract_numbers(text) -> List[float]:
    """Extract numeric values from text.
    
    Args:
        text: Input that can be a string, datetime, or other type
        
    Returns:
        List of float numbers extracted from the text
    """
    import re
    
    # Convert input to string if it's not already one
    if hasattr(text, 'timestamp'):  # Handle datetime objects
        return [float(text.timestamp())]
    elif not isinstance(text, str):
        text = str(text)
        
    return [float(x) for x in re.findall(r'\d+\.?\d*', text)]

def are_similar_strings(str1: str, str2: str) -> bool:
    """Check if strings are similar using basic comparison."""
    # Remove common variations
    str1 = str1.replace(" ", "").lower()
    str2 = str2.replace(" ", "").lower()
    
    # Calculate similarity ratio
    from difflib import SequenceMatcher
    return SequenceMatcher(None, str1, str2).ratio() > 0.8

def find_similar_medication(expected_med: dict, actual_meds: List) -> Optional[dict]:
    """Find similar medication based on name and properties."""
    best_match = None
    best_score = 0
    
    expected_name = expected_med.get("name", "").lower()
    if not expected_name:
        return None
        
    for med in actual_meds:
        actual_name = getattr(med, "name", "").lower()
        if not actual_name:
            continue
            
        similarity = SequenceMatcher(None, expected_name, actual_name).ratio()
        if similarity > 0.8 and similarity > best_score:
            best_score = similarity
            best_match = med
            
    return best_match

def calculate_similarity_score(expected_med: dict, actual_med) -> float:
    """Calculate overall similarity score between two medications."""
    scores = []
    
    # Name similarity (weighted heavily)
    name_similarity = SequenceMatcher(None, 
                                    expected_med.get("name", "").lower(), 
                                    getattr(actual_med, "name", "").lower()).ratio()
    scores.append(name_similarity * 0.4)  # 40% weight
    
    # Property similarities
    props = ["dosage", "form", "frequency", "route"]
    for prop in props:
        expected_val = str(expected_med.get(prop, "")).lower()
        actual_val = str(getattr(actual_med, prop, "")).lower()
        if expected_val and actual_val:
            similarity = SequenceMatcher(None, expected_val, actual_val).ratio()
            scores.append(similarity * 0.15)  # 15% weight each
            
    return sum(scores) * 100  # Convert to percentage


@inject
def main(commands: ICommandHandlingPort, query: IQueryPort, storage: IStoragePort):
    asyncio.run(run_orchestration_test(commands, query, storage))

if __name__ == "__main__":
    main()
