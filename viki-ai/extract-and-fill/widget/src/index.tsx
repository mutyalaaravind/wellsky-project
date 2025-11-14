import React, { useEffect } from "react";
import ReactDOM from "react-dom/client";
import ExtractManager from "./Extract";
import reportWebVitals from "./reportWebVitals";
import { Drawer, FloatButton } from 'antd';
import { AudioOutlined, BulbTwoTone, SettingOutlined } from '@ant-design/icons';
import { PrimaryButton, SecondaryButton, LinkButton, Grid, Popover, Select, TextArea, CustomSideDrawer } from '@mediwareinc/wellsky-dls-react';
import { Box, Button, ChakraProvider, Text } from "@chakra-ui/react";
import { lightTheme } from '@mediwareinc/wellsky-dls-react'
import StartOfCare from './assets/99131-5.json';
import AnnotatedForm from './components/review/AnnotatedFormV3';
import CustomFormAnnotatedForm from './components/review/AnnotatedFormV4';

import { sampleTranscript } from './prompt_templates/sample_transcript_2';
import { SectionsViewer } from "./components/sections/SectionsViewer";

type InitArgs = {
  el: HTMLElement;
  transactionId: string;
  sectionId: string;
  transcriptText: string;
  extractFields?: Array<any>;
  template?: any;
  onExtractionCompleted?: (extractedText: string | null) => {};
  setApprovedFormFieldValues?: (approvedFields: any) => {};
  mount?: string;
  promptTemplate?: any;
  questionnaireTemplate?: any;
  componentType?: string;
  isOpen: boolean;
  onCancel?: () => void;
};

type SectionViewerArgs = {
  el: HTMLElement;
  sectionsSchema: any;
  transactionId: string;
}

declare global {
  interface Window {
    initExtract: (args: InitArgs) => void;
    initAnnotatedFormV3: (args: any) => void;
    initSectionViewer: (args: any) => void;
    initCustomFormAnnotatorV4: (args: any) => void;
  }
}

type BubbleProps = {
  component: any;
  onOpen?: () => void;
  onConfirm?: (text: string) => void;
  onCancel?: () => void;
};

type InlineWidgetProps = BubbleProps

