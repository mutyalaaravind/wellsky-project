#!/usr/bin/env python3

from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
import json
import re
import sys
from typing import Annotated, Any, List, Literal, Optional

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field
from pydantic.alias_generators import to_camel
import requests
import rich


class Model(BaseModel):
    """
    Base model with support for camelCase fields.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        frozen=True,
        # populate_by_name=True,
        # from_attribute=True,
    )


class SourceFormUnit(Model):
    name: str
    code: Optional[str]  # Present in 99131-5, but null in 48802-3
    system: Optional[str]  # Present in 99131-5, but null in 48802-3
    default: bool


class SourceFormAnswer(Model):
    label: Optional[str]
    code: Optional[str]
    text: Optional[str]
    other: Any  # ?


def value_or_empty_list(value):
    return value or []


class SourceFormStem(Model):
    """
    Fields that occur in both `SourceForm` and `SourceFormItem`.
    """

    # Known data types implied from form 99131-5CNE.
    # ST - "String", i. e. free text
    # REAL - "Real number", i. e. numeric
    # CNE - "Coded with no exceptions", i. e. one from "answers"
    data_type: Literal["ST", "REAL", "CNE"]

    header: bool  # True if this field is a header
    units: Annotated[
        List[SourceFormUnit], BeforeValidator(value_or_empty_list)
    ]  # Pattern for value - may be used to imply a more specific data type, e. g. date/time
    coding_instructions: Optional[str]
    copyright_notice: Optional[str]
    items: Annotated[
        List["SourceFormItem"], BeforeValidator(value_or_empty_list)
    ] = Field(default_factory=list)


class SourceForm(SourceFormStem):
    """
    Source form root element.
    """

    type: Literal["LOINC"]
    code: str
    name: str


class SourceFormItem(SourceFormStem):
    """
    Source form item.
    """

    question_code: str
    local_question_code: Optional[
        str
    ]  # Some internal identifier, not sure what does it reference
    question: str
    answers: Annotated[
        List[SourceFormAnswer], BeforeValidator(value_or_empty_list)
    ]  # ?
    skip_logic: Any  # ?
    restrictions: Any  # ?
    default_answer: Any  # ?
    formatting: Any  # ?
    calculation_method: Any  # ?


def transform(source_item: SourceFormItem, depth: int = 0) -> dict:
    """
    Transform source form into preform format.
    """
    el = {}
    if source_item.header:
        # This is header that has child items
        if depth == 0:
            # Treat as a section
            el = {
                "fieldType": "Section",
                "displayName": source_item.question,
                "fieldName": "",
                "fields": [],
            }
        else:
            # Treat as a field group
            el = {
                "fieldType": "FieldGroup",
                "displayName": source_item.question,
                "fieldName": "",
                "fields": [],
            }
        el["fields"] = [transform(child, depth + 1) for child in source_item.items]
    else:
        # This is a field
        el = {
            "fieldType": "TextBox"
            if source_item.data_type in ("ST", "CNE")
            else "INPUT_NUMBER",
            "displayName": source_item.question,
            "fieldName": source_item.question_code,
        }

    return el


def print_as_text(source_item: SourceFormItem, depth: int = 0):
    print("  " * depth, source_item.question)

    for child in source_item.items:
        print_as_text(child, depth + 1)


def main(form_code, output_type):
    # Set user agent
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
    }
    response = requests.get(
        "https://forms.loinc.org/" + form_code + "/", headers=headers
    )
    response.raise_for_status()

    source_form = SourceForm.model_validate_json(
        re.findall(
            r"window.formDef(\s*)=(\s*)\n([^\n]+)\n;",
            response.content.decode("utf-8"),
            re.M,
        )[0][2]
    )
    if output_type == "model":
        rich.print(source_form)
    elif output_type == "text":
        for item in source_form.items:
            print_as_text(item)
    else:
        root_fields = [transform(source_item) for source_item in source_form.items]
        print(json.dumps(root_fields, indent=2))


class Parser(ArgumentParser):
    def error(self, message):
        sys.stderr.write(f"error: {message}\n")
        self.print_help()
        sys.exit(2)


if __name__ == "__main__":
    parser = Parser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description="Fetch & convert LOINC form into preform format",
    )
    parser.add_argument(
        "form_code", help="LOINC form code (try these: 99131-5, 48802-3, 54089-8)"
    )
    parser.add_argument(
        "-t",
        "--output-type",
        choices=["model", "text", "preform"],
        default="preform",
        help="Output type",
    )
    args = parser.parse_args()
    main(args.form_code, args.output_type)