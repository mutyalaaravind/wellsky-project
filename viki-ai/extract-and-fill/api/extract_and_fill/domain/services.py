from copy import deepcopy
import json, os
from typing import Any, Iterator, Tuple

from json5.tokenizer import tokenize

from extract_and_fill.domain.models import PromptChunk

from copy import deepcopy
import os, json
import aiofiles
from extract_and_fill.infrastructure.ports import IPromptPort

Path = Tuple[str]


class PromptChunkGenerator:
    def make_chunks(
        self,
        transcript_id: str,
        transcript_text: str,
        schema: dict,
        model: str,
        transcript_version: int,
        max_size: int = 512,
    ) -> Iterator[PromptChunk]:
        """
        Split schema into chunks (including required "_meta" definitions) that are under max_size.
        """
        # final_max_size = max_size - len(transcript_text) - 166

        index = 0
        under_limit = True
        chunk = {}
        included_paths = []
        for path in self._iter_paths(schema):
            # Set value & meta in chunk
            updated_chunk = self._set_value(chunk, path, None)
            try:
                field_meta = self._get_value(schema, path[:-1] + ('_meta',) + path[-1:])
                if field_meta is not None:
                    updated_chunk = self._set_value(updated_chunk, path[:-1] + ('_meta',) + path[-1:], field_meta)
            except:
                # Field has no meta associated with it
                # print(f"Field has no meta associated with it {updated_chunk}")
                pass

            if len(json.dumps(updated_chunk)) > max_size:
                # all models have bigger input token limit
                # if not chunk:
                #     # Single value is too large, we cannot proceed
                #     raise ValueError(f'Value (and its meta) at {path} is too large to fit in a single chunk')
                yield PromptChunk.create(
                    index,
                    transcript_id,
                    transcript_text,
                    ['//'.join(path) for path in included_paths],
                    updated_chunk,
                    model,
                    transcript_version,
                )
                index += 1
                chunk = {}
                included_paths = []
            else:
                # Max size not reached yet, continue
                chunk = updated_chunk
                included_paths.append(path)

        # Yield last chunk if not empty
        if chunk:
            yield PromptChunk.create(
                index,
                transcript_id,
                transcript_text,
                ['//'.join(path) for path in included_paths],
                chunk,
                model,
                transcript_version,
            )

    def merge_chunks(self, chunks: Iterator[PromptChunk]) -> dict:
        result = {}
        for chunk in chunks:
            if chunk.result is None:
                raise ValueError(f'Chunk {chunk.id} has no result')
            result = self._merge(result, chunk.result)
        return result

    def _merge(self, left, right):
        """
        Merge two dictionaries recursively.
        Return a copy without modifying the originals.
        """
        new = dict(left)
        for key, value in right.items():
            if key in new:
                if isinstance(value, dict):
                    new[key] = self._merge(new[key], value)
                else:
                    new[key] = value
            else:
                new[key] = value
        return new

    def _iter_paths(self, root: dict) -> Iterator[Path]:
        """
        Walk over dictionary recursively
        """
        for key, value in root.items():
            if key == '_meta':
                continue
            if isinstance(value, dict):
                for path in self._iter_paths(value):
                    yield (key,) + path
            else:
                yield key,

    def _get_value(self, doc: dict, path: Path):
        """
        Get deep value from doc.
        """
        element = doc
        for key in path:
            element = element[key]
        return element

    def _set_value(self, doc: dict, path: Path, value) -> dict:
        """
        Set deep value in doc, deep-copy affected parts of doc to prevent modifying the original.
        """
        new = dict(doc)
        element = new
        for key in path[:-1]:
            if key not in element:
                element[key] = {}
            else:
                element[key] = dict(element[key])
            element = element[key]
        element[path[-1]] = value
        return new


class JSONHealer:
    def is_invalid(self, s: str) -> bool:
        balance = 0
        for token in tokenize(s):
            if token.type == 'LBRACE':
                balance += 1
            elif token.type == 'RBRACE':
                balance -= 1
        return balance != 0

    def heal(self, s: str) -> str:
        result = []
        balance = 0
        for token in tokenize(s):
            if token.type == 'LBRACE':
                balance += 1
            elif token.type == 'RBRACE':
                balance -= 1
            if token.type == 'WHITESPACE':
                # Strip whitespaces
                continue
            result.append(token.value)
        while balance > 0:
            result.append('}')
            balance -= 1
        while balance < 0:
            result.pop()
            balance += 1
        return ''.join(result)


