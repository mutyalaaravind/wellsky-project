from typing import Dict

class PromptTemplates:
    CLASSIFY = """
            You are expert medical transcriber. 
            Taking each page of the document attached, 
            can you extract comprehensive details with all the text elements on the given page?
            Additionally, please extract medications in <MEDICATIONS> section and conditions in <CONDITIONS> section.
            
            Output expected:
            <EXTRACT>
            Page: #X
            Comprehensive Details:
            **[section header]**
                [section comprehensive details]
            </EXTRACT>
            <MEDICATIONS>
            </MEDICATIONS>
            <CONDITIONS>
            </CONDITIONS>
            """

    EXTRACT_MEDICATIONS = """
            Please study this document:[Task]:
            please extract medications as array of JSON with keys as name, strength, dosage, route, form, discontinued_date, frequency, start_date, end_date, instructions, explanation, is_long_standing, document_reference and page_number.
            Please do not include any markup other than JSON.
            Output must be a single JSON array only.
            Return [] only if you are certain there are no medication mentions in the document.
            If any medication is mentioned but some details are missing, still return it with all required keys (unknown values as null).
            Please format start_date and end_date as mm/dd/yyyy.
            **The 'name' field should include alias , punctuation if present but exclude strength and unit of measurement (e.g., 'Aspirin 81mg' should be 'Aspirin', and 'hydrocodone 5 mg-acetaminophen' should be 'hydrocodone-acetaminophen')**
            **For 'strength' field: Extract with unit of measurement if present in document (e.g., 'AMLODIPINE 10 MG' -> strength: '10 MG'). If no unit is mentioned, extract just the numeric value.**
            **Distinguish between dosage (eg. 1 tab -> 1, 2-3 tablets -> 2-3) and strength of medication. Dosage field does not have Unit of Measurement(MG, ML, GM, %, UT, ACT, UNIT), if it has considered as Strength, leave dosage blank**
            
            Additional Instructions for Frequency Field:
                Frequency: Please recognize and correctly interpret Latin abbreviations related to medication frequency (e.g., "Q" for "every", "BID" for "twice a day", "TID" for "three times a day", etc.) and convert them into their full phrases (e.g., "Q 8 H" should be read as "every 8 hours").
            
            Additional Instructions for is_long_standing Field:
                is_long_standing: This is a boolean field (true/false). Set to true ONLY if the medication line explicitly shows any of these markers: 'LS', 'L/S', 'L-S', 'Longstanding', 'long-standing', or 'long standing'. If none of these markers are present, set to false.
            
            Return a single JSON array with no markup other than JSON.
            """

    MEDISPAN_MATCH = """
            For each GIVEN MEDICATION, find the best matching medication from the MATCH LIST below using these rules (in order):
            1) The GIVEN MEDICATION's name must match the "NameDescription" field of the MATCH LIST entries. Otherwise, do not match.
            2) Prefer the match if the MATCH LIST entry's "NameDescription" begins with the first word of the GIVEN MEDICATION name
            3) Prefer the match if the name of the GIVEN MEDICATION exactly matches (case insensitive) the name of the MATCH LIST "NameDescription" entry.  
            4) Lower the consideration for the match if the name of the GIVEN MEDICATION only matches the "GenericName" field and does not match the "NameDescription" field of the MATCH LIST entry.
            5) If the GIVEN MEDICATION has medication strength specified, select from the list only if there is exact match of the Strength
            6) If the GIVEN MEDICATION has medication form specified, select from the list only if there is exact match of the Dosage_Form
            7) If the GIVEN MEDICATION has medication route specified, select from the list only if there is exact match of the Route
            
            Input Format:
            GIVEN MEDICATIONS: A list of objects, each with an "id" and a "medication_name".
            MATCH LIST: A list of medication objects with at least the fields: "id", "NameDescription", "GenericName", "Strength", "Dosage_Form", "Route".

            For each medication, only return the best match from the list.
            If no suitable match is found, use null as the value.

            Response Format:
            Return a JSON array.
            For each medication in GIVEN MEDICATIONS, return one object, where the key is the medication's "id" and the value is the matched MATCH LIST "id".
            
            Example:
            [
                {"f979a02a7a4a407788ebdf714d92d211": "66706"},
                {"cb717c42d51f415281249a835c142fda": "191575"},
                {"d6cfee897e044e2a9ee737aeed3398e1": "69072"},
                {"8d6a57115b034eae97311f1fa6e8944a": "177191"}
            ]


            GIVEN MEDICATIONS:
            {SEARCH_TERM}

            MATCH LIST:
            {DATA}
            """

class ModelVersions:
    STEP_CLASSIFY = "gemini-1.5-flash-002"
    STEP_EXTRACT_MEDICATION = "gemini-1.5-flash-002"
    STEP_MEDISPAN_MATCH = "gemini-1.5-flash-002"

    GEMINI_MODELS = {
        "gemini-pro": "gemini-pro",
        "gemini-pro-vision": "gemini-pro-vision",
        "gemini-1.5-flash-002": "gemini-1.5-flash-002",
        "gemini-2.0-flash-lite-001": "gemini-2.0-flash-lite-001",
        "gemini-2.5-flash": "gemini-2.5-flash",
        "gemini-2.5-pro": "gemini-2.5-pro",
        "gemini-2.5-flash-lite": "gemini-2.5-flash-lite",
    }

    @staticmethod
    def get_available_models() -> Dict[str, Dict[str, str]]:
        return {
            "gemini": ModelVersions.GEMINI_MODELS
        }