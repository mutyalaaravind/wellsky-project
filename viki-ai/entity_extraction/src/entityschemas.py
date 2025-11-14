


SCHEMAS = {

    "insurance_data": {
        #"$schema": "https://json-schema.org/draft/2020-12/schema",
        "description": "A insurance data schema",
        "type": "OBJECT",
        #"$id": "https://example.com/schemas/insurance_data.json",
        "additionalProperties": False,
        "title": "Insurance Data Schema",
        "properties": {
            "memberId": {
            "description": "Unique identifier for the insured member",
            "type": "STRING"
            },
            "metadata": {
            "description": "Additional metadata",
            "type": "OBJECT",
            "additionalProperties": True
            },
            "memberName": {
            "description": "name of the insured member",
            "type": "STRING"
            },
            "providerName": {
            "description": "Name of the insurance provider",
            "type": "STRING"
            },
            "planName": {
            "description": "Name of the insurance plan",
            "type": "STRING"
            },
            "groupNumber": {
            "description": "Group number for the insurance policy",
            "type": "STRING"
            },
            "employerName": {
            "description": "Name of insured's employer",
            "type": "STRING",
            "maxLength": 100
            }
        },
        "required": []
        }

}