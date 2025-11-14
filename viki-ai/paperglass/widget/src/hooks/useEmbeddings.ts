import { useCallback, useState } from "react";

export const useEmbeddingsApi = (env:any) => {
    const [documentEmbeddings, setDocumentEmbeddings] = useState<any[]>();
    const [busy, setBusy] = useState<boolean>(false);
    const [error, setError] = useState<any | null>(null);

    const getDocumentEmbeddings = useCallback(async (patientId: string,documentId:string,embeddingStrategy:number,embeddingChunkingStrategy:number) => {
        setBusy(true);
        setError(false);
        setDocumentEmbeddings([]);
        if(env){
            const response = await fetch(env?.API_URL + `/api/get_embeddings?patientId=${patientId}&embeddingStrategy=${embeddingStrategy}&embeddingChunkingStrategy=${embeddingChunkingStrategy}`);
            try{
                const data = await response.json()
                // hack for now to filter by docId
                setDocumentEmbeddings(data.filter((doc:any)=>{
                    if (doc.id.includes(documentId)){
                        return true;
                    }
                    return false;
                }));
                setBusy(false);
            } catch(err){
                console.error(err);
                setError(err);
                setBusy(false);
            }
        }
    },[env]);

    const reindexDocumentEmbeddings = useCallback(async (documentId:string,chunkIndex:number) => {
        setBusy(true);
        setError(false);
        if(env){
            const response = await fetch(env?.API_URL + `/api/document_vector_reindex?documentId=${documentId}&chunkIndex=${chunkIndex}`);
            try{
                const data = await response.json()
                // hack for now to filter by docId
                setBusy(false);
            } catch(err){
                console.error(err);
                setError(err);
                setBusy(false);
            }
        }
    },[env]);

    const updateDocumentEmbeddingStrategy = useCallback(async (documentId:string,embeddingStrategy:number,embeddingChunkingStrategy:number) => {
        setBusy(true);
        setError(false);
        if(env){
            const response = await fetch(env?.API_URL + `/api/update_document_embedding_strategy?documentId=${documentId}&embeddingStrategy=${embeddingStrategy}&embeddingChunkingStrategy=${embeddingChunkingStrategy}`);
            try{
                const data = await response.json()
                // hack for now to filter by docId
                setBusy(false);
            } catch(err){
                console.error(err);
                setError(err);
                setBusy(false);
            }
        }
    },[env]);


    return {getDocumentEmbeddings,reindexDocumentEmbeddings,updateDocumentEmbeddingStrategy, busy,error, documentEmbeddings}
}
    
