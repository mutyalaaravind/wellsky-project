/*
  * This component renders an "annotated form".
  * It's currently using LHC form as renderer, so it can only be used with host application that uses LHC form as well.
  * We'll need to replace LHC form with a generic form renderer owned by us.
*/

import React from 'react';
import { useScript } from 'usehooks-ts';
import './AnnotatedForm.css';

const root = new URL((document as any).currentScript.src).origin;

declare global {
  interface Window {
    LForms: any;
  }
}

type GetFieldsValueOpts = {
  checkedOnly?: boolean;
};

export interface AnnotatedFormAdapter {
  getFieldsValue: (opts?: GetFieldsValueOpts) => any;
  getFieldValue: (path: Array<string>) => any;
  setFieldsValue: (values: any,sectionId:string) => void;
  setFieldValue: (path: Array<string>, value: any) => void;
  setCheckboxValue: (path: Array<string>, value: boolean) => void;
  setCheckboxesValue: (value: boolean) => void;
}

type AnnotatedFormProps = {
  schema: any; // Schema in questionnaire format. TODO: This field must be removed once we have our own form renderer.
  onFormReady?: (annotatedFormAdapter: AnnotatedFormAdapter) => void;
  onCheckboxToggle?: (path: Array<string>, checked: boolean) => void;
  onInfoClick?: (item: any) => void;
  sectionId?: string;
}

const getFormFieldsFromQuestionnaire = (item: any) => {
  // Convert questionnaire into AntD-like structure, e.g.
  // {
  //   'Demographics': {
  //     'First Name': 'John',
  //     'Last Name': 'Doe',
  //   },
  //   'Medical History': {
  //     'Diabetes': 'Yes',
  //     'Hypertension': 'No',
  //   },
  // }
  //
  // Also wrap repeating groups into arrays, e.g.
  // {
  //   'Medical Conditions': [
  //     {
  //       'Condition': 'Foo',
  //       'Active': 'Yes',
  //     },
  //     {
  //       'Condition': 'Bar',
  //       'Active': 'No',
  //     },
  //   ],
  // }
  //
  // Finally, replace answer objects with their text values

  let result: any = {};

  // console.log(item);

  if (typeof item.items !== 'undefined' && item.items != null) {
    // This is a group
    item.items.forEach((item: any) => {
      let value = getFormFieldsFromQuestionnaire(item);
      if (typeof item.answers !== 'undefined' && item.answers != null) {
        // Child is a field with answers, add possible values as metadata
        // value = {
        //   ...value,
        //   _meta: {
        //     answers: item.answers,
        //   },
        // };
        result._meta = result._meta || {};
        result._meta[item.question] = {
          answers: item.answers.map((answer: any) => answer.text),
        };
      }
      if (typeof item.questionCode !== 'undefined') {
        // Child is a field with a code, add it as metadata
        // value = {
        //   ...value,
        //   _meta: {
        //     code: item.questionCode,
        //   },
        // };
        result._meta = result._meta || {};
        result._meta[item.question] = {
          code: item.questionCode,
        };
      }
      if (item.questionCardinality.max !== '1') {
        // This is a repeating group, wrap into array if not wrapped yet
        if (typeof result[item.question] === 'undefined') {
          result[item.question] = [];
        }
        result[item.question].push(value);
      } else {
        result[item.question] = value;
      }
    });
  } else {
    if (typeof item.answers !== 'undefined' && item.answers != null) {
      // This is a field with answers, replace answer object with its text value
      result = typeof item.value !== 'undefined' ? item.value.text : null;
    } else {
      // This is a normal field
      if (typeof item.value === 'undefined') {
        result = null;
      } else {
        result = item.value;
      }
    }
  }

  return result;
};

const setQuestionnaireFromFormFields = (item: any, key: any, value: any) => {
  // Populate questionnaire from AntD-like structure while parsing repeatable groups and converting text values into answer objects when needed
  const newItem = { ...item };

  if (Array.isArray(value)) {
    // This is a value for a repeating group
    // Remove all occurences of this group from questionnaire and take the first one as a template
    const template = item.items?.find((item: any) => item.question === key);
    let originalIndex = newItem.items?.indexOf(template);
    newItem.items = item.items?.filter((item: any) => item.question !== key);

    // Now add new items
    value.forEach((valueItem: any) => {
      newItem.items?.splice(originalIndex, 0, setQuestionnaireFromFormFields(template, key, valueItem));
      originalIndex++;
    });

  } else {
    // This is a value for an ordinary group or a field
    if (typeof item.items !== 'undefined' && item.items != null) {
      // This is a group
      newItem.items = newItem.items?.map((childItem: any) => {
        if (typeof value[childItem.question] !== 'undefined' && value[childItem.question] !== null) {
          return setQuestionnaireFromFormFields(childItem, childItem.question, value[childItem.question]);
        }
        return childItem;
      });
    } else if (item !== null && typeof item !== 'undefined') {
      if (typeof item.answers !== 'undefined' && item.answers != null) {
        // This is a field with answers, replace text value with answer object
        const answerObj = newItem.answers?.find((answer: any) => {
            //console.log(answer.text);
            return answer.text === value || answer.text === value?.["value"]
          }
        );
        if (typeof answerObj === 'undefined') {
          console.error('No answer object found for value', value, 'in field', key, 'answer to look for');
        }
        console.log("newItem.value = answerObj",answerObj);
        newItem.value = answerObj;
        newItem["verbatim_source"] = value?.["verbatim_source"]
      } else {
        console.log("value=",value);
        newItem.value = value?.["value"] || value;
        newItem["verbatim_source"] = value?.["verbatim_source"]
      }
    }
  }

  return newItem;
};

