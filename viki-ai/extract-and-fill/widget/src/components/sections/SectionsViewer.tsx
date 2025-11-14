import { memo, useCallback, useEffect, useState } from "react";
import { Env, Evidence } from "../../types";
import { Box, ChakraProvider, HStack, VStack } from "@chakra-ui/react";
import { AutoScribeWidgetBlock, AutoScribeWidgetBubble } from "../autoscribe/AutoScribeBlock";
import useEnvJson from "../../hooks/useEnvJson";
import { SectionList, Section } from "./SectionList";
import CustomFormAnnotatedForm, { CustomFormAnnotatedFormProps } from "../review/AnnotatedFormV4";
import { Button } from "antd";
import { useExtractApi } from "../../hooks/useExtractApi";
import { useTranscriptApi } from "../../hooks/useTranscriptApi";
import { useTemplateApi } from "../../hooks/useTemplateApi";
import { useEmbeddingSearchApi } from "../../hooks/useEmbeddingApi";
import { Settings } from "../settings";
import CustomFormsComponent, { CustomFormsComponentProps } from "../custom-form";
import { LinkButton } from "@mediwareinc/wellsky-dls-react";

const SECTION_TO_CF_MAPPING: any = {
    "C": "COGNITIVE_FORM",
    // "N": "MEDICATION_FORM",
    "N": "MEDICATION_NEW",
    "I": "ACTIVE_DIAGNOSIS_UPDATED",
    //"I":"ENDOCRINE_UPDATED",
    "B": "HEARING_UPDATED",
    "H": "BLADDER_AND_BOWL_UPDATED",
    //"I":"ENVIRONMENT_CONDITIONS_UPDATED",
    "K": "SWALLOWING_UPDATED",
    //"I":"VITALS_UPDATED",
    //"I":"RESPIRATORY_STATUS_UPDATED",
    "J": "HEALTH_CONDITIONS_UPDATED",
    "A": "ADMINISTRATIVE_UPDATED",
    //"I":"CARDIAC_UPDATED",
    "F": "PREFERENCES_FOR_CUSTOMER_ROUTINE_UPDATED",
    "G": "FUNCTIONAL_STATUS_UPDATED",
    //"I":"PATIENT_HISTORY_UPDATED",
    "M": "SKIN_CONDITIONS_UPDATED",


}



const MemoizedAnnotatedForm = memo(CustomFormsComponent,
    ((prevProps: Readonly<CustomFormsComponentProps>, nextprops: Readonly<CustomFormsComponentProps>) => {
        //console.log("memoprops", prevProps.originalData, nextprops.originalData, prevProps.newData, nextprops.newData, prevProps.originalData === nextprops.originalData, prevProps.newData === nextprops.newData);
        return JSON.stringify(prevProps.newData) === JSON.stringify(nextprops.newData);
    }));

