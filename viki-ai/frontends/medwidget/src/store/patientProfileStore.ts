import { useAuth } from "hooks/useAuth";
import { create } from "zustand";
import { devtools } from "zustand/middleware";
import { immer } from "zustand/middleware/immer";
import { enableMapSet } from "immer";
import { PatientProfileState } from "./storeTypes";
import InstanceManager from "utils/InstanceManager";
import { genericSetState } from "utils/helpers";
import { SetStateLikeAction } from "types";
import { useMemo } from "react";

enableMapSet();

const defaultState: Pick<
  PatientProfileState,
  | "allPageProfiles"
  | "allergies"
  | "immunizations"
  | "loading"
  | "conditions"
  | "config"
  | "medications"
  | "cachedEvidences"
  | "medicationClassifications"
  | "documents"
  | "documentStatuses"
  | "hasMedicationUpdates"
  | "pageProfiles"
  | "documentsInReview"
  | "pageProfileState"
  | "pageOcrStatus"
> = {
  allPageProfiles: new Map() as PatientProfileState["allPageProfiles"],
  pageProfiles: [] as PatientProfileState["pageProfiles"],
  config: {
    extractAllergies: false,
    extractImmunizations: false,
    extractConditions: false,
    extractionPersistedToMedicationProfile: true,
    usePagination: true,
    uiControlUploadEnable: false,
    enableOnDemandExternalFilesDownload: false,
    uiNonstandardDoseEnable: false,
    uiHideMedicationTab: false,
    uiDocumentActionExtractEnable: false,
    uiDocumentActionUpsertGoldenDatasetTestcaseEnable: false,
    useAsyncDocumentStatus: false,
    useClientSideFiltering: false,
    orchestrationEngineVersion: "v3",
    validationRules: null,
    ocrTriggerConfig: {
      enabled: false,
      touchPoints: {
        bubbleClick: false,
        evidenceLinkClick: false,
        pageClick: false,
      },
    },
    uiHostLinkedDeleteEnable: true,
    uiLongstandingEnable: true,
    uiClassificationEnable: true,
  },
  loading: new Set(),
  allergies: [] as PatientProfileState["allergies"],
  immunizations: [] as PatientProfileState["immunizations"],
  conditions: [] as PatientProfileState["conditions"],
  medications: [] as PatientProfileState["medications"],
  cachedEvidences: {} as PatientProfileState["cachedEvidences"],
  medicationClassifications:
    [] as PatientProfileState["medicationClassifications"],
  documents: [] as PatientProfileState["documents"],
  documentStatuses: {} as PatientProfileState["documentStatuses"],
  hasMedicationUpdates: false,
  documentsInReview: [] as PatientProfileState["documentsInReview"],
  pageProfileState: {} as PatientProfileState["pageProfileState"],
  pageOcrStatus: {} as PatientProfileState["pageOcrStatus"],
};

