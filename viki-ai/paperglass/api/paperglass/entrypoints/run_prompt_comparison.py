import asyncio
import sys, os
import json
import time
from datetime import datetime

import vertexai
from vertexai.generative_models import GenerativeModel, Part
from google.cloud import storage

import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)

# Configuration - set these values directly
GCP_PROJECT_ID = "viki-dev-app-wsky"  # Update this to your project ID
GCP_LOCATION_2 = "us-east4"  # Update this to your preferred location

LOGGER.setLevel(logging.DEBUG)
logging.getLogger('google.auth._default').setLevel(logging.INFO)
logging.getLogger('grpc._cython.cygrpc').setLevel(logging.INFO)
logging.getLogger('google.auth.transport.requests').setLevel(logging.INFO)
logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)

# Test Configuration Variables
PROMPT_1 = """
Please study this document:[Task]:      
            please extract medications as array of JSON with keys as name, strength, dosage, route, form, discontinued_date, frequency, start_date, end_date, instructions,explanation, document_reference and page_number.      
            Please do not include any markup other than JSON.      
            Please format start_date and end_date as mm/dd/yyyy.      
            **The 'name' field should include alias , punctuation if present but exclude strength and unit of measurement (e.g., 'Aspirin 81mg' should be 'Aspirin', and 'hydrocodone 5 mg-acetaminophen' should be 'hydrocodone-acetaminophen')**     
            **Distinguish between dosage (eg. 1 tab, 2-3 tablets) and strength of medication.     Dosage field does not have Unit of Measurement(MG, ML, GM, % , UT, ACT, UNIT), if it has considered as Strength, leave dosage blank**
"""
PROMPT_2 = """
                For each GIVEN MEDICATIONS, can you find the best medication match from the MATCH LIST given below? Please follow these instructions:
                1) The name of the GIVEN MEDICATION should be match the \"NameDescription\" field of the MATCH LIST entries. Otherwise no name match
                2) Prefer the match if the MATCH LIST entry's \"NameDescription\" begins with the first word of the GIVEN MEDICATION name
                3) Prefer the match if the name of the GIVEN MEDICATION exactly matches (case insensitive) the name of the MATCH LIST \"NameDescription\" entry.  
                4) Lower the consideration for the match if the name of the GIVEN MEDICATION only matches the \"GenericName\" field and does not match the \"NameDescription\" field of the MATCH LIST entry.
                5) If the GIVEN MEDICATION has medication strength specified, select from the list only if there is exact match of the Strength
                6) If the GIVEN MEDICATION has medication form specified, select from the list only if there is exact match of the Dosage_Form
                7) If the GIVEN MEDICATION has medication route specified, select from the list only if there is exact match of the Route

                The list of GIVEN MEDICATIONS is a dictionary with the key being the index and the value being the name of the medication.

                For each medication, only return the best match from the list. 

                Return the response in the following json format:

                [
                    {"**MEDICATION_ID": "**MATCHLIST id"}
                ]

                GIVEN MEDICATIONS:
                [{"id": "603e008918bc4fda8b6877ccaab63475", "medication_name": "OXYCODONE HCL (IR) 5 TABLET by mouth"}, {"id": "49e042d4ff11451cbba18415c0b416d8", "medication_name": "CYCLOBENZAPRIN 5 TABLET by mouth"}, {"id": "5f040609b3af4d3a99d59037d3f2c2b2", "medication_name": "ACETAMINOPHEN 500 TABLET by mouth"}]

                MATCH LIST:
                [{"id": "52959-0131-02", "NameDescription": "OXYCODONE HCL PO TABLET 5 MG", "GenericName": "oxyCODONE hydrochloride", "Route": "PO", "Strength": "5 MG", "StrengthUnitOfMeasure": null, "Dosage_Form": "TABLET", "Aliases": []}, {"id": "73780-0001-10", "NameDescription": "OXYCODONE HCL PO TABLET 5 MG", "GenericName": "oxyCODONE hydrochloride", "Route": "PO", "Strength": "5 MG", "StrengthUnitOfMeasure": null, "Dosage_Form": "TABLET", "Aliases": []}, {"id": "23635-0580-10", "NameDescription": "ROXICODONE PO TABLET 5 MG", "GenericName": "oxyCODONE hydrochloride", "Route": "PO", "Strength": "5 MG", "StrengthUnitOfMeasure": null, "Dosage_Form": "TABLET", "Aliases": []}, {"id": "76420-0136-30", "NameDescription": "OXYCODONE HCL-ACETAMINOPHEN PO TABLET 325 MG-5 MG", "GenericName": "Acetaminophen/oxyCODONE hydrochloride", "Route": "PO", "Strength": "325 MG-5 MG", "StrengthUnitOfMeasure": null, "Dosage_Form": "TABLET", "Aliases": []}, {"id": "81140-0101-10", "NameDescription": "ROXYBOND PO TABLET 5 MG", "GenericName": "oxyCODONE hydrochloride", "Route": "PO", "Strength": "5 MG", "StrengthUnitOfMeasure": null, "Dosage_Form": "TABLET", "Aliases": []}, {"id": "00591-3256-01", "NameDescription": "CYCLOBENZAPRINE HCL PO TABLET 5 MG", "GenericName": "Cyclobenzaprine Hydrochloride", "Route": "PO", "Strength": "5 MG", "StrengthUnitOfMeasure": null, "Dosage_Form": "TABLET", "Aliases": []}, {"id": "00378-0441-01", "NameDescription": "BENAZEPRIL HYDROCHLORIDE PO TABLET 5 MG", "GenericName": "Benazepril Hydrochloride", "Route": "PO", "Strength": "5 MG", "StrengthUnitOfMeasure": null, "Dosage_Form": "TABLET", "Aliases": []}, {"id": "23155-0749-01", "NameDescription": "BENAZEPRIL HYDROCHLORIDE PO TABLET 5 MG", "GenericName": "Benazepril Hydrochloride", "Route": "PO", "Strength": "5 MG", "StrengthUnitOfMeasure": null, "Dosage_Form": "TABLET", "Aliases": []}, {"id": "50268-0109-11", "NameDescription": "BENAZEPRIL HCL AVPAK PO TABLET 5 MG", "GenericName": "Benazepril Hydrochloride", "Route": "PO", "Strength": "5 MG", "StrengthUnitOfMeasure": null, "Dosage_Form": "TABLET", "Aliases": []}, {"id": "62559-0414-01", "NameDescription": "BENAZEPRIL HCL/HYDROCHLOROTHIAZIDE PO TABLET 5 MG-6.25 MG", "GenericName": "Benazepril Hydrochloride/hydroCHLOROthiazide", "Route": "PO", "Strength": "5 MG-6.25 MG", "StrengthUnitOfMeasure": null, "Dosage_Form": "TABLET", "Aliases": []}, {"id": "63629-1516-01", "NameDescription": "ACETAMINOPHEN PO TABLET 500 MG", "GenericName": "Acetaminophen", "Route": "PO", "Strength": "500 MG", "StrengthUnitOfMeasure": null, "Dosage_Form": "TABLET", "Aliases": []}, {"id": "70518-2805-00", "NameDescription": "ACETAMINOPHEN EXTRA STRENGTH PO TABLET 500 MG", "GenericName": "Acetaminophen", "Route": "PO", "Strength": "500 MG", "StrengthUnitOfMeasure": null, "Dosage_Form": "TABLET", "Aliases": []}, {"id": "50090-7252-01", "NameDescription": "ACETAMINOPHEN PO TABLET 500 MG", "GenericName": "Acetaminophen", "Route": "PO", "Strength": "500 MG", "StrengthUnitOfMeasure": null, "Dosage_Form": "TABLET", "Aliases": []}, {"id": "65155-0204-01", "NameDescription": "BENEHEALTH ACETAMINOPHEN PO TABLET 500 MG", "GenericName": "Acetaminophen", "Route": "PO", "Strength": "500 MG", "StrengthUnitOfMeasure": null, "Dosage_Form": "TABLET", "Aliases": []}, {"id": "00536-1292-29", "NameDescription": "ACETAMINOPHEN EXTRA STRENGTH PO TABLET 500 MG", "GenericName": "Acetaminophen", "Route": "PO", "Strength": "500 MG", "StrengthUnitOfMeasure": null, "Dosage_Form": "TABLET", "Aliases": []}]\n                ', 'medication_list': [{'id': '603e008918bc4fda8b6877ccaab63475', 'medication_name': 'OXYCODONE HCL (IR) 5 TABLET by mouth'}, {'id': '49e042d4ff11451cbba18415c0b416d8', 'medication_name': 'CYCLOBENZAPRIN 5 TABLET by mouth'}, {'id': '5f040609b3af4d3a99d59037d3f2c2b2', 'medication_name': 'ACETAMINOPHEN 500 TABLET by mouth'}], 'medispan_list': [{'id': '52959-0131-02', 'NameDescription': 'OXYCODONE HCL PO TABLET 5 MG', 'GenericName': 'oxyCODONE hydrochloride', 'Route': 'PO', 'Strength': '5 MG', 'StrengthUnitOfMeasure': None, 'Dosage_Form': 'TABLET', 'Aliases': []}, {'id': '73780-0001-10', 'NameDescription': 'OXYCODONE HCL PO TABLET 5 MG', 'GenericName': 'oxyCODONE hydrochloride', 'Route': 'PO', 'Strength': '5 MG', 'StrengthUnitOfMeasure': None, 'Dosage_Form': 'TABLET', 'Aliases': []}, {'id': '23635-0580-10', 'NameDescription': 'ROXICODONE PO TABLET 5 MG', 'GenericName': 'oxyCODONE hydrochloride', 'Route': 'PO', 'Strength': '5 MG', 'StrengthUnitOfMeasure': None, 'Dosage_Form': 'TABLET', 'Aliases': []}, {'id': '76420-0136-30', 'NameDescription': 'OXYCODONE HCL-ACETAMINOPHEN PO TABLET 325 MG-5 MG', 'GenericName': 'Acetaminophen/oxyCODONE hydrochloride', 'Route': 'PO', 'Strength': '325 MG-5 MG', 'StrengthUnitOfMeasure': None, 'Dosage_Form': 'TABLET', 'Aliases': []}, {'id': '81140-0101-10', 'NameDescription': 'ROXYBOND PO TABLET 5 MG', 'GenericName': 'oxyCODONE hydrochloride', 'Route': 'PO', 'Strength': '5 MG', 'StrengthUnitOfMeasure': None, 'Dosage_Form': 'TABLET', 'Aliases': []}, {'id': '00591-3256-01', 'NameDescription': 'CYCLOBENZAPRINE HCL PO TABLET 5 MG', 'GenericName': 'Cyclobenzaprine Hydrochloride', 'Route': 'PO', 'Strength': '5 MG', 'StrengthUnitOfMeasure': None, 'Dosage_Form': 'TABLET', 'Aliases': []}, {'id': '00378-0441-01', 'NameDescription': 'BENAZEPRIL HYDROCHLORIDE PO TABLET 5 MG', 'GenericName': 'Benazepril Hydrochloride', 'Route': 'PO', 'Strength': '5 MG', 'StrengthUnitOfMeasure': None, 'Dosage_Form': 'TABLET', 'Aliases': []}, {'id': '23155-0749-01', 'NameDescription': 'BENAZEPRIL HYDROCHLORIDE PO TABLET 5 MG', 'GenericName': 'Benazepril Hydrochloride', 'Route': 'PO', 'Strength': '5 MG', 'StrengthUnitOfMeasure': None, 'Dosage_Form': 'TABLET', 'Aliases': []}, {'id': '50268-0109-11', 'NameDescription': 'BENAZEPRIL HCL AVPAK PO TABLET 5 MG', 'GenericName': 'Benazepril Hydrochloride', 'Route': 'PO', 'Strength': '5 MG', 'StrengthUnitOfMeasure': None, 'Dosage_Form': 'TABLET', 'Aliases': []}, {'id': '62559-0414-01', 'NameDescription': 'BENAZEPRIL HCL/HYDROCHLOROTHIAZIDE PO TABLET 5 MG-6.25 MG', 'GenericName': 'Benazepril Hydrochloride/hydroCHLOROthiazide', 'Route': 'PO', 'Strength': '5 MG-6.25 MG', 'StrengthUnitOfMeasure': None, 'Dosage_Form': 'TABLET', 'Aliases': []}, {'id': '63629-1516-01', 'NameDescription': 'ACETAMINOPHEN PO TABLET 500 MG', 'GenericName': 'Acetaminophen', 'Route': 'PO', 'Strength': '500 MG', 'StrengthUnitOfMeasure': None, 'Dosage_Form': 'TABLET', 'Aliases': []}, {'id': '70518-2805-00', 'NameDescription': 'ACETAMINOPHEN EXTRA STRENGTH PO TABLET 500 MG', 'GenericName': 'Acetaminophen', 'Route': 'PO', 'Strength': '500 MG', 'StrengthUnitOfMeasure': None, 'Dosage_Form': 'TABLET', 'Aliases': []}, {'id': '50090-7252-01', 'NameDescription': 'ACETAMINOPHEN PO TABLET 500 MG', 'GenericName': 'Acetaminophen', 'Route': 'PO', 'Strength': '500 MG', 'StrengthUnitOfMeasure': None, 'Dosage_Form': 'TABLET', 'Aliases': []}, {'id': '65155-0204-01', 'NameDescription': 'BENEHEALTH ACETAMINOPHEN PO TABLET 500 MG', 'GenericName': 'Acetaminophen', 'Route': 'PO', 'Strength': '500 MG', 'StrengthUnitOfMeasure': None, 'Dosage_Form': 'TABLET', 'Aliases': []}, {'id': '00536-1292-29', 'NameDescription': 'ACETAMINOPHEN EXTRA STRENGTH PO TABLET 500 MG', 'GenericName': 'Acetaminophen', 'Route': 'PO', 'Strength': '500 MG', 'StrengthUnitOfMeasure': None, 'Dosage_Form': 'TABLET', 'Aliases': []}]
"""



