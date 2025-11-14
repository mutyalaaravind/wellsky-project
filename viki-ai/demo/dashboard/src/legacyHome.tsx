import React, { useCallback, useEffect } from "react";
import { useOktaAuth } from '@okta/okta-react';
import CustomFormsComponent from "./components/custom-form";
import { PortalHeader } from "./components/portal-header";
import { Box, VStack, HStack, useToast, Button, Text } from '@chakra-ui/react'
import {AutoScribeBlock} from "./components/autoscribe";
import {ExtractAndFillBlock} from "./components/extract";
import logo from './images/wellsky-logo.png';
import { extendTheme } from '@chakra-ui/react'
import { Env } from "./types";
import { buildExtractPromptTemplate } from "./helpers/prompt";
import { LHCForm, FormAdapter } from "./components/lhc-form";
import { createPortal } from 'react-dom';
import { useSections } from "./hooks/useSections";
import { PrimaryButton, SecondaryButton } from "@mediwareinc/wellsky-dls-react";
import { AudioOutlined, SettingOutlined, CheckOutlined } from '@ant-design/icons';

// 2. Define the new text styles
const theme = extendTheme({
  textStyles: {
    h1: {
      // you can also use responsive styles
      fontSize: ['48px', '72px'],
      fontWeight: 'bold',
      lineHeight: '110%',
      letterSpacing: '-2%',
    },
    h2: {
      fontSize: ['36px', '48px'],
      fontWeight: 'semibold',
      lineHeight: '110%',
      letterSpacing: '-1%',
    },
  },
})



enum Stage {
  TRANSCRIPTION,
  ANNOTATION,
};

type LegacyHomeArgs = {
  env: Env;
};

const LegacyHome: React.FC<LegacyHomeArgs> = ({ env }: LegacyHomeArgs) => {
  // render a custom forms

  const { oktaAuth, authState } = useOktaAuth();
  const toast = useToast();

  const [stage, setStage] = React.useState<Stage>(Stage.TRANSCRIPTION);
  const [transcription, setTranscription] = React.useState<string>('');
  const [extractedText, setExtractedText] = React.useState<string>('');
  const [template, setFormTemplate] =  React.useState<any>([]);
  const [approvedFormFieldValues, setApprovedFormFieldValues] =  React.useState<any>([]);
  const [promptTemplate,setPromptTemplate] = React.useState<any>(null);
  const [formAdapter, setFormAdapter] = React.useState<FormAdapter | null>(null);
  const [sections, setSections] = React.useState<Array<any>>([]);
  const [activeAutoscribeSectionId, setActiveAutoscribeSectionId] = React.useState<string>("");
  const [activeExtractionSectionId, setActiveExtractionSectionId] = React.useState<string>("");
  const [transactionId, setTransactionId] = React.useState<string>("test-demo");
  const [extractInlineClicked, setExtractInlineClicked] = React.useState<number>(0);
  const [savedFormInstanceData, setSavedFormInstanceData] = React.useState<object>({});
  const [formLoadedFromSave, setFormLoadedFromSave] = React.useState<boolean>(false);

  const { getSectionData, existingSections,sectionTranscripts } = useSections();

  const replacer = (key:string, value:any) =>{
    return typeof value === 'undefined' ? null : value;
  }

  useEffect(() => {
    if(approvedFormFieldValues && formAdapter){
      console.log("approvedFormFieldValues", approvedFormFieldValues);
      formAdapter?.setFieldsValue(approvedFormFieldValues);
      //ToDo: save into DB
    }
  },[approvedFormFieldValues]);

  useEffect(() => {
    if (!authState) {
      return;
    }

    if (!authState?.isAuthenticated && !env.OKTA_DISABLE) {
      // const originalUri = toRelativeUrl(window.location.href, window.location.origin);
      oktaAuth.setOriginalUri('/');
      oktaAuth.signInWithRedirect();
    }

    if (!env.OKTA_DISABLE && authState?.isAuthenticated) {
      oktaAuth.getUser().then((info: any) => {
        setTransactionId(info.sub);
      });
    }
  }, [oktaAuth, authState, authState?.isAuthenticated, env.OKTA_DISABLE]);

  useEffect(()=>{
      getSectionData(transactionId ,sections,env);
  },[sections])

  useEffect(()=>{
    console.log("existingSections",existingSections);
},[existingSections])

  useEffect(()=>{
    console.log("activeExtractionSectionId",activeExtractionSectionId);
  },[activeExtractionSectionId])

  useEffect(() => {
    if (formLoadedFromSave) {
      // Form already loaded
      return;
    }
    if (formAdapter === null) {
      return;
    }
    if (!authState || (!authState?.isAuthenticated && !env.OKTA_DISABLE)) {
      // Wait till Okta settles
      return;
    }
    fetch(env.DEMO_API + '/api/form-instances/' + transactionId).then(async (response) => {
      if (response.status === 404) {
        // Form not found
      } else {
        const data = await response.json();
        console.log("savedFormInstanceData",data);
        setSavedFormInstanceData(data);
        setFormLoadedFromSave(true);
        formAdapter.setFieldsValue(data);
      }
    });
  }, [authState, env, transactionId, formAdapter, formLoadedFromSave]);
  const saveForm = useCallback(() => {
    if (formAdapter === null) {
      console.error('Form adapter not ready');
      return;
    }
    fetch(env.DEMO_API + '/api/form-instances/' + transactionId, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formAdapter.getFieldsValue()),
    }).then(async (response) => {
      if (response.status !== 204) {
        alert('Error saving form');
      } else {
        toast({
          title: 'Form saved',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
      }
    });
  }, [env, formAdapter, transactionId, toast]);

  if (!env) {
    return <div>Loading configuration...</div>;
  }

  if (!authState || (!authState?.isAuthenticated && !env.OKTA_DISABLE)) {
    return (<div>Checking login...</div>);
  }

  return <>
    <HStack align="center" w="100%" position="sticky" top={0} zIndex={9999999} backgroundColor="white">
      <VStack width="15%"  alignItems="left">
        <Box alignItems="left"><img src={logo} alt="wellsky"/></Box>
      </VStack>
      <VStack width="50%"  alignItems="left">
        <Box alignItems="left" style={{fontSize: '48px'}}>Clinician Saver</Box>
      </VStack>
      <HStack width="35%" alignItems="center" justifyContent="end">
        {authState?.isAuthenticated ? (
          <>
            <Box>
              Signed in as {authState?.idToken?.claims.name}
            </Box>
            <Box style={{paddingRight: '1rem'}}>
              <Button onClick={() => oktaAuth.signOut()}>
                Log out
              </Button>
            </Box>
          </>
        ) : null}
      </HStack>
    </HStack>
    <HStack align="top" w="100%">
      <VStack width="100%">
        {/* <Box><PortalHeader /></Box>
        <Box></Box> */}
        <Box width="100%"  >
        <LHCForm id="lhc-form" onFormReady={(schema:any,adapter:any) => {
              setPromptTemplate(JSON.parse(JSON.stringify(adapter?.getFieldsValue(),replacer)));
              setFormAdapter(adapter);
              setSections(adapter.getSections());
            }} />
        {sections.map((section) => {
          return <>
            {existingSections && existingSections.includes(section) ? createPortal(
                  <div style={{float: 'right'}}>
                    <SecondaryButton onClick={()=>{setActiveAutoscribeSectionId(section.id)}} leftIcon={<CheckOutlined />} >Autoscribe</SecondaryButton>
                    &nbsp;
                    <Button onClick={()=>{setActiveExtractionSectionId(section.id);setExtractInlineClicked(extractInlineClicked+1)}}>Review & Fill</Button>
                  </div>
                ,section.el):
                createPortal(
                  <div style={{float: 'right'}}>
                      <PrimaryButton onClick={()=>{setActiveAutoscribeSectionId(section.id)} } leftIcon={<AudioOutlined />} >Autoscribe</PrimaryButton>
                  </div>,
                section.el) 
            }
          </>
        })}
        {activeAutoscribeSectionId && <AutoScribeBlock 
                                                        widgetHost={env.AUTOSCRIBE_WIDGET_HOST} 
                                                        onConfirm={(text: any) => { 
                                                          // can get the latest confirmed section transcript
                                                          getSectionData(transactionId ,sections,env);
                                                          //reset the active section
                                                          setActiveAutoscribeSectionId("");
                                                        }} 
                                                        onCancel={()=>{setActiveAutoscribeSectionId("")}}
                                                        transactionId={transactionId} 
                                                        sectionId={activeAutoscribeSectionId} 
                                                      />}
        {<AutoScribeBlock widgetHost={env.AUTOSCRIBE_WIDGET_HOST} onConfirm={(text: Array<any>) => { let finalTranscript = "";text?.forEach(sentence=>finalTranscript=finalTranscript+sentence.text+"\n");setTranscription(finalTranscript); setStage(Stage.ANNOTATION) }} onCancel={()=>{setActiveAutoscribeSectionId("")}} />}
        { transcription &&
            <ExtractAndFillBlock
                                autoScribeTranscriptId={''}
                                widgetHost={env.EXTRACT_WIDGET_HOST}
                                transcriptText={transcription}
                                setApprovedFormFieldValues={setApprovedFormFieldValues}
                                promptTemplate={promptTemplate}
                                componentType="bubble"
                                onCancel={()=>{setActiveExtractionSectionId("")}}
                          />}
        { activeExtractionSectionId &&
            <ExtractAndFillBlock
                                transactionId={transactionId}
                                sectionId={activeExtractionSectionId}
                                widgetHost={env.EXTRACT_WIDGET_HOST}
                                transcriptText={sectionTranscripts[activeExtractionSectionId]}
                                setApprovedFormFieldValues={setApprovedFormFieldValues}
                                promptTemplate={activeExtractionSectionId ?formAdapter?.getFieldsValue(activeExtractionSectionId): promptTemplate}
                                componentType="inline"
                                extractInlineClicked={extractInlineClicked}
                          />}
        </Box>
        <PrimaryButton onClick={saveForm}>Save</PrimaryButton>
      </VStack>
    </HStack >
  </>
}

export default LegacyHome;
