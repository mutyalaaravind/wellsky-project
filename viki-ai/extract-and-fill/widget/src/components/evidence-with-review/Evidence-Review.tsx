import { Box, VStack, HStack, useToast, Button, Text, IconButton, Modal, ModalOverlay, ModalContent, ModalCloseButton, ModalHeader, ModalBody, ModalFooter, useDisclosure, useStatStyles, ChakraProvider } from '@chakra-ui/react'
import { PhoneIcon, AddIcon, WarningIcon } from '@chakra-ui/icons'
import { Review } from '../lforms/review/Review';
import AnnotatedForm, { AnnotatedFormProps } from '../review/AnnotatedFormV3';
import React, { memo, useEffect } from 'react';
import { TranscriptView } from '../transcript/TranscriptView';
import { useEmbeddingApi, useEmbeddingSearchApi, useEmbeddingStatusApi } from '../../hooks/useEmbeddingApi';
import useEnvJson from '../../hooks/useEnvJson';
import { Env, Evidence } from '../../types';
import { EvidenceGuide } from './EvidenceGuide';
import { useExtractApi } from '../../hooks/useExtractApi';
import { Checkbox, Spinner, Tooltip } from '@mediwareinc/wellsky-dls-react';
import { AutoScribeWidgetBlock } from '../autoscribe/AutoScribeBlock';

type EvidenceReviewProps = {
  transcriptId: string;
  transactionId?: string;
  transcriptText?: null | string;
  transcriptVersion?: number;
  extractedText?: null | string;
  model: string;
  setApprovedFormFieldValues?: (approvedFields: any) => {};
  onApprovedFormFieldValues?: (approvedFields: any) => void;
  promptTemplate?: any;
  questionnaireTemplate?: any;
  sectionId?: string;
  relevanceScoreThreshold: number;
  showEmbeddingStatus: boolean;
}

const MemoizedAnnotatedForm = React.memo(AnnotatedForm,
  ((prevProps: Readonly<AnnotatedFormProps>, nextprops: Readonly<AnnotatedFormProps>) => {
    //console.log("memoprops", prevProps.originalData, nextprops.originalData, prevProps.newData, nextprops.newData, prevProps.originalData === nextprops.originalData, prevProps.newData === nextprops.newData);
    return prevProps.originalData === nextprops.originalData && JSON.stringify(prevProps.newData) === JSON.stringify(nextprops.newData);
  }));