PROMPT = PROMPT_2

MODEL_1 = "gemini-1.5-flash-002"
MODEL_2 = "gemini-2.5-flash-lite"

FILE_URI = "gs://viki-ai-provisional-dev/paperglass/documents/007/54321/cb54e6d2228a462f902b8c4e0764d812/eb3d10e06c9b11f0925f0242ac140004/1.pdf"

# Results storage
test_results = []

async def run_llm_test(prompt, model, file_uri):
    """
    Run a single LLM test with the given prompt, model, and file URI using direct Vertex AI calls.
    
    Returns:
        Dict containing test results with elapsed time, tokens, and output
    """
    LOGGER.info(f"Running test with model: {model}")
    LOGGER.info(f"File URI: {file_uri}")
    LOGGER.info(f"Prompt: {prompt}")
    
    # Initialize Vertex AI
    vertexai.init(project=GCP_PROJECT_ID, location=GCP_LOCATION_2)
    
    # Record start time
    start_time = time.time()
    
    try:
        # Create the generative model
        model_obj = GenerativeModel(model)
        
        # Create content parts: file + prompt
        file_part = Part.from_uri(file_uri, mime_type="application/pdf")
        text_part = Part.from_text(prompt)
        
        # Prepare content
        contents = [file_part, text_part]
        
        # Count tokens before generation
        token_count_request = model_obj.count_tokens(contents)
        input_tokens = token_count_request.total_tokens
        input_billable_chars = token_count_request.total_billable_characters
        
        LOGGER.info(f"Input tokens: {input_tokens}, Input billable characters: {input_billable_chars}")
        
        # Generate content
        response = await model_obj.generate_content_async(
            contents,
            generation_config={
                "max_output_tokens": 2048,
                "temperature": 0.1,
                "top_p": 0.95,
            }
        )
        
        # Record end time
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Extract response text
        output_text = response.text if response.text else ""
        
        # Get usage metadata if available
        usage_metadata = getattr(response, 'usage_metadata', None)
        output_tokens = 0
        total_tokens = 0
        
        if usage_metadata:
            output_tokens = getattr(usage_metadata, 'candidates_token_count', 0)
            total_tokens = getattr(usage_metadata, 'total_token_count', 0)
            LOGGER.info(f"Usage metadata - Output tokens: {output_tokens}, Total tokens: {total_tokens}")
        else:
            # Fallback estimation: 1 token ≈ 4 characters
            output_tokens = len(output_text) // 4
            total_tokens = input_tokens + output_tokens
        
        test_result = {
            "model": model,
            "elapsed_time_seconds": round(elapsed_time, 2),
            "input_tokens": input_tokens,
            "input_billable_characters": input_billable_chars,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "output_length_chars": len(output_text),
            "output": output_text,
            "success": True,
            "error": None
        }
        
        LOGGER.info(f"Test completed for {model}")
        LOGGER.info(f"Elapsed time: {elapsed_time:.2f} seconds")
        LOGGER.info(f"Output tokens: {output_tokens}")
        LOGGER.info(f"Total tokens: {total_tokens}")
        LOGGER.info(f"Output length: {len(output_text)} characters")
        
        return test_result
        
    except Exception as e:
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        error_result = {
            "model": model,
            "elapsed_time_seconds": round(elapsed_time, 2),
            "input_tokens": 0,
            "input_billable_characters": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "output_length_chars": 0,
            "output": "",
            "success": False,
            "error": str(e)
        }
        
        LOGGER.error(f"Test failed for {model}: {str(e)}")
        return error_result