window.initExtract = ({
  el,
  transactionId,
  sectionId,
  transcriptText,
  extractFields,
  onExtractionCompleted,
  template,
  setApprovedFormFieldValues,
  mount,
  promptTemplate,
  questionnaireTemplate,
  componentType,
  onCancel
}: InitArgs) => {
  const root = document.createElement('div');
  document.body.appendChild(root);
  const reactRoot = ReactDOM.createRoot(root);
  reactRoot.render(
    <ChakraProvider theme={lightTheme}>

      {componentType === "bubble" ? <ExtractBubble component={
                                        <ExtractManager
                                          transactionId={transactionId}
                                          sectionId={sectionId}
                                          transcriptText={transcriptText}
                                          //transcriptText={sampleTranscript}
                                          setApprovedFormFieldValues={setApprovedFormFieldValues}
                                          promptTemplate={promptTemplate}
                                          questionnaireTemplate={questionnaireTemplate}
                                        />
                                    } />:
                                    <ExtractDrawer component={
                                      <ExtractManager
                                          transactionId={transactionId}
                                          sectionId={sectionId}
                                          transcriptText={transcriptText}
                                          //transcriptText={sampleTranscript}
                                          setApprovedFormFieldValues={setApprovedFormFieldValues}
                                          promptTemplate={promptTemplate}
                                          questionnaireTemplate={questionnaireTemplate}
                                          onCancel={onCancel}
                                        />}
                                      />}
      {/* <AnnotatedForm originalData={
        {
          "Administrative Information": {
            "_meta": {
              "National Provider Identifier (NPI) for the attending physician who has signed the plan of care": {
                "answers": [
                  null
                ]
              },
              "Branch State": {
                "answers": [
                  null
                ]
              },
              "Patient State of Residence": {
                "answers": [
                  null
                ]
              },
              "Gender": {
                "answers": [
                  "Male",
                  "Female"
                ]
              },
              "Ethnicity: Are you of Hispanic, Latino/a, or Spanish origin?": {
                "answers": [
                  "No, not of Hispanic, Latino/a, or Spanish origin",
                  "Yes, Mexican, Mexican American, Chicano/a",
                  "Yes, Puerto Rican",
                  "Yes, Cuban",
                  "Yes, another Hispanic, Latino, or Spanish origin",
                  "Patient unable to respond"
                ]
              },
              "Race: What is your race?": {
                "answers": [
                  "White",
                  "Black or African American",
                  "American Indian or Alaska Native",
                  "Asian Indian",
                  "Chinese",
                  "Filipino",
                  "Japanese",
                  "Korean",
                  "Vietnamese",
                  "Other Asian",
                  "Native Hawaiian",
                  "Guamanian or Chamorro",
                  "Samoan",
                  "Other Pacific Islander",
                  "Patient unable to respond"
                ]
              },
              "Current Payment Sources for Home Care": {
                "answers": [
                  "None; no charge for current services",
                  "Medicare (traditional fee-for-service)",
                  "Medicare (HMO/managed care/Advantage plan)",
                  "Medicaid (traditional fee-for-service)",
                  "Medicaid (HMO/managed care)",
                  "Workers' compensation",
                  "Title programs (for example, Title III, V, or XX)",
                  "Other government (for example, Tricare, VA)",
                  "Private insurance",
                  "Private HMO/managed care",
                  "Self-pay",
                  "Other (specify)",
                  "Unknown"
                ]
              },
              "Discipline of Person Completing Assessment": {
                "answers": [
                  "RN",
                  "PT",
                  "SLP/ST",
                  "OT"
                ]
              },
              "This Assessment is Currently Being Completed for the Following Reason": {
                "answers": [
                  "Start of care - further visits planned",
                  "Resumption of care (after inpatient stay)",
                  "Recertification (follow-up) reassessment",
                  "Other follow-up",
                  "Transferred to an inpatient facility - patient not discharged from agency",
                  "Transferred to an inpatient facility - patient discharged from agency",
                  "Death at home",
                  "Discharge from agency"
                ]
              },
              "Episode Timing: Is the Medicare home health payment episode for which this assessment will define a case mix group an \"early\" episode or a \"later\" episode in the patient's current sequence of adjacent Medicare home health payment episodes?": {
                "answers": [
                  "Early",
                  "Later",
                  "Unknown",
                  "Not Applicable: No Medicare case mix group to be defined by this assessment."
                ]
              },
              "Transportation. Has lack of transportation kept you from medical appointments, meetings, work, or from getting things needed for daily living?": {
                "answers": [
                  "Yes, it has kept me from medical appointments or from getting my medications",
                  "Yes, it has kept me from non-medical meetings, appointments, work, or from getting things that I need",
                  "No",
                  "Resident unable to respond",
                  "Resident declines to respond"
                ]
              },
              "From which of the following Inpatient Facilities was the patient discharged within the past 14 days?": {
                "answers": [
                  "Long-term nursing facility (NF)",
                  "Skilled nursing facility (SNF/TCU)",
                  "Short-stay acute hospital (IPPS)",
                  "Long-Term Care Hospital (LTCH)",
                  "Inpatient rehabilitation hospital or unit (IRF)",
                  "Psychiatric hospital or unit",
                  "Other (specify)",
                  "Patient was not discharged from an inpatient facility"
                ]
              }
            },
            "National Provider Identifier (NPI) for the attending physician who has signed the plan of care": null,
            "CMS Certification Number": null,
            "Branch State": null,
            "Branch ID Number": null,
            "Patient ID Number": null,
            "Patient Name": {
              "(First)": "Old first name",
              "(MI)": "Old middle name",
              "(Last)": null,
              "(Suffix)": null
            },
            "Patient State of Residence": null,
            "Patient ZIP Code": null,
            "Social Security Number": null,
            "Medicare Number": null,
            "Medicaid Number": null,
            "Gender": "Male",
            "Birth Date": null,
            "Ethnicity: Are you of Hispanic, Latino/a, or Spanish origin?": "Yes, Puerto Rican",
            "Race: What is your race?": null,
            "Current Payment Sources for Home Care": null,
            "Language": {
              "_meta": {
                "What is your preferred language?": {
                  "answers": [
                    "English",
                    "Spanish",
                    "Chinese",
                    "Vietnamese",
                    "Tagalog",
                    "Other"
                  ]
                },
                "Do you need or want an interpreter to communicate with a doctor or health care staff?": {
                  "answers": [
                    "No",
                    "Yes",
                    "Unable to determine"
                  ]
                }
              },
              "What is your preferred language?": null,
              "Do you need or want an interpreter to communicate with a doctor or health care staff?": null
            },
            "Start of Care Date": null,
            "Discipline of Person Completing Assessment": null,
            "Date Assessment Completed": null,
            "This Assessment is Currently Being Completed for the Following Reason": null,
            "Date of Physician-ordered Start of Care (Resumption of Care)": null,
            "Date of Referral": null,
            "Episode Timing: Is the Medicare home health payment episode for which this assessment will define a case mix group an \"early\" episode or a \"later\" episode in the patient's current sequence of adjacent Medicare home health payment episodes?": null,
            "Transportation. Has lack of transportation kept you from medical appointments, meetings, work, or from getting things needed for daily living?": null,
            "From which of the following Inpatient Facilities was the patient discharged within the past 14 days?": null,
            "Inpatient Discharge Date (most recent)": null
          },
          "Hearing, Speech, and Vision": {
            "_meta": {
              "Hearing. Ability to hear (with hearing aid or hearing appliances if normally used)": {
                "answers": [
                  "Adequate - no difficulty in normal conversation, social interaction, listening to TV",
                  "Minimal difficulty - difficulty in some environments (e.g. when person speaks softly or setting is noisy)",
                  "Moderate difficulty - speaker has to increase volume and speak distinctly",
                  "Highly impaired - absence of useful hearing"
                ]
              },
              "Vision. Ability to see in adequate light (with glasses or other visual appliances)": {
                "answers": [
                  "Adequate - sees fine detail, such as regular print in newspapers/books",
                  "Impaired - sees large print, but not regular print in newspapers/books",
                  "Moderately impaired - limited vision; not able to see newspaper headlines but can identify objects",
                  "Highly impaired - object identification in question, but eyes appear to follow objects",
                  "Severely impaired - no vision or sees only light, colors or shapes; eyes do not appear to follow objects"
                ]
              },
              "Health Literacy: How often do you need to have someone help you when you read instructions, pamphlets, or other written material from your doctor or pharmacy?": {
                "answers": [
                  "Never",
                  "Rarely",
                  "Sometimes",
                  "Often",
                  "Always"
                ]
              }
            },
            "Hearing. Ability to hear (with hearing aid or hearing appliances if normally used)": null,
            "Vision. Ability to see in adequate light (with glasses or other visual appliances)": null,
            "Health Literacy: How often do you need to have someone help you when you read instructions, pamphlets, or other written material from your doctor or pharmacy?": null
          },
          "Cognitive Patterns": {
            "_meta": {
              "Cognitive Functioning": {
                "answers": [
                  "Alert/oriented, able to focus and shift attention, comprehends and recalls task directions independently.",
                  "Requires prompting (cueing, repetition, reminders) only under stressful or unfamiliar conditions.",
                  "Requires assistance and some direction in specific situations (for example, all tasks involving shifting of attention) or consistently requires low stimulus environment due to distractibility.",
                  "Requires considerable assistance in routine situations. Is not alert and oriented or is unable to shift attention and recall directions more than half the time.",
                  "Totally dependent due to disturbances such as constant disorientation, coma, persistent vegetative state, or delirium."
                ]
              },
              "When Confused": {
                "answers": [
                  "Never",
                  "In new or complex situations only",
                  "On awakening or at night only",
                  "During the day and evening, but not constantly",
                  "Constantly",
                  "Patient nonresponsive"
                ]
              },
              "When Anxious": {
                "answers": [
                  "None of the time",
                  "Less often than daily",
                  "Daily, but not constantly",
                  "All of the time",
                  "Patient nonresponsive"
                ]
              },
              "Should Brief Interview for Mental Status (C0200-C0500) be Conducted?": {
                "answers": [
                  "No (resident is rarely/never understood)",
                  "Yes"
                ]
              }
            },
            "Cognitive Functioning": null,
            "When Confused": null,
            "When Anxious": null,
            "Should Brief Interview for Mental Status (C0200-C0500) be Conducted?": null,
            "Brief Interview for Mental Status": {
              "_meta": {
                "Repetition of Three Words": {
                  "answers": [
                    "None",
                    "One",
                    "Two",
                    "Three"
                  ]
                }
              },
              "Repetition of Three Words": null,
              "Temporal Orientation (Orientation to year, month, and day)": {
                "_meta": {
                  "Able to report correct year": {
                    "answers": [
                      "Missed by > 5 years or no answer",
                      "Missed by 2-5 years",
                      "Missed by 1 year",
                      "Correct"
                    ]
                  },
                  "Able to report correct month": {
                    "answers": [
                      "Missed by > 1 month or no answer",
                      "Missed by 6 days to 1 month",
                      "Accurate within 5 days"
                    ]
                  },
                  "Able to report correct day of the week": {
                    "answers": [
                      "Incorrect or no answer",
                      "Correct"
                    ]
                  }
                },
                "Able to report correct year": null,
                "Able to report correct month": null,
                "Able to report correct day of the week": null
              },
              "Recall": {
                "_meta": {
                  "Able to recall \"sock\"": {
                    "answers": [
                      "No - could not recall",
                      "Yes, after cueing (\"something to wear\")",
                      "Yes, no cue required"
                    ]
                  },
                  "Able to recall \"blue\"": {
                    "answers": [
                      "No - could not recall",
                      "Yes, after cueing (\"a color\")",
                      "Yes, no cue required"
                    ]
                  },
                  "Able to recall \"bed\"": {
                    "answers": [
                      "No - could not recall",
                      "Yes, after cueing (\"a piece of furniture\")",
                      "Yes, no cue required"
                    ]
                  }
                },
                "Able to recall \"sock\"": null,
                "Able to recall \"blue\"": null,
                "Able to recall \"bed\"": null
              },
              "BIMS Summary Score": 0
            },
            "Signs and Symptoms of Delirium (from CAM)": {
              "_meta": {
                "Acute Onset Mental Status Change. Is there evidence of an acute change in mental status from the patient's baseline?": {
                  "answers": [
                    "No",
                    "Yes"
                  ]
                },
                "Inattention - Did the patient have difficulty focusing attention, for example, being easily distractible or having difficulty keeping track of what was being said?": {
                  "answers": [
                    "Behavior not present",
                    "Behavior continuously present, does not fluctuate",
                    "Behavior present, fluctuates (comes and goes, changes in severity)"
                  ]
                },
                "Disorganized thinking - Was the patient's thinking disorganized or incoherent (rambling or irrelevant conversation, unclear or illogical flow of ideas, or unpredictable switching from subject to subject)?": {
                  "answers": [
                    "Behavior not present",
                    "Behavior continuously present, does not fluctuate",
                    "Behavior present, fluctuates (comes and goes, changes in severity)"
                  ]
                },
                "Altered level of consciousness - Did the patient have altered level of consciousness, as indicated by any of the following criteria?": {
                  "answers": [
                    "Behavior not present",
                    "Behavior continuously present, does not fluctuate",
                    "Behavior present, fluctuates (comes and goes, changes in severity)"
                  ]
                }
              },
              "Acute Onset Mental Status Change. Is there evidence of an acute change in mental status from the patient's baseline?": null,
              "Inattention - Did the patient have difficulty focusing attention, for example, being easily distractible or having difficulty keeping track of what was being said?": null,
              "Disorganized thinking - Was the patient's thinking disorganized or incoherent (rambling or irrelevant conversation, unclear or illogical flow of ideas, or unpredictable switching from subject to subject)?": null,
              "Altered level of consciousness - Did the patient have altered level of consciousness, as indicated by any of the following criteria?": null
            }
          },
          "Mood": {
            "Patient Mood Interview (PHQ-2 to 9)": {
              "Symptom Presence": {
                "_meta": {
                  "Little interest or pleasure in doing things": {
                    "answers": [
                      "No",
                      "Yes",
                      "No response"
                    ]
                  },
                  "Feeling down, depressed or hopeless": {
                    "answers": [
                      "No",
                      "Yes",
                      "No response"
                    ]
                  },
                  "Trouble falling or staying asleep, or sleeping too much": {
                    "answers": [
                      "No",
                      "Yes",
                      "No response"
                    ]
                  },
                  "Feeling tired or having little energy": {
                    "answers": [
                      "No",
                      "Yes",
                      "No response"
                    ]
                  },
                  "Poor appetite or overeating": {
                    "answers": [
                      "No",
                      "Yes",
                      "No response"
                    ]
                  },
                  "Feeling bad about yourself - or that you are a failure or have let yourself or your family down": {
                    "answers": [
                      "No",
                      "Yes",
                      "No response"
                    ]
                  },
                  "Trouble concentrating on things, such as reading the newspaper or watching television": {
                    "answers": [
                      "No",
                      "Yes",
                      "No response"
                    ]
                  },
                  "Moving or speaking so slowly that other people could have noticed. Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual": {
                    "answers": [
                      "No",
                      "Yes",
                      "No response"
                    ]
                  },
                  "Thoughts that you would be better off dead, or of hurting yourself in some way": {
                    "answers": [
                      "No",
                      "Yes",
                      "No response"
                    ]
                  }
                },
                "Little interest or pleasure in doing things": null,
                "Feeling down, depressed or hopeless": null,
                "Trouble falling or staying asleep, or sleeping too much": null,
                "Feeling tired or having little energy": null,
                "Poor appetite or overeating": null,
                "Feeling bad about yourself - or that you are a failure or have let yourself or your family down": null,
                "Trouble concentrating on things, such as reading the newspaper or watching television": null,
                "Moving or speaking so slowly that other people could have noticed. Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual": null,
                "Thoughts that you would be better off dead, or of hurting yourself in some way": null
              },
              "Symptom Frequency": {
                "_meta": {
                  "Little interest or pleasure in doing things": {
                    "answers": [
                      "Never or 1 day",
                      "2-6 days (several days)",
                      "7-11 days (half or more of the days)",
                      "12-14 days (nearly every day)"
                    ]
                  },
                  "Feeling down, depressed or hopeless": {
                    "answers": [
                      "Never or 1 day",
                      "2-6 days (several days)",
                      "7-11 days (half or more of the days)",
                      "12-14 days (nearly every day)"
                    ]
                  },
                  "Trouble falling or staying asleep, or sleeping too much": {
                    "answers": [
                      "Never or 1 day",
                      "2-6 days (several days)",
                      "7-11 days (half or more of the days)",
                      "12-14 days (nearly every day)"
                    ]
                  },
                  "Feeling tired or having little energy": {
                    "answers": [
                      "Never or 1 day",
                      "2-6 days (several days)",
                      "7-11 days (half or more of the days)",
                      "12-14 days (nearly every day)"
                    ]
                  },
                  "Poor appetite or overeating": {
                    "answers": [
                      "Never or 1 day",
                      "2-6 days (several days)",
                      "7-11 days (half or more of the days)",
                      "12-14 days (nearly every day)"
                    ]
                  },
                  "Feeling bad about yourself - or that you are a failure or have let yourself or your family down": {
                    "answers": [
                      "Never or 1 day",
                      "2-6 days (several days)",
                      "7-11 days (half or more of the days)",
                      "12-14 days (nearly every day)"
                    ]
                  },
                  "Trouble concentrating on things, such as reading the newspaper or watching television": {
                    "answers": [
                      "Never or 1 day",
                      "2-6 days (several days)",
                      "7-11 days (half or more of the days)",
                      "12-14 days (nearly every day)"
                    ]
                  },
                  "Moving or speaking so slowly that other people could have noticed. Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual": {
                    "answers": [
                      "Never or 1 day",
                      "2-6 days (several days)",
                      "7-11 days (half or more of the days)",
                      "12-14 days (nearly every day)"
                    ]
                  },
                  "Thoughts that you would be better off dead, or of hurting yourself in some way": {
                    "answers": [
                      "Never or 1 day",
                      "2-6 days (several days)",
                      "7-11 days (half or more of the days)",
                      "12-14 days (nearly every day)"
                    ]
                  }
                },
                "Little interest or pleasure in doing things": null,
                "Feeling down, depressed or hopeless": null,
                "Trouble falling or staying asleep, or sleeping too much": null,
                "Feeling tired or having little energy": null,
                "Poor appetite or overeating": null,
                "Feeling bad about yourself - or that you are a failure or have let yourself or your family down": null,
                "Trouble concentrating on things, such as reading the newspaper or watching television": null,
                "Moving or speaking so slowly that other people could have noticed. Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual": null,
                "Thoughts that you would be better off dead, or of hurting yourself in some way": null
              }
            },
            "Total Severity Score": 0,
            "_meta": {
              "Social Isolation. How often do you feel lonely or isolated from those around you?": {
                "answers": [
                  "Never",
                  "Rarely",
                  "Sometimes",
                  "Often",
                  "Always",
                  "Patient unable to respond"
                ]
              }
            },
            "Social Isolation. How often do you feel lonely or isolated from those around you?": null
          },
          "Behavior": {
            "_meta": {
              "Cognitive, Behavorial, and Psychiatric Symptoms that are demonstrated at least once a week (reported or observed)": {
                "answers": [
                  "Memory deficit: failure to recognize familiar persons/places, inability to recall events of past 24 hours, significant memory loss so that supervision is required",
                  "Impaired decision-making: failure to perform usual ADLs or IADLs, inability to appropriately stop activities, jeopardizes safety through actions",
                  "Verbal disruption: yelling, threatening, excessive profanity, sexual references, etc.",
                  "Physical aggression: aggressive or combative to self and others (for example, hits self, throws objects, punches, dangerous maneuvers with wheelchair or other objects)",
                  "Disruptive, infantile, or socially inappropriate behavior (excludes verbal actions)",
                  "Delusional, hallucinatory, or paranoid behavior",
                  "None of the above behaviors demonstrated"
                ]
              },
              "Frequency of Disruptive Behavior Symptoms (reported or observed): Any physical, verbal, or other disruptive/dangerous symptoms that are injurious to self or others or jeopardize personal safety.": {
                "answers": [
                  "Never",
                  "Less than once a month",
                  "Once a month",
                  "Several times each month",
                  "Several times a week",
                  "At least daily"
                ]
              }
            },
            "Cognitive, Behavorial, and Psychiatric Symptoms that are demonstrated at least once a week (reported or observed)": null,
            "Frequency of Disruptive Behavior Symptoms (reported or observed): Any physical, verbal, or other disruptive/dangerous symptoms that are injurious to self or others or jeopardize personal safety.": null
          },
          "Preferences for Customary Routine Activities": {
            "_meta": {
              "Patient Living Situation: Which of the following best describes the patient's residential circumstance and availability of assistance?": {
                "answers": [
                  "Patient lives alone - around the clock",
                  "Patient lives alone - regular daytime",
                  "Patient lives alone - regular nighttime",
                  "Patient lives alone - occasional/short-term assistance",
                  "Patient lives alone - no assistance available",
                  "Patient lives with other person(s) in the home - around the clock",
                  "Patient lives with other person(s) in the home - regular daytime",
                  "Patient lives with other person(s) in the home - regular nighttime",
                  "Patient lives with other person(s) in the home - occasional/short-term assistance",
                  "Patient lives with other person(s) in the home - no assistance available",
                  "Patient lives in congregate situation (for example, assisted living, residential care home) - around the clock",
                  "Patient lives in congregate situation (for example, assisted living, residential care home) - regular daytime",
                  "Patient lives in congregate situation (for example, assisted living, residential care home) - regular nighttime",
                  "Patient lives in congregate situation (for example, assisted living, residential care home) - occasional/short-term assistance",
                  "Patient lives in congregate situation (for example, assisted living, residential care home) - no assistance available"
                ]
              }
            },
            "Patient Living Situation: Which of the following best describes the patient's residential circumstance and availability of assistance?": null,
            "Types and Sources of Assistance": {
              "_meta": {
                "Supervision and safety (for example, due to cognitive impairment)": {
                  "answers": [
                    "No assistance needed -patient is independent or does not have needs in this area",
                    "Non-agency caregiver(s) currently provide assistance",
                    "Non-agency caregiver(s) need training/ supportive services to provide assistance",
                    "Non-agency caregiver(s) are not likely to provide assistance OR it is unclear if they will provide assistance",
                    "Assistance needed, but no non-agency caregiver(s) available"
                  ]
                }
              },
              "Supervision and safety (for example, due to cognitive impairment)": null
            }
          },
          "Functional Status": {
            "_meta": {
              "Grooming: Current ability to tend safely to personal hygiene needs (specifically: washing face and hands, hair care, shaving or make up, teeth or denture care, or fingernail care).": {
                "answers": [
                  "Able to groom self unaided, with or without the use of assistive devices or adapted methods.",
                  "Grooming utensils must be placed within reach before able to complete grooming activities.",
                  "Someone must assist the patient to groom self.",
                  "Patient depends entirely upon someone else for grooming needs."
                ]
              },
              "Current Ability to Dress Upper Body safely (with or without dressing aids) including undergarments, pullovers, front-opening shirts and blouses, managing zippers, buttons, and snaps.": {
                "answers": [
                  "Able to get clothes out of closets and drawers, put them on and remove them from the upper body without assistance.",
                  "Able to dress upper body without assistance if clothing is laid out or handed to the patient.",
                  "Someone must help the patient put on upper body clothing.",
                  "Patient depends entirely upon another person to dress the upper body."
                ]
              },
              "Current Ability to Dress Lower Body safely (with or without dressing aids) including undergarments, slacks, socks or nylons, shoes.": {
                "answers": [
                  "Able to obtain, put on, and remove clothing and shoes without assistance.",
                  "Able to dress lower body without assistance if clothing and shoes are laid out or handed to the patient.",
                  "Someone must help the patient put on undergarments, slacks, socks or nylons, and shoes.",
                  "Patient depends entirely upon another person to dress lower body."
                ]
              },
              "Bathing: Current ability to wash entire body safely. Excludes grooming (washing face, washing hands, and shampooing hair).": {
                "answers": [
                  "Able to bathe self in shower or tub independently, including getting in and out of tub/shower.",
                  "With the use of devices, is able to bathe self in shower or tub independently, including getting in and out of the tub/shower.",
                  "Able to bathe in shower or tub with the intermittent assistance of another person: (a) for intermittent supervision or encouragement or reminders, OR (b) to get in and out of the shower or tub, OR (c) for washing difficult to reach areas.",
                  "Able to participate in bathing self in shower or tub, but requires presence of another person throughout the bath for assistance or supervision.",
                  "Unable to use the shower or tub, but able to bathe self independently with or without the use of devices at the sink, in chair, or on commode.",
                  "Unable to use the shower or tub, but able to participate in bathing self in bed, at the sink, in bedside chair, or on commode, with the assistance or supervision of another person.",
                  "Unable to participate effectively in bathing and is bathed totally by another person."
                ]
              },
              "Toilet Transferring: Current ability to get to and from the toilet or bedside commode safely and transfer on and off toilet/commode.": {
                "answers": [
                  "Able to get to and from the toilet and transfer independently with or without a device.",
                  "When reminded, assisted, or supervised by another person, able to get to and from the toilet and transfer.",
                  "Unable to get to and from the toilet but is able to use a bedside commode (with or without assistance).",
                  "Unable to get to and from the toilet or bedside commode but is able to use a bedpan/urinal independently.",
                  "Is totally dependent in toileting."
                ]
              },
              "Toileting Hygiene: Current ability to maintain perineal hygiene safely, adjust clothes and/or incontinence pads before and after using toilet, commode, bedpan, urinal. If managing ostomy, includes cleaning area around stoma, but not managing equipment.": {
                "answers": [
                  "Able to manage toileting hygiene and clothing management without assistance.",
                  "Able to manage toileting hygiene and clothing management without assistance if supplies/implements are laid out for the patient.",
                  "Someone must help the patient to maintain toileting hygiene and/or adjust clothing.",
                  "Patient depends entirely upon another person to maintain toileting hygiene."
                ]
              },
              "Transferring: Current ability to move safely from bed to chair, or ability to turn and position self in bed if patient is bedfast.": {
                "answers": [
                  "Able to independently transfer.",
                  "Able to transfer with minimal human assistance or with use of an assistive device.",
                  "Able to bear weight and pivot during the transfer process but unable to transfer self.",
                  "Unable to transfer self and is unable to bear weight or pivot when transferred by another person.",
                  "Bedfast, unable to transfer but is able to turn and position self in bed.",
                  "Bedfast, unable to transfer and is unable to turn and position self."
                ]
              },
              "Ambulation/Locomotion: Current ability to walk safely, once in a standing position, or use a wheelchair, once in a seated position, on a variety of surfaces.": {
                "answers": [
                  "Able to independently walk on even and uneven surfaces and negotiate stairs with or without railings (specifically: needs no human assistance or assistive device).",
                  "With the use of a one-handed device (for example, cane, single crutch, hemi-walker), able to independently walk on even and uneven surfaces and negotiate stairs with or without railings.",
                  "Requires use of a two-handed device (for example, walker or crutches) to walk alone on a level surface and/or requires human supervision or assistance to negotiate stairs or steps or uneven surfaces.",
                  "Able to walk only with the supervision or assistance of another person at all times.",
                  "Chairfast, unable to ambulate but is able to wheel self independently.",
                  "Chairfast, unable to ambulate and is unable to wheel self.",
                  "Bedfast, unable to ambulate or be up in a chair."
                ]
              }
            },
            "Grooming: Current ability to tend safely to personal hygiene needs (specifically: washing face and hands, hair care, shaving or make up, teeth or denture care, or fingernail care).": null,
            "Current Ability to Dress Upper Body safely (with or without dressing aids) including undergarments, pullovers, front-opening shirts and blouses, managing zippers, buttons, and snaps.": null,
            "Current Ability to Dress Lower Body safely (with or without dressing aids) including undergarments, slacks, socks or nylons, shoes.": null,
            "Bathing: Current ability to wash entire body safely. Excludes grooming (washing face, washing hands, and shampooing hair).": null,
            "Toilet Transferring: Current ability to get to and from the toilet or bedside commode safely and transfer on and off toilet/commode.": null,
            "Toileting Hygiene: Current ability to maintain perineal hygiene safely, adjust clothes and/or incontinence pads before and after using toilet, commode, bedpan, urinal. If managing ostomy, includes cleaning area around stoma, but not managing equipment.": null,
            "Transferring: Current ability to move safely from bed to chair, or ability to turn and position self in bed if patient is bedfast.": null,
            "Ambulation/Locomotion: Current ability to walk safely, once in a standing position, or use a wheelchair, once in a seated position, on a variety of surfaces.": null
          },
          "Functional Abilities and Goals": {
            "Prior Functioning: Everyday Activities": {
              "_meta": {
                "Self-Care": {
                  "answers": [
                    "Independent - Patient completed all the activities by themself, with or without an assistive device, with no assistance from a helper.",
                    "Needed some help - Patient needed partial assistance from another person to complete any activities.",
                    "Dependent - A helper completed all the activities for the patient.",
                    "Unknown",
                    "Not applicable"
                  ]
                },
                "Indoor Mobility (Ambulation)": {
                  "answers": [
                    "Independent - Patient completed all the activities by themself, with or without an assistive device, with no assistance from a helper.",
                    "Needed some help - Patient needed partial assistance from another person to complete any activities.",
                    "Dependent - A helper completed all the activities for the patient.",
                    "Unknown",
                    "Not applicable"
                  ]
                },
                "Stairs": {
                  "answers": [
                    "Independent - Patient completed all the activities by themself, with or without an assistive device, with no assistance from a helper.",
                    "Needed some help - Patient needed partial assistance from another person to complete any activities.",
                    "Dependent - A helper completed all the activities for the patient.",
                    "Unknown",
                    "Not applicable"
                  ]
                },
                "Functional Cognition": {
                  "answers": [
                    "Independent - Patient completed all the activities by themself, with or without an assistive device, with no assistance from a helper.",
                    "Needed some help - Patient needed partial assistance from another person to complete any activities.",
                    "Dependent - A helper completed all the activities for the patient.",
                    "Unknown",
                    "Not applicable"
                  ]
                }
              },
              "Self-Care": null,
              "Indoor Mobility (Ambulation)": null,
              "Stairs": null,
              "Functional Cognition": null
            },
            "_meta": {
              "Prior Device Use": {
                "answers": [
                  "Manual wheelchair",
                  "Motorized wheelchair and/or scooter",
                  "Mechanical lift",
                  "Walker",
                  "Orthotics/Prosthetics",
                  "None of the above"
                ]
              }
            },
            "Prior Device Use": null,
            "Self-Care - SOC/ROC Performance": {
              "_meta": {
                "Eating": {
                  "answers": [
                    "Independent - Person completes the activity by themself with no assistance from a helper.",
                    "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                    "Person refused.",
                    "Not applicable - Person does not usually do this activity.",
                    "Not attempted due to short-term medical condition or safety concerns."
                  ]
                },
                "Oral hygiene": {
                  "answers": [
                    "Independent - Person completes the activity by themself with no assistance from a helper.",
                    "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                    "Person refused.",
                    "Not applicable - Person does not usually do this activity.",
                    "Not attempted due to short-term medical condition or safety concerns."
                  ]
                },
                "Toileting hygiene": {
                  "answers": [
                    "Independent - Patient completes the activity by themself with no assistance from a helper.",
                    "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                    "Patient refused",
                    "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                    "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                    "Not attempted due to medical condition or safety concerns"
                  ]
                },
                "Shower/bathe self": {
                  "answers": [
                    "Independent - Person completes the activity by themself with no assistance from a helper.",
                    "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                    "Person refused.",
                    "Not applicable - Person does not usually do this activity.",
                    "Not attempted due to short-term medical condition or safety concerns."
                  ]
                },
                "Upper body dressing": {
                  "answers": [
                    "Independent - Person completes the activity by themself with no assistance from a helper.",
                    "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                    "Person refused.",
                    "Not applicable - Person does not usually do this activity.",
                    "Not attempted due to short-term medical condition or safety concerns."
                  ]
                },
                "Lower body dressing": {
                  "answers": [
                    "Independent - Person completes the activity by themself with no assistance from a helper.",
                    "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                    "Person refused.",
                    "Not applicable - Person does not usually do this activity.",
                    "Not attempted due to short-term medical condition or safety concerns."
                  ]
                },
                "Putting on/taking off footwear": {
                  "answers": [
                    "Independent - Person completes the activity by themself with no assistance from a helper.",
                    "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                    "Person refused.",
                    "Not applicable - Person does not usually do this activity.",
                    "Not attempted due to short-term medical condition or safety concerns."
                  ]
                }
              },
              "Eating": null,
              "Oral hygiene": null,
              "Toileting hygiene": null,
              "Shower/bathe self": null,
              "Upper body dressing": null,
              "Lower body dressing": null,
              "Putting on/taking off footwear": null
            },
            "Self-Care - Discharge Goal": {
              "_meta": {
                "Eating": {
                  "answers": [
                    "Independent - Patient completes the activity by themself with no assistance from a helper.",
                    "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                    "Patient refused",
                    "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                    "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                    "Not attempted due to medical condition or safety concerns"
                  ]
                },
                "Oral hygiene": {
                  "answers": [
                    "Independent - Patient completes the activity by themself with no assistance from a helper.",
                    "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                    "Patient refused",
                    "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                    "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                    "Not attempted due to medical condition or safety concerns"
                  ]
                },
                "Toileting hygiene": {
                  "answers": [
                    "Independent - Patient completes the activity by themself with no assistance from a helper.",
                    "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                    "Patient refused",
                    "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                    "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                    "Not attempted due to medical condition or safety concerns"
                  ]
                },
                "Shower/bathe self": {
                  "answers": [
                    "Independent - Patient completes the activity by themself with no assistance from a helper.",
                    "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                    "Patient refused",
                    "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                    "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                    "Not attempted due to medical condition or safety concerns"
                  ]
                },
                "Upper body dressing": {
                  "answers": [
                    "Independent - Patient completes the activity by themself with no assistance from a helper.",
                    "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                    "Patient refused",
                    "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                    "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                    "Not attempted due to medical condition or safety concerns"
                  ]
                },
                "Lower body dressing": {
                  "answers": [
                    "Independent - Patient completes the activity by themself with no assistance from a helper.",
                    "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                    "Patient refused",
                    "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                    "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                    "Not attempted due to medical condition or safety concerns"
                  ]
                },
                "Putting on/taking off footwear": {
                  "answers": [
                    "Independent - Patient completes the activity by themself with no assistance from a helper.",
                    "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                    "Patient refused",
                    "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                    "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                    "Not attempted due to medical condition or safety concerns"
                  ]
                }
              },
              "Eating": null,
              "Oral hygiene": null,
              "Toileting hygiene": null,
              "Shower/bathe self": null,
              "Upper body dressing": null,
              "Lower body dressing": null,
              "Putting on/taking off footwear": null
            },
            "Mobility - SOC/ROC Performance": {
              "_meta": {
                "Roll left and right": {
                  "answers": [
                    "Independent - Person completes the activity by themself with no assistance from a helper.",
                    "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                    "Person refused.",
                    "Not applicable - Person does not usually do this activity.",
                    "Not attempted due to short-term medical condition or safety concerns."
                  ]
                },
                "Sit to lying": {
                  "answers": [
                    "Independent - Person completes the activity by themself with no assistance from a helper.",
                    "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                    "Person refused.",
                    "Not applicable - Person does not usually do this activity.",
                    "Not attempted due to short-term medical condition or safety concerns."
                  ]
                },
                "Lying to sitting on side of bed": {
                  "answers": [
                    "Independent - Patient completes the activity by themself with no assistance from a helper.",
                    "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                    "Patient refused",
                    "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                    "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                    "Not attempted due to medical condition or safety concerns"
                  ]
                },
                "Sit to stand": {
                  "answers": [
                    "Independent - Person completes the activity by themself with no assistance from a helper.",
                    "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                    "Person refused.",
                    "Not applicable - Person does not usually do this activity.",
                    "Not attempted due to short-term medical condition or safety concerns."
                  ]
                },
                "Chair/bed-to-chair transfer": {
                  "answers": [
                    "Independent - Person completes the activity by themself with no assistance from a helper.",
                    "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                    "Person refused.",
                    "Not applicable - Person does not usually do this activity.",
                    "Not attempted due to short-term medical condition or safety concerns."
                  ]
                },
                "Toilet transfer": {
                  "answers": [
                    "Independent - Patient completes the activity by themself with no assistance from a helper.",
                    "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                    "Patient refused",
                    "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                    "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                    "Not attempted due to medical condition or safety concerns"
                  ]
                },
                "Car transfer": {
                  "answers": [
                    "Independent - Person completes the activity by themself with no assistance from a helper.",
                    "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                    "Person refused.",
                    "Not applicable - Person does not usually do this activity.",
                    "Not attempted due to short-term medical condition or safety concerns."
                  ]
                },
                "Walk 10 feet": {
                  "answers": [
                    "Independent - Person completes the activity by themself with no assistance from a helper.",
                    "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                    "Person refused.",
                    "Not applicable - Person does not usually do this activity.",
                    "Not attempted due to short-term medical condition or safety concerns."
                  ]
                },
                "Walk 50 feet with two turns": {
                  "answers": [
                    "Independent - Person completes the activity by themself with no assistance from a helper.",
                    "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                    "Person refused.",
                    "Not applicable - Person does not usually do this activity.",
                    "Not attempted due to short-term medical condition or safety concerns."
                  ]
                },
                "Walk 150 feet": {
                  "answers": [
                    "Independent - Person completes the activity by themself with no assistance from a helper.",
                    "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                    "Person refused.",
                    "Not applicable - Person does not usually do this activity.",
                    "Not attempted due to short-term medical condition or safety concerns."
                  ]
                },
                "Walking 10 feet on uneven surfaces": {
                  "answers": [
                    "Independent - Person completes the activity by themself with no assistance from a helper.",
                    "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                    "Person refused.",
                    "Not applicable - Person does not usually do this activity.",
                    "Not attempted due to short-term medical condition or safety concerns."
                  ]
                },
                "1 step (curb)": {
                  "answers": [
                    "Independent - Person completes the activity by themself with no assistance from a helper.",
                    "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                    "Person refused.",
                    "Not applicable - Person does not usually do this activity.",
                    "Not attempted due to short-term medical condition or safety concerns."
                  ]
                },
                "4 steps": {
                  "answers": [
                    "Independent - Person completes the activity by themself with no assistance from a helper.",
                    "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                    "Person refused.",
                    "Not applicable - Person does not usually do this activity.",
                    "Not attempted due to short-term medical condition or safety concerns."
                  ]
                },
                "12 steps": {
                  "answers": [
                    "Independent - Person completes the activity by themself with no assistance from a helper.",
                    "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                    "Person refused.",
                    "Not applicable - Person does not usually do this activity.",
                    "Not attempted due to short-term medical condition or safety concerns."
                  ]
                },
                "Picking up object": {
                  "answers": [
                    "Independent - Person completes the activity by themself with no assistance from a helper.",
                    "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                    "Person refused.",
                    "Not applicable - Person does not usually do this activity.",
                    "Not attempted due to short-term medical condition or safety concerns."
                  ]
                },
                "Does the patient use a wheelchair and/or scooter?": {
                  "answers": [
                    "No",
                    "Yes"
                  ]
                },
                "Wheel 50 feet with two turns": {
                  "answers": [
                    "Independent - Person completes the activity by themself with no assistance from a helper.",
                    "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                    "Person refused.",
                    "Not applicable - Person does not usually do this activity.",
                    "Not attempted due to short-term medical condition or safety concerns."
                  ]
                },
                "Indicate the type of wheelchair or scooter used": {
                  "answers": [
                    "Manual",
                    "Motorized"
                  ]
                },
                "Wheel 150 feet": {
                  "answers": [
                    "Independent - Person completes the activity by themself with no assistance from a helper.",
                    "Setup or cleanup assistance - Helper sets up or cleans up; person completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as person completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Person does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the person to complete the activity.",
                    "Person refused.",
                    "Not applicable - Person does not usually do this activity.",
                    "Not attempted due to short-term medical condition or safety concerns."
                  ]
                }
              },
              "Roll left and right": null,
              "Sit to lying": null,
              "Lying to sitting on side of bed": null,
              "Sit to stand": null,
              "Chair/bed-to-chair transfer": null,
              "Toilet transfer": null,
              "Car transfer": null,
              "Walk 10 feet": null,
              "Walk 50 feet with two turns": null,
              "Walk 150 feet": null,
              "Walking 10 feet on uneven surfaces": null,
              "1 step (curb)": null,
              "4 steps": null,
              "12 steps": null,
              "Picking up object": null,
              "Does the patient use a wheelchair and/or scooter?": null,
              "Wheel 50 feet with two turns": null,
              "Indicate the type of wheelchair or scooter used": null,
              "Wheel 150 feet": null
            },
            "Mobility - Discharge Goal": {
              "_meta": {
                "Roll left and right": {
                  "answers": [
                    "Independent - Patient completes the activity by themself with no assistance from a helper.",
                    "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                    "Patient refused",
                    "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                    "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                    "Not attempted due to medical condition or safety concerns"
                  ]
                },
                "Sit to lying": {
                  "answers": [
                    "Independent - Patient completes the activity by themself with no assistance from a helper.",
                    "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                    "Patient refused",
                    "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                    "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                    "Not attempted due to medical condition or safety concerns"
                  ]
                },
                "Lying to sitting on side of bed": {
                  "answers": [
                    "Independent - Patient completes the activity by themself with no assistance from a helper.",
                    "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                    "Patient refused",
                    "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                    "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                    "Not attempted due to medical condition or safety concerns"
                  ]
                },
                "Sit to stand": {
                  "answers": [
                    "Independent - Patient completes the activity by themself with no assistance from a helper.",
                    "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                    "Patient refused",
                    "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                    "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                    "Not attempted due to medical condition or safety concerns"
                  ]
                },
                "Chair/bed-to-chair transfer": {
                  "answers": [
                    "Independent - Patient completes the activity by themself with no assistance from a helper.",
                    "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                    "Patient refused",
                    "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                    "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                    "Not attempted due to medical condition or safety concerns"
                  ]
                },
                "Toilet transfer": {
                  "answers": [
                    "Independent - Patient completes the activity by themself with no assistance from a helper.",
                    "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                    "Patient refused",
                    "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                    "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                    "Not attempted due to medical condition or safety concerns"
                  ]
                },
                "Car transfer": {
                  "answers": [
                    "Independent - Patient completes the activity by themself with no assistance from a helper.",
                    "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                    "Patient refused",
                    "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                    "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                    "Not attempted due to medical condition or safety concerns"
                  ]
                },
                "Walk 10 feet": {
                  "answers": [
                    "Independent - Patient completes the activity by themself with no assistance from a helper.",
                    "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                    "Patient refused",
                    "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                    "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                    "Not attempted due to medical condition or safety concerns"
                  ]
                },
                "Walk 50 feet with two turns": {
                  "answers": [
                    "Independent - Patient completes the activity by themself with no assistance from a helper.",
                    "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                    "Patient refused",
                    "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                    "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                    "Not attempted due to medical condition or safety concerns"
                  ]
                },
                "Walk 150 feet": {
                  "answers": [
                    "Independent - Patient completes the activity by themself with no assistance from a helper.",
                    "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                    "Patient refused",
                    "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                    "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                    "Not attempted due to medical condition or safety concerns"
                  ]
                },
                "Walking 10 feet on uneven surfaces": {
                  "answers": [
                    "Independent - Patient completes the activity by themself with no assistance from a helper.",
                    "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                    "Patient refused",
                    "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                    "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                    "Not attempted due to medical condition or safety concerns"
                  ]
                },
                "1 step (curb)": {
                  "answers": [
                    "Independent - Patient completes the activity by themself with no assistance from a helper.",
                    "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                    "Patient refused",
                    "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                    "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                    "Not attempted due to medical condition or safety concerns"
                  ]
                },
                "4 steps": {
                  "answers": [
                    "Independent - Patient completes the activity by themself with no assistance from a helper.",
                    "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                    "Patient refused",
                    "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                    "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                    "Not attempted due to medical condition or safety concerns"
                  ]
                },
                "12 steps": {
                  "answers": [
                    "Independent - Patient completes the activity by themself with no assistance from a helper.",
                    "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                    "Patient refused",
                    "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                    "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                    "Not attempted due to medical condition or safety concerns"
                  ]
                },
                "Picking up object": {
                  "answers": [
                    "Independent - Patient completes the activity by themself with no assistance from a helper.",
                    "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                    "Patient refused",
                    "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                    "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                    "Not attempted due to medical condition or safety concerns"
                  ]
                },
                "Wheel 50 feet with two turns": {
                  "answers": [
                    "Independent - Patient completes the activity by themself with no assistance from a helper.",
                    "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                    "Patient refused",
                    "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                    "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                    "Not attempted due to medical condition or safety concerns"
                  ]
                },
                "Wheel 150 feet": {
                  "answers": [
                    "Independent - Patient completes the activity by themself with no assistance from a helper.",
                    "Setup or clean-up assistance - Helper sets up or cleans up; patient completes activity. Helper assists only prior to or following the activity.",
                    "Supervision or touching assistance - Helper provides verbal cues and/or touching/steadying and/or contact guard assistance as patient completes activity. Assistance may be provided throughout the activity or intermittently.",
                    "Partial/moderate assistance - Helper does less than half the effort. Helper lifts, holds or supports trunk or limbs, but provides less than half the effort.",
                    "Substantial/maximal assistance - Helper does more than half the effort. Helper lifts or holds trunk or limbs and provides more than half the effort.",
                    "Dependent - Helper does all of the effort. Patient does none of the effort to complete the activity. Or, the assistance of 2 or more helpers is required for the patient to complete the activity.",
                    "Patient refused",
                    "Not applicable - Not attempted and the patient did not perform this activity prior to the current illness, exacerbation, or injury.",
                    "Not attempted due to environmental limitations (e.g., lack of equipment, weather constraints).",
                    "Not attempted due to medical condition or safety concerns"
                  ]
                }
              },
              "Roll left and right": null,
              "Sit to lying": null,
              "Lying to sitting on side of bed": null,
              "Sit to stand": null,
              "Chair/bed-to-chair transfer": null,
              "Toilet transfer": null,
              "Car transfer": null,
              "Walk 10 feet": null,
              "Walk 50 feet with two turns": null,
              "Walk 150 feet": null,
              "Walking 10 feet on uneven surfaces": null,
              "1 step (curb)": null,
              "4 steps": null,
              "12 steps": null,
              "Picking up object": null,
              "Wheel 50 feet with two turns": null,
              "Wheel 150 feet": null
            }
          },
          "Bladder and Bowel": {
            "_meta": {
              "Has this patient been treated for a Urinary Tract Infection in the past 14 days?": {
                "answers": [
                  "No",
                  "Yes",
                  "Patient on prophylactic treatment",
                  "Unknown"
                ]
              },
              "Urinary Incontinence or Urinary Catheter Presence": {
                "answers": [
                  "No incontinence or catheter (includes anuria or ostomy for urinary drainage)",
                  "Patient is incontinent",
                  "Patient requires a urinary catheter (specifically: external, indwelling, intermittent, or suprapubic)"
                ]
              },
              "Bowel Incontinence Frequency": {
                "answers": [
                  "Very rarely or never has bowel incontinence",
                  "Less than once weekly",
                  "One to three times weekly",
                  "Four to six times weekly",
                  "On a daily basis",
                  "More often than once daily",
                  "Patient has ostomy for bowel elimination",
                  "Unknown"
                ]
              },
              "Ostomy for Bowel Elimination: Does this patient have an ostomy for bowel elimination that (within the last 14 days): a) was related to an inpatient facility stay; or b) necessitated a change in medical or treatment regimen?": {
                "answers": [
                  "Patient does not have an ostomy for bowel elimination.",
                  "Patient's ostomy was not related to an inpatient stay and did not necessitate change in medical or treatment regimen.",
                  "The ostomy was related to an inpatient stay or did necessitate change in medical or treatment regimen."
                ]
              }
            },
            "Has this patient been treated for a Urinary Tract Infection in the past 14 days?": null,
            "Urinary Incontinence or Urinary Catheter Presence": null,
            "Bowel Incontinence Frequency": null,
            "Ostomy for Bowel Elimination: Does this patient have an ostomy for bowel elimination that (within the last 14 days): a) was related to an inpatient facility stay; or b) necessitated a change in medical or treatment regimen?": null
          },
          "Active Diagnoses": {
            "_meta": {
              "Active Diagnoses-Comorbidities and Co-existing Conditions": {
                "answers": [
                  "Peripheral vascular disease (PVD) or peripheral arterial disease (PAD)",
                  "Diabetes mellitus (DM)",
                  "None of the above"
                ]
              }
            },
            "Active Diagnoses-Comorbidities and Co-existing Conditions": null,
            "Primary Diagnosis & Other Diagnoses": {
              "Primary Diagnosis": {
                "_meta": {
                  "Primary Diagnosis: ICD-10-code": {
                    "answers": [
                      null
                    ]
                  },
                  "Primary Diagnosis Symptom Control Rating": {
                    "answers": [
                      "Asymptomatic, no treatment needed at this time",
                      "Symptoms well controlled with current therapy",
                      "Symptoms controlled with difficulty, affecting daily functioning; patient needs ongoing monitoring",
                      "Symptoms poorly controlled; patient needs frequent adjustment in treatment and dose monitoring",
                      "Symptoms poorly controlled; history of re-hospitalizations"
                    ]
                  }
                },
                "Primary Diagnosis: ICD-10-code": null,
                "Primary Diagnosis Symptom Control Rating": null
              },
              "Other Diagnoses": {
                "Other Diagnoses: ICD-10-CM": null,
                "_meta": {
                  "Other Diagnoses Symptom Control Rating": {
                    "answers": [
                      "Asymptomatic, no treatment needed at this time",
                      "Symptoms well controlled with current therapy",
                      "Symptoms controlled with difficulty, affecting daily functioning; patient needs ongoing monitoring",
                      "Symptoms poorly controlled; patient needs frequent adjustment in treatment and dose monitoring",
                      "Symptoms poorly controlled; history of re-hospitalizations"
                    ]
                  }
                },
                "Other Diagnoses Symptom Control Rating": null
              }
            }
          },
          "Health Conditions": {
            "_meta": {
              "Risk for Hospitalization: Which of the following signs or symptoms characterize this patient as at risk for hospitalization?": {
                "answers": [
                  "History of falls (2 or more falls - or any fall with an injury - in the past 12 months)",
                  "Unintentional weight loss of a total of 10 pounds or more in the past 12 months",
                  "Multiple hospitalizations (2 or more) in the past 6 months",
                  "Multiple emergency department visits (2 or more) in the past 6 months",
                  "Decline in mental, emotional, or behavioral status in the past 3 months",
                  "Reported or observed history of difficulty complying with any medical instructions (for example, medications, diet, exercise) in the past 3 months",
                  "Currently taking 5 or more medications",
                  "Currently reports exhaustion",
                  "Other risk(s) not listed in 1 - 8",
                  "None of the above"
                ]
              },
              "Pain Effect on Sleep. Over the past 5 days, how much of the time has pain made it hard for you to sleep at night?": {
                "answers": [
                  "Does not apply - I have not had any pain or hurting in the past 5 days",
                  "Rarely or not at all",
                  "Occasionally",
                  "Frequently",
                  "Almost constantly",
                  "Unable to answer"
                ]
              },
              "Pain Interference with Therapy Activities. Over the past 5 days, how often have you limited your participation in rehabilitation therapy sessions due to pain?": {
                "answers": [
                  "Does not apply - I have not received rehabilitation therapy in the past 5 days",
                  "Rarely or not at all",
                  "Occasionally",
                  "Frequently",
                  "Almost constantly",
                  "Unable to answer"
                ]
              },
              "Pain Interference with Day-to-Day Activities. Over the past 5 days, how often have you limited your day-to-day activities (excluding rehabilitation therapy sessions) because of pain?": {
                "answers": [
                  "Does not apply - I have not received rehabilitation therapy in the past 5 days",
                  "Rarely or not at all",
                  "Occasionally",
                  "Frequently",
                  "Almost constantly",
                  "Unable to answer"
                ]
              },
              "When is the patient dyspneic or noticeably Short of Breath?": {
                "answers": [
                  "Patient is not short of breath",
                  "When walking more than 20 feet, climbing stairs",
                  "With moderate exertion (for example, while dressing, using commode or bedpan, walking distances less than 20 feet)",
                  "With minimal exertion (for example, while eating, talking, or performing other ADLs) or with agitation",
                  "At rest (during day or night)"
                ]
              }
            },
            "Risk for Hospitalization: Which of the following signs or symptoms characterize this patient as at risk for hospitalization?": null,
            "Pain Effect on Sleep. Over the past 5 days, how much of the time has pain made it hard for you to sleep at night?": null,
            "Pain Interference with Therapy Activities. Over the past 5 days, how often have you limited your participation in rehabilitation therapy sessions due to pain?": null,
            "Pain Interference with Day-to-Day Activities. Over the past 5 days, how often have you limited your day-to-day activities (excluding rehabilitation therapy sessions) because of pain?": null,
            "When is the patient dyspneic or noticeably Short of Breath?": null
          },
          "Swallowing/Nutritional Status": {
            "Height and Weight:  - While measuring, if the number is X.1-X.4 round down; X.5 or greater round up.": {
              "Height (in inches)": null,
              "Weight (in pounds)": null
            },
            "_meta": {
              "Nutritional Approaches - On Admission. Check all of the following nutritional approaches that apply on admission.": {
                "answers": [
                  "Parenteral/IV feeding",
                  "Feeding tube (e.g., nasogastric or abdominal (PEG))",
                  "Mechanically altered diet - require change in texture of food or liquids (e.g., pureed food, thickened liquids)",
                  "Therapeutic diet (e.g. low salt, diabetic, low cholesterol)",
                  "None of the above"
                ]
              },
              "Feeding or Eating: Current ability to feed self meals and snacks safely.": {
                "answers": [
                  "Able to independently feed self.",
                  "Able to feed self independently but requires: (a) meal set-up; OR (b) intermittent assistance or supervision from another person; OR (c) a liquid, pureed or ground meat diet.",
                  "Unable to feed self and must be assisted or supervised throughout the meal/snack.",
                  "Able to take in nutrients orally AND receives supplemental nutrients through a nasogastric tube or gastrostomy.",
                  "Unable to take in nutrients orally and is fed nutrients through a nasogastric tube or gastrostomy.",
                  "Unable to take in nutrients orally or by tube feeding."
                ]
              }
            },
            "Nutritional Approaches - On Admission. Check all of the following nutritional approaches that apply on admission.": null,
            "Feeding or Eating: Current ability to feed self meals and snacks safely.": null
          },
          "Skin Conditions": {
            "_meta": {
              "Does this patient have at least one Unhealed Pressure Ulcer/Injury at Stage 2 or Higher or designated as Unstageable?": {
                "answers": [
                  "No",
                  "Yes"
                ]
              },
              "Current Number of Stage 1 Pressure Injuries": {
                "answers": [
                  "0",
                  "1",
                  "2",
                  "3",
                  "4 or more"
                ]
              },
              "Stage of Most Problematic Unhealed Pressure Ulcer/Injury that is Stageable": {
                "answers": [
                  "Stage 1",
                  "Stage 2",
                  "Stage 3",
                  "Stage 4",
                  "Patient has no pressure ulcers/injuries or no stageable pressure ulcers/injuries"
                ]
              },
              "Does this patient have a Stasis Ulcer?": {
                "answers": [
                  "No",
                  "Yes, patient has BOTH observable and unobservable stasis ulcers",
                  "Yes, patient has observable stasis ulcers ONLY",
                  "Yes, patient has unobservable stasis ulcers ONLY (known but not observable due to non-removable dressing/device)"
                ]
              },
              "Current Number of Stasis Ulcer(s) that are Observable": {
                "answers": [
                  "One",
                  "Two",
                  "Three",
                  "Four"
                ]
              },
              "Status of Most Problematic Stasis Ulcer that is Observable": {
                "answers": [
                  "Fully granulating",
                  "Early/partial granulation",
                  "Not healing"
                ]
              },
              "Does this patient have a Surgical Wound?": {
                "answers": [
                  "No",
                  "Yes, patient has at least one observable surgical wound",
                  "Surgical wound known but not observable due to non-removable dressing/device"
                ]
              },
              "Status of Most Problematic Surgical Wound that is Observable": {
                "answers": [
                  "Newly epithelialized",
                  "Fully granulating",
                  "Early/partial granulation",
                  "Not healing"
                ]
              }
            },
            "Does this patient have at least one Unhealed Pressure Ulcer/Injury at Stage 2 or Higher or designated as Unstageable?": null,
            "Current Number of Unhealed Pressure Ulcers/Injuries at Each Stage": {
              "Number of Stage 2 pressure ulcers": null,
              "Number of Stage 3 pressure ulcers": null,
              "Number of Stage 4 pressure ulcers": null,
              "Number of unstageable pressure ulcers/injuries due to non-removable dressing/device": null,
              "Number of unstageable pressure ulcers/injuries due to coverage of wound bed by slough and/or eschar": null,
              "Number of unstageable pressure injuries presenting as deep tissue injury": null
            },
            "Current Number of Stage 1 Pressure Injuries": null,
            "Stage of Most Problematic Unhealed Pressure Ulcer/Injury that is Stageable": null,
            "Does this patient have a Stasis Ulcer?": null,
            "Current Number of Stasis Ulcer(s) that are Observable": null,
            "Status of Most Problematic Stasis Ulcer that is Observable": null,
            "Does this patient have a Surgical Wound?": null,
            "Status of Most Problematic Surgical Wound that is Observable": null
          },
          "Medications": {
            "High-Risk Drug Classes: Use and Indication": {
              "_meta": {
                "Is taking. Check if the patient is taking any medications by pharmacological classification, not how it is used, in the following classes": {
                  "answers": [
                    "Antipsychotic",
                    "Anticoagulant",
                    "Antibiotic",
                    "Opioid",
                    "Antiplatelet",
                    "Hypoglycemic (including insulin)",
                    "None of the above"
                  ]
                },
                "Indication noted. If column 1 [Is Taking] is checked, check if there is an indication noted for all medications in the drug class": {
                  "answers": [
                    "Antipsychotic",
                    "Anticoagulant",
                    "Antibiotic",
                    "Opioid",
                    "Antiplatelet",
                    "Hypoglycemic (including insulin)"
                  ]
                }
              },
              "Is taking. Check if the patient is taking any medications by pharmacological classification, not how it is used, in the following classes": null,
              "Indication noted. If column 1 [Is Taking] is checked, check if there is an indication noted for all medications in the drug class": null
            },
            "_meta": {
              "Drug Regimen Review: Did a complete drug regimen review identify potential clinically significant medication issues?": {
                "answers": [
                  "No - No issues found during review",
                  "Yes - Issues found during review",
                  "NA - Resident is not taking any medications"
                ]
              },
              "Medication Follow-up: Did the agency contact a physician (or physician-designee) by midnight of the next calendar day and complete prescribed/recommended actions in response to the identified potential clinically significant medication issues?": {
                "answers": [
                  "No",
                  "Yes"
                ]
              },
              "Patient/Caregiver High-Risk Drug Education: Has the patient/caregiver received instruction on special precautions for all high-risk medications (such as hypoglycemics, anticoagulants, etc.) and how and when to report problems that may occur?": {
                "answers": [
                  "No",
                  "Yes",
                  "Patient not taking any high risk drugs OR patient/caregiver fully knowledgeable about special precautions associated with all high-risk medications"
                ]
              },
              "Management of Oral Medications: Patient's current ability to prepare and take all oral medications reliably and safely, including administration of the correct dosage at the appropriate times/intervals.": {
                "answers": [
                  "Able to independently take the correct oral medication(s) and proper dosage(s) at the correct times.",
                  "Able to take medication(s) at the correct times if: (a) individual dosages are prepared in advance by another person; OR (b) another person develops a drug diary or chart.",
                  "Able to take medication(s) at the correct times if given reminders by another person at the appropriate times",
                  "Unable to take medication unless administered by another person.",
                  "No oral medications prescribed."
                ]
              },
              "Management of Injectable Medications: Patient's current ability to prepare and take all prescribed injectable medications reliably and safely, including administration of correct dosage at the appropriate times/intervals.": {
                "answers": [
                  "Able to independently take the correct medication(s) and proper dosage(s) at the correct times.",
                  "Able to take injectable medication(s) at the correct times if: (a) individual syringes are prepared in advance by another person; OR (b) another person develops a drug diary or chart.",
                  "Able to take medication(s) at the correct times if given reminders by another person based on the frequency of the injection",
                  "Unable to take injectable medication unless administered by another person.",
                  "No injectable medications prescribed."
                ]
              }
            },
            "Drug Regimen Review: Did a complete drug regimen review identify potential clinically significant medication issues?": null,
            "Medication Follow-up: Did the agency contact a physician (or physician-designee) by midnight of the next calendar day and complete prescribed/recommended actions in response to the identified potential clinically significant medication issues?": null,
            "Patient/Caregiver High-Risk Drug Education: Has the patient/caregiver received instruction on special precautions for all high-risk medications (such as hypoglycemics, anticoagulants, etc.) and how and when to report problems that may occur?": null,
            "Management of Oral Medications: Patient's current ability to prepare and take all oral medications reliably and safely, including administration of the correct dosage at the appropriate times/intervals.": null,
            "Management of Injectable Medications: Patient's current ability to prepare and take all prescribed injectable medications reliably and safely, including administration of correct dosage at the appropriate times/intervals.": null
          },
          "Special Treatment, Procedures, and Programs": {
            "_meta": {
              "Special Treatments, Procedures, and Programs - On Admission. Check all of the following treatments, procedures, and programs that apply on admission.": {
                "answers": [
                  "Chemotherapy",
                  "Chemotherapy - IV",
                  "Chemotherapy - Oral",
                  "Chemotherapy - Other",
                  "Radiation",
                  "Oxygen therapy",
                  "Oxygen therapy - Continuous",
                  "Oxygen therapy - Intermittent",
                  "Oxygen therapy - High-concentration",
                  "Suctioning",
                  "Suctioning - Scheduled",
                  "Suctioning - As needed",
                  "Tracheostomy care",
                  "Invasive Mechanical Ventilator (ventilator or respirator)",
                  "Non-invasive mechanical ventilator",
                  "Non-invasive mechanical ventilator - BiPAP",
                  "Non-invasive mechanical ventilator - CPAP",
                  "IV medications",
                  "IV medications - Vasoactive medications",
                  "IV medications - Antibiotics",
                  "IV medications - Anticoagulation",
                  "IV medications - Other",
                  "Transfusions",
                  "Dialysis",
                  "Dialysis - Hemodialysis",
                  "Dialysis - Peritoneal dialysis",
                  "IV Access",
                  "IV Access - Peripheral",
                  "IV Access - Midline",
                  "IV Access - Central (e.g., PICC, tunneled, port)",
                  "None of the above"
                ]
              }
            },
            "Special Treatments, Procedures, and Programs - On Admission. Check all of the following treatments, procedures, and programs that apply on admission.": null,
            "Therapy need: Number of therapy visits indicated (total of physical, occupational and speech-language pathology combined).": null
          }
        }
      } newData={
        {
          "Administrative Information": {
            "_meta": {
              "National Provider Identifier (NPI) for the attending physician who has signed the plan of care": {
                "answers": [
                  null
                ]
              },
              "Branch State": {
                "answers": [
                  null
                ]
              },
              "Patient State of Residence": {
                "answers": [
                  null
                ]
              },
              "Gender": {
                "answers": [
                  "Male",
                  "Female"
                ]
              },
              "Ethnicity: Are you of Hispanic, Latino/a, or Spanish origin?": {
                "answers": [
                  "No, not of Hispanic, Latino/a, or Spanish origin",
                  "Yes, Mexican, Mexican American, Chicano/a",
                  "Yes, Puerto Rican",
                  "Yes, Cuban",
                  "Yes, another Hispanic, Latino, or Spanish origin",
                  "Patient unable to respond"
                ]
              },
              "Race: What is your race?": {
                "answers": [
                  "White",
                  "Black or African American",
                  "American Indian or Alaska Native",
                  "Asian Indian",
                  "Chinese",
                  "Filipino",
                  "Japanese",
                  "Korean",
                  "Vietnamese",
                  "Other Asian",
                  "Native Hawaiian",
                  "Guamanian or Chamorro",
                  "Samoan",
                  "Other Pacific Islander",
                  "Patient unable to respond"
                ]
              },
              "Current Payment Sources for Home Care": {
                "answers": [
                  "None; no charge for current services",
                  "Medicare (traditional fee-for-service)",
                  "Medicare (HMO/managed care/Advantage plan)",
                  "Medicaid (traditional fee-for-service)",
                  "Medicaid (HMO/managed care)",
                  "Workers' compensation",
                  "Title programs (for example, Title III, V, or XX)",
                  "Other government (for example, Tricare, VA)",
                  "Private insurance",
                  "Private HMO/managed care",
                  "Self-pay",
                  "Other (specify)",
                  "Unknown"
                ]
              },
              "Discipline of Person Completing Assessment": {
                "answers": [
                  "RN",
                  "PT",
                  "SLP/ST",
                  "OT"
                ]
              },
              "This Assessment is Currently Being Completed for the Following Reason": {
                "answers": [
                  "Start of care - further visits planned",
                  "Resumption of care (after inpatient stay)",
                  "Recertification (follow-up) reassessment",
                  "Other follow-up",
                  "Transferred to an inpatient facility - patient not discharged from agency",
                  "Transferred to an inpatient facility - patient discharged from agency",
                  "Death at home",
                  "Discharge from agency"
                ]
              },
              "Episode Timing: Is the Medicare home health payment episode for which this assessment will define a case mix group an \"early\" episode or a \"later\" episode in the patient's current sequence of adjacent Medicare home health payment episodes?": {
                "answers": [
                  "Early",
                  "Later",
                  "Unknown",
                  "Not Applicable: No Medicare case mix group to be defined by this assessment."
                ]
              },
              "Transportation. Has lack of transportation kept you from medical appointments, meetings, work, or from getting things needed for daily living?": {
                "answers": [
                  "Yes, it has kept me from medical appointments or from getting my medications",
                  "Yes, it has kept me from non-medical meetings, appointments, work, or from getting things that I need",
                  "No",
                  "Resident unable to respond",
                  "Resident declines to respond"
                ]
              },
              "From which of the following Inpatient Facilities was the patient discharged within the past 14 days?": {
                "answers": [
                  "Long-term nursing facility (NF)",
                  "Skilled nursing facility (SNF/TCU)",
                  "Short-stay acute hospital (IPPS)",
                  "Long-Term Care Hospital (LTCH)",
                  "Inpatient rehabilitation hospital or unit (IRF)",
                  "Psychiatric hospital or unit",
                  "Other (specify)",
                  "Patient was not discharged from an inpatient facility"
                ]
              }
            },
            "National Provider Identifier (NPI) for the attending physician who has signed the plan of care": '123456',
            "CMS Certification Number": null,
            "Branch State": null,
            "Branch ID Number": null,
            "Patient ID Number": null,
            "Patient Name": {
              "(First)": 'New first name',
              "(MI)": null,
              "(Last)": 'New last name',
              "(Suffix)": null
            },
            "Patient State of Residence": null,
            "Patient ZIP Code": '31337',
            "Social Security Number": null,
            "Medicare Number": null,
            "Medicaid Number": null,
            "Gender": null,
            "Birth Date": null,
            "Ethnicity: Are you of Hispanic, Latino/a, or Spanish origin?": "Yes, Cuban",
            "Race: What is your race?": null,
            "Current Payment Sources for Home Care": null,
            "Language": {
              "_meta": {
                "What is your preferred language?": {
                  "answers": [
                    "English",
                    "Spanish",
                    "Chinese",
                    "Vietnamese",
                    "Tagalog",
                    "Other"
                  ]
                },
                "Do you need or want an interpreter to communicate with a doctor or health care staff?": {
                  "answers": [
                    "No",
                    "Yes",
                    "Unable to determine"
                  ]
                }
              },
              "What is your preferred language?": null,
              "Do you need or want an interpreter to communicate with a doctor or health care staff?": null
            },
            "Start of Care Date": null,
            "Discipline of Person Completing Assessment": null,
            "Date Assessment Completed": null,
            "This Assessment is Currently Being Completed for the Following Reason": null,
            "Date of Physician-ordered Start of Care (Resumption of Care)": null,
            "Date of Referral": null,
            "Episode Timing: Is the Medicare home health payment episode for which this assessment will define a case mix group an \"early\" episode or a \"later\" episode in the patient's current sequence of adjacent Medicare home health payment episodes?": null,
            "Transportation. Has lack of transportation kept you from medical appointments, meetings, work, or from getting things needed for daily living?": null,
            "From which of the following Inpatient Facilities was the patient discharged within the past 14 days?": null,
            "Inpatient Discharge Date (most recent)": null
          },
        }
      } /> */}
    </ChakraProvider>
  );
  return () => reactRoot.unmount();
};

