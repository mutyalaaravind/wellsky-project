import useEnvJson from "./useEnvJson";
import { Env, Evidence } from "../types";
import axios from "axios";
import { useEffect, useState } from "react";

export const useEmbeddingApi = () => {
    
    const [embeddingApiResponse, setEmbeddingApiResponse] = useState<boolean | null>(null);

    const createEmbeddings = async (transcriptId: string, env: any) => {
        if (transcriptId) {
            const res = await axios(`${env?.API_URL}/api/createEmbeddings`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                data:{"groupId":transcriptId}
            })
            
            setEmbeddingApiResponse(true);

        }
    }

    return {embeddingApiResponse,createEmbeddings};
}

export const useEmbeddingSearchApi = () => {

    const [embeddingSearchApiResponse, setEmbeddingSearchApiResponse] = useState<Array<Evidence> | null>(null);

    const search = async (transcriptId: string, question:string, answer:string, relevanceScoreThreshold: number, env: any) => {
        // const res1 = await axios({
        //     method: 'post',
        //     url: `${(env as any).API_URL}/api/search`,
        //     headers:{},
        //     data:{
        //       transcript_id: transcriptId,
        //       query_strings: [question]
        //     }
        //   });
        // setEmbeddingSearchApiResponse(res1.data);
        const res2 = await axios({
            method: 'post',
            url: `${(env as any).API_URL}/api/search`,
            headers:{},
            data:{
              transcript_id: transcriptId,
              query_strings: [ answer ? answer: question]
            }
          });
        setEmbeddingSearchApiResponse(res2.data?.filter((item:any)=>item.distance>relevanceScoreThreshold));
    }

    return {embeddingSearchApiResponse,search};

}

export const useEmbeddingStatusApi = () => {
    const [embeddingStatusApiResponse, setEmbeddingStatusApiResponse] = useState<boolean>(false);
    const [embeddingPollerId, setEmbeddingPollerId] = useState<any>(null);

    const getEmbeddingStatus = async (transcriptId: string, env: any) => {
        const callEmbeddingStatusApi = async (transcriptId: string, env: any) => {
            const res = await axios({
                method: 'get',
                url: `${(env as any).API_URL}/api/getEmbeddingsStatus?groupId=${transcriptId}`,
                headers:{},
                data:{
                groupId: transcriptId,
                }
            });
            setEmbeddingStatusApiResponse(res.data?.status);
        }
        const id = setInterval(()=>{callEmbeddingStatusApi(transcriptId,env)},5000);
        setEmbeddingPollerId(id);
    }

    useEffect(()=>{
        if(embeddingStatusApiResponse === true && embeddingPollerId){
            clearInterval(embeddingPollerId);
        }
        return () => embeddingPollerId ? clearInterval(embeddingPollerId): void(0);
    },[embeddingStatusApiResponse])

    return {embeddingStatusApiResponse,getEmbeddingStatus};
}