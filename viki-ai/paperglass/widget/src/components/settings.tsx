
import { Badge, Checkbox, LinkButton, Popover, Select } from "@mediwareinc/wellsky-dls-react";
import { SettingOutlined } from "@ant-design/icons/lib/icons";
import { Switch } from 'antd';
import { Box, Divider, Grid, Input, NumberDecrementStepper, NumberIncrementStepper, NumberInput, NumberInputField, NumberInputStepper, PopoverArrow, PopoverBody, PopoverCloseButton, PopoverContent, PopoverHeader, PopoverTrigger, Radio, RadioGroup, Stack, StepSeparator, Text } from "@chakra-ui/react";
import React, { useEffect } from "react";
import { AnnotationType, DocumentSettingsType, Env } from "../types";
import { SettingType } from "../types";
import { useSettingsApi } from "../hooks/useSettings";



type SettingsProps = {
    onSettingsChange: (settings: SettingType) => void;
}

export const DefaultSettings: SettingType = {
    model: "text-bison-32k@002",
    embeddingStatus: true,
    annotationType: AnnotationType.LINE,
    formTemplateId: "REFERRAL_INTAKE",
    correction: 0.00,
    confidenceThreshold: 0.7,
    enableSearchGlass: false,
    enableDocumentVectorBasedSearch: false,
    documentVectorSearchThreshold: 0.65,
    enableLBISearch: false, // TODO: Change to false?
}

const DocumentSettingsDefault: DocumentSettingsType = {
    pageTextExtractionModel: "gemini-1.5-flash-preview-0514",
    pageClassificationModelType: 1,
    pageClassificationModel: "gemini-1.5-flash-preview-0514",
    pageTextExtractionModelType: 1,
    classificationBasedRetreivalModel: "gemini-1.5-flash-preview-0514",
    classificationBasedRetreivalModelType: 1,
    evidenceLinkingModel: "gemini-1.5-flash-preview-0514",
    evidenceLinkingModelType: 1
}

const DocumentSetting = (props: { modelType: number, model: string, setModelType: any, setModel: any }) => {
    const { modelType, model, setModelType, setModel } = props;
    return <>
        <Box>
            <Box>
                <RadioGroup defaultValue={"0"} value={modelType?.toString()} onChange={(e: string) => { setModelType(parseInt(e)) }} >
                    <Stack direction="row">
                        <Radio value={"0"}>Language</Radio>
                        <Radio value={"1"}>MultiModal</Radio>
                    </Stack>
                </RadioGroup>
            </Box>
            <Box>
                {modelType === 0 && <Select onChange={(e: any) => { setModel(e.target.value); }} value={model}>
                    <option value="text-bison-32k@002">Text Bison 32 K</option>
                </Select>}
                {modelType === 1 && <Select onChange={(e: any) => { setModel(e.target.value); }} value={model}>
                    <option value="gemini-1.5-flash-preview-0514">gemini-1.5-flash-preview-0514</option>
                    <option value="gemini-1.5-pro-preview-0409">gemini-1.5-pro-preview-0409</option>
                </Select>}
            </Box>
        </Box>
    </>
}

