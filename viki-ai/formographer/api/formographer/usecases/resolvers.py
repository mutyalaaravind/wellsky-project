from base64 import b64decode
from typing import Any, List, TypedDict
from json import dumps, loads


from graphql import GraphQLResolveInfo
from kink import inject
from formographer.infrastructure.ports import IQNAPort

from formographer.settings import VERSION
from formographer.log import getLogger
from formographer.usecases.types import CompleteFormResult, FormField, FormValue


def get_version(obj: Any, info: GraphQLResolveInfo):
    return VERSION


LOGGER = getLogger(__name__)


@inject
async def complete_form(
    obj: Any,
    info: GraphQLResolveInfo,
    text: str,
    form_fields: List[FormField],
    qna: IQNAPort,
) -> CompleteFormResult:
    LOGGER.debug('complete_form: building AI model...')
    model = await qna.build_model(text)

    responses = []

    schema = {'type': 'object', 'properties': {}}

    for index, field in enumerate(form_fields):
        schema['properties'][field.name] = {
            'type': 'string',
            'description': field.question,
        }
    query = f'Generate JSON for schema:\n\n{dumps(schema, indent=4)}'
    LOGGER.debug('complete_form: query = %s', query)
    response = await model.query(query)
    LOGGER.debug('complete_form: response = %s', response)
    data = loads(response)
    form_values = []
    for key, value in data.items():
        form_values.append(FormValue(name=key, value=value))
        LOGGER.debug('complete_form: asking question %d/%d: "%s"', index + 1, len(form_fields), field.question)

    # form_values = []
    # for index, field in enumerate(form_fields):
    #     LOGGER.debug('complete_form: asking question %d/%d: "%s"', index + 1, len(form_fields), field.question)
    #     answer = await model.query(field.question)
    #     LOGGER.debug('complete_form: answer: "%s"', answer)
    #     form_values.append(FormValue(name=field.name, value=answer))

    return CompleteFormResult(
        error=None,
        form_values=form_values,
    )
    pass

@inject
async def extract(content: str, extract_adapter:ExtractPort):
    print(content)
    if not extract_adapter:
        from formographer.formographer.infrastructure.adapters.extract import Extract
        extract_adapter = Extract()
    output = extract_adapter.get_medical_record(content)
    print(output)
    return output
    