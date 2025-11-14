import {
  DocumentFile,
  ExtractedMedication,
  Medication,
  MedicationResponse,
  OriginType,
  SetStateLikeAction,
} from "types";
import InstanceManager from "./InstanceManager";
import { MedicationValidationRules } from "store/storeTypes";

// Default validation rules based on existing logic
const defaultValidationRules: MedicationValidationRules = {
  skipImportedValidation: true,
  validateMedispanId: true,
  validateClassification: true,
  validateStatusReason: true,
  validateDosage: true,
  validateName: true,
  validateDates: true,
  errorMessages: {
    medispanId: [
      "Please either select unlisted or search and select medication.",
    ],
    classification: ["Classification is missing."],
    statusReason: [
      "Please fill/update the reason for none of the above status. If already filled, please ignore",
    ],
    dosage: ["Amount/Dose is missing."],
    name: ["Medication name is missing."],
    startDate: ["Start Date is missing."],
    startDateWithEndDate: ["Start Date is required if End Date is provided"],
  },
};

/**
 * Validates a medication object based on the provided validation rules.
 *
 * @param {Medication} medication - The medication object to validate.
 * @param {MedicationValidationRules} [rules=defaultValidationRules] - The validation rules to apply.
 *   The `MedicationValidationRules` type includes the following properties:
 *   - `skipImportedValidation` (boolean): Whether to skip validation for imported medications.
 *   - `validateMedispanId` (boolean): Whether to validate the Medispan ID.
 *   - `validateClassification` (boolean): Whether to validate the classification.
 *   - `validateStatusReason` (boolean): Whether to validate the status reason.
 *   - `validateDosage` (boolean): Whether to validate the dosage.
 *   - `validateName` (boolean): Whether to validate the medication name.
 *   - `validateDates` (boolean): Whether to validate the start and end dates.
 *   - `errorMessages` (object): Custom error messages for validation failures, with keys corresponding
 *     to the fields being validated (e.g., `medispanId`, `classification`, `statusReason`, etc.).
 * @returns {Object} An object containing the validation result:
 *   - `success` (boolean): Whether the validation passed.
 *   - `errors` (string[]): A list of error messages, if any.
 */
export function validateMedication(
  medication: Medication,
  rules: MedicationValidationRules | null = defaultValidationRules,
) {
  const validationRules = rules || defaultValidationRules;
  const errors: string[] = [];
  const fieldWiseErrors = new Map() as Map<
    Partial<
      | Extract<
          keyof Medication,
          | "classification"
          | "dosage"
          | "name"
          | "startDate"
          | "endDate"
          | "medispanId"
        >
      | "statusReason"
    >,
    string[]
  >;

  // Skip validation for imported medications if configured
  if (
    validationRules.skipImportedValidation &&
    medication?.origin === OriginType.IMPORTED
  ) {
    return {
      success: true,
      errors,
    };
  }

  // Validate medispanId
  if (
    validationRules.validateMedispanId &&
    !medication?.isUnlisted &&
    !medication?.medispanId
  ) {
    const err = validationRules.errorMessages?.medispanId || [
      "Please either select unlisted or search and select medication.",
    ];
    errors.push(...err);
    fieldWiseErrors.set("medispanId", err);
  }

  // Validate classification for unlisted medications
  if (
    validationRules.validateClassification &&
    medication?.isUnlisted &&
    !medication?.classification?.trim()
  ) {
    const err = validationRules.errorMessages?.classification || [
      "Classification is missing.",
    ];
    errors.push(...err);
    fieldWiseErrors.set("classification", err);
  }

  // Validate status reason
  if (
    validationRules.validateStatusReason &&
    medication?.medicationStatus?.statusReason === "other" &&
    !medication?.medicationStatus?.statusReason
  ) {
    const err = validationRules.errorMessages?.statusReason || [
      "Please fill/update the reason for none of the above status. If already filled, please ignore",
    ];
    errors.push(...err);
    fieldWiseErrors.set("statusReason", err);
  }

  // Validate dosage
  if (
    validationRules.validateDosage &&
    !medication?.isUnlisted &&
    !medication?.isNonStandardDose &&
    !medication?.dosage?.trim()
  ) {
    const err = validationRules.errorMessages?.dosage || [
      "Amount/Dose is missing.",
    ];
    errors.push(...err);
    fieldWiseErrors.set("dosage", err);
  }

  // Validate name
  if (validationRules.validateName && !medication?.name?.trim()) {
    const err = validationRules.errorMessages?.name || [
      "Medication name is missing.",
    ];
    errors.push(...err);
    fieldWiseErrors.set("name", err);
  }

  // Validate dates
  if (validationRules.validateDates && !Boolean(medication?.isLongStanding)) {
    if (!medication?.startDate) {
      const err = validationRules.errorMessages?.startDate || [
        "Start Date is missing.",
      ];
      errors.push(...err);
      fieldWiseErrors.set("startDate", err);
    }

    if (!medication?.startDate && medication?.endDate) {
      const err = validationRules.errorMessages?.startDateWithEndDate || [
        "Start Date is required if End Date is provided",
      ];
      errors.push(...err);
      fieldWiseErrors.set("startDate", err);
    }
  }

  return {
    success: errors.length === 0,
    errors,
    fieldWiseErrors,
  };
}

