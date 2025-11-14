# if you run into module not found error. In shell do following:
# export PYTHONPATH=$PYTHONPATH:yourprojectpath/eai-ai/extract-and-fill/api
from extract_and_fill.domain.services import PromptChunkGenerator, JSONHealer



# transcript_text = "\n I need some help with my medical care. Alright, let's start with some basic information. How old are you? I'm 65 years old. Great. Do you have any medical diagnosis that have been documented? Yes, I do. Could you please tell me what they are? Sure, I have a few conditions like hypertension, diabetes, and arthritis. Okay, have you had any prior history of falls within the last 3 months? Yes, I have had a few falls in the past 3 monthsDo you have any visual impairment such as macular degeneration, diabetic retinopathies, visual field loss, age related changes, decline in visual acuity, accommodation, glare tolerance, depth perception, or night vision? Yes, I do have some visual impairment. I'm not wearing my prescribed glasses and my vision has been declining. Are you having any issues with incontinence such as frequency, urgency, or nocturia? Yes, I do have some issues with incontinence. Are you having any other impairments? Not that I can think of.\n Can you tell me about your current level of alertness, orientation, comprehension, concentration, and immediate memory for simple commands? Yes, I'm alert and oriented and I can focus and shift my attention. I can comprehend and recall task directions independently. Are you confused in new or complex situations? No, not usually. Are you anxious daily, but not constantly? Yes, that's correct. Do you demonstrate any cognitive, behavioral, or psychiatric symptoms at least once a week? No, I don't. How often do you demonstrate disruptive behavior symptoms? Less than once a month. Should I conduct a brief interview for mental status? Yes, that would be great. Please repeat the three words I'm about to say: sock, blue, and bed. Sock, blue, and bed. What year is it right now? It's 2023. What month are we in right now? We're in October. What day of the week is today? Today is Monday. Can you recall the three words I asked you to remember earlier? Yes, the three words were sock, blue, and bed. NO That's great to hear. Can you tell me if you have been feeling little interest or pleasure in doing things over the last 2 weeks? No, I haven't. How about feeling down, depressed, or hopeless? No, I haven't been feeling like that either. Do you feel lonely or isolated from those around you? Sometimes. Are you alert and oriented to person, place, and time? Yes, I am. Are you able to follow simple commands? Yes, I am able to follow simple commands. Do you have any problems or abnormal neurological findings such as headache? No, I don't have any such problems or abnormal neurological findings. \n Can you tell me if you have been feeling little interest or pleasure in doing things over the last 2 weeks? No, I haven't. How about feeling down, depressed, or hopeless? No, I haven't been feeling like that either. Do you feel lonely or isolated from those around you? Sometimes. Are you alert and oriented to person, place, and time? Yes, I am. an you tell me about your current level of alertness, orientation, comprehension, concentration, and immediate memory for simple commands? Yes, I am alert and oriented, able to focus and shift attention, and I understand and recall task directions independently. Are you eating well? I am sometimes do not have appetite to eat Do you feel like hurting yourselves? No \n Can you tell me about your current level of alertness, orientation, comprehension, concentration, and immediate memory for simple commands? Yes, I am alert and oriented, able to focus and shift attention, and I understand and recall task directions independently. Are you ever confused in new or complex situations? Yes, I can get confused in new or complex situations. How often do you get anxious? I get anxious daily, but not constantly. Are there any cognitive, behavioral, or psychiatric symptoms that you demonstrate at least once a week? No, I don't demonstrate any of those behaviors. How often do you have disruptive behavior symptoms? I have disruptive behavior symptoms less than once a month"
# json_template = {
#   "Cognitive, Mood, and Behavior": {
#     "Mental Status": {
#       "Oriented": {
#         "_meta": {
#           "Person": {
#             "answers": [
#               "Oriented",
#               "Disoriented"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "COMBO_BOX",
#                 "columns": "0"
#               }
#             }
#           },
#           "Time": {
#             "answers": [
#               "Oriented",
#               "Disoriented"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "COMBO_BOX",
#                 "columns": "0"
#               }
#             }
#           },
#           "Place": {
#             "answers": [
#               "Oriented",
#               "Disoriented"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "COMBO_BOX",
#                 "columns": "0"
#               }
#             }
#           },
#           "Situation": {
#             "answers": [
#               "Oriented",
#               "Disroiented"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "COMBO_BOX",
#                 "columns": "0"
#               }
#             }
#           }
#         },
#         "Person": None,
#         "Time": None,
#         "Place": None,
#         "Situation": None
#       },
#       "Memory": {
#         "_meta": {
#           "No problems": {
#             "answers": [
#               "No problems"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "CHECK_BOX",
#                 "columns": "0"
#               }
#             }
#           },
#           "Forgetful": {
#             "answers": [
#               "Forgetful"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "CHECK_BOX",
#                 "columns": "0"
#               }
#             }
#           },
#           "Misplaces objects": {
#             "answers": [
#               "Misplaces objects"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "CHECK_BOX",
#                 "columns": "0"
#               }
#             }
#           },
#           "Short-term loss": {
#             "answers": [
#               "Short-term loss"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "CHECK_BOX",
#                 "columns": "0"
#               }
#             }
#           },
#           "Long-term loss": {
#             "answers": [
#               "Long-term loss"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "CHECK_BOX",
#                 "columns": "0"
#               }
#             }
#           }
#         },
#         "No problems": None,
#         "Forgetful": None,
#         "Misplaces objects": None,
#         "Short-term loss": None,
#         "Long-term loss": None
#       },
#       "Neurological": {
#         "_meta": {
#           "No problems": {
#             "answers": [
#               "No problems"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "CHECK_BOX",
#                 "columns": "0"
#               }
#             }
#           },
#           "Seizures": {
#             "answers": [
#               "Seizures"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "CHECK_BOX",
#                 "columns": "0"
#               }
#             }
#           },
#           "Aphasic": {
#             "answers": [
#               "Aphasic"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "CHECK_BOX",
#                 "columns": "0"
#               }
#             }
#           },
#           "Headaches": {
#             "answers": [
#               "Headaches"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "CHECK_BOX",
#                 "columns": "0"
#               }
#             }
#           },
#           "Spasms": {
#             "answers": [
#               "Spasms"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "CHECK_BOX",
#                 "columns": "0"
#               }
#             }
#           },
#           "Tremors": {
#             "answers": [
#               "Tremors"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "CHECK_BOX",
#                 "columns": "0"
#               }
#             }
#           }
#         },
#         "No problems": None,
#         "Seizures": None,
#         "Aphasic": None,
#         "Headaches": None,
#         "Spasms": None,
#         "Tremors": None
#       },
#       "Mood": {
#         "_meta": {
#           "Appropriate (WNL)": {
#             "answers": [
#               "Appropriate (WNL)"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "CHECK_BOX",
#                 "columns": "0"
#               }
#             }
#           },
#           "Apathetic": {
#             "answers": [
#               "Apathetic"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "CHECK_BOX",
#                 "columns": "0"
#               }
#             }
#           },
#           "Depressed": {
#             "answers": [
#               "Depressed"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "CHECK_BOX",
#                 "columns": "0"
#               }
#             }
#           },
#           "Agitated": {
#             "answers": [
#               "Agitated"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "CHECK_BOX",
#                 "columns": "0"
#               }
#             }
#           },
#           "Irritable": {
#             "answers": [
#               "Irritable"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "CHECK_BOX",
#                 "columns": "0"
#               }
#             }
#           },
#           "Anxious": {
#             "answers": [
#               "Anxious"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "CHECK_BOX",
#                 "columns": "0"
#               }
#             }
#           },
#           "Elated": {
#             "answers": [
#               "Elated"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "CHECK_BOX",
#                 "columns": "0"
#               }
#             }
#           },
#           "Hostile": {
#             "answers": [
#               "Hostile"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "CHECK_BOX",
#                 "columns": "0"
#               }
#             }
#           }
#         },
#         "Appropriate (WNL)": None,
#         "Apathetic": None,
#         "Depressed": None,
#         "Agitated": None,
#         "Irritable": None,
#         "Anxious": None,
#         "Elated": None,
#         "Hostile": None
#       },
#       "Behavioral": {
#         "_meta": {
#           "Appropriate (WNL)": {
#             "answers": [
#               "Appropriate (WNL)"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "CHECK_BOX",
#                 "columns": "0"
#               }
#             }
#           },
#           "Inappropriate": {
#             "answers": [
#               "Inappropriate"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "CHECK_BOX",
#                 "columns": "0"
#               }
#             }
#           },
#           "Indifferent": {
#             "answers": [
#               "Indifferent"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "CHECK_BOX",
#                 "columns": "0"
#               }
#             }
#           },
#           "Assaultive": {
#             "answers": [
#               "Assaultive"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "CHECK_BOX",
#                 "columns": "0"
#               }
#             }
#           },
#           "Impaired judgement": {
#             "answers": [
#               "Impaired judgement"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "CHECK_BOX",
#                 "columns": "0"
#               }
#             }
#           },
#           "Impulsive": {
#             "answers": [
#               "Impulsive"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "CHECK_BOX",
#                 "columns": "0"
#               }
#             }
#           },
#           "Poor coping skills": {
#             "answers": [
#               "Poor coping skills"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "CHECK_BOX",
#                 "columns": "0"
#               }
#             }
#           },
#           "Compulsive": {
#             "answers": [
#               "Compulsive"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "CHECK_BOX",
#                 "columns": "0"
#               }
#             }
#           },
#           "Evasive": {
#             "answers": [
#               "Evasive"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "CHECK_BOX",
#                 "columns": "0"
#               }
#             }
#           },
#           "Poor decision making": {
#             "answers": [
#               "Poor decision making"
#             ],
#             "displayControl": {
#               "answerLayout": {
#                 "type": "CHECK_BOX",
#                 "columns": "0"
#               }
#             }
#           }
#         },
#         "Appropriate (WNL)": None,
#         "Inappropriate": None,
#         "Indifferent": None,
#         "Assaultive": None,
#         "Impaired judgement": None,
#         "Impulsive": None,
#         "Poor coping skills": None,
#         "Compulsive": None,
#         "Evasive": None,
#         "Poor decision making": None
#       }
#     },
#     "_meta": {
#       "Should Brief Interview for Mental Status (C0200-C0500) be Conducted?": {
#         "answers": [
#           "No (resident is rarely/never understood)",
#           "Yes"
#         ],
#         "displayControl": {
#           "answerLayout": {
#             "type": "COMBO_BOX",
#             "columns": "0"
#           }
#         }
#       },
#       "Cognitive Functioning": {
#         "answers": [
#           "Alert/oriented, able to focus and shift attention, comprehends and recalls task directions independently.",
#           "Requires prompting (cueing, repetition, reminders) only under stressful or unfamiliar conditions.",
#           "Requires assistance and some direction in specific situations (for example, all tasks involving shifting of attention) or consistently requires low stimulus environment due to distractibility.",
#           "Requires considerable assistance in routine situations. Is not alert and oriented or is unable to shift attention and recall directions more than half the time.",
#           "Totally dependent due to disturbances such as constant disorientation, coma, persistent vegetative state, or delirium."
#         ],
#         "displayControl": {
#           "answerLayout": {
#             "type": "COMBO_BOX",
#             "columns": "0"
#           }
#         }
#       },
#       "When Confused": {
#         "answers": [
#           "Never",
#           "In new or complex situations only",
#           "On awakening or at night only",
#           "During the day and evening, but not constantly",
#           "Constantly",
#           "Patient nonresponsive"
#         ],
#         "displayControl": {
#           "answerLayout": {
#             "type": "COMBO_BOX",
#             "columns": "0"
#           }
#         }
#       },
#       "When Anxious": {
#         "answers": [
#           "None of the time",
#           "Less often than daily",
#           "Daily, but not constantly",
#           "All of the time",
#           "Patient nonresponsive"
#         ],
#         "displayControl": {
#           "answerLayout": {
#             "type": "COMBO_BOX",
#             "columns": "0"
#           }
#         }
#       }
#     },
#     "Should Brief Interview for Mental Status (C0200-C0500) be Conducted?": None,
#     "Brief Interview for Mental Status": {
#       "_meta": {
#         "Repetition of Three Words": {
#           "answers": [
#             "None",
#             "One",
#             "Two",
#             "Three",
#             "No Information / Not Assessed"
#           ],
#           "displayControl": {
#             "answerLayout": {
#               "type": "COMBO_BOX",
#               "columns": "0"
#             }
#           }
#         }
#       },
#       "Repetition of Three Words": None
#     },
#     "Temporal Orientation (Orientation to year, month, and day)": {
#       "_meta": {
#         "Able to report correct year": {
#           "answers": [
#             "Missed by > 5 years or no answer",
#             "Missed by 2-5 years",
#             "Missed by 1 year",
#             "Correct",
#             "Not Assessed / No Information"
#           ],
#           "displayControl": {
#             "answerLayout": {
#               "type": "COMBO_BOX",
#               "columns": "0"
#             }
#           }
#         },
#         "Able to report correct month": {
#           "answers": [
#             "Missed by > 1 month or no answer",
#             "Missed by 6 days to 1 month",
#             "Accurate within 5 days",
#             "Not Assessed / No Information"
#           ],
#           "displayControl": {
#             "answerLayout": {
#               "type": "COMBO_BOX",
#               "columns": "0"
#             }
#           }
#         },
#         "Able to report correct day of the week": {
#           "answers": [
#             "Incorrect or no answer",
#             "Correct",
#             "Not Assessed / No Information"
#           ],
#           "displayControl": {
#             "answerLayout": {
#               "type": "COMBO_BOX",
#               "columns": "0"
#             }
#           }
#         }
#       },
#       "Able to report correct year": None,
#       "Able to report correct month": None,
#       "Able to report correct day of the week": None
#     },
#     "Recall": {
#       "_meta": {
#         "Able to recall \"sock\"": {
#           "answers": [
#             "No - could not recall",
#             "Yes, after cueing (\"something to wear\")",
#             "Yes, no cue required",
#             "Not Assessed / No Information"
#           ],
#           "displayControl": {
#             "answerLayout": {
#               "type": "COMBO_BOX",
#               "columns": "0"
#             }
#           }
#         },
#         "Able to recall \"blue\"": {
#           "answers": [
#             "No - could not recall",
#             "Yes, after cueing (\"a color\")",
#             "Yes, no cue required",
#             "Not Assessed / No Information"
#           ],
#           "displayControl": {
#             "answerLayout": {
#               "type": "COMBO_BOX",
#               "columns": "0"
#             }
#           }
#         },
#         "Able to recall \"bed\"": {
#           "answers": [
#             "No - could not recall",
#             "Yes, after cueing (\"a piece of furniture\")",
#             "Yes, no cue required",
#             "Not Assessed / No Information"
#           ],
#           "displayControl": {
#             "answerLayout": {
#               "type": "COMBO_BOX",
#               "columns": "0"
#             }
#           }
#         }
#       },
#       "Able to recall \"sock\"": None,
#       "Able to recall \"blue\"": None,
#       "Able to recall \"bed\"": None
#     },
#     "BIMS Summary Score": 0,
#     "Signs and Symptoms of Delirium (from CAM)": {
#       "_meta": {
#         "Acute Onset Mental Status Change. Is there evidence of an acute change in mental status from the patient's baseline?": {
#           "answers": [
#             "No",
#             "Yes",
#             "Not Assessed / No Information"
#           ],
#           "displayControl": {
#             "answerLayout": {
#               "type": "COMBO_BOX",
#               "columns": "0"
#             }
#           }
#         },
#         "Inattention - Did the patient have difficulty focusing attention, for example, being easily distractible or having difficulty keeping track of what was being said?": {
#           "answers": [
#             "Behavior not present",
#             "Behavior continuously present, does not fluctuate",
#             "Behavior present, fluctuates (comes and goes, changes in severity)",
#             "Not Assessed / No Information"
#           ],
#           "displayControl": {
#             "answerLayout": {
#               "type": "COMBO_BOX",
#               "columns": "0"
#             }
#           }
#         },
#         "Disorganized thinking - Was the patient's thinking disorganized or incoherent (rambling or irrelevant conversation, unclear or illogical flow of ideas, or unpredictable switching from subject to subject)?": {
#           "answers": [
#             "Behavior not present",
#             "Behavior continuously present, does not fluctuate",
#             "Behavior present, fluctuates (comes and goes, changes in severity)"
#           ],
#           "displayControl": {
#             "answerLayout": {
#               "type": "COMBO_BOX",
#               "columns": "0"
#             }
#           }
#         },
#         "Altered level of consciousness - Did the patient have altered level of consciousness, as indicated by any of the following criteria?": {
#           "answers": [
#             "Behavior not present",
#             "Behavior continuously present, does not fluctuate",
#             "Behavior present, fluctuates (comes and goes, changes in severity)"
#           ],
#           "displayControl": {
#             "answerLayout": {
#               "type": "COMBO_BOX",
#               "columns": "0"
#             }
#           }
#         }
#       },
#       "Acute Onset Mental Status Change. Is there evidence of an acute change in mental status from the patient's baseline?": None,
#       "Inattention - Did the patient have difficulty focusing attention, for example, being easily distractible or having difficulty keeping track of what was being said?": None,
#       "Disorganized thinking - Was the patient's thinking disorganized or incoherent (rambling or irrelevant conversation, unclear or illogical flow of ideas, or unpredictable switching from subject to subject)?": None,
#       "Altered level of consciousness - Did the patient have altered level of consciousness, as indicated by any of the following criteria?": None
#     },
#     "Cognitive Functioning": None,
#     "When Confused": None,
#     "When Anxious": None,
#     "Mood": {
#       "Patient Mood Interview (PHQ-2 to 9)": {
#         "Symptom Presence": {
#           "_meta": {
#             "Little interest or pleasure in doing things": {
#               "answers": [
#                 "No",
#                 "Yes",
#                 "No response"
#               ],
#               "displayControl": {
#                 "answerLayout": {
#                   "type": "COMBO_BOX",
#                   "columns": "0"
#                 }
#               }
#             },
#             "Feeling down, depressed or hopeless": {
#               "answers": [
#                 "No",
#                 "Yes",
#                 "No response"
#               ],
#               "displayControl": {
#                 "answerLayout": {
#                   "type": "COMBO_BOX",
#                   "columns": "0"
#                 }
#               }
#             },
#             "Trouble falling or staying asleep, or sleeping too much": {
#               "answers": [
#                 "No",
#                 "Yes",
#                 "No response"
#               ],
#               "displayControl": {
#                 "answerLayout": {
#                   "type": "COMBO_BOX",
#                   "columns": "0"
#                 }
#               }
#             },
#             "Feeling tired or having little energy": {
#               "answers": [
#                 "No",
#                 "Yes",
#                 "No response"
#               ],
#               "displayControl": {
#                 "answerLayout": {
#                   "type": "COMBO_BOX",
#                   "columns": "0"
#                 }
#               }
#             },
#             "Poor appetite or overeating": {
#               "answers": [
#                 "No",
#                 "Yes",
#                 "No response"
#               ],
#               "displayControl": {
#                 "answerLayout": {
#                   "type": "COMBO_BOX",
#                   "columns": "0"
#                 }
#               }
#             },
#             "Feeling bad about yourself - or that you are a failure or have let yourself or your family down": {
#               "answers": [
#                 "No",
#                 "Yes",
#                 "No response"
#               ],
#               "displayControl": {
#                 "answerLayout": {
#                   "type": "COMBO_BOX",
#                   "columns": "0"
#                 }
#               }
#             },
#             "Trouble concentrating on things, such as reading the newspaper or watching television": {
#               "answers": [
#                 "No",
#                 "Yes",
#                 "No response"
#               ],
#               "displayControl": {
#                 "answerLayout": {
#                   "type": "COMBO_BOX",
#                   "columns": "0"
#                 }
#               }
#             },
#             "Moving or speaking so slowly that other people could have noticed. Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual": {
#               "answers": [
#                 "No",
#                 "Yes",
#                 "No response"
#               ],
#               "displayControl": {
#                 "answerLayout": {
#                   "type": "COMBO_BOX",
#                   "columns": "0"
#                 }
#               }
#             },
#             "Thoughts that you would be better off dead, or of hurting yourself in some way": {
#               "answers": [
#                 "No",
#                 "Yes",
#                 "No response"
#               ],
#               "displayControl": {
#                 "answerLayout": {
#                   "type": "COMBO_BOX",
#                   "columns": "0"
#                 }
#               }
#             }
#           },
#           "Little interest or pleasure in doing things": None,
#           "Feeling down, depressed or hopeless": None,
#           "Trouble falling or staying asleep, or sleeping too much": None,
#           "Feeling tired or having little energy": None,
#           "Poor appetite or overeating": None,
#           "Feeling bad about yourself - or that you are a failure or have let yourself or your family down": None,
#           "Trouble concentrating on things, such as reading the newspaper or watching television": None,
#           "Moving or speaking so slowly that other people could have noticed. Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual": None,
#           "Thoughts that you would be better off dead, or of hurting yourself in some way": None
#         },
#         "Symptom Frequency": {
#           "_meta": {
#             "Little interest or pleasure in doing things": {
#               "answers": [
#                 "Never or 1 day",
#                 "2-6 days (several days)",
#                 "7-11 days (half or more of the days)",
#                 "12-14 days (nearly every day)"
#               ],
#               "displayControl": {
#                 "answerLayout": {
#                   "type": "COMBO_BOX",
#                   "columns": "0"
#                 }
#               }
#             },
#             "Feeling down, depressed or hopeless": {
#               "answers": [
#                 "Never or 1 day",
#                 "2-6 days (several days)",
#                 "7-11 days (half or more of the days)",
#                 "12-14 days (nearly every day)"
#               ],
#               "displayControl": {
#                 "answerLayout": {
#                   "type": "COMBO_BOX",
#                   "columns": "0"
#                 }
#               }
#             },
#             "Trouble falling or staying asleep, or sleeping too much": {
#               "answers": [
#                 "Never or 1 day",
#                 "2-6 days (several days)",
#                 "7-11 days (half or more of the days)",
#                 "12-14 days (nearly every day)"
#               ],
#               "displayControl": {
#                 "answerLayout": {
#                   "type": "COMBO_BOX",
#                   "columns": "0"
#                 }
#               }
#             },
#             "Feeling tired or having little energy": {
#               "answers": [
#                 "Never or 1 day",
#                 "2-6 days (several days)",
#                 "7-11 days (half or more of the days)",
#                 "12-14 days (nearly every day)"
#               ],
#               "displayControl": {
#                 "answerLayout": {
#                   "type": "COMBO_BOX",
#                   "columns": "0"
#                 }
#               }
#             },
#             "Poor appetite or overeating": {
#               "answers": [
#                 "Never or 1 day",
#                 "2-6 days (several days)",
#                 "7-11 days (half or more of the days)",
#                 "12-14 days (nearly every day)"
#               ],
#               "displayControl": {
#                 "answerLayout": {
#                   "type": "COMBO_BOX",
#                   "columns": "0"
#                 }
#               }
#             },
#             "Feeling bad about yourself - or that you are a failure or have let yourself or your family down": {
#               "answers": [
#                 "Never or 1 day",
#                 "2-6 days (several days)",
#                 "7-11 days (half or more of the days)",
#                 "12-14 days (nearly every day)"
#               ],
#               "displayControl": {
#                 "answerLayout": {
#                   "type": "COMBO_BOX",
#                   "columns": "0"
#                 }
#               }
#             },
#             "Trouble concentrating on things, such as reading the newspaper or watching television": {
#               "answers": [
#                 "Never or 1 day",
#                 "2-6 days (several days)",
#                 "7-11 days (half or more of the days)",
#                 "12-14 days (nearly every day)"
#               ],
#               "displayControl": {
#                 "answerLayout": {
#                   "type": "COMBO_BOX",
#                   "columns": "0"
#                 }
#               }
#             },
#             "Moving or speaking so slowly that other people could have noticed. Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual": {
#               "answers": [
#                 "Never or 1 day",
#                 "2-6 days (several days)",
#                 "7-11 days (half or more of the days)",
#                 "12-14 days (nearly every day)"
#               ],
#               "displayControl": {
#                 "answerLayout": {
#                   "type": "COMBO_BOX",
#                   "columns": "0"
#                 }
#               }
#             },
#             "Thoughts that you would be better off dead, or of hurting yourself in some way": {
#               "answers": [
#                 "Never or 1 day",
#                 "2-6 days (several days)",
#                 "7-11 days (half or more of the days)",
#                 "12-14 days (nearly every day)"
#               ],
#               "displayControl": {
#                 "answerLayout": {
#                   "type": "COMBO_BOX",
#                   "columns": "0"
#                 }
#               }
#             }
#           },
#           "Little interest or pleasure in doing things": None,
#           "Feeling down, depressed or hopeless": None,
#           "Trouble falling or staying asleep, or sleeping too much": None,
#           "Feeling tired or having little energy": None,
#           "Poor appetite or overeating": None,
#           "Feeling bad about yourself - or that you are a failure or have let yourself or your family down": None,
#           "Trouble concentrating on things, such as reading the newspaper or watching television": None,
#           "Moving or speaking so slowly that other people could have noticed. Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual": None,
#           "Thoughts that you would be better off dead, or of hurting yourself in some way": None
#         }
#       },
#       "Total Severity Score": 0,
#       "_meta": {
#         "Social Isolation. How often do you feel lonely or isolated from those around you?": {
#           "answers": [
#             "Never",
#             "Rarely",
#             "Sometimes",
#             "Often",
#             "Always",
#             "Patient unable to respond"
#           ],
#           "displayControl": {
#             "answerLayout": {
#               "type": "COMBO_BOX",
#               "columns": "0"
#             }
#           }
#         }
#       },
#       "Social Isolation. How often do you feel lonely or isolated from those around you?": None
#     },
#     "Behavior": {
#       "_meta": {
#         "Cognitive, Behavorial, and Psychiatric Symptoms that are demonstrated at least once a week (reported or observed)": {
#           "answers": [
#             "Memory deficit: failure to recognize familiar persons/places, inability to recall events of past 24 hours, significant memory loss so that supervision is required",
#             "Impaired decision-making: failure to perform usual ADLs or IADLs, inability to appropriately stop activities, jeopardizes safety through actions",
#             "Verbal disruption: yelling, threatening, excessive profanity, sexual references, etc.",
#             "Physical aggression: aggressive or combative to self and others (for example, hits self, throws objects, punches, dangerous maneuvers with wheelchair or other objects)",
#             "Disruptive, infantile, or socially inappropriate behavior (excludes verbal actions)",
#             "Delusional, hallucinatory, or paranoid behavior",
#             "None of the above behaviors demonstrated"
#           ],
#           "displayControl": {
#             "answerLayout": {
#               "type": "COMBO_BOX",
#               "columns": "0"
#             }
#           }
#         },
#         "Frequency of Disruptive Behavior Symptoms (reported or observed): Any physical, verbal, or other disruptive/dangerous symptoms that are injurious to self or others or jeopardize personal safety.": {
#           "answers": [
#             "Never",
#             "Less than once a month",
#             "Once a month",
#             "Several times each month",
#             "Several times a week",
#             "At least daily"
#           ],
#           "displayControl": {
#             "answerLayout": {
#               "type": "COMBO_BOX",
#               "columns": "0"
#             }
#           }
#         }
#       },
#       "Cognitive, Behavorial, and Psychiatric Symptoms that are demonstrated at least once a week (reported or observed)": None,
#       "Frequency of Disruptive Behavior Symptoms (reported or observed): Any physical, verbal, or other disruptive/dangerous symptoms that are injurious to self or others or jeopardize personal safety.": None
#     }
#   }
# }
# model = "medlm-medium"
# transcript_version=10
# print(len(transcript_text))
# # for chunk in PromptChunkGenerator().make_chunks("", transcript_text, json_template, model,transcript_version,1024):
# #         #print(chunk.chunk_schema)
# #         #import pdb;pdb.set_trace()
# #         # if "Place" in json.dumps(chunk.chunk_schema):
# #         #     import pdb;pdb.set_trace()
# #         pass


