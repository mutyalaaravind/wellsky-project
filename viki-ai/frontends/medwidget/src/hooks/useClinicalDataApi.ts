import { useCallback, useContext } from "react";
import useEnvJson from "./useEnvJson";
import { Env } from "types";
import { AuthContext } from "context/AuthContext";
import { usePatientProfileStore } from "store/patientProfileStore";
import {
  Immunizations,
  Allergies,
  NestedRecordObject,
  Condition,
} from "store/storeTypes";

export type ClinicalResponse<T extends Immunizations | Allergies> = Array<
  | ({
      clinical_data?: T[];
    } & NestedRecordObject)
  | undefined
>;

const useClinicalDataApi = () => {
  const { setLoading, setAllergies, setImmunizations, setConditions } =
    usePatientProfileStore();
  const env = useEnvJson<Env>();
  const authContext = useContext(AuthContext);
  const token = authContext.token;
  const oktaToken = authContext.oktaToken;
  // const ehrToken = authContext.ehrToken;

  // Fetch allergies from an API or any other data source
  const fetchAllergies = useCallback(
    async (documentId: string) => {
      if (!env?.API_URL) {
        return;
      }
      setLoading((prev) => {
        const set = new Set(Array.from(prev));
        set.add("allergies");
        return set;
      });
      try {
        const response = await fetch(
          `${env?.API_URL}/api/v2/extracted_clinical_data/allergies?documentIds=${documentId}`,
          {
            headers: {
              Authorization: "Bearer " + token,
              "Okta-Token": oktaToken,
            },
          },
        );
        const data: Array<Allergies> = await response.json();

        const allergiesDataOriginal: Array<Allergies> = data.map(
          (allergy: any) => {
            return {
              id: allergy.id,
              data: {
                substance: allergy.clinical_data.substance,
                reaction: allergy.clinical_data.reaction,
                date: allergy.clinical_data.date,
              },
              references: allergy.references.map((reference: any) => {
                return {
                  clinicalDataId: reference.extracted_clinical_data_id,
                  documentId: reference.document_id,
                  pageNumber: reference.page_number,
                  evidenceMarkId:
                    allergy.clinical_data.substance +
                    reference.page_number.toString() +
                    new Date().getTime(),
                };
              }),
            };
          },
        );

        setAllergies(allergiesDataOriginal);
        return data;
      } catch (error) {
        console.error("Error fetching allergies:", error);
      } finally {
        setLoading((prev) => {
          const set = new Set(Array.from(prev));
          set.delete("allergies");
          return set;
        });
      }
    },
    [env?.API_URL, oktaToken, setAllergies, setLoading, token],
  );

  const fetchImmunizations = useCallback(
    async (documentId: string) => {
      setLoading((prev) => {
        const set = new Set(Array.from(prev));
        set.add("immunizations");
        return set;
      });
      try {
        const response = await fetch(
          `${env?.API_URL}/api/v2/extracted_clinical_data/immunizations?documentIds=${documentId}`,
          {
            headers: {
              Authorization: "Bearer " + token,
              "Okta-Token": oktaToken,
            },
          },
        );
        const data: Array<any> = await response.json();

        const immunizationsDataOriginal: Array<Immunizations> = data.map(
          (immunization: any) => {
            return {
              id: immunization.id,
              data: {
                name: immunization.clinical_data.name,
                status: immunization.clinical_data.status,
                date: immunization.clinical_data.date,
                originalExtractedString:
                  immunization.clinical_data.original_extracted_string || "",
              },
              references: immunization.references.map((reference: any) => {
                return {
                  clinicalDataId: reference.extracted_clinical_data_id,
                  documentId: reference.document_id,
                  pageNumber: reference.page_number,
                  evidenceMarkId:
                    immunization.clinical_data.name +
                    reference.page_number.toString() +
                    new Date().getTime(),
                };
              }),
            };
          },
        );

        setImmunizations(immunizationsDataOriginal);
        return immunizationsDataOriginal;
      } catch (error) {
        console.error("Error fetching immunizations:", error);
      } finally {
        setLoading((prev) => {
          const set = new Set(Array.from(prev));
          set.delete("immunizations");
          return set;
        });
      }
    },
    [env?.API_URL, oktaToken, setImmunizations, setLoading, token],
  );

  const fetchConditions = useCallback(
    async (documentId: string) => {
      setLoading((prev) => {
        const set = new Set(Array.from(prev));
        set.add("conditions");
        return set;
      });
      try {
        const response = await fetch(
          `${env?.API_URL}/api/v2/extracted_clinical_data/conditions?documentIds=${documentId}`,
          {
            headers: {
              Authorization: "Bearer " + token,
              "Okta-Token": oktaToken,
            },
          },
        );
        const data: Array<any> = await response.json();

        const conditionsDataOriginal: Array<Condition> = data.map(
          (condition: any) => {
            return {
              evidences: condition.evidences.map((evidence: any) => {
                return {
                  endPosition: evidence.end_position,
                  startPosition: evidence.start_position,
                  evidenceReference: evidence.evidence_reference,
                  evidenceSnippet: evidence.evidence_snippet,
                  documentId: evidence.document_id,
                  pageNumber: evidence.page_number,
                  markerId:
                    condition.category +
                    evidence.page_number.toString() +
                    new Date().getTime(),
                };
              }),
              icd10Codes: condition.icd10_codes.map((code: any) => {
                return {
                  category: code.category,
                  description: code.description,
                  icdCode: code.icd_code,
                };
              }),
              category: condition.category,
            };
          },
        );
        setConditions(conditionsDataOriginal);
        return data;
      } catch (error) {
        console.error("Error fetching conditions:", error);
      } finally {
        setLoading((prev) => {
          const set = new Set(Array.from(prev));
          set.delete("conditions");
          return set;
        });
      }
    },
    [env?.API_URL, oktaToken, setConditions, setLoading, token],
  );

  return {
    fetchAllergies,
    fetchImmunizations,
    fetchConditions,
  };
};

export default useClinicalDataApi;
