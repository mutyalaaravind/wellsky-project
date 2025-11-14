import { useEffect, useState } from "react";
import useEnvJson from "./useEnvJson";
import axios from "axios";
import { Env } from "../types";

const useSentencesApi = () => {

    const env = useEnvJson<Env>();
    const [sentences, setSentences] = useState<[]>([]);
    
    const getSentences = async (groupId:string,env?:any) => {
        const res = await axios({
            method: "post",
            url: `${env?.API_URL}/api/getSentenceByGroupId`,
            headers: {},
            data: {
              groupId: groupId
            },
          });

        //firestore stores sentences lexically, so we need to sort by sentence_id
        //sentence_id is in the form of "sentence#1"
        const sortedSenteces = await res.data.sort((a:any, b:any) => (
            parseInt(a.sentence_id.split("#")[1]) >  parseInt(b.sentence_id.split("#")[1]) ? 1:-1
          )
        )

        setSentences(sortedSenteces);
    }

    return {sentences, getSentences};
}

export { useSentencesApi }