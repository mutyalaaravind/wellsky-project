from vertexai.preview.language_models import TextGenerationModel
import vertexai


class Extract(object):
    
    def __init__(self) -> None:
        PROJECT_ID = "wscc-dev-app-wsky" # @param {type:"string"}
        LOCATION = "us-central1" # @param {type:"string"}
        vertexai.init(project=PROJECT_ID, location=LOCATION)

    def get_medical_record(self, statement):
        generation_model = TextGenerationModel.from_pretrained("text-bison")
        template=f"""You are medical transcriber.Your job is extract
            patient's name, patient's demographic information,
            medications, past and current medical conditions from the
            following context and return a json response. Use the JSON
            template below.
            {{
            "patient": {{
            "name": "",
            "age": ,
            "gender": "",
            "race": "unidentified",
            "ethnicity": "unidentified",
            "marital_status": "unidentified",
            "occupation": "unidentified",
            "address": "unidentified",
            "phone_number": "unidentified",
            "email": "unidentified",
            "emergency_contact": "unidentified"
            }},
            "medical_history": {{
            "past_medical_conditions": [
            ""
            ],
            "current_medical_conditions": [
            ""
            ],
            "medications": [
            ],
            "hospitalizations": [
            {{
            "date": "",
            "reason": "",
            "hospital": ""
            }}
            ],
            "surgeries": [
            {{
            "date": "unidentified",
            "type": "unidentified",
            "hospital": "unidentified"
            }}
            ],
            "allergies": [
            "unidentified"
            ],
            "social_history": {{
            "tobacco_use": "unidentified",
            "alcohol_use": "unidentified",
            "drug_use": "unidentified"
            }},
            "family_history": {{
            "diabetes": "unidentified",
            "heart_disease": "unidentified",
            "stroke": "unidentified",
            "cancer": "unidentified",
            "other": "unidentified"
            }}
            }}
            }}
            context:{statement}
            response:
            """
        response=generation_model.predict(
            template,
            max_output_tokens=1024,
            temperature=0
        )
        answer = response.text
        return answer

    def get_health_info(self, statement, question):
        generation_model = TextGenerationModel.from_pretrained("text-bison")
        template=f"""Answer the question given in the context below.
        Provide only specific answers without elaborate sentences.
        context:{statement}
        criteria:{question}
        answer:
        """
        response=generation_model.predict(
            template,
            max_output_tokens=1024,
            temperature=0
        )
        answer = response.text
        return answer