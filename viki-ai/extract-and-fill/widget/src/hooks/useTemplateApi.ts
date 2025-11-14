import useEnvJson from "./useEnvJson";
import { Env } from "../types";
import axios from "axios";
import { useCallback, useEffect, useState } from "react";

export const useTemplateApi = () => {
    
    const [promptTemplateId, setPromptTemplateId] = useState<string>("");
    const [questionnaireTemplateId, setQuestionnaireTemplateId] = useState<string>("");

    const savePromptTemplate =  useCallback(async (transcriptId: string, promptTemplate: any, model: string, env: any) => {
        if (transcriptId) {
            const response = await axios(`${env?.API_URL}/api/savePromptTemplate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                data:{"transcriptId":transcriptId,"promptTemplate":promptTemplate, "model":model}
            });
            const id = await response.data;
            setPromptTemplateId(id);
        }
    },[])

    const saveQuestionnaireTemplate = async (transcriptId: string, questionnaireTemplate: any, model: string, env: any) => {
        if (transcriptId) {
            const response = await axios(`${env?.API_URL}/api/saveQuestionnaireTemplate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                data:{"transcriptId":transcriptId,"questionnaireTemplate":questionnaireTemplate, "model":model}
            });
            const id = await response.data;
            setQuestionnaireTemplateId(id);
        }
    }

    return {
        promptTemplateId,
        questionnaireTemplateId,
        savePromptTemplate,
        saveQuestionnaireTemplate
    };
}