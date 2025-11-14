import React, { useEffect, useState } from "react";

import "./Extract.css";

import {
  FloatButton,
  Drawer,
  Button,
  Input,
  Tabs,
  TabsProps,
  Switch,
} from "antd";


import useEnvJson from "./hooks/useEnvJson";
import { Summarization } from "./components/summarization/Summarization";
import { Env } from "./types";
import { useTranscriptApi } from "./hooks/useTranscriptApi";
import { EvidenceReviewView } from "./components/evidence-with-review/Evidence-Review";
import { Box, Grid, NumberDecrementStepper, NumberIncrementStepper, NumberInput, NumberInputField, NumberInputStepper, Text } from "@chakra-ui/react";
import { NLParseBlock } from "./components/nlparse/NLParseBlock";
import { Badge, LinkButton, Popover, Select } from "@mediwareinc/wellsky-dls-react";
import { SettingOutlined } from "@ant-design/icons/lib/icons";
import { Dropdown } from "@mediwareinc/wellsky-dls-react-icons";
import { useTemplateApi } from "./hooks/useTemplateApi";

type ExtractManagerProps = {
  transactionId?: string;
  sectionId?: string;
  transcriptText?: null | string;
  model?: string;
  setApprovedFormFieldValues?: (approvedFields: any) => {};
  onApprovedFormFieldValues?: (approvedFields: any) => void;
  promptTemplate?: any;
  questionnaireTemplate?: any;
  onCancel?: () => void;
};



// Main component for the widget
const ExtractManager: React.FC<ExtractManagerProps> = ({
  transactionId,
  sectionId,
  transcriptText,
  setApprovedFormFieldValues,
  promptTemplate,
  questionnaireTemplate,
  onCancel
}: ExtractManagerProps) => {


  const { transcriptId, transcriptVersion, saveTranscript, getTranscriptId } = useTranscriptApi();

  const [approvedExtractedText, setApprovedExtractedText] = React.useState<string>("");
  const [relevanceScore, setRelevanceScore] = React.useState<number>(0.7);
  const [model, setModel] = React.useState<string>("medlm-medium");
  const [showEmbeddingStatus, setShowEmbeddingStatus] = React.useState<boolean>(false);
  const [showNLPParserWidget, setShowNLPParserWidget] = React.useState<boolean>(false);
  const [showSummarization, setShowSummarization] = React.useState<boolean>(false);
  const { savePromptTemplate, saveQuestionnaireTemplate } = useTemplateApi();

  const env = useEnvJson<Env>();

  useEffect(() => {
    console.log("ExtractManager:useEffect:transactionId", transactionId, sectionId, transcriptText);
    if (env === null) {
      // env.json not loaded yet
      return;
    }
    transactionId ? getTranscriptId(sectionId ? `${transactionId}-${sectionId}` : transactionId || "", env) :
      saveTranscript("", transcriptText || "", env);

  }, [transactionId, sectionId, transcriptText, env]);

  useEffect(() => {
    if (promptTemplate && transcriptId) {
      savePromptTemplate(transcriptId, promptTemplate, model, env);
      saveQuestionnaireTemplate(transcriptId, questionnaireTemplate, model, env);
    }
  }, [transcriptId, env, promptTemplate,model])

  const EvidenceReviewComponent = () => {
    return <>
    <EvidenceReviewView
            transcriptId={transcriptId}
            transcriptVersion={transcriptVersion}
            transcriptText={transcriptText}
            setApprovedFormFieldValues={setApprovedFormFieldValues}
            onApprovedFormFieldValues={(text) => {
              setApprovedExtractedText(text);
            }}
            promptTemplate={promptTemplate}
            questionnaireTemplate={questionnaireTemplate}
            sectionId={sectionId}
            transactionId={transactionId}
            relevanceScoreThreshold={relevanceScore}
            model={model}
            showEmbeddingStatus={showEmbeddingStatus}
          />
    </>
  }

  const items: TabsProps["items"] = [
    {
      key: "1",
      label: "Review",
      children: (
        <>
          <EvidenceReviewComponent />
        </>
      ),
    },
    {
      key: "2",
      label: "NLP Extract",
      disabled: !showNLPParserWidget,
      children: (
        <>
          <NLParseBlock
            text={transcriptText}
            widgetHost={env?.NLPARSE_WIDGET_HOST}
          />
        </>
      ),
    },
    {
      key: "3",
      label: "Summarization",
      disabled: !showSummarization,
      children: (
        <>
          <Summarization
            transcriptText={transcriptText || ""}
            model={model}
          />
        </>
      ),
    },
  ];

  

  if (env === null) {
    return <>Loading configuration...</>;
  }

  return (
    <>
      <div style={{ width: "100%", display: "flex", flex: 1, flexDirection: "column", alignItems: 'stretch' }}>
        {/* <Box width="40%" height="80vh" borderTop="1px" borderColor="gray.200"> */}
        <Box borderBottom="1px" borderColor="gray.200" paddingY={1}>
          <div style={{ float: 'right' }}>
            <Popover title="Settings" content={(
              <Box>
                <Box>
                  <Box>Relevance Score Threshold:</Box>
                  <Box>
                  <NumberInput
                    defaultValue={relevanceScore} min={0.4} max={1.0} precision={2} step={0.05}
                    onChange={(valueString) => { setRelevanceScore(parseFloat(valueString)) }}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                  </Box>
                </Box>
                <Box>
                  <Box>Select the Model:</Box>
                  <Box>
                    <Select onChange={(e: any) => { console.log("moddel changed", e); setModel(e.target.value) }} value={model}>
                      <option value="text-bison-32k@002">Text Bison 32 K</option>
                      <option value="medlm-medium">MedLM-Medium</option>
                      <option value="medlm-large">MedLM-Large</option>
                      <option value="gemini-pro">Gemini-Pro</option>
                    </Select>
                  </Box>
                </Box>
                <Box>
                  <Box>Show Embedding Status:</Box>
                  <Box>
                    <Switch checked={showEmbeddingStatus} onChange={(e) => { setShowEmbeddingStatus(e) }} />
                  </Box>
                </Box>
                <Box>
                  <Box>Show NLP Parser</Box>
                  <Box>
                  <Switch checked={showNLPParserWidget} onChange={(e) => { setShowNLPParserWidget(e) }} />
                  </Box>
                </Box>
                <Box>
                  <Box>Summarization</Box>
                  <Box>
                  <Switch checked={showSummarization} onChange={(e) => { setShowSummarization(e) }} />
                  </Box>
                </Box>
              </Box>
            )} trigger="click">
              <LinkButton><SettingOutlined /></LinkButton>
            </Popover>
          </div>
          <Text fontSize="lg" fontWeight="bold">
            Oasis-E start of care Assessment
          </Text>
        </Box>
        {/*sectionId && <Text fontSize="sm" fontWeight="bold" paddingY={2}>
          Section: {sectionId}
          </Text>*/}
          {/* dirty hack, but todo: tab base show/hiding*/}
          {(showNLPParserWidget || showSummarization) ? 
          <Tabs items={items} style={{ display: 'flex', flexDirection: 'column', flex: 1, alignItems: 'stretch' }} className="antd-with-flex-content" />
          : <EvidenceReviewComponent />}
      </div>
      {/* </Drawer> */}
    </>
  );
};

export default ExtractManager;