export const mapDocumentToShortKey = (
  document_id: string,
  documentsInReview: DocumentFile[],
) => {
  let alphabet = "Z";
  documentsInReview.forEach((document, index) => {
    if (document.id === document_id) {
      alphabet = (index + 1 + 9).toString(36).toUpperCase();
    }
  });
  return alphabet;
};

export const groupByDocument = (
  extractedMedications: Array<ExtractedMedication>,
  documentsInReview: DocumentFile[],
): Record<string, Array<ExtractedMedication>> => {
  let groupByDocuments: Record<string, Array<any>> = {};
  if (extractedMedications && extractedMedications?.length === 0)
    return groupByDocuments;
  extractedMedications?.forEach((element) => {
    groupByDocuments[
      mapDocumentToShortKey(element.documentId, documentsInReview)
    ] = [
      ...(groupByDocuments[
        mapDocumentToShortKey(element.documentId, documentsInReview)
      ] || []),
      element,
    ];
  });
  return groupByDocuments;
};

export const genericSetState = <TVal, TStore>(
  key: keyof TStore,
  set: (fn: (state: TStore) => any) => any,
  get: () => TStore,
) => {
  return (val: TVal) => {
    set((state: TStore) => {
      if (typeof val === "function") {
        state[key] = val((get() as TStore)[key]);
      } else {
        state[key] = val as TStore[keyof TStore];
      }
    });
  };
};

export const genericSetStateV2 = <TStore, TKey extends keyof TStore>(
  key: TKey,
  set: (fn: (state: TStore) => any) => any,
  get: () => TStore,
) => {
  return (val: SetStateLikeAction<TStore[TKey]>) => {
    set((state: TStore) => {
      if (typeof val === "function") {
        state[key] = (val as (prevState: TStore[TKey]) => TStore[TKey])(
          (get() as TStore)[key],
        );
      } else {
        state[key] = val;
      }
    });
  };
};

export function getDocumentTabLabel(fileName: string, index: number) {
  return `${fileName.substring(0, 10)}.. [${(index + 1 + 9).toString(36).toUpperCase()}]`;
}

export const positiveModulo = (dividend: number, divisor: number) =>
  ((dividend % divisor) + divisor) % divisor;

export const getSingletonInstance = <TInstance,>(
  instanceId: string,
  instanceCreator: () => TInstance,
) => {
  const instanceManager = new InstanceManager<TInstance>();
  return instanceManager.getOrCreate(instanceId, instanceCreator);
};

export const getInstructions = (medication: MedicationResponse) => {
  const { instructions, frequency } = medication.medication;

  const instructionsWords = instructions?.split(/\s+/) || [];
  const frequencyWords = frequency?.split(/\s+/) || [];
  const isSubset = frequencyWords.every((word) =>
    instructionsWords.includes(word),
  );

  if (
    instructions?.toLowerCase()?.trim() === frequency?.toLowerCase()?.trim() ||
    isSubset
  ) {
    return instructions;
  }

  return [instructions, instructions?.trim() && frequency?.trim()].join(" ");
};

export const getNameOriginal = (med: MedicationResponse): string => {
  const originalMedication =
    med.medication.name_original !== null
      ? med.medication.name_original
      : med.medication.name;
  return originalMedication;
};
