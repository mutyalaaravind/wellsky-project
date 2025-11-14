# if you run into module not found error. In shell do following:
# export PYTHONPATH=$PYTHONPATH:yourprojectpath/eai-ai/extract-and-fill/api

import asyncio
import json
import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from extract_and_fill.domain.services import (
    PromptTemplateWithVerbatimSourceExtractionManager,
    PromptTemplateWithSingleStepExtractionManager,
)
from extract_and_fill.usecases.prompt_manager import execute_prompt


async def test_extraction():
    section_type = "T"
    transcript = ""
    model = "medlm-medium"
    # model = "text-bison-32k@002"
    if not transcript:
        with open(
            f"{os.path.dirname(__file__)}/../config/programs/oasis_e/transcripts/{section_type}.txt"
        ) as transcript_file_reader:
            transcript = transcript_file_reader.read()

    result = await PromptTemplateWithSingleStepExtractionManager(section_id=section_type).get_answers_extracted(
        section_type, transcript, model, execute_prompt
    )

    with open(f"{os.path.dirname(__file__)}/../config/programs/oasis_e/expected_answers.json") as expected_answer_file:
        expected_answers = json.load(expected_answer_file)

    if result:
        final_result = {}
        for key, value in result.items():
            final_result[key] = value.get("value")
        print(final_result)

    # if result:
    #     for key, value in result.items():
    #         assert key in expected_answers
    #         assert value is not None
    #         print("-------------------")
    #         print(value.get("value"))
    #         print(expected_answers.get(key).get("value"))
    #         print(value.get("verbatim_source"))
    #         print(expected_answers.get(key).get("verbatim_source"))
    #         assert value.get("value") == expected_answers.get(key).get("value")
    #         assert value.get("verbatim_source") == expected_answers.get(key).get("verbatim_source")


async def test_get_questionnaires():
    section_type = "T"
    result = await PromptTemplateWithVerbatimSourceExtractionManager(section_type).get_questionnaires(section_type)
    print(result)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_extraction())
    print("=====================================")
    # loop.run_until_complete(
    #      test_get_questionnaires()
    #    )