export const EvidenceReviewView = (props: EvidenceReviewProps) => {
  const [evidences, setEvidences] = React.useState<Array<string>>();
  const env = useEnvJson<Env>();
  const { embeddingSearchApiResponse, search } = useEmbeddingSearchApi();
  const { embeddingStatusApiResponse, getEmbeddingStatus } = useEmbeddingStatusApi();
  const { extractionAdapter } = useExtractApi(props.transcriptId, props.promptTemplate, env);
  const [verbatimSourceEvidence, setVerbatimSourceEvidence] = React.useState<any>(null);
  const [reviewStatus, setReviewStatus] = React.useState<boolean>(false);
  const [finalChanges, setFinalChanges] = React.useState<any>({});

  const StatusModal = () => {
    const { isOpen, onOpen, onClose } = useDisclosure();
    return <>
      <ChakraProvider>
        <IconButton onClick={() => { onOpen() }} aria-label='Extraction Status' icon={<WarningIcon />} />
        <Modal isOpen={isOpen} onClose={onClose} size={"lg"}>
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>Extraction Status</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              {Object.entries(extractionAdapter?.extractionStatus).map(([key, value]) => {
                return <Box key={key}><b>{key}</b>:&nbsp;{extractionAdapter?.getStatusText(value)}</Box>
              })}
            </ModalBody>
            <ModalFooter>
              <Button colorScheme='blue' mr={3} onClick={onClose}>
                Close
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      </ChakraProvider>
    </>
  }

  useEffect(() => {
    if (props.showEmbeddingStatus) {
      getEmbeddingStatus(props.transcriptId, env);
    }
  }, [props.showEmbeddingStatus, env])

  useEffect(() => {
    if (embeddingSearchApiResponse) {
      let evidencesTemp: Array<string> = [];
      embeddingSearchApiResponse?.forEach((evidence: Evidence) => {
        evidencesTemp.push(evidence.sentence?.sentence);
      });
      setEvidences(evidencesTemp);
    }
  }, [embeddingSearchApiResponse])

  useEffect(() => {
    console.log("props", props);
    if (props.transcriptId === "" || props.transcriptText === "") { return; }
    extractionAdapter?.getStatusAsync(props.transcriptId, props.transcriptVersion || 0,env);

  }, [props.model, props.transcriptId, props.transcriptText, env])

  useEffect(() => {
    if (props.transcriptId === "" || props.transcriptText === "") { return; }
    if (extractionAdapter?.getOverallStatus() === "No Extraction Run" || extractionAdapter?.getOverallStatus() === "Errored") {
      // something happened in backend that resulted in extraction failure or no extraction run. lets trigger extraction
      // as a fallback
      //extractionAdapter?.extractAsync(props.transcriptId, props.transcriptText || "", props.promptTemplate, props.model, true,0, env);
    }
  }, [extractionAdapter,props.transactionId,props.transcriptId,props.transcriptText])

  console.log('BUSY:', extractionAdapter?.busy);
  console.log("props", props);

  return (
    <>
      <HStack width={"100%"} align={"top"} flex={1}>
        {/* Left side */}
        <Box width={"40%"} minHeight="0" position="relative" display="flex" flexDirection="column" gap="1rem">
          {props.showEmbeddingStatus && <Box fontWeight={"bold"}>Embedding status: {embeddingStatusApiResponse ? 'Completed' : 'In Progress'}</Box>}
          <Box height={"30px"} fontWeight={"bold"} borderColor='gray.200' paddingTop="1rem">Transcript</Box>
          {env?.AUTOSCRIBE_WIDGET_HOST && <AutoScribeWidgetBlock
            transactionId={props.transactionId}
            sectionId={props.sectionId}
            widgetHost={env?.AUTOSCRIBE_WIDGET_HOST}
            inlineWidgetEmbedding={true}
            evidences={evidences}
            verbatimSourceEvidence={verbatimSourceEvidence}
            onConfirm={(text: Array<any>, transactionId: string, sectionId: string, version: number) => {
                console.log("autoscribeVersion", transactionId, sectionId, version);
                let finalTranscript = ""; text?.forEach(sentence => finalTranscript = finalTranscript + sentence.text + "\n");
                //extractionAdapter?.extractAsync(props.transcriptId, finalTranscript, props.promptTemplate, props.model, true, env);
                extractionAdapter?.getStatusAsync(props.transcriptId,version, env);
            }
            }
          />}
        </Box>
        {/* Right side */}
        <Box width={"60%"} borderColor='gray.200' minHeight="min-content" position="relative">
          <div style={{ position: 'absolute', top: '0', left: '0', right: '0', bottom: '0', display: 'flex', flexDirection: 'column' }}>
            <Box borderColor='gray.200' width={"100%"} flexDirection="column">
              {/*
              <Box width={"100%"} fontWeight={"bold"}>
                {extractionAdapter?.getOverallStatus() === "In Progress" && <Spinner size="sm" color="blue.500" speed="0.65s" emptyColor="gray.200" thickness="4px" />}
                Extraction Status:&nbsp;{extractionAdapter?.getOverallStatus()}&nbsp;
                <StatusModal />
              </Box>
              */}
              <Box>
                <div style={{ width: '100%', height: '100%', paddingLeft: '12px', paddingRight: '12px', paddingTop: '16px', paddingBottom: '16px', background: '#2D9CDB', justifyContent: 'space-between', alignItems: 'center', display: 'inline-flex' }}>
                  <div style={{ color: 'white', fontSize: '14px', fontFamily: 'Roboto', fontWeight: '600', lineHeight: '30px', wordWrap: 'break-word' }} >Start of Care</div>
                </div>
              </Box>
            </Box>
            <Box flex="1" display="flex" minHeight="0" marginTop="1rem" marginBottom="1rem" position="relative" style={{ pointerEvents: extractionAdapter?.busy ? 'none' : 'auto' }}>
              <div style={{display: 'flex', flex: '1 1 0', position: 'relative', width: '100%'}}>
                {extractionAdapter?.busy && (
                  <div style={{ position: 'absolute', top: '0', left: '0', right: '0', bottom: '0', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: 'rgba(255, 255, 255, 0.8)', zIndex: '1000' }}>
                    <Spinner />
                    <div style={{ marginTop: '1rem' }}>Extraction in progress</div>
                    <div style={{ marginTop: '1rem', fontSize: '1.5rem' }}>{extractionAdapter?.completionPercentage}%</div>
                  </div>
                )}
                <div style={{flex: '1 1 0', display: 'flex', width: '100%', overflowY: 'auto'}}>
                  {<MemoizedAnnotatedForm
                    originalData={props.promptTemplate}
                    newData={extractionAdapter?.extractedText ? JSON.parse(extractionAdapter?.extractedText) : {}}
                    schema={props.questionnaireTemplate}
                    onPreferenceChange={(e: any) => {
                      setFinalChanges(e);
                    }}
                    onEvidenceRequested={(e: any) => {
                      console.log("Evidence requested for", e);
                      search(props.transcriptId, e.question, e.verbatim_source || e.answer, props.relevanceScoreThreshold, env);
                      setVerbatimSourceEvidence(e.verbatim_source);
                    }}
                    />}
                </div>
              </div>
            </Box>
            <Box>
              <Box textAlign="center">
                <Checkbox onChange={(e) => { console.log(e.target.checked); setReviewStatus(e.target.checked); }}>I have Reviewed all the values</Checkbox>&nbsp;
              </Box>
              <Box textAlign="center">
                <Tooltip placement="bottom" label={<div>Please review the form and check the checkbox to apply changes</div>}>
                  <Button isActive={reviewStatus} isDisabled={!reviewStatus} onClick={(e) => {
                    props.setApprovedFormFieldValues?.(finalChanges);
                  }}>Apply Changes</Button>
                </Tooltip>
              </Box>
            </Box>
          </div>
        </Box>
      </HStack>
    </>
  )
}
