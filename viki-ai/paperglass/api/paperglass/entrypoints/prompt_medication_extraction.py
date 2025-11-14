import asyncio
import sys, os
from typing import List
import json
import csv
import tenacity

from kink import inject

from vertexai.preview.generative_models import GenerativeModel, HarmCategory, HarmBlockThreshold, Part

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from paperglass.domain.time import now_utc

from paperglass.infrastructure.ports import IMedispanPort, IRelevancyFilterPort, IPromptAdapter
from paperglass.interface.ports import  ICommandHandlingPort
from paperglass.domain.models import MedispanDrug
from paperglass.usecases.commands import ExtractMedication

test_case_list = [
    {
        "filename": "test6",
        "doc_id": "ad71b2a4a6bf11ef81f242004e494300",
        "path": "gs://viki-ai-provisional-dev/paperglass/documents/007/54321/38f6b655f82f4a18b512f5cd6dbfa018/ad71b2a4a6bf11ef81f242004e494300/document.pdf",
    },
    {
        "filename": "test5",
        "doc_id": "ea89bc9aa75a11efbfac42004e494300",
        "path": "gs://viki-ai-provisional-dev/paperglass/documents/007/54321/38f6b655f82f4a18b512f5cd6dbfa018/ea89bc9aa75a11efbfac42004e494300/document.pdf",
    },
    {
        "filename": "test4",
        "doc_id": "a460f1d4a6bf11ef81f242004e494300",
        "path": "gs://viki-ai-provisional-dev/paperglass/documents/007/54321/38f6b655f82f4a18b512f5cd6dbfa018/a460f1d4a6bf11ef81f242004e494300/document.pdf",
    },
    {
        "filename": "test3",
        "doc_id": "a1207256a6bf11ef81f242004e494300",
        "path": "gs://viki-ai-provisional-dev/paperglass/documents/007/54321/38f6b655f82f4a18b512f5cd6dbfa018/a1207256a6bf11ef81f242004e494300/document.pdf",
    },
    {
        "filename": "test2",
        "doc_id": "9e1e80e8a6bf11ef81f242004e494300",
        "path": "gs://viki-ai-provisional-dev/paperglass/documents/007/54321/38f6b655f82f4a18b512f5cd6dbfa018/9e1e80e8a6bf11ef81f242004e494300/document.pdf",
        "expected": "id='59660' NameDescription='MiraLax Oral Powder 17 GM/SCOOP' GenericName='Polyethylene Glycol 3350' Route='Oral' Strength='17' StrengthUnitOfMeasure='GM/SCOOP' Dosage_Form='Powder'",
    },
    {
        "filename": "test1",
        "doc_id": "9a51bb88a6bf11ef81f242004e494300",
        "path": "gs://viki-ai-provisional-dev/paperglass/documents/007/54321/38f6b655f82f4a18b512f5cd6dbfa018/9a51bb88a6bf11ef81f242004e494300/document.pdf",
    },
]

# Define the CSV file path
csv_file_path = 'medication_results_final_final.csv'

# Define the headers for the CSV file
csv_headers = ['run', 'prompt', 'response', 'search_term', 'medispan_result', 'matched_item', 'result']


medispan_prompt = '''For the GIVEN MEDICATION, can you find the best med match from the MATCH LIST given below. Please follow these instructions:
                        1) The name of medication should be present in the "content" field of the MATCH LIST entries. Otherwise say no name match
                        2) If the GIVEN MEDICATION has medication strength specified, select from the list only if there is exact match of the Strength                        
                        3) If the GIVEN MEDICATION has medication form specified, select from the list only if there is exact match of the Dosage_Form                        
                        4) If the GIVEN MEDICATION has medication route specified, select from the list only if there is exact match of the Route                       
                        5) Otherwise, return "{}" and specific what attributes were not found Only return the best match from the list. 
                        If no match is found, return "{}"Only return the best match from the list. If no match is found, return "{}" 
                        GIVEN MEDICATION:{SEARCH_TERM} MATCH LIST:'''

prompt_Medication_extraction = {
    "gemini-1.5-flash-002": '''
[Page Text]:
Please study the conttentin this file below:
{context}

[Task]:

Please extract medications as array of JSON with keys as name, strength, dosage, route, form, discontinued_date, frequency,start_date, end_date, instructions,explanation, document_reference and page_number.
Please do not include any markup other than JSON.
Please format start_date and end_date as mm/dd/yyyy.
'''
}


prompt_Medication_extraction_2 = {
    "gemini-1.5-flash-002": '''
[Page Text]:
For the given document
[Task]:

Please extract medications as array of JSON with keys as name, strength, dosage, form, dosage_form, route , discontinued_date, frequency,start_date, end_date, instructions,explanation, document_reference and page_number.
Please do not include any markup other than JSON.
Please format start_date and end_date as mm/dd/yyyy.
'''
}

