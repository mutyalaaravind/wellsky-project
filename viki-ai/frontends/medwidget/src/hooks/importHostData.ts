import { useCallback, useContext, useState } from "react";
import { Env } from "types";
import { AuthContext } from "context/AuthContext";
import { isLocal } from "utils/constants";

const enableSkipImportCalls = false;

const isSkipImportCalls = isLocal && enableSkipImportCalls;

export const useImportHostDataApi = () => {
  const authContext = useContext(AuthContext);
  const token = authContext.token;
  const oktaToken = authContext.oktaToken;
  const ehrToken = authContext.ehrToken;

  const [HostAttachment, setHostAttachments] = useState<
    Array<{ storage_uri: string }>
  >([]);

  const importMedications = useCallback(
    (env: Env) => {
      if (env === null || isSkipImportCalls) {
        return;
      }
      return fetch(`${env?.API_URL}/api/v2/medications/import`, {
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
            console.error("Error importing medications:", data.error);
            throw new Error(data.error);
          }
          return data;
        });
    },
    [token, oktaToken, ehrToken],
  );

  const importAttachments = useCallback(
    (env: Env) => {
      if (env === null) {
        return;
      }
      return fetch(`${env.API_URL}/api/v2/attachments/import`, {
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
            console.error("Error importing medications:", data.error);
            throw new Error(data.error);
          }
          setHostAttachments(data);
          return data;
        });
    },
    [token, oktaToken, ehrToken],
  );

  return { importMedications, importAttachments, HostAttachment };
};
