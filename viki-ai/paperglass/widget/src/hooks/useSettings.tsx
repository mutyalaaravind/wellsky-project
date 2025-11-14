import { useCallback, useState } from "react";
import { DocumentSettingsType, Env } from "../types";
import { set } from "lodash";

export const useSettingsApi = (env: Env) => {

    const [docSettings, setDocSettings] = useState<DocumentSettingsType>();

    const getDocumentSettings = useCallback(async (patientId: string) => {
        const res = await fetch(env?.API_URL + `/api/${patientId}/docsettings/`);
        const data = await res.json();
        setDocSettings(data);
    }, []);

    const setDocumentSettings = useCallback(async (patientId: string, docSettings: DocumentSettingsType) => {
        const res = await fetch(env?.API_URL + `/api/${patientId}/docsettings/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(docSettings),
        });
        setDocSettings(docSettings);
    }, []);

    return { docSettings, getDocumentSettings, setDocumentSettings };
}