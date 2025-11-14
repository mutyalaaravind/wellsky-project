const template = `You are medical transcriber.Your job is extract patient's name, patient's demographic information,
medications, past and current medical conditions from the
following context and return a json response. Use the JSON
template below.
{{
"patient": {{
"name": "",
"age": "",
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
`;

export default template;