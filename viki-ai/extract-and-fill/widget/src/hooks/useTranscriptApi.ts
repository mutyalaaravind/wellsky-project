import useEnvJson from "./useEnvJson";
import { Env } from "../types";
import axios from "axios";
import { useCallback, useEffect, useState } from "react";

export const useTranscriptApi = () => {
    
    const [transcriptId, setTranscriptId] = useState<string>("");
    const [transcriptVersion, setTranscriptVersion] = useState<number>(0);

    const saveTranscript = async (autoScribeId: string, transcript: string, env: any) => {
        if (transcript) {
            const response = await axios(`${env?.API_URL}/api/saveTranscript`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                data:{"autoScribeTranscriptId":autoScribeId,"transcript":transcript}
            });
            const id = await response.data;
            setTranscriptId(id);
        }
    }

    const getTranscriptId = useCallback(async (autoScribeId: string, env: any) => {
        if (autoScribeId) {
            const response = await axios(`${env?.API_URL}/api/getTranscriptId?autoScribeTranscriptId=${autoScribeId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            const id = await response.data.transcriptId;
            const version = await response.data.transcriptVersion;
            setTranscriptId(id);
            setTranscriptVersion(version)
        }
    },[])

    return {
        transcriptId,
        transcriptVersion,
        saveTranscript,
        getTranscriptId
    };
}