const storeGenerator = (patientId: string) =>
  create<
    PatientProfileState,
    [["zustand/devtools", never], ["zustand/immer", never]]
  >(
    devtools(
      immer(
        (set, get): PatientProfileState => ({
          ...defaultState,
          setAllergies: genericSetState<
            SetStateLikeAction<PatientProfileState["allergies"]>,
            PatientProfileState
          >("allergies", set, get),

          setImmunizations: genericSetState<
            SetStateLikeAction<PatientProfileState["immunizations"]>,
            PatientProfileState
          >("immunizations", set, get),

          setConditions: genericSetState<
            SetStateLikeAction<PatientProfileState["conditions"]>,
            PatientProfileState
          >("conditions", set, get),

          setLoading: genericSetState<
            SetStateLikeAction<PatientProfileState["loading"]>,
            PatientProfileState
          >("loading", set, get),

          updateLoading: (key, isLoading = true) => {
            set((state) => {
              if (isLoading) {
                state.loading.add(key);
              } else {
                state.loading.delete(key);
              }
            });
          },

          setConfig: genericSetState<
            SetStateLikeAction<PatientProfileState["config"]>,
            PatientProfileState
          >("config", set, get),

          setMedications: genericSetState<
            SetStateLikeAction<PatientProfileState["medications"]>,
            PatientProfileState
          >("medications", set, get),

          setCachedEvidences: (id, data) => {
            set((state) => {
              state.cachedEvidences[id] = data;
            });
          },

          setMedicationClassifications: genericSetState<
            SetStateLikeAction<
              PatientProfileState["medicationClassifications"]
            >,
            PatientProfileState
          >("medicationClassifications", set, get),

          setDocuments: genericSetState<
            SetStateLikeAction<PatientProfileState["documents"]>,
            PatientProfileState
          >("documents", set, get),

          setDocumentStatuses: genericSetState<
            SetStateLikeAction<PatientProfileState["documentStatuses"]>,
            PatientProfileState
          >("documentStatuses", set, get),

          setHasMedicationUpdates: genericSetState<
            SetStateLikeAction<PatientProfileState["hasMedicationUpdates"]>,
            PatientProfileState
          >("hasMedicationUpdates", set, get),

          setPageProfiles: genericSetState<
            SetStateLikeAction<PatientProfileState["pageProfiles"]>,
            PatientProfileState
          >("pageProfiles", set, get),

          setAllPageProfiles: genericSetState<
            SetStateLikeAction<PatientProfileState["allPageProfiles"]>,
            PatientProfileState
          >("allPageProfiles", set, get),

          setDocumentsInReview: genericSetState<
            SetStateLikeAction<PatientProfileState["documentsInReview"]>,
            PatientProfileState
          >("documentsInReview", set, get),

          setPageProfileState: genericSetState<
            SetStateLikeAction<PatientProfileState["pageProfileState"]>,
            PatientProfileState
          >("pageProfileState", set, get),

          updatePageProfileState: (
            documentId,
            extractionType,
            pageNumber,
            pageProfileState,
          ) => {
            set((state) => {
              const currentProfile =
                state.allPageProfiles.get(documentId) || {};
              const currentProfileValue =
                currentProfile?.[extractionType] || {};
              const currentProfilePageValue = {
                ...(currentProfileValue?.[pageNumber] || {}),
                ...pageProfileState,
              };

              currentProfileValue[pageNumber] = currentProfilePageValue;
              currentProfile[extractionType] = currentProfileValue;
              state.allPageProfiles.set(documentId, currentProfile);
            });
          },

          setPageOcrStatus: (documentId, pageNumber, status) => {
            set((state) => {
              state.pageOcrStatus[documentId] = {
                ...(state.pageOcrStatus[documentId] || {}),
                [pageNumber]: status,
              };
            });
          },

          resetStore: () => {
            set((state) => {
              for (const k of Object.keys(defaultState) as Array<
                keyof typeof defaultState
              >) {
                state[k] = defaultState[k] as any;
              }
            });
          },

          destroyStore: () => {
            storeManagerInstance.removeInstance(patientId);
          },
        }),
      ),
    ),
  );

const storeManagerInstance = new InstanceManager<
  ReturnType<typeof storeGenerator>
>();

export function usePatientProfileStore(): PatientProfileState;

export function usePatientProfileStore<T = any>(
  cb: (state: PatientProfileState) => T,
): T;

export function usePatientProfileStore(
  cb?: (state: PatientProfileState) => unknown,
) {
  const { patientId } = useAuth();
  if (!patientId) {
    throw new Error("Error binding patient");
  }

  const useStore = storeManagerInstance.getOrCreate(
    patientId + "patientProfileStore",
    () => storeGenerator(patientId),
  );

  const callBack = useMemo(() => cb, [cb]);

  if (!useStore) {
    throw new Error("Error creating store");
  }

  const store = useStore();

  return callBack ? callBack(store) : store;
}