prompt_Medication_extraction_3 = {
    "gemini-1.5-flash-002": '''
[Page Text]:
For the given document
[Task]:

Please extract medications as array of JSON with keys as name, strength, dosage, form, dosage_form, route , discontinued_date, frequency,start_date, end_date, instructions,explanation, document_reference and page_number.
Please do not include any markup other than JSON.
Please format start_date and end_date as mm/dd/yyyy.
**Distinguish between dosage and strength field. Dosage field does not have Unit of Measurement(Mg, %). If Dosage has attached measurement unit, keep dossage blank**
'''
}


prompt_Medication_extraction_4 = {
    "gemini-1.5-flash-002": '''
[Page Text]:
For the given document
[Task]:

Please extract medications as array of JSON with keys as name, strength, dosage, form, route , discontinued_date, frequency,start_date, end_date, instructions,explanation, document_reference and page_number.
Please do not include any markup other than JSON.
Please format start_date and end_date as mm/dd/yyyy.
**The 'name' field should include punctuation if present but exclude strength and unit of measurement (e.g., 'Aspirin 81mg' should be 'Aspirin', and 'hydrocodone 5 mg-acetaminophen' should be 'hydrocodone-acetaminophen')**
**Distinguish between dosage (eg. 1 tab, 2-3 tablets) and strength of medication. 
Dosage field does not have Unit of Measurement(MG, ML, GM, % , UT, ACT, UNIT), if it has considered as Strength, leave dosage blank**
'''
}


prompt_Medication_extraction_5 = {
    "gemini-1.5-flash-002": '''
        "instruction": "Extract medications from the provided document as a JSON array. Each object in the array must contain the following keys: name, strength, dosage, form, route, discontinued_date, frequency, start_date, end_date, instructions, explanation, document_reference, and page_number. Dates (start_date, end_date, discontinued_date) should be formatted as MM/DD/YYYY.  The 'name' field should include punctuation if present but exclude strength and unit of measurement (e.g., 'Aspirin 81mg' should be 'Aspirin', and 'hydrocodone 5 mg-acetaminophen' should be 'hydrocodone-acetaminophen').  Distinguish between 'dosage' (numeric value without units) and 'strength' (value with unit).  Output only the JSON array; no other text or markup."
        '''
}


prompt_Medication_extraction_6 = {
    "gemini-1.5-flash-002": '''
[Page Text]:
For the given document
[Task]:

Please extract medications as array of JSON with keys as name, strength, dosage, form, route , discontinued_date, frequency,start_date, end_date, instructions,explanation, document_reference and page_number.
Please do not include any markup other than JSON.
Please format start_date and end_date as mm/dd/yyyy.
**The 'name' field should include alias , punctuation if present but exclude strength and unit of measurement (e.g., 'Aspirin 81mg' should be 'Aspirin', and 'hydrocodone 5 mg-acetaminophen' should be 'hydrocodone-acetaminophen')**
**Distinguish between dosage (eg. 1 tab, 2-3 tablets) and strength of medication. 
Dosage field does not have Unit of Measurement(MG, ML, GM, % , UT, ACT, UNIT), if it has considered as Strength, leave dosage blank**
'''
}

prompt_Medication_extraction_final = {
    "gemini-1.5-flash-002": '''
     Please study this document:
     [Task]:
     please extract medications as array of JSON with keys as name, strength, dosage, route, form, discontinued_date, frequency, start_date, end_date, instructions,explanation, document_reference and page_number.
     Please do not include any markup other than JSON.
     Please format start_date and end_date as mm/dd/yyyy.
     **The 'name' field should include alias , punctuation if present but exclude strength and unit of measurement (e.g., 'Aspirin 81mg' should be 'Aspirin', and 'hydrocodone 5 mg-acetaminophen' should be 'hydrocodone-acetaminophen')**
    **Distinguish between dosage (eg. 1 tab, 2-3 tablets) and strength of medication.
    Dosage field does not have Unit of Measurement(MG, ML, GM, % , UT, ACT, UNIT), if it has considered as Strength, leave dosage blank**
    '''
}

# prompt_Medication_extraction_final = {
#     "gemini-1.5-flash-002": '''
#      Please study this context:<content></content> please extract medications as array of JSON with keys as name(include alias), strength, dosage, route, form, discontinued_date, frequency, start_date, end_date, instructions,explanation, document_reference and page_number.
# 	 Please use include alias , punctuation in 'name' field if present but exclude strength and unit of measurement (e.g., 'Aspirin 81mg' should be 'Aspirin', and 'hydrocodone 5 mg-acetaminophen' should be 'hydrocodone-acetaminophen')
# 	 Please distinguish between dosage (eg. 1 tab, 2-3 tablets) and strength of medication. Dosage field does not have Unit of Measurement(MG, ML, GM, % , UT, ACT, UNIT), if it has considered as Strength, leave dosage blank.
#      Please do not include any markup other than JSON.
#      Please format start_date and end_date as mm/dd/yyyy.

