import re
import os
import sys
import json
import asyncio
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Add the src directory to the Python path to import modules from there
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from adapters.llm import StandardPromptAdapter

# check = "medmatch"
check = "medspanid"

from google.cloud import firestore
db = firestore.Client(project="viki-qa-app-wsky", database="viki-qa")
collection_ref = db.collection("meddb_medispan")

prompts = {
    "medspanid": """
        Please analyze the following JSON data, which contains results from different models.
        Compare the 'model_result' with the 'expected_result' for each record.
        Based on the comparison, calculate the accuracy of each model's predictions.

        Provide a summary of the accuracy, Precision, Recall, F1-Score, Total Expected, Total Extracted, No of True Positives, No of False Positives, No of False Negatives for each model only.
        Ensure the output is structured as a JSON object only, json should be able to convert to table format later.
        Response should be in the following format:
        {
            "model_name": {
                "accuracy": 0.95,
                "precision": 0.9,
                "recall": 0.85,
                "f1_score": 0.875,
                "total_expected": 100,
                "total_extracted": 95,
                "true_positives": 90,
                "false_positives": 5,
                "false_negatives": 10
            }
        }
        
        The data is:

        """,
    "medmatch": """
        Please analyze the following JSON data, which contains results from different models.
        Compare the 'model_result' with the 'expected_result' for each record.
        Based on the comparison, calculate the accuracy of each model's predictions.
        Ignore case-sensitive differences in medication names.
        e.g. 1, [OMEPRAZOLE, OXYGEN] and [O2 - OXYGEN, OMEPRAZOLE, DELAYED RELEASE] both should be considered as matching.
        e.g. 2, [MAGNESIUM, OMEPRAZOLE] and [MAGNESIUM (AS MAGNESIUM OXIDE), OMEPRAZOLE, DELAYED RELEASE] both should be considered as matching.
        e.g. 3, [CLOBETASOL] and [CLOBETASOL 0.05% TOPICAL CREAM] both should be considered as matching.
        e.g. 3, [CALCIUM + D(3), FERROUS SULFATE (65 MG IRON)] and [CALCIUM 600 + D(3), FERROUS SULFATE] both should be considered as matching.

        Provide a summary of the accuracy, Precision, Recall, F1-Score, Total Expected, Total Extracted, No of True Positives, No of False Positives, No of False Negatives for each model, including any discrepancies found.
        Ensure the output is structured as a JSON object only, json should be able to convert to table format later.
        Response should be in the following format:
        {
            "model_name": {
                "accuracy": 0.95,
                "precision": 0.9,
                "recall": 0.85,
                "f1_score": 0.875,
                "total_expected": 100,
                "total_extracted": 95,
                "true_positives": 90,
                "false_positives": 5,
                "false_negatives": 10
            }
        }

        The data is:

        """
}

async def main():

    with open('model_comparison_results.json', 'r') as f:
        result_data = json.load(f)
    rows = []
    for rec in result_data:
        del rec["test_start_date"]
        del rec["test_source_document_name"]
        del rec["test_source_document_id"]
        del rec["test_source_document_path"]
        del rec["category"]
        del rec["run_id"]
        del rec["errors"]
        for page_name, page in rec.get("page_results", {}).items():
            if check == "medspanid":
                extracted_medispan_ids = set(page.get("extracted_medispan_ids"))
                expected_medispan_ids = set(page.get("expected_medispan_ids"))
                extracted_unique = list(extracted_medispan_ids - expected_medispan_ids)  # Items in list1 but not in list2
                expected_unique = list(expected_medispan_ids - extracted_medispan_ids)
                
                # rows = []

                extracted_unique_drugs = [collection_ref.where("ExternalDrugId", "==", int(i)).get() for i in extracted_unique]
                extracted_unique_drugs = [i[0].to_dict() if i else {} for i in extracted_unique_drugs]
                for drug in extracted_unique_drugs:
                    rows.append({
                        "TestCaseDocId": rec["test_case_id"],
                        "Page": page_name,
                        "Type": "Extracted",
                        "NameDescription": drug.get("NameDescription"),
                        "Route": drug.get("Route"),
                        "Strength": drug.get("Strength"),
                        "DosageForm": drug.get("Dosage_Form"),
                        "MediSpanID": drug.get("ExternalDrugId")
                    })

                expected_unique_drugs = [collection_ref.where("ExternalDrugId", "==", int(i)).get() for i in expected_unique]
                expected_unique_drugs = [i[0].to_dict() if i else {} for i in expected_unique_drugs]
                for drug in expected_unique_drugs:
                    rows.append({
                        "TestCaseDocId": rec["test_case_id"],
                        "Page": page_name,
                        "Type": "Expected",
                        "NameDescription": drug.get("NameDescription"),
                        "Route": drug.get("Route"),
                        "Strength": drug.get("Strength"),
                        "DosageForm": drug.get("Dosage_Form"),
                        "MediSpanID": drug.get("ExternalDrugId")
                    })
                page.pop("extracted_medications", None)
                page.pop("expected_medications", None)
            elif check == "medmatch":
                page.pop("extracted_medispan_ids", None)
                page.pop("expected_medispan_ids", None)
        del rec["test_case_id"]
        
    # The data variable now holds the JSON content
    # The prompt below instructs the model to compare the results and calculate accuracy
    df = pd.DataFrame(rows)
    df.to_excel('med_comparison_tall.xlsx', index=False)

    prompt = prompts[check] + json.dumps(result_data, indent=2)

    # Call the multi_modal_predict_2 function with the new prompt
    # Note: You need to specify the model you want to use, e.g., "gemini-1.5-flash-001"
    result = await StandardPromptAdapter().multi_modal_predict_2(
        prompt,
        model="gemini-2.5-flash",
        metadata={}
    )
    json_str = re.sub(r"^```json|```$", "", result, flags=re.MULTILINE).strip()

    data = json.loads(json_str)

    df = pd.DataFrame(data).T

    df.reset_index(inplace=True)
    df.rename(columns={'index': 'Model'}, inplace=True)

    df.to_excel(f'model_metrics-{check}.xlsx', index=False)

    print("Saved to model_metrics.xlsx")

if __name__ == "__main__":
    asyncio.run(main())