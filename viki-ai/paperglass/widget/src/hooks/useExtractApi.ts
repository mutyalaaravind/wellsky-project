import react, { useCallback, useState } from "react";

const dummyResults: any = {
  "section_general_patient_details.first_name": "minnie",
  "section_general_patient_details.last_name": "mouse",
  "section_general_patient_details.date_of_birth": "1/1/44",
  "section_general_patient_details.home_phone": "3864096916",
  "section_general_patient_details.mobile_phone": "",
};

export const useExtractApi = (env: any) => {
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<boolean>(false);
  const [busy, setBusy] = useState(false);
  const extract = useCallback(
    async (summary: string, model: string) => {
      if (!summary) {
        return null;
      }
      const promptText = `
        you are a transcriber who is good at extracting key values from provided context.

        Please use below rules for extraction:
        1. any date field needs to be in mm/dd/yyyy format
        2. facility is same as Provider Name. No need to provide full address, just the provider name
        3. some times address don't have state.
        4. USA is the default country
        5. date of birth cannot be a future date and should be in mm/dd/yyyy format. e.g: 01/01/1944
        6. section_1708067359.mar_medication_section will be array of medication with its keys as medication_input,dose_input,route_input,frequence_input,prn_reason_input,location_input, patient_response_input
        7. the final json keys should match the provided JSON format keys 

        You need to strictly extract it in the provided JSON format only:
        {
            "section_general_patient_details.first_name":"",
            "section_general_patient_details.last_name":"",
            "section_general_patient_details.date_of_birth":"",
            "section_general_patient_details.home_phone":"",
            "section_general_patient_details.mobile_phone":"",
            "section_general_patient_details.patient_gender":"",
            "referral_information_section.referring_physician":"",
            "referral_information_section.facility":"",
            "section_patient_home_address.patient_home_address_1":"",
            "section_patient_home_address.patient_home_address_2":"",
            "section_patient_home_address.patient_home_city":"",
            "section_patient_home_address.patient_home_country":"",
            "section_patient_home_address.patient_zip_code":"",
            "section_1708067359.mar_medication_section":""
        }
        EXAMPLE:
        CONTEXT: Patient Mickey mouse has date of birth: 1/1/44

        {
          "section_general_patient_details.first_name":"Mickey",
            "section_general_patient_details.last_name":"mouse",
            "section_general_patient_details.date_of_birth":"01/01/1944",
            "section_general_patient_details.home_phone":"",
            "section_general_patient_details.mobile_phone":"",
            "section_general_patient_details.patient_gender":"",
            "referral_information_section.referring_physician":"",
            "referral_information_section.facility":"",
            "section_patient_home_address.patient_home_address_1":"",
            "section_patient_home_address.patient_home_address_2":"",
            "section_patient_home_address.patient_home_city":"",
            "section_patient_home_address.patient_home_country":"",
            "section_patient_home_address.patient_zip_code":""
        }

        CONTEXT:
        ${summary}
        `;
      setBusy(true);
      console.log("prompt text", promptText);
      const response = await fetch(
        env?.API_URL + `/api/extract`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ prompt_text: promptText, model: model })
        }
      );
      try {
        const data = await response.json();
        console.log("extract results", data);
        if (data === undefined) {
          return;
        }
        const result = JSON.parse(
          data.replace("json", "").replace("```", "").replace("```", "").trim(),
        );
        console.log("extract results", result);
        setResults(result);
        setBusy(false);
      } catch (error) {
        console.error(error);
        setError(true);
        setBusy(false);
      }
    },
    [env?.API_URL],
  );

  return { extract, results, busy, error };
};