const ExtractBubble = (props: BubbleProps) => {

  const { component, onOpen, onConfirm, onCancel } = props;

  const [childComponent, setChildComponent] = React.useState<any>(null);

  const [isOpen, setIsOpen] = React.useState(true);

  const open = React.useCallback(() => {
    console.log("bubble component open", component, childComponent);
    setIsOpen(true);
    if (typeof onOpen !== 'undefined') {
      onOpen();
    }
  }, [onOpen]);

  const onClose = React.useCallback(() => {
    console.log("bubble component closed", component, childComponent);
    setIsOpen(false);
    if (typeof onCancel !== 'undefined') {
      onCancel();
    }
  }, [onCancel]);

  const onConfirmRequested = React.useCallback((text: string) => {
    setIsOpen(false);
    if (typeof onConfirm !== 'undefined') {
      onConfirm(text);
    }
  }, [onConfirm]);

  useEffect(() => {
    setChildComponent(component);
    console.log("bubble component mounted", component, childComponent);
  }, [component])

  return <>
    <FloatButton style={{ right: 24 }} icon={<BulbTwoTone />} tooltip="WellSky AI Assistant" onClick={open} type="primary" />
    {/* <CustomSideDrawer placement="right" handleOk={onClose} handleCancel={onClose} isOpen={isOpen} size="xl">
      {childComponent}
      </CustomSideDrawer> */}
    <Drawer destroyOnClose placement="right" onClose={onClose} open={isOpen} size={"large"} width={"1200px"}>
      {childComponent}
    </Drawer>
  </>
}

const ExtractDrawer = (props: InlineWidgetProps) => {

  const { component, onOpen, onConfirm, onCancel } = props;

  const [childComponent, setChildComponent] = React.useState<any>(null);

  const [isOpen, setIsOpen] = React.useState(true);

  const open = React.useCallback(() => {
    console.log("extract drawer component open", component, childComponent);
    setIsOpen(true);
    if (typeof onOpen !== 'undefined') {
      onOpen();
    }
  }, [onOpen]);

  const onClose = React.useCallback(() => {
    console.log("extract drawer component closed", component, childComponent);
    setIsOpen(false);
    if (typeof onCancel !== 'undefined') {
      onCancel();
    }
  }, [onCancel]);

  const onConfirmRequested = React.useCallback((text: string) => {
    setIsOpen(false);
    if (typeof onConfirm !== 'undefined') {
      onConfirm(text);
    }
  }, [onConfirm]);

  useEffect(() => {
    setChildComponent(component);
    console.log("extract inline component mounted", component, childComponent);
    setIsOpen(true);
    console.log("opened drawer");
  }, [component])

  // TODO: Use DLS drawer?
  return <>
  <Drawer destroyOnClose placement="right" onClose={onClose} open={isOpen} size={"large"} width={"1200px"} bodyStyle={{display: 'flex'}}>
      {childComponent}
    </Drawer>
  </>
}

window.initAnnotatedFormV3 = ({ el, schema, originalData, newData }: any) => {
  const reactRoot = ReactDOM.createRoot(el);
  reactRoot.render(
    <ChakraProvider>
      <AnnotatedForm schema={schema} originalData={originalData} newData={newData} />
    </ChakraProvider>
  );
  return () => reactRoot.unmount();
}

window.initSectionViewer = (props: SectionViewerArgs) => {
  const reactRoot = ReactDOM.createRoot(props.el);
  reactRoot.render(
    <ChakraProvider>
      <SectionsViewer schema={props.sectionsSchema} transactionId={props.transactionId} />
    </ChakraProvider>
  );
  return () => reactRoot.unmount();
}

window.initCustomFormAnnotatorV4 = ({ el, schema, originalData, newData, formTemplateId, formInstanceId }: any) => {
  const reactRoot = ReactDOM.createRoot(el);
  reactRoot.render(
    <ChakraProvider>
      <CustomFormAnnotatedForm schema={schema} originalData={originalData} newData={newData} formInstanceId={formInstanceId} formTemplateId={formTemplateId} />
    </ChakraProvider>
  );
  return () => reactRoot.unmount();
}

reportWebVitals();
