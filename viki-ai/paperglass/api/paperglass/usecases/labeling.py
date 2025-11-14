import re
from textwrap import dedent
from typing import Dict, List, Tuple

from jinja2 import Environment
import yaml


class LabelingTemplate:
    def __init__(self, prefix, postfix):
        self.prefix = prefix
        self.postfix = postfix

    def render(self, **kwargs):
        env = Environment()
        return (
            env.from_string(self.prefix).render(**kwargs),
            env.from_string(self.postfix).render(**kwargs),
        )

    def parse_response(self, text) -> List[Tuple[str, str]]:
        raise NotImplementedError


class SingleLabeling(LabelingTemplate):
    def __init__(self):
        super().__init__(
            dedent(
                """
                Your are a medical expert. Your job is to extract text from medical documents. Please take a look at this page:
                """
            ).strip(),
            dedent(
                """
                You must extract all text from the page and label each section with one of the following labels:
                {% for label in labels %}
                - {{ label }}
                {%- endfor %}

                Example response:

                ```
                # demographics
                (All text that is related to demographics)

                # medications
                (All text that is related to medications)

                # procedures
                (All text that is related to procedures)

                # medications
                (More text that is related to medications, located elsewhere on the page)
                ```

                RULES:
                1. Each label MUST be preceded by a '#' symbol.
                2. Text MUST be extracted from the page exactly as it appears.
                3. Use ONLY labels that were provided above: do NOT make up new labels.
                4. If a section CANNOT be labeled with any of the provided labels, do NOT include it in the response.

                """
            ).strip(),
        )

    def render(self, labels: List[str]):
        return super().render(labels=labels)

    def parse_response(self, text) -> Dict[str, str]:
        text = text.strip('`')
        result = {}
        current_label = None
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            if line.startswith('#'):
                # New label encountered
                current_label = line.strip(' #').strip('* ')
                if current_label not in result:
                    result[current_label] = ''
            elif current_label is not None:
                result[current_label] += line + '\n'
        return result


# class MultiLabeling(LabelingTemplate):
#     def __init__(self):
#         super().__init__(
#             dedent(
#                 """
#                 Your are a medical expert. Your job is to categorize this page using labels and sublabels. Please take a look at this page:
#                 """
#             ).strip(),
#             dedent(
#                 """
#                 What are the main topics that are mentioned on this page? Here are possible labels and sublabels:
#
#                 {% for label in labels %}
#                 - {{ label[0] }}
#                 {%- for sublabel in label[1] %}
#                   - {{ sublabel }}
#                 {%- endfor %}
#                 {% endfor %}
#
#                 RULES:
#                 1. Use only labels and sublabels that were provided above: do not make up new labels or sublabels.
#                 2. Please reply in the following format, and only include labels and sublabels that are relevant to the page:
#                 - label1:
#                   - sublabel11: [comma-separated keywords from page that reason why this label was chosen (up to 5)]
#                   - sublabel19: [comma-separated keywords from page that reason why this label was chosen (up to 5)]
#                 - label4:
#                   - sublabel43: [comma-separated keywords from page that reason why this label was chosen (up to 5)]
#                   - sublabel47: [comma-separated keywords from page that reason why this label was chosen (up to 5)]
#                 3. If a label has no sublabels, do not include it in the response.
#                 4. If a label has sublabels, but none of them are relevant, do not include the label in the response.
#                 5. Do not include any special characters in the response besides dots, commas, colons, dashes, and spaces.
#                 6. Always include exactly one whitespace after colon.
#                 7. The reasons list must include terms that look like field or section names from the provided document, not just keywords.
#
#                 Example:
#                 - {{ labels[0][0] }}:
#                   - {{ labels[0][1][0] }}: ...
#                   - {{ labels[0][1][1] }}: ...
#                 - {{ labels[2][0] }}:
#                   - {{ labels[2][1][0] }}: ...
#                   - {{ labels[2][1][1] }}: ...
#                 """
#             ).strip(),
#         )
#
#     def render(self, labels: List[Tuple[str, List[str]]]):
#         return super().render(labels=labels)
#
#     def parse_response(self, text) -> List[Tuple[str, str]]:
#         labels = []
#         current_label = 'unknown'
#         interesting_lines = [line for line in text.split('\n') if re.match(r'^\s*-', line)]
#         for line in interesting_lines:
#             left, _, right = line.partition(":")
#             is_sublabel = left.startswith(' ')
#             left = left.strip(' -')
#             right = right.strip(' -')
#             if is_sublabel:
#                 labels.append((f'{current_label}:{left}', right))
#             else:
#                 current_label = left
#                 labels.append((left, right))
#         return labels
#
#
# if __name__ == "__main__":
#     # labeling = SingleLabeling()
#     # print('\n'.join(labeling.render(["label1", "label2"])))
#     #
#     # labeling = MultiLabeling()
#     # print(
#     #     '\n'.join(
#     #         labeling.render(
#     #             [
#     #                 ("label1", ["sublabel11", "sublabel12"]),
#     #                 ("label2", ["sublabel21", "sublabel22"]),
#     #                 ("label3", ["sublabel31", "sublabel32"]),
#     #             ]
#     #         )
#     #     )
#     # )
#
#     labeling = MultiLabeling()
#     labels = labeling.parse_response(
#         '''
# - **patient_administration**:
#   - **Patient**:  Patient's Medicare No., Patient's Name and Address, Patient's Date of Birth, Patient's Gender
#   - **Practitioner**: Physician's Name & Address
#   - **Organization**:  Provider's Name, Address and Telephone Number, HOME HEALTH AGENCY
#   - **Encounter**:  SOC Date, Certification Period, Medical Record No.
# - **orders_and_observations**:
#   - **Condition**: ORTHOSTATIC HYPOTENSION, SEVERE SEPSIS WITH SEPTIC SHOCK, ACUTE EMBOLISM AND THOMBOS UNSP DEEP VEINS OF LOW EXTRM, BI
#   - **Observation**: Vitals signs monitoring (TEMP, PULSE, RESP, SYSTOLICBP, DIASTOLICBP, PAIN, O2SAT)
#   - **ServiceRequest**: PHYSICAL THERAPY, OCCUPATIONAL THERAPY
# - **patient_care**:
#   - **CarePlan**: Home Health Certification and Plan of Care,  Patient's Expressed Goals,  Frequency/Duration of Visits, Orders of Discipline and Treatments, Goals/Rehabilitation Potential/Discharge Plans
#   - **Goal**:  TO GET STRONGER AND IMPROVE ENDURANCE,  improve awareness of fall risk factors,  improve functional strength and power, improve gait and ambulation, improve static and dynamic, functional balance
#  - **Procedure**:   SIT TO STAND TRANSFERS,  TUG, STANDARDIZED BALANCE TEST
# - **clinical_decision_support**:
#   - **PlanDefinition**: PHYSICAL THERAPY PLAN OF CARE
#   - **RiskAssessment**:  FALL RISK,  RISK OF HOSPITALIZATION
# '''
#     )
#     print(labels)
