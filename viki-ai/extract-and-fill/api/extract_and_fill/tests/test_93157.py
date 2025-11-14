
import os

from extract_and_fill.usecases.prompt_manager import get_verbatim_source_extraction_prompt_text

#ToDo: add setup and teardown methods

def test_get_verbatim_source_extraction_prompt_text():
    prompt_template = None
    script_dir = os.path.dirname(__file__)
    rel_path = "../config/programs/oasis_e/93157.json"
    abs_file_path = os.path.join(script_dir, rel_path)
    
    with open(abs_file_path) as prompt_file:
        prompt_template = prompt_file.read()
    
    questions= {
        "93157-6-1-1":{"question":"is your visibility within normal limits?","instructions":"if visibility is within normal limits, select true as the value otherwise false"},
        "93157-6-1-2":{"question":"Do you have to use glasses?","instructions":"if require glasses, select true as the value"},
        "93157-6-1-3":{"question":"do you use contacts for left eye?","instructions":"if require contacts for left eye, select true as the value"},
    }
    
    transcript= """
            do you use glasses?
            yes i do use glasses
            can you read without glasses?
            i cannot
            do you use any additional contacts?
            no
            """
        
    prompt_template_applied = get_verbatim_source_extraction_prompt_text(questions, transcript, prompt_template)
    
    assert prompt_template_applied is not None
    