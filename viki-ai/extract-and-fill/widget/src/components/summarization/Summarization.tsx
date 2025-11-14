import { Button, Input } from "antd";
import axios from "axios";
import { useEffect, useState } from "react";
import useEnvJson from "../../hooks/useEnvJson";
import { Env } from "../../types";
import { useExtractApi } from "../../hooks/useExtractApi";

type SummarizationProps = {
  transcriptText: string;
  model: string;
};

export const Summarization = ({
  transcriptText,
  model
}: SummarizationProps) => {
  const [summarizeStatus, setSummarizeStatus] = useState<string>("");
  const [summarizedText, setSummarizedText] = useState<string>("");
  const [summarizePrompt, setSummarizePrompt] = useState<string>(
    "Please summarize the transcript in less than 300 words"
  );
  const env = useEnvJson<Env>();
  const { extractionAdapter } = useExtractApi("",null,env);

  const summarizeInit = async (e: string) => {
    if (env === null) {
      return;
    }
    console.log("summarizing", transcriptText);
    setSummarizeStatus("Initating Summarization");
    const promptTemplate = `${summarizePrompt}
        ${transcriptText}
        context: ${transcriptText}
        `;

    try{
      await extractionAdapter?.extractSync("", transcriptText, promptTemplate, model, false, 0,env);
    } catch(error){
      setSummarizeStatus("Error while Summarizing");
    }
    
  };

  useEffect(()=>{
    if (extractionAdapter?.extractedText !== "") {
      setSummarizedText(extractionAdapter?.extractedText);
      setSummarizeStatus("Summarization complete");
    }
  },[extractionAdapter?.extractedText])

  return (
    <>
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 4
      }}>
        <div>
        <p style={{ color: "Red" }}>{summarizeStatus}</p>
      </div>
      <div>
        <Button
          onClick={() => {
            summarizeInit(transcriptText);
          }}
        >
          Summarize
        </Button>
      </div>
      
      <div>
        <br></br>
        <Input
          value={summarizePrompt}
          onChange={(e: any) => {
            setSummarizePrompt(e.target.value);
          }}
        />
        <br></br>
      </div>
      </div>

      <br></br>
      <br></br>
      <div>{summarizedText}</div>
      {/* <Input.TextArea defaultValue={approvedText} value={JSON.stringify(approvedText)} onChange={OnSummarizationCompleted} /> */}
    </>
  );
};
