import { useState } from "react";
import { APIStatus, AnnotationType, Env } from "../types";

export const useSummarizer = ( env: Env | undefined) => {
    const [evidences, setEvidences] = useState<any[] | null>(null);
    const [evidenceApiStatus, setEvidenceApiStatus] = useState<APIStatus>(APIStatus.COMPLETED);

    const findEvidences = (identifier: string | undefined, substring: string, annotationType: AnnotationType | undefined, confidenceThreshold: number) => {
        // Search evidence of a substring
            setEvidenceApiStatus(APIStatus.PROCESSING);
            setEvidences([]);
            fetch(`${env?.API_URL}/api/documents/${identifier}/find-evidence?substring=${substring}&annotationType=${annotationType}`).then(
                (response) => response.json()
            ).then((data) => {

                setEvidences(data);
                console.log("evidence received",data);
                setEvidenceApiStatus(APIStatus.COMPLETED);
            }).catch((error) => {
                console.log("error",error);
                setEvidenceApiStatus(APIStatus.ERRORED);
                setEvidences([]);
            });
        
    }

    return {findEvidences, evidences , evidenceApiStatus};
};