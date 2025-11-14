import asyncio
from typing import List
from enum import Enum
from datetime import datetime
from kink import inject # type: ignore
import json

from paperglass.settings import (
    VERSION,
    E2E_TEST_ENABLE,
    E2E_TEST_UPDATE_ENABLE,
    E2E_TEST_SAMPLE_SIZE,
    E2E_TEST_MAX_DURATION_SECONDS,
    E2E_TEST_MAX_DURATION_SECONDS_OVERRIDE,
    E2E_TEST_RUN_PATIENT_ID,
    E2E_TEST_ASSERTION_F1_GOOD_LOWER,
    E2E_TEST_TLDR_RESULTS_WINDOW_MINUTES,
    E2E_TEST_MEDICATION_RETRY_COUNT,
)
GOLDEN_DATASET_CATEGORY = "golden_dataset"

from paperglass.domain.util_json import DateTimeEncoder 
from paperglass.domain.utils.task_utils import retry_with_backoff
from paperglass.domain.model_metric import Metric
from paperglass.domain.models import (
    Document,
    ExtractedMedication,
)
from paperglass.domain.model_testing import ( 
    E2ETestCase,
    E2ETestCaseArchive,
    E2ETestDocumentExpections,
    E2ETestPageExpections,
    E2ETestCaseResults,
    E2ETestCaseSummaryResults,
)
from paperglass.domain.models_common import TimeoutException, NotFoundException
from paperglass.domain.values import (
    DocumentOperationType,
    DocumentOperationStatus,
    AccuracyAssessment,
)

from paperglass.domain.utils.uuid_utils import uuid4
from paperglass.domain.time import now_utc
from paperglass.domain.utils.token_utils import mktoken
from paperglass.domain.utils.exception_utils import exceptionToMap

from paperglass.usecases.v4.medications import list_medications


from paperglass.interface.ports import ICommandHandlingPort
from paperglass.usecases.commands import (
    CreateTestDocument
)

from paperglass.infrastructure.ports import (
    IUnitOfWork,
    IQueryPort,
    IStoragePort,
)

class TestMode(str, Enum):
    FULL = "full"
    SAMPLE = "sample"
    TEST_ONLY = "test_only"

from paperglass.log import getLogger
LOGGER = getLogger(__name__)

