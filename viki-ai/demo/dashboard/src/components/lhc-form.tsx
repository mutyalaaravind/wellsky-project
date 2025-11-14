import React from 'react';
import { useScript } from 'usehooks-ts';
import StartOfCare from '../assets/lhc-forms/99131-5.json';
import '../assets/lhc-forms/styles.css';

const root = new URL((document as any).currentScript.src).origin;

declare global {
  interface Window {
    LForms: any;
  }
}

type Section = {
  id: string;
  title: string;
  el: HTMLDivElement;
};

export interface FormAdapter {
  getSections: () => Array<Section>;
  getFieldsValue: (sectionId?: string) => any;
  setFieldsValue: (values: any) => void;
}

type FormProps = {
  id: string;
  onFormReady?: (schema: any, formAdapter: FormAdapter) => void; // `schema` arg needs to be dropped once we get rid of LHC forms inside review widget.
  onError?: (e: any) => void;
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
        // result._meta = result._meta || {};
        // result._meta[item.question] = {
        //   code: item.questionCode,
        // };
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

  if (Array.isArray(value) && item.items != null) {
    // This is a value for a repeating group
    // Remove all occurences of this group from questionnaire and take the first one as a template
    const template = item.items.find((item: any) => item.question === key);
    let originalIndex = newItem.items.indexOf(template);
    newItem.items = item.items.filter((item: any) => item.question !== key);


    // Now add new items
    value.forEach((valueItem: any) => {
      newItem.items.splice(originalIndex, 0, setQuestionnaireFromFormFields(template, key, valueItem));
      originalIndex++;
    });
  } else {
    // This is a value for an ordinary group or a field
    if (typeof item.items !== 'undefined' && item.items != null) {
      // This is a group
      newItem.items = newItem.items.map((childItem: any) => {
        if (typeof value[childItem.question] !== 'undefined' && value[childItem.question] != null) {
          return setQuestionnaireFromFormFields(childItem, childItem.question, value[childItem.question]);
        }
        return childItem;
      });
    } else if (item !== null && typeof item !== 'undefined') {
      if (typeof item.answers !== 'undefined' && item.answers != null) {
        // This is a field with answers, replace text value with answer object
        const answerObj = newItem.answers.find((answer: any) => answer.text === value);
        if (typeof answerObj === 'undefined') {
          console.error('No answer object found for value', value, 'in field', key);
        }
        newItem.value = answerObj;
      } else {
        // This is a normal field
        newItem.value = value;
      }
    }
  }

  return newItem;
};

export const LHCForm: React.FC<FormProps> = ({ id, onFormReady, onError }) => {
  const zoneStatus = useScript(`${root}/3rdparty/lhc-forms/zone.min.js`, { removeOnUnmount: true });
  const lhcStatus = useScript(`${root}/3rdparty/lhc-forms/lhc-forms.js`, { removeOnUnmount: true });

  const scriptsReady = zoneStatus === 'ready' && lhcStatus === 'ready';

  const [formId, setFormId] = React.useState<string | null>(null);
  React.useEffect(() => {
    setFormId(`lhc-original-form-${Math.random().toString(36).substring(7)}`);
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

    console.log('adding to page', StartOfCare, formRef.current.id);
    window.LForms.Util.addFormToPage(StartOfCare, formRef.current.id);
    lhcFormRef.current = formRef.current.querySelector('wc-lhc-form');
    (window as any).lhcForm = lhcFormRef.current;

    const onLHCFormReady = () => {
      // Form object
      const formObj = window.LForms.Util._getFormObjectInScope(formRef.current);
      (window as any).formObj = formObj;

      const formAdapter = {
        getSections: () : Array<Section> => {
          const topLevelSectionEls = lhcFormRef.current.querySelectorAll('form > div > lhc-item');
          return (Array.prototype.map.call(topLevelSectionEls, (el: any) => {
            const linkId = el.getAttribute('id').split('-').slice(1).join('-');
            const label = el.querySelector(`label[id="label-${linkId}"]`);
            const text = label.innerText;
            return {
              id: text,
              title: text,
              el: (label.parentNode.parentNode as HTMLDivElement),
            };
          }) as Array<Section>);
        },
        getFieldsValue: (sectionId?: string) => {
          const questionnaire = formObj.getFormData(false, true);
          const data = getFormFieldsFromQuestionnaire(questionnaire);
          if (typeof sectionId === 'undefined') {
            // Return all sections
            return data;
          }
          // Return only one section
          return { [sectionId]: data[sectionId] };
        },
        setFieldsValue: (values: any) => {
          console.log('Setting original form values to:', values);
          if (typeof values === 'undefined') {
            console.error('setFieldsValue got undefined as value');
            return;
          }
          let questionnaire = formObj.getFormData(false, true);
          
          questionnaire = setQuestionnaireFromFormFields(questionnaire, null, values);
          
          lhcFormRef.current.questionnaire = questionnaire;
        },
      };
      (window as any).formAdapter = formAdapter;

      window.requestAnimationFrame(() => {
        // Dirty, dirty hack to wait for inputs to render
        onFormReady?.(formObj.getFormData(false, true), formAdapter);
      });
    };

    const onLHCFormError = (e: any) => {
      console.log("Host form error:", e)
      onError?.(e);
    };

    lhcFormRef.current.addEventListener('onFormReady', onLHCFormReady);
    formRef.current.addEventListener('onError', onLHCFormError);

    const currentFormRef = formRef.current;
    return () => {
      // Effect destructor
      currentFormRef.removeEventListener('onFormReady', onLHCFormReady);
      currentFormRef.removeEventListener('onError', onLHCFormError);
      window.LForms.Util.removeFormsFromPage(currentFormRef);
    };
  }, [formId, scriptsReady]);

  // TODO: Remove hard-coded id
  return formId !== null ? (
    <div id={id} ref={formRef}>Loading LHC Form...</div>
  ) : null;
};
