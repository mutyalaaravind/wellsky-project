import react, { useCallback, useState } from 'react';

export const useSearchApi = (env:any) => {
    const [results, setResults] = useState<any[]>([])
    const [summary, setSummary] = useState<any>({});
    const [ error, setError] = useState<boolean>(false);
    const [busy, setBusy] = useState(false);
    const search = useCallback(async (identifier:string, search_query: string) => {
        setBusy(true);
        setResults([]);
        const response = await fetch(env?.API_URL + `/api/search?identifier=${identifier}&search_query=${search_query}`);
        try{
            const data = await response.json()
            setResults(data.results);
            setSummary(data.summary);
            setBusy(false);
        } catch(error){
            console.error(error);
            setError(true);
            setBusy(false);
        }
    },[]);

    return { search, results, busy, summary, error }
}

export const useDocumentVectorSearchApi = (env:any) => {
    const [documentSearchResults, setDocumentSearchResults] = useState<any[]>();
    const [busy, setBusy] = useState<boolean>(false);
    const [error, setError] = useState<any | null>(null);

    const searchDocumentByVectors = useCallback(async (patientId: string, searchText:string,distanceThreshold:number=0.65,embeddingStrategy:number=0,searchQueryStrategy:string|null="") => {
        setBusy(true);
        setError(false);
        setDocumentSearchResults([]);
        if(env){
            const response = await fetch(env?.API_URL + `/api/searchDocumentsByVector?patientId=${patientId}&searchText=${searchText}&distanceThreshold=${distanceThreshold}&embeddingStrategy=${embeddingStrategy}&searchQueryStrategy=${searchQueryStrategy}`);
            try{
                const data = await response.json()
                setDocumentSearchResults(data);
                setBusy(false);
            } catch(err){
                console.error(err);
                setError(err);
                setBusy(false);
            }
        }
    },[env]);

    return {searchDocumentByVectors, busy,error, documentSearchResults}
}
