# how to run

make up

# if you add new package
1. uv add <package>
2. make init (uv lock and uv sync)

# Running Tests

## Prerequisites
The project uses pytest for testing. Test dependencies are defined in the `pyproject.toml` file under the `[project.optional-dependencies]` section. You can install these dependencies with:

```bash
make install-test
```

This will install the project along with all test dependencies including:
- pytest
- pytest-asyncio
- pytest-cov
- pytest-mock

## Unit Tests
To run unit tests:
```bash
make test
```

This command runs all tests in the `tests/unit` directory. Unit tests focus on testing individual components in isolation, using mocks for external dependencies.

## Integration Tests
To run integration tests:
```bash
make test-integration
```

This command runs all tests in the `tests/integration` directory. Integration tests verify that different components work together correctly.

## Test Coverage
To run tests with coverage report:
```bash
make test-coverage
```

This command runs all tests and generates a coverage report showing which parts of the code are covered by tests. The coverage report includes information about missing lines to help identify areas that need additional testing.

# Running Evaluation

The evaluation script is used to assess the accuracy of medication extraction and matching against known test cases.

## Prerequisites
Before running the evaluation, you need to:
1. Have appropriate GCP credentials set up
2. Have access to the test cases in Firestore

## Running the Evaluation
To run the evaluation script:
```bash
make run-evaluation
```

This command:
1. Sets up a tunnel to the database using Google Cloud IAP
2. Loads environment variables from `.env.qa`
3. Runs the evaluation script (`evaluation/evaluation.py`)

## Evaluation Process
The evaluation script:
1. Retrieves test cases from the `paperglass_testcases` Firestore collection
2. For each test case, extracts medications from the associated document
3. Compares the extracted medications with the expected medications
4. Generates detailed evaluation results including metrics on matching accuracy
5. Saves the results to CSV files (`evaluation_result.csv` and `evaluation_v2_results.csv`)

The evaluation results include information about:
- Successfully matched medications
- Partially matched medications
- Failed matches
- Medispan ID matching accuracy


# Terms

HHH Medication - 
Profile Medication - added from document (either edited or new)
Document Medication - extracted
Deduped client side profile medications

# Schema

Document --> run --> pageNo (medications count also saved) --> medications

medication_profile (always by patient) -> medications (HHH + add/edit/delete) includes documentId references from where it was added


# API Schema

For Selected document Ids, we need medication count by page (existing pageprofile api)

bubble click on page -> get medications for the page


 
1. Medications by documentIds -> Profile Medication (by selected doc) which also includes HHH Medications
2. Medications by Page (new one to support buble) -> Doc Medication
3. import medications from HHH API -> HHH Medication (always) updated to profile medication [move it to background job]
4. New/update/delete medication -> CRUD Profile medications
5. update medications to HHH API -> 


# Use cases

Document listing page
 - get list of docs (paginated) +  status + medications count (assumption: pipeline status and medication count)
 - get profile medications

selected documents medication review
 - get profile medications filtered by documentId + dedup with doc medications (medication based on active run) - [server side]
 - get bubbles -> api will get each page medications count
   - bubble click/unclick -> client side rendering (no dedup or additional operation needed)
 - edit medication drawer -> it should render client side and not do server side calls
 - edit medication (added from bubble selection) --> add medication to profile (server side)
 - edit medication (already part of profile medication) --> update medication in the  profile medication (server side)
 - add medication --> add medication to profile
 - delete medication (added from bubble selection) --> soft delete in doc medications
 - delete medication (part of profile medication) --> soft delete in profile medication

import from HHH
 - 
 


API for bubbles logic (count of medications) - get doc medications

API for profile medication - get profile medications 

Add from bubble to profile (transient) -> profile medications (already rendered in client side) deduped at client side with selected bubble/page medications

Remove by clicking bubble again (transient) -> remove page/bubble level medications from the deduped client side medications

Add/Edit/Delete Medications -> profile medications mutation (no dedup since user explictly adds. delete doesnt need dedup. edit is updating existing deduped record)

Updated Medication to HHH -> selected medications sent to HHH

Import from HHH -> profile medications mutation (dedup needed - e.g Tylenol from HHH should be reconcilled if Tylenol already exists in profile medications)


# Decisions

1. when a medication is added/edited from frontend, we do a dedup and update medication profile. Not worth doing same during extraction pipeline
2. 
