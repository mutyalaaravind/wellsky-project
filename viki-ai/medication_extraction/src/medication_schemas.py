"""
Entity schemas for medication extraction.

This module defines JSON schemas used to structure LLM responses for medication extraction.
Schemas use UPPERCASE types (STRING, OBJECT, ARRAY, etc.) as required by Vertex AI Gemini API.
"""

SCHEMAS = {
    "medication_extraction": {
        "description": "Schema for extracting medication information from medical documents",
        "type": "ARRAY",
        "items": {
            "type": "OBJECT",
            "additionalProperties": False,
            "properties": {
                "name": {
                    "description": "Medication name including alias and punctuation if present, but excluding strength and unit of measurement (e.g., 'Aspirin 81mg' should be 'Aspirin', and 'hydrocodone 5 mg-acetaminophen' should be 'hydrocodone-acetaminophen')",
                    "type": "STRING"
                },
                "strength": {
                    "description": "Medication strength with unit of measurement when available (e.g., '10 MG', '80 MG', '100 UNIT/ML (3 ML)'). Include the unit (MG, ML, GM, %, UNIT, ACT) with the numeric value if present in the document. If no unit is specified, extract just the numeric value. If dosage has these units, it belongs in strength not dosage.",
                    "type": "STRING",
                    "nullable": True
                },
                "dosage": {
                    "description": "Dosage numeric quantity ONLY - just the number without any words (CORRECT: '1', '2', '2-3' | WRONG: '1 tablet', '2 capsules'). Extract ONLY the numeric part. The word 'tablet' or 'capsule' goes in the 'form' field.",
                    "type": "STRING",
                    "nullable": True
                },
                "route": {
                    "description": "Route of administration in UPPERCASE (e.g., 'ORAL', 'SUBCUTANEOUS', 'IV', 'TOPICAL', 'INTRAMUSCULAR')",
                    "type": "STRING",
                    "nullable": True
                },
                "form": {
                    "description": "Medication physical form in UPPERCASE - extract from dosage phrase (CORRECT: 'TABLET', 'CAPSULE' | EXAMPLES: '1 tablet'→form='TABLET', '2 capsules'→form='CAPSULE', 'extended release capsule'→form='CAPSULE, EXTENDED RELEASE 24 HR')",
                    "type": "STRING",
                    "nullable": True
                },
                "discontinued_date": {
                    "description": "Discontinued date of medication in mm/dd/yyyy format. Use null if not discontinued",
                    "type": "STRING",
                    "nullable": True
                },
                "frequency": {
                    "description": "Frequency of administration (e.g., 'BEDTIME', 'DAILY', '2 TIMES DAILY'). Recognize and interpret Latin abbreviations and convert to full phrases",
                    "type": "STRING",
                    "nullable": True
                },
                "start_date": {
                    "description": "Start date of medication in mm/dd/yyyy format (e.g., '06/01/2022')",
                    "type": "STRING",
                    "nullable": True
                },
                "end_date": {
                    "description": "End date of medication in mm/dd/yyyy format. Use null if ongoing",
                    "type": "STRING",
                    "nullable": True
                },
                "instructions": {
                    "description": "Additional instructions for taking the medication. Use null if not specified",
                    "type": "STRING",
                    "nullable": True
                },
                "explanation": {
                    "description": "Explanation or reasoning for the medication extraction. Use null if not needed",
                    "type": "STRING",
                    "nullable": True
                },
                "is_long_standing": {
                    "description": "Boolean indicating if medication is long-standing. Set to true ONLY if explicitly marked with: 'LS', 'L/S', 'L-S', 'Longstanding', 'long-standing', or 'long standing' near the medication. Otherwise set to false.",
                    "type": "BOOLEAN"
                },
                "document_reference": {
                    "description": "Reference to the source document location",
                    "type": "STRING"
                },
                "page_number": {
                    "description": "Page number where the medication was found",
                    "type": "INTEGER"
                }
            },
            "required": ["name"]
        }
    },
    
    "medispan_matching": {
        "description": "Schema for matching extracted medications to Medispan drug database entries",
        "type": "ARRAY",
        "items": {
            "type": "OBJECT",
            "additionalProperties": False,
            "properties": {
                "medication_id": {
                    "description": "The unique identifier of the extracted medication to match",
                    "type": "STRING"
                },
                "matched_medispan_id": {
                    "description": "The matched Medispan drug ID from the match list, or null if no suitable match found",
                    "type": ["STRING", "NULL"]
                }
            },
            "required": ["medication_id", "matched_medispan_id"]
        }
    },
    
    "classification_extraction": {
        "description": "Schema for comprehensive document classification and extraction including medications and conditions",
        "type": "OBJECT",
        "additionalProperties": False,
        "properties": {
            "page_number": {
                "description": "Page number being analyzed",
                "type": "INTEGER"
            },
            "comprehensive_details": {
                "description": "Comprehensive details with all text elements organized by section",
                "type": "OBJECT",
                "additionalProperties": True
            },
            "medications": {
                "description": "Array of medications found on this page",
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "name": {
                            "description": "Medication name",
                            "type": "STRING"
                        },
                        "strength": {
                            "description": "Medication strength",
                            "type": "STRING"
                        },
                        "dosage": {
                            "description": "Dosage amount",
                            "type": "STRING"
                        },
                        "route": {
                            "description": "Route of administration",
                            "type": "STRING"
                        },
                        "form": {
                            "description": "Medication form",
                            "type": "STRING"
                        },
                        "frequency": {
                            "description": "Frequency of administration",
                            "type": "STRING"
                        },
                        "instructions": {
                            "description": "Additional instructions",
                            "type": "STRING"
                        }
                    },
                    "required": ["name"]
                }
            },
            "conditions": {
                "description": "Array of medical conditions found on this page",
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "condition": {
                            "description": "Medical condition or diagnosis",
                            "type": "STRING"
                        },
                        "status": {
                            "description": "Status of the condition (e.g., active, resolved, chronic)",
                            "type": "STRING"
                        }
                    },
                    "required": ["condition"]
                }
            }
        },
        "required": ["page_number"]
    }
}