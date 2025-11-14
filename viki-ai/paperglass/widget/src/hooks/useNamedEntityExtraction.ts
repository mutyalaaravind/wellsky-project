import { useCallback, useState } from "react";

export const useNamedEntityExtractionApi = (env: any) => {
    const [namedEntityExtractions, setNamedEntityExtractions] = useState<any[]>();
    const [busy, setBusy] = useState<boolean>(false);
    const [error, setError] = useState<any | null>(null);

    const getNamedEntityExtraction = useCallback(async (patientId: string, namedEntityType: string, documentId: string, currentPage: number) => {
        setBusy(true);
        setError(false);
        setNamedEntityExtractions([]);
        if (env) {
            const response = await fetch(env?.API_URL + `/api/medications?documentId=${documentId}&pageNumber=${currentPage}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            try {
                const data = await response.json()
                // hack for now to filter by docId
                console.log("setNamedEntityExtractions", data, documentId);
                setNamedEntityExtractions(data);
                //setNamedEntityExtractions(data?.filter((namedEntity: any) => namedEntity.reference?.document === documentId));
                setBusy(false);
            } catch (err) {
                console.error(err);
                setError(err);
                setBusy(false);
            }
        }
    }, [env]);

    return { getNamedEntityExtraction, busy, error, namedEntityExtractions }
}

