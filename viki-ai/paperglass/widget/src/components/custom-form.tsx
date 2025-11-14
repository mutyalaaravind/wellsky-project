// import { v4 as uuidv4 } from 'uuid'
import {
  PrimaryButton,
  SecondaryButton,
  TitleNavigation,
} from "@mediwareinc/wellsky-dls-react";
// import { useRouter } from 'next/router'
import { useEffect, useRef, useState } from "react";
import useScript from "../hooks/useScript";
import { Box, VStack, useToast } from "@chakra-ui/react";
import useCustomFormWrapper from "../hooks/useCustomFormWrapper";

export interface CustomWindow extends Window {
  FormsWidgetSettings: any;
  formsEventBus: any;
}

declare let window: CustomWindow;

export type CustomFormsComponentProps = {
  widgetHost: string;
  formFieldValues?: any;
  newData?: any;
  onFormFieldsLoaded?: (fields: Array<any>) => void;
  env: any;
  setFormTemplate?: any;
  approvedFormFieldValues?: any;
  mount?: string;
  formInstanceId?: string;
  formTemplateId?: string;
  onEvidenceRequested?: (field: any,newData: any) => void;
};

const CustomFormsComponent: React.FC<CustomFormsComponentProps> = ({
  widgetHost,
  formFieldValues,
  onFormFieldsLoaded,
  env,
  setFormTemplate,
  approvedFormFieldValues,
  formInstanceId,
  formTemplateId,
  newData,
  onEvidenceRequested,
  mount = "custom-form-component",
}: CustomFormsComponentProps) => {
  const toast = useToast();
  // const router = useRouter()
  const patientId = "abc";
  const organizationId = "org1";
  const customFormsTenantId = "ORG-2ddf3fbd-9dcd-432a-bbf6-ae0f238f0df4";
  const customFormsTokenDefault =
    "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhcHBfaWQiOiI0QmdXWnJOWTR6NSIsInRlbmFudF9pZCI6Ik9SRy0yZGRmM2ZiZC05ZGNkLTQzMmEtYmJmNi1hZTBmMjM4ZjBkZjQiLCJ0ZW5hbnRfaWRzIjpbXSwiYXV0aGRfdGVuYW50X2lkcyI6WyIxNjY5Il0sIndyaXRlX29wX3RlbmFudF9pZHMiOltdLCJ1c2VyIjp7ImlkIjoiVVNFUi0xZjEwMWM5My0zMTBhLTRlZTgtOWJhYS1jODY4MGY4YWRlNWIiLCJlbWFpbCI6InZrb292YStxYUBjbGVhcmNhcmVvbmxpbmUuY29tIiwiZnVsbF9uYW1lIjoiVmlwaW4gS29vdmEiLCJuYW1lIjoiVmlwaW4gS29vdmEiLCJyb2xlcyI6WyJSRUdJU1RFUkVEX1VTRVIiLCJBUFBfQURNSU4iLCJURU5BTlRfQURNSU4iXX0sImlhdCI6MTcwODU0NjY5N30.pR8Z0_k7zYq_Gz_G-eI_wIpcGC83vNGMzfQVq-7x0V4";

  const [formsSettingsId, setFormsSettingsId] = useState<any>("");
  const [saveLoading, setSaveLoading] = useState(false);
  const [submitLoading, setSubmitLoading] = useState(false);
  const formsContainerRef = useRef(null);
  const [customFormsToken, setCustomFormsToken] = useState<string>(
    customFormsTokenDefault,
  );
  const [formTemplateFields, setFormTemplateFields] = useState<Array<any>>([]);
  const [form, setForm] = useState<any>(null);

  const formInstance = useRef<any>(null);

  const resolveFormFieldValue = (
    fieldValue: any,
    fieldType: string,
    formField: any,
  ) => {
    if (fieldType === "ENUM_CHECKBOX") {
      return { checkboxValues: JSON.stringify([fieldValue]) };
    }
    return fieldValue;
  };

  useCustomFormWrapper(form, newData, mount, onEvidenceRequested);

  useEffect(() => {
    // console.log("formTemplateFields",formTemplateFields,formFieldValues,approvedFormFieldValues);
    formInstance.current = form;
    try {
      const formFieldJsonValues = approvedFormFieldValues; //JSON.parse(formFieldValues);
      // console.log("formFieldJsonValues",formFieldJsonValues)
      // debugger;
      formTemplateFields.forEach((field: any) => {
        const fieldKeyValue: { [key: string]: string | number | any } = {};
        const resolvedPathedName = field.pathedName
          .toString()
          .replace(/,/gi, ".");

        if (field.pathedName && field.pathedName.length > 1) {
          fieldKeyValue[field.pathedName[0]] = resolveFormFieldValue(
            formFieldJsonValues[field.pathedName[0]],
            field.formFieldType,
            field,
          );
        } else if (formFieldJsonValues.hasOwnProperty(field.fieldName)) {
          fieldKeyValue[field.fieldName] = resolveFormFieldValue(
            formFieldJsonValues[field.fieldName],
            field.formFieldType,
            field,
          );
        }
        //console.log("field", field, fieldKeyValue);
        if (field.fieldType === "ENUM_CHECKBOX") {
          formInstance.current.setFieldsValue(fieldKeyValue);
        } else {
          formInstance.current.setFieldsValue(fieldKeyValue);
        }
      });
    } catch (error) {
      // console.log("error in form rendering", error);
    }
  }, [
    JSON.stringify(formFieldValues),
    JSON.stringify(approvedFormFieldValues),
  ]);

  useEffect(() => {
    const collectFieldsWithQuestions = (fieldsList: any) => {
      let fields: Array<any> = [];
      fieldsList.forEach((field: any) => {
        // console.log('Collecting', field);
        if (
          field.formFieldType === "SECTION" ||
          field.formFieldType === "FIELD_GROUP"
        ) {
          fields = fields.concat(collectFieldsWithQuestions(field.fields));
        } else {
          if (field) {
            fields.push(field);
          }
        }
      });

      return fields;
    };

    if (!customFormsToken || !formInstanceId) {
      return;
    }

    // const uuid = uuidv4();

    // setFormsSettingsId(uuid);
    setFormsSettingsId("formsSettingsId-1");

    const cfApi = (env as any).FORMS_API;
    const cfkey = (env as any).FORMS_API_KEY;
    const version = (env as any).VERSION;

    (window as any).cf_config = {
      env: version,
      aws_appsync_graphqlEndpoint: cfApi,
      aws_appsync_apiKey: cfkey,
    };
    window.FormsWidgetSettings = window.FormsWidgetSettings || {};
    window.FormsWidgetSettings.widgets =
      window.FormsWidgetSettings.widgets || [];

    window.FormsWidgetSettings.widgets.push({
      widget: "complete_form",
      formTemplateId,
      type: "inline",
      mount,
      metadataForSubmit: [
        {
          key: "patient_id",
          value: patientId,
        },
        {
          key: "patient_name",
          value: patientId,
        },
        {
          key: "organization_id",
          value: customFormsTenantId,
        },
      ],
      formInstanceId: formInstanceId || "None",
      timezone: "US/Eastern",
      token: customFormsToken,
      baseUrl: window.location.href,
      showCancel: true,
      // showCard: false,
      // showSave: true,
      // showSubmit: true,
      updateButtonText: "Update & Continue Later",
      saveButtonText: "Save & Continue Later",
      submitButtonText: "Submit Assessment",
      afterSubmitUrl: `/patients/cpplist?id=${patientId}`,
      afterSaveUrl: `/patients/cpplist?id=${patientId}`,
      viewFormUrl: `/patients/cpp?id=${patientId}&formInstanceId=`,
      //autoSave: 'False',
      metadataFilter: [
        {
          key: "patient_id",
          value: patientId,
        },
      ],
      onFormError: (e: any) => {
        setSaveLoading(false);
        setSubmitLoading(false);
      },
      onFormSubmit: function (yesno: any, formfields: any, response: any) {
        setSaveLoading(false);
        setSubmitLoading(false);
        if (response === undefined) {
          setTimeout(() => {
            //router.push('/screening')
          }, 2000);
        } else {
        }
      },
      autoFillLastResponse: false,
      onFormReady: (form: any, formTemplate: any) => {
        setForm(form);
        formInstance.current = form;
        setFormTemplate?.(formTemplate);
        // console.log({formInstance})
        // console.log("formTemplate", formTemplate)

        const fields: Array<any> = collectFieldsWithQuestions(
          formTemplate.fields,
        );
        //console.log(fields);
        if (formInstance && formInstance.current) {
          fields.forEach((field: any) => {
            //   //form.setFieldValue(field.name, 'foo bar');
            // });
            //console.log(field);
          });
          //console.log(formInstance.current.setFieldsValue({"select_screeningType":"Self-screening"}));
        }

        if (onFormFieldsLoaded) {
          setFormTemplateFields(fields);
          onFormFieldsLoaded(fields);
        }
      },
    });
  }, [customFormsToken, formInstanceId, JSON.stringify(env)]);

  useScript(`${widgetHost}/widgets/formsWidgetsNG.js`, [
    formsSettingsId,
    customFormsToken,
    formInstanceId,
    JSON.stringify(env),
  ]);

  const onSubmit = async () => {
    if (formsContainerRef && (formsContainerRef.current as any)) {
      setSubmitLoading(true);
      await window.formsEventBus.dispatch(`${mount}_onFormSubmit`);
    }
  };

  const onSaveAndContinue = async () => {
    if (formsContainerRef && (formsContainerRef.current as any)) {
      setSaveLoading(true);
      await window.formsEventBus.dispatch(`${mount}_onFormSubmit`);
      //await window.formsEventBus.dispatch(`custom-form-complete_onFormUpdate`)
    }
  };

  return (
    <>
      <VStack gap={4} w="100%" h="full">
        {/* <Box
          bg='white'
          borderTopWidth='1px'
          borderStyle='solid'
          borderColor='bigStone.50'
          p='2'
          position='relative'
          bottom='0'
          left='0'
          right='0'
          width='100%'
          h="30px"
        >

        </Box> */}

        <Box
          // overflow="scroll"
          id={mount}
          alignContent="center"
          w="100%"
          // h='calc(100vh - 200px)'
          justifyContent="center"
        >
          <Box>Assessment</Box>
          <Box ref={formsContainerRef}>Loading...</Box>
        </Box>
      </VStack>
    </>
  );
};

export default CustomFormsComponent;