#     '''
# }


def write_to_csv(run, prompt, response, search_term, medispan_result, matched_item, result):
    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([run, prompt, response, search_term, medispan_result, matched_item, result])


retry_strategy = tenacity.Retrying(
    wait=tenacity.wait_fixed(2),
    stop=tenacity.stop_after_attempt(5),
    retry=tenacity.retry_if_exception_type(Exception),
)


def generate_content_with_retry(model, contents):
    return retry_strategy(model.generate_content, contents)


def get_response(filepart, messages):
    """
    Obtain responses from a specified model

    Args:
        messages (list of dict): List of messages structured for API input.
        model_name (str): Identifier for the model to query.
        temperature (float): Controls randomness of response, where 0 is deterministic.
        max_tokens (int): Limit on the number of tokens in the response.

    Returns:
        str: The content of the response message from the model.
    """
    MODEL = "gemini-1.5-flash-002"
    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0,
        "top_p": 0.95,
    }
    # system_message = "You are healthcare expert assistant which identifies medical information from documents. Please provide the required information."
    model = GenerativeModel(
        MODEL,
        safety_settings={HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH},
        generation_config=generation_config,
    )
    contents = [filepart, messages]
    response = generate_content_with_retry(model, contents)
    return response.text.strip()


def construct_prompt_template(context, model_name):
    template = prompt_Medication_extraction_final[model_name]
    return template.format(context=context)


@inject()
async def orchestrate_prompt_tests(prompt_adapter: IPromptAdapter, command_handler: ICommandHandlingPort):
    for test_case in test_case_list:
        # if test_case:
        if test_case['filename'] == "test5":
            path = test_case['path']
            # file_part = Part.from_uri(uri=path, mime_type="application/pdf")
            # prompt_template = construct_prompt_template(file_part, "gemini-1.5-flash-002")
            # response = get_response(file_part, prompt_template)
            prompts = [
                (path, "application/pdf"),
                prompt_Medication_extraction_final["gemini-1.5-flash-002"],
            ]
            response = await prompt_adapter.multi_modal_predict_2(prompts, model="gemini-1.5-flash-002", metadata=None)
            command = ExtractMedication(app_id="007", tenant_id="54321",patient_id="38f6b655f82f4a18b512f5cd6dbfa018", document_id="ea89bc9aa75a11efbfac42004e494300", document_operation_instance_id="ec2db1f0a75a11ef9bfd42004e494300", document_operation_definition_id= "4d3f0b2aa2c811ef9e0b3e3297f4bd07" ,model= "gemini-1.5-flash-002", prompt=prompt_Medication_extraction_final["gemini-1.5-flash-002"], page_id ="edb13d9ea75a11efbfac42004e494300", page_number=1, labelled_content=["medications"])
            Extracted_Medication =await command_handler.handle_command(command)
            print(Extracted_Medication)
            print(response[7:-3].strip())
            breakpoint()
            search_term = ""
            try:
                response_json = json.loads(response[7:-3])
                for item in response_json:
                    search_term = f"{item['name']} {item['route']} {item['strength']} {item['form']}"
                    medispan_list, matched_item, result = await medispan_match_test(search_term)
                    write_to_csv(
                        f'run_{now_utc()}',
                        prompt_Medication_extraction_final["gemini-1.5-flash-002"],
                        item,
                        search_term,
                        medispan_list,
                        matched_item,
                        result,
                    )
                    print(result)
            except json.JSONDecodeError as e:
                print(f"Failed to decode JSON: {e}")


@inject()
async def medispan_match_test(
    search_term, medispan_port: IMedispanPort, relevancy_filter_adapter: IRelevancyFilterPort
):
    medispan_port_result: List[MedispanDrug] = await medispan_port.search_medications(search_term)
    medispan_results_tuple = None
    try:
        medispan_results_tuple = await relevancy_filter_adapter.re_rank(
            search_term,
            medispan_port_result,
            model="gemini-1.5-flash-002",
            prompt=medispan_prompt,
            enable_llm=True,
            metadata=None,
        )
    except:
        if medispan_results_tuple is None:
            print("Warning: No valid medispan results found.")
            return None, None, None
    medispan_port_result_final, context = medispan_results_tuple
    return medispan_port_result, medispan_port_result_final, context


def main():
    if not os.path.exists(csv_file_path):
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(csv_headers)
    asyncio.run(orchestrate_prompt_tests())


if __name__ == "__main__":
    main()