export const SettingsComponent = (props: { onSettingsChange: (settings: SettingType) => void, patientId: string, env: Env }) => {
    const { patientId, onSettingsChange, env } = props;
    const [model, setModel] = React.useState<string>("text-bison-32k@002") //["text-bison-32k@002", "medlm-medium", "medlm-large", "gemini-pro"
    const [embeddingStatus, setEmbeddingStatus] = React.useState<boolean>(false);
    const [annotationType, setAnnotationType] = React.useState<AnnotationType>(AnnotationType.LINE) //["line", "block", "paragraph", "token"
    const [formTemplateId, setFormtemplateId] = React.useState<string>("REFERRAL_INTAKE");
    const [settings, setSettings] = React.useState<SettingType>(DefaultSettings);
    const [correction, setCorrection] = React.useState<number>(0);
    const [confidenceThreshold, setConfidenceThreshold] = React.useState<number>(0.7);
    const [enableSearchGlass, setEnableSearchGlass] = React.useState<boolean>(false);
    const [enableDocumentVectorBasedSearch, setEnableDocumentVectorBasedSearch] = React.useState<boolean>(false);
    const [documentVectorSearchThreshold, setDocumentVectorSearchThreshold] = React.useState<number>(0.65);
    const [enableLBISearch, setEnableLBISearch] = React.useState<boolean>(DefaultSettings.enableLBISearch);

    const [pageTextExtractionModel, setPageTextExtractionModel] = React.useState<string>(DocumentSettingsDefault.pageTextExtractionModel);
    const [pageTextExtractionModelType, setPageTextExtractionModelType] = React.useState<number>(DocumentSettingsDefault.pageTextExtractionModelType);

    const [pageClassificationModel, setPageClassificationModel] = React.useState<string>(DocumentSettingsDefault.pageClassificationModel);
    const [pageClassificationModelType, setPageClassificationModelType] = React.useState<number>(DocumentSettingsDefault.pageClassificationModelType);

    const [classificationBasedRetreivalModel, setClassificationBasedRetreivalModel] = React.useState<string>(DocumentSettingsDefault.classificationBasedRetreivalModel);
    const [classificationBasedRetreivalModelType, setClassificationBasedRetreivalModelType] = React.useState<number>(DocumentSettingsDefault.classificationBasedRetreivalModelType);

    const [evidenceLinkingModel, setEvidenceLinkingModel] = React.useState<string>(DocumentSettingsDefault.evidenceLinkingModel);
    const [evidenceLinkingModelType, setEvidenceLinkingModelType] = React.useState<any>(DocumentSettingsDefault.evidenceLinkingModelType);

    const { docSettings, getDocumentSettings, setDocumentSettings } = useSettingsApi(env);

    useEffect(() => {
        console.log("settings changed", settings);
        onSettingsChange(settings);
    }, [settings]);

    useEffect(() => {
        setSettings({
            model: model, embeddingStatus: embeddingStatus,
            annotationType: annotationType,
            formTemplateId: formTemplateId,
            correction: correction,
            confidenceThreshold: confidenceThreshold,
            enableSearchGlass: enableSearchGlass,
            enableDocumentVectorBasedSearch: enableDocumentVectorBasedSearch,
            documentVectorSearchThreshold: documentVectorSearchThreshold,
            enableLBISearch: enableLBISearch,
        });
    }, [model, embeddingStatus, annotationType, formTemplateId, correction, confidenceThreshold, enableSearchGlass, enableDocumentVectorBasedSearch, documentVectorSearchThreshold, enableLBISearch])

    useEffect(() => {
        setDocumentSettings(patientId, { pageTextExtractionModel, pageTextExtractionModelType, pageClassificationModel, pageClassificationModelType, classificationBasedRetreivalModel, classificationBasedRetreivalModelType, evidenceLinkingModel, evidenceLinkingModelType })
    }, [pageClassificationModel, pageClassificationModelType, pageTextExtractionModel, pageTextExtractionModelType, classificationBasedRetreivalModel, classificationBasedRetreivalModelType, evidenceLinkingModel, evidenceLinkingModelType])

    return (
        <Box paddingTop={5}>
            <div style={{ float: 'right', justifyItems: 'baseline', zIndex: 9999 }}>
                <Popover title="Settings" content={(
                    <Box>
                        <Box>
                            <Box>Select the Model:</Box>
                            <Box>
                                <Select onChange={(e: any) => { setModel(e.target.value); }} value={model}>
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
                                <Switch checked={embeddingStatus} onChange={(e: any) => { setEmbeddingStatus(e) }} />
                            </Box>
                        </Box>
                        <Box>
                            <Box>Annotation Type:</Box>
                            <Box>
                                <Select onChange={(e: any) => { setAnnotationType(e.target.value); }} value={annotationType}>
                                    <option value="line">Line</option>
                                    <option value="block">Block</option>
                                    <option value="paragraph">Paragraph</option>
                                    <option value="token">Token</option>
                                </Select>
                            </Box>
                        </Box>
                        <Box>
                            <Box>Form template Name:</Box>
                            <Box>
                                <Input onChange={(e: any) => setFormtemplateId(e.target.value)} value={formTemplateId} />
                            </Box>
                        </Box>
                        <Box>
                            <Box>Annotation Correction:</Box>
                            <Box>
                                <Input onChange={(e: any) => setCorrection(e.target.value)} value={correction} />
                            </Box>
                        </Box>
                        <Box>
                            <Box>Annotation Confidence Threshold:</Box>
                            <Box>
                                <Input onChange={(e: any) => setConfidenceThreshold(e.target.value)} value={confidenceThreshold} />
                            </Box>
                        </Box>
                        <Box>
                            <Box>Enable SearchGlass</Box>
                            <Box>
                                <Switch checked={enableSearchGlass} onChange={(e: any) => { setEnableSearchGlass(e) }} />
                            </Box>
                        </Box>
                        <Box>
                            <Box>Enable Documents Vector Based Search</Box>
                            <Box>
                                <Switch checked={enableDocumentVectorBasedSearch} onChange={(e: any) => { setEnableDocumentVectorBasedSearch(e) }} />
                            </Box>
                        </Box>
                        {enableDocumentVectorBasedSearch && <Box>
                            <Box>Document Vector Search Threshold:</Box>
                            <Box>
                                <Input value={documentVectorSearchThreshold} onChange={(e: any) => { setDocumentVectorSearchThreshold(e.target.value) }} />
                            </Box>
                        </Box>}
                        <Box>
                            <Box>Enable LBI search</Box>
                            <Box>
                                <Switch checked={enableLBISearch} onChange={(e: any) => { setEnableLBISearch(e) }} />
                            </Box>
                        </Box>
                        <Box paddingTop={5}>
                            <Divider />
                        </Box>
                        <Box>
                            <Box>Page Text Extraction Model</Box>
                            <Box><DocumentSetting model={pageTextExtractionModel} modelType={pageTextExtractionModelType} setModel={setPageTextExtractionModel} setModelType={setPageTextExtractionModelType} /></Box>
                        </Box>
                        <Box>
                            <Box>Page Classification Model</Box>
                            <Box><DocumentSetting model={pageClassificationModel} modelType={pageClassificationModelType} setModel={setPageClassificationModel} setModelType={setPageClassificationModelType} /></Box>
                        </Box>
                        <Box>
                            <Box>Classification Based Retreival Model</Box>
                            <Box><DocumentSetting model={classificationBasedRetreivalModel} modelType={classificationBasedRetreivalModelType} setModel={setClassificationBasedRetreivalModel} setModelType={setClassificationBasedRetreivalModelType} /></Box>
                        </Box>
                        <Box>
                            <Box>Evidence Linking Model</Box>
                            <Box><DocumentSetting model={evidenceLinkingModel} modelType={evidenceLinkingModelType} setModel={setEvidenceLinkingModel} setModelType={setEvidenceLinkingModelType} /></Box>
                        </Box>
                    </Box>
                )} trigger="click">
                    <PopoverTrigger>
                        <LinkButton><SettingOutlined /></LinkButton>
                    </PopoverTrigger>
                </Popover>
            </div>
        </Box>
    )

}