const AnnotatedForm: React.FC<AnnotatedFormProps> = ({ schema, onFormReady, onCheckboxToggle, onInfoClick, sectionId }) => {
  const zoneStatus = useScript(`${root}/3rdparty/lhc-forms/zone.min.js`, { removeOnUnmount: true });
  const lhcStatus = useScript(`${root}/3rdparty/lhc-forms/lhc-forms.js`, { removeOnUnmount: true });

  const scriptsReady = zoneStatus === 'ready' && lhcStatus === 'ready';

  const [formId, setFormId] = React.useState<string | null>(null);
  React.useEffect(() => {
    setFormId(`lhc-annotated-form-${Math.random().toString(36).substring(7)}`);
  }, []);

  // Form container (div)
  const formRef = React.useRef<HTMLDivElement | any>(null);
  // Actual form WebComponent - <wc-lhc-form />
  const lhcFormRef = React.useRef<any>(null);

  React.useEffect(() => {
    if (!scriptsReady) {
      // Scripts not loaded yet
      return;
    }
    if (formId === null) {
      // Form ID not generated yet
      return;
    }

    console.log('Rendering annotated form into', formRef.current.id);
    window.LForms.Util.addFormToPage(schema, formRef.current.id);
    lhcFormRef.current = formRef.current.querySelector('wc-lhc-form');

    (window as any).lhcForm = lhcFormRef.current;

    lhcFormRef.current.addEventListener('onFormReady', () => {
      // Form object
      const formObj = window.LForms.Util._getFormObjectInScope(formRef.current);
      (window as any).formObj = formObj;

      let checkboxes: {
        [key: string]: HTMLInputElement;
      } = {};

      const annotatedFormAdapter: AnnotatedFormAdapter = {
        getFieldsValue: (opts: GetFieldsValueOpts = {}) => {
          const questionnaire = formObj.getFormData(false, true);
          const data = getFormFieldsFromQuestionnaire(questionnaire);

          const filterChecked = (obj: any, path: Array<string> = []): any => {
            let newObj: any = {};
            Object.entries(obj).forEach(([key, value]) => {
              if (key === 'Mobility - SOC/ROC Performance') {
                console.log(key, typeof value, typeof value === 'object', value !== null, Array.isArray(value));
              }
              if (key === '_meta') {
                // Return metadata as is
                newObj[key] = value;
              } else if (typeof value === 'object' && value !== null) {
                // Nested group
                console.log('Nested:', key);
                newObj[key] = filterChecked(value, [...path, key]);
              } else if (Array.isArray(value)) {
                // Repeating group
                newObj[key] = value.map((item) => filterChecked(item, [...path, key]));
              } else {
                // Normal value
                const fieldPath = [...path, key];
                const checkbox = checkboxes[fieldPath.join('//')];
                if (typeof checkbox === 'undefined') {
                  console.error('No checkbox found for path', fieldPath);
                } else if (checkbox.checked) {
                  newObj[key] = value;
                }
              }
            });
            return newObj;
          }

          if (opts.checkedOnly) {
            return filterChecked(data);
          }
          return data;
        },
        getFieldValue: (path: Array<string>) => {
          const questionnaire = formObj.getFormData(false, true);
          let value = getFormFieldsFromQuestionnaire(questionnaire);
          path.forEach((key) => {
            value = typeof value === 'undefined' ? undefined : value[key];
          });
          return value;
        },
        setFieldsValue: (values: any, sectionId?:string) => {
          let questionnaire = formObj.getFormData(false, true);

          questionnaire = setQuestionnaireFromFormFields(questionnaire, null, values);
          
          console.log("questionnaire",questionnaire);

          if(sectionId){
            console.log("sectionId",sectionId);
            questionnaire.items = questionnaire.items.filter((item:any)=>item.question === sectionId);
            console.log("questionnaire1",questionnaire);
          }

          lhcFormRef.current.questionnaire = questionnaire;
        },
        setFieldValue: (path: Array<string>, value: any) => {
          console.error('Not implemented');
        },
        setCheckboxValue: (path: Array<string>, value: boolean) => {
          lhcFormRef.current.querySelector(`input[type="checkbox"][data-path="${path.join('//')}"]`).checked = value;
        },
        setCheckboxesValue: (value: boolean) => {
          Array.prototype.slice.call(lhcFormRef.current.querySelectorAll('input[type="checkbox"][data-path]')).forEach((el: any) => {
            el.checked = value;
          });
        }
      };
      (window as any).annotatedFormAdapter = annotatedFormAdapter;

      window.requestAnimationFrame(() => {
        // Dirty, dirty hack to wait for inputs to render
        onFormReady?.(annotatedFormAdapter);

        const questionnaire = formObj.getFormData(false, true);

        if(sectionId){
          console.log("sectionId",sectionId);
          questionnaire.items = questionnaire.items.filter((item:any)=>item.question === sectionId);
          console.log("questionnaire1",questionnaire);
        }

        const walkQuestionnaireFields = (root: any, callback: any, prefix: Array<string> = []) => {
          if (root.items !== null && typeof root.items !== 'undefined') {
            // This is a group
            root.items.forEach((item: any) => {
              if (item.questionCardinality.max !== '1') {
                // TODO: This is a repeating group, need to add index to prefix
              }
              walkQuestionnaireFields(item, callback, [...prefix, item.question]);
            });
          } else {
            // This is a field
            callback(root, prefix);
          }
        };

        walkQuestionnaireFields(questionnaire, (item: any, path: Array<string>) => {
          const els = lhcFormRef.current.querySelectorAll(`[id^="item-${item.linkId}"]`);
          if (els.length !== 1) {
            console.error('Expected 1 element for linkId', item.linkId, 'but found', els.length, '- stuff is going to break!');
            return;
          }
          const el = els[0];
          const questionTextEl = el.querySelector('lhc-item-question lhc-item-question-text span.lhc-question');
          const checkbox = document.createElement('input');
          checkbox.type = 'checkbox';
          checkbox.setAttribute('style', 'margin: 0 5px 0 0; vertical-align: middle; cursor: pointer');
          checkbox.setAttribute('data-path', path.join('//'));  // More hacks!
          checkbox.addEventListener('change', () => {
            onCheckboxToggle?.(path, checkbox.checked);
          });
          checkboxes[path.join('//')] = checkbox;

          const infoIcon = document.createElement('label');
          infoIcon.innerHTML = "&#169;";
          // infoIcon.innerHTML = `<svg class="bi bi-x-circle" fill="#ec5e45" focusable="true"
          //   viewBox="64 64 896 896" width="1em" height="1em" xmlns="http://www.w3.org/2000/svg">
          //   <path
          //       d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
          //   <path
          //       d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>
          // </svg>`;
          // infoIcon.innerHTML =`<svg viewBox="64 64 896 896" focusable="false" 
          //     data-icon="exclamation-circle" width="1em" height="1em" fill="currentColor" 
          //     aria-hidden="true">
          //     <path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm0 820c-205.4 0-372-166.6-372-372s166.6-372 372-372 372 166.6 372 372-166.6 372-372 372z"></path>
          //     <path d="M464 688a48 48 0 1096 0 48 48 0 10-96 0zm24-112h48c4.4 0 8-3.6 8-8V296c0-4.4-3.6-8-8-8h-48c-4.4 0-8 3.6-8 8v272c0 4.4 3.6 8 8 8z"></path>
          //     </svg>`;
          infoIcon.addEventListener('click', () => {
            console.log("infoIcon",item);
            onInfoClick?.(item);
          });
          //infoIcon.setAttribute('style','width:1px')

          questionTextEl.insertBefore(checkbox, questionTextEl.firstChild);

          questionTextEl.insertBefore(infoIcon, questionTextEl.childNodes[2]);
          const label = questionTextEl.querySelector('label');
          label.addEventListener('click', () => {
            checkbox.click();
          });
          label.setAttribute('style', 'cursor: pointer; user-select: none');
        });
      });
    });

    const currentFormRef = formRef.current;
    return () => {
      window.LForms.Util.removeFormsFromPage(currentFormRef);
    };
  }, [scriptsReady, formId, schema, onCheckboxToggle]);

  // TODO: Remove hard-coded id
  return formId !== null ? (
    <div id={formId} ref={formRef}>Loading LHC Form...</div>
  ) : null;
};

export default AnnotatedForm;
