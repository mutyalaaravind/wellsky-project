export const form = {
  "lformsVersion": "29.0.0",
  "PATH_DELIMITER": "/",
  "code": "99131-5",
  "codeList": [
    {
      "code": "99131-5",
      "display": "Outcome and assessment information set (OASIS) form - version E - Start of Care [CMS Assessment]",
      "system": "http://loinc.org"
    }
  ],
  "identifier": null,
  "codeSystem": "http://loinc.org",
  "name": "Outcome and assessment information set (OASIS) form - version E - Start of Care [CMS Assessment]",
  "type": "LOINC",
  "template": "table",
  "copyrightNotice": null,
  "items": [
    {
      "questionCode": "99132-3",
      "localQuestionCode": "A",
      "dataType": "SECTION",
      "header": true,
      "units": null,
      "codingInstructions": null,
      "copyrightNotice": null,
      "question": "Administrative Information",
      "answers": null,
      "skipLogic": null,
      "restrictions": null,
      "defaultAnswer": null,
      "formatting": null,
      "calculationMethod": null,
      "items": [
        {
          "questionCode": "68468-8",
          "localQuestionCode": "M0018",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "National Provider Identifier (NPI) for the attending physician who has signed the plan of care",
          "answers": [
            {
              "label": null,
              "code": null,
              "text": null,
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99132-3/68468-8",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "68468-8",
              "display": "National Provider Identifier (NPI) for the attending physician who has signed the plan of care",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "69417-4",
          "localQuestionCode": "M0010",
          "dataType": "ST",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "CMS Certification Number",
          "answers": null,
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99132-3/69417-4",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "69417-4",
              "display": "CMS Certification Number",
              "system": "http://loinc.org"
            }
          ],
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "46494-1",
          "localQuestionCode": "M0014",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": "The state where the agency branch office is located.",
          "copyrightNotice": null,
          "question": "Branch State",
          "answers": [
            {
              "label": null,
              "code": null,
              "text": null,
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99132-3/46494-1",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "46494-1",
              "display": "Branch State",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "46495-8",
          "localQuestionCode": "M0016",
          "dataType": "ST",
          "header": false,
          "units": null,
          "codingInstructions": "Specifies the branch identification code, as assigned by CMS. The identifier consists of 10 digits with the State code as the first two digits, followed by Q (upper case), followed by the last four digits of the current Medicare provider number, and ending with the three-digit CMS-assigned branch number.",
          "copyrightNotice": null,
          "question": "Branch ID Number",
          "answers": null,
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99132-3/46495-8",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "46495-8",
              "display": "Branch ID Number",
              "system": "http://loinc.org"
            }
          ],
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "46496-6",
          "localQuestionCode": "M0020",
          "dataType": "ST",
          "header": false,
          "units": null,
          "codingInstructions": "Agency-specific patient identifier. This is the identification code the agency assigns to the patient and uses for record keeping purposes for this episode of care.",
          "copyrightNotice": null,
          "question": "Patient ID Number",
          "answers": null,
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99132-3/46496-6",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "46496-6",
              "display": "Patient ID Number",
              "system": "http://loinc.org"
            }
          ],
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "54503-8",
          "localQuestionCode": "M0040",
          "dataType": "SECTION",
          "header": true,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Patient Name",
          "answers": null,
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": [
            {
              "questionCode": "45392-8",
              "localQuestionCode": "M0040",
              "dataType": "ST",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "(First)",
              "answers": null,
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/99132-3/54503-8/45392-8",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "45392-8",
                  "display": "(First)",
                  "system": "http://loinc.org"
                }
              ],
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "45393-6",
              "localQuestionCode": "M0040",
              "dataType": "ST",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "(MI)",
              "answers": null,
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/99132-3/54503-8/45393-6",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "45393-6",
                  "display": "(MI)",
                  "system": "http://loinc.org"
                }
              ],
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "45394-4",
              "localQuestionCode": "M0040",
              "dataType": "ST",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "(Last)",
              "answers": null,
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/99132-3/54503-8/45394-4",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "45394-4",
                  "display": "(Last)",
                  "system": "http://loinc.org"
                }
              ],
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "45395-1",
              "localQuestionCode": "M0040",
              "dataType": "ST",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "(Suffix)",
              "answers": null,
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/99132-3/54503-8/45395-1",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "45395-1",
                  "display": "(Suffix)",
                  "system": "http://loinc.org"
                }
              ],
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            }
          ],
          "linkId": "/99132-3/54503-8",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "54503-8",
              "display": "Patient Name",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": { "questionLayout": "vertical" },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "46499-0",
          "localQuestionCode": "M0050",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": "The state in which the patient is currently residing while receiving care.",
          "copyrightNotice": null,
          "question": "Patient State of Residence",
          "answers": [
            {
              "label": null,
              "code": null,
              "text": null,
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99132-3/46499-0",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "46499-0",
              "display": "Patient State of Residence",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "45401-7",
          "localQuestionCode": "M0060",
          "dataType": "ST",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Patient ZIP Code",
          "answers": null,
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99132-3/45401-7",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "45401-7",
              "display": "Patient ZIP Code",
              "system": "http://loinc.org"
            }
          ],
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "45396-9",
          "localQuestionCode": "M0064",
          "dataType": "ST",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Social Security Number",
          "answers": null,
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99132-3/45396-9",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "45396-9",
              "display": "Social Security Number",
              "system": "http://loinc.org"
            }
          ],
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "45397-7",
          "localQuestionCode": "M0063",
          "dataType": "ST",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Medicare Number",
          "answers": null,
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99132-3/45397-7",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "45397-7",
              "display": "Medicare Number",
              "system": "http://loinc.org"
            }
          ],
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "45400-9",
          "localQuestionCode": "M0065",
          "dataType": "ST",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Medicaid Number",
          "answers": null,
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99132-3/45400-9",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "45400-9",
              "display": "Medicaid Number",
              "system": "http://loinc.org"
            }
          ],
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "46098-0",
          "localQuestionCode": "M0069",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Gender",
          "answers": [
            {
              "label": "1",
              "code": "LA2-8",
              "text": "Male",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA3-6",
              "text": "Female",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99132-3/46098-0",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "46098-0",
              "display": "Gender",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "21112-8",
          "localQuestionCode": "M0066",
          "dataType": "REAL",
          "header": false,
          "units": [
            {
              "name": "{mm/dd/yyyy}",
              "code": "{mm/dd/yyyy}",
              "system": "http://unitsofmeasure.org",
              "default": false
            }
          ],
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Birth Date",
          "answers": null,
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99132-3/21112-8",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "21112-8",
              "display": "Birth Date",
              "system": "http://loinc.org"
            }
          ],
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" },
          "unit": {
            "name": "{mm/dd/yyyy}",
            "code": "{mm/dd/yyyy}",
            "system": "http://unitsofmeasure.org",
            "default": false
          }
        },
        {
          "questionCode": "69854-8",
          "localQuestionCode": "A1005",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": "This term is used for reporting ethnicity based on, but not limited in use to, the Department of Health and Human Services, Affordable Care Act Section 4302.",
          "copyrightNotice": null,
          "question": "Ethnicity: Are you of Hispanic, Latino/a, or Spanish origin?",
          "answers": [
            {
              "label": "A",
              "code": "LA30254-9",
              "text": "No, not of Hispanic, Latino/a, or Spanish origin",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "B",
              "code": "LA30255-6",
              "text": "Yes, Mexican, Mexican American, Chicano/a",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "C",
              "code": "LA18369-1",
              "text": "Yes, Puerto Rican",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "D",
              "code": "LA18370-9",
              "text": "Yes, Cuban",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "E",
              "code": "LA30256-4",
              "text": "Yes, another Hispanic, Latino, or Spanish origin",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "X",
              "code": "LA30257-2",
              "text": "Patient unable to respond",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99132-3/69854-8",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "69854-8",
              "display": "Ethnicity: Are you of Hispanic, Latino/a, or Spanish origin?",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "69855-5",
          "localQuestionCode": "A1010",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": "This term is used for reporting race based on the Department of Health and Human Services, Affordable Care Act Section 4302.",
          "copyrightNotice": null,
          "question": "Race: What is your race?",
          "answers": [
            {
              "label": "A",
              "code": "LA4457-3",
              "text": "White",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "B",
              "code": "LA10610-6",
              "text": "Black or African American",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "C",
              "code": "LA6155-1",
              "text": "American Indian or Alaska Native",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "D",
              "code": "LA14048-5",
              "text": "Asian Indian",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "E",
              "code": "LA4168-6",
              "text": "Chinese",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "F",
              "code": "LA3969-8",
              "text": "Filipino",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "G",
              "code": "LA4595-0",
              "text": "Japanese",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "H",
              "code": "LA4603-2",
              "text": "Korean",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "I",
              "code": "LA4443-3",
              "text": "Vietnamese",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "J",
              "code": "LA14049-3",
              "text": "Other Asian",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "K",
              "code": "LA14045-1",
              "text": "Native Hawaiian",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "L",
              "code": "LA18375-8",
              "text": "Guamanian or Chamorro",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "M",
              "code": "LA4300-5",
              "text": "Samoan",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "N",
              "code": "LA14047-7",
              "text": "Other Pacific Islander",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "X",
              "code": "LA30257-2",
              "text": "Patient unable to respond",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99132-3/69855-5",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "69855-5",
              "display": "Race: What is your race?",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "57199-2",
          "localQuestionCode": "M0150",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Current Payment Sources for Home Care",
          "answers": [
            {
              "label": "0",
              "code": "LA12090-9",
              "text": "None; no charge for current services",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA6259-1",
              "text": "Medicare (traditional fee-for-service)",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA12092-5",
              "text": "Medicare (HMO/managed care/Advantage plan)",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA6257-5",
              "text": "Medicaid (traditional fee-for-service)",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "4",
              "code": "LA6256-7",
              "text": "Medicaid (HMO/managed care)",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "5",
              "code": "LA6452-2",
              "text": "Workers' compensation",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "6",
              "code": "LA27774-1",
              "text": "Title programs (for example, Title III, V, or XX)",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "7",
              "code": "LA27775-8",
              "text": "Other government (for example, Tricare, VA)",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "8",
              "code": "LA6350-8",
              "text": "Private insurance",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "9",
              "code": "LA6349-0",
              "text": "Private HMO/managed care",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "10",
              "code": "LA6369-8",
              "text": "Self-pay",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "11",
              "code": "LA6310-2",
              "text": "Other (specify)",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "UK",
              "code": "LA4489-6",
              "text": "Unknown",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99132-3/57199-2",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "57199-2",
              "display": "Current Payment Sources for Home Care",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "93186-5",
          "localQuestionCode": "A1110",
          "dataType": "SECTION",
          "header": true,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Language",
          "answers": null,
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": [
            {
              "questionCode": "54899-0",
              "localQuestionCode": "A1110A",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "What is your preferred language?",
              "answers": [
                {
                  "label": null,
                  "code": "LA43-5",
                  "text": "English",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": null,
                  "code": "LA44-3",
                  "text": "Spanish",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": null,
                  "code": "LA4168-6",
                  "text": "Chinese",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": null,
                  "code": "LA4443-3",
                  "text": "Vietnamese",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": null,
                  "code": "LA15353-8",
                  "text": "Tagalog",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": null,
                  "code": "LA46-8",
                  "text": "Other",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/99132-3/93186-5/54899-0",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "54899-0",
                  "display": "What is your preferred language?",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "54588-9",
              "localQuestionCode": "A1110B",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": "Patient/resident's need or want an interpreter to communicate with a doctor or health care staff",
              "copyrightNotice": null,
              "question": "Do you need or want an interpreter to communicate with a doctor or health care staff?",
              "answers": [
                {
                  "label": "0",
                  "code": "LA32-8",
                  "text": "No",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "1",
                  "code": "LA33-6",
                  "text": "Yes",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "9",
                  "code": "LA11137-9",
                  "text": "Unable to determine",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/99132-3/93186-5/54588-9",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "54588-9",
                  "display": "Do you need or want an interpreter to communicate with a doctor or health care staff?",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            }
          ],
          "linkId": "/99132-3/93186-5",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "93186-5",
              "display": "Language",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": { "questionLayout": "vertical" },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "46497-4",
          "localQuestionCode": "M0030",
          "dataType": "REAL",
          "header": false,
          "units": [
            {
              "name": "{mm/dd/yyyy}",
              "code": "{mm/dd/yyyy}",
              "system": "http://unitsofmeasure.org",
              "default": false
            }
          ],
          "codingInstructions": "The date that care begins. When the first reimbursable service is delivered, this is the start of care.",
          "copyrightNotice": null,
          "question": "Start of Care Date",
          "answers": null,
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99132-3/46497-4",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "46497-4",
              "display": "Start of Care Date",
              "system": "http://loinc.org"
            }
          ],
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" },
          "unit": {
            "name": "{mm/dd/yyyy}",
            "code": "{mm/dd/yyyy}",
            "system": "http://unitsofmeasure.org",
            "default": false
          }
        },
        {
          "questionCode": "46500-5",
          "localQuestionCode": "M0080",
          "hostFieldId": "M0080_ASSESSOR_DISCIPLINE",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": "Identifies the discipline of the clinician completing the comprehensive assessment at the specified time points or the clinician reporting the transfer to an inpatient facility, death at home, or discharge (no further visits after start of care).",
          "copyrightNotice": null,
          "question": "Discipline of Person Completing Assessment",
          "answers": [
            {
              "label": "1",
              "code": "LA6367-2",
              "text": "RN",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA6353-2",
              "text": "PT",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA6378-9",
              "text": "SLP/ST",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "4",
              "code": "LA6309-4",
              "text": "OT",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99132-3/46500-5",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "46500-5",
              "display": "Discipline of Person Completing Assessment",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "46501-3",
          "localQuestionCode": "M0090",
          "dataType": "REAL",
          "header": false,
          "units": [
            {
              "name": "{mm/dd/yyyy}",
              "code": "{mm/dd/yyyy}",
              "system": "http://unitsofmeasure.org",
              "default": false
            }
          ],
          "codingInstructions": "The actual date the assessment is completed, except if agency policy allows assessments to be performed over more than one visit date, in which case the last date (when the assessment is finished) is the appropriate date to record.",
          "copyrightNotice": null,
          "question": "Date Assessment Completed",
          "answers": null,
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99132-3/46501-3",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "46501-3",
              "display": "Date Assessment Completed",
              "system": "http://loinc.org"
            }
          ],
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" },
          "unit": {
            "name": "{mm/dd/yyyy}",
            "code": "{mm/dd/yyyy}",
            "system": "http://unitsofmeasure.org",
            "default": false
          }
        },
        {
          "questionCode": "57200-8",
          "localQuestionCode": "M0100",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "This Assessment is Currently Being Completed for the Following Reason",
          "answers": [
            {
              "label": "1",
              "code": "LA6390-4",
              "text": "Start of care - further visits planned",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA6366-4",
              "text": "Resumption of care (after inpatient stay)",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "4",
              "code": "LA6355-7",
              "text": "Recertification (follow-up) reassessment",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "5",
              "code": "LA6312-8",
              "text": "Other follow-up",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "6",
              "code": "LA6402-7",
              "text": "Transferred to an inpatient facility - patient not discharged from agency",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "7",
              "code": "LA6401-9",
              "text": "Transferred to an inpatient facility - patient discharged from agency",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "8",
              "code": "LA6179-1",
              "text": "Death at home",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "9",
              "code": "LA6184-1",
              "text": "Discharge from agency",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99132-3/57200-8",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "57200-8",
              "display": "This Assessment is Currently Being Completed for the Following Reason",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "57201-6",
          "localQuestionCode": "M0102",
          "hostFieldId":"M0102_PHYSN_ORDRD_SOCROC_DT|spWritefrmDateOasis|0|isOasis",
          "dataType": "REAL",
          "header": false,
          "units": [
            {
              "name": "{mm/dd/yyyy}",
              "code": "{mm/dd/yyyy}",
              "system": "http://unitsofmeasure.org",
              "default": false
            }
          ],
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Date of Physician-ordered Start of Care (Resumption of Care)",
          "answers": null,
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99132-3/57201-6",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "57201-6",
              "display": "Date of Physician-ordered Start of Care (Resumption of Care)",
              "system": "http://loinc.org"
            }
          ],
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" },
          "unit": {
            "name": "{mm/dd/yyyy}",
            "code": "{mm/dd/yyyy}",
            "system": "http://unitsofmeasure.org",
            "default": false
          }
        },
        {
          "questionCode": "57202-4",
          "localQuestionCode": "M0104",
          "dataType": "REAL",
          "header": false,
          "units": [
            {
              "name": "{mm/dd/yyyy}",
              "code": "{mm/dd/yyyy}",
              "system": "http://unitsofmeasure.org",
              "default": false
            }
          ],
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Date of Referral",
          "answers": null,
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99132-3/57202-4",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "57202-4",
              "display": "Date of Referral",
              "system": "http://loinc.org"
            }
          ],
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" },
          "unit": {
            "name": "{mm/dd/yyyy}",
            "code": "{mm/dd/yyyy}",
            "system": "http://unitsofmeasure.org",
            "default": false
          }
        },
        {
          "questionCode": "57203-2",
          "localQuestionCode": "M0110",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Episode Timing: Is the Medicare home health payment episode for which this assessment will define a case mix group an \"early\" episode or a \"later\" episode in the patient's current sequence of adjacent Medicare home health payment episodes?",
          "answers": [
            {
              "label": "1",
              "code": "LA12111-3",
              "text": "Early",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA12112-1",
              "text": "Later",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "UK",
              "code": "LA4489-6",
              "text": "Unknown",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "NA",
              "code": "LA12114-7",
              "text": "Not Applicable: No Medicare case mix group to be defined by this assessment.",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99132-3/57203-2",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "57203-2",
              "display": "Episode Timing: Is the Medicare home health payment episode for which this assessment will define a case mix group an \"early\" episode or a \"later\" episode in the patient's current sequence of adjacent Medicare home health payment episodes?",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "101351-5",
          "localQuestionCode": "A1250",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Transportation. Has lack of transportation kept you from medical appointments, meetings, work, or from getting things needed for daily living?",
          "answers": [
            {
              "label": "A",
              "code": "LA30133-5",
              "text": "Yes, it has kept me from medical appointments or from getting my medications",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "B",
              "code": "LA30134-3",
              "text": "Yes, it has kept me from non-medical meetings, appointments, work, or from getting things that I need",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "C",
              "code": "LA32-8",
              "text": "No",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "X",
              "code": "LA30435-4",
              "text": "Resident unable to respond",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "Y",
              "code": "LA33608-3",
              "text": "Resident declines to respond",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99132-3/101351-5",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "101351-5",
              "display": "Transportation. Has lack of transportation kept you from medical appointments, meetings, work, or from getting things needed for daily living?",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "57204-0",
          "localQuestionCode": "M1000",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "From which of the following Inpatient Facilities was the patient discharged within the past 14 days?",
          "answers": [
            {
              "label": "1",
              "code": "LA12115-4",
              "text": "Long-term nursing facility (NF)",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA10080-2",
              "text": "Skilled nursing facility (SNF/TCU)",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA10078-6",
              "text": "Short-stay acute hospital (IPPS)",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "4",
              "code": "LA10000-0",
              "text": "Long-Term Care Hospital (LTCH)",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "5",
              "code": "LA9986-6",
              "text": "Inpatient rehabilitation hospital or unit (IRF)",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "6",
              "code": "LA10065-3",
              "text": "Psychiatric hospital or unit",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "7",
              "code": "LA6310-2",
              "text": "Other (specify)",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "NA",
              "code": "LA6342-5",
              "text": "Patient was not discharged from an inpatient facility",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99132-3/57204-0",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "57204-0",
              "display": "From which of the following Inpatient Facilities was the patient discharged within the past 14 days?",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "86470-2",
          "localQuestionCode": "M1005",
          "dataType": "REAL",
          "header": false,
          "units": [
            {
              "name": "{mm/dd/yyyy}",
              "code": "{mm/dd/yyyy}",
              "system": "http://unitsofmeasure.org",
              "default": false
            }
          ],
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Inpatient Discharge Date (most recent)",
          "answers": null,
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99132-3/86470-2",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "86470-2",
              "display": "Inpatient Discharge Date (most recent)",
              "system": "http://loinc.org"
            }
          ],
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" },
          "unit": {
            "name": "{mm/dd/yyyy}",
            "code": "{mm/dd/yyyy}",
            "system": "http://unitsofmeasure.org",
            "default": false
          }
        }
      ],
      "linkId": "/99132-3",
      "questionCodeSystem": "http://loinc.org",
      "codeList": [
        {
          "code": "99132-3",
          "display": "Administrative Information",
          "system": "http://loinc.org"
        }
      ],
      "displayControl": { "questionLayout": "vertical" },
      "questionCardinality": { "min": "1", "max": "1" },
      "answerCardinality": { "min": "0", "max": "1" }
    },
    {
      "questionCode": "99138-0",
      "localQuestionCode": "B",
      "dataType": "SECTION",
      "header": true,
      "units": null,
      "codingInstructions": null,
      "copyrightNotice": null,
      "question": "Hearing, Speech, and Vision",
      "answers": null,
      "skipLogic": null,
      "restrictions": null,
      "defaultAnswer": null,
      "formatting": null,
      "calculationMethod": null,
      "items": [
        {
          "questionCode": "95744-9",
          "localQuestionCode": "B0200",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Hearing. Ability to hear (with hearing aid or hearing appliances if normally used)",
          "answers": [
            {
              "label": "0",
              "code": "LA10941-5",
              "text": "Adequate - no difficulty in normal conversation, social interaction, listening to TV",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA10942-3",
              "text": "Minimal difficulty - difficulty in some environments (e.g. when person speaks softly or setting is noisy)",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA10943-1",
              "text": "Moderate difficulty - speaker has to increase volume and speak distinctly",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA10944-9",
              "text": "Highly impaired - absence of useful hearing",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99138-0/95744-9",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "95744-9",
              "display": "Hearing. Ability to hear (with hearing aid or hearing appliances if normally used)",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "95745-6",
          "localQuestionCode": "B1000",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Vision. Ability to see in adequate light (with glasses or other visual appliances)",
          "answers": [
            {
              "label": "0",
              "code": "LA10956-3",
              "text": "Adequate - sees fine detail, such as regular print in newspapers/books",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA10957-1",
              "text": "Impaired - sees large print, but not regular print in newspapers/books",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA10958-9",
              "text": "Moderately impaired - limited vision; not able to see newspaper headlines but can identify objects",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA10959-7",
              "text": "Highly impaired - object identification in question, but eyes appear to follow objects",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "4",
              "code": "LA10960-5",
              "text": "Severely impaired - no vision or sees only light, colors or shapes; eyes do not appear to follow objects",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99138-0/95745-6",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "95745-6",
              "display": "Vision. Ability to see in adequate light (with glasses or other visual appliances)",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "93157-6",
          "localQuestionCode": "B1300",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": "© 2006 Morris et al. Used with permission",
          "question": "Health Literacy: How often do you need to have someone help you when you read instructions, pamphlets, or other written material from your doctor or pharmacy?",
          "answers": [
            {
              "label": "0",
              "code": "LA6270-8",
              "text": "Never",
              "score": 0,
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA10066-1",
              "text": "Rarely",
              "score": 1,
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA10082-8",
              "text": "Sometimes",
              "score": 2,
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA10044-8",
              "text": "Often",
              "score": 3,
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "4",
              "code": "LA9933-8",
              "text": "Always",
              "score": 4,
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99138-0/93157-6",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "93157-6",
              "display": "Health Literacy: How often do you need to have someone help you when you read instructions, pamphlets, or other written material from your doctor or pharmacy?",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        }
      ],
      "linkId": "/99138-0",
      "questionCodeSystem": "http://loinc.org",
      "codeList": [
        {
          "code": "99138-0",
          "display": "Hearing, Speech, and Vision",
          "system": "http://loinc.org"
        }
      ],
      "displayControl": { "questionLayout": "vertical" },
      "questionCardinality": { "min": "1", "max": "1" },
      "answerCardinality": { "min": "0", "max": "1" }
    },
    {
      "questionCode": "99140-6",
      "localQuestionCode": "C",
      "dataType": "SECTION",
      "header": true,
      "units": null,
      "codingInstructions": null,
      "copyrightNotice": null,
      "question": "Cognitive Patterns",
      "answers": null,
      "skipLogic": null,
      "restrictions": null,
      "defaultAnswer": null,
      "formatting": null,
      "calculationMethod": null,
      "items": [
        {
          "questionCode": "46589-8",
          "localQuestionCode": "M1700",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": "Identifies the patient's current level of cognitive functioning, including alertness, orientation, comprehension, concentration, and immediate memory for simple commands.",
          "copyrightNotice": null,
          "question": "Cognitive Functioning",
          "answers": [
            {
              "label": "0",
              "code": "LA6153-6",
              "text": "Alert/oriented, able to focus and shift attention, comprehends and recalls task directions independently.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA6362-3",
              "text": "Requires prompting (cueing, repetition, reminders) only under stressful or unfamiliar conditions.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA6359-9",
              "text": "Requires assistance and some direction in specific situations (for example, all tasks involving shifting of attention) or consistently requires low stimulus environment due to distractibility.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA12251-7",
              "text": "Requires considerable assistance in routine situations. Is not alert and oriented or is unable to shift attention and recall directions more than half the time.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "4",
              "code": "LA6399-5",
              "text": "Totally dependent due to disturbances such as constant disorientation, coma, persistent vegetative state, or delirium.",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99140-6/46589-8",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "46589-8",
              "display": "Cognitive Functioning",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "58104-1",
          "localQuestionCode": "M1710",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "When Confused",
          "answers": [
            {
              "label": "0",
              "code": "LA6270-8",
              "text": "Never",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA6231-0",
              "text": "In new or complex situations only",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA6303-7",
              "text": "On awakening or at night only",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA6190-8",
              "text": "During the day and evening, but not constantly",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "4",
              "code": "LA6174-2",
              "text": "Constantly",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "NA",
              "code": "LA6335-9",
              "text": "Patient nonresponsive",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99140-6/58104-1",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "58104-1",
              "display": "When Confused",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "86495-9",
          "localQuestionCode": "M1720",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "When Anxious",
          "answers": [
            {
              "label": "0",
              "code": "LA6297-1",
              "text": "None of the time",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA6249-2",
              "text": "Less often than daily",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA6177-5",
              "text": "Daily, but not constantly",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA6154-4",
              "text": "All of the time",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "NA",
              "code": "LA6335-9",
              "text": "Patient nonresponsive",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99140-6/86495-9",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "86495-9",
              "display": "When Anxious",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "54605-1",
          "localQuestionCode": "C0100",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Should Brief Interview for Mental Status (C0200-C0500) be Conducted?",
          "answers": [
            {
              "label": "0",
              "code": "LA11150-2",
              "text": "No (resident is rarely/never understood)",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA33-6",
              "text": "Yes",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99140-6/54605-1",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "54605-1",
              "display": "Should Brief Interview for Mental Status (C0200-C0500) be Conducted?",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "52491-8",
          "localQuestionCode": null,
          "dataType": "SECTION",
          "header": true,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Brief Interview for Mental Status",
          "answers": null,
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": [
            {
              "questionCode": "52731-7",
              "localQuestionCode": "C0200",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Repetition of Three Words",
              "answers": [
                {
                  "label": "0",
                  "code": "LA137-2",
                  "text": "None",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "1",
                  "code": "LA6306-0",
                  "text": "One",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "2",
                  "code": "LA6404-3",
                  "text": "Two",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "3",
                  "code": "LA6395-3",
                  "text": "Three",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/99140-6/52491-8/52731-7",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "52731-7",
                  "display": "Repetition of Three Words",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "54510-3",
              "localQuestionCode": "C0300",
              "dataType": "SECTION",
              "header": true,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Temporal Orientation (Orientation to year, month, and day)",
              "answers": null,
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": [
                {
                  "questionCode": "52732-5",
                  "localQuestionCode": "C0300A",
                  "dataType": "CNE",
                  "header": false,
                  "units": null,
                  "codingInstructions": null,
                  "copyrightNotice": null,
                  "question": "Able to report correct year",
                  "answers": [
                    {
                      "label": "0",
                      "code": "LA10965-4",
                      "text": "Missed by > 5 years or no answer",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "1",
                      "code": "LA10966-2",
                      "text": "Missed by 2-5 years",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "2",
                      "code": "LA10008-3",
                      "text": "Missed by 1 year",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "3",
                      "code": "LA9960-1",
                      "text": "Correct",
                      "other": null,
                      "system": "http://loinc.org"
                    }
                  ],
                  "skipLogic": null,
                  "restrictions": null,
                  "defaultAnswer": null,
                  "formatting": null,
                  "calculationMethod": null,
                  "items": null,
                  "linkId": "/99140-6/52491-8/54510-3/52732-5",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "52732-5",
                      "display": "Able to report correct year",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "52733-3",
                  "localQuestionCode": "C0300B",
                  "dataType": "CNE",
                  "header": false,
                  "units": null,
                  "codingInstructions": null,
                  "copyrightNotice": null,
                  "question": "Able to report correct month",
                  "answers": [
                    {
                      "label": "0",
                      "code": "LA10969-6",
                      "text": "Missed by > 1 month or no answer",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "1",
                      "code": "LA10010-9",
                      "text": "Missed by 6 days to 1 month",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "2",
                      "code": "LA9927-0",
                      "text": "Accurate within 5 days",
                      "other": null,
                      "system": "http://loinc.org"
                    }
                  ],
                  "skipLogic": null,
                  "restrictions": null,
                  "defaultAnswer": null,
                  "formatting": null,
                  "calculationMethod": null,
                  "items": null,
                  "linkId": "/99140-6/52491-8/54510-3/52733-3",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "52733-3",
                      "display": "Able to report correct month",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "54609-3",
                  "localQuestionCode": "C0300C",
                  "dataType": "CNE",
                  "header": false,
                  "units": null,
                  "codingInstructions": null,
                  "copyrightNotice": null,
                  "question": "Able to report correct day of the week",
                  "answers": [
                    {
                      "label": "0",
                      "code": "LA9981-7",
                      "text": "Incorrect or no answer",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "1",
                      "code": "LA9960-1",
                      "text": "Correct",
                      "other": null,
                      "system": "http://loinc.org"
                    }
                  ],
                  "skipLogic": null,
                  "restrictions": null,
                  "defaultAnswer": null,
                  "formatting": null,
                  "calculationMethod": null,
                  "items": null,
                  "linkId": "/99140-6/52491-8/54510-3/54609-3",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "54609-3",
                      "display": "Able to report correct day of the week",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                }
              ],
              "linkId": "/99140-6/52491-8/54510-3",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "54510-3",
                  "display": "Temporal Orientation (Orientation to year, month, and day)",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": { "questionLayout": "vertical" },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "52493-4",
              "localQuestionCode": "C0400",
              "dataType": "SECTION",
              "header": true,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Recall",
              "answers": null,
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": [
                {
                  "questionCode": "52735-8",
                  "localQuestionCode": "C0400A",
                  "dataType": "CNE",
                  "header": false,
                  "units": null,
                  "codingInstructions": null,
                  "copyrightNotice": null,
                  "question": "Able to recall \"sock\"",
                  "answers": [
                    {
                      "label": "0",
                      "code": "LA10974-6",
                      "text": "No - could not recall",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "1",
                      "code": "LA10126-3",
                      "text": "Yes, after cueing (\"something to wear\")",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "2",
                      "code": "LA10134-7",
                      "text": "Yes, no cue required",
                      "other": null,
                      "system": "http://loinc.org"
                    }
                  ],
                  "skipLogic": null,
                  "restrictions": null,
                  "defaultAnswer": null,
                  "formatting": null,
                  "calculationMethod": null,
                  "items": null,
                  "linkId": "/99140-6/52491-8/52493-4/52735-8",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "52735-8",
                      "display": "Able to recall \"sock\"",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "52736-6",
                  "localQuestionCode": "C0400B",
                  "dataType": "CNE",
                  "header": false,
                  "units": null,
                  "codingInstructions": null,
                  "copyrightNotice": null,
                  "question": "Able to recall \"blue\"",
                  "answers": [
                    {
                      "label": "0",
                      "code": "LA10974-6",
                      "text": "No - could not recall",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "1",
                      "code": "LA10978-7",
                      "text": "Yes, after cueing (\"a color\")",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "2",
                      "code": "LA10134-7",
                      "text": "Yes, no cue required",
                      "other": null,
                      "system": "http://loinc.org"
                    }
                  ],
                  "skipLogic": null,
                  "restrictions": null,
                  "defaultAnswer": null,
                  "formatting": null,
                  "calculationMethod": null,
                  "items": null,
                  "linkId": "/99140-6/52491-8/52493-4/52736-6",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "52736-6",
                      "display": "Able to recall \"blue\"",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "52737-4",
                  "localQuestionCode": "C0400C",
                  "dataType": "CNE",
                  "header": false,
                  "units": null,
                  "codingInstructions": null,
                  "copyrightNotice": null,
                  "question": "Able to recall \"bed\"",
                  "answers": [
                    {
                      "label": "0",
                      "code": "LA10974-6",
                      "text": "No - could not recall",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "1",
                      "code": "LA10125-5",
                      "text": "Yes, after cueing (\"a piece of furniture\")",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "2",
                      "code": "LA10134-7",
                      "text": "Yes, no cue required",
                      "other": null,
                      "system": "http://loinc.org"
                    }
                  ],
                  "skipLogic": null,
                  "restrictions": null,
                  "defaultAnswer": null,
                  "formatting": null,
                  "calculationMethod": null,
                  "items": null,
                  "linkId": "/99140-6/52491-8/52493-4/52737-4",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "52737-4",
                      "display": "Able to recall \"bed\"",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                }
              ],
              "linkId": "/99140-6/52491-8/52493-4",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "52493-4",
                  "display": "Recall",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": { "questionLayout": "vertical" },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "54614-3",
              "localQuestionCode": "C0500",
              "dataType": "REAL",
              "header": false,
              "units": [
                {
                  "name": "{score}",
                  "code": "{score}",
                  "system": "http://unitsofmeasure.org",
                  "default": false
                }
              ],
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "BIMS Summary Score",
              "answers": null,
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": {
                "name": "TOTALSCORE",
                "value": ["/99138-0/93157-6", "/93170-9/93159-2"]
              },
              "items": null,
              "linkId": "/99140-6/52491-8/54614-3",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "54614-3",
                  "display": "BIMS Summary Score",
                  "system": "http://loinc.org"
                }
              ],
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" },
              "unit": {
                "name": "{score}",
                "code": "{score}",
                "system": "http://unitsofmeasure.org",
                "default": false
              },
              "value": 0
            }
          ],
          "linkId": "/99140-6/52491-8",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "52491-8",
              "display": "Brief Interview for Mental Status",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": { "questionLayout": "vertical" },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "95816-5",
          "localQuestionCode": "C1310",
          "dataType": "SECTION",
          "header": true,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Signs and Symptoms of Delirium (from CAM)",
          "answers": null,
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": [
            {
              "questionCode": "95813-2",
              "localQuestionCode": "C1310A",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": "Copyright © 2003 Sharon K. Inouye, M.D., MPH. Adapted from: Inouye SK, vanDyck CH, Alessi CA, Balkin S, Siegal AP, Horwitz RI. Clarifying confusion: The Confusion Assessment Method. A new method for detection of delirium. Ann Intern Med. 1990; 113: 941-948. Confusion Assessment Method: Training Manual and Coding Guide. Used with permission.",
              "question": "Acute Onset Mental Status Change. Is there evidence of an acute change in mental status from the patient's baseline?",
              "answers": [
                {
                  "label": "0",
                  "code": "LA32-8",
                  "text": "No",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "1",
                  "code": "LA33-6",
                  "text": "Yes",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/99140-6/95816-5/95813-2",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "95813-2",
                  "display": "Acute Onset Mental Status Change. Is there evidence of an acute change in mental status from the patient's baseline?",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "95812-4",
              "localQuestionCode": "C1310B",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": "Copyright © 2003 Sharon K. Inouye, M.D., MPH. Adapted from: Inouye SK, vanDyck CH, Alessi CA, Balkin S, Siegal AP, Horwitz RI. Clarifying confusion: The Confusion Assessment Method. A new method for detection of delirium. Ann Intern Med. 1990; 113: 941-948. Confusion Assessment Method: Training Manual and Coding Guide. Used with permission.",
              "question": "Inattention - Did the patient have difficulty focusing attention, for example, being easily distractible or having difficulty keeping track of what was being said?",
              "answers": [
                {
                  "label": "0",
                  "code": "LA61-7",
                  "text": "Behavior not present",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "1",
                  "code": "LA10992-8",
                  "text": "Behavior continuously present, does not fluctuate",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "2",
                  "code": "LA10993-6",
                  "text": "Behavior present, fluctuates (comes and goes, changes in severity)",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/99140-6/95816-5/95812-4",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "95812-4",
                  "display": "Inattention - Did the patient have difficulty focusing attention, for example, being easily distractible or having difficulty keeping track of what was being said?",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "95814-0",
              "localQuestionCode": "C1310C",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": "Copyright © 2003 Sharon K. Inouye, M.D., MPH. Adapted from: Inouye SK, vanDyck CH, Alessi CA, Balkin S, Siegal AP, Horwitz RI. Clarifying confusion: The Confusion Assessment Method. A new method for detection of delirium. Ann Intern Med. 1990; 113: 941-948. Confusion Assessment Method: Training Manual and Coding Guide. Used with permission.",
              "question": "Disorganized thinking - Was the patient's thinking disorganized or incoherent (rambling or irrelevant conversation, unclear or illogical flow of ideas, or unpredictable switching from subject to subject)?",
              "answers": [
                {
                  "label": "0",
                  "code": "LA61-7",
                  "text": "Behavior not present",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "1",
                  "code": "LA10992-8",
                  "text": "Behavior continuously present, does not fluctuate",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "2",
                  "code": "LA10993-6",
                  "text": "Behavior present, fluctuates (comes and goes, changes in severity)",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/99140-6/95816-5/95814-0",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "95814-0",
                  "display": "Disorganized thinking - Was the patient's thinking disorganized or incoherent (rambling or irrelevant conversation, unclear or illogical flow of ideas, or unpredictable switching from subject to subject)?",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "95815-7",
              "localQuestionCode": "C1310D",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": "This term is the CMS Assessment adaption of question 4 on the Confusion Assessment Method (CAM): \"[Altered level of consciousness] Overall, how would you rate this patient's level of consciousness? (Alert [normal]; Vigilant [hyperalert, overly sensitive to environmental stimuli, startled very easily], Lethargic [drowsy, easily aroused]; Stupor [difficult to arouse]; Coma; [unarousable]; Uncertain)\"",
              "copyrightNotice": "Copyright © 2003 Sharon K. Inouye, M.D., MPH. Adapted from: Inouye SK, vanDyck CH, Alessi CA, Balkin S, Siegal AP, Horwitz RI. Clarifying confusion: The Confusion Assessment Method. A new method for detection of delirium. Ann Intern Med. 1990; 113: 941-948. Confusion Assessment Method: Training Manual and Coding Guide. Used with permission.",
              "question": "Altered level of consciousness - Did the patient have altered level of consciousness, as indicated by any of the following criteria?",
              "answers": [
                {
                  "label": "0",
                  "code": "LA61-7",
                  "text": "Behavior not present",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "1",
                  "code": "LA10992-8",
                  "text": "Behavior continuously present, does not fluctuate",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "2",
                  "code": "LA10993-6",
                  "text": "Behavior present, fluctuates (comes and goes, changes in severity)",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/99140-6/95816-5/95815-7",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "95815-7",
                  "display": "Altered level of consciousness - Did the patient have altered level of consciousness, as indicated by any of the following criteria?",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            }
          ],
          "linkId": "/99140-6/95816-5",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "95816-5",
              "display": "Signs and Symptoms of Delirium (from CAM)",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": { "questionLayout": "vertical" },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        }
      ],
      "linkId": "/99140-6",
      "questionCodeSystem": "http://loinc.org",
      "codeList": [
        {
          "code": "99140-6",
          "display": "Cognitive Patterns",
          "system": "http://loinc.org"
        }
      ],
      "displayControl": { "questionLayout": "vertical" },
      "questionCardinality": { "min": "1", "max": "1" },
      "answerCardinality": { "min": "0", "max": "1" }
    },
    {
      "questionCode": "93170-9",
      "localQuestionCode": "D",
      "dataType": "SECTION",
      "header": true,
      "units": null,
      "codingInstructions": null,
      "copyrightNotice": null,
      "question": "Mood",
      "answers": null,
      "skipLogic": null,
      "restrictions": null,
      "defaultAnswer": null,
      "formatting": null,
      "calculationMethod": null,
      "items": [
        {
          "questionCode": "54635-8",
          "localQuestionCode": "D0150",
          "dataType": "SECTION",
          "header": true,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": "Copyright © Pfizer Inc. All rights reserved. Developed by Drs. Robert L. Spitzer, Janet B.W. Williams, Kurt Kroenke and colleagues, with an educational grant from Pfizer Inc. No permission required to reproduce, translate, display or distribute.",
          "question": "Patient Mood Interview (PHQ-2 to 9)",
          "answers": null,
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": [
            {
              "questionCode": "86843-0",
              "localQuestionCode": "D0150_1",
              "dataType": "SECTION",
              "header": true,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Symptom Presence",
              "answers": null,
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": [
                {
                  "questionCode": "54636-6",
                  "localQuestionCode": "D0150A1",
                  "dataType": "CNE",
                  "header": false,
                  "units": null,
                  "codingInstructions": null,
                  "copyrightNotice": "Copyright © Pfizer Inc. All rights reserved. Developed by Drs. Robert L. Spitzer, Janet B.W. Williams, Kurt Kroenke and colleagues, with an educational grant from Pfizer Inc. No permission required to reproduce, translate, display or distribute.",
                  "question": "Little interest or pleasure in doing things",
                  "answers": [
                    {
                      "label": "0",
                      "code": "LA32-8",
                      "text": "No",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "1",
                      "code": "LA33-6",
                      "text": "Yes",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "9",
                      "code": "LA10996-9",
                      "text": "No response",
                      "other": null,
                      "system": "http://loinc.org"
                    }
                  ],
                  "skipLogic": null,
                  "restrictions": null,
                  "defaultAnswer": null,
                  "formatting": null,
                  "calculationMethod": null,
                  "items": null,
                  "linkId": "/93170-9/54635-8/86843-0/54636-6",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "54636-6",
                      "display": "Little interest or pleasure in doing things",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "54638-2",
                  "localQuestionCode": "D0150B1",
                  "dataType": "CNE",
                  "header": false,
                  "units": null,
                  "codingInstructions": null,
                  "copyrightNotice": "Copyright © Pfizer Inc. All rights reserved. Developed by Drs. Robert L. Spitzer, Janet B.W. Williams, Kurt Kroenke and colleagues, with an educational grant from Pfizer Inc. No permission required to reproduce, translate, display or distribute.",
                  "question": "Feeling down, depressed or hopeless",
                  "answers": [
                    {
                      "label": "0",
                      "code": "LA32-8",
                      "text": "No",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "1",
                      "code": "LA33-6",
                      "text": "Yes",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "9",
                      "code": "LA10996-9",
                      "text": "No response",
                      "other": null,
                      "system": "http://loinc.org"
                    }
                  ],
                  "skipLogic": null,
                  "restrictions": null,
                  "defaultAnswer": null,
                  "formatting": null,
                  "calculationMethod": null,
                  "items": null,
                  "linkId": "/93170-9/54635-8/86843-0/54638-2",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "54638-2",
                      "display": "Feeling down, depressed or hopeless",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "54640-8",
                  "localQuestionCode": "D0150C1",
                  "dataType": "CNE",
                  "header": false,
                  "units": null,
                  "codingInstructions": null,
                  "copyrightNotice": "Copyright © Pfizer Inc. All rights reserved. Developed by Drs. Robert L. Spitzer, Janet B.W. Williams, Kurt Kroenke and colleagues, with an educational grant from Pfizer Inc. No permission required to reproduce, translate, display or distribute.",
                  "question": "Trouble falling or staying asleep, or sleeping too much",
                  "answers": [
                    {
                      "label": "0",
                      "code": "LA32-8",
                      "text": "No",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "1",
                      "code": "LA33-6",
                      "text": "Yes",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "9",
                      "code": "LA10996-9",
                      "text": "No response",
                      "other": null,
                      "system": "http://loinc.org"
                    }
                  ],
                  "skipLogic": null,
                  "restrictions": null,
                  "defaultAnswer": null,
                  "formatting": null,
                  "calculationMethod": null,
                  "items": null,
                  "linkId": "/93170-9/54635-8/86843-0/54640-8",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "54640-8",
                      "display": "Trouble falling or staying asleep, or sleeping too much",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "54642-4",
                  "localQuestionCode": "D0150D1",
                  "dataType": "CNE",
                  "header": false,
                  "units": null,
                  "codingInstructions": null,
                  "copyrightNotice": "Copyright © Pfizer Inc. All rights reserved. Developed by Drs. Robert L. Spitzer, Janet B.W. Williams, Kurt Kroenke and colleagues, with an educational grant from Pfizer Inc. No permission required to reproduce, translate, display or distribute.",
                  "question": "Feeling tired or having little energy",
                  "answers": [
                    {
                      "label": "0",
                      "code": "LA32-8",
                      "text": "No",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "1",
                      "code": "LA33-6",
                      "text": "Yes",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "9",
                      "code": "LA10996-9",
                      "text": "No response",
                      "other": null,
                      "system": "http://loinc.org"
                    }
                  ],
                  "skipLogic": null,
                  "restrictions": null,
                  "defaultAnswer": null,
                  "formatting": null,
                  "calculationMethod": null,
                  "items": null,
                  "linkId": "/93170-9/54635-8/86843-0/54642-4",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "54642-4",
                      "display": "Feeling tired or having little energy",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "54644-0",
                  "localQuestionCode": "D0150E1",
                  "dataType": "CNE",
                  "header": false,
                  "units": null,
                  "codingInstructions": null,
                  "copyrightNotice": "Copyright © Pfizer Inc. All rights reserved. Developed by Drs. Robert L. Spitzer, Janet B.W. Williams, Kurt Kroenke and colleagues, with an educational grant from Pfizer Inc. No permission required to reproduce, translate, display or distribute.",
                  "question": "Poor appetite or overeating",
                  "answers": [
                    {
                      "label": "0",
                      "code": "LA32-8",
                      "text": "No",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "1",
                      "code": "LA33-6",
                      "text": "Yes",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "9",
                      "code": "LA10996-9",
                      "text": "No response",
                      "other": null,
                      "system": "http://loinc.org"
                    }
                  ],
                  "skipLogic": null,
                  "restrictions": null,
                  "defaultAnswer": null,
                  "formatting": null,
                  "calculationMethod": null,
                  "items": null,
                  "linkId": "/93170-9/54635-8/86843-0/54644-0",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "54644-0",
                      "display": "Poor appetite or overeating",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "54646-5",
                  "localQuestionCode": "D0150F1",
                  "dataType": "CNE",
                  "header": false,
                  "units": null,
                  "codingInstructions": null,
                  "copyrightNotice": "Copyright © Pfizer Inc. All rights reserved. Developed by Drs. Robert L. Spitzer, Janet B.W. Williams, Kurt Kroenke and colleagues, with an educational grant from Pfizer Inc. No permission required to reproduce, translate, display or distribute.",
                  "question": "Feeling bad about yourself - or that you are a failure or have let yourself or your family down",
                  "answers": [
                    {
                      "label": "0",
                      "code": "LA32-8",
                      "text": "No",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "1",
                      "code": "LA33-6",
                      "text": "Yes",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "9",
                      "code": "LA10996-9",
                      "text": "No response",
                      "other": null,
                      "system": "http://loinc.org"
                    }
                  ],
                  "skipLogic": null,
                  "restrictions": null,
                  "defaultAnswer": null,
                  "formatting": null,
                  "calculationMethod": null,
                  "items": null,
                  "linkId": "/93170-9/54635-8/86843-0/54646-5",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "54646-5",
                      "display": "Feeling bad about yourself - or that you are a failure or have let yourself or your family down",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "54648-1",
                  "localQuestionCode": "D0150G1",
                  "dataType": "CNE",
                  "header": false,
                  "units": null,
                  "codingInstructions": null,
                  "copyrightNotice": "Copyright © Pfizer Inc. All rights reserved. Developed by Drs. Robert L. Spitzer, Janet B.W. Williams, Kurt Kroenke and colleagues, with an educational grant from Pfizer Inc. No permission required to reproduce, translate, display or distribute.",
                  "question": "Trouble concentrating on things, such as reading the newspaper or watching television",
                  "answers": [
                    {
                      "label": "0",
                      "code": "LA32-8",
                      "text": "No",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "1",
                      "code": "LA33-6",
                      "text": "Yes",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "9",
                      "code": "LA10996-9",
                      "text": "No response",
                      "other": null,
                      "system": "http://loinc.org"
                    }
                  ],
                  "skipLogic": null,
                  "restrictions": null,
                  "defaultAnswer": null,
                  "formatting": null,
                  "calculationMethod": null,
                  "items": null,
                  "linkId": "/93170-9/54635-8/86843-0/54648-1",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "54648-1",
                      "display": "Trouble concentrating on things, such as reading the newspaper or watching television",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "54650-7",
                  "localQuestionCode": "D0150H1",
                  "dataType": "CNE",
                  "header": false,
                  "units": null,
                  "codingInstructions": null,
                  "copyrightNotice": "Copyright © Pfizer Inc. All rights reserved. Developed by Drs. Robert L. Spitzer, Janet B.W. Williams, Kurt Kroenke and colleagues, with an educational grant from Pfizer Inc. No permission required to reproduce, translate, display or distribute.",
                  "question": "Moving or speaking so slowly that other people could have noticed. Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual",
                  "answers": [
                    {
                      "label": "0",
                      "code": "LA32-8",
                      "text": "No",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "1",
                      "code": "LA33-6",
                      "text": "Yes",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "9",
                      "code": "LA10996-9",
                      "text": "No response",
                      "other": null,
                      "system": "http://loinc.org"
                    }
                  ],
                  "skipLogic": null,
                  "restrictions": null,
                  "defaultAnswer": null,
                  "formatting": null,
                  "calculationMethod": null,
                  "items": null,
                  "linkId": "/93170-9/54635-8/86843-0/54650-7",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "54650-7",
                      "display": "Moving or speaking so slowly that other people could have noticed. Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "54652-3",
                  "localQuestionCode": "D0150I1",
                  "dataType": "CNE",
                  "header": false,
                  "units": null,
                  "codingInstructions": null,
                  "copyrightNotice": "Copyright © Pfizer Inc. All rights reserved. Developed by Drs. Robert L. Spitzer, Janet B.W. Williams, Kurt Kroenke and colleagues, with an educational grant from Pfizer Inc. No permission required to reproduce, translate, display or distribute.",
                  "question": "Thoughts that you would be better off dead, or of hurting yourself in some way",
                  "answers": [
                    {
                      "label": "0",
                      "code": "LA32-8",
                      "text": "No",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "1",
                      "code": "LA33-6",
                      "text": "Yes",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "9",
                      "code": "LA10996-9",
                      "text": "No response",
                      "other": null,
                      "system": "http://loinc.org"
                    }
                  ],
                  "skipLogic": null,
                  "restrictions": null,
                  "defaultAnswer": null,
                  "formatting": null,
                  "calculationMethod": null,
                  "items": null,
                  "linkId": "/93170-9/54635-8/86843-0/54652-3",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "54652-3",
                      "display": "Thoughts that you would be better off dead, or of hurting yourself in some way",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                }
              ],
              "linkId": "/93170-9/54635-8/86843-0",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "86843-0",
                  "display": "Symptom Presence",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": { "questionLayout": "vertical" },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "86844-8",
              "localQuestionCode": "D0150_2",
              "dataType": "SECTION",
              "header": true,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Symptom Frequency",
              "answers": null,
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": [
                {
                  "questionCode": "54637-4",
                  "localQuestionCode": "D0150A2",
                  "dataType": "CNE",
                  "header": false,
                  "units": null,
                  "codingInstructions": null,
                  "copyrightNotice": "Copyright © Pfizer Inc. All rights reserved. Developed by Drs. Robert L. Spitzer, Janet B.W. Williams, Kurt Kroenke and colleagues, with an educational grant from Pfizer Inc. No permission required to reproduce, translate, display or distribute.",
                  "question": "Little interest or pleasure in doing things",
                  "answers": [
                    {
                      "label": "0",
                      "code": "LA10997-7",
                      "text": "Never or 1 day",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "1",
                      "code": "LA10998-5",
                      "text": "2-6 days (several days)",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "2",
                      "code": "LA10999-3",
                      "text": "7-11 days (half or more of the days)",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "3",
                      "code": "LA11000-9",
                      "text": "12-14 days (nearly every day)",
                      "other": null,
                      "system": "http://loinc.org"
                    }
                  ],
                  "skipLogic": null,
                  "restrictions": null,
                  "defaultAnswer": null,
                  "formatting": null,
                  "calculationMethod": null,
                  "items": null,
                  "linkId": "/93170-9/54635-8/86844-8/54637-4",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "54637-4",
                      "display": "Little interest or pleasure in doing things",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "54639-0",
                  "localQuestionCode": "D0150B2",
                  "dataType": "CNE",
                  "header": false,
                  "units": null,
                  "codingInstructions": null,
                  "copyrightNotice": "Copyright © Pfizer Inc. All rights reserved. Developed by Drs. Robert L. Spitzer, Janet B.W. Williams, Kurt Kroenke and colleagues, with an educational grant from Pfizer Inc. No permission required to reproduce, translate, display or distribute.",
                  "question": "Feeling down, depressed or hopeless",
                  "answers": [
                    {
                      "label": "0",
                      "code": "LA10997-7",
                      "text": "Never or 1 day",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "1",
                      "code": "LA10998-5",
                      "text": "2-6 days (several days)",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "2",
                      "code": "LA10999-3",
                      "text": "7-11 days (half or more of the days)",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "3",
                      "code": "LA11000-9",
                      "text": "12-14 days (nearly every day)",
                      "other": null,
                      "system": "http://loinc.org"
                    }
                  ],
                  "skipLogic": null,
                  "restrictions": null,
                  "defaultAnswer": null,
                  "formatting": null,
                  "calculationMethod": null,
                  "items": null,
                  "linkId": "/93170-9/54635-8/86844-8/54639-0",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "54639-0",
                      "display": "Feeling down, depressed or hopeless",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "54641-6",
                  "localQuestionCode": "D0150C2",
                  "dataType": "CNE",
                  "header": false,
                  "units": null,
                  "codingInstructions": null,
                  "copyrightNotice": "Copyright © Pfizer Inc. All rights reserved. Developed by Drs. Robert L. Spitzer, Janet B.W. Williams, Kurt Kroenke and colleagues, with an educational grant from Pfizer Inc. No permission required to reproduce, translate, display or distribute.",
                  "question": "Trouble falling or staying asleep, or sleeping too much",
                  "answers": [
                    {
                      "label": "0",
                      "code": "LA10997-7",
                      "text": "Never or 1 day",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "1",
                      "code": "LA10998-5",
                      "text": "2-6 days (several days)",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "2",
                      "code": "LA10999-3",
                      "text": "7-11 days (half or more of the days)",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "3",
                      "code": "LA11000-9",
                      "text": "12-14 days (nearly every day)",
                      "other": null,
                      "system": "http://loinc.org"
                    }
                  ],
                  "skipLogic": null,
                  "restrictions": null,
                  "defaultAnswer": null,
                  "formatting": null,
                  "calculationMethod": null,
                  "items": null,
                  "linkId": "/93170-9/54635-8/86844-8/54641-6",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "54641-6",
                      "display": "Trouble falling or staying asleep, or sleeping too much",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "54643-2",
                  "localQuestionCode": "D0150D2",
                  "dataType": "CNE",
                  "header": false,
                  "units": null,
                  "codingInstructions": null,
                  "copyrightNotice": "Copyright © Pfizer Inc. All rights reserved. Developed by Drs. Robert L. Spitzer, Janet B.W. Williams, Kurt Kroenke and colleagues, with an educational grant from Pfizer Inc. No permission required to reproduce, translate, display or distribute.",
                  "question": "Feeling tired or having little energy",
                  "answers": [
                    {
                      "label": "0",
                      "code": "LA10997-7",
                      "text": "Never or 1 day",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "1",
                      "code": "LA10998-5",
                      "text": "2-6 days (several days)",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "2",
                      "code": "LA10999-3",
                      "text": "7-11 days (half or more of the days)",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "3",
                      "code": "LA11000-9",
                      "text": "12-14 days (nearly every day)",
                      "other": null,
                      "system": "http://loinc.org"
                    }
                  ],
                  "skipLogic": null,
                  "restrictions": null,
                  "defaultAnswer": null,
                  "formatting": null,
                  "calculationMethod": null,
                  "items": null,
                  "linkId": "/93170-9/54635-8/86844-8/54643-2",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "54643-2",
                      "display": "Feeling tired or having little energy",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "54645-7",
                  "localQuestionCode": "D0150E2",
                  "dataType": "CNE",
                  "header": false,
                  "units": null,
                  "codingInstructions": null,
                  "copyrightNotice": "Copyright © Pfizer Inc. All rights reserved. Developed by Drs. Robert L. Spitzer, Janet B.W. Williams, Kurt Kroenke and colleagues, with an educational grant from Pfizer Inc. No permission required to reproduce, translate, display or distribute.",
                  "question": "Poor appetite or overeating",
                  "answers": [
                    {
                      "label": "0",
                      "code": "LA10997-7",
                      "text": "Never or 1 day",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "1",
                      "code": "LA10998-5",
                      "text": "2-6 days (several days)",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "2",
                      "code": "LA10999-3",
                      "text": "7-11 days (half or more of the days)",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "3",
                      "code": "LA11000-9",
                      "text": "12-14 days (nearly every day)",
                      "other": null,
                      "system": "http://loinc.org"
                    }
                  ],
                  "skipLogic": null,
                  "restrictions": null,
                  "defaultAnswer": null,
                  "formatting": null,
                  "calculationMethod": null,
                  "items": null,
                  "linkId": "/93170-9/54635-8/86844-8/54645-7",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "54645-7",
                      "display": "Poor appetite or overeating",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "54647-3",
                  "localQuestionCode": "D0150F2",
                  "dataType": "CNE",
                  "header": false,
                  "units": null,
                  "codingInstructions": null,
                  "copyrightNotice": "Copyright © Pfizer Inc. All rights reserved. Developed by Drs. Robert L. Spitzer, Janet B.W. Williams, Kurt Kroenke and colleagues, with an educational grant from Pfizer Inc. No permission required to reproduce, translate, display or distribute.",
                  "question": "Feeling bad about yourself - or that you are a failure or have let yourself or your family down",
                  "answers": [
                    {
                      "label": "0",
                      "code": "LA10997-7",
                      "text": "Never or 1 day",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "1",
                      "code": "LA10998-5",
                      "text": "2-6 days (several days)",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "2",
                      "code": "LA10999-3",
                      "text": "7-11 days (half or more of the days)",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "3",
                      "code": "LA11000-9",
                      "text": "12-14 days (nearly every day)",
                      "other": null,
                      "system": "http://loinc.org"
                    }
                  ],
                  "skipLogic": null,
                  "restrictions": null,
                  "defaultAnswer": null,
                  "formatting": null,
                  "calculationMethod": null,
                  "items": null,
                  "linkId": "/93170-9/54635-8/86844-8/54647-3",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "54647-3",
                      "display": "Feeling bad about yourself - or that you are a failure or have let yourself or your family down",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "54649-9",
                  "localQuestionCode": "D0150G2",
                  "dataType": "CNE",
                  "header": false,
                  "units": null,
                  "codingInstructions": null,
                  "copyrightNotice": "Copyright © Pfizer Inc. All rights reserved. Developed by Drs. Robert L. Spitzer, Janet B.W. Williams, Kurt Kroenke and colleagues, with an educational grant from Pfizer Inc. No permission required to reproduce, translate, display or distribute.",
                  "question": "Trouble concentrating on things, such as reading the newspaper or watching television",
                  "answers": [
                    {
                      "label": "0",
                      "code": "LA10997-7",
                      "text": "Never or 1 day",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "1",
                      "code": "LA10998-5",
                      "text": "2-6 days (several days)",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "2",
                      "code": "LA10999-3",
                      "text": "7-11 days (half or more of the days)",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "3",
                      "code": "LA11000-9",
                      "text": "12-14 days (nearly every day)",
                      "other": null,
                      "system": "http://loinc.org"
                    }
                  ],
                  "skipLogic": null,
                  "restrictions": null,
                  "defaultAnswer": null,
                  "formatting": null,
                  "calculationMethod": null,
                  "items": null,
                  "linkId": "/93170-9/54635-8/86844-8/54649-9",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "54649-9",
                      "display": "Trouble concentrating on things, such as reading the newspaper or watching television",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "54651-5",
                  "localQuestionCode": "D0150H2",
                  "dataType": "CNE",
                  "header": false,
                  "units": null,
                  "codingInstructions": null,
                  "copyrightNotice": "Copyright © Pfizer Inc. All rights reserved. Developed by Drs. Robert L. Spitzer, Janet B.W. Williams, Kurt Kroenke and colleagues, with an educational grant from Pfizer Inc. No permission required to reproduce, translate, display or distribute.",
                  "question": "Moving or speaking so slowly that other people could have noticed. Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual",
                  "answers": [
                    {
                      "label": "0",
                      "code": "LA10997-7",
                      "text": "Never or 1 day",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "1",
                      "code": "LA10998-5",
                      "text": "2-6 days (several days)",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "2",
                      "code": "LA10999-3",
                      "text": "7-11 days (half or more of the days)",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "3",
                      "code": "LA11000-9",
                      "text": "12-14 days (nearly every day)",
                      "other": null,
                      "system": "http://loinc.org"
                    }
                  ],
                  "skipLogic": null,
                  "restrictions": null,
                  "defaultAnswer": null,
                  "formatting": null,
                  "calculationMethod": null,
                  "items": null,
                  "linkId": "/93170-9/54635-8/86844-8/54651-5",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "54651-5",
                      "display": "Moving or speaking so slowly that other people could have noticed. Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "54653-1",
                  "localQuestionCode": "D0150I2",
                  "dataType": "CNE",
                  "header": false,
                  "units": null,
                  "codingInstructions": null,
                  "copyrightNotice": "Copyright © Pfizer Inc. All rights reserved. Developed by Drs. Robert L. Spitzer, Janet B.W. Williams, Kurt Kroenke and colleagues, with an educational grant from Pfizer Inc. No permission required to reproduce, translate, display or distribute.",
                  "question": "Thoughts that you would be better off dead, or of hurting yourself in some way",
                  "answers": [
                    {
                      "label": "0",
                      "code": "LA10997-7",
                      "text": "Never or 1 day",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "1",
                      "code": "LA10998-5",
                      "text": "2-6 days (several days)",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "2",
                      "code": "LA10999-3",
                      "text": "7-11 days (half or more of the days)",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "3",
                      "code": "LA11000-9",
                      "text": "12-14 days (nearly every day)",
                      "other": null,
                      "system": "http://loinc.org"
                    }
                  ],
                  "skipLogic": null,
                  "restrictions": null,
                  "defaultAnswer": null,
                  "formatting": null,
                  "calculationMethod": null,
                  "items": null,
                  "linkId": "/93170-9/54635-8/86844-8/54653-1",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "54653-1",
                      "display": "Thoughts that you would be better off dead, or of hurting yourself in some way",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                }
              ],
              "linkId": "/93170-9/54635-8/86844-8",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "86844-8",
                  "display": "Symptom Frequency",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": { "questionLayout": "vertical" },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            }
          ],
          "linkId": "/93170-9/54635-8",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "54635-8",
              "display": "Patient Mood Interview (PHQ-2 to 9)",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": { "questionLayout": "vertical" },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "54654-9",
          "localQuestionCode": "D0160",
          "dataType": "REAL",
          "header": false,
          "units": [
            {
              "name": "{score}",
              "code": "{score}",
              "system": "http://unitsofmeasure.org",
              "default": false
            }
          ],
          "codingInstructions": null,
          "copyrightNotice": "Copyright © Pfizer Inc. All rights reserved. Developed by Drs. Robert L. Spitzer, Janet B.W. Williams, Kurt Kroenke and colleagues, with an educational grant from Pfizer Inc. No permission required to reproduce, translate, display or distribute.",
          "question": "Total Severity Score",
          "answers": null,
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": {
            "name": "TOTALSCORE",
            "value": ["/99138-0/93157-6", "/93170-9/93159-2"]
          },
          "items": null,
          "linkId": "/93170-9/54654-9",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "54654-9",
              "display": "Total Severity Score",
              "system": "http://loinc.org"
            }
          ],
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" },
          "unit": {
            "name": "{score}",
            "code": "{score}",
            "system": "http://unitsofmeasure.org",
            "default": false
          },
          "value": 0
        },
        {
          "questionCode": "93159-2",
          "localQuestionCode": "D0700",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Social Isolation. How often do you feel lonely or isolated from those around you?",
          "answers": [
            {
              "label": "0",
              "code": "LA6270-8",
              "text": "Never",
              "score": 0,
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA10066-1",
              "text": "Rarely",
              "score": 1,
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA10082-8",
              "text": "Sometimes",
              "score": 2,
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA10044-8",
              "text": "Often",
              "score": 3,
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "4",
              "code": "LA9933-8",
              "text": "Always",
              "score": 4,
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "8",
              "code": "LA30257-2",
              "text": "Patient unable to respond",
              "score": 8,
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/93170-9/93159-2",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "93159-2",
              "display": "Social Isolation. How often do you feel lonely or isolated from those around you?",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        }
      ],
      "linkId": "/93170-9",
      "questionCodeSystem": "http://loinc.org",
      "codeList": [
        { "code": "93170-9", "display": "Mood", "system": "http://loinc.org" }
      ],
      "displayControl": { "questionLayout": "vertical" },
      "questionCardinality": { "min": "1", "max": "1" },
      "answerCardinality": { "min": "0", "max": "1" }
    },
    {
      "questionCode": "99144-8",
      "localQuestionCode": "E",
      "dataType": "SECTION",
      "header": true,
      "units": null,
      "codingInstructions": null,
      "copyrightNotice": null,
      "question": "Behavior",
      "answers": null,
      "skipLogic": null,
      "restrictions": null,
      "defaultAnswer": null,
      "formatting": null,
      "calculationMethod": null,
      "items": [
        {
          "questionCode": "46473-5",
          "localQuestionCode": "M1740",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Cognitive, Behavorial, and Psychiatric Symptoms that are demonstrated at least once a week (reported or observed)",
          "answers": [
            {
              "label": "1",
              "code": "LA12257-4",
              "text": "Memory deficit: failure to recognize familiar persons/places, inability to recall events of past 24 hours, significant memory loss so that supervision is required",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA6228-6",
              "text": "Impaired decision-making: failure to perform usual ADLs or IADLs, inability to appropriately stop activities, jeopardizes safety through actions",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA6439-9",
              "text": "Verbal disruption: yelling, threatening, excessive profanity, sexual references, etc.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "4",
              "code": "LA12260-8",
              "text": "Physical aggression: aggressive or combative to self and others (for example, hits self, throws objects, punches, dangerous maneuvers with wheelchair or other objects)",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "5",
              "code": "LA6187-4",
              "text": "Disruptive, infantile, or socially inappropriate behavior (excludes verbal actions)",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "6",
              "code": "LA6181-7",
              "text": "Delusional, hallucinatory, or paranoid behavior",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "7",
              "code": "LA6294-8",
              "text": "None of the above behaviors demonstrated",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99144-8/46473-5",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "46473-5",
              "display": "Cognitive, Behavorial, and Psychiatric Symptoms that are demonstrated at least once a week (reported or observed)",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "46592-2",
          "localQuestionCode": "M1745",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Frequency of Disruptive Behavior Symptoms (reported or observed): Any physical, verbal, or other disruptive/dangerous symptoms that are injurious to self or others or jeopardize personal safety.",
          "answers": [
            {
              "label": "0",
              "code": "LA6270-8",
              "text": "Never",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA6251-8",
              "text": "Less than once a month",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA6304-5",
              "text": "Once a month",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA6374-8",
              "text": "Several times each month",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "4",
              "code": "LA6371-4",
              "text": "Several times a week",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "5",
              "code": "LA6157-7",
              "text": "At least daily",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99144-8/46592-2",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "46592-2",
              "display": "Frequency of Disruptive Behavior Symptoms (reported or observed): Any physical, verbal, or other disruptive/dangerous symptoms that are injurious to self or others or jeopardize personal safety.",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        }
      ],
      "linkId": "/99144-8",
      "questionCodeSystem": "http://loinc.org",
      "codeList": [
        {
          "code": "99144-8",
          "display": "Behavior",
          "system": "http://loinc.org"
        }
      ],
      "displayControl": { "questionLayout": "vertical" },
      "questionCardinality": { "min": "1", "max": "1" },
      "answerCardinality": { "min": "0", "max": "1" }
    },
    {
      "questionCode": "99147-1",
      "localQuestionCode": "F",
      "dataType": "SECTION",
      "header": true,
      "units": null,
      "codingInstructions": null,
      "copyrightNotice": null,
      "question": "Preferences for Customary Routine Activities",
      "answers": null,
      "skipLogic": null,
      "restrictions": null,
      "defaultAnswer": null,
      "formatting": null,
      "calculationMethod": null,
      "items": [
        {
          "questionCode": "85950-4",
          "localQuestionCode": "M1100",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Patient Living Situation: Which of the following best describes the patient's residential circumstance and availability of assistance?",
          "answers": [
            {
              "label": "01",
              "code": "LA27650-3",
              "text": "Patient lives alone - around the clock",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "02",
              "code": "LA27651-1",
              "text": "Patient lives alone - regular daytime",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "03",
              "code": "LA27652-9",
              "text": "Patient lives alone - regular nighttime",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "04",
              "code": "LA27653-7",
              "text": "Patient lives alone - occasional/short-term assistance",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "05",
              "code": "LA27654-5",
              "text": "Patient lives alone - no assistance available",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "06",
              "code": "LA27655-2",
              "text": "Patient lives with other person(s) in the home - around the clock",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "07",
              "code": "LA27656-0",
              "text": "Patient lives with other person(s) in the home - regular daytime",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "08",
              "code": "LA27657-8",
              "text": "Patient lives with other person(s) in the home - regular nighttime",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "09",
              "code": "LA27658-6",
              "text": "Patient lives with other person(s) in the home - occasional/short-term assistance",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "10",
              "code": "LA27659-4",
              "text": "Patient lives with other person(s) in the home - no assistance available",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "11",
              "code": "LA27660-2",
              "text": "Patient lives in congregate situation (for example, assisted living, residential care home) - around the clock",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "12",
              "code": "LA27661-0",
              "text": "Patient lives in congregate situation (for example, assisted living, residential care home) - regular daytime",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "13",
              "code": "LA27662-8",
              "text": "Patient lives in congregate situation (for example, assisted living, residential care home) - regular nighttime",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "14",
              "code": "LA27663-6",
              "text": "Patient lives in congregate situation (for example, assisted living, residential care home) - occasional/short-term assistance",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "15",
              "code": "LA27664-4",
              "text": "Patient lives in congregate situation (for example, assisted living, residential care home) - no assistance available",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99147-1/85950-4",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "85950-4",
              "display": "Patient Living Situation: Which of the following best describes the patient's residential circumstance and availability of assistance?",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "88465-0",
          "localQuestionCode": "M2102",
          "dataType": "SECTION",
          "header": true,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Types and Sources of Assistance",
          "answers": null,
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": [
            {
              "questionCode": "57265-1",
              "localQuestionCode": "M2102f",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Supervision and safety (for example, due to cognitive impairment)",
              "answers": [
                {
                  "label": "0",
                  "code": "LA27608-1",
                  "text": "No assistance needed -patient is independent or does not have needs in this area",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "1",
                  "code": "LA27610-7",
                  "text": "Non-agency caregiver(s) currently provide assistance",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "2",
                  "code": "LA27611-5",
                  "text": "Non-agency caregiver(s) need training/ supportive services to provide assistance",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "3",
                  "code": "LA27612-3",
                  "text": "Non-agency caregiver(s) are not likely to provide assistance OR it is unclear if they will provide assistance",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "4",
                  "code": "LA27613-1",
                  "text": "Assistance needed, but no non-agency caregiver(s) available",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/99147-1/88465-0/57265-1",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "57265-1",
                  "display": "Supervision and safety (for example, due to cognitive impairment)",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            }
          ],
          "linkId": "/99147-1/88465-0",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "88465-0",
              "display": "Types and Sources of Assistance",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": { "questionLayout": "vertical" },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        }
      ],
      "linkId": "/99147-1",
      "questionCodeSystem": "http://loinc.org",
      "codeList": [
        {
          "code": "99147-1",
          "display": "Preferences for Customary Routine Activities",
          "system": "http://loinc.org"
        }
      ],
      "displayControl": { "questionLayout": "vertical" },
      "questionCardinality": { "min": "1", "max": "1" },
      "answerCardinality": { "min": "0", "max": "1" }
    },
    {
      "questionCode": "99148-9",
      "localQuestionCode": "G",
      "dataType": "SECTION",
      "header": true,
      "units": null,
      "codingInstructions": null,
      "copyrightNotice": null,
      "question": "Functional Status",
      "answers": null,
      "skipLogic": null,
      "restrictions": null,
      "defaultAnswer": null,
      "formatting": null,
      "calculationMethod": null,
      "items": [
        {
          "questionCode": "46595-5",
          "localQuestionCode": "M1800",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": "Identifies the patient's ability to tend to personal hygiene needs, excluding bathing (such as washing face and hands, hair care, shaving or make up, teeth or denture care, or fingernail care).",
          "copyrightNotice": null,
          "question": "Grooming: Current ability to tend safely to personal hygiene needs (specifically: washing face and hands, hair care, shaving or make up, teeth or denture care, or fingernail care).",
          "answers": [
            {
              "label": "0",
              "code": "LA6131-2",
              "text": "Able to groom self unaided, with or without the use of assistive devices or adapted methods.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA6207-0",
              "text": "Grooming utensils must be placed within reach before able to complete grooming activities.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA6379-7",
              "text": "Someone must assist the patient to groom self.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA6326-8",
              "text": "Patient depends entirely upon someone else for grooming needs.",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99148-9/46595-5",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "46595-5",
              "display": "Grooming: Current ability to tend safely to personal hygiene needs (specifically: washing face and hands, hair care, shaving or make up, teeth or denture care, or fingernail care).",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "46597-1",
          "localQuestionCode": "M1810",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": "Identifies the patient's ability to dress upper body, including the ability to obtain, put on and remove upper body clothing.",
          "copyrightNotice": null,
          "question": "Current Ability to Dress Upper Body safely (with or without dressing aids) including undergarments, pullovers, front-opening shirts and blouses, managing zippers, buttons, and snaps.",
          "answers": [
            {
              "label": "0",
              "code": "LA6129-6",
              "text": "Able to get clothes out of closets and drawers, put them on and remove them from the upper body without assistance.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA6127-0",
              "text": "Able to dress upper body without assistance if clothing is laid out or handed to the patient.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA6381-3",
              "text": "Someone must help the patient put on upper body clothing.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA6325-0",
              "text": "Patient depends entirely upon another person to dress the upper body.",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99148-9/46597-1",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "46597-1",
              "display": "Current Ability to Dress Upper Body safely (with or without dressing aids) including undergarments, pullovers, front-opening shirts and blouses, managing zippers, buttons, and snaps.",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "46599-7",
          "localQuestionCode": "M1820",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": "Identifies the patient's ability to dress lower body, including the ability to obtain, put on and remove lower body clothing.",
          "copyrightNotice": null,
          "question": "Current Ability to Dress Lower Body safely (with or without dressing aids) including undergarments, slacks, socks or nylons, shoes.",
          "answers": [
            {
              "label": "0",
              "code": "LA6138-7",
              "text": "Able to obtain, put on, and remove clothing and shoes without assistance.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA6126-2",
              "text": "Able to dress lower body without assistance if clothing and shoes are laid out or handed to the patient.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA6380-5",
              "text": "Someone must help the patient put on undergarments, slacks, socks or nylons, and shoes.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA6324-3",
              "text": "Patient depends entirely upon another person to dress lower body.",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99148-9/46599-7",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "46599-7",
              "display": "Current Ability to Dress Lower Body safely (with or without dressing aids) including undergarments, slacks, socks or nylons, shoes.",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "57243-8",
          "localQuestionCode": "M1830",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Bathing: Current ability to wash entire body safely. Excludes grooming (washing face, washing hands, and shampooing hair).",
          "answers": [
            {
              "label": "0",
              "code": "LA12264-0",
              "text": "Able to bathe self in shower or tub independently, including getting in and out of tub/shower.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA12265-7",
              "text": "With the use of devices, is able to bathe self in shower or tub independently, including getting in and out of the tub/shower.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA12266-5",
              "text": "Able to bathe in shower or tub with the intermittent assistance of another person: (a) for intermittent supervision or encouragement or reminders, OR (b) to get in and out of the shower or tub, OR (c) for washing difficult to reach areas.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA12267-3",
              "text": "Able to participate in bathing self in shower or tub, but requires presence of another person throughout the bath for assistance or supervision.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "4",
              "code": "LA12268-1",
              "text": "Unable to use the shower or tub, but able to bathe self independently with or without the use of devices at the sink, in chair, or on commode.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "5",
              "code": "LA12269-9",
              "text": "Unable to use the shower or tub, but able to participate in bathing self in bed, at the sink, in bedside chair, or on commode, with the assistance or supervision of another person.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "6",
              "code": "LA12270-7",
              "text": "Unable to participate effectively in bathing and is bathed totally by another person.",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99148-9/57243-8",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "57243-8",
              "display": "Bathing: Current ability to wash entire body safely. Excludes grooming (washing face, washing hands, and shampooing hair).",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "57244-6",
          "localQuestionCode": "M1840",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Toilet Transferring: Current ability to get to and from the toilet or bedside commode safely and transfer on and off toilet/commode.",
          "answers": [
            {
              "label": "0",
              "code": "LA12271-5",
              "text": "Able to get to and from the toilet and transfer independently with or without a device.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA12272-3",
              "text": "When reminded, assisted, or supervised by another person, able to get to and from the toilet and transfer.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA6415-9",
              "text": "Unable to get to and from the toilet but is able to use a bedside commode (with or without assistance).",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA6416-7",
              "text": "Unable to get to and from the toilet or bedside commode but is able to use a bedpan/urinal independently.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "4",
              "code": "LA6245-0",
              "text": "Is totally dependent in toileting.",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99148-9/57244-6",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "57244-6",
              "display": "Toilet Transferring: Current ability to get to and from the toilet or bedside commode safely and transfer on and off toilet/commode.",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "57245-3",
          "localQuestionCode": "M1845",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Toileting Hygiene: Current ability to maintain perineal hygiene safely, adjust clothes and/or incontinence pads before and after using toilet, commode, bedpan, urinal. If managing ostomy, includes cleaning area around stoma, but not managing equipment.",
          "answers": [
            {
              "label": "0",
              "code": "LA12276-4",
              "text": "Able to manage toileting hygiene and clothing management without assistance.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA12277-2",
              "text": "Able to manage toileting hygiene and clothing management without assistance if supplies/implements are laid out for the patient.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA12278-0",
              "text": "Someone must help the patient to maintain toileting hygiene and/or adjust clothing.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA12279-8",
              "text": "Patient depends entirely upon another person to maintain toileting hygiene.",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99148-9/57245-3",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "57245-3",
              "display": "Toileting Hygiene: Current ability to maintain perineal hygiene safely, adjust clothes and/or incontinence pads before and after using toilet, commode, bedpan, urinal. If managing ostomy, includes cleaning area around stoma, but not managing equipment.",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "57246-1",
          "localQuestionCode": "M1850",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Transferring: Current ability to move safely from bed to chair, or ability to turn and position self in bed if patient is bedfast.",
          "answers": [
            {
              "label": "0",
              "code": "LA6136-1",
              "text": "Able to independently transfer.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA12281-4",
              "text": "Able to transfer with minimal human assistance or with use of an assistive device.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA12282-2",
              "text": "Able to bear weight and pivot during the transfer process but unable to transfer self.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA6426-6",
              "text": "Unable to transfer self and is unable to bear weight or pivot when transferred by another person.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "4",
              "code": "LA6161-9",
              "text": "Bedfast, unable to transfer but is able to turn and position self in bed.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "5",
              "code": "LA6160-1",
              "text": "Bedfast, unable to transfer and is unable to turn and position self.",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99148-9/57246-1",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "57246-1",
              "display": "Transferring: Current ability to move safely from bed to chair, or ability to turn and position self in bed if patient is bedfast.",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "57247-9",
          "localQuestionCode": "M1860",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Ambulation/Locomotion: Current ability to walk safely, once in a standing position, or use a wheelchair, once in a seated position, on a variety of surfaces.",
          "answers": [
            {
              "label": "0",
              "code": "LA12286-3",
              "text": "Able to independently walk on even and uneven surfaces and negotiate stairs with or without railings (specifically: needs no human assistance or assistive device).",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA12287-1",
              "text": "With the use of a one-handed device (for example, cane, single crutch, hemi-walker), able to independently walk on even and uneven surfaces and negotiate stairs with or without railings.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA12288-9",
              "text": "Requires use of a two-handed device (for example, walker or crutches) to walk alone on a level surface and/or requires human supervision or assistance to negotiate stairs or steps or uneven surfaces.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA6147-8",
              "text": "Able to walk only with the supervision or assistance of another person at all times.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "4",
              "code": "LA6171-8",
              "text": "Chairfast, unable to ambulate but is able to wheel self independently.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "5",
              "code": "LA6170-0",
              "text": "Chairfast, unable to ambulate and is unable to wheel self.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "6",
              "code": "LA6159-3",
              "text": "Bedfast, unable to ambulate or be up in a chair.",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99148-9/57247-9",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "57247-9",
              "display": "Ambulation/Locomotion: Current ability to walk safely, once in a standing position, or use a wheelchair, once in a seated position, on a variety of surfaces.",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        }
      ],
      "linkId": "/99148-9",
      "questionCodeSystem": "http://loinc.org",
      "codeList": [
        {
          "code": "99148-9",
          "display": "Functional Status",
          "system": "http://loinc.org"
        }
      ],
      "displayControl": { "questionLayout": "vertical" },
      "questionCardinality": { "min": "1", "max": "1" },
      "answerCardinality": { "min": "0", "max": "1" }
    },
    {
      "questionCode": "89572-2",
      "localQuestionCode": "GG",
      "dataType": "SECTION",
      "header": true,
      "units": null,
      "codingInstructions": null,
      "copyrightNotice": null,
      "question": "Functional Abilities and Goals",
      "answers": null,
      "skipLogic": null,
      "restrictions": null,
      "defaultAnswer": null,
      "formatting": null,
      "calculationMethod": null,
      "items": [
        {
          "questionCode": "83239-4",
          "localQuestionCode": "GG0100",
          "dataType": "SECTION",
          "header": true,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Prior Functioning: Everyday Activities",
          "answers": null,
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": [
            {
              "questionCode": "85070-1",
              "localQuestionCode": "GG0100A",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": "Need for assistance with bathing, dressing, using the toilet, and eating prior to the current illness, exacerbation, or injury.",
              "copyrightNotice": null,
              "question": "Self-Care",
              "answers": [
                {
                  "label": "3",
                  "code": "LA11539-6",
                  "text": "Independent - Patient completed all the activities by themself, with or without an assistive device, with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "2",
                  "code": "LA30364-6",
                  "text": "Needed some help - Patient needed partial assistance from another person to complete any activities.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "1",
                  "code": "LA30365-3",
                  "text": "Dependent - A helper completed all the activities for the patient.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "8",
                  "code": "LA4489-6",
                  "text": "Unknown",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "9",
                  "code": "LA4720-4",
                  "text": "Not applicable",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/83239-4/85070-1",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "85070-1",
                  "display": "Self-Care",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "85071-9",
              "localQuestionCode": "GG0100B",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": "Need for assistance with walking from room to room (with or without a device such as cane, crutch, or walker) prior to the current illness, exacerbation, or injury.",
              "copyrightNotice": null,
              "question": "Indoor Mobility (Ambulation)",
              "answers": [
                {
                  "label": "3",
                  "code": "LA11539-6",
                  "text": "Independent - Patient completed all the activities by themself, with or without an assistive device, with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "2",
                  "code": "LA30364-6",
                  "text": "Needed some help - Patient needed partial assistance from another person to complete any activities.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "1",
                  "code": "LA30365-3",
                  "text": "Dependent - A helper completed all the activities for the patient.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "8",
                  "code": "LA4489-6",
                  "text": "Unknown",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "9",
                  "code": "LA4720-4",
                  "text": "Not applicable",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/83239-4/85071-9",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "85071-9",
                  "display": "Indoor Mobility (Ambulation)",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "85072-7",
              "localQuestionCode": "GG0100C",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": "Need for assistance with internal or external stairs (with or without a device such as cane, crutch, or walker) prior to the current illness, exacerbation, or injury.",
              "copyrightNotice": null,
              "question": "Stairs",
              "answers": [
                {
                  "label": "3",
                  "code": "LA11539-6",
                  "text": "Independent - Patient completed all the activities by themself, with or without an assistive device, with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "2",
                  "code": "LA30364-6",
                  "text": "Needed some help - Patient needed partial assistance from another person to complete any activities.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "1",
                  "code": "LA30365-3",
                  "text": "Dependent - A helper completed all the activities for the patient.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "8",
                  "code": "LA4489-6",
                  "text": "Unknown",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "9",
                  "code": "LA4720-4",
                  "text": "Not applicable",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/83239-4/85072-7",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "85072-7",
                  "display": "Stairs",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "85073-5",
              "localQuestionCode": "GG0100D",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": "Need for assistance with planning regular tasks, such as shopping or remembering to take medication prior to the current illness, exacerbation, or injury.",
              "copyrightNotice": null,
              "question": "Functional Cognition",
              "answers": [
                {
                  "label": "3",
                  "code": "LA11539-6",
                  "text": "Independent - Patient completed all the activities by themself, with or without an assistive device, with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "2",
                  "code": "LA30364-6",
                  "text": "Needed some help - Patient needed partial assistance from another person to complete any activities.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "1",
                  "code": "LA30365-3",
                  "text": "Dependent - A helper completed all the activities for the patient.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "8",
                  "code": "LA4489-6",
                  "text": "Unknown",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "9",
                  "code": "LA4720-4",
                  "text": "Not applicable",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/83239-4/85073-5",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "85073-5",
                  "display": "Functional Cognition",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            }
          ],
          "linkId": "/89572-2/83239-4",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "83239-4",
              "display": "Prior Functioning: Everyday Activities",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": { "questionLayout": "vertical" },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "83234-5",
          "localQuestionCode": "GG0110",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": "Devices and aids used by the patient prior to the current illness, exacerbation, or injury.",
          "copyrightNotice": null,
          "question": "Prior Device Use",
          "answers": [
            {
              "label": "A",
              "code": "LA18363-4",
              "text": "Manual wheelchair",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "B",
              "code": "LA26730-4",
              "text": "Motorized wheelchair and/or scooter",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "C",
              "code": "LA11549-5",
              "text": "Mechanical lift",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "D",
              "code": "LA10117-2",
              "text": "Walker",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "E",
              "code": "LA10046-3",
              "text": "Orthotics/Prosthetics",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "Z",
              "code": "LA9-3",
              "text": "None of the above",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/89572-2/83234-5",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "83234-5",
              "display": "Prior Device Use",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "89479-0",
          "localQuestionCode": "GG0130_1",
          "dataType": "SECTION",
          "header": true,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Self-Care - SOC/ROC Performance",
          "answers": null,
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": [
            {
              "questionCode": "95019-6",
              "localQuestionCode": "GG0130A1",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": "The patient's usual ability to use suitable utensils to bring food/liquid to the mouth and swallow food once the meal is presented on a table/tray. Includes modified food consistency.",
              "copyrightNotice": null,
              "question": "Eating",
              "answers": [
                {
                  "label": "06",
                  "code": "LA30909-8",
                  "text": "Independent - Person completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA30910-6",
                  "text": "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA30911-4",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA30914-8",
                  "text": "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA30915-5",
                  "text": "Person refused.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "11",
                  "code": "LA30916-3",
                  "text": "Not applicable - Person does not usually do this activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "90",
                  "code": "LA30917-1",
                  "text": "Not attempted due to short-term medical condition or safety concerns.",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89479-0/95019-6",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "95019-6",
                  "display": "Eating",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "95018-8",
              "localQuestionCode": "GG0130B1",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Oral hygiene",
              "answers": [
                {
                  "label": "06",
                  "code": "LA30909-8",
                  "text": "Independent - Person completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA30910-6",
                  "text": "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA30911-4",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA30914-8",
                  "text": "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA30915-5",
                  "text": "Person refused.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "11",
                  "code": "LA30916-3",
                  "text": "Not applicable - Person does not usually do this activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "90",
                  "code": "LA30917-1",
                  "text": "Not attempted due to short-term medical condition or safety concerns.",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89479-0/95018-8",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "95018-8",
                  "display": "Oral hygiene",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "95017-0",
              "localQuestionCode": "GG0130C1",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Toileting hygiene",
              "answers": [
                {
                  "label": "06",
                  "code": "LA9983-3",
                  "text": "Independent - Patient completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA10073-7",
                  "text": "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA28225-3",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA27665-1",
                  "text": "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA10058-8",
                  "text": "Patient refused",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "09",
                  "code": "LA28226-1",
                  "text": "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "10",
                  "code": "LA28227-9",
                  "text": "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "88",
                  "code": "LA26735-3",
                  "text": "Not attempted due to medical condition or safety concerns",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89479-0/95017-0",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "95017-0",
                  "display": "Toileting hygiene",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "95015-4",
              "localQuestionCode": "GG0130E1",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Shower/bathe self",
              "answers": [
                {
                  "label": "06",
                  "code": "LA30909-8",
                  "text": "Independent - Person completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA30910-6",
                  "text": "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA30911-4",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA30914-8",
                  "text": "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA30915-5",
                  "text": "Person refused.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "11",
                  "code": "LA30916-3",
                  "text": "Not applicable - Person does not usually do this activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "90",
                  "code": "LA30917-1",
                  "text": "Not attempted due to short-term medical condition or safety concerns.",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89479-0/95015-4",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "95015-4",
                  "display": "Shower/bathe self",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "95014-7",
              "localQuestionCode": "GG0130F1",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Upper body dressing",
              "answers": [
                {
                  "label": "06",
                  "code": "LA30909-8",
                  "text": "Independent - Person completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA30910-6",
                  "text": "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA30911-4",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA30914-8",
                  "text": "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA30915-5",
                  "text": "Person refused.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "11",
                  "code": "LA30916-3",
                  "text": "Not applicable - Person does not usually do this activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "90",
                  "code": "LA30917-1",
                  "text": "Not attempted due to short-term medical condition or safety concerns.",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89479-0/95014-7",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "95014-7",
                  "display": "Upper body dressing",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "95013-9",
              "localQuestionCode": "GG0130G1",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Lower body dressing",
              "answers": [
                {
                  "label": "06",
                  "code": "LA30909-8",
                  "text": "Independent - Person completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA30910-6",
                  "text": "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA30911-4",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA30914-8",
                  "text": "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA30915-5",
                  "text": "Person refused.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "11",
                  "code": "LA30916-3",
                  "text": "Not applicable - Person does not usually do this activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "90",
                  "code": "LA30917-1",
                  "text": "Not attempted due to short-term medical condition or safety concerns.",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89479-0/95013-9",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "95013-9",
                  "display": "Lower body dressing",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "95012-1",
              "localQuestionCode": "GG0130H1",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Putting on/taking off footwear",
              "answers": [
                {
                  "label": "06",
                  "code": "LA30909-8",
                  "text": "Independent - Person completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA30910-6",
                  "text": "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA30911-4",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA30914-8",
                  "text": "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA30915-5",
                  "text": "Person refused.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "11",
                  "code": "LA30916-3",
                  "text": "Not applicable - Person does not usually do this activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "90",
                  "code": "LA30917-1",
                  "text": "Not attempted due to short-term medical condition or safety concerns.",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89479-0/95012-1",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "95012-1",
                  "display": "Putting on/taking off footwear",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            }
          ],
          "linkId": "/89572-2/89479-0",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "89479-0",
              "display": "Self-Care - SOC/ROC Performance",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": { "questionLayout": "vertical" },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "89478-2",
          "localQuestionCode": "GG0130_2",
          "dataType": "SECTION",
          "header": true,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Self-Care - Discharge Goal",
          "answers": null,
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": [
            {
              "questionCode": "89409-7",
              "localQuestionCode": "GG0130A2",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Eating",
              "answers": [
                {
                  "label": "06",
                  "code": "LA9983-3",
                  "text": "Independent - Patient completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA10073-7",
                  "text": "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA28225-3",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA27665-1",
                  "text": "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA10058-8",
                  "text": "Patient refused",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "09",
                  "code": "LA28226-1",
                  "text": "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "10",
                  "code": "LA28227-9",
                  "text": "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "88",
                  "code": "LA26735-3",
                  "text": "Not attempted due to medical condition or safety concerns",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89478-2/89409-7",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "89409-7",
                  "display": "Eating",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "89404-8",
              "localQuestionCode": "GG0130B2",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Oral hygiene",
              "answers": [
                {
                  "label": "06",
                  "code": "LA9983-3",
                  "text": "Independent - Patient completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA10073-7",
                  "text": "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA28225-3",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA27665-1",
                  "text": "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA10058-8",
                  "text": "Patient refused",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "09",
                  "code": "LA28226-1",
                  "text": "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "10",
                  "code": "LA28227-9",
                  "text": "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "88",
                  "code": "LA26735-3",
                  "text": "Not attempted due to medical condition or safety concerns",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89478-2/89404-8",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "89404-8",
                  "display": "Oral hygiene",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "89389-1",
              "localQuestionCode": "GG0130C2",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Toileting hygiene",
              "answers": [
                {
                  "label": "06",
                  "code": "LA9983-3",
                  "text": "Independent - Patient completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA10073-7",
                  "text": "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA28225-3",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA27665-1",
                  "text": "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA10058-8",
                  "text": "Patient refused",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "09",
                  "code": "LA28226-1",
                  "text": "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "10",
                  "code": "LA28227-9",
                  "text": "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "88",
                  "code": "LA26735-3",
                  "text": "Not attempted due to medical condition or safety concerns",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89478-2/89389-1",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "89389-1",
                  "display": "Toileting hygiene",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "89396-6",
              "localQuestionCode": "GG0130E2",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Shower/bathe self",
              "answers": [
                {
                  "label": "06",
                  "code": "LA9983-3",
                  "text": "Independent - Patient completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA10073-7",
                  "text": "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA28225-3",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA27665-1",
                  "text": "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA10058-8",
                  "text": "Patient refused",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "09",
                  "code": "LA28226-1",
                  "text": "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "10",
                  "code": "LA28227-9",
                  "text": "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "88",
                  "code": "LA26735-3",
                  "text": "Not attempted due to medical condition or safety concerns",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89478-2/89396-6",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "89396-6",
                  "display": "Shower/bathe self",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "89387-5",
              "localQuestionCode": "GG0130F2",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Upper body dressing",
              "answers": [
                {
                  "label": "06",
                  "code": "LA9983-3",
                  "text": "Independent - Patient completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA10073-7",
                  "text": "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA28225-3",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA27665-1",
                  "text": "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA10058-8",
                  "text": "Patient refused",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "09",
                  "code": "LA28226-1",
                  "text": "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "10",
                  "code": "LA28227-9",
                  "text": "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "88",
                  "code": "LA26735-3",
                  "text": "Not attempted due to medical condition or safety concerns",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89478-2/89387-5",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "89387-5",
                  "display": "Upper body dressing",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "89406-3",
              "localQuestionCode": "GG0130G2",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Lower body dressing",
              "answers": [
                {
                  "label": "06",
                  "code": "LA9983-3",
                  "text": "Independent - Patient completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA10073-7",
                  "text": "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA28225-3",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA27665-1",
                  "text": "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA10058-8",
                  "text": "Patient refused",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "09",
                  "code": "LA28226-1",
                  "text": "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "10",
                  "code": "LA28227-9",
                  "text": "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "88",
                  "code": "LA26735-3",
                  "text": "Not attempted due to medical condition or safety concerns",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89478-2/89406-3",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "89406-3",
                  "display": "Lower body dressing",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "89400-6",
              "localQuestionCode": "GG0130H2",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Putting on/taking off footwear",
              "answers": [
                {
                  "label": "06",
                  "code": "LA9983-3",
                  "text": "Independent - Patient completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA10073-7",
                  "text": "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA28225-3",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA27665-1",
                  "text": "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA10058-8",
                  "text": "Patient refused",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "09",
                  "code": "LA28226-1",
                  "text": "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "10",
                  "code": "LA28227-9",
                  "text": "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "88",
                  "code": "LA26735-3",
                  "text": "Not attempted due to medical condition or safety concerns",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89478-2/89400-6",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "89400-6",
                  "display": "Putting on/taking off footwear",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            }
          ],
          "linkId": "/89572-2/89478-2",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "89478-2",
              "display": "Self-Care - Discharge Goal",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": { "questionLayout": "vertical" },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "89477-4",
          "localQuestionCode": "GG0170_1",
          "dataType": "SECTION",
          "header": true,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Mobility - SOC/ROC Performance",
          "answers": null,
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": [
            {
              "questionCode": "95011-3",
              "localQuestionCode": "GG0170A1",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Roll left and right",
              "answers": [
                {
                  "label": "06",
                  "code": "LA30909-8",
                  "text": "Independent - Person completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA30910-6",
                  "text": "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA30911-4",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA30914-8",
                  "text": "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA30915-5",
                  "text": "Person refused.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "11",
                  "code": "LA30916-3",
                  "text": "Not applicable - Person does not usually do this activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "90",
                  "code": "LA30917-1",
                  "text": "Not attempted due to short-term medical condition or safety concerns.",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89477-4/95011-3",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "95011-3",
                  "display": "Roll left and right",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "95010-5",
              "localQuestionCode": "GG0170B1",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Sit to lying",
              "answers": [
                {
                  "label": "06",
                  "code": "LA30909-8",
                  "text": "Independent - Person completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA30910-6",
                  "text": "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA30911-4",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA30914-8",
                  "text": "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA30915-5",
                  "text": "Person refused.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "11",
                  "code": "LA30916-3",
                  "text": "Not applicable - Person does not usually do this activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "90",
                  "code": "LA30917-1",
                  "text": "Not attempted due to short-term medical condition or safety concerns.",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89477-4/95010-5",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "95010-5",
                  "display": "Sit to lying",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "95009-7",
              "localQuestionCode": "GG0170C1",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Lying to sitting on side of bed",
              "answers": [
                {
                  "label": "06",
                  "code": "LA9983-3",
                  "text": "Independent - Patient completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA10073-7",
                  "text": "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA28225-3",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA27665-1",
                  "text": "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA10058-8",
                  "text": "Patient refused",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "09",
                  "code": "LA28226-1",
                  "text": "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "10",
                  "code": "LA28227-9",
                  "text": "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "88",
                  "code": "LA26735-3",
                  "text": "Not attempted due to medical condition or safety concerns",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89477-4/95009-7",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "95009-7",
                  "display": "Lying to sitting on side of bed",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "95008-9",
              "localQuestionCode": "GG0170D1",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Sit to stand",
              "answers": [
                {
                  "label": "06",
                  "code": "LA30909-8",
                  "text": "Independent - Person completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA30910-6",
                  "text": "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA30911-4",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA30914-8",
                  "text": "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA30915-5",
                  "text": "Person refused.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "11",
                  "code": "LA30916-3",
                  "text": "Not applicable - Person does not usually do this activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "90",
                  "code": "LA30917-1",
                  "text": "Not attempted due to short-term medical condition or safety concerns.",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89477-4/95008-9",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "95008-9",
                  "display": "Sit to stand",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "95007-1",
              "localQuestionCode": "GG0170E1",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Chair/bed-to-chair transfer",
              "answers": [
                {
                  "label": "06",
                  "code": "LA30909-8",
                  "text": "Independent - Person completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA30910-6",
                  "text": "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA30911-4",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA30914-8",
                  "text": "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA30915-5",
                  "text": "Person refused.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "11",
                  "code": "LA30916-3",
                  "text": "Not applicable - Person does not usually do this activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "90",
                  "code": "LA30917-1",
                  "text": "Not attempted due to short-term medical condition or safety concerns.",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89477-4/95007-1",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "95007-1",
                  "display": "Chair/bed-to-chair transfer",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "95006-3",
              "localQuestionCode": "GG0170F1",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Toilet transfer",
              "answers": [
                {
                  "label": "06",
                  "code": "LA9983-3",
                  "text": "Independent - Patient completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA10073-7",
                  "text": "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA28225-3",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA27665-1",
                  "text": "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA10058-8",
                  "text": "Patient refused",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "09",
                  "code": "LA28226-1",
                  "text": "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "10",
                  "code": "LA28227-9",
                  "text": "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "88",
                  "code": "LA26735-3",
                  "text": "Not attempted due to medical condition or safety concerns",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89477-4/95006-3",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "95006-3",
                  "display": "Toilet transfer",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "95005-5",
              "localQuestionCode": "GG0170G1",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Car transfer",
              "answers": [
                {
                  "label": "06",
                  "code": "LA30909-8",
                  "text": "Independent - Person completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA30910-6",
                  "text": "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA30911-4",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA30914-8",
                  "text": "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA30915-5",
                  "text": "Person refused.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "11",
                  "code": "LA30916-3",
                  "text": "Not applicable - Person does not usually do this activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "90",
                  "code": "LA30917-1",
                  "text": "Not attempted due to short-term medical condition or safety concerns.",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89477-4/95005-5",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "95005-5",
                  "display": "Car transfer",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "95004-8",
              "localQuestionCode": "GG0170I1",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Walk 10 feet",
              "answers": [
                {
                  "label": "06",
                  "code": "LA30909-8",
                  "text": "Independent - Person completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA30910-6",
                  "text": "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA30911-4",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA30914-8",
                  "text": "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA30915-5",
                  "text": "Person refused.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "11",
                  "code": "LA30916-3",
                  "text": "Not applicable - Person does not usually do this activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "90",
                  "code": "LA30917-1",
                  "text": "Not attempted due to short-term medical condition or safety concerns.",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89477-4/95004-8",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "95004-8",
                  "display": "Walk 10 feet",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "95003-0",
              "localQuestionCode": "GG0170J1",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Walk 50 feet with two turns",
              "answers": [
                {
                  "label": "06",
                  "code": "LA30909-8",
                  "text": "Independent - Person completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA30910-6",
                  "text": "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA30911-4",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA30914-8",
                  "text": "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA30915-5",
                  "text": "Person refused.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "11",
                  "code": "LA30916-3",
                  "text": "Not applicable - Person does not usually do this activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "90",
                  "code": "LA30917-1",
                  "text": "Not attempted due to short-term medical condition or safety concerns.",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89477-4/95003-0",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "95003-0",
                  "display": "Walk 50 feet with two turns",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "95002-2",
              "localQuestionCode": "GG0170K1",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Walk 150 feet",
              "answers": [
                {
                  "label": "06",
                  "code": "LA30909-8",
                  "text": "Independent - Person completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA30910-6",
                  "text": "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA30911-4",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA30914-8",
                  "text": "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA30915-5",
                  "text": "Person refused.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "11",
                  "code": "LA30916-3",
                  "text": "Not applicable - Person does not usually do this activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "90",
                  "code": "LA30917-1",
                  "text": "Not attempted due to short-term medical condition or safety concerns.",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89477-4/95002-2",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "95002-2",
                  "display": "Walk 150 feet",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "95001-4",
              "localQuestionCode": "GG0170L1",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Walking 10 feet on uneven surfaces",
              "answers": [
                {
                  "label": "06",
                  "code": "LA30909-8",
                  "text": "Independent - Person completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA30910-6",
                  "text": "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA30911-4",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA30914-8",
                  "text": "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA30915-5",
                  "text": "Person refused.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "11",
                  "code": "LA30916-3",
                  "text": "Not applicable - Person does not usually do this activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "90",
                  "code": "LA30917-1",
                  "text": "Not attempted due to short-term medical condition or safety concerns.",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89477-4/95001-4",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "95001-4",
                  "display": "Walking 10 feet on uneven surfaces",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "95000-6",
              "localQuestionCode": "GG0170M1",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "1 step (curb)",
              "answers": [
                {
                  "label": "06",
                  "code": "LA30909-8",
                  "text": "Independent - Person completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA30910-6",
                  "text": "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA30911-4",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA30914-8",
                  "text": "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA30915-5",
                  "text": "Person refused.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "11",
                  "code": "LA30916-3",
                  "text": "Not applicable - Person does not usually do this activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "90",
                  "code": "LA30917-1",
                  "text": "Not attempted due to short-term medical condition or safety concerns.",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89477-4/95000-6",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "95000-6",
                  "display": "1 step (curb)",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "94999-0",
              "localQuestionCode": "GG0170N1",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "4 steps",
              "answers": [
                {
                  "label": "06",
                  "code": "LA30909-8",
                  "text": "Independent - Person completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA30910-6",
                  "text": "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA30911-4",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA30914-8",
                  "text": "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA30915-5",
                  "text": "Person refused.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "11",
                  "code": "LA30916-3",
                  "text": "Not applicable - Person does not usually do this activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "90",
                  "code": "LA30917-1",
                  "text": "Not attempted due to short-term medical condition or safety concerns.",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89477-4/94999-0",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "94999-0",
                  "display": "4 steps",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "94998-2",
              "localQuestionCode": "GG0170O1",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "12 steps",
              "answers": [
                {
                  "label": "06",
                  "code": "LA30909-8",
                  "text": "Independent - Person completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA30910-6",
                  "text": "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA30911-4",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA30914-8",
                  "text": "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA30915-5",
                  "text": "Person refused.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "11",
                  "code": "LA30916-3",
                  "text": "Not applicable - Person does not usually do this activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "90",
                  "code": "LA30917-1",
                  "text": "Not attempted due to short-term medical condition or safety concerns.",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89477-4/94998-2",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "94998-2",
                  "display": "12 steps",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "94997-4",
              "localQuestionCode": "GG0170P1",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Picking up object",
              "answers": [
                {
                  "label": "06",
                  "code": "LA30909-8",
                  "text": "Independent - Person completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA30910-6",
                  "text": "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA30911-4",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA30914-8",
                  "text": "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA30915-5",
                  "text": "Person refused.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "11",
                  "code": "LA30916-3",
                  "text": "Not applicable - Person does not usually do this activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "90",
                  "code": "LA30917-1",
                  "text": "Not attempted due to short-term medical condition or safety concerns.",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89477-4/94997-4",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "94997-4",
                  "display": "Picking up object",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "95738-1",
              "localQuestionCode": "GG0170Q1",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Does the patient use a wheelchair and/or scooter?",
              "answers": [
                {
                  "label": "0",
                  "code": "LA32-8",
                  "text": "No",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "1",
                  "code": "LA33-6",
                  "text": "Yes",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89477-4/95738-1",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "95738-1",
                  "display": "Does the patient use a wheelchair and/or scooter?",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "94992-5",
              "localQuestionCode": "GG0170R1",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Wheel 50 feet with two turns",
              "answers": [
                {
                  "label": "06",
                  "code": "LA30909-8",
                  "text": "Independent - Person completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA30910-6",
                  "text": "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA30911-4",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA30914-8",
                  "text": "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA30915-5",
                  "text": "Person refused.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "11",
                  "code": "LA30916-3",
                  "text": "Not applicable - Person does not usually do this activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "90",
                  "code": "LA30917-1",
                  "text": "Not attempted due to short-term medical condition or safety concerns.",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89477-4/94992-5",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "94992-5",
                  "display": "Wheel 50 feet with two turns",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "95739-9",
              "localQuestionCode": "GG0170RR1",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Indicate the type of wheelchair or scooter used",
              "answers": [
                {
                  "label": "1",
                  "code": "LA19016-7",
                  "text": "Manual",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "2",
                  "code": "LA26847-6",
                  "text": "Motorized",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89477-4/95739-9",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "95739-9",
                  "display": "Indicate the type of wheelchair or scooter used",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "94991-7",
              "localQuestionCode": "GG0170S1",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Wheel 150 feet",
              "answers": [
                {
                  "label": "06",
                  "code": "LA30909-8",
                  "text": "Independent - Person completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA30910-6",
                  "text": "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA30911-4",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA30914-8",
                  "text": "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA30915-5",
                  "text": "Person refused.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "11",
                  "code": "LA30916-3",
                  "text": "Not applicable - Person does not usually do this activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "90",
                  "code": "LA30917-1",
                  "text": "Not attempted due to short-term medical condition or safety concerns.",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89477-4/94991-7",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "94991-7",
                  "display": "Wheel 150 feet",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "95739-9",
              "localQuestionCode": "GG0170SS1",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Indicate the type of wheelchair or scooter used",
              "answers": [
                {
                  "label": "1",
                  "code": "LA19016-7",
                  "text": "Manual",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "2",
                  "code": "LA26847-6",
                  "text": "Motorized",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89477-4/95739-9",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "95739-9",
                  "display": "Indicate the type of wheelchair or scooter used",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            }
          ],
          "linkId": "/89572-2/89477-4",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "89477-4",
              "display": "Mobility - SOC/ROC Performance",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": { "questionLayout": "vertical" },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "89476-6",
          "localQuestionCode": "GG0170_2",
          "dataType": "SECTION",
          "header": true,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Mobility - Discharge Goal",
          "answers": null,
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": [
            {
              "questionCode": "89398-2",
              "localQuestionCode": "GG0170A2",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Roll left and right",
              "answers": [
                {
                  "label": "06",
                  "code": "LA9983-3",
                  "text": "Independent - Patient completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA10073-7",
                  "text": "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA28225-3",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA27665-1",
                  "text": "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA10058-8",
                  "text": "Patient refused",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "09",
                  "code": "LA28226-1",
                  "text": "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "10",
                  "code": "LA28227-9",
                  "text": "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "88",
                  "code": "LA26735-3",
                  "text": "Not attempted due to medical condition or safety concerns",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89476-6/89398-2",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "89398-2",
                  "display": "Roll left and right",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "89394-1",
              "localQuestionCode": "GG0170B2",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Sit to lying",
              "answers": [
                {
                  "label": "06",
                  "code": "LA9983-3",
                  "text": "Independent - Patient completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA10073-7",
                  "text": "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA28225-3",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA27665-1",
                  "text": "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA10058-8",
                  "text": "Patient refused",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "09",
                  "code": "LA28226-1",
                  "text": "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "10",
                  "code": "LA28227-9",
                  "text": "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "88",
                  "code": "LA26735-3",
                  "text": "Not attempted due to medical condition or safety concerns",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89476-6/89394-1",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "89394-1",
                  "display": "Sit to lying",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "85927-2",
              "localQuestionCode": "GG0170C2",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": "Expected functional performance for the patient's usual ability to move from lying on the back to sitting on the side of the bed with feet flat on the floor, and with no back support.",
              "copyrightNotice": null,
              "question": "Lying to sitting on side of bed",
              "answers": [
                {
                  "label": "06",
                  "code": "LA9983-3",
                  "text": "Independent - Patient completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA10073-7",
                  "text": "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA28225-3",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA27665-1",
                  "text": "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA10058-8",
                  "text": "Patient refused",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "09",
                  "code": "LA28226-1",
                  "text": "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "10",
                  "code": "LA28227-9",
                  "text": "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "88",
                  "code": "LA26735-3",
                  "text": "Not attempted due to medical condition or safety concerns",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89476-6/85927-2",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "85927-2",
                  "display": "Lying to sitting on side of bed",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "89392-5",
              "localQuestionCode": "GG0170D2",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Sit to stand",
              "answers": [
                {
                  "label": "06",
                  "code": "LA9983-3",
                  "text": "Independent - Patient completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA10073-7",
                  "text": "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA28225-3",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA27665-1",
                  "text": "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA10058-8",
                  "text": "Patient refused",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "09",
                  "code": "LA28226-1",
                  "text": "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "10",
                  "code": "LA28227-9",
                  "text": "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "88",
                  "code": "LA26735-3",
                  "text": "Not attempted due to medical condition or safety concerns",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89476-6/89392-5",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "89392-5",
                  "display": "Sit to stand",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "89414-7",
              "localQuestionCode": "GG0170E2",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Chair/bed-to-chair transfer",
              "answers": [
                {
                  "label": "06",
                  "code": "LA9983-3",
                  "text": "Independent - Patient completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA10073-7",
                  "text": "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA28225-3",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA27665-1",
                  "text": "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA10058-8",
                  "text": "Patient refused",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "09",
                  "code": "LA28226-1",
                  "text": "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "10",
                  "code": "LA28227-9",
                  "text": "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "88",
                  "code": "LA26735-3",
                  "text": "Not attempted due to medical condition or safety concerns",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89476-6/89414-7",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "89414-7",
                  "display": "Chair/bed-to-chair transfer",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "89390-9",
              "localQuestionCode": "GG0170F2",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Toilet transfer",
              "answers": [
                {
                  "label": "06",
                  "code": "LA9983-3",
                  "text": "Independent - Patient completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA10073-7",
                  "text": "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA28225-3",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA27665-1",
                  "text": "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA10058-8",
                  "text": "Patient refused",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "09",
                  "code": "LA28226-1",
                  "text": "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "10",
                  "code": "LA28227-9",
                  "text": "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "88",
                  "code": "LA26735-3",
                  "text": "Not attempted due to medical condition or safety concerns",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89476-6/89390-9",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "89390-9",
                  "display": "Toilet transfer",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "89412-1",
              "localQuestionCode": "GG0170G2",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Car transfer",
              "answers": [
                {
                  "label": "06",
                  "code": "LA9983-3",
                  "text": "Independent - Patient completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA10073-7",
                  "text": "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA28225-3",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA27665-1",
                  "text": "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA10058-8",
                  "text": "Patient refused",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "09",
                  "code": "LA28226-1",
                  "text": "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "10",
                  "code": "LA28227-9",
                  "text": "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "88",
                  "code": "LA26735-3",
                  "text": "Not attempted due to medical condition or safety concerns",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89476-6/89412-1",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "89412-1",
                  "display": "Car transfer",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "89385-9",
              "localQuestionCode": "GG0170I2",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Walk 10 feet",
              "answers": [
                {
                  "label": "06",
                  "code": "LA9983-3",
                  "text": "Independent - Patient completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA10073-7",
                  "text": "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA28225-3",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA27665-1",
                  "text": "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA10058-8",
                  "text": "Patient refused",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "09",
                  "code": "LA28226-1",
                  "text": "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "10",
                  "code": "LA28227-9",
                  "text": "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "88",
                  "code": "LA26735-3",
                  "text": "Not attempted due to medical condition or safety concerns",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89476-6/89385-9",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "89385-9",
                  "display": "Walk 10 feet",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "89381-8",
              "localQuestionCode": "GG0170J2",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Walk 50 feet with two turns",
              "answers": [
                {
                  "label": "06",
                  "code": "LA9983-3",
                  "text": "Independent - Patient completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA10073-7",
                  "text": "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA28225-3",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA27665-1",
                  "text": "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA10058-8",
                  "text": "Patient refused",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "09",
                  "code": "LA28226-1",
                  "text": "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "10",
                  "code": "LA28227-9",
                  "text": "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "88",
                  "code": "LA26735-3",
                  "text": "Not attempted due to medical condition or safety concerns",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89476-6/89381-8",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "89381-8",
                  "display": "Walk 50 feet with two turns",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "89383-4",
              "localQuestionCode": "GG0170K2",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Walk 150 feet",
              "answers": [
                {
                  "label": "06",
                  "code": "LA9983-3",
                  "text": "Independent - Patient completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA10073-7",
                  "text": "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA28225-3",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA27665-1",
                  "text": "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA10058-8",
                  "text": "Patient refused",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "09",
                  "code": "LA28226-1",
                  "text": "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "10",
                  "code": "LA28227-9",
                  "text": "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "88",
                  "code": "LA26735-3",
                  "text": "Not attempted due to medical condition or safety concerns",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89476-6/89383-4",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "89383-4",
                  "display": "Walk 150 feet",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "89379-2",
              "localQuestionCode": "GG0170L2",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Walking 10 feet on uneven surfaces",
              "answers": [
                {
                  "label": "06",
                  "code": "LA9983-3",
                  "text": "Independent - Patient completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA10073-7",
                  "text": "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA28225-3",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA27665-1",
                  "text": "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA10058-8",
                  "text": "Patient refused",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "09",
                  "code": "LA28226-1",
                  "text": "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "10",
                  "code": "LA28227-9",
                  "text": "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "88",
                  "code": "LA26735-3",
                  "text": "Not attempted due to medical condition or safety concerns",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89476-6/89379-2",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "89379-2",
                  "display": "Walking 10 feet on uneven surfaces",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "89420-4",
              "localQuestionCode": "GG0170M2",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "1 step (curb)",
              "answers": [
                {
                  "label": "06",
                  "code": "LA9983-3",
                  "text": "Independent - Patient completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA10073-7",
                  "text": "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA28225-3",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA27665-1",
                  "text": "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA10058-8",
                  "text": "Patient refused",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "09",
                  "code": "LA28226-1",
                  "text": "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "10",
                  "code": "LA28227-9",
                  "text": "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "88",
                  "code": "LA26735-3",
                  "text": "Not attempted due to medical condition or safety concerns",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89476-6/89420-4",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "89420-4",
                  "display": "1 step (curb)",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "89416-2",
              "localQuestionCode": "GG0170N2",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "4 steps",
              "answers": [
                {
                  "label": "06",
                  "code": "LA9983-3",
                  "text": "Independent - Patient completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA10073-7",
                  "text": "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA28225-3",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA27665-1",
                  "text": "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA10058-8",
                  "text": "Patient refused",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "09",
                  "code": "LA28226-1",
                  "text": "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "10",
                  "code": "LA28227-9",
                  "text": "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "88",
                  "code": "LA26735-3",
                  "text": "Not attempted due to medical condition or safety concerns",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89476-6/89416-2",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "89416-2",
                  "display": "4 steps",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "89418-8",
              "localQuestionCode": "GG0170O2",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "12 steps",
              "answers": [
                {
                  "label": "06",
                  "code": "LA9983-3",
                  "text": "Independent - Patient completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA10073-7",
                  "text": "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA28225-3",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA27665-1",
                  "text": "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA10058-8",
                  "text": "Patient refused",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "09",
                  "code": "LA28226-1",
                  "text": "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "10",
                  "code": "LA28227-9",
                  "text": "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "88",
                  "code": "LA26735-3",
                  "text": "Not attempted due to medical condition or safety concerns",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89476-6/89418-8",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "89418-8",
                  "display": "12 steps",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "89402-2",
              "localQuestionCode": "GG0170P2",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Picking up object",
              "answers": [
                {
                  "label": "06",
                  "code": "LA9983-3",
                  "text": "Independent - Patient completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA10073-7",
                  "text": "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA28225-3",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA27665-1",
                  "text": "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA10058-8",
                  "text": "Patient refused",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "09",
                  "code": "LA28226-1",
                  "text": "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "10",
                  "code": "LA28227-9",
                  "text": "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "88",
                  "code": "LA26735-3",
                  "text": "Not attempted due to medical condition or safety concerns",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89476-6/89402-2",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "89402-2",
                  "display": "Picking up object",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "89375-0",
              "localQuestionCode": "GG0170R2",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Wheel 50 feet with two turns",
              "answers": [
                {
                  "label": "06",
                  "code": "LA9983-3",
                  "text": "Independent - Patient completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA10073-7",
                  "text": "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA28225-3",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA27665-1",
                  "text": "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA10058-8",
                  "text": "Patient refused",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "09",
                  "code": "LA28226-1",
                  "text": "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "10",
                  "code": "LA28227-9",
                  "text": "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "88",
                  "code": "LA26735-3",
                  "text": "Not attempted due to medical condition or safety concerns",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89476-6/89375-0",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "89375-0",
                  "display": "Wheel 50 feet with two turns",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "89377-6",
              "localQuestionCode": "GG0170S2",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Wheel 150 feet",
              "answers": [
                {
                  "label": "06",
                  "code": "LA9983-3",
                  "text": "Independent - Patient completes the activity by themself with no assistance from a helper.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "05",
                  "code": "LA10073-7",
                  "text": "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "04",
                  "code": "LA28225-3",
                  "text": "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "03",
                  "code": "LA10055-4",
                  "text": "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "02",
                  "code": "LA11759-0",
                  "text": "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "01",
                  "code": "LA27665-1",
                  "text": "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "07",
                  "code": "LA10058-8",
                  "text": "Patient refused",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "09",
                  "code": "LA28226-1",
                  "text": "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "10",
                  "code": "LA28227-9",
                  "text": "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "88",
                  "code": "LA26735-3",
                  "text": "Not attempted due to medical condition or safety concerns",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/89572-2/89476-6/89377-6",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "89377-6",
                  "display": "Wheel 150 feet",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            }
          ],
          "linkId": "/89572-2/89476-6",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "89476-6",
              "display": "Mobility - Discharge Goal",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": { "questionLayout": "vertical" },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        }
      ],
      "linkId": "/89572-2",
      "questionCodeSystem": "http://loinc.org",
      "codeList": [
        {
          "code": "89572-2",
          "display": "Functional Abilities and Goals",
          "system": "http://loinc.org"
        }
      ],
      "displayControl": { "questionLayout": "vertical" },
      "questionCardinality": { "min": "1", "max": "1" },
      "answerCardinality": { "min": "0", "max": "1" }
    },
    {
      "questionCode": "88496-5",
      "localQuestionCode": "H",
      "dataType": "SECTION",
      "header": true,
      "units": null,
      "codingInstructions": null,
      "copyrightNotice": null,
      "question": "Bladder and Bowel",
      "answers": null,
      "skipLogic": null,
      "restrictions": null,
      "defaultAnswer": null,
      "formatting": null,
      "calculationMethod": null,
      "items": [
        {
          "questionCode": "46552-6",
          "localQuestionCode": "M1600",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": "Identifies treatment of urinary tract infection during the past 14 days.",
          "copyrightNotice": null,
          "question": "Has this patient been treated for a Urinary Tract Infection in the past 14 days?",
          "answers": [
            {
              "label": "0",
              "code": "LA32-8",
              "text": "No",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA33-6",
              "text": "Yes",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "NA",
              "code": "LA6337-5",
              "text": "Patient on prophylactic treatment",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "UK",
              "code": "LA4489-6",
              "text": "Unknown",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/88496-5/46552-6",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "46552-6",
              "display": "Has this patient been treated for a Urinary Tract Infection in the past 14 days?",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "46553-4",
          "localQuestionCode": "M1610",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": "Identifies presence of urinary incontinence or condition that requires urinary catheterization of any type, including intermittent or indwelling.",
          "copyrightNotice": null,
          "question": "Urinary Incontinence or Urinary Catheter Presence",
          "answers": [
            {
              "label": "0",
              "code": "LA6278-1",
              "text": "No incontinence or catheter (includes anuria or ostomy for urinary drainage)",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA6332-6",
              "text": "Patient is incontinent",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA6339-1",
              "text": "Patient requires a urinary catheter (specifically: external, indwelling, intermittent, or suprapubic)",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/88496-5/46553-4",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "46553-4",
              "display": "Urinary Incontinence or Urinary Catheter Presence",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "46587-2",
          "localQuestionCode": "M1620",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": "Identifies how often the patient experiences bowel incontinence.",
          "copyrightNotice": null,
          "question": "Bowel Incontinence Frequency",
          "answers": [
            {
              "label": "0",
              "code": "LA6440-7",
              "text": "Very rarely or never has bowel incontinence",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA6252-6",
              "text": "Less than once weekly",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA6307-8",
              "text": "One to three times weekly",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA6201-3",
              "text": "Four to six times weekly",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "4",
              "code": "LA6302-9",
              "text": "On a daily basis",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "5",
              "code": "LA6263-3",
              "text": "More often than once daily",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "NA",
              "code": "LA6330-0",
              "text": "Patient has ostomy for bowel elimination",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "UK",
              "code": "LA4489-6",
              "text": "Unknown",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/88496-5/46587-2",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "46587-2",
              "display": "Bowel Incontinence Frequency",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "86471-0",
          "localQuestionCode": "M1630",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Ostomy for Bowel Elimination: Does this patient have an ostomy for bowel elimination that (within the last 14 days): a) was related to an inpatient facility stay; or b) necessitated a change in medical or treatment regimen?",
          "answers": [
            {
              "label": "0",
              "code": "LA6328-4",
              "text": "Patient does not have an ostomy for bowel elimination.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA6343-3",
              "text": "Patient's ostomy was not related to an inpatient stay and did not necessitate change in medical or treatment regimen.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA6392-0",
              "text": "The ostomy was related to an inpatient stay or did necessitate change in medical or treatment regimen.",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/88496-5/86471-0",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "86471-0",
              "display": "Ostomy for Bowel Elimination: Does this patient have an ostomy for bowel elimination that (within the last 14 days): a) was related to an inpatient facility stay; or b) necessitated a change in medical or treatment regimen?",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        }
      ],
      "linkId": "/88496-5",
      "questionCodeSystem": "http://loinc.org",
      "codeList": [
        {
          "code": "88496-5",
          "display": "Bladder and Bowel",
          "system": "http://loinc.org"
        }
      ],
      "displayControl": { "questionLayout": "vertical" },
      "questionCardinality": { "min": "1", "max": "1" },
      "answerCardinality": { "min": "0", "max": "1" }
    },
    {
      "questionCode": "99146-3",
      "localQuestionCode": "I",
      "dataType": "SECTION",
      "header": true,
      "units": null,
      "codingInstructions": null,
      "copyrightNotice": null,
      "question": "Active Diagnoses",
      "answers": null,
      "skipLogic": null,
      "restrictions": null,
      "defaultAnswer": null,
      "formatting": null,
      "calculationMethod": null,
      "items": [
        {
          "questionCode": "83243-6",
          "localQuestionCode": "M1028",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Active Diagnoses-Comorbidities and Co-existing Conditions",
          "answers": [
            {
              "label": "1",
              "code": "LA18399-8",
              "text": "Peripheral vascular disease (PVD) or peripheral arterial disease (PAD)",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA27539-8",
              "text": "Diabetes mellitus (DM)",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA9-3",
              "text": "None of the above",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99146-3/83243-6",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "83243-6",
              "display": "Active Diagnoses-Comorbidities and Co-existing Conditions",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "88488-2",
          "localQuestionCode": "M1021, M1023",
          "dataType": "SECTION",
          "header": true,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Primary Diagnosis & Other Diagnoses",
          "answers": null,
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": [
            {
              "questionCode": "88489-0",
              "localQuestionCode": "M1021",
              "dataType": "SECTION",
              "header": true,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Primary Diagnosis",
              "answers": null,
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": [
                {
                  "questionCode": "86255-7",
                  "localQuestionCode": "M1021_A2_ICD",
                  "dataType": "CNE",
                  "header": false,
                  "units": null,
                  "codingInstructions": "The condition that is the chief reason for providing care.",
                  "copyrightNotice": null,
                  "question": "Primary Diagnosis: ICD-10-code",
                  "answers": [
                    {
                      "label": null,
                      "code": null,
                      "text": null,
                      "other": null,
                      "system": "http://loinc.org"
                    }
                  ],
                  "skipLogic": null,
                  "restrictions": null,
                  "defaultAnswer": null,
                  "formatting": null,
                  "calculationMethod": null,
                  "items": null,
                  "linkId": "/99146-3/88488-2/88489-0/86255-7",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "86255-7",
                      "display": "Primary Diagnosis: ICD-10-code",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "85920-7",
                  "localQuestionCode": "M1021_A2_Severity",
                  "dataType": "CNE",
                  "header": false,
                  "units": null,
                  "codingInstructions": "Assessment of the degree of symptom control includes review of presenting signs and symptoms, type and number of medications, frequency of treatment readjustments, and frequency of contact with health care provider, the degree to which each condition limits daily activities, and if symptoms are controlled by current treatments.",
                  "copyrightNotice": null,
                  "question": "Primary Diagnosis Symptom Control Rating",
                  "answers": [
                    {
                      "label": "0",
                      "code": "LA27597-6",
                      "text": "Asymptomatic, no treatment needed at this time",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "1",
                      "code": "LA27598-4",
                      "text": "Symptoms well controlled with current therapy",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "2",
                      "code": "LA27599-2",
                      "text": "Symptoms controlled with difficulty, affecting daily functioning; patient needs ongoing monitoring",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "3",
                      "code": "LA27600-8",
                      "text": "Symptoms poorly controlled; patient needs frequent adjustment in treatment and dose monitoring",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "4",
                      "code": "LA27601-6",
                      "text": "Symptoms poorly controlled; history of re-hospitalizations",
                      "other": null,
                      "system": "http://loinc.org"
                    }
                  ],
                  "skipLogic": null,
                  "restrictions": null,
                  "defaultAnswer": null,
                  "formatting": null,
                  "calculationMethod": null,
                  "items": null,
                  "linkId": "/99146-3/88488-2/88489-0/85920-7",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "85920-7",
                      "display": "Primary Diagnosis Symptom Control Rating",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                }
              ],
              "linkId": "/99146-3/88488-2/88489-0",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "88489-0",
                  "display": "Primary Diagnosis",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": { "questionLayout": "vertical" },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "88490-8",
              "localQuestionCode": "M1023",
              "dataType": "SECTION",
              "header": true,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Other Diagnoses",
              "answers": null,
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": [
                {
                  "questionCode": "81885-6",
                  "localQuestionCode": "M1023_B2_ICD-M1023_F2_ICD",
                  "dataType": "ST",
                  "header": false,
                  "units": null,
                  "codingInstructions": null,
                  "copyrightNotice": null,
                  "question": "Other Diagnoses: ICD-10-CM",
                  "answers": null,
                  "skipLogic": null,
                  "restrictions": null,
                  "defaultAnswer": null,
                  "formatting": null,
                  "calculationMethod": null,
                  "items": null,
                  "linkId": "/99146-3/88488-2/88490-8/81885-6",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "81885-6",
                      "display": "Other Diagnoses: ICD-10-CM",
                      "system": "http://loinc.org"
                    }
                  ],
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "85920-7",
                  "localQuestionCode": "M1023_B2_Severity - M1023_F2_Severity",
                  "dataType": "CNE",
                  "header": false,
                  "units": null,
                  "codingInstructions": "Assessment of the degree of symptom control includes review of presenting signs and symptoms, type and number of medications, frequency of treatment readjustments, and frequency of contact with health care provider, the degree to which each condition limits daily activities, and if symptoms are controlled by current treatments.",
                  "copyrightNotice": null,
                  "question": "Other Diagnoses Symptom Control Rating",
                  "answers": [
                    {
                      "label": "0",
                      "code": "LA27597-6",
                      "text": "Asymptomatic, no treatment needed at this time",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "1",
                      "code": "LA27598-4",
                      "text": "Symptoms well controlled with current therapy",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "2",
                      "code": "LA27599-2",
                      "text": "Symptoms controlled with difficulty, affecting daily functioning; patient needs ongoing monitoring",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "3",
                      "code": "LA27600-8",
                      "text": "Symptoms poorly controlled; patient needs frequent adjustment in treatment and dose monitoring",
                      "other": null,
                      "system": "http://loinc.org"
                    },
                    {
                      "label": "4",
                      "code": "LA27601-6",
                      "text": "Symptoms poorly controlled; history of re-hospitalizations",
                      "other": null,
                      "system": "http://loinc.org"
                    }
                  ],
                  "skipLogic": null,
                  "restrictions": null,
                  "defaultAnswer": null,
                  "formatting": null,
                  "calculationMethod": null,
                  "items": null,
                  "linkId": "/99146-3/88488-2/88490-8/85920-7",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "85920-7",
                      "display": "Other Diagnoses Symptom Control Rating",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                }
              ],
              "linkId": "/99146-3/88488-2/88490-8",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "88490-8",
                  "display": "Other Diagnoses",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": { "questionLayout": "vertical" },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            }
          ],
          "linkId": "/99146-3/88488-2",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "88488-2",
              "display": "Primary Diagnosis & Other Diagnoses",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": { "questionLayout": "vertical" },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        }
      ],
      "linkId": "/99146-3",
      "questionCodeSystem": "http://loinc.org",
      "codeList": [
        {
          "code": "99146-3",
          "display": "Active Diagnoses",
          "system": "http://loinc.org"
        }
      ],
      "displayControl": { "questionLayout": "vertical" },
      "questionCardinality": { "min": "1", "max": "1" },
      "answerCardinality": { "min": "0", "max": "1" }
    },
    {
      "questionCode": "99142-2",
      "localQuestionCode": "J",
      "dataType": "SECTION",
      "header": true,
      "units": null,
      "codingInstructions": null,
      "copyrightNotice": null,
      "question": "Health Conditions",
      "answers": null,
      "skipLogic": null,
      "restrictions": null,
      "defaultAnswer": null,
      "formatting": null,
      "calculationMethod": null,
      "items": [
        {
          "questionCode": "57319-6",
          "localQuestionCode": "M1033",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Risk for Hospitalization: Which of the following signs or symptoms characterize this patient as at risk for hospitalization?",
          "answers": [
            {
              "label": "1",
              "code": "LA27614-9",
              "text": "History of falls (2 or more falls - or any fall with an injury - in the past 12 months)",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA27615-6",
              "text": "Unintentional weight loss of a total of 10 pounds or more in the past 12 months",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA27616-4",
              "text": "Multiple hospitalizations (2 or more) in the past 6 months",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "4",
              "code": "LA27617-2",
              "text": "Multiple emergency department visits (2 or more) in the past 6 months",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "5",
              "code": "LA27618-0",
              "text": "Decline in mental, emotional, or behavioral status in the past 3 months",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "6",
              "code": "LA27619-8",
              "text": "Reported or observed history of difficulty complying with any medical instructions (for example, medications, diet, exercise) in the past 3 months",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "7",
              "code": "LA27620-6",
              "text": "Currently taking 5 or more medications",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "8",
              "code": "LA27621-4",
              "text": "Currently reports exhaustion",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "9",
              "code": "LA27622-2",
              "text": "Other risk(s) not listed in 1 - 8",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "10",
              "code": "LA9-3",
              "text": "None of the above",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99142-2/57319-6",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "57319-6",
              "display": "Risk for Hospitalization: Which of the following signs or symptoms characterize this patient as at risk for hospitalization?",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "93156-8",
          "localQuestionCode": "J0510",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Pain Effect on Sleep. Over the past 5 days, how much of the time has pain made it hard for you to sleep at night?",
          "answers": [
            {
              "label": "0",
              "code": "LA30272-1",
              "text": "Does not apply - I have not had any pain or hurting in the past 5 days",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA30273-9",
              "text": "Rarely or not at all",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA6483-7",
              "text": "Occasionally",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA6482-9",
              "text": "Frequently",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "4",
              "code": "LA11055-3",
              "text": "Almost constantly",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "8",
              "code": "LA11054-6",
              "text": "Unable to answer",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99142-2/93156-8",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "93156-8",
              "display": "Pain Effect on Sleep. Over the past 5 days, how much of the time has pain made it hard for you to sleep at night?",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "93160-0",
          "localQuestionCode": "J0520",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Pain Interference with Therapy Activities. Over the past 5 days, how often have you limited your participation in rehabilitation therapy sessions due to pain?",
          "answers": [
            {
              "label": "0",
              "code": "LA30274-7",
              "text": "Does not apply - I have not received rehabilitation therapy in the past 5 days",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA30273-9",
              "text": "Rarely or not at all",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA6483-7",
              "text": "Occasionally",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA6482-9",
              "text": "Frequently",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "4",
              "code": "LA11055-3",
              "text": "Almost constantly",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "8",
              "code": "LA11054-6",
              "text": "Unable to answer",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99142-2/93160-0",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "93160-0",
              "display": "Pain Interference with Therapy Activities. Over the past 5 days, how often have you limited your participation in rehabilitation therapy sessions due to pain?",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "93158-4",
          "localQuestionCode": "J0530",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Pain Interference with Day-to-Day Activities. Over the past 5 days, how often have you limited your day-to-day activities (excluding rehabilitation therapy sessions) because of pain?",
          "answers": [
            {
              "label": "0",
              "code": "LA30274-7",
              "text": "Does not apply - I have not received rehabilitation therapy in the past 5 days",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA30273-9",
              "text": "Rarely or not at all",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA6483-7",
              "text": "Occasionally",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA6482-9",
              "text": "Frequently",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "4",
              "code": "LA11055-3",
              "text": "Almost constantly",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "8",
              "code": "LA11054-6",
              "text": "Unable to answer",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99142-2/93158-4",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "93158-4",
              "display": "Pain Interference with Day-to-Day Activities. Over the past 5 days, how often have you limited your day-to-day activities (excluding rehabilitation therapy sessions) because of pain?",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "57237-0",
          "localQuestionCode": "M1400",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "When is the patient dyspneic or noticeably Short of Breath?",
          "answers": [
            {
              "label": "0",
              "code": "LA12224-4",
              "text": "Patient is not short of breath",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA6443-1",
              "text": "When walking more than 20 feet, climbing stairs",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA6446-4",
              "text": "With moderate exertion (for example, while dressing, using commode or bedpan, walking distances less than 20 feet)",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA6445-6",
              "text": "With minimal exertion (for example, while eating, talking, or performing other ADLs) or with agitation",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "4",
              "code": "LA6158-5",
              "text": "At rest (during day or night)",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99142-2/57237-0",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "57237-0",
              "display": "When is the patient dyspneic or noticeably Short of Breath?",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        }
      ],
      "linkId": "/99142-2",
      "questionCodeSystem": "http://loinc.org",
      "codeList": [
        {
          "code": "99142-2",
          "display": "Health Conditions",
          "system": "http://loinc.org"
        }
      ],
      "displayControl": { "questionLayout": "vertical" },
      "questionCardinality": { "min": "1", "max": "1" },
      "answerCardinality": { "min": "0", "max": "1" }
    },
    {
      "questionCode": "99152-1",
      "localQuestionCode": "K",
      "dataType": "SECTION",
      "header": true,
      "units": null,
      "codingInstructions": null,
      "copyrightNotice": null,
      "question": "Swallowing/Nutritional Status",
      "answers": null,
      "skipLogic": null,
      "restrictions": null,
      "defaultAnswer": null,
      "formatting": null,
      "calculationMethod": null,
      "items": [
        {
          "questionCode": "54567-3",
          "localQuestionCode": "M1060",
          "dataType": "SECTION",
          "header": true,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Height and Weight:  - While measuring, if the number is X.1-X.4 round down; X.5 or greater round up.",
          "answers": null,
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": [
            {
              "questionCode": "3137-7",
              "localQuestionCode": "M1060a",
              "dataType": "QTY",
              "header": false,
              "units": [
                {
                  "name": "[in_us]",
                  "code": "[in_us]",
                  "system": "http://unitsofmeasure.org",
                  "default": false
                },
                {
                  "name": "cm",
                  "code": "cm",
                  "system": "http://unitsofmeasure.org",
                  "default": false
                },
                {
                  "name": "m",
                  "code": "m",
                  "system": "http://unitsofmeasure.org",
                  "default": false
                }
              ],
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Height (in inches)",
              "answers": null,
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/99152-1/54567-3/3137-7",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "3137-7",
                  "display": "Height (in inches)",
                  "system": "http://loinc.org"
                }
              ],
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "3141-9",
              "localQuestionCode": "M1060b",
              "dataType": "QTY",
              "header": false,
              "units": [
                {
                  "name": "[lb_av]",
                  "code": "[lb_av]",
                  "system": "http://unitsofmeasure.org",
                  "default": false
                },
                {
                  "name": "kg",
                  "code": "kg",
                  "system": "http://unitsofmeasure.org",
                  "default": false
                }
              ],
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Weight (in pounds)",
              "answers": null,
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/99152-1/54567-3/3141-9",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "3141-9",
                  "display": "Weight (in pounds)",
                  "system": "http://loinc.org"
                }
              ],
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            }
          ],
          "linkId": "/99152-1/54567-3",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "54567-3",
              "display": "Height and Weight:  - While measuring, if the number is X.1-X.4 round down; X.5 or greater round up.",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": { "questionLayout": "vertical" },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "93178-2",
          "localQuestionCode": "K0520_1",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Nutritional Approaches - On Admission. Check all of the following nutritional approaches that apply on admission.",
          "answers": [
            {
              "label": "A",
              "code": "LA18604-1",
              "text": "Parenteral/IV feeding",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "B",
              "code": "LA30294-5",
              "text": "Feeding tube (e.g., nasogastric or abdominal (PEG))",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "C",
              "code": "LA18606-6",
              "text": "Mechanically altered diet - require change in texture of food or liquids (e.g., pureed food, thickened liquids)",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "D",
              "code": "LA18607-4",
              "text": "Therapeutic diet (e.g. low salt, diabetic, low cholesterol)",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "Z",
              "code": "LA9-3",
              "text": "None of the above",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99152-1/93178-2",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "93178-2",
              "display": "Nutritional Approaches - On Admission. Check all of the following nutritional approaches that apply on admission.",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "57248-7",
          "localQuestionCode": "M1870",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Feeding or Eating: Current ability to feed self meals and snacks safely.",
          "answers": [
            {
              "label": "0",
              "code": "LA6133-8",
              "text": "Able to independently feed self.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA12294-7",
              "text": "Able to feed self independently but requires: (a) meal set-up; OR (b) intermittent assistance or supervision from another person; OR (c) a liquid, pureed or ground meat diet.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA6414-2",
              "text": "Unable to feed self and must be assisted or supervised throughout the meal/snack.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA6142-9",
              "text": "Able to take in nutrients orally AND receives supplemental nutrients through a nasogastric tube or gastrostomy.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "4",
              "code": "LA6422-5",
              "text": "Unable to take in nutrients orally and is fed nutrients through a nasogastric tube or gastrostomy.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "5",
              "code": "LA6423-3",
              "text": "Unable to take in nutrients orally or by tube feeding.",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99152-1/57248-7",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "57248-7",
              "display": "Feeding or Eating: Current ability to feed self meals and snacks safely.",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        }
      ],
      "linkId": "/99152-1",
      "questionCodeSystem": "http://loinc.org",
      "codeList": [
        {
          "code": "99152-1",
          "display": "Swallowing/Nutritional Status",
          "system": "http://loinc.org"
        }
      ],
      "displayControl": { "questionLayout": "vertical" },
      "questionCardinality": { "min": "1", "max": "1" },
      "answerCardinality": { "min": "0", "max": "1" }
    },
    {
      "questionCode": "88463-5",
      "localQuestionCode": "M",
      "dataType": "SECTION",
      "header": true,
      "units": null,
      "codingInstructions": null,
      "copyrightNotice": null,
      "question": "Skin Conditions",
      "answers": null,
      "skipLogic": null,
      "restrictions": null,
      "defaultAnswer": null,
      "formatting": null,
      "calculationMethod": null,
      "items": [
        {
          "questionCode": "85918-1",
          "localQuestionCode": "M1306",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": "Excludes Stage 1 pressure inuries and all healed pressure ulcers/injuries.",
          "copyrightNotice": null,
          "question": "Does this patient have at least one Unhealed Pressure Ulcer/Injury at Stage 2 or Higher or designated as Unstageable?",
          "answers": [
            {
              "label": "0",
              "code": "LA32-8",
              "text": "No",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA33-6",
              "text": "Yes",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/88463-5/85918-1",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "85918-1",
              "display": "Does this patient have at least one Unhealed Pressure Ulcer/Injury at Stage 2 or Higher or designated as Unstageable?",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "88494-0",
          "localQuestionCode": "M1311",
          "dataType": "SECTION",
          "header": true,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Current Number of Unhealed Pressure Ulcers/Injuries at Each Stage",
          "answers": null,
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": [
            {
              "questionCode": "55124-2",
              "localQuestionCode": "M1311A1",
              "dataType": "REAL",
              "header": false,
              "units": [
                {
                  "name": "{#}",
                  "code": "{#}",
                  "system": "http://unitsofmeasure.org",
                  "default": false
                }
              ],
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Number of Stage 2 pressure ulcers",
              "answers": null,
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/88463-5/88494-0/55124-2",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "55124-2",
                  "display": "Number of Stage 2 pressure ulcers",
                  "system": "http://loinc.org"
                }
              ],
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" },
              "unit": {
                "name": "{#}",
                "code": "{#}",
                "system": "http://unitsofmeasure.org",
                "default": false
              }
            },
            {
              "questionCode": "55125-9",
              "localQuestionCode": "M1311B1",
              "dataType": "REAL",
              "header": false,
              "units": [
                {
                  "name": "{#}",
                  "code": "{#}",
                  "system": "http://unitsofmeasure.org",
                  "default": false
                }
              ],
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Number of Stage 3 pressure ulcers",
              "answers": null,
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/88463-5/88494-0/55125-9",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "55125-9",
                  "display": "Number of Stage 3 pressure ulcers",
                  "system": "http://loinc.org"
                }
              ],
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" },
              "unit": {
                "name": "{#}",
                "code": "{#}",
                "system": "http://unitsofmeasure.org",
                "default": false
              }
            },
            {
              "questionCode": "55126-7",
              "localQuestionCode": "M1311C1",
              "dataType": "REAL",
              "header": false,
              "units": [
                {
                  "name": "{#}",
                  "code": "{#}",
                  "system": "http://unitsofmeasure.org",
                  "default": false
                }
              ],
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Number of Stage 4 pressure ulcers",
              "answers": null,
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/88463-5/88494-0/55126-7",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "55126-7",
                  "display": "Number of Stage 4 pressure ulcers",
                  "system": "http://loinc.org"
                }
              ],
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" },
              "unit": {
                "name": "{#}",
                "code": "{#}",
                "system": "http://unitsofmeasure.org",
                "default": false
              }
            },
            {
              "questionCode": "54893-3",
              "localQuestionCode": "M1311D1",
              "dataType": "REAL",
              "header": false,
              "units": [
                {
                  "name": "{#}",
                  "code": "{#}",
                  "system": "http://unitsofmeasure.org",
                  "default": false
                }
              ],
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Number of unstageable pressure ulcers/injuries due to non-removable dressing/device",
              "answers": null,
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/88463-5/88494-0/54893-3",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "54893-3",
                  "display": "Number of unstageable pressure ulcers/injuries due to non-removable dressing/device",
                  "system": "http://loinc.org"
                }
              ],
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" },
              "unit": {
                "name": "{#}",
                "code": "{#}",
                "system": "http://unitsofmeasure.org",
                "default": false
              }
            },
            {
              "questionCode": "54946-9",
              "localQuestionCode": "M1311E1",
              "dataType": "REAL",
              "header": false,
              "units": [
                {
                  "name": "{#}",
                  "code": "{#}",
                  "system": "http://unitsofmeasure.org",
                  "default": false
                }
              ],
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Number of unstageable pressure ulcers/injuries due to coverage of wound bed by slough and/or eschar",
              "answers": null,
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/88463-5/88494-0/54946-9",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "54946-9",
                  "display": "Number of unstageable pressure ulcers/injuries due to coverage of wound bed by slough and/or eschar",
                  "system": "http://loinc.org"
                }
              ],
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" },
              "unit": {
                "name": "{#}",
                "code": "{#}",
                "system": "http://unitsofmeasure.org",
                "default": false
              }
            },
            {
              "questionCode": "54950-1",
              "localQuestionCode": "M1311F1",
              "dataType": "REAL",
              "header": false,
              "units": [
                {
                  "name": "{#}",
                  "code": "{#}",
                  "system": "http://unitsofmeasure.org",
                  "default": false
                }
              ],
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Number of unstageable pressure injuries presenting as deep tissue injury",
              "answers": null,
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/88463-5/88494-0/54950-1",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "54950-1",
                  "display": "Number of unstageable pressure injuries presenting as deep tissue injury",
                  "system": "http://loinc.org"
                }
              ],
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" },
              "unit": {
                "name": "{#}",
                "code": "{#}",
                "system": "http://unitsofmeasure.org",
                "default": false
              }
            }
          ],
          "linkId": "/88463-5/88494-0",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "88494-0",
              "display": "Current Number of Unhealed Pressure Ulcers/Injuries at Each Stage",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": { "questionLayout": "vertical" },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "46536-9",
          "localQuestionCode": "M1322",
          "dataType": "CNE",
          "header": false,
          "units": [
            {
              "name": "{#}",
              "code": "{#}",
              "system": "http://unitsofmeasure.org",
              "default": false
            }
          ],
          "codingInstructions": "A stage 1 pressure injury is defined as intact skin with non-blanchable redness of a localized area usually over a bony prominence. Darkly pigmented skin may not have a visible blanching; in dark skin tones only it may appear with persistent blue or purple hues.",
          "copyrightNotice": null,
          "question": "Current Number of Stage 1 Pressure Injuries",
          "answers": [
            {
              "label": "0",
              "code": "LA6111-4",
              "text": "0",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA6112-2",
              "text": "1",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA6113-0",
              "text": "2",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA6114-8",
              "text": "3",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "4",
              "code": "LA12206-1",
              "text": "4 or more",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/88463-5/46536-9",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "46536-9",
              "display": "Current Number of Stage 1 Pressure Injuries",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "57231-3",
          "localQuestionCode": "M1324",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Stage of Most Problematic Unhealed Pressure Ulcer/Injury that is Stageable",
          "answers": [
            {
              "label": "1",
              "code": "LA6383-9",
              "text": "Stage 1",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA6384-7",
              "text": "Stage 2",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA6385-4",
              "text": "Stage 3",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "4",
              "code": "LA6386-2",
              "text": "Stage 4",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": null,
              "code": "LA29202-1",
              "text": "Patient has no pressure ulcers/injuries or no stageable pressure ulcers/injuries",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/88463-5/57231-3",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "57231-3",
              "display": "Stage of Most Problematic Unhealed Pressure Ulcer/Injury that is Stageable",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "57232-1",
          "localQuestionCode": "M1330",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Does this patient have a Stasis Ulcer?",
          "answers": [
            {
              "label": "0",
              "code": "LA32-8",
              "text": "No",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA12402-6",
              "text": "Yes, patient has BOTH observable and unobservable stasis ulcers",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA12400-0",
              "text": "Yes, patient has observable stasis ulcers ONLY",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA12401-8",
              "text": "Yes, patient has unobservable stasis ulcers ONLY (known but not observable due to non-removable dressing/device)",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/88463-5/57232-1",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "57232-1",
              "display": "Does this patient have a Stasis Ulcer?",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "57233-9",
          "localQuestionCode": "M1332",
          "dataType": "CNE",
          "header": false,
          "units": [
            {
              "name": "{#}",
              "code": "{#}",
              "system": "http://unitsofmeasure.org",
              "default": false
            }
          ],
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Current Number of Stasis Ulcer(s) that are Observable",
          "answers": [
            {
              "label": "1",
              "code": "LA6306-0",
              "text": "One",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA6404-3",
              "text": "Two",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA6395-3",
              "text": "Three",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "4",
              "code": "LA33103-5",
              "text": "Four",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/88463-5/57233-9",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "57233-9",
              "display": "Current Number of Stasis Ulcer(s) that are Observable",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "57234-7",
          "localQuestionCode": "M1334",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Status of Most Problematic Stasis Ulcer that is Observable",
          "answers": [
            {
              "label": "1",
              "code": "LA6203-9",
              "text": "Fully granulating",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA6193-2",
              "text": "Early/partial granulation",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA6300-3",
              "text": "Not healing",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/88463-5/57234-7",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "57234-7",
              "display": "Status of Most Problematic Stasis Ulcer that is Observable",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "57235-4",
          "localQuestionCode": "M1340",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Does this patient have a Surgical Wound?",
          "answers": [
            {
              "label": "0",
              "code": "LA32-8",
              "text": "No",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA12633-6",
              "text": "Yes, patient has at least one observable surgical wound",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA12634-4",
              "text": "Surgical wound known but not observable due to non-removable dressing/device",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/88463-5/57235-4",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "57235-4",
              "display": "Does this patient have a Surgical Wound?",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "57236-2",
          "localQuestionCode": "M1342",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Status of Most Problematic Surgical Wound that is Observable",
          "answers": [
            {
              "label": "0",
              "code": "LA12197-2",
              "text": "Newly epithelialized",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA6203-9",
              "text": "Fully granulating",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA6193-2",
              "text": "Early/partial granulation",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA6300-3",
              "text": "Not healing",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/88463-5/57236-2",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "57236-2",
              "display": "Status of Most Problematic Surgical Wound that is Observable",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        }
      ],
      "linkId": "/88463-5",
      "questionCodeSystem": "http://loinc.org",
      "codeList": [
        {
          "code": "88463-5",
          "display": "Skin Conditions",
          "system": "http://loinc.org"
        }
      ],
      "displayControl": { "questionLayout": "vertical" },
      "questionCardinality": { "min": "1", "max": "1" },
      "answerCardinality": { "min": "0", "max": "1" }
    },
    {
      "questionCode": "99151-3",
      "localQuestionCode": "N",
      "dataType": "SECTION",
      "header": true,
      "units": null,
      "codingInstructions": null,
      "copyrightNotice": null,
      "question": "Medications",
      "answers": null,
      "skipLogic": null,
      "restrictions": null,
      "defaultAnswer": null,
      "formatting": null,
      "calculationMethod": null,
      "items": [
        {
          "questionCode": "93155-0",
          "localQuestionCode": "N0415",
          "dataType": "SECTION",
          "header": true,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "High-Risk Drug Classes: Use and Indication",
          "answers": null,
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": [
            {
              "questionCode": "93153-5",
              "localQuestionCode": "N0415_1",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Is taking. Check if the patient is taking any medications by pharmacological classification, not how it is used, in the following classes",
              "answers": [
                {
                  "label": "A",
                  "code": "LA30297-8",
                  "text": "Antipsychotic",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "E",
                  "code": "LA30298-6",
                  "text": "Anticoagulant",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "F",
                  "code": "LA30299-4",
                  "text": "Antibiotic",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "H",
                  "code": "LA28420-0",
                  "text": "Opioid",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "I",
                  "code": "LA30300-0",
                  "text": "Antiplatelet",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "J",
                  "code": "LA30301-8",
                  "text": "Hypoglycemic (including insulin)",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "Z",
                  "code": "LA9-3",
                  "text": "None of the above",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/99151-3/93155-0/93153-5",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "93153-5",
                  "display": "Is taking. Check if the patient is taking any medications by pharmacological classification, not how it is used, in the following classes",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "93154-3",
              "localQuestionCode": "N0415_2",
              "dataType": "CNE",
              "header": false,
              "units": null,
              "codingInstructions": null,
              "copyrightNotice": null,
              "question": "Indication noted. If column 1 [Is Taking] is checked, check if there is an indication noted for all medications in the drug class",
              "answers": [
                {
                  "label": "A",
                  "code": "LA30297-8",
                  "text": "Antipsychotic",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "E",
                  "code": "LA30298-6",
                  "text": "Anticoagulant",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "F",
                  "code": "LA30299-4",
                  "text": "Antibiotic",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "H",
                  "code": "LA28420-0",
                  "text": "Opioid",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "I",
                  "code": "LA30300-0",
                  "text": "Antiplatelet",
                  "other": null,
                  "system": "http://loinc.org"
                },
                {
                  "label": "J",
                  "code": "LA30301-8",
                  "text": "Hypoglycemic (including insulin)",
                  "other": null,
                  "system": "http://loinc.org"
                }
              ],
              "skipLogic": null,
              "restrictions": null,
              "defaultAnswer": null,
              "formatting": null,
              "calculationMethod": null,
              "items": null,
              "linkId": "/99151-3/93155-0/93154-3",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "93154-3",
                  "display": "Indication noted. If column 1 [Is Taking] is checked, check if there is an indication noted for all medications in the drug class",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            }
          ],
          "linkId": "/99151-3/93155-0",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "93155-0",
              "display": "High-Risk Drug Classes: Use and Indication",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": { "questionLayout": "vertical" },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "57255-2",
          "localQuestionCode": "M2001",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": "Indicates whether a drug regimen review indicate potential clinically significant medication issues.",
          "copyrightNotice": null,
          "question": "Drug Regimen Review: Did a complete drug regimen review identify potential clinically significant medication issues?",
          "answers": [
            {
              "label": "1",
              "code": "LA27634-7",
              "text": "No - No issues found during review",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA27635-4",
              "text": "Yes - Issues found during review",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "9",
              "code": "LA27636-2",
              "text": "NA - Resident is not taking any medications",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99151-3/57255-2",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "57255-2",
              "display": "Drug Regimen Review: Did a complete drug regimen review identify potential clinically significant medication issues?",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "57281-8",
          "localQuestionCode": "M2003",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Medication Follow-up: Did the agency contact a physician (or physician-designee) by midnight of the next calendar day and complete prescribed/recommended actions in response to the identified potential clinically significant medication issues?",
          "answers": [
            {
              "label": "0",
              "code": "LA32-8",
              "text": "No",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA33-6",
              "text": "Yes",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99151-3/57281-8",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "57281-8",
              "display": "Medication Follow-up: Did the agency contact a physician (or physician-designee) by midnight of the next calendar day and complete prescribed/recommended actions in response to the identified potential clinically significant medication issues?",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "57257-8",
          "localQuestionCode": "M2010",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Patient/Caregiver High-Risk Drug Education: Has the patient/caregiver received instruction on special precautions for all high-risk medications (such as hypoglycemics, anticoagulants, etc.) and how and when to report problems that may occur?",
          "answers": [
            {
              "label": "0",
              "code": "LA32-8",
              "text": "No",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA33-6",
              "text": "Yes",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "NA",
              "code": "LA12317-6",
              "text": "Patient not taking any high risk drugs OR patient/caregiver fully knowledgeable about special precautions associated with all high-risk medications",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99151-3/57257-8",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "57257-8",
              "display": "Patient/Caregiver High-Risk Drug Education: Has the patient/caregiver received instruction on special precautions for all high-risk medications (such as hypoglycemics, anticoagulants, etc.) and how and when to report problems that may occur?",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "57285-9",
          "localQuestionCode": "M2020",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Management of Oral Medications: Patient's current ability to prepare and take all oral medications reliably and safely, including administration of the correct dosage at the appropriate times/intervals.",
          "answers": [
            {
              "label": "0",
              "code": "LA6135-3",
              "text": "Able to independently take the correct oral medication(s) and proper dosage(s) at the correct times.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA12322-6",
              "text": "Able to take medication(s) at the correct times if: (a) individual dosages are prepared in advance by another person; OR (b) another person develops a drug diary or chart.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA12323-4",
              "text": "Able to take medication(s) at the correct times if given reminders by another person at the appropriate times",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA12324-2",
              "text": "Unable to take medication unless administered by another person.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "NA",
              "code": "LA6290-6",
              "text": "No oral medications prescribed.",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99151-3/57285-9",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "57285-9",
              "display": "Management of Oral Medications: Patient's current ability to prepare and take all oral medications reliably and safely, including administration of the correct dosage at the appropriate times/intervals.",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "57284-2",
          "localQuestionCode": "M2030",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Management of Injectable Medications: Patient's current ability to prepare and take all prescribed injectable medications reliably and safely, including administration of correct dosage at the appropriate times/intervals.",
          "answers": [
            {
              "label": "0",
              "code": "LA12326-7",
              "text": "Able to independently take the correct medication(s) and proper dosage(s) at the correct times.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "1",
              "code": "LA12327-5",
              "text": "Able to take injectable medication(s) at the correct times if: (a) individual syringes are prepared in advance by another person; OR (b) another person develops a drug diary or chart.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "2",
              "code": "LA12328-3",
              "text": "Able to take medication(s) at the correct times if given reminders by another person based on the frequency of the injection",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "3",
              "code": "LA12329-1",
              "text": "Unable to take injectable medication unless administered by another person.",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "NA",
              "code": "LA6280-7",
              "text": "No injectable medications prescribed.",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99151-3/57284-2",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "57284-2",
              "display": "Management of Injectable Medications: Patient's current ability to prepare and take all prescribed injectable medications reliably and safely, including administration of correct dosage at the appropriate times/intervals.",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        }
      ],
      "linkId": "/99151-3",
      "questionCodeSystem": "http://loinc.org",
      "codeList": [
        {
          "code": "99151-3",
          "display": "Medications",
          "system": "http://loinc.org"
        }
      ],
      "displayControl": { "questionLayout": "vertical" },
      "questionCardinality": { "min": "1", "max": "1" },
      "answerCardinality": { "min": "0", "max": "1" }
    },
    {
      "questionCode": "99143-0",
      "localQuestionCode": "O",
      "dataType": "SECTION",
      "header": true,
      "units": null,
      "codingInstructions": null,
      "copyrightNotice": null,
      "question": "Special Treatment, Procedures, and Programs",
      "answers": null,
      "skipLogic": null,
      "restrictions": null,
      "defaultAnswer": null,
      "formatting": null,
      "calculationMethod": null,
      "items": [
        {
          "questionCode": "83252-7",
          "localQuestionCode": "O0110_a",
          "dataType": "CNE",
          "header": false,
          "units": null,
          "codingInstructions": null,
          "copyrightNotice": null,
          "question": "Special Treatments, Procedures, and Programs - On Admission. Check all of the following treatments, procedures, and programs that apply on admission.",
          "answers": [
            {
              "label": "A1",
              "code": "LA6172-6",
              "text": "Chemotherapy",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "A2",
              "code": "LA30275-4",
              "text": "Chemotherapy - IV",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "A3",
              "code": "LA30276-2",
              "text": "Chemotherapy - Oral",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "A10",
              "code": "LA30277-0",
              "text": "Chemotherapy - Other",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "B1",
              "code": "LA4351-8",
              "text": "Radiation",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "C1",
              "code": "LA27962-2",
              "text": "Oxygen therapy",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "C2",
              "code": "LA30278-8",
              "text": "Oxygen therapy - Continuous",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "C3",
              "code": "LA30279-6",
              "text": "Oxygen therapy - Intermittent",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "C4",
              "code": "LA30280-4",
              "text": "Oxygen therapy - High-concentration",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "D1",
              "code": "LA27963-0",
              "text": "Suctioning",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "D2",
              "code": "LA30359-6",
              "text": "Suctioning - Scheduled",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "D3",
              "code": "LA30360-4",
              "text": "Suctioning - As needed",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "E1",
              "code": "LA27964-8",
              "text": "Tracheostomy care",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "F1",
              "code": "LA28889-6",
              "text": "Invasive Mechanical Ventilator (ventilator or respirator)",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "G1",
              "code": "LA30281-2",
              "text": "Non-invasive mechanical ventilator",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "G2",
              "code": "LA30282-0",
              "text": "Non-invasive mechanical ventilator - BiPAP",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "G3",
              "code": "LA30283-8",
              "text": "Non-invasive mechanical ventilator - CPAP",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "H1",
              "code": "LA27972-1",
              "text": "IV medications",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "H2",
              "code": "LA30284-6",
              "text": "IV medications - Vasoactive medications",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "H3",
              "code": "LA30285-3",
              "text": "IV medications - Antibiotics",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "H4",
              "code": "LA30286-1",
              "text": "IV medications - Anticoagulation",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "H10",
              "code": "LA30287-9",
              "text": "IV medications - Other",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "I1",
              "code": "LA27966-3",
              "text": "Transfusions",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "J1",
              "code": "LA7216-0",
              "text": "Dialysis",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "J2",
              "code": "LA30288-7",
              "text": "Dialysis - Hemodialysis",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "J3",
              "code": "LA30289-5",
              "text": "Dialysis - Peritoneal dialysis",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "O1",
              "code": "LA30290-3",
              "text": "IV Access",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "O2",
              "code": "LA30291-1",
              "text": "IV Access - Peripheral",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "O3",
              "code": "LA30292-9",
              "text": "IV Access - Midline",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "O4",
              "code": "LA30293-7",
              "text": "IV Access - Central (e.g., PICC, tunneled, port)",
              "other": null,
              "system": "http://loinc.org"
            },
            {
              "label": "Z1",
              "code": "LA9-3",
              "text": "None of the above",
              "other": null,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99143-0/83252-7",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "83252-7",
              "display": "Special Treatments, Procedures, and Programs - On Admission. Check all of the following treatments, procedures, and programs that apply on admission.",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "57268-5",
          "localQuestionCode": "M2200",
          "dataType": "REAL",
          "header": false,
          "units": [
            {
              "name": "{#}",
              "code": "{#}",
              "system": "http://unitsofmeasure.org",
              "default": false
            }
          ],
          "codingInstructions": "Total number of therapy visits in the plan of care, including physical therapy, occupational therapy, and speech-language pathology",
          "copyrightNotice": null,
          "question": "Therapy need: Number of therapy visits indicated (total of physical, occupational and speech-language pathology combined).",
          "answers": null,
          "skipLogic": null,
          "restrictions": null,
          "defaultAnswer": null,
          "formatting": null,
          "calculationMethod": null,
          "items": null,
          "linkId": "/99143-0/57268-5",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "57268-5",
              "display": "Therapy need: Number of therapy visits indicated (total of physical, occupational and speech-language pathology combined).",
              "system": "http://loinc.org"
            }
          ],
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" },
          "unit": {
            "name": "{#}",
            "code": "{#}",
            "system": "http://unitsofmeasure.org",
            "default": false
          }
        }
      ],
      "linkId": "/99143-0",
      "questionCodeSystem": "http://loinc.org",
      "codeList": [
        {
          "code": "99143-0",
          "display": "Special Treatment, Procedures, and Programs",
          "system": "http://loinc.org"
        }
      ],
      "displayControl": { "questionLayout": "vertical" },
      "questionCardinality": { "min": "1", "max": "1" },
      "answerCardinality": { "min": "0", "max": "1" }
    }
  ],
  "templateOptions": {
    "showQuestionCode": false,
    "showCodingInstruction": false,
    "allowMultipleEmptyRepeatingItems": false,
    "allowHTMLInInstructions": false,
    "displayControl": { "questionLayout": "vertical" },
    "viewMode": "auto",
    "defaultAnswerLayout": {
      "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
    },
    "hideTreeLine": false,
    "hideIndentation": false,
    "hideRepetitionNumber": false,
    "displayScoreWithAnswerText": true
  },
  "hasSavedData": true
}
