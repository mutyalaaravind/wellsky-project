import { Box, HStack } from "@chakra-ui/react";
import { useSentencesApi } from "../../hooks/useSentencesApi";
import { useEffect } from "react";
import { Env } from "../../types";
import useEnvJson from "../../hooks/useEnvJson";
import { useEmbeddingApi } from "../../hooks/useEmbeddingApi";

type TranscriptViewProps = {
    transcriptId: string;
    transcriptText?: null | string;
    evidence?: null | any;
    evidences?: null | Array<any>;
    evidenceRequestedFor?: null | any;
  };

export const TranscriptView = (props:TranscriptViewProps) => {
    const env = useEnvJson<Env>(); 
    const {sentences, getSentences} = useSentencesApi();

    useEffect(() => {
        if(env === null || env === undefined || props.transcriptId === "" || props.transcriptId === null || props.transcriptId === undefined) {
            return;
        }
        getSentences(props.transcriptId, env);
        // Remove this once we have embeddings part of queue based processing
        //createEmbeddings(props.transcriptId, env);
    },[props.transcriptId,env]);

    useEffect(() => {
        console.log("evidence", props.evidence);
        if (props.evidence && props.evidence?.sentence.sentence_id) {
            const element = document.getElementById(props.evidence?.sentence.sentence_id);
            console.log("evidence element", element);
            element?.scrollIntoView({
                behavior: "smooth",
                block: "center",
                inline: "nearest",
            });
        }
    },[sentences, props.evidence])

    useEffect(() => {
        if (props.evidenceRequestedFor && props.evidenceRequestedFor?.verbatim_source) {
            sentences?.forEach((sentence:any) => {
                props.evidenceRequestedFor?.verbatim_source.split("\n").find((verbatim: string) => {
                    if (sentence?.sentence?.includes(verbatim)) {
                        const element = document.getElementById(sentence?.sentence_id);
                        console.log("evidenceRequestedFor element", element);
                        element?.scrollIntoView({
                            behavior: "smooth",
                            block: "center",
                            inline: "nearest",
                        });
                        return true;
                    }
                    return false;
                });
            });

        }
    },[props.evidenceRequestedFor])

    const doesEvidenceExist = (sentenceId: string) => {
        
        const mathedEvidences = props.evidences?.find((sentence: any) => {
            if (sentence?.sentence.sentence_id === sentenceId) {
                return true;
            }
            return false;  
        });
        
        if (mathedEvidences !== undefined) {
            return true;
        } else{
            return false;
        }
    }

    const doesVerbatimExists = (sentence: string) => {
        
        const matchedVerbatim = props.evidenceRequestedFor?.verbatim_source.split("\n").find((verbatim: string) => {
            if (sentence?.includes(verbatim)) {
                return true;
            }
            return false;
        });

        if (matchedVerbatim){
            return true;
        }
        return false;
    }

    return (
        <>
            <Box verticalAlign={"top"}>
                {sentences?.map((sentence:any, index) => {
                    return (
                        <Box key={sentence.sentence_id} id={sentence.sentence_id} >
                            {(doesEvidenceExist(sentence.sentence_id)) ? <Box fontWeight={"bold"} backgroundColor={doesVerbatimExists(sentence?.sentence) ? "#AFEEEE":""}>{sentence.sentence}</Box>:<Box fontWeight={doesVerbatimExists(sentence?.sentence) ? "bold":"normal"} backgroundColor={doesVerbatimExists(sentence?.sentence) ? "#AFEEEE":""}>{sentence.sentence}</Box>}
                            {/* {props.evidence && props.evidence.sentence.sentence_id !== sentence.sentence_id && !doesEvidenceExist(sentence.sentence_id) && <Box>{sentence.sentence}</Box>} */}
                        </Box>
                    )
                })}
                {sentences?.length === 0 && <Box>Transcript Processing in Progress...</Box>}
            </Box>
        </>
    )
}