class TestHarness:

    def __init__(self):
        pass

    async def run(self, mode: str = TestMode.SAMPLE.value, sample_size: int = E2E_TEST_SAMPLE_SIZE, filename:str = None, run_id:str = uuid4().hex ):
        
        test_startdate = now_utc()

        extra = {
            "mode": mode,
            "sample_size": sample_size,
            "run_id": run_id,
            "startdate": test_startdate.isoformat(),
        }
        if not E2E_TEST_ENABLE:
            LOGGER.debug("TestHarness: E2E test is disabled", extra=extra)
            return

        LOGGER.debug("Starting test run...")

        if mode == TestMode.SAMPLE.value and sample_size is None:
            sample_size = E2E_TEST_SAMPLE_SIZE

        try:
            Metric.send("E2E::TestHarness::start", tags=extra)
            
            testcases = await self.list_testcases(mode, sample_size=sample_size)
            extra.update({
                "elapsed_time": (now_utc() - test_startdate).total_seconds(),
                "nbr_of_testcases": len(testcases) if testcases else 0,
            })
            Metric.send("E2E::TestHarness::list_testcases", tags=extra)

            # Record the aggregate test run to Firestore
            testcase_summary = await self.save_testcase_run(mode, run_id, test_startdate, testcases)
            
            await self.run_testcases(mode, run_id, test_startdate, testcases, is_do_assessment=False)
            extra.update({
                "elapsed_time": (now_utc() - test_startdate).total_seconds(),
            })
            Metric.send("E2E::TestHarness::run_testcases", tags=extra)

            return

            await self.persist_test_case_results(results)
            extra.update({
                "elapsed_time": (now_utc() - test_startdate).total_seconds(),
            })
            Metric.send("E2E::TestHarness::persist_testcase_results", tags=extra)

            summary = await self.compile_summary(mode, run_id, test_startdate, results)
            extra.update({
                "elapsed_time": (now_utc() - test_startdate).total_seconds(),
            })            
            Metric.send("E2E::TestHarness::compile_summary", tags=extra)

            await self.persist_summary(summary)
            extra.update({
                "elapsed_time": (now_utc() - test_startdate).total_seconds(),
            })
            Metric.send("E2E::TestHarness::persist_summary", tags=extra)
                        
            extra.update({
                "is_overall_passed": summary.is_overall_passed,
                "summary": summary.summary,
                "elapsed_time": (now_utc() - test_startdate).total_seconds(),
            })
            Metric.send("E2E::TestHarness::complete", tags=extra)
        except Exception as e:
            enddate = now_utc()
            extra.update({
                "error": exceptionToMap(e),
                "enddate": enddate.isoformat(),
                "elapsed_time": (enddate - test_startdate).total_seconds(),
            })
            LOGGER.error("Error running test harness", extra=extra)
            Metric.send("E2E::TestHarness::failed", tags=extra)
            raise e

    async def run_test_only(self, test_document_id: str, document_id: str, mode:str = "test_only"):
        LOGGER.debug("Starting test run for a single test case where document is already processed...")

        run_id = uuid4().hex
        test_startdate = now_utc()
        
        results = await self.test_only(mode, run_id, test_startdate, test_document_id, document_id)
        summary = await self.compile_summary(mode, run_id, test_startdate, results)
        await self.persist_summary(summary)

    
    @inject
    async def list_testcases(self, mode:str, query: IQueryPort, sample_size: int = E2E_TEST_SAMPLE_SIZE) -> List[E2ETestCase]:
        LOGGER.debug("Get list of test cases")
        testcases = []
        if mode == TestMode.FULL.value:
            LOGGER.debug("Get all test cases")
            testcases = await query.list_testcases()
        elif mode == TestMode.SAMPLE.value:
            LOGGER.debug("Get sample of %s test cases", sample_size)
            testcases = await query.list_testcases(sample_size)
        else:
            raise ValueError("Invalid mode: %s", mode)

        return testcases
    
    @inject
    async def save_testcase_run(self, mode:str, run_id:str, test_startdate:datetime, testcases: List[E2ETestCase], commands: ICommandHandlingPort):
        from paperglass.usecases.commands import CreateE2ETestCaseSummaryResults
        from paperglass.interface.ports import ICommandHandlingPort

        summary_results = E2ETestCaseSummaryResults(id=run_id,
                                                    mode=mode,
                                                    run_id=run_id,
                                                    test_startdate=test_startdate,
                                                    summary=None,
                                                    is_overall_passed=None,
                                                    test_cases=testcases)
        
        command = CreateE2ETestCaseSummaryResults(summary_testcase_results=summary_results)

        @inject
        async def save_testcase_run(command:CreateE2ETestCaseSummaryResults, commands: ICommandHandlingPort):
            return await commands.handle_command(command)


        LOGGER.debug("Saving testcase run results: %s", summary_results)

        results = await save_testcase_run(command)
                
        return results

    
    async def run_testcases(self, mode: str, run_id:str, test_startdate:datetime, testcases: List[E2ETestCase], is_do_assessment:bool = False) -> List[E2ETestCaseResults]:
        LOGGER.debug("For each testcase, create a new document (which launches an extract pipeline in parallel so that once the first document is done, the others are not far behind)")
        
        results = []

        for testcase in testcases:
            extra = {
                "mode": mode,
                "run_id": run_id,
                "testcase_id": testcase.id,
                "testcase_document_id": testcase.test_document_id,
            }
            LOGGER.debug("Creating document for test case: %s", testcase.test_document_name, extra=extra)
            document = await self.create_document(testcase=testcase, mode=mode, run_id=run_id, start_date=test_startdate)
            
        return results    
    

    """
    This is a test only mode where the document is already processed and we are just running the test case to get the assessment"""
    @inject
    async def test_only(self, mode:str, run_id:str, test_startdate:datetime, test_document_id, document_id: str, query:IQueryPort):
        
        #This gets the generated test document
        doc = await query.get_document(document_id)
        document: Document = Document(**doc)        

        testcase = await query.get_testcase_by_document_id(test_document_id)
        if not testcase:
            raise NotFoundException(f"Test case not found for document: {test_document_id}")
        
        assessment = await self.run_testcase(mode, testcase, document, run_id, test_startdate)

        return [assessment]

    @inject
    async def assess_summary(self, run_id:str, uow: IUnitOfWork, query: IQueryPort):
        LOGGER.debug("Assessing summary for run_id: %s", run_id)

        # Get summary
        #summary:E2ETestCaseSummaryResults = await uow.get(E2ETestCaseSummaryResults, run_id)
        summary:E2ETestCaseSummaryResults = await query.get_testcase_results_summary_by_runid(run_id)

        if not summary:
            LOGGER.error("Summary not found for run_id: %s", run_id)
            raise NotFoundException(f"Summary not found for run_id: {run_id}")
        
        if isinstance(summary, list):
            summary = summary[0]

        # Get all testcase results for summary
        detail_results: List[E2ETestCaseResults] = await query.get_testcase_results_details_by_runid(run_id)

        # Filter out duplicates based on test_case.id
        unique_results = {result.test_case.id: result for result in detail_results}
        detail_results = list(unique_results.values())

        # Calculate the summary stats
        summary.results = detail_results
        overall_assessment = AccuracyAssessment()
        for result in detail_results:
            overall_assessment.add(result.assessment)

        summary.summary = overall_assessment.get_summary()
        summary.nbr_of_testcases = len(summary.test_cases) if summary.test_cases else 0

        # Determine if the test case run is complete or not
        nbr_test_cases = len(summary.test_cases) if summary.test_cases else 0
        nbr_test_results = len(detail_results) if detail_results else 0

        if nbr_test_cases == nbr_test_results:
            LOGGER.debug("Test case run is detected as COMPLETE: %s", run_id)
            summary.status = DocumentOperationStatus.COMPLETED.value        

        # Return the summary
        return summary
    
    async def assess_testcase(self, mode:str, testcase: E2ETestCase, document:Document, run_id:str, test_startdate:datetime) -> E2ETestCaseResults:
                
        medications = await self.get_document_medications(document, testcase)
        assessment: E2ETestCaseResults = await self.assert_testcase(testcase, document, medications, mode, run_id, test_startdate)

        extra = {
            "mode": mode,
            "run_id": run_id,
            "test_startdate": test_startdate,
            "test_document_name": testcase.test_document_name,
            "test_document_id": testcase.test_document_id,
            "document_id": document.id,
            "document_name": document.file_name,
            "is_overall_passed": assessment.is_overall_passed,
            "elapsed_time": (now_utc() - test_startdate).total_seconds(),
            "assessment": assessment.assessment.get_summary()
        }

        Metric.send("E2E::TestHarness::run_testcase::assessment", tags=extra)

        return assessment
    
    @inject
    async def create_document(self, testcase: E2ETestCase, mode: str, run_id: str, start_date: datetime, query:IQueryPort):        
        LOGGER.debug("Create a new document (which launches an extract pipeline): %s", testcase.test_document_name)

        document_id = testcase.test_document_id
        doc = await query.get_document(document_id)

        if not doc:
            raise NotFoundException(f"Document not found: {document_id}")

        document: Document = Document(**doc)

        storage_uri = document.storage_uri
        app_id = document.app_id
        tenant_id = document.tenant_id
        patient_id = E2E_TEST_RUN_PATIENT_ID    # We will assign this document to a different patient to keep the source golden dataset separate from the documents created during the test run
        filename = testcase.test_document_name
        token = mktoken(app_id, tenant_id, patient_id)
        
        metadata = {
            "is_test": True,
            "e2e_test": {
                "source": {
                    "document_id": document_id,
                    "storage_uri": storage_uri,
                    "filename": filename,
                },
                "mode": mode,
                "testrun_id": run_id,
                "testcase_id": testcase.id,
                "test_document_name": testcase.test_document_name,
                "test_startdate": start_date.isoformat(),
            }
        }

        datestr = start_date.strftime("%Y%m%d-%H%M%S")

        name = f"e2e-{datestr}-{filename}"

        from paperglass.interface.ports import ICommandHandlingPort
        from paperglass.usecases.commands import (
            CreateTestDocument
        )

        create_test_doc = CreateTestDocument(
            app_id=app_id, tenant_id=tenant_id, patient_id=patient_id, storage_uri=storage_uri, name=name, token=token, metadata=metadata
        )

        @inject
        async def create_test_document(command:CreateTestDocument, commands: ICommandHandlingPort):
            return await commands.handle_command(command)            
        
        test_document = await create_test_document(create_test_doc)

        extra = {
            "testcase": testcase.dict(),
            "document": test_document.dict(),            
            "run_id": run_id,
            "test_startdate": start_date,
        }
        LOGGER.debug("Test document created", extra=extra)

        return test_document
    

    @inject
    async def get_document_medications(self, document: Document, testcase: E2ETestCase, query: IQueryPort):        
        from paperglass.usecases.v4.medications import list_medications

        results = {}
        for i in range(document.page_count):
            page_number = i + 1

            medications = []
            if testcase.page_expections.get(page_number):
                medications = await self.list_medications_retryable(document_id=document.id, page_number=page_number)
            else:
                # If we aren't expecting medications on a page, then only try to get the medications once
                medications = await list_medications(document_id=document.id, page_number=page_number)

            results[page_number] = medications
        
        return results

    @retry_with_backoff(max_retries=E2E_TEST_MEDICATION_RETRY_COUNT, initial_delay=0, retry_on_empty=True)
    async def list_medications_retryable(self, document_id:str, page_number:int):
        LOGGER.debug("List medications for document: %s, page: %s", document_id, page_number)
        medications = await list_medications(document_id=document_id, page_number=page_number)
        return medications
    
    async def assert_testcase(self, testcase: E2ETestCase, document: Document, medications: dict[int, list], mode:str, run_id: str, test_startdate: datetime):
        
        #LOGGER.debug("Medications for document: %s", medications)

        document_accuracy = AccuracyAssessment()

        page_accuracy = []

        for i in range(document.page_count):
            page_number = i + 1
            actual_page_medications = medications.get(page_number, [])
            page_expectations = testcase.page_expections.get(page_number)
            expected_page_medications = page_expectations.medication if page_expectations else []
            expected_page_medications = [ExtractedMedication(**x) for x in expected_page_medications]

            results = await self.assess_accuracy(actual_page_medications, expected_page_medications)
            page_accuracy.append(results)            

            document_accuracy.add(results)

        results = E2ETestCaseResults(
            id=uuid4().hex,
            mode=mode,
            run_id=run_id,
            document=document,
            test_case=testcase,
            test_startdate=test_startdate,
            assessment=document_accuracy,
            is_overall_passed=document_accuracy.is_pass
        )
        return results
    
    async def assess_accuracy(self, actuals, expecteds):

        accuracy_assessment = AccuracyAssessment()

        LOGGER.debug("Count of actual: %s  Count of expected: %s", len(actuals), len(expecteds))

        # Accuracy sort
        for actual in actuals:
            found = False
            actual_resolved = actual.resolved_medication
            for expected in expecteds:                
                expected_resolved = expected.resolved_medication
                if (actual_resolved.medispan_id is not None and actual_resolved.medispan_id==expected_resolved.medispan_id) or actual_resolved.matches(expected_resolved):
                    LOGGER.debug("Accurate match found: [%s] %s", actual_resolved.medispan_id, actual_resolved.to_string)
                    accuracy_assessment.accurate_items.append(actual)
                    found = True
                    break
            if not found:
                LOGGER.debug("Not accurate (could not match medication to expected): [%s] %s", actual_resolved.medispan_id, actual_resolved.to_string)
                accuracy_assessment.not_accurate_items.append(actual)

        # Recall sort
        for expected in expecteds:
            found = False
            expected_resolved = expected.resolved_medication
            for actual in actuals:
                actual_resolved = actual.resolved_medication
                if (expected_resolved.medispan_id is not None and actual_resolved.medispan_id==expected_resolved.medispan_id) or expected_resolved.matches(actual_resolved):
                    LOGGER.debug("Recall match found: [%s] %s", expected_resolved.medispan_id, expected_resolved.to_string)
                    accuracy_assessment.recalled_items.append(expected)
                    found = True
                    break
            if not found:
                LOGGER.debug("Not recalled (could not match expected to medication): [%s] %s", expected_resolved.medispan_id, expected_resolved.to_string)
                accuracy_assessment.not_recalled_items.append(expected)
            
        return accuracy_assessment

    
    @inject
    async def persist_test_case_results(self, test_results: List[E2ETestCaseResults], storage: IStoragePort):

        for test_result in test_results:
            test_result_json = json.dumps(test_result.dict(), indent=2, cls=DateTimeEncoder)
            path = f"e2e/{test_result.mode}/{test_result.test_startdate.strftime('%Y')}/{test_result.test_startdate.strftime('%m-%d')}/testcase_results"    
            file_name = f"e2e-test-{test_result.test_case.test_document_name}.json"

            LOGGER.debug("Persisting details to GCS: %s/%s", path, file_name)
            await storage.put_report(test_result_json, path, file_name)
        
        return
    
    async def compile_summary(self, mode: str, run_id:str, test_startdate:datetime, results: List[E2ETestCaseResults]) -> E2ETestCaseSummaryResults:

        extra = {
            "mode": mode,
            "run_id": run_id,
            "startdate": test_startdate.isoformat(),
            "nbr_of_results": len(results) if results else 0,
        }

        LOGGER.debug("Compiling summary of %s test results", len(results), extra=extra) 

        overall_assessment = AccuracyAssessment()

        for result in results:
            overall_assessment.add(result.assessment)
            extra ={
                "mode": mode,
                "run_id": run_id,
                "test_startdate": test_startdate,
                "testcase_id": result.test_case.id,
                "test_document_id": result.test_case.test_document_id,
                "test_document_name": result.test_case.test_document_name,
                "document_id": result.document.id,
                "document_name": result.document.file_name,
                "assessment": result.assessment.get_summary(),
            }            
            Metric.send("E2E::TestHarness::compile_summary:testcase", tags=extra)

        summary = E2ETestCaseSummaryResults(
            mode = mode,
            run_id = run_id,
            test_startdate = test_startdate,
            summary = overall_assessment.get_summary(),
            is_overall_passed = overall_assessment.is_pass,
            results = results
        )

        extra.update({
            "is_overall_passed": summary.is_overall_passed,
        })
        Metric.send("E2E::TestHarness::compile_summary:overall", tags=extra)

        return summary
    

    async def persist_summary(self, summary: E2ETestCaseSummaryResults):
        await self.persist_summary_to_gcs(summary)            
        return
    
    @inject
    async def persist_summary_to_gcs(self, summary:E2ETestCaseSummaryResults, storage: IStoragePort):
        LOGGER.debug("Persisting summary to GCS")
        summary_dict = summary.dict()
        summary_json = json.dumps(summary_dict, indent=2, cls=DateTimeEncoder)        
        path = f"e2e/{summary.mode}/{summary.test_startdate.strftime('%Y')}/{summary.test_startdate.strftime('%m-%d')}"
        file_name = f"e2e-test-summary-{summary.test_startdate.strftime('%Y%m%d-%H%M%S')}.json"
        tldr_file_name = f"e2e-test-tldr-{summary.test_startdate.strftime('%Y%m%d-%H%M%S')}.json"
        
        latest_path = f"e2e/{summary.mode}/latest"
        latest_file_name = f"e2e-test-summary-latest.json"
        tldr_latest_file_name = f"e2e-test-tldr-latest.json"

        version_latest_path = f"e2e/{summary.mode}/version/{VERSION}"

        LOGGER.debug("Persisting summary to GCS: %s/%s", path, file_name)
        await storage.put_report(summary_json, path, file_name)
        await storage.put_report(summary_json, latest_path, latest_file_name)
        await storage.put_report(summary_json, version_latest_path, latest_file_name)

        
        #Remove the results array to create more compact summary for TLDR
        summary_dict["results"] = None
        summary_json = json.dumps(summary_dict, indent=2, cls=DateTimeEncoder)

        await storage.put_report(summary_json, path, tldr_file_name)
        await storage.put_report(summary_json, latest_path, tldr_latest_file_name)
        await storage.put_report(summary_json, version_latest_path, tldr_latest_file_name)


        xlsx_bytes = summary.to_xlsx()
        xlsx_file_name = f"e2e-test-summary-{summary.test_startdate.strftime('%Y%m%d-%H%M%S')}.xlsx"
        xlsx_latest_file_name = f"e2e-test-summary-latest.xlsx"

        await storage.put_report(xlsx_bytes, path, xlsx_file_name)
        await storage.put_report(xlsx_bytes, latest_path, xlsx_latest_file_name)
        await storage.put_report(xlsx_bytes, version_latest_path, xlsx_latest_file_name)

        #LOGGER.debug("Summary JSON: %s", summary_json)
        return

    @inject
    async def get_testcase_latest_tldr(self, mode:str, storage: IStoragePort, query: IQueryPort, age_window:int = E2E_TEST_TLDR_RESULTS_WINDOW_MINUTES, f1_threshold:float = E2E_TEST_ASSERTION_F1_GOOD_LOWER) -> dict:
        path = f"e2e/{mode}/latest"
        file_name = f"e2e-test-tldr-latest.json"  # This could be done with the summary, but the large filesize results in a slow calculation time

        LOGGER.debug("Get latest TLDR summary data: %s/%s", path, file_name)

        summary = await query.get_testcase_results_summary_latest(mode=mode)
        summary:E2ETestCaseSummaryResults = summary[0] if summary else None
        
        #summary_json = await storage.get_report(path, file_name)
        #summary_dict = json.loads(summary_json)
        #summary: E2ETestCaseSummaryResults = E2ETestCaseSummaryResults(**summary_dict)

        # TODO The GCS latest summary doesn't have the embedded summary results or the individual test results. Fix this so that the persisted summary has the embedded summary
        # if summary.summary is None:
        #     LOGGER.debug("Summary is None, getting details from Firestore")
        #     detail_results = await query.get_testcase_results_details_by_runid(summary.run_id)
        #     overall_assessment = AccuracyAssessment()
        #     for result in detail_results:
        #         overall_assessment.add(result.assessment)

        #     summary.summary = overall_assessment.get_summary()


        LOGGER.debug("Summary: %s", summary)

        test_startdate = summary.test_startdate
        time_difference = now_utc() - test_startdate
        
        if time_difference.total_seconds() > age_window * 60:
            raise ValueError(f"Test results are too old ({time_difference.total_seconds()/60} min). Test results can be no older than {age_window} min old.  Test start date: {test_startdate}")
        else:
            LOGGER.debug("Test results are within the window of %s minutes", age_window)

        overall_passed = summary.summary["f1"] >= f1_threshold

        summary_dict = summary.dict()
        summary_dict["is_overall_passed"] = overall_passed

        tldr = summary_dict

        return tldr
    
    @inject
    async def get_testcase_latest_results(self, mode:str, storage: IStoragePort) -> E2ETestCaseSummaryResults:
        path = f"e2e/{mode}/latest"
        file_name = f"e2e-test-summary-latest.json"

        summary_json = await storage.get_report(path, file_name)
        report: E2ETestCaseSummaryResults = E2ETestCaseSummaryResults(**json.loads(summary_json))

        return report