async def run_comparison_test():
    """
    Run comparison tests between two LLM models.
    """
    LOGGER.info("Starting LLM model comparison test")
    LOGGER.info(f"Testing models: {MODEL_1} vs {MODEL_2}")
    LOGGER.info(f"File: {FILE_URI}")
    LOGGER.info("=" * 80)
    
    # Test Model 1
    LOGGER.info(f"\n🔬 Testing {MODEL_1}")
    result1 = await run_llm_test(PROMPT, MODEL_1, FILE_URI)
    test_results.append(result1)
    
    # Test Model 2
    LOGGER.info(f"\n🔬 Testing {MODEL_2}")
    result2 = await run_llm_test(PROMPT, MODEL_2, FILE_URI)
    test_results.append(result2)
    
    # Generate comparison report
    LOGGER.info("\n" + "=" * 80)
    LOGGER.info("📊 COMPARISON RESULTS")
    LOGGER.info("=" * 80)
    
    if result1["success"] and result2["success"]:
        time_diff = result2["elapsed_time_seconds"] - result1["elapsed_time_seconds"]
        token_diff = result2["total_tokens"] - result1["total_tokens"]
        output_token_diff = result2["output_tokens"] - result1["output_tokens"]
        
        LOGGER.info(f"\n⏱️  TIMING COMPARISON:")
        LOGGER.info(f"   {MODEL_1}: {result1['elapsed_time_seconds']}s")
        LOGGER.info(f"   {MODEL_2}: {result2['elapsed_time_seconds']}s")
        LOGGER.info(f"   Difference: {time_diff:+.2f}s ({MODEL_2} is {'faster' if time_diff < 0 else 'slower'})")
        
        LOGGER.info(f"\n📊 TOKEN COMPARISON:")
        LOGGER.info(f"   {MODEL_1}:")
        LOGGER.info(f"     - Input tokens: {result1['input_tokens']}")
        LOGGER.info(f"     - Output tokens: {result1['output_tokens']}")
        LOGGER.info(f"     - Total tokens: {result1['total_tokens']}")
        LOGGER.info(f"   {MODEL_2}:")
        LOGGER.info(f"     - Input tokens: {result2['input_tokens']}")
        LOGGER.info(f"     - Output tokens: {result2['output_tokens']}")
        LOGGER.info(f"     - Total tokens: {result2['total_tokens']}")
        LOGGER.info(f"   Differences:")
        LOGGER.info(f"     - Output tokens: {output_token_diff:+}")
        LOGGER.info(f"     - Total tokens: {token_diff:+}")
        
        LOGGER.info(f"\n💰 BILLING COMPARISON:")
        LOGGER.info(f"   {MODEL_1}: {result1['input_billable_characters']} billable characters")
        LOGGER.info(f"   {MODEL_2}: {result2['input_billable_characters']} billable characters")
        
        LOGGER.info(f"\n📄 OUTPUT LENGTH COMPARISON:")
        LOGGER.info(f"   {MODEL_1}: {result1['output_length_chars']} characters")
        LOGGER.info(f"   {MODEL_2}: {result2['output_length_chars']} characters")
        
        # Show first 300 characters of each output for quick comparison
        LOGGER.info(f"\n📝 OUTPUT PREVIEW:")
        LOGGER.info(f"   {MODEL_1}:")
        LOGGER.info(f"   {result1['output'][:300]}...")
        LOGGER.info(f"\n   {MODEL_2}:")
        LOGGER.info(f"   {result2['output'][:300]}...")
        
        # Performance winner
        faster_model = MODEL_1 if time_diff > 0 else MODEL_2
        more_tokens_model = MODEL_1 if token_diff < 0 else MODEL_2
        
        LOGGER.info(f"\n🏆 SUMMARY:")
        LOGGER.info(f"   ⚡ Faster model: {faster_model}")
        LOGGER.info(f"   📊 More detailed output: {more_tokens_model}")
        
    else:
        LOGGER.error("⚠️  One or both tests failed. Check individual results above.")
        if not result1["success"]:
            LOGGER.error(f"   {MODEL_1} error: {result1['error']}")
        if not result2["success"]:
            LOGGER.error(f"   {MODEL_2} error: {result2['error']}")
    
    # Save detailed results to file
    timestamp = int(time.time())
    results_file = f"prompt_test_results_{timestamp}.json"
    
    try:
        with open(results_file, 'w') as f:
            json.dump({
                "test_config": {
                    "prompt": PROMPT,
                    "models": [MODEL_1, MODEL_2],
                    "file_uri": FILE_URI,
                    "timestamp": datetime.utcnow().isoformat(),
                    "project_id": GCP_PROJECT_ID,
                    "location": GCP_LOCATION_2
                },
                "results": test_results
            }, f, indent=2)
        
        LOGGER.info(f"\n💾 Detailed results saved to: {results_file}")
    except Exception as e:
        LOGGER.error(f"Failed to save results file: {e}")

async def run():    
    """Main execution function"""
    await run_comparison_test()

def main():    
    """Entry point"""
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        LOGGER.info("Test interrupted by user")
    except Exception as e:
        LOGGER.error(f"Test failed: {e}")

if __name__ == "__main__":   
    main()