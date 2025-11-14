import { AuthContext } from "context/AuthContext";
import { EnvContext } from "context/EnvContext";
import { useCallback, useContext } from "react";
import { usePatientProfileStore } from "store/patientProfileStore";

export const usePageOcrApi = () => {
  const authContext = useContext(AuthContext);
  const token = authContext.token;
  const oktaToken = authContext.oktaToken;
  const ehrToken = authContext.ehrToken;

  const {setPageOcrStatus} = usePatientProfileStore();

  const env = useContext(EnvContext);

  const triggerOcr = useCallback(
    (documentId:string, pageNumber:number) => {
      
      return fetch(`${env?.API_URL}/api/v4/trigger_page_ocr/${documentId}/${pageNumber}`, {
        method: "POST",
        headers: {
          Authorization: "Bearer " + token,
          "okta-token": oktaToken,
          "ehr-token": ehrToken,
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.error) {
            console.error("Error triggering ocr:", data.error);
            throw new Error(data.error);
          }
          return data;
        });
    },
    [token, oktaToken, ehrToken,env],
  );

  const getPageOcrStatus = useCallback(
    (documentId:string, pageNumber:number) => {
      
      return fetch(`${env?.API_URL}/api/v4/ocr/${documentId}/${pageNumber}/status`, {
        method: "GET",
        headers: {
          Authorization: "Bearer " + token,
          "okta-token": oktaToken,
          "ehr-token": ehrToken,
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.error) {
            console.error("Error triggering ocr:", data.error);
            throw new Error(data.error);
          }
          console.log("data.status",data.status);
          setPageOcrStatus(documentId,pageNumber,data.status);
        });
    },
    [token, oktaToken, ehrToken,env, setPageOcrStatus],
  );

  return { triggerOcr,getPageOcrStatus };

};