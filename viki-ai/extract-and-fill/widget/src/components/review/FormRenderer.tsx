import { Button, Card, Checkbox, Col, Form, Input, Radio, Row } from "antd";
import React, { useCallback, useEffect, useMemo, useRef } from "react";
import FormInput from "./FormInput";
import InputWithEdit from "./InputWithEdit";

import EditableCard from "./EditableCard";
import ReadOnlyField from "./ReadOnlyField";
import useEnvJson from "../../hooks/useEnvJson";
import { Env } from "../../types";

import { EvidencePopover } from "./EvidencePopover";


export interface FormRendererProps {
  template: any;
  extractedText?: string | undefined | null;
  transcriptText?: string | undefined | null;
  transcriptId?: string | undefined | null;
  setApprovedFormFieldValues?: (approvedFields: any) => {};
  onApprovedFormFieldValues?: (approvedFields: any) => void;
  mount?: string;
  onEvidenceReceived:(evidence: any)=>void;
}

function FormRenderer({
  template,
  extractedText,
  transcriptText,
  transcriptId,
  setApprovedFormFieldValues,
  onApprovedFormFieldValues,
  mount,
  onEvidenceReceived
}: FormRendererProps) {
  // const extractedText = demoText;
  const [form] = Form.useForm();
  const env = useEnvJson<Env>();
  
  console.log(
    "Widget form",
    { form },
    { extractedText },
    { transcriptText },
    { template },
    { transcriptId}
  );

  const formValues = useMemo(() => {
    try {
      return JSON.parse(extractedText as string);
    } catch (error) {
      return {};
    }
  }, [extractedText]);


  const renderFields = useCallback(
    (fields: any[], inputOnly = true, isFieldMapping = true) => {
      const sectionFields = ["SECTION", "DATA_ENTITY", "FIELD_GROUP"];
      if (!fields || !fields.length) {
        return null;
      }

      return fields?.map((field) => {
        //console.log("formRenderField", field);
        if (sectionFields.includes(field.formFieldType) && field.isList) {
          return (
            <div style={{ display: "flex", gap: 4 }}>
              <Form.Item
                name={["approved"].concat(
                  field.pathedName || field.fieldName || field.displayName
                )}
                valuePropName="checked"
              >
                <Checkbox />
              </Form.Item>
              <EditableCard
                field={field}
                evidencePopover={
                                  <EvidencePopover 
                                        field={field}
                                        env={env}
                                        onEvidenceReceived={onEvidenceReceived}
                                        transcriptId={transcriptId}
                                        transcriptText={transcriptText}
                                        extractedText={extractedText}
                                  />
                                }
              />
            </div>
          );
        }

        if (sectionFields.includes(field.formFieldType)) {
          return (
            <Card
              size="small"
              title={field.displayName}
              key={field.pathedName || field.fieldName || field.displayName}
              style={{ marginBottom: 10 }}
            >
              {isFieldMapping && field.isList
                ? renderFields(
                    field.fields?.map((f: any) => {
                      let pathedName = [...(f.pathedName || [])];
                      const last = pathedName.pop();
                      pathedName = [...pathedName, 0, last];
                      return {
                        ...f,
                        pathedName,
                      };
                    }),
                    inputOnly,
                    isFieldMapping
                  )
                : renderFields(field.fields, inputOnly, isFieldMapping)}
            </Card>
          );
        }

        if (field.formFieldType === "READONLY") {
          return (
            <Row>
              <Col span={2}>
                {/* <Form.Item
                name={["approved"].concat(
                  field.pathedName || field.fieldName || field.displayName
                )}
                valuePropName="checked"
              >
                <Checkbox />
              </Form.Item> */}
              </Col>
              <Col span={22}>
                <ReadOnlyField
                  field={field}
                  evidencePopover={
                    <EvidencePopover 
                          field={field}
                          env={env}
                          onEvidenceReceived={onEvidenceReceived}
                          transcriptId={transcriptId}
                          transcriptText={transcriptText}
                          extractedText={extractedText}
                    />
                  }
                />
              </Col>
            </Row>
          );
        }

        return (
          <Row>
            <Col span={2}>
              <Form.Item
                name={["approved"].concat(
                  field.pathedName || field.fieldName || field.displayName
                )}
                valuePropName="checked"
              >
                <Checkbox />
              </Form.Item>
            </Col>
            <Col span={22}>
              <FormInput
                key={field.pathedName || field.fieldName || field.displayName}
                label={<b>{field.displayName}</b>}
                name={field.pathedName || field.fieldName || field.displayName}
              >
                {inputOnly ? (
                  <InputWithEdit
                    formFieldType={field.formFieldType}
                    field={field}
                    evidencePopover={
                      <EvidencePopover 
                            field={field}
                            env={env}
                            onEvidenceReceived={onEvidenceReceived}
                            transcriptId={transcriptId}
                            transcriptText={transcriptText}
                            extractedText={extractedText}
                      />
                    }
                  />
                ) : (
                  <Input.TextArea />
                )}
              </FormInput>
            </Col>
          </Row>
        );
      });
    },
    [form, env]
  );

  useEffect(() => {
    form.setFieldsValue(formValues);

    return () => {
      form.resetFields();
    };
  }, [form, formValues]);

  useEffect(() => {
    if (form) {
      form.setFieldValue(["hidden"], "test");
    }
  }, [form]);

  // console.log({ template });

  const setNestedObjectValue = (
    path: string[] = [],
    obj: any = {},
    value: any = {}
  ) => {
    let newObj = obj?.[path[0]] || {};

    if (path.length > 1) {
      obj[path[0]] = setNestedObjectValue(
        path.slice(1),
        newObj,
        value?.[path[0]]
      );
    } else {
      obj[path[0]] = value?.[path[0]];
    }

    return obj;
  };

  const setNestedValue = useCallback(
    (obj: any = {}, value: any, formFieldValues: any) => {
      let result: any = {};
      const keys = Object.keys(obj);

      for (const k of keys) {
        if (
          ["string", "number", "boolean", "undefined"].includes(
            typeof obj[k]
          ) ||
          obj[k] === null
        ) {
          if (formFieldValues && formFieldValues[k] !== "") result[k] = value;
        } else {
          result[k] = setNestedValue(obj[k], value, formFieldValues);
        }
      }

      return result;
    },
    []
  );

  function deriveApprovedValues(paths: string[][], data: any) {
    let result: Partial<typeof data> = {};

    for (const path of paths) {
      result = setNestedObjectValue(path, result, data);
    }
    return result;
  }

  const selectAllChange = useCallback(
    (selectAll: boolean) => {
      const values = form.getFieldsValue();

      const approvedFieldsData = values.approved;
      form.setFieldsValue({
        approved: setNestedValue(approvedFieldsData, selectAll, values),
        // approved: setNestedValue(approvedFieldsData, form.getFieldValue(['checkAll'])),
      });
    },
    [form, setNestedValue]
  );

  const selectAll = Form.useWatch("checkAll", form);

  useEffect(() => {
    selectAllChange(selectAll);
  }, [selectAll, selectAllChange]);

  function createNestedPathedValue(obj: any, prevArray: string[] = []) {
    let result: any[] = [];
    const keys = Object.keys(obj || {});
    for (const k of keys) {
      if (
        ["string", "number", "boolean", "undefined"].includes(typeof obj[k]) ||
        obj[k] === null
      ) {
        result.push({ name: [...prevArray].concat(k), value: obj[k] });
      } else {
        result.push(...createNestedPathedValue(obj[k], [...prevArray, k]));
      }
    }
    return result;
  }

  return (
    <div>
      <Button
        onClick={() => {
          const approvedFlagFieldsKeys = createNestedPathedValue(
            form.getFieldValue("approved")
          )
            ?.filter((f) => f.value === true)
            ?.map((f) => f.name as string[]);

          if (approvedFlagFieldsKeys?.length) {
            const resultData = deriveApprovedValues(
              approvedFlagFieldsKeys,
              form.getFieldsValue(true)
            );
            console.log({ resultData, formValues: form.getFieldsValue(true) });
            setApprovedFormFieldValues?.(resultData);
            onApprovedFormFieldValues?.(resultData);
          } else {
            setApprovedFormFieldValues?.({});
            onApprovedFormFieldValues?.({});
          }
        }}
      >
        Apply AI recommendation
      </Button>
      <div style={{ margin: "2rem 0 0.5rem" }}>
        <strong>Review the content:</strong>
      </div>
      <Form
        layout="horizontal"
        form={form}
        style={{
          maxHeight: "calc(100vh - 300px)",
          overflowY: "auto",
        }}
      >
        <Row>
          <Col span={2}>
            <Form.Item name="checkAll" valuePropName="checked">
              <Checkbox>All</Checkbox>
            </Form.Item>
          </Col>
          <Col span={22}></Col>
        </Row>
        <div style={{ display: "none" }}>
          <Form.Item name="hidden">
            <Input value="1" />
          </Form.Item>
        </div>
        {env !== null && renderFields(template?.fields)}
      </Form>
    </div>
  );
}

export default FormRenderer;
