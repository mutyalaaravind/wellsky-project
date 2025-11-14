import { useState } from "react";
import { Env } from "../types";
import { set } from "lodash";

export const useDocumentsApi = () => {
  const [documentList, setDocumentList] = useState([] as any[]);
  const [busy, setBusy] = useState(false);
  const getDocuments = async (env: Env, patientId: string) => {
    setBusy(true);
    const response = await fetch(
      `${env.API_URL}/api/documents?patientId=${patientId}`,
      {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      },
    );
    const data = await response.json();
    setDocumentList(data);
    setBusy(false);
  };

  return { busy, documentList, getDocuments };
};