# uses 2 step extraction process
# 1. verbatim source extraction
# 2. answers extraction
class PromptTemplateWithVerbatimSourceExtractionManager:

    def __init__(self, section_id, program="oasis_e") -> None:
        self.section_id = section_id
        self.program = program

    async def get_verbatim_source_extraction_prompt_template(
        self, verbatim_prompt_template_file_name="verbatim_source_extraction.txt"
    ):
        import aiofiles

        script_dir = f"{os.path.dirname(__file__)}/../config/programs/{self.program}"
        verbatim_source_prompt_template_path = os.path.join(
            script_dir, f"prompt_templates/{verbatim_prompt_template_file_name}"
        )
        async with aiofiles.open(verbatim_source_prompt_template_path) as prompt_file_reader:
            verbatim_source_prompt_template = await prompt_file_reader.read()
        return verbatim_source_prompt_template

    async def get_verbatim_source_extraction_prompt_text(
        self, transcript, questions, verbatim_source_prompt_template=None, example_template=None
    ):
        if not verbatim_source_prompt_template:
            verbatim_source_prompt_template = await self.get_verbatim_source_extraction_prompt_template()
        if not example_template:
            example_template = await self.get_examples(self.section_id, "verbatim")
        prompt_template = verbatim_source_prompt_template.replace("<transcript></transcript>", transcript).replace(
            "<questions></questions>", str(questions)
        )
        prompt_template = prompt_template.replace("<example></example>", example_template)
        return prompt_template

    async def get_examples(self, section_id, example_type):
        import aiofiles

        script_dir = f"{os.path.dirname(__file__)}/../config/programs/{self.program}/examples"
        examples = ""
        example = ""
        if os.path.isfile(f"{script_dir}/{section_id}.txt"):
            async with aiofiles.open(f"{script_dir}/{section_id}.txt") as section_examples_file_reader:
                examples = await section_examples_file_reader.read()
                import re

                example = re.findall(f"<{example_type}>(.*?)</{example_type}>", examples, re.DOTALL)
                if example:
                    example = example[0]
        return example

    async def get_questionnaires(self, section_id):
        import aiofiles

        script_dir = f"{os.path.dirname(__file__)}/../config/programs/{self.program}"
        list_of_files = {}
        relevant_codes = {}

        async with aiofiles.open(f"{script_dir}/sections.json") as section_file_reader:
            relevant_codes = json.loads((await section_file_reader.read())).get(section_id, {}).get("codes")

        if not relevant_codes:
            return None

        for dirpath, dirnames, filenames in os.walk(script_dir):
            for filename in filenames:
                if filename.split(".json")[0] in relevant_codes:
                    list_of_files[filename] = os.sep.join([dirpath, filename])

        questionnaire = {}

        for files in list_of_files:
            async with aiofiles.open(list_of_files[files]) as questionnaire_file_reader:
                questionnaire.update(json.loads(await questionnaire_file_reader.read()))

        return questionnaire

    async def get_answers_extraction_prompt_template(self, answers_prompt_template_file_name="answers_extraction.txt"):
        import aiofiles

        script_dir = f"{os.path.dirname(__file__)}/../config/programs/{self.program}"
        answers_generation_prompt_template_path = os.path.join(
            script_dir, f"prompt_templates/{answers_prompt_template_file_name}"
        )
        async with aiofiles.open(answers_generation_prompt_template_path) as answers_generation_prompt_file_reader:
            answer_prompt_template = await answers_generation_prompt_file_reader.read()
        return answer_prompt_template

    async def get_answers_extraction_prompt_text(self, questions, answers_prompt_template=None, example_template=None):
        if not answers_prompt_template:
            answers_prompt_template = await self.get_answers_extraction_prompt_template()
        if not example_template:
            example_template = await self.get_examples(self.section_id, "answers")
        answers_prompt_template = answers_prompt_template.replace("<questions></questions>", str(questions))
        answers_prompt_template = answers_prompt_template.replace("<example></example>", example_template)
        return answers_prompt_template

    async def merge_verbatim_source_and_questions(self, verbatim_source, questionnaires):
        questions_with_verbatim_source = deepcopy(questionnaires)
        for key, value in questions_with_verbatim_source.items():
            if type(verbatim_source.get(key, {})) == dict:
                questions_with_verbatim_source[key]["verbatim_source"] = verbatim_source.get(key, {}).get(
                    "verbatim_source", ""
                )
        return questions_with_verbatim_source

    async def merge_verbatim_source_and_answers(self, verbatim_source, answers):
        answers_with_verbatim_source = {}
        for key, value in answers.items():
            answers_with_verbatim_source[key] = {}
            answers_with_verbatim_source[key]["value"] = answers.get(key)
            answers_with_verbatim_source[key]["verbatim_source"] = verbatim_source.get(key, {}).get(
                "verbatim_source", ""
            )
        return answers_with_verbatim_source

    def merge_results_with_form_schema(self, results, form_schema):
        if form_schema:
            for key, value in form_schema.items():
                if key in results.keys():
                    form_schema[key] = results[key]
                else:
                    if type(value) == dict:
                        form_schema[key] = self.merge_results_with_form_schema(results, value)
        return form_schema

    # ToDo: need to refactor this in a better model based approach
    def results_with_hierarchy(self, results, form_schema, hierarchy_results={}):
        if form_schema:
            if type(form_schema) == dict:
                key = form_schema.get("localQuestionCode")
                if form_schema.get("items"):
                    for item in form_schema.get("items"):
                        if not hierarchy_results.get(key):
                            hierarchy_results[key] = {}
                            # hierarchy_results[key] = []
                        hierarchy_results[key].update(self.results_with_hierarchy(results, item, {}))
                else:
                    if not hierarchy_results.get(key):
                        hierarchy_results[key] = {}
                    hierarchy_results[key] = results.get(key)
        return hierarchy_results

    # one big abstraction to get final result
    async def get_answers_extracted(self, section, transcript, model, execute_prompt):
        verbatim_source_result = None
        answers_result = None
        try:
            questionnaires = await self.get_questionnaires(section)

            if not questionnaires:
                return {}

            # miracle 1
            verbatim_source_result = await execute_prompt(
                await self.get_verbatim_source_extraction_prompt_text(transcript, questionnaires), model
            )
            # print(await self.get_verbatim_source_extraction_prompt_text(transcript, questionnaires))
            # print(verbatim_source_result)
            # print("=====================================")
            verbatim_source_result = json.loads(verbatim_source_result)

            verbatim_merged_questionnaires = await self.merge_verbatim_source_and_questions(
                verbatim_source_result, questionnaires
            )

            # print(await self.get_answers_extraction_prompt_text(verbatim_merged_questionnaires))
            # print("=====================================")
            # miracle 2
            answers_result = await execute_prompt(
                await self.get_answers_extraction_prompt_text(verbatim_merged_questionnaires), model
            )
            print(answers_result)
            answers_result = json.loads(answers_result)

            return await self.merge_verbatim_source_and_answers(verbatim_source_result, answers_result)
        except Exception as e:
            return {
                "error": str(e),
                "verbatim_source": {str(verbatim_source_result) if verbatim_source_result else None},
                "answers": {str(answers_result) if answers_result else None},
            }


