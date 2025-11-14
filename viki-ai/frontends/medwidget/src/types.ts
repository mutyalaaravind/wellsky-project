import { ReactNode } from "react";
import { MedicationValidationRules, PageProfile } from "store/storeTypes";
import MedWidgetInstance from "utils/MedWidgetInstance";

export interface Env {
  API_URL: string;
  VERSION: string;
  FORMS_WIDGETS_HOST: string;
  FORMS_API: string;
  FORMS_API_KEY: string;
  IS_UPLOAD_ENABLED: string;
  NEWRELIC_ACCOUNT_ID: string;
  NEWRELIC_TRUST_KEY: string;
  NEWRELIC_APPLICATION_ID: string;
  NEWRELIC_API_BROWSER_KEY: string;
}

export enum APIStatus {
  PROCESSING = "PROCESSING",
  COMPLETED = "COMPLETED",
  ERRORED = "ERRORED",
}

export enum AnnotationType {
  LINE = "line",
  BLOCK = "block",
  PARAGRAPH = "paragraph",
  TOKEN = "token",
}

export interface SettingType {
  model: string;
  embeddingStatus: boolean;
  annotationType: AnnotationType;
  formTemplateId: string;
  correction: number;
  confidenceThreshold: number;
  enableSearchGlass: boolean;
  enableDocumentVectorBasedSearch: boolean;
  documentVectorSearchThreshold: number;
  enableLBISearch: boolean;
}

export type ExtractedMedication = {
  documentId: string;
  extractedMedicationId: string;
  documentOperationInstanceId: string;
  pageNumber: number;
};

export type MedicationStatus = {
  status: string;
  statusReason: string;
  statusReasonExplaination: string;
};

export enum OriginType {
  EXTRACTED = "extracted",
  USER_ENTERED = "user_entered",
  IMPORTED = "imported",
}

export type Medication = {
  id: string;
  name: string;
  name_original: string;
  dosage: string;
  route: string;
  frequency: string;
  form: string;
  strength: string;
  instructions: string;
  extractedMedications: Array<ExtractedMedication>;
  startDate: string;
  endDate: string;
  discontinuedDate: string;
  deleted: boolean;
  //medispanMatchStatus: string;
  medicationStatus: MedicationStatus | null;
  evidences: Array<any>; //deprecated. we do on-demand evidence query
  modifiedBy: string | null;
  medicationType: string;
  classification?: string;
  hostLinked: boolean;
  isUnlisted: boolean;
  origin: OriginType;
  medispanId: string | null;
  isLongStanding?: boolean;
  isNonStandardDose?: boolean;
};

export type Configuration = {
  extractAllergies: boolean;
  extractImmunizations: boolean;
  extractConditions: boolean;
  extractionPersistedToMedicationProfile: boolean;
  usePagination: boolean;
  uiControlUploadEnable: boolean;
  uiNonstandardDoseEnable: boolean;
  uiHostLinkedDeleteEnable: boolean;
  uiLongstandingEnable: boolean;
  uiClassificationEnable: boolean;
  enableOnDemandExternalFilesDownload: boolean;
  uiHideMedicationTab: boolean;
  uiDocumentActionExtractEnable: boolean;
  uiDocumentActionUpsertGoldenDatasetTestcaseEnable: boolean;
  useAsyncDocumentStatus: boolean;
  useClientSideFiltering: boolean;
  orchestrationEngineVersion: string;
  validationRules?: MedicationValidationRules | null;
  ocrTriggerConfig: {
    enabled: boolean;
    touchPoints: {
      bubbleClick: boolean;
      evidenceLinkClick: boolean;
      pageClick: boolean;
    };
  };
};

export type EvidenceInfo = {
  documentId: string;
  pageNumber: number;
  annotations: Array<Coordinate>;
  // TODO: add more fields (coordinates, text?)
};

export type KeyOfMap<M extends Map<unknown, unknown>> =
  M extends Map<infer K, unknown> ? K : never;

export type PipeLineStatusEnums =
  | "NOT_STARTED"
  | "QUEUED"
  | "IN_PROGRESS"
  | "COMPLETED"
  | "FAILED"
  | "UNKNOWN";

export type PipleLineTypesEnums =
  | "MEDICATION_EXTRACTION"
  | "TOC"
  | "MEDICATION_GRADER";

// 'CANCELLED' | 'SKIPPED' | 'RETRYING' | 'RETRIED' | 'STOPPED' | 'PAUSED' | 'RESUMED' | 'SUSPENDED' | 'SUCCEEDED' | 'FAILED' | 'ABORTED' | 'TIMEOUT' | 'EXPIRED' | 'DELETED' | 'ARCHIVED' | 'PENDING' | 'REJECTED' | 'APPROVED' | 'REVIEW' | 'REVIEWED' | 'REVIEWING'

