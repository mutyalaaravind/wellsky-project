import { useEffect, useState, useCallback, useRef } from "react";
import useEnvJson from "./useEnvJson";
import axios from "axios";
import { Env } from "../types";

interface IExtractAdapter {
  extractedText: string;
  extract: (transcriptId: string, transcriptText: string, promptTemplate: string, model: string, enable_embedding: boolean, env: Env | null) => void;
  extractAsync: (transcriptId: string, transcriptText: string, promptTemplate: string, model: string, enable_embedding: boolean, env: Env | null) => void;
  extractSync: (transcriptId: string, transcriptText: string, promptTemplate: string, model: string, enable_embedding: boolean, env: Env | null) => void;
  extractionStatus: Record<string, number>;
  getStatusText: (value: number) => string;
  getStatusAsync: (transcriptId: string, prommptTemplate: any, env: Env | null) => void;
  getOverallStatus: () => string;
  busy: boolean;
  completionPercentage: number;
}

const useExtractApi = (transcriptIdProp: string, promptTemplateProp: any, env: any) => {

  const [extractedText, setExtractedText] = useState<string>("");
  // 0 - not started, 1 - started, 2 - completed, 3- errored
  const [extractionStatus, setExtractionStatus] = useState<Record<string, number>>({});
  const [busy, setBusy] = useState<boolean>(false);
  const [promptTemplate, setPromptTemplate] = useState<Record<string, any>>();
  const statusPollerIdRef = useRef<any>();
  const [transcriptVersion, setTranscriptVersion] = useState<number>(0);
  const [completionPercentage, setCompletionPercentage] = useState<number>(0);
  const [transcriptId, setTranscriptId] = useState<string | null>(null);
  const [chunkCount, setChunkCount] = useState<number>(0);

  const extractAsync = useCallback(async (transcriptId: string, transcriptText: string, promptTemplate: any, model: string, enable_embedding: boolean,transcript_version:number,env: any) => {
    setBusy(true);
    const res = await axios({
      method: "post",
      url: `${env?.API_URL}/api/extract`,
      headers: {},
      data: {
        transcript_id: transcriptId,
        transcript_text: transcriptText,
        json_template: promptTemplate, // TODO: Why is this text?
        model: model,
        enable_embedding: enable_embedding,
        transcript_version:transcript_version
      },
    });
  },[]);

  const extractSync = useCallback(async (transcriptId: string, transcriptText: string, promptTemplate: string, model: string, enable_embedding: boolean, transcript_version: number=0, env: any) => {
    setBusy(true);
    try {
      const res = await axios({
        method: "post",
        url: `${env?.API_URL}/api/extractSync`,
        headers: {},
        data: {
          transcript_id: transcriptId,
          transcript_text: transcriptText,
          json_template: promptTemplate, //template,
          model: model,
          enable_embedding: enable_embedding,
          transcript_version:transcript_version
        },
      });
      setExtractedText(res.data);
      setExtractionStatus({ "status": 2 });
    } catch (error) {
      console.log("error in extract", error);
      setExtractionStatus({ "status": 3 });
    }
  },[]);

  const getStatusAsync = async (transcriptId: string | null, transcriptVersion:number,env: any) => {
    setTranscriptId(transcriptId);
    setTranscriptVersion(transcriptVersion);
    await collect();
    const extractionStatusTemp: Record<string, number> = {};
    try {
      const resStatus = await axios({
        method: "get",
        url: `${env?.API_URL}/api/extract/${transcriptId}`,
        headers: {},
      });
      if (resStatus.data?.length === 0) {
        // no extraction ever happened
        console.log("no extraction ever happened");
        transcriptVersion && transcriptVersion > 0 ? extractionStatusTemp["status"] = 1: extractionStatusTemp["status"] = 2;
      }
      resStatus.data?.forEach((result: any) => {
        if (result) {
          if(result["chunk_schema"]  ) {
            const valueJson = result["chunk_schema"];
            if (valueJson["dataType"] && valueJson["dataType"] === "SECTION"){
                const sectionId = valueJson["localQuestionCode"];
                if (result["transcript_version"] && transcriptVersion && transcriptVersion > result["transcript_version"]) {
                  console.log("version mismatch",transcriptVersion,result["transcript_version"]);
                  extractionStatusTemp[sectionId] = 0;
                  return;
                }
                if (result["status"] === "errored") {
                  extractionStatusTemp[sectionId] = extractionStatusTemp[sectionId] < 3 ? extractionStatusTemp[sectionId] : 3;
                } else if (result["status"] === "pending" || result["status"] === "processing") {
                  extractionStatusTemp[sectionId] = 1;
                } else if (result["status"] === "completed") {
                  extractionStatusTemp[sectionId] = extractionStatusTemp[sectionId] < 2 ? extractionStatusTemp[sectionId] : 2;
                }
                else {
                  extractionStatusTemp[sectionId] = 0;
                }
            }
          }
          // Object.entries(result["chunk_schema"]).forEach(([key, value]: [string, any]) => {
          //   if (result["transcript_version"] && transcriptVersion && transcriptVersion > result["transcript_version"]) {
          //     console.log("version mismatch",transcriptVersion,result["transcript_version"]);
          //     extractionStatusTemp[key] = 1;
          //     return;
          //   }
          //   //console.log("key",key,"value",value);
          //   if (result["status"] === "errored") {
          //     extractionStatusTemp[key] = extractionStatusTemp[key] < 3 ? extractionStatusTemp[key] : 3;
          //   } else if (result["status"] === "pending" || result["status"] === "processing") {
          //     extractionStatusTemp[key] = 1;
          //   } else if (result["status"] === "completed") {
          //     extractionStatusTemp[key] = extractionStatusTemp[key] < 2 ? extractionStatusTemp[key] : 2;
          //   }
          //   else {
          //     extractionStatusTemp[key] = 0;
          //   }
          // });
        }
      });
      setExtractionStatus(extractionStatusTemp);

      // Calculate completion percentage
      let totalCount = 0;
      let finishedCount = 0;
      resStatus.data?.forEach((result: any) => {
        totalCount++;
        if (result["status"] === "completed" || result["status"] === "errored") {
          finishedCount++;
        }
        if(transcriptVersion > result["transcript_version"]){
          finishedCount = 0;
          return;
        }
      });
      
      if (totalCount === 0) {
        totalCount = 1;
        finishedCount = 0;
      }
      setCompletionPercentage(Math.round((finishedCount / totalCount) * 100));

    } catch (error) {
      console.log("error in extract", error);
    }
  }

  const getStatusText = (value: number) => {
    switch (value) {
      case 0:
        return "In Progress";
      case 1:
        return "In Progress";
      case 2:
        return "Completed";
      case 3:
        return "Errored";
      default:
        return "Not Started";
    }
  }

  const getOverallStatus = useCallback(() => {
    let overallStatuses = Array<number>();
    console.log("chunkCount check",chunkCount, Object.keys(extractionStatus).length, extractionStatus);
    // if (Object.keys(extractionStatus).length < chunkCount){
    //   return "In Progress";
    // }
    Object.entries(extractionStatus).forEach(([key, value]) => {
      overallStatuses.push(value);
    })
    // if no extraction ever happened
    overallStatuses.length === 0 ? overallStatuses.push(-1) : void (0);

    if (overallStatuses.includes(-1)) {
      return "No Extraction Run"
    }

    if (overallStatuses.includes(1)) {
      return "In Progress"
    }
    if (overallStatuses.includes(0)) {
      //some of them still not started
      return "In Progress"
    }
    // if (overallStatuses.includes(3) && overallStatuses.includes(2)){
    //   return "Completed with Some Errors"
    // }
    if (overallStatuses.includes(2)) {
      return "Completed"
    }
    if (overallStatuses.includes(3)) {
      return "Errored"
    }

    return "In Progress";
  }, [extractionStatus]);

  const getChunkCount = useCallback(async (transcriptId:string|null) => {
    if(transcriptId === null) return;
    const resStatus =await axios({
      method: "get",
      url: `${env?.API_URL}/api/getChunkCount?transcriptId=${transcriptId}`,
      headers: {},
    });
    setChunkCount(resStatus.data);
  }, [env?.API_URL]);


  const sanitizeExtractedOutput = useCallback(async (extractedJson: Record<string, any>) => {
    let extractedJsonObjSanitized: Record<string, any> = {};
    Object.entries(extractedJson).forEach(([key, value]) => {
      if (promptTemplate?.[key]) {
        extractedJsonObjSanitized[key] = value;
      }
    })
    return extractedJsonObjSanitized;
  }, [promptTemplate]);


  const collect = useCallback(async () => {
    console.log("collecting")
    const url = `${env?.API_URL}/api/extract/${transcriptId}/collect`;
    let res;
    if (window.hasOwnProperty('eafOverrides')) {
      res = await axios.post(url, {
        overrides: (window as any).eafOverrides
      }, {
        headers: {}
      });
    } else {
      res = await axios.get(url, {
        url,
        headers: {},
      });
    }
    setExtractedText(JSON.stringify(res.data));
    //setExtractedText(JSON.stringify(await sanitizeExtractedOutput(res.data)));
  }, [env?.API_URL, sanitizeExtractedOutput, transcriptId]);

  useEffect(() => {
    getChunkCount(transcriptId);
  },[transcriptId]);

  useEffect(() => {
    console.log(extractionStatus,"extractionStatus");
    if (typeof env?.API_URL === "undefined") {
      return;
    }
    if (getOverallStatus() !== "Completed" && getOverallStatus() !== "Errored") {
      setBusy(true);
      collect();
      // const id = setInterval(() => { getStatusAsync(transcriptId,transcriptVersion, env) }, 3000);
      // statusPollerIdRef.current = id;
    } else {
      collect();
      clearInterval(statusPollerIdRef.current);
    }
    if (getOverallStatus() === "Completed" || getOverallStatus() === "Errored") {
      setBusy(false);
    }
    return () => {
      if (statusPollerIdRef.current !== null) {
        clearInterval(statusPollerIdRef.current);
      }
    };
  }, [extractionStatus, env, transcriptId, promptTemplate,transcriptVersion, collect, getOverallStatus]);

  useEffect(() => {
    if (promptTemplateProp) {
      setPromptTemplate(promptTemplateProp);
    }
  }, [promptTemplateProp])

  return {
    extractionAdapter: {
      extractedText: extractedText,
      extractSync: extractSync,
      extractAsync: extractAsync,
      extractionStatus: extractionStatus,
      getStatusText: getStatusText,
      getStatusAsync: getStatusAsync,
      getOverallStatus: getOverallStatus,
      busy: busy,
      completionPercentage: completionPercentage,
    }
  };
}

export { useExtractApi }
