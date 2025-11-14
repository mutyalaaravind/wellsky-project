import { ContextDocumentItemFilter } from "tableOfContentsTypes";
import {
  Configuration,
  DocumentFile,
  EvidenceInfo,
  Medication,
  pipelineStatus,
  SetStateLikeAction,
} from "types";

export interface NestedRecordObject {
  [key: string | number | symbol]:
    | string
    | number
    | undefined
    | boolean
    | null
    | Date
    | string[]
    | number[]
    | boolean[]
    | Date[]
    | Array<Date | string | number | undefined | boolean | null>
    | Array<NestedRecordObject>
    | NestedRecordObject;
}

export interface ClinicalData {
  // TODO: Add common fields here.
  date?: Date | null;
}

export interface ClinicalDataReference {
  clinicalDataId: string;
  documentId: string;
  pageNumber: number;
  evidenceMarkId?: string;
}

export interface ConditionEvidence {
  endPosition: number;
  startPosition: number;
  evidenceReference: Array<string>;
  evidenceSnippet: string;
  documentId: string;
  pageNumber: number;
  markerId: string;
}

export interface ConditionICD10Code {
  category: string;
  description: string;
  icdCode: string;
}

export interface Allergies {
  id: string;
  data: { substance: string; reaction: string; date: Date | null };
  references: ClinicalDataReference[];
}

export interface Immunizations {
  id: string;
  data: {
    name: string;
    status: "yes" | "no" | "unknown";
    date?: string | null;
    originalExtractedString: string | null;
  };
  references: ClinicalDataReference[];
}

export interface Classification {
  code: string;
  value: string;
}

export interface Condition {
  evidences: Array<ConditionEvidence>;
  icd10Codes: Array<ConditionICD10Code>;
  category: string;
}

type loadingStatuses =
  | "allergies"
  | "immunizations"
  | "medications"
  | "conditions"
  | "config"
  | "documents"
  | "medications_count"
  | "documents_status";

export type ProfileItem = {
  name: string;
};

export type PageProfile = {
  hasItems: boolean;
  numberOfItems: number;
  type: string;
  items: Array<ProfileItem>;
  isSelected?: boolean;
};

export interface PatientProfileState {
  hasMedicationUpdates?: boolean;
  allergies: Allergies[];
  immunizations: Immunizations[];
  conditions: Condition[];
  loading: Set<loadingStatuses>;
  config?: Configuration;
  medications: Medication[];
  cachedEvidences: Record<string, EvidenceInfo>;
  medicationClassifications: Classification[];
  documents: DocumentFile[];
  documentStatuses: Record<string, pipelineStatus>;
  pageProfiles?: PageProfile[];
  allPageProfiles: Map<
    string,
    Record<string | number, Record<number, PageProfile>>
  >;
  documentsInReview: DocumentFile[];
  pageProfileState: Record<string, ContextDocumentItemFilter>;
  pageOcrStatus: Record<string, Record<number, string>>;

  setAllergies: (
    allergies: SetStateLikeAction<PatientProfileState["allergies"]>,
  ) => void;
  setImmunizations: (
    immunizations: SetStateLikeAction<PatientProfileState["immunizations"]>,
  ) => void;
  setConditions: (
    conditions: SetStateLikeAction<PatientProfileState["conditions"]>,
  ) => void;
  setLoading: (
    loading: SetStateLikeAction<PatientProfileState["loading"]>,
  ) => void;
  updateLoading: (key: loadingStatuses, isLoading: boolean) => void;
  setMedications: (
    medications: SetStateLikeAction<PatientProfileState["medications"]>,
  ) => void;
  resetStore: () => void;
  setConfig: (
    config: SetStateLikeAction<PatientProfileState["config"]>,
  ) => void;
  setCachedEvidences: (id: string, data: EvidenceInfo) => void;
  setMedicationClassifications: (
    classifications: SetStateLikeAction<
      PatientProfileState["medicationClassifications"]
    >,
  ) => void;
  setDocuments: (
    documents: SetStateLikeAction<PatientProfileState["documents"]>,
  ) => void;
  setDocumentStatuses: (
    documentStatues: SetStateLikeAction<
      PatientProfileState["documentStatuses"]
    >,
  ) => void;
  setHasMedicationUpdates: (
    hasMedicationUpdates: SetStateLikeAction<
      PatientProfileState["hasMedicationUpdates"]
    >,
  ) => void;
  setPageProfiles: (
    pageProfiles: SetStateLikeAction<PatientProfileState["pageProfiles"]>,
  ) => void;
  setAllPageProfiles: (
    allPageProfiles: SetStateLikeAction<PatientProfileState["allPageProfiles"]>,
  ) => void;
  setDocumentsInReview: (
    documentsInReview: SetStateLikeAction<
      PatientProfileState["documentsInReview"]
    >,
  ) => void;
  setPageProfileState: (
    pageProfileState: SetStateLikeAction<
      PatientProfileState["pageProfileState"]
    >,
  ) => void;

  updatePageProfileState: (
    documentId: string,
    extractionType: string,
    pageNumber: number,
    pageProfileState: Partial<PageProfile>,
  ) => void;

  setPageOcrStatus: (
    documentId: string,
    pageNumber: number,
    status: string,
  ) => void;

  destroyStore: () => void;
}

// Define the validation rules type
export interface MedicationValidationRules {
  skipImportedValidation?: boolean;
  validateMedispanId?: boolean;
  validateClassification?: boolean;
  validateStatusReason?: boolean;
  validateDosage?: boolean;
  validateName?: boolean;
  validateDates?: boolean;
  errorMessages?: {
    medispanId?: string[];
    classification?: string[];
    statusReason?: string[];
    dosage?: string[];
    name?: string[];
    startDate?: string[];
    startDateWithEndDate?: string[];
  };
}