class PromptTemplateWithSingleStepExtractionManager(PromptTemplateWithVerbatimSourceExtractionManager):

    def __init__(self, section_id, program="oasis_e") -> None:
        super().__init__(section_id, program)

    async def get_answers_extraction_prompt_template(
        self, answers_prompt_template_file_name="single_step_answers_extraction.txt"
    ):
        import aiofiles

        script_dir = f"{os.path.dirname(__file__)}/../config/programs/{self.program}"
        answers_generation_prompt_template_path = os.path.join(
            script_dir, f"prompt_templates/{answers_prompt_template_file_name}"
        )
        async with aiofiles.open(answers_generation_prompt_template_path) as answers_generation_prompt_file_reader:
            answer_prompt_template = await answers_generation_prompt_file_reader.read()
        return answer_prompt_template

    async def get_answers_extraction_prompt_text(
        self, transcript, questions, answers_prompt_template=None, example_template=None
    ):
        if not answers_prompt_template:
            answers_prompt_template = await self.get_answers_extraction_prompt_template()
        if not example_template:
            example_template = await self.get_examples(self.section_id, "answers")
        answers_prompt_template = answers_prompt_template.replace("<questions></questions>", str(questions))
        answers_prompt_template = answers_prompt_template.replace("<example></example>", example_template)
        answers_prompt_template = answers_prompt_template.replace("<transcript></transcript>", transcript)
        return answers_prompt_template

    # one big abstraction to get final result
    async def get_answers_extracted(self, section, transcript, model, execute_prompt):
        verbatim_source_result = None
        answers_result = None
        try:
            questionnaires = await self.get_questionnaires(section)

            if not questionnaires:
                return {}

            questionnaire_batch = {}
            chunk_count = 0
            index = 0

            for key, value in questionnaires.items():
                # chunk at every 10 or multiple of 10th question
                if chunk_count % 30 == 0:
                    index = index + 1

                if not questionnaire_batch.get(index):
                    questionnaire_batch[index] = []

                questionnaire_batch[index].append({"key": key, "value": value})
                chunk_count = chunk_count + 1

            final_result = {}
            for key, values in questionnaire_batch.items():
                # for each chunk of questions (values) we run prompt and merge results
                answers_prompt_text = await self.get_answers_extraction_prompt_text(transcript, values)

                answers_result = await execute_prompt(answers_prompt_text, model)
                if answers_result:
                    final_result.update(json.loads(answers_result).get("result"))

            return final_result
        except Exception as e:
            return {"error": str(e), "answers": {str(answers_result) if answers_result else None}}