export const SectionsViewer = (props: { schema: any, transactionId: any }) => {
    const env: Env | null = useEnvJson();
    const [evidences, setEvidences] = useState<Array<string>>();
    const [selectedSectionId, setSelectedSectionId] = useState<string | null>(null);
    const [selectedSectionData, setSelectedSectionData] = useState<any | null>(null);
    const [sectionValues, setSectionvalues] = useState<any | null>(null);
    const [sections, setSections] = useState<Array<Section>>([]);
    const [savedTranscriptVersion, setSavedTranscriptVersion] = useState<number>(0);
    const [verbatimSourceEvidence, setVerbatimSourceEvidence] = useState<any>(null);
    const [model, setModel] = useState<string>("medlm-medium");
    const [relevanceScore, setRelevanceScore] = useState<number>(0.7);

    // hooks
    const { embeddingSearchApiResponse, search } = useEmbeddingSearchApi();
    const { extractionAdapter } = useExtractApi(props.transactionId, null, env);
    const { getTranscriptId, transcriptId } = useTranscriptApi();
    const { savePromptTemplate } = useTemplateApi();

    const onEvidenceRequested = (fieldId: any) => {
        console.log("Evidence requested for", fieldId);
        // search(transcriptId, e.question, e.verbatim_source || e.answer, relevanceScore, env);
        // setVerbatimSourceEvidence(e.verbatim_source);
    };

    const getSectionValues = useCallback((sectionId: string, sectionData: any) => {
        sectionData["C"] = {
            "bims_C0200_C0500.C0300_section.C0300_a_radio": {
              "value": "2",
              "verbatim_source": "Clinician- (C0300) Temporal Orientation​(Orientation to year, month, and day):\n“Please tell me what year it is right now”\nPatient – 2022"
            },
            "ds_section_1708000588.cognitive_radio_1708001390": {
              "value": null,
              "verbatim_source": null
            },
            "section_1707994970.severity_score": {
              "value": "3",
              "verbatim_source": "“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Feeling tired or having little energy”\nPatient- oh yes for sure\n“About how often have you been bothered by this? \nNo (Never or 1 day) \n1. 2 to 6 days (several days) \n2. 7-11 days (half or more of the days) \n3. 12-14 days (nearly every day)”\nPatient- I’m tired every day"
            },
            "section_1707994970.social_isolation": {
              "value": "2",
              "verbatim_source": "“How often do you feel lonely or isolated from those around you?”  \nPatient- Sometimes, I wish I got to see my family more often"
            },
            "section_1707994970.disruptive_behaviour": {
              "value": "0",
              "verbatim_source": "Upon completion of the BIMS- Clinician CAM assessment  \nThe patient has no evidence of acute change in mental status.  She is able to pay attention and think clearly.  The patient did not display any altered level of consciousness."
            },
            "section_1707994970.question_b.symptom_presence_option_b": {
              "value": "1",
              "verbatim_source": "D0150 Patient Mood Interview (PHQ-2 to PHQ-9)\n“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Feeling down, depressed, or hopeless”\nPatient- MMM Sometimes"
            },
            "ds_section_1708000588.confused_radio_1708002707": {
              "value": null,
              "verbatim_source": null
            },
            "mental_status_01.orientation_01.person_01": {
              "value": "true",
              "verbatim_source": "Clinician- (C0200)  \nRepetition of Three Words​Ask patient“I am going to say three words for you to remember. Please repeat the words after I have said all three. The words are: sock, blue, and bed. Now tell me the three words.”\nPatient- sock, blue, bed"
            },
            "mental_status_01.orientation_01.time_01": {
              "value": "true",
              "verbatim_source": "Clinician- (C0300) Temporal Orientation​(Orientation to year, month, and day):\n“Please tell me what year it is right now”\nPatient – 2022\n“What month are we in right now?”\nPatient- September\nWhat day of the week is today?”\nPatient- Saturday"
            },
            "ds_section_1708000588.ds_thinking_radio_1707998219": {
              "value": null,
              "verbatim_source": null
            },
            "bims_C0200_C0500.C0400_recall_secton.C0400_b_radio": {
              "value": "2",
              "verbatim_source": "Clinician- (C0400) Recall:\n“Let's go back to an earlier question. What were those three words that I asked you to repeat?”\nIf unable to remember a word, give cue (something to wear, a color, a piece of furniture) for that word.\nPatient- sock, blue, bed"
            },
            "section_1707994970.symptom_frequency_options_c": {
              "value": null,
              "verbatim_source": "“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Trouble falling or staying asleep, or sleeping too much”\nPatient – no"
            },
            "section_1707994970.symptom_frequency_options_f": {
              "value": null,
              "verbatim_source": "“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Feeling bad about yourself - or that you are a failure or have let yourself or your family down”\nPatient- no"
            },
            "section_1707994970.symptom_frequency_options_i": {
              "value": null,
              "verbatim_source": "“Over the last 2 weeks, have you been bothered by any of the following problems?”\n “Thoughts that you would be better off dead, or of hurting yourself in some way”\nPatient- definitely no"
            },
            "section_1707994970.cognitive_behavioural_psychiatric": {
              "value": "7",
              "verbatim_source": "Upon completion of the BIMS- Clinician CAM assessment  \nThe patient has no evidence of acute change in mental status.  She is able to pay attention and think clearly.  The patient did not display any altered level of consciousness."
            },
            "mental_status_01.orientation_01.place_01": {
              "value": "true",
              "verbatim_source": "Clinician- (C0300) Temporal Orientation​(Orientation to year, month, and day):\n“Please tell me what year it is right now”\nPatient – 2022\n“What month are we in right now?”\nPatient- September\nWhat day of the week is today?”\nPatient- Saturday"
            },
            "section_1707994970.Question F.symptom_presence_option_f": {
              "value": "0",
              "verbatim_source": "“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Feeling bad about yourself - or that you are a failure or have let yourself or your family down”\nPatient- no"
            },
            "section_1707994970.Question H.symptom_presence_options_h": {
              "value": "0",
              "verbatim_source": "“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Moving or speaking so slowly that other people could have noticed. Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual”\nPatient- no"
            },
            "mental_status_01.orientation_01.neurological_01": {
              "value": null,
              "verbatim_source": null
            },
            "mental_status_01.orientation_01.status_001": {
              "value": "false",
              "verbatim_source": null
            },
            "bims_C0200_C0500.CO200.CO200": {
              "value": "3",
              "verbatim_source": "Clinician- (C0200)  \nRepetition of Three Words​Ask patient“I am going to say three words for you to remember. Please repeat the words after I have said all three. The words are: sock, blue, and bed. Now tell me the three words.”\nPatient- sock, blue, bed"
            },
            "section_1707994970.symptom_presence_option_c": {
              "value": "0",
              "verbatim_source": "“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Trouble falling or staying asleep, or sleeping too much”\nPatient – no"
            },
            "ds_section_1708000588.anxious_radio_1708002984": {
              "value": null,
              "verbatim_source": null
            },
            "section_1707994970.Question G.symptom_presence_options_g": {
              "value": "0",
              "verbatim_source": "“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Trouble concentrating on things, such as reading the newspaper or watching television”\nPatient- no"
            },
            "section_1707994970.symptom_frequency_options": {
              "value": "3",
              "verbatim_source": "D0150 Patient Mood Interview (PHQ-2 to PHQ-9)\n“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Little interest or pleasure in doing things”\nPatient- yes\n“About how often have you been bothered by this?”\nNo (Never or 1 day)​1. 2 to 6 days (several days)​2. 7-11 days (half or more of the days)​3. 12-14 days (nearly every day)\nPatient- probably most every day"
            },
            "section_1707994970.Question I.symptom_presence_options_i": {
              "value": "0",
              "verbatim_source": "“Over the last 2 weeks, have you been bothered by any of the following problems?”\n “Thoughts that you would be better off dead, or of hurting yourself in some way”\nPatient- definitely no"
            },
            "section_1707994970.symptom_frequency_options_g": {
              "value": null,
              "verbatim_source": "“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Trouble concentrating on things, such as reading the newspaper or watching television”\nPatient- no"
            },
            "mental_status_01.orientation_01.mood_01.behavioral__01": {
              "value": null,
              "verbatim_source": null
            },
            "ds_section_1708000588.ds_altered_radio_1707999826": {
              "value": null,
              "verbatim_source": null
            },
            "bims_C0200_C0500.C0300_section.C0300_c_radio": {
              "value": "1",
              "verbatim_source": "Clinician- (C0300) Temporal Orientation​(Orientation to year, month, and day):\n“Please tell me what year it is right now”\nPatient – 2022\n“What month are we in right now?”\nPatient- September\nWhat day of the week is today?”\nPatient- Saturday"
            },
            "mental_status_01.orientation_01.psychosocial_01": {
              "value": null,
              "verbatim_source": null
            },
            "ds_section_1708000588.ds_inattention_radio_1707997679": {
              "value": null,
              "verbatim_source": null
            },
            "section_1707994970.symptom_frequency_options_d": {
              "value": "3",
              "verbatim_source": "“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Feeling tired or having little energy”\nPatient- oh yes for sure\n“About how often have you been bothered by this? \nNo (Never or 1 day) \n1. 2 to 6 days (several days) \n2. 7-11 days (half or more of the days) \n3. 12-14 days (nearly every day)”\nPatient- I’m tired every day"
            },
            "section_1707994970.question_a.symptom_presence_options": {
              "value": "1",
              "verbatim_source": "D0150 Patient Mood Interview (PHQ-2 to PHQ-9)\n“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Little interest or pleasure in doing things”\nPatient- yes"
            },
            "bims_C0200_C0500.C0500_summary_section.C0500_input": {
              "value": null,
              "verbatim_source": null
            },
            "mental_status_01.orientation_01.mood_01.mood_01": {
              "value": [
                "Depressed"
              ],
              "verbatim_source": "D0150 Patient Mood Interview (PHQ-2 to PHQ-9)\n“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Little interest or pleasure in doing things”\nPatient- yes\n“About how often have you been bothered by this?”\nNo (Never or 1 day)​1. 2 to 6 days (several days)​2. 7-11 days (half or more of the days)​3. 12-14 days (nearly every day)\nPatient- probably most every day\n“What about, Feeling down, depressed, or hopeless”\nPatient- MMM Sometimes\n“About how often have you been bothered by this?”\nNo (Never or 1 day)​1. 2 to 6 days (several days)​2. 7-11 days (half or more of the days)​3. 12-14 days (nearly every day)\nPatient- probably just a couple days"
            },
            "section_1707994970.symptom_frequency_options_h": {
              "value": null,
              "verbatim_source": "“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Moving or speaking so slowly that other people could have noticed. Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual”\nPatient- no"
            },
            "bims_C0200_C0500.C0400_recall_secton.C0400_a_radio": {
              "value": "2",
              "verbatim_source": "Clinician- (C0400) Recall:\n“Let's go back to an earlier question. What were those three words that I asked you to repeat?”\nIf unable to remember a word, give cue (something to wear, a color, a piece of furniture) for that word.\nPatient- sock, blue, bed"
            },
            "section_1707994970.symptom_presence_options_d": {
              "value": "1",
              "verbatim_source": "“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Feeling tired or having little energy”\nPatient- oh yes for sure"
            },
            "section_1707994970.symptom_frequency_options_b": {
              "value": "1",
              "verbatim_source": "D0150 Patient Mood Interview (PHQ-2 to PHQ-9)\n“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Feeling down, depressed, or hopeless”\nPatient- MMM Sometimes\n“About how often have you been bothered by this?”\nNo (Never or 1 day)​1. 2 to 6 days (several days)​2. 7-11 days (half or more of the days)​3. 12-14 days (nearly every day)\nPatient- probably just a couple days"
            },
            "mental_status_01.orientation_01.mental_status_additional_info": {
              "value": null,
              "verbatim_source": null
            },
            "bims_C0200_C0500.C0400_recall_secton.C0400_c_radio": {
              "value": "2",
              "verbatim_source": "Clinician- (C0400) Recall:\n“Let's go back to an earlier question. What were those three words that I asked you to repeat?”\nIf unable to remember a word, give cue (something to wear, a color, a piece of furniture) for that word.\nPatient- sock, blue, bed"
            },
            "section_1707994970.symptom_frequency_options_e": {
              "value": null,
              "verbatim_source": "“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Poor appetite or overeating”\t \nPatient- nope I eat fine, can’t you tell, hahaha"
            },
            "bims_C0200_C0500.C0300_section.C0300_b_radio": {
              "value": "2",
              "verbatim_source": "Clinician- (C0300) Temporal Orientation​(Orientation to year, month, and day):\n“Please tell me what year it is right now”\nPatient – 2022\n“What month are we in right now?”\nPatient- September"
            },
            "mental_status_01.orientation_01.situation_01": {
              "value": "true",
              "verbatim_source": "Clinician- (C0300) Temporal Orientation​(Orientation to year, month, and day):\n“Please tell me what year it is right now”\nPatient – 2022\n“What month are we in right now?”\nPatient- September\nWhat day of the week is today?”\nPatient- Saturday"
            },
            "ds_section_1708000588.ds_mental_status_radio_1707997269": {
              "value": "false",
              "verbatim_source": "Upon completion of the BIMS- Clinician CAM assessment\nThe patient has no evidence of acute change in mental status.  She is able to pay attention and think clearly.  The patient did not display any altered level of consciousness."
            },
            "section_1707994970.Question E.symptom_presence_option_e": {
              "value": "0",
              "verbatim_source": "“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Poor appetite or overeating”\t \nPatient- nope I eat fine, can’t you tell, hahaha"
            },
            "mental_status_01.orientation_01.memory_01": {
              "value": [
                "Forgetful"
              ],
              "verbatim_source": "Clinician- (C0400) Recall:\n“Let's go back to an earlier question. What were those three words that I asked you to repeat?”\nIf unable to remember a word, give cue (something to wear, a color, a piece of furniture) for that word.\nPatient- sock, blue, bed"
            }
          }
        console.log("sectionData", sectionData);
        let selectedSectionTemp: any = {};
        Object.keys(sectionData).forEach((key) => {
            console.log("sectionData[key]", sectionData[key].value, Array.isArray(sectionData[key]?.value), sectionData[key]?.value instanceof Array);
            if (sectionData[key]?.value instanceof Array || Array.isArray(sectionData[key]?.value)) {
                selectedSectionTemp[key] = [];
                for (let i = 0; i < sectionData[key].value.length; i++) {
                    try{
                        const subSectionTemp: any = {};
                        Object.keys(sectionData[key]?.value[i]).forEach((key1) => { subSectionTemp[key1] = sectionData[key]?.value[i][key1]?.value });
                        selectedSectionTemp[key].push(subSectionTemp);
                    }catch (error){
                        console.log("Error in sectionData[key].value[i]", sectionData[key]?.value[i]);
                    }
                    
                }
                //selectedSectionTemp[key] = sectionData[key].value.map((item:any) => Object.keys(item).map((key)=>{return {[key]:item[key].value}}));
            } else {
                selectedSectionTemp[key] = sectionData[key]?.value && sectionData[key]?.value !== "null" ? sectionData[key]?.value: null;
            }
        });
        console.log("selectedSectionTemp", selectedSectionTemp);
        return selectedSectionTemp;
    },[]);

    const getSections = useCallback((sectionNode: any, extractionStatus: any, getExtractionStatusText: (status: number) => string) => {
        const sections: Array<Section> = [];
        sectionNode?.items?.forEach((item: any) => {
            if (item.dataType === "SECTION") {
                sections.push({
                    sectionName: item.question,
                    sectionId: item.localQuestionCode,
                    extractionStatus: getExtractionStatusText(extractionStatus?.[item.localQuestionCode]) || "Not Extracted",
                    customFormTemplateName: SECTION_TO_CF_MAPPING[item.localQuestionCode]
                });
            }
        });
        return sections;
    },[]);
    
    const getSectionSchema = useCallback((sectionId: string, schema: any) => {
        let selectedSection = schema.items.find((item: any) => item.localQuestionCode === sectionId);
    
        return selectedSection;
    },[]);
    
    const getSectionData = useCallback((sectionId: string, sectionsData: any) => {
        sectionsData.push({"C":{
            "bims_C0200_C0500.C0300_section.C0300_a_radio": {
              "value": "2",
              "verbatim_source": "Clinician- (C0300) Temporal Orientation​(Orientation to year, month, and day):\n“Please tell me what year it is right now”\nPatient – 2022"
            },
            "ds_section_1708000588.cognitive_radio_1708001390": {
              "value": null,
              "verbatim_source": null
            },
            "section_1707994970.severity_score": {
              "value": "3",
              "verbatim_source": "“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Feeling tired or having little energy”\nPatient- oh yes for sure\n“About how often have you been bothered by this? \nNo (Never or 1 day) \n1. 2 to 6 days (several days) \n2. 7-11 days (half or more of the days) \n3. 12-14 days (nearly every day)”\nPatient- I’m tired every day"
            },
            "section_1707994970.social_isolation": {
              "value": "2",
              "verbatim_source": "“How often do you feel lonely or isolated from those around you?”  \nPatient- Sometimes, I wish I got to see my family more often"
            },
            "section_1707994970.disruptive_behaviour": {
              "value": "0",
              "verbatim_source": "Upon completion of the BIMS- Clinician CAM assessment  \nThe patient has no evidence of acute change in mental status.  She is able to pay attention and think clearly.  The patient did not display any altered level of consciousness."
            },
            "section_1707994970.question_b.symptom_presence_option_b": {
              "value": "1",
              "verbatim_source": "D0150 Patient Mood Interview (PHQ-2 to PHQ-9)\n“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Feeling down, depressed, or hopeless”\nPatient- MMM Sometimes"
            },
            "ds_section_1708000588.confused_radio_1708002707": {
              "value": null,
              "verbatim_source": null
            },
            "mental_status_01.orientation_01.person_01": {
              "value": "true",
              "verbatim_source": "Clinician- (C0200)  \nRepetition of Three Words​Ask patient“I am going to say three words for you to remember. Please repeat the words after I have said all three. The words are: sock, blue, and bed. Now tell me the three words.”\nPatient- sock, blue, bed"
            },
            "mental_status_01.orientation_01.time_01": {
              "value": "true",
              "verbatim_source": "Clinician- (C0300) Temporal Orientation​(Orientation to year, month, and day):\n“Please tell me what year it is right now”\nPatient – 2022\n“What month are we in right now?”\nPatient- September\nWhat day of the week is today?”\nPatient- Saturday"
            },
            "ds_section_1708000588.ds_thinking_radio_1707998219": {
              "value": null,
              "verbatim_source": null
            },
            "bims_C0200_C0500.C0400_recall_secton.C0400_b_radio": {
              "value": "2",
              "verbatim_source": "Clinician- (C0400) Recall:\n“Let's go back to an earlier question. What were those three words that I asked you to repeat?”\nIf unable to remember a word, give cue (something to wear, a color, a piece of furniture) for that word.\nPatient- sock, blue, bed"
            },
            "section_1707994970.symptom_frequency_options_c": {
              "value": null,
              "verbatim_source": "“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Trouble falling or staying asleep, or sleeping too much”\nPatient – no"
            },
            "section_1707994970.symptom_frequency_options_f": {
              "value": null,
              "verbatim_source": "“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Feeling bad about yourself - or that you are a failure or have let yourself or your family down”\nPatient- no"
            },
            "section_1707994970.symptom_frequency_options_i": {
              "value": null,
              "verbatim_source": "“Over the last 2 weeks, have you been bothered by any of the following problems?”\n “Thoughts that you would be better off dead, or of hurting yourself in some way”\nPatient- definitely no"
            },
            "section_1707994970.cognitive_behavioural_psychiatric": {
              "value": "7",
              "verbatim_source": "Upon completion of the BIMS- Clinician CAM assessment  \nThe patient has no evidence of acute change in mental status.  She is able to pay attention and think clearly.  The patient did not display any altered level of consciousness."
            },
            "mental_status_01.orientation_01.place_01": {
              "value": "true",
              "verbatim_source": "Clinician- (C0300) Temporal Orientation​(Orientation to year, month, and day):\n“Please tell me what year it is right now”\nPatient – 2022\n“What month are we in right now?”\nPatient- September\nWhat day of the week is today?”\nPatient- Saturday"
            },
            "section_1707994970.Question F.symptom_presence_option_f": {
              "value": "0",
              "verbatim_source": "“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Feeling bad about yourself - or that you are a failure or have let yourself or your family down”\nPatient- no"
            },
            "section_1707994970.Question H.symptom_presence_options_h": {
              "value": "0",
              "verbatim_source": "“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Moving or speaking so slowly that other people could have noticed. Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual”\nPatient- no"
            },
            "mental_status_01.orientation_01.neurological_01": {
              "value": null,
              "verbatim_source": null
            },
            "mental_status_01.orientation_01.status_001": {
              "value": "false",
              "verbatim_source": null
            },
            "bims_C0200_C0500.CO200.CO200": {
              "value": "3",
              "verbatim_source": "Clinician- (C0200)  \nRepetition of Three Words​Ask patient“I am going to say three words for you to remember. Please repeat the words after I have said all three. The words are: sock, blue, and bed. Now tell me the three words.”\nPatient- sock, blue, bed"
            },
            "section_1707994970.symptom_presence_option_c": {
              "value": "0",
              "verbatim_source": "“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Trouble falling or staying asleep, or sleeping too much”\nPatient – no"
            },
            "ds_section_1708000588.anxious_radio_1708002984": {
              "value": null,
              "verbatim_source": null
            },
            "section_1707994970.Question G.symptom_presence_options_g": {
              "value": "0",
              "verbatim_source": "“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Trouble concentrating on things, such as reading the newspaper or watching television”\nPatient- no"
            },
            "section_1707994970.symptom_frequency_options": {
              "value": "3",
              "verbatim_source": "D0150 Patient Mood Interview (PHQ-2 to PHQ-9)\n“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Little interest or pleasure in doing things”\nPatient- yes\n“About how often have you been bothered by this?”\nNo (Never or 1 day)​1. 2 to 6 days (several days)​2. 7-11 days (half or more of the days)​3. 12-14 days (nearly every day)\nPatient- probably most every day"
            },
            "section_1707994970.Question I.symptom_presence_options_i": {
              "value": "0",
              "verbatim_source": "“Over the last 2 weeks, have you been bothered by any of the following problems?”\n “Thoughts that you would be better off dead, or of hurting yourself in some way”\nPatient- definitely no"
            },
            "section_1707994970.symptom_frequency_options_g": {
              "value": null,
              "verbatim_source": "“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Trouble concentrating on things, such as reading the newspaper or watching television”\nPatient- no"
            },
            "mental_status_01.orientation_01.mood_01.behavioral__01": {
              "value": null,
              "verbatim_source": null
            },
            "ds_section_1708000588.ds_altered_radio_1707999826": {
              "value": null,
              "verbatim_source": null
            },
            "bims_C0200_C0500.C0300_section.C0300_c_radio": {
              "value": "1",
              "verbatim_source": "Clinician- (C0300) Temporal Orientation​(Orientation to year, month, and day):\n“Please tell me what year it is right now”\nPatient – 2022\n“What month are we in right now?”\nPatient- September\nWhat day of the week is today?”\nPatient- Saturday"
            },
            "mental_status_01.orientation_01.psychosocial_01": {
              "value": null,
              "verbatim_source": null
            },
            "ds_section_1708000588.ds_inattention_radio_1707997679": {
              "value": null,
              "verbatim_source": null
            },
            "section_1707994970.symptom_frequency_options_d": {
              "value": "3",
              "verbatim_source": "“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Feeling tired or having little energy”\nPatient- oh yes for sure\n“About how often have you been bothered by this? \nNo (Never or 1 day) \n1. 2 to 6 days (several days) \n2. 7-11 days (half or more of the days) \n3. 12-14 days (nearly every day)”\nPatient- I’m tired every day"
            },
            "section_1707994970.question_a.symptom_presence_options": {
              "value": "1",
              "verbatim_source": "D0150 Patient Mood Interview (PHQ-2 to PHQ-9)\n“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Little interest or pleasure in doing things”\nPatient- yes"
            },
            "bims_C0200_C0500.C0500_summary_section.C0500_input": {
              "value": null,
              "verbatim_source": null
            },
            "mental_status_01.orientation_01.mood_01.mood_01": {
              "value": [
                "Depressed"
              ],
              "verbatim_source": "D0150 Patient Mood Interview (PHQ-2 to PHQ-9)\n“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Little interest or pleasure in doing things”\nPatient- yes\n“About how often have you been bothered by this?”\nNo (Never or 1 day)​1. 2 to 6 days (several days)​2. 7-11 days (half or more of the days)​3. 12-14 days (nearly every day)\nPatient- probably most every day\n“What about, Feeling down, depressed, or hopeless”\nPatient- MMM Sometimes\n“About how often have you been bothered by this?”\nNo (Never or 1 day)​1. 2 to 6 days (several days)​2. 7-11 days (half or more of the days)​3. 12-14 days (nearly every day)\nPatient- probably just a couple days"
            },
            "section_1707994970.symptom_frequency_options_h": {
              "value": null,
              "verbatim_source": "“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Moving or speaking so slowly that other people could have noticed. Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual”\nPatient- no"
            },
            "bims_C0200_C0500.C0400_recall_secton.C0400_a_radio": {
              "value": "2",
              "verbatim_source": "Clinician- (C0400) Recall:\n“Let's go back to an earlier question. What were those three words that I asked you to repeat?”\nIf unable to remember a word, give cue (something to wear, a color, a piece of furniture) for that word.\nPatient- sock, blue, bed"
            },
            "section_1707994970.symptom_presence_options_d": {
              "value": "1",
              "verbatim_source": "“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Feeling tired or having little energy”\nPatient- oh yes for sure"
            },
            "section_1707994970.symptom_frequency_options_b": {
              "value": "1",
              "verbatim_source": "D0150 Patient Mood Interview (PHQ-2 to PHQ-9)\n“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Feeling down, depressed, or hopeless”\nPatient- MMM Sometimes\n“About how often have you been bothered by this?”\nNo (Never or 1 day)​1. 2 to 6 days (several days)​2. 7-11 days (half or more of the days)​3. 12-14 days (nearly every day)\nPatient- probably just a couple days"
            },
            "mental_status_01.orientation_01.mental_status_additional_info": {
              "value": null,
              "verbatim_source": null
            },
            "bims_C0200_C0500.C0400_recall_secton.C0400_c_radio": {
              "value": "2",
              "verbatim_source": "Clinician- (C0400) Recall:\n“Let's go back to an earlier question. What were those three words that I asked you to repeat?”\nIf unable to remember a word, give cue (something to wear, a color, a piece of furniture) for that word.\nPatient- sock, blue, bed"
            },
            "section_1707994970.symptom_frequency_options_e": {
              "value": null,
              "verbatim_source": "“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Poor appetite or overeating”\t \nPatient- nope I eat fine, can’t you tell, hahaha"
            },
            "bims_C0200_C0500.C0300_section.C0300_b_radio": {
              "value": "2",
              "verbatim_source": "Clinician- (C0300) Temporal Orientation​(Orientation to year, month, and day):\n“Please tell me what year it is right now”\nPatient – 2022\n“What month are we in right now?”\nPatient- September"
            },
            "mental_status_01.orientation_01.situation_01": {
              "value": "true",
              "verbatim_source": "Clinician- (C0300) Temporal Orientation​(Orientation to year, month, and day):\n“Please tell me what year it is right now”\nPatient – 2022\n“What month are we in right now?”\nPatient- September\nWhat day of the week is today?”\nPatient- Saturday"
            },
            "ds_section_1708000588.ds_mental_status_radio_1707997269": {
              "value": "false",
              "verbatim_source": "Upon completion of the BIMS- Clinician CAM assessment\nThe patient has no evidence of acute change in mental status.  She is able to pay attention and think clearly.  The patient did not display any altered level of consciousness."
            },
            "section_1707994970.Question E.symptom_presence_option_e": {
              "value": "0",
              "verbatim_source": "“Over the last 2 weeks, have you been bothered by any of the following problems?”\n“Poor appetite or overeating”\t \nPatient- nope I eat fine, can’t you tell, hahaha"
            },
            "mental_status_01.orientation_01.memory_01": {
              "value": [
                "Forgetful"
              ],
              "verbatim_source": "Clinician- (C0400) Recall:\n“Let's go back to an earlier question. What were those three words that I asked you to repeat?”\nIf unable to remember a word, give cue (something to wear, a color, a piece of furniture) for that word.\nPatient- sock, blue, bed"
            }
          }});
        console.log("sectionsData", sectionsData,sectionId);
        let selectedSection = null;
        sectionsData.forEach((item: any) => {
            Object.keys(item).forEach((key) => {
                if (key === sectionId) {
                    selectedSection = item;
                }
            });
        });
        console.log("selectedSection", selectedSection?.[sectionId]);
        return selectedSection?.[sectionId];
    },[]);

    useEffect(()=>{
        if(selectedSectionId && selectedSectionData){
            console.log("selectedSectionId",selectedSectionId,selectedSectionData);
            setSectionvalues(getSectionValues(selectedSectionId, selectedSectionData));
        }
    },[selectedSectionData,selectedSectionId,getSectionValues]);

    useEffect(() => {
        setSections(getSections(props.schema, extractionAdapter?.extractionStatus, extractionAdapter?.getStatusText));
    }, [props.schema, extractionAdapter?.extractionStatus]);

    useEffect(() => {
        if (selectedSectionId) {
            setSelectedSectionData(getSectionData(selectedSectionId, JSON.parse(extractionAdapter?.extractedText)) || null);
        }
    }, [selectedSectionId, props.schema, extractionAdapter?.extractedText]);

    useEffect(() => {
        if (env) {
            getTranscriptId(`${props.transactionId}-default`, env);
        }
    }, [props.transactionId, env, getTranscriptId])

    useEffect(() => {
        if (env) {
            savePromptTemplate(transcriptId, props.schema, model, env);
        }
    }, [transcriptId, props.schema, env, savePromptTemplate, model]);

    useEffect(() => {
        if (env && transcriptId && transcriptId != null) {
            extractionAdapter?.getStatusAsync(transcriptId, savedTranscriptVersion, env);
        }
    }, [transcriptId, savedTranscriptVersion, env])

    useEffect(() => {
        if (embeddingSearchApiResponse) {
            let evidencesTemp: Array<string> = [];
            embeddingSearchApiResponse?.forEach((evidence: Evidence) => {
                evidencesTemp.push(evidence.sentence?.sentence);
            });
            setEvidences(evidencesTemp);
        }
    }, [embeddingSearchApiResponse])

    return (
        <div style={{ width: "100%", display: "flex", flex: 1, flexDirection: "column", alignItems: 'stretch' }}>
            {/* <HStack padding={2} align={"right"} flex={1} width={"100%"}> */}
            <Settings onModelChange={(model: string) => { setModel(model) }} onRelevanceScoreChange={(score: number) => { setRelevanceScore(score) }} />
            {/* </HStack> */}
            <HStack padding={2} align={"top"} flex={1}>
                {!selectedSectionId && env && <AutoScribeWidgetBubble
                    widgetHost={env?.AUTOSCRIBE_WIDGET_HOST}
                    transactionId={props.transactionId}
                    onConfirm={(text: Array<any>, transactionId: string, sectionId: string, version: number) => {
                        console.log("confirmed by autoscribe", transactionId, sectionId, version, text);
                        setSelectedSectionId(null);
                        setSavedTranscriptVersion(version);
                        extractionAdapter?.getStatusAsync(transactionId, version, env);
                    }}
                    onCancel={() => { }}
                    sectionId={"default"}
                />
                }
                {selectedSectionId && <VStack w={"30%"} align={"top"} flex={1} >
                    <Box minHeight={"700px"} maxHeight={"700px"} position="relative" display="flex" flexDirection="column" gap="1rem">
                        {!env && <Box>Loading Autoscribe...</Box>}
                        {env && <AutoScribeWidgetBlock
                            widgetHost={env?.AUTOSCRIBE_WIDGET_HOST}
                            transactionId={props.transactionId}
                            onConfirm={(text: Array<any>, transactionId: string, sectionId: string, version: number) => {
                                console.log(transactionId, sectionId, version, text);
                                setSelectedSectionId(null);
                                setSavedTranscriptVersion(version);
                                extractionAdapter?.getStatusAsync(transactionId, version, env);
                            }}
                            onCancel={() => { }}
                            sectionId={"default"}
                            inlineWidgetEmbedding={true}
                            evidences={evidences}
                            verbatimSourceEvidence={verbatimSourceEvidence}
                        />
                        }
                    </Box>
                </VStack>}
                <VStack w={selectedSectionId ? "70%" : "100%"} >
                    <Box maxHeight={"700px"} position="relative" display="flex" flexDirection="column" gap="1rem">
                        {selectedSectionId === null && <SectionList sections={sections} onFormViewEvent={(sectionId: string) => { setSelectedSectionId(sectionId) }} />}
                    </Box>
                    <Box>
                        <Box>
                            {selectedSectionId && <LinkButton onClick={() => { setSelectedSectionId(null); console.log("extracted text", extractionAdapter?.extractedText) }}>Back</LinkButton>}
                        </Box>

                        <Box maxHeight={"700px"} position="relative" display="flex" flexDirection="column" gap="1rem" overflowY={"scroll"}>
                            <ChakraProvider>
                                {selectedSectionId && selectedSectionData && env && <MemoizedAnnotatedForm
                                    //newData={{"C0000-1":{"C0000-2":"true"}}}
                                    env={env}
                                    widgetHost={env.FORMS_WIDGETS_HOST}
                                    newData={sectionValues}
                                    formInstanceId={"None"} // ToDo: get from list of forms page
                                    formTemplateId={SECTION_TO_CF_MAPPING[selectedSectionId]}
                                    onEvidenceRequested={(field: any) => {
                                        
                                        const answer: any = selectedSectionData[field.id];
                                        let resolvedAnswer = answer;
                                        if (Array.isArray(answer.value)) {
                                            answer.value.forEach((item:any) => {
                                                Object.keys(item).find((key) => {
                                                    if (key.toLowerCase().includes(field.text.toLowerCase())){
                                                        resolvedAnswer = item[key];
                                                    }
                                                });
                                                if (field.text.includes(item)){
                                                    resolvedAnswer = item;
                                                }
                                            });
                                        }
                                        console.log("Evidence requested for", field,resolvedAnswer);
                                        search(transcriptId, field.text, resolvedAnswer.verbatim_source || resolvedAnswer.value, relevanceScore, env);
                                        setVerbatimSourceEvidence(resolvedAnswer.verbatim_source);
                                    }}
                                />
                                }
                            </ChakraProvider>
                        </Box>
                    </Box>

                </VStack>
            </HStack>
        </div>
    )
}