def testing_strategy_based_prompting():
    sample_section_schema = {
      "questionCode": "99138-0",
      "localQuestionCode": "B",
      "dataType": "SECTION",
      "header": True,
      "units": None,
      "codingInstructions": None,
      "copyrightNotice": None,
      "question": "Hearing, Speech, and Vision",
      "answers": None,
      "skipLogic": None,
      "restrictions": None,
      "defaultAnswer": None,
      "formatting": None,
      "calculationMethod": None,
      "items": [
        {
          "questionCode": "93157-6",
          "localQuestionCode": "B1300",
          "dataType": "CNE",
          "header": False,
          "units": None,
          "codingInstructions": None,
          "copyrightNotice": "© 2006 Morris et al. Used with permission",
          "question":
            "Sensory Status",
          "answers": None,
          "skipLogic": None,
          "restrictions": None,
          "defaultAnswer": None,
          "formatting": None,
          "calculationMethod": None,
          "items": [
            {
              "questionCode": "93157-6",
              "localQuestionCode": "B1300",
              "dataType": "CNE",
              "header": False,
              "units": None,
              "codingInstructions": None,
              "copyrightNotice": "© 2006 Morris et al. Used with permission",
              "question":
                "Eyes",
              "answers": None,
              "skipLogic": None,
              "restrictions": None,
              "defaultAnswer": None,
              "formatting": None,
              "calculationMethod": None,
              "items": [
                {
                  "questionCode": "93157-6",
                  "localQuestionCode": "",
                  "dataType": "CNE",
                  "header": False,
                  "units": None,
                  "codingInstructions": None,
                  "copyrightNotice": "© 2006 Morris et al. Used with permission",
                  "question": "WNL",
                  "hostFieldId":"cSS_wnl",
                  "answers": [{
                    "label": "1",
                    "code": "LA2-8",
                    "text": "WNL (Within Normal Limits)",
                    "other": None,
                    "system": "http://loinc.org"
                  }],
                  "skipLogic": None,
                  "restrictions": None,
                  "defaultAnswer": None,
                  "formatting": None,
                  "calculationMethod": None,
                  "items": None,
                  "linkId": "/99138-0/93157-6",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "93157-6",
                      "display":
                        "Eyes",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "93157-6",
                  "localQuestionCode": "",
                  "dataType": "CNE",
                  "header": False,
                  "units": None,
                  "codingInstructions": None,
                  "copyrightNotice": "© 2006 Morris et al. Used with permission",
                  "question": "Glasses",
                  "hostFieldId":"cSS_glasses",
                  "answers": [{
                    "label": "1",
                    "code": "LA2-8",
                    "text": "Glasses",
                    "other": None,
                    "system": "http://loinc.org"
                  }],
                  "skipLogic": None,
                  "restrictions": None,
                  "defaultAnswer": None,
                  "formatting": None,
                  "calculationMethod": None,
                  "items": None,
                  "linkId": "/99138-0/93157-6",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "93157-6",
                      "display":
                        "Eyes",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "93157-6",
                  "localQuestionCode": "",
                  "dataType": "CNE",
                  "header": False,
                  "units": None,
                  "codingInstructions": None,
                  "copyrightNotice": "© 2006 Morris et al. Used with permission",
                  "question": "Contacts Left",
                  "hostFieldId":"cSS_contactsl",
                  "answers": [{
                    "label": "1",
                    "code": "LA2-8",
                    "text": "Contacts Left",
                    "other": None,
                    "system": "http://loinc.org"
                  }],
                  "skipLogic": None,
                  "restrictions": None,
                  "defaultAnswer": None,
                  "formatting": None,
                  "calculationMethod": None,
                  "items": None,
                  "linkId": "/99138-0/93157-6",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "93157-6",
                      "display":
                        "Eyes",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "93157-6",
                  "localQuestionCode": "",
                  "dataType": "CNE",
                  "header": False,
                  "units": None,
                  "codingInstructions": None,
                  "copyrightNotice": "© 2006 Morris et al. Used with permission",
                  "question": "Contacts Right",
                  "hostFieldId":"cSS_contactsr",
                  "answers": [{
                    "label": "1",
                    "code": "LA2-8",
                    "text": "Contacts Right",
                    "other": None,
                    "system": "http://loinc.org"
                  }],
                  "skipLogic": None,
                  "restrictions": None,
                  "defaultAnswer": None,
                  "formatting": None,
                  "calculationMethod": None,
                  "items": None,
                  "linkId": "/99138-0/93157-6",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "93157-6",
                      "display":
                        "Eyes",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "93157-6",
                  "localQuestionCode": "",
                  "dataType": "CNE",
                  "header": False,
                  "units": None,
                  "codingInstructions": None,
                  "copyrightNotice": "© 2006 Morris et al. Used with permission",
                  "question": "Blurred Vision",
                  "hostFieldId":"cSS_blurred",
                  "answers": [{
                    "label": "1",
                    "code": "LA2-8",
                    "text": "Blurred Vision",
                    "other": None,
                    "system": "http://loinc.org"
                  }],
                  "skipLogic": None,
                  "restrictions": None,
                  "defaultAnswer": None,
                  "formatting": None,
                  "calculationMethod": None,
                  "items": None,
                  "linkId": "/99138-0/93157-6",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "93157-6",
                      "display":
                        "Eyes",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "93157-6",
                  "localQuestionCode": "",
                  "dataType": "CNE",
                  "header": False,
                  "units": None,
                  "codingInstructions": None,
                  "copyrightNotice": "© 2006 Morris et al. Used with permission",
                  "question": "Glaucoma",
                  "hostFieldId":"cSS_glaucoma",
                  "answers": [{
                    "label": "1",
                    "code": "LA2-8",
                    "text": "Glaucoma",
                    "other": None,
                    "system": "http://loinc.org"
                  }],
                  "skipLogic": None,
                  "restrictions": None,
                  "defaultAnswer": None,
                  "formatting": None,
                  "calculationMethod": None,
                  "items": None,
                  "linkId": "/99138-0/93157-6",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "93157-6",
                      "display":
                        "Eyes",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "93157-6",
                  "localQuestionCode": "",
                  "dataType": "CNE",
                  "header": False,
                  "units": None,
                  "codingInstructions": None,
                  "copyrightNotice": "© 2006 Morris et al. Used with permission",
                  "question": "Cataracts",
                  "hostFieldId":"cSS_glaucoma",
                  "answers": [{
                    "label": "1",
                    "code": "LA2-8",
                    "text": "Cataracts",
                    "other": None,
                    "system": "http://loinc.org"
                  }],
                  "skipLogic": None,
                  "restrictions": None,
                  "defaultAnswer": None,
                  "formatting": None,
                  "calculationMethod": None,
                  "items": None,
                  "linkId": "/99138-0/93157-6",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "93157-6",
                      "display":
                        "Eyes",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "93157-6",
                  "localQuestionCode": "",
                  "dataType": "CNE",
                  "header": False,
                  "units": None,
                  "codingInstructions": None,
                  "copyrightNotice": "© 2006 Morris et al. Used with permission",
                  "question": "Macular Degeneration",
                  "hostFieldId": "cSS_macular",
                  "answers": [{
                    "label": "1",
                    "code": "LA2-8",
                    "text": "Macular Degeneration",
                    "other": None,
                    "system": "http://loinc.org"
                  }],
                  "skipLogic": None,
                  "restrictions": None,
                  "defaultAnswer": None,
                  "formatting": None,
                  "calculationMethod": None,
                  "items": None,
                  "linkId": "/99138-0/93157-6",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "93157-6",
                      "display":
                        "Eyes",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "93157-6",
                  "localQuestionCode": "",
                  "dataType": "CNE",
                  "header": False,
                  "units": None,
                  "codingInstructions": None,
                  "copyrightNotice": "© 2006 Morris et al. Used with permission",
                  "question": "Redness",
                  "hostFieldId": "cSS_redness",
                  "answers": [{
                    "label": "1",
                    "code": "LA2-8",
                    "text": "Redness",
                    "other": None,
                    "system": "http://loinc.org"
                  }],
                  "skipLogic": None,
                  "restrictions": None,
                  "defaultAnswer": None,
                  "formatting": None,
                  "calculationMethod": None,
                  "items": None,
                  "linkId": "/99138-0/93157-6",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "93157-6",
                      "display":
                        "Eyes",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "93157-6",
                  "localQuestionCode": "",
                  "dataType": "CNE",
                  "header": False,
                  "units": None,
                  "codingInstructions": None,
                  "copyrightNotice": "© 2006 Morris et al. Used with permission",
                  "question": "Drainage",
                  "answers": [{
                    "label": "1",
                    "code": "LA2-8",
                    "text": "Drainage",
                    "other": None,
                    "system": "http://loinc.org"
                  }],
                  "skipLogic": None,
                  "restrictions": None,
                  "defaultAnswer": None,
                  "formatting": None,
                  "calculationMethod": None,
                  "items": None,
                  "linkId": "/99138-0/93157-6",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "93157-6",
                      "display":
                        "Eyes",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "93157-6",
                  "localQuestionCode": "",
                  "dataType": "CNE",
                  "header": False,
                  "units": None,
                  "codingInstructions": None,
                  "copyrightNotice": "© 2006 Morris et al. Used with permission",
                  "question": "Itching",
                  "answers": [{
                    "label": "1",
                    "code": "LA2-8",
                    "text": "Itching",
                    "other": None,
                    "system": "http://loinc.org"
                  }],
                  "skipLogic": None,
                  "restrictions": None,
                  "defaultAnswer": None,
                  "formatting": None,
                  "calculationMethod": None,
                  "items": None,
                  "linkId": "/99138-0/93157-6",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "93157-6",
                      "display":
                        "Eyes",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "93157-6",
                  "localQuestionCode": "",
                  "dataType": "CNE",
                  "header": False,
                  "units": None,
                  "codingInstructions": None,
                  "copyrightNotice": "© 2006 Morris et al. Used with permission",
                  "question": "Watering",
                  "answers": [{
                    "label": "1",
                    "code": "LA2-8",
                    "text": "Watering",
                    "other": None,
                    "system": "http://loinc.org"
                  }],
                  "skipLogic": None,
                  "restrictions": None,
                  "defaultAnswer": None,
                  "formatting": None,
                  "calculationMethod": None,
                  "items": None,
                  "linkId": "/99138-0/93157-6",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "93157-6",
                      "display":
                        "Eyes",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "93157-6",
                  "localQuestionCode": "",
                  "dataType": "CNE",
                  "header": False,
                  "units": None,
                  "codingInstructions": None,
                  "copyrightNotice": "© 2006 Morris et al. Used with permission",
                  "question": "Other",
                  "answers": [{
                    "label": "1",
                    "code": "LA2-8",
                    "text": "Other",
                    "other": None,
                    "system": "http://loinc.org"
                  }],
                  "skipLogic": None,
                  "restrictions": None,
                  "defaultAnswer": None,
                  "formatting": None,
                  "calculationMethod": None,
                  "items": None,
                  "linkId": "/99138-0/93157-6",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "93157-6",
                      "display":
                        "Eyes",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "93157-6",
                  "localQuestionCode": "",
                  "dataType": "CNE",
                  "header": False,
                  "units": None,
                  "codingInstructions": None,
                  "copyrightNotice": "© 2006 Morris et al. Used with permission",
                  "question": "Date of Last Eye",
                  "answers": None,
                  "skipLogic": None,
                  "restrictions": None,
                  "defaultAnswer": None,
                  "formatting": None,
                  "calculationMethod": None,
                  "items": None,
                  "linkId": "/99138-0/93157-6",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "93157-6",
                      "display":
                        "Eyes",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                }
              ],
              "linkId": "/99138-0/93157-6",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "93157-6",
                  "display":
                    "Health Literacy: How often do you need to have someone help you when you read instructions, pamphlets, or other written material from your doctor or pharmacy?",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "93157-6",
              "localQuestionCode": "B1300",
              "dataType": "CNE",
              "header": False,
              "units": None,
              "codingInstructions": None,
              "copyrightNotice": "© 2006 Morris et al. Used with permission",
              "question":
                "Ears",
              "answers": None,
              "skipLogic": None,
              "restrictions": None,
              "defaultAnswer": None,
              "formatting": None,
              "calculationMethod": None,
              "items": [
                {
                  "questionCode": "93157-6",
                  "localQuestionCode": "",
                  "dataType": "CNE",
                  "header": False,
                  "units": None,
                  "codingInstructions": None,
                  "copyrightNotice": "© 2006 Morris et al. Used with permission",
                  "question": "WNL",
                  "hostFieldId":"cSS_earswnl",
                  "answers": [{
                    "label": "1",
                    "code": "LA2-8",
                    "text": "WNL (Within Normal Limits)",
                    "other": None,
                    "system": "http://loinc.org"
                  }],
                  "skipLogic": None,
                  "restrictions": None,
                  "defaultAnswer": None,
                  "formatting": None,
                  "calculationMethod": None,
                  "items": None,
                  "linkId": "/99138-0/93157-6",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "93157-6",
                      "display":
                        "Eyes",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "93157-6",
                  "localQuestionCode": "",
                  "dataType": "CNE",
                  "header": False,
                  "units": None,
                  "codingInstructions": None,
                  "copyrightNotice": "© 2006 Morris et al. Used with permission",
                  "question": "Hearing Impaired",
                  "hostFieldId":"cSS_himpaired",
                  "answers": [{
                    "label": "1",
                    "code": "LA2-8",
                    "text": "Hearing Impaired",
                    "other": None,
                    "system": "http://loinc.org"
                  }],
                  "skipLogic": None,
                  "restrictions": None,
                  "defaultAnswer": None,
                  "formatting": None,
                  "calculationMethod": None,
                  "items": [
                    {
                      "questionCode": "93157-6",
                      "localQuestionCode": "",
                      "dataType": "CNE",
                      "header": False,
                      "units": None,
                      "codingInstructions": None,
                      "copyrightNotice": "© 2006 Morris et al. Used with permission",
                      "question": "Left",
                      "hostFieldId":"cSS_himpairedl",
                      "answers": [{
                        "label": "1",
                        "code": "LA2-8",
                        "text": "Left",
                        "other": None,
                        "system": "http://loinc.org"
                      }],
                      "skipLogic": None,
                      "restrictions": None,
                      "defaultAnswer": None,
                      "formatting": None,
                      "calculationMethod": None,
                      "items": None,
                      "linkId": "/99138-0/93157-6",
                      "questionCodeSystem": "http://loinc.org",
                      "codeList": [
                        {
                          "code": "93157-6",
                          "display":
                            "Eyes",
                          "system": "http://loinc.org"
                        }
                      ],
                      "displayControl": {
                        "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
                      },
                      "questionCardinality": { "min": "1", "max": "1" },
                      "answerCardinality": { "min": "0", "max": "1" }
                    },
                    {
                      "questionCode": "93157-6",
                      "localQuestionCode": "",
                      "dataType": "CNE",
                      "header": False,
                      "units": None,
                      "codingInstructions": None,
                      "copyrightNotice": "© 2006 Morris et al. Used with permission",
                      "question": "Right",
                      "hostFieldId":"cSS_himpairedr",
                      "answers": [{
                        "label": "1",
                        "code": "LA2-8",
                        "text": "Right",
                        "other": None,
                        "system": "http://loinc.org"
                      }],
                      "skipLogic": None,
                      "restrictions": None,
                      "defaultAnswer": None,
                      "formatting": None,
                      "calculationMethod": None,
                      "items": None,
                      "linkId": "/99138-0/93157-6",
                      "questionCodeSystem": "http://loinc.org",
                      "codeList": [
                        {
                          "code": "93157-6",
                          "display":
                            "Eyes",
                          "system": "http://loinc.org"
                        }
                      ],
                      "displayControl": {
                        "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
                      },
                      "questionCardinality": { "min": "1", "max": "1" },
                      "answerCardinality": { "min": "0", "max": "1" }
                    }
                  ],
                  "linkId": "/99138-0/93157-6",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "93157-6",
                      "display":
                        "Eyes",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "93157-6",
                  "localQuestionCode": "",
                  "dataType": "CNE",
                  "header": False,
                  "units": None,
                  "codingInstructions": None,
                  "copyrightNotice": "© 2006 Morris et al. Used with permission",
                  "question": "Deaf",
                  "hostFieldId":"cSS_deaf",
                  "answers": [{
                    "label": "1",
                    "code": "LA2-8",
                    "text": "Deaf",
                    "other": None,
                    "system": "http://loinc.org"
                  }],
                  "skipLogic": None,
                  "restrictions": None,
                  "defaultAnswer": None,
                  "formatting": None,
                  "calculationMethod": None,
                  "items": None,
                  "linkId": "/99138-0/93157-6",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "93157-6",
                      "display":
                        "Eyes",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "93157-6",
                  "localQuestionCode": "",
                  "dataType": "CNE",
                  "header": False,
                  "units": None,
                  "codingInstructions": None,
                  "copyrightNotice": "© 2006 Morris et al. Used with permission",
                  "question": "Drainage",
                  "hostFieldId":"cSS_eardrainage",
                  "answers": [{
                    "label": "1",
                    "code": "LA2-8",
                    "text": "Drainage",
                    "other": None,
                    "system": "http://loinc.org"
                  }],
                  "skipLogic": None,
                  "restrictions": None,
                  "defaultAnswer": None,
                  "formatting": None,
                  "calculationMethod": None,
                  "items": None,
                  "linkId": "/99138-0/93157-6",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "93157-6",
                      "display":
                        "Eyes",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "93157-6",
                  "localQuestionCode": "",
                  "dataType": "CNE",
                  "header": False,
                  "units": None,
                  "codingInstructions": None,
                  "copyrightNotice": "© 2006 Morris et al. Used with permission",
                  "question": "Pain",
                  "hostFieldId":"cSS_pain",
                  "answers": [{
                    "label": "1",
                    "code": "LA2-8",
                    "text": "Pain",
                    "other": None,
                    "system": "http://loinc.org"
                  }],
                  "skipLogic": None,
                  "restrictions": None,
                  "defaultAnswer": None,
                  "formatting": None,
                  "calculationMethod": None,
                  "items": None,
                  "linkId": "/99138-0/93157-6",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "93157-6",
                      "display":
                        "Eyes",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "93157-6",
                  "localQuestionCode": "",
                  "dataType": "CNE",
                  "header": False,
                  "units": None,
                  "codingInstructions": None,
                  "copyrightNotice": "© 2006 Morris et al. Used with permission",
                  "question": "Hearing Aids",
                  "hostFieldId": "cSS_haids",
                  "answers": [{
                    "label": "1",
                    "code": "LA2-8",
                    "text": "Hearing Aids",
                    "other": None,
                    "system": "http://loinc.org"
                  }],
                  "skipLogic": None,
                  "restrictions": None,
                  "defaultAnswer": None,
                  "formatting": None,
                  "calculationMethod": None,
                  "items": [
                    {
                      "questionCode": "93157-6",
                      "localQuestionCode": "",
                      "dataType": "CNE",
                      "header": False,
                      "units": None,
                      "codingInstructions": None,
                      "copyrightNotice": "© 2006 Morris et al. Used with permission",
                      "question": "Left",
                      "hostFieldId": "cSS_haidsl",
                      "answers": [{
                        "label": "1",
                        "code": "LA2-8",
                        "text": "Left",
                        "other": None,
                        "system": "http://loinc.org"
                      }],
                      "skipLogic": None,
                      "restrictions": None,
                      "defaultAnswer": None,
                      "formatting": None,
                      "calculationMethod": None,
                      "items": None,
                      "linkId": "/99138-0/93157-6",
                      "questionCodeSystem": "http://loinc.org",
                      "codeList": [
                        {
                          "code": "93157-6",
                          "display":
                            "Eyes",
                          "system": "http://loinc.org"
                        }
                      ],
                      "displayControl": {
                        "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
                      },
                      "questionCardinality": { "min": "1", "max": "1" },
                      "answerCardinality": { "min": "0", "max": "1" }
                    },
                    {
                      "questionCode": "93157-6",
                      "localQuestionCode": "",
                      "dataType": "CNE",
                      "header": False,
                      "units": None,
                      "codingInstructions": None,
                      "copyrightNotice": "© 2006 Morris et al. Used with permission",
                      "question": "Right",
                      "hostFieldId":"cSS_aidsr",
                      "answers": [{
                        "label": "1",
                        "code": "LA2-8",
                        "text": "Right",
                        "other": None,
                        "system": "http://loinc.org"
                      }],
                      "skipLogic": None,
                      "restrictions": None,
                      "defaultAnswer": None,
                      "formatting": None,
                      "calculationMethod": None,
                      "items": None,
                      "linkId": "/99138-0/93157-6",
                      "questionCodeSystem": "http://loinc.org",
                      "codeList": [
                        {
                          "code": "93157-6",
                          "display":
                            "Eyes",
                          "system": "http://loinc.org"
                        }
                      ],
                      "displayControl": {
                        "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
                      },
                      "questionCardinality": { "min": "1", "max": "1" },
                      "answerCardinality": { "min": "0", "max": "1" }
                    }
                  ],
                  "linkId": "/99138-0/93157-6",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "93157-6",
                      "display":
                        "Eyes",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                }
              ],
              "linkId": "/99138-0/93157-6",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "93157-6",
                  "display":
                    "Health Literacy: How often do you need to have someone help you when you read instructions, pamphlets, or other written material from your doctor or pharmacy?",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "93157-6",
              "localQuestionCode": "B1300",
              "dataType": "CNE",
              "header": False,
              "units": None,
              "codingInstructions": None,
              "copyrightNotice": "© 2006 Morris et al. Used with permission",
              "question":
                "Nose",
              "answers": None,
              "skipLogic": None,
              "restrictions": None,
              "defaultAnswer": None,
              "formatting": None,
              "calculationMethod": None,
              "items": [
                {
                  "questionCode": "93157-6",
                  "localQuestionCode": "",
                  "dataType": "CNE",
                  "header": False,
                  "units": None,
                  "codingInstructions": None,
                  "copyrightNotice": "© 2006 Morris et al. Used with permission",
                  "question": "WNL",
                  "hostFieldId":"cSS_nosewnl",
                  "answers": [{
                    "label": "1",
                    "code": "LA2-8",
                    "text": "WNL (Within Normal Limits)",
                    "other": None,
                    "system": "http://loinc.org"
                  }],
                  "skipLogic": None,
                  "restrictions": None,
                  "defaultAnswer": None,
                  "formatting": None,
                  "calculationMethod": None,
                  "items": None,
                  "linkId": "/99138-0/93157-6",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "93157-6",
                      "display":
                        "Eyes",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "93157-6",
                  "localQuestionCode": "",
                  "dataType": "CNE",
                  "header": False,
                  "units": None,
                  "codingInstructions": None,
                  "copyrightNotice": "© 2006 Morris et al. Used with permission",
                  "question": "Congestion",
                  "hostFieldId":"cSS_congestion",
                  "answers": [{
                    "label": "1",
                    "code": "LA2-8",
                    "text": "Congestion",
                    "other": None,
                    "system": "http://loinc.org"
                  }],
                  "skipLogic": None,
                  "restrictions": None,
                  "defaultAnswer": None,
                  "formatting": None,
                  "calculationMethod": None,
                  "items": None,
                  "linkId": "/99138-0/93157-6",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "93157-6",
                      "display":
                        "Eyes",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "93157-6",
                  "localQuestionCode": "",
                  "dataType": "CNE",
                  "header": False,
                  "units": None,
                  "codingInstructions": None,
                  "copyrightNotice": "© 2006 Morris et al. Used with permission",
                  "question": "Loss of Smell",
                  "hostFieldId": "cSS_smell",
                  "answers": [{
                    "label": "1",
                    "code": "LA2-8",
                    "text": "Loss of Smell",
                    "other": None,
                    "system": "http://loinc.org"
                  }],
                  "skipLogic": None,
                  "restrictions": None,
                  "defaultAnswer": None,
                  "formatting": None,
                  "calculationMethod": None,
                  "items": None,
                  "linkId": "/99138-0/93157-6",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "93157-6",
                      "display":
                        "Eyes",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "93157-6",
                  "localQuestionCode": "",
                  "dataType": "CNE",
                  "header": False,
                  "units": None,
                  "codingInstructions": None,
                  "copyrightNotice": "© 2006 Morris et al. Used with permission",
                  "question": "Nose Bleeds",
                  "hostFieldId": "cSS_bleeds",
                  "answers": [{
                    "label": "1",
                    "code": "LA2-8",
                    "text": "Nose Bleeds",
                    "other": None,
                    "system": "http://loinc.org"
                  }],
                  "skipLogic": None,
                  "restrictions": None,
                  "defaultAnswer": None,
                  "formatting": None,
                  "calculationMethod": None,
                  "items": None,
                  "linkId": "/99138-0/93157-6",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "93157-6",
                      "display":
                        "Eyes",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                },
                {
                  "questionCode": "93157-6",
                  "localQuestionCode": "",
                  "dataType": "CNE",
                  "header": False,
                  "units": None,
                  "codingInstructions": None,
                  "copyrightNotice": "© 2006 Morris et al. Used with permission",
                  "question": "Other",
                  "answers": [{
                    "label": "1",
                    "code": "LA2-8",
                    "text": "Other",
                    "other": None,
                    "system": "http://loinc.org"
                  }],
                  "skipLogic": None,
                  "restrictions": None,
                  "defaultAnswer": None,
                  "formatting": None,
                  "calculationMethod": None,
                  "items": None,
                  "linkId": "/99138-0/93157-6",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "93157-6",
                      "display":
                        "Eyes",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
                }
              ],
              "linkId": "/99138-0/93157-6",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "93157-6",
                  "display":
                    "Health Literacy: How often do you need to have someone help you when you read instructions, pamphlets, or other written material from your doctor or pharmacy?",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            }
          ],
          "linkId": "/99138-0/93157-6",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "93157-6",
              "display":
                "Health Literacy: How often do you need to have someone help you when you read instructions, pamphlets, or other written material from your doctor or pharmacy?",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "95744-9",
          "localQuestionCode": "B0200",
          "dataType": "CNE",
          "header": False,
          "units": None,
          "codingInstructions": None,
          "copyrightNotice": None,
          "question":
            "Hearing. Ability to hear (with hearing aid or hearing appliances if normally used)",
          "answers": [
            {
              "hostFieldId":"B0200",
              "setHostFieldId":"B0200_00",
              "label": "0",
              "code": "LA10941-5",
              "text": "Adequate - no difficulty in normal conversation, social interaction, listening to TV",
              "other": None,
              "system": "http://loinc.org"
            },
            {
              "hostFieldId":"B0200",
              "setHostFieldId":"B0200_01",
              "label": "1",
              "code": "LA10942-3",
              "text": "Minimal difficulty - difficulty in some environments (e.g. when person speaks softly or setting is noisy)",
              "other": None,
              "system": "http://loinc.org"
            },
            {
              "hostFieldId":"B0200",
              "setHostFieldId":"B0200_02",
              "label": "2",
              "code": "LA10943-1",
              "text": "Moderate difficulty - speaker has to increase volume and speak distinctly",
              "other": None,
              "system": "http://loinc.org"
            },
            {
              "hostFieldId":"B0200",
              "setHostFieldId":"B0200_03",
              "label": "3",
              "code": "LA10944-9",
              "text": "Highly impaired - absence of useful hearing",
              "other": None,
              "system": "http://loinc.org"
            },
            {
              "hostFieldId":"B0200",
              "setHostFieldId":"B0200_04",
              "label": "4",
              "code": "LA10944-9",
              "text": "Not Assessed / No Information",
              "other": None,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": None,
          "restrictions": None,
          "defaultAnswer": None,
          "formatting": None,
          "calculationMethod": None,
          "items": None,
          "linkId": "/99138-0/95744-9",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "95744-9",
              "display":
                "Hearing. Ability to hear (with hearing aid or hearing appliances if normally used)",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "95745-6",
          "localQuestionCode": "B1000",
          "dataType": "CNE",
          "header": False,
          "units": None,
          "codingInstructions": None,
          "copyrightNotice": None,
          "question":
            "Vision. Ability to see in adequate light (with glasses or other visual appliances)",
          "answers": [
            {
              "hostFieldId":"B1000",
              "setHostFieldId":"B1000_00",
              "label": "0",
              "code": "LA10956-3",
              "text": "Adequate - sees fine detail, such as regular print in newspapers/books",
              "other": None,
              "system": "http://loinc.org"
            },
            {
              "hostFieldId":"B1000",
              "setHostFieldId":"B1000_01",
              "label": "1",
              "code": "LA10957-1",
              "text": "Impaired - sees large print, but not regular print in newspapers/books",
              "other": None,
              "system": "http://loinc.org"
            },
            {
              "hostFieldId":"B1000",
              "setHostFieldId":"B1000_02",
              "label": "2",
              "code": "LA10958-9",
              "text": "Moderately impaired - limited vision; not able to see newspaper headlines but can identify objects",
              "other": None,
              "system": "http://loinc.org"
            },
            {
              "hostFieldId":"B1000",
              "setHostFieldId":"B1000_03",
              "label": "3",
              "code": "LA10959-7",
              "text": "Highly impaired - object identification in question, but eyes appear to follow objects",
              "other": None,
              "system": "http://loinc.org"
            },
            {
              "hostFieldId":"B1000",
              "setHostFieldId":"B1000_04",
              "label": "4",
              "code": "LA10960-5",
              "text": "Severely impaired - no vision or sees only light, colors or shapes; eyes do not appear to follow objects",
              "other": None,
              "system": "http://loinc.org"
            },
            {
              "hostFieldId":"B1000",
              "setHostFieldId":"B1000_05",
              "label": "4",
              "code": "LA10960-5",
              "text": "Not Assessed / No Information",
              "other": None,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": None,
          "restrictions": None,
          "defaultAnswer": None,
          "formatting": None,
          "calculationMethod": None,
          "items": None,
          "linkId": "/99138-0/95745-6",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "95745-6",
              "display":
                "Vision. Ability to see in adequate light (with glasses or other visual appliances)",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        },
        {
          "questionCode": "93157-6",
          "localQuestionCode": "B1300",
          "dataType": "CNE",
          "header": False,
          "units": None,
          "codingInstructions": None,
          "copyrightNotice": "© 2006 Morris et al. Used with permission",
          "question":
            "Health Literacy: How often do you need to have someone help you when you read instructions, pamphlets, or other written material from your doctor or pharmacy?",
          "answers": [
            {
              "hostFieldId":"B1300",
              "setHostFieldId":"B1300_0",
              "label": "0",
              "code": "LA6270-8",
              "text": "Never",
              "score": 0,
              "other": None,
              "system": "http://loinc.org"
            },
            {
              "hostFieldId":"B1300",
              "setHostFieldId":"B1300_1",
              "label": "1",
              "code": "LA10066-1",
              "text": "Rarely",
              "score": 1,
              "other": None,
              "system": "http://loinc.org"
            },
            {
              "hostFieldId":"B1300",
              "setHostFieldId":"B1300_2",
              "label": "2",
              "code": "LA10082-8",
              "text": "Sometimes",
              "score": 2,
              "other": None,
              "system": "http://loinc.org"
            },
            {
              "hostFieldId":"B1300",
              "setHostFieldId":"B1300_3",
              "label": "3",
              "code": "LA10044-8",
              "text": "Often",
              "score": 3,
              "other": None,
              "system": "http://loinc.org"
            },
            {
              "hostFieldId":"B1300",
              "setHostFieldId":"B1300_4",
              "label": "4",
              "code": "LA9933-8",
              "text": "Always",
              "score": 4,
              "other": None,
              "system": "http://loinc.org"
            },
            {
              "hostFieldId":"B1300",
              "setHostFieldId":"B1300_7",
              "label": "4",
              "code": "LA9933-8",
              "text": "Patient declines to respond",
              "score": 4,
              "other": None,
              "system": "http://loinc.org"
            },
            {
              "hostFieldId":"B1300",
              "setHostFieldId":"B1300_8",
              "label": "4",
              "code": "LA9933-8",
              "text": "Patient unable to respond",
              "score": 4,
              "other": None,
              "system": "http://loinc.org"
            }
          ],
          "skipLogic": None,
          "restrictions": None,
          "defaultAnswer": None,
          "formatting": None,
          "calculationMethod": None,
          "items": None,
          "linkId": "/99138-0/93157-6",
          "questionCodeSystem": "http://loinc.org",
          "codeList": [
            {
              "code": "93157-6",
              "display":
                "Health Literacy: How often do you need to have someone help you when you read instructions, pamphlets, or other written material from your doctor or pharmacy?",
              "system": "http://loinc.org"
            }
          ],
          "displayControl": {
            "answerLayout": { "type": "COMBO_BOX", "columns": "0" }
          },
          "questionCardinality": { "min": "1", "max": "1" },
          "answerCardinality": { "min": "0", "max": "1" }
        }
      ],
      "linkId": "/99138-0",
      "questionCodeSystem": "http://loinc.org",
      "codeList": [
        {
          "code": "99138-0",
          "display": "Hearing, Speech, and Vision",
          "system": "http://loinc.org"
        }
      ],
      "displayControl": { "questionLayout": "vertical" },
      "questionCardinality": { "min": "1", "max": "1" },
      "answerCardinality": { "min": "0", "max": "1" }
    }

    section_questionnairre = {
    "questionCode": "99138-0",
    "localQuestionCode": "B",
    "dataType": "SECTION",
    "header": True,
    "units": None,
    "codingInstructions": None,
    "copyrightNotice": None,
    "question": "Hearing, Speech, and Vision",
    "answers": None,
    "skipLogic": None,
    "restrictions": None,
    "defaultAnswer": None,
    "formatting": None,
    "calculationMethod": None,
    "items":[{
        "questionCode":"93157-6",
        "question":"do you have any sensory issues?",
        "instructions":"",
        "items":[{
          "questionCode":"93157-6-1",
          "question":"do you have issue with eyes?",
          "instructions":"",
          "items":[
            {
                  "questionCode": "93157-6-1-1",
                  "localQuestionCode": "",
                  "dataType": "CNE",
                  "header": False,
                  "units": None,
                  "codingInstructions": None,
                  "copyrightNotice": "© 2006 Morris et al. Used with permission",
                  "question": "WNL",
                  "promptQuestion":"is your visibility within normal limits?",
                  "hostFieldId":"cSS_wnl",
                  "instructions":"""
                                  if visibility is within normal limits, select true as the value
                                """,
                  "answers": [{
                    "label": "1",
                    "code": "LA2-8",
                    "text": "WNL (Within Normal Limits)",
                    "other": None,
                    "system": "http://loinc.org"
                  }],
                  "skipLogic": None,
                  "restrictions": None,
                  "defaultAnswer": None,
                  "formatting": None,
                  "calculationMethod": None,
                  "items": None,
                  "linkId": "/99138-0/93157-6",
                  "questionCodeSystem": "http://loinc.org",
                  "codeList": [
                    {
                      "code": "93157-6",
                      "display":
                        "Eyes",
                      "system": "http://loinc.org"
                    }
                  ],
                  "displayControl": {
                    "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
                  },
                  "questionCardinality": { "min": "1", "max": "1" },
                  "answerCardinality": { "min": "0", "max": "1" }
            },
            {
              "questionCode": "93157-6-1-2",
              "localQuestionCode": "",
              "dataType": "CNE",
              "header": False,
              "units": None,
              "codingInstructions": None,
              "copyrightNotice": "© 2006 Morris et al. Used with permission",
              "question": "Glasses",
              "promptQuestion":"Do you have to use glasses?",
              "hostFieldId":"cSS_glasses",
              "instructions":"""
                                if require glasses, select true as the value
                                """,
              "answers": [{
                "label": "1",
                "code": "LA2-8",
                "text": "Glasses",
                "other": None,
                "system": "http://loinc.org"
              }],
              "skipLogic": None,
              "restrictions": None,
              "defaultAnswer": None,
              "formatting": None,
              "calculationMethod": None,
              "items": None,
              "linkId": "/99138-0/93157-6",
              "questionCodeSystem": "http://loinc.org",
              "codeList": [
                {
                  "code": "93157-6",
                  "display":
                    "Eyes",
                  "system": "http://loinc.org"
                }
              ],
              "displayControl": {
                "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
              },
              "questionCardinality": { "min": "1", "max": "1" },
              "answerCardinality": { "min": "0", "max": "1" }
            },
            {
            "questionCode": "93157-6-1-3",
            "localQuestionCode": "",
            "dataType": "CNE",
            "header": False,
            "units": None,
            "codingInstructions": None,
            "copyrightNotice": "© 2006 Morris et al. Used with permission",
            "question": "Contacts Left",
            "hostFieldId":"cSS_contactsl",
            "promptQuestion":"do you use contacts for left eye?",
            "instructions":"""
                                if require contacts for left eye, select true as the value
                                """,
            "answers": [{
              "label": "1",
              "code": "LA2-8",
              "text": "Contacts Left",
              "other": None,
              "system": "http://loinc.org"
            }],
            "skipLogic": None,
            "restrictions": None,
            "defaultAnswer": None,
            "formatting": None,
            "calculationMethod": None,
            "items": None,
            "linkId": "/99138-0/93157-6",
            "questionCodeSystem": "http://loinc.org",
            "codeList": [
              {
                "code": "93157-6",
                "display":
                  "Eyes",
                "system": "http://loinc.org"
              }
            ],
            "displayControl": {
              "answerLayout": { "type": "CHECK_BOX", "columns": "0" }
            },
            "questionCardinality": { "min": "1", "max": "1" },
            "answerCardinality": { "min": "0", "max": "1" }
          },
          ]
        }]
    }]
    }
    
    
    # question instructions prompt input
    section_question_instructions_prompt_input = {
      "93157-6-1-1":{"question":"is your visibility within normal limits?","instructions":"if visibility is within normal limits, select true as the value otherwise false"},
      "93157-6-1-2":{"question":"Do you have to use glasses?","instructions":"if require glasses, select true as the value"},
      "93157-6-1-3":{"question":"do you use contacts for left eye?","instructions":"if require contacts for left eye, select true as the value"},
    }
    
    # question source prompt output
    section_question_source_prompt_output = {
        "93157-6-1-1":{"source":"some transcript source"},
        "93157-6-1-2":{"source":"some transcript source"},
        "93157-6-1-3":{"source":"some transcript source"},
    }
    
    # answers prompt output
    section_question_answer_prompt_output = {
      "93157-6-1-1":{"value":""},
      "93157-6-1-2":{"value":""},
      "93157-6-1-3":{"value":""},
    }
    
    # merge above 2 outputs into the desired output result
    section_extraction_result_output = {
      
    }
    

    