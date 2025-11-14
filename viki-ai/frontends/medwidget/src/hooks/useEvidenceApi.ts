import { useCallback, useContext, useState } from "react";
import { Env, EvidenceInfo } from "types";
import { AuthContext } from "context/AuthContext";

const useEvidenceApi = () => {
  const authContext = useContext(AuthContext);
  const token = authContext.token;
  const oktaToken = authContext.oktaToken;

  const [evidence, setEvidence] = useState<EvidenceInfo>({
    documentId: "",
    pageNumber: 0,
    annotations: [],
  });

  // Fetch allergies from an API or any other data source
  const getEvidence = useCallback(
    async (
      env: Env,
      extractedClinicalDataId: string,
      extractedClinicalString: string,
      documentId: string,
      pageNumber: number,
    ) => {
      if (!env?.API_URL) {
        return;
      }
      try {
        const response = await fetch(
          `${env?.API_URL}/api/v2/search_evidences_for_clinical_data?extractedClinicalDataId=${extractedClinicalDataId}&extractedClinicalString=${extractedClinicalString}`,
          {
            headers: {
              Authorization: "Bearer " + token,
              "Okta-Token": oktaToken,
            },
          },
        );
        const data = await response.json();
        const evidenceInfo: EvidenceInfo = {
          documentId: documentId,
          pageNumber: pageNumber,
          annotations: data.map((evidence: any) => {
            return {
              width: evidence.x2 - evidence.x1,
              height: evidence.y2 - evidence.y1,
              x: evidence.x1,
              y: evidence.y1,
              text: evidence.text,
              page: pageNumber,
            };
          }),
        };
        setEvidence(evidenceInfo);
      } catch (error) {
        console.error("Error fetching configuration:", error);
      } finally {
      }
    },
    [oktaToken, token],
  );

  const getConditionsEvidence = useCallback(
    async (
      env: Env,
      evidenceSnippet: string,
      startPosition: number,
      endPosition: number,
      evidenceReference: string[],
      documentId: string,
      pageNumber: number,
    ) => {
      if (!env?.API_URL) {
        return;
      }
      try {
        const response = await fetch(
          `${env?.API_URL}/api/v2/search_evidences_for_conditions?evidenceSnippet=${evidenceSnippet}&startPosition=${startPosition}&endPosition=${endPosition}&documentId=${documentId}&pageNumber=${pageNumber}`,
          {
            headers: {
              Authorization: "Bearer " + token,
              "Okta-Token": oktaToken,
            },
          },
        );
        const data = await response.json();
        const evidenceInfo: EvidenceInfo = {
          documentId: documentId,
          pageNumber: pageNumber,
          annotations: data.map((evidence: any) => {
            return {
              width: evidence.x2 - evidence.x1,
              height: evidence.y2 - evidence.y1,
              x: evidence.x1,
              y: evidence.y1,
              text: evidence.text,
              page: pageNumber,
            };
          }),
        };
        setEvidence(evidenceInfo);
      } catch (error) {
        console.error("Error fetching configuration:", error);
      } finally {
      }
    },
    [oktaToken, token],
  );

  return {
    getEvidence,
    evidence,
    getConditionsEvidence,
  };
};

export default useEvidenceApi;
