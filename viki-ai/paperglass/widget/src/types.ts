export interface Env {
  API_URL: string
  VERSION: string
  FORMS_WIDGETS_HOST: string
  FORMS_API: string
  FORMS_API_KEY: string
}

export enum APIStatus {
  PROCESSING = 'PROCESSING',
  COMPLETED = 'COMPLETED',
  ERRORED = 'ERRORED'
}

export enum AnnotationType {
  LINE = "line",
  BLOCK = "block",
  PARAGRAPH = "paragraph",
  TOKEN = "token"
}

export interface SettingType {
  model: string;
  embeddingStatus: boolean;
  annotationType: AnnotationType
  formTemplateId: string;
  correction: number;
  confidenceThreshold: number;
  enableSearchGlass: boolean;
  enableDocumentVectorBasedSearch: boolean;
  documentVectorSearchThreshold: number;
  enableLBISearch: boolean;
}

export interface DocumentSettingsType {
  pageTextExtractionModel: string;
  pageTextExtractionModelType: number;
  pageClassificationModel: string;
  pageClassificationModelType: number;
  classificationBasedRetreivalModel: string;
  classificationBasedRetreivalModelType: number;
  evidenceLinkingModel: string;
  evidenceLinkingModelType: number;
}