export interface DocumentFileApiResponse {
  created_at: string;
  app_id: string;
  embedding_strategy: number;
  id: string;
  page_count: number;
  embedding_chunking_strategy?: number;
  document_operation_instance_id?: string | null;
  execution_id: string | null;
  modified_at: string;
  active: boolean;
  pages: {
    number: number;
    storage_uri: string;
    mediabox: {
      tl: {
        y: number;
        x: number;
      };
      br: {
        y: number;
        x: number;
      };
    };
  }[];
  patient_id: string;
  tenant_id: string;
  source: "app" | string;
  token: string;
  modified_by?: string | null;
  storage_uri: string;
  file_name: string;
  created_by?: string | null;
  source_storage_uri?: string | null;
  status: {
    pipelineStatuses: {
      type: PipleLineTypesEnums;
      status: PipeLineStatusEnums;
      start_date: string | null;
      end_date: string | null;
      failed: number;
      details?: string;
    }[];
    status: PipeLineStatusEnums;
    failed: number;
  };
  priority?: "default" | "high" | "none";
  metadata?: { [key: string]: any };
}

export type SetStateLikeAction<T> = T | ((prevState: T) => T);

export type SetStateActionCallBack<TArg, TReturn = void> = (
  arg: SetStateLikeAction<TArg>,
) => TReturn;

export type PdfViewerContextType = {
  storeId: string | null;
  patientId: string | null;
  updatePageProfileState?: (
    documentId: string,
    extractionType: string,
    pageNumber: number,
    pageProfileState: Partial<PageProfile>,
  ) => void;
};

export type pipelineStatus = {
  type: PipleLineTypesEnums;
  status: PipeLineStatusEnums;
  start_date: string | null;
  end_date: string | null;
  failed: number;
  details?: string;
  progress?: number | null;
};

export type operationStatus = {
  medication_extraction: {
    orchestration_engine_version: string;
    status: string;
  };
};

export interface DocumentFile extends Partial<DocumentFileApiResponse> {
  id: string;
  created_at: string;
  file_name: string;
  page_count: number;
  status: {
    pipelineStatuses: pipelineStatus[];
    status: PipeLineStatusEnums;
    failed: number;
    progress?: number | null;
  };
  operation_status?: operationStatus;
  pdfUrl?: string;
  total_records?: number;
  metadata?: { [key: string]: any };
}

export type EventBusEvents =
  | "pdfViewer_documentLoaded"
  | "pdfViewer_pageLoaded"
  | "pdfViewer_pageRendered"
  | "pdfViewer_pageUnloaded"
  | "pdfViewer_documentUnloaded"
  | "pdfViewer_documentChanged"
  | "pdfViewer_pageChanged"
  | "pdfViewer_annotationCreated"
  | "pdfViewer_annotationUpdated"
  | "pdfViewer_annotationDeleted"
  | "pdfViewer_annotationSelected"
  | "pdfViewer_annotationDeselected"
  | "pdfViewer_annotationHovered"
  | "pdfViewer_annotationClicked"
  | "widgetReady"
  | "open"
  | "close"
  | "medication.save"
  | `medWidgetEvent-${string}`;

export type Coordinate = {
  x: number;
  y: number;
  width: number;
  height: number;
  text: string;
  page: number;
  orientation?: "PAGE_RIGHT" | "PAGE_DOWN" | "PAGE_LEFT" | "PAGE_UP";
};

export type Suggestion = {
  id?: string;
  generic_name?: string;
  brand_name?: string;
  route?: string;
  form?: string;
  strength?: {
    value?: string | number;
    unit?: string | number;
  };
  package?: {
    value?: string | number;
    unit?: string | number;
  };
};

export type MedicationFormFields =
  | "name"
  | "dosage"
  | "startDate"
  | "endDate"
  | "classification"
  | "medispanId"
  | "statusReason"
  | "strength"
  | "route"
  | "form"
  | "instructions"
  | "discontinuedDate";

export type validateFormType = () => {
  success: boolean;
  errors: string[];
  fieldWiseErrors?: Map<Partial<MedicationFormFields>, string[]> | undefined;
};

export type AnnotationRecord = {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  text: string;
  pageNumber: number;
  orientation?: Coordinate["orientation"];
};

export type MedWidgetInstanceContextType = {
  medWidgetInstance: MedWidgetInstance;
};

export interface MedWidgetInstanceConfig {
  enableUpload?: boolean;
  emptyMedicationListMessage?: ReactNode;
  emptyDocumentListMessage?: ReactNode;
}

export type MedicationResponse = {
  change_sets: any;
  deleted: boolean;
  extracted_medication_reference?: {
    document_id: string;
    document_operation_instance_id: string;
    extracted_medication_id: string;
    page_number: number;
  }[];
  host_linked: boolean;
  id: string;
  medication: {
    classification?: any;
    discontinued_date: string;
    dosage: string;
    end_date: string;
    form: string;
    frequency: string;
    instructions: string;
    medispan_id: string;
    name: string;
    name_original: string;
    route: string;
    start_date: string;
    strength: string;
    is_long_standing: boolean;
    is_nonstandard_dose: boolean;
  };
  medication_status: any;
  medispan_id: string;
  modified_by: any;
  origin: OriginType;
  unlisted: boolean;
};
