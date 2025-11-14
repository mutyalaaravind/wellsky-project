import { AuthContext } from "context/AuthContext";
import { useCallback, useContext, useEffect, useState } from "react";
import {
  AnnotationRecord,
  Coordinate,
  DocumentFile,
  EvidenceInfo,
  ExtractedMedication,
  Medication,
  MedicationResponse,
  Suggestion,
} from "types";
import { ContextDocumentItemFilter } from "tableOfContentsTypes";
import { usePatientProfileStore } from "store/patientProfileStore";
import { Classification } from "store/storeTypes";
import { useMedWidgetInstanceContext } from "context/MedWidgetInstanceContext";
import { getInstructions, getNameOriginal } from "utils/helpers";
import { useConfigData } from "context/AppConfigContext";

export const medicationFields = [
  "name",
  "dosage",
  "frequency",
  "route",
  "reason",
  "start_date",
  "end_date",
  "medication_status",
  "medication_status_reason",
  "medication_status_reason_explaination",
];

export const medicationFieldsLayout = [
  ["name"],
  ["dosage", "frequency", "route"],
  ["reason"],
  ["start_date", "end_date"],
  ["medication_status"],
  ["medication_status_reason"],
  ["medication_status_reason_explaination"],
];

export type MedicationsApiHookParams = {
  apiRoot: string;
  patientId: string;
  documentsInReview: DocumentFile[] | null;
};

export type MedicationsApiHook = {
  // TODO: Define the medication type?
  medications: Medication[];
  busy: boolean;
  error: Error | null;
  refreshMedications: () => Promise<any>;
  refreshMedicationsV2: (ignoreCache?: boolean) => Promise<any>;
  refreshMedicationsV4: (ignoreCache?: boolean) => Promise<any>;
  createMedication: (documentId: string, medication: any) => Promise<any>;
  createMedicationV2: (documentId: string, medication: any) => Promise<any>;
  updateMedication: (id: string, medication: any) => Promise<any>;
  updateMedicationV2: (
    id: string,
    medication: any,
    changedValues: any,
    documentId: string,
  ) => Promise<any>;
  deleteMedication: (id: string) => Promise<any>;
  deleteMedicationV2: (
    id: string,
    currentMed: any,
    documentId: string,
  ) => Promise<any>;
  searchMedications: (
    term: string,
    signal?: AbortSignal,
  ) => Promise<Suggestion[]>;
  undeleteMedication: (id: string) => Promise<any>;
  undeleteMedicationV2: (id: string) => Promise<any>;
  getEvidence: (id: string) => Promise<EvidenceInfo>;
  getEvidenceV2: (
    id: string,
    signal?: AbortSignal,
    promiseSignal?: AbortSignal,
  ) => Promise<EvidenceInfo>;
  getEvidenceV4: (
    id: string,
    signal?: AbortSignal,
    promiseSignal?: AbortSignal,
  ) => Promise<EvidenceInfo>;
  getEvidenceForGroupedMedications: (medication: any) => Promise<EvidenceInfo>;
  getExtractedMedicationV2: (extractedMedicationId: string) => Promise<any>;
  importMedications: () => Promise<any>;
  updateHostMedicationsV2: (
    profileFilter: Record<string, ContextDocumentItemFilter>,
    medications: Array<Medication>,
  ) => Promise<any>;
  updateHostMedicationsResult: {
    errored_medications?: {
      medication: { id: string; [key: string]: string };
    }[];
    success_medications?: {
      medication: { id: string; [key: string]: string };
    }[];
    error?: string;
  } | null;
  getClassificationV2: () => Promise<{ code: string; value: string }[]>;
  medicationClassifications: Classification[];
  setUpdateHostMedicationsResult: (result: any) => void;
};

export const getMedicationStatuses = () => {
  return [
    { text: "Relevant - Current", value: "current" },
    { text: "Relevant - Past", value: "past" },
    { text: "Relevant - Unknown", value: "unknown" },
    { text: "Not Relevant", value: "not_relevant" },
  ];
};

export const getMedicationStatusReasons = (medicationStatus: string) => {
  if (medicationStatus?.toLowerCase() === "past") {
    return [
      { text: "Discontinued", value: "discontinued" },
      { text: "Finite range", value: "finite_range" },
      { text: "Administration record", value: "admin_record" },
      { text: "Other", value: "other" },
    ];
  }
  if (medicationStatus?.toLowerCase() === "not_relevant") {
    return [
      { text: "Allergy", value: "allergy" },
      { text: "Instructional", value: "instructional" },
      { text: "Other", value: "other" },
    ];
  }
  return [];
};

const localCache = new Map<string, any>();

const useLocalRefreshLogic = false;

export const useMedicationsApi = ({
  apiRoot,
  patientId,
  documentsInReview,
}: MedicationsApiHookParams): MedicationsApiHook => {
  const [error, setError] = useState<Error | null>(null);
  const {
    loading,
    medications,
    setMedications,
    updateLoading,
    medicationClassifications,
    setMedicationClassifications,
    setHasMedicationUpdates,
  } = usePatientProfileStore();

  const config = useConfigData();
  const { medWidgetInstance } = useMedWidgetInstanceContext();
  const [updateHostMedicationsResult, setUpdateHostMedicationsResult] =
    useState<MedicationsApiHook["updateHostMedicationsResult"]>(
      null,
      //   // Example result
      //   {
      //   errored_medications: [
      //     { medication: { id: "1", name: "med1" } },
      //     { medication: { id: "2", name: "med1" } },
      //     // { medication: { id: "3", name: "med1" } },
      //   ],
      //   success_medications: [
      //     { medication: { id: "4", name: "med1" } },
      //     { medication: { id: "5", name: "med1" } },
      //     { medication: { id: "6", name: "med1" } },
      //   ],
      // }
    );
  const authContext = useContext(AuthContext);
  const token = authContext.token;
  const oktaToken = authContext.oktaToken;
  const ehrToken = authContext.ehrToken;

  const refreshMedications = useCallback(() => {
    if (!documentsInReview) {
      return Promise.resolve([]);
    }

    let promise: Promise<any>;
    updateLoading("medications", true);

    const documentIds = documentsInReview.map((doc) => doc.id).join(",");
    promise = fetch(
      `${apiRoot}/api/medications_by_documents?documentIds=${documentIds}`,
      { headers: { Authorization: "Bearer " + token } },
    )
      .then((response) => response.json())
      .then((data) => {
        return data;
      });
    // promise = fetch(`${apiRoot}/api/get_medications_grouped?documentIds=${documentIds}`, { headers: { 'Authorization': 'Bearer ' + token } })
    //   .then((response) => response.json())
    //   .then((data) => {
    //     console.log('Got named entities:', data);
    //     return data;
    //   })

    return promise
      .then((medications) => {
        setMedications(
          medications?.map((med: any) => {
            // construct new class with this object which contains
            // methods of validations and other class methods like
            // isUnlisted, getMedicationSource
            return med;
          }),
        );
        setError(null);
        return medications;
      })
      .catch(setError)
      .finally(() => {
        updateLoading("medications", false);
      });
  }, [apiRoot, documentsInReview, setMedications, token, updateLoading]);

  const refreshMedicationsV2 = useCallback(
    async (ignoreCache = false) => {
      if (!documentsInReview) {
        return Promise.resolve([]);
      }

      let promise: Promise<any>;
      updateLoading("medications", true);

      try {
        const documentIds = documentsInReview.map((doc) => doc.id).join(",");
        const makeApiCall = async () => {
          promise = fetch(
            `${apiRoot}/api/v2/medications_by_documents?documentIds=${documentIds}`,
            {
              headers: {
                Authorization: "Bearer " + token,
                "okta-token": oktaToken,
                "ehr-token": ehrToken,
              },
            },
          );
          const res: Response = await promise;

          if (!res.ok) {
            throw new Error(res.statusText);
          }

          const resp = (await res.json()) as Array<MedicationResponse>;
          localCache.set(documentIds, resp);
          return resp;
        };

        const fromCache = localCache.get(documentIds);

        const response = ignoreCache
          ? await makeApiCall()
          : fromCache || (await makeApiCall());

        const medications = response?.map(
          (med: MedicationResponse): Medication => {
            // construct new class with this object which contains
            // methods of validations and other class methods like
            // isUnlisted, getMedicationSource

            const extractedMedicationRefs: Array<ExtractedMedication> = [];

            med?.extracted_medication_reference?.forEach(
              (extracted_medication_ref: any) => {
                extractedMedicationRefs.push({
                  documentId: extracted_medication_ref.document_id,
                  extractedMedicationId:
                    extracted_medication_ref.extracted_medication_id,
                  documentOperationInstanceId:
                    extracted_medication_ref.document_operation_instance_id,
                  pageNumber: extracted_medication_ref.page_number,
                });
              },
            );

            const medication: Medication = {
              id: med.id,
              name: med.medication.name,
              name_original: getNameOriginal(med),
              dosage: med.medication.dosage,
              route: med.medication.route,
              frequency: med.medication.frequency,
              form: med.medication.form,
              strength: med.medication.strength,
              instructions: getInstructions(med),
              extractedMedications: extractedMedicationRefs,
              startDate: med.medication.start_date,
              endDate: med.medication.end_date,
              discontinuedDate: med.medication.discontinued_date,
              deleted: med.deleted,
              medicationStatus: med.medication_status,
              evidences: [],
              modifiedBy: med.modified_by,
              medicationType: "", // deprecated
              classification: med.medication.classification,
              hostLinked: med.host_linked,
              isUnlisted: med.unlisted,
              origin: med.origin,
              medispanId: med.medispan_id,
              isLongStanding: med.medication.is_long_standing,
              isNonStandardDose: med.medication.is_nonstandard_dose,
            };

            return medication;
          },
        );

        setMedications(medications);
        setError(null);

        return medications;
      } catch (error: Error | any) {
        setError(error);
      } finally {
        updateLoading("medications", false);
      }

      // promise = fetch(`${apiRoot}/api/get_medications_grouped?documentIds=${documentIds}`, { headers: { 'Authorization': 'Bearer ' + token } })
      //   .then((response) => response.json())
      //   .then((data) => {
      //     console.log('Got named entities:', data);
      //     return data;
      //   })
    },
    [
      documentsInReview,
      updateLoading,
      apiRoot,
      token,
      oktaToken,
      ehrToken,
      setMedications,
    ],
  );

  const refreshMedicationsV4 = useCallback(
    async (ignoreCache = false) => {
      if (!documentsInReview) {
        return Promise.resolve([]);
      }

      let promise: Promise<any>;
      updateLoading("medications", true);

      try {
        const documentIds = documentsInReview.map((doc) => doc.id).join(",");
        const documentVersions:Record<string, string> = {};
        console.log("documentsInReview", documentsInReview);
        const docVersions = documentsInReview.map((doc) => {
          documentVersions[doc.id] = doc?.operation_status?.["medication_extraction"]?.orchestration_engine_version || "v3";
          return doc?.operation_status?.["medication_extraction"]?.orchestration_engine_version || "v3";
        });
        console.log(docVersions, documentVersions);
        const makeApiCall = async () => {
          promise = fetch(
            `${apiRoot}/api/v4/medications_by_documents?documentVersions=${JSON.stringify(documentVersions)}`,
            {
              headers: {
                Authorization: "Bearer " + token,
                "okta-token": oktaToken,
                "ehr-token": ehrToken,
              },
              //body: JSON.stringify({ documentVersions }),
            },
          );
          const res: Response = await promise;

          if (!res.ok) {
            throw new Error(res.statusText);
          }

          const resp = (await res.json()) as Array<MedicationResponse>;
          localCache.set(documentIds, resp);
          return resp;
        };

        const fromCache = localCache.get(documentIds);

        const response = ignoreCache
          ? await makeApiCall()
          : fromCache || (await makeApiCall());

        const medications = response?.map(
          (med: MedicationResponse): Medication => {
            // construct new class with this object which contains
            // methods of validations and other class methods like
            // isUnlisted, getMedicationSource

            const extractedMedicationRefs: Array<ExtractedMedication> = [];

            med?.extracted_medication_reference?.forEach(
              (extracted_medication_ref: any) => {
                extractedMedicationRefs.push({
                  documentId: extracted_medication_ref.document_id,
                  extractedMedicationId:
                    extracted_medication_ref.extracted_medication_id,
                  documentOperationInstanceId:
                    extracted_medication_ref.document_operation_instance_id,
                  pageNumber: extracted_medication_ref.page_number,
                });
              },
            );

            const medication: Medication = {
              id: med.id,
              name: med.medication.name,
              name_original: getNameOriginal(med),
              dosage: med.medication.dosage,
              route: med.medication.route,
              frequency: med.medication.frequency,
              form: med.medication.form,
              strength: med.medication.strength,
              instructions: getInstructions(med),
              extractedMedications: extractedMedicationRefs,
              startDate: med.medication.start_date,
              endDate: med.medication.end_date,
              discontinuedDate: med.medication.discontinued_date,
              deleted: med.deleted,
              medicationStatus: med.medication_status,
              evidences: [],
              modifiedBy: med.modified_by,
              medicationType: "", // deprecated
              classification: med.medication.classification,
              hostLinked: med.host_linked,
              isUnlisted: med.unlisted,
              origin: med.origin,
              medispanId: med.medispan_id,
              isLongStanding: med.medication.is_long_standing,
              isNonStandardDose: med.medication.is_nonstandard_dose,
            };

            return medication;
          },
        );
        
        console.log("medications_by_documents response", medications);
        setMedications(medications);
        setError(null);

        return medications;
      } catch (error: Error | any) {
        setError(error);
      } finally {
        updateLoading("medications", false);
      }

      // promise = fetch(`${apiRoot}/api/get_medications_grouped?documentIds=${documentIds}`, { headers: { 'Authorization': 'Bearer ' + token } })
      //   .then((response) => response.json())
      //   .then((data) => {
      //     console.log('Got named entities:', data);
      //     return data;
      //   })
    },
    [
      documentsInReview,
      updateLoading,
      apiRoot,
      token,
      oktaToken,
      ehrToken,
      setMedications,
    ],
  );

  const createMedication = useCallback(
    (documentId: string, medication: any) => {
      let promise: Promise<any>;
      updateLoading("medications", true);
      let values: any = {};
      medicationFields.forEach((field) => {
        if (medicationFields.includes(field)) {
          values[field] = medication[field];
        }
      });
      promise = fetch(`${apiRoot}/api/medications`, {
        method: "POST",
        headers: {
          Authorization: "Bearer " + token,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          document_id: documentId,
          // page_id: pageId,
          values,
        }),
      }).then((response) => response.json());
      return promise
        .then((medication) => {
          refreshMedications();
          // setMedications((prevMedications: any) => {
          //   return [...prevMedications, medication];
          // });
          setError(null);
          return medication;
        })
        .catch(setError)
        .finally(() => {
          updateLoading("medications", false);
        });
    },
    [updateLoading, apiRoot, token, refreshMedications],
  );

  const createMedicationV2 = useCallback(
    (documentId: string, medication: any) => {
      let promise: Promise<any>;
      updateLoading("medications", true);
      promise = fetch(`${apiRoot}/api/v2/medications`, {
        method: "POST",
        headers: {
          Authorization: "Bearer " + token,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          documentId,
          // page_id: pageId,
          medication,
        }),
      }).then((response) => response.json());
      return promise
        .then((medication) => {
          localCache.clear();
          config?.orchestrationEngineVersion === "v3" ? refreshMedicationsV2(true):refreshMedicationsV4(true);
          // setMedications((prevMedications: any) => {
          //   return [...prevMedications, medication];
          // });
          setError(null);
          return medication;
        })
        .catch(setError)
        .finally(() => {
          updateLoading("medications", false);
        });
    },
    [updateLoading, apiRoot, token, refreshMedicationsV2, config, refreshMedicationsV4],
  );

  const updateMedication = useCallback(
    (id: string, medication: any) => {
      let promise: Promise<any>;
      updateLoading("medications", true);
      // Take only the fields that are allowed to be updated (i.e., medicationFields)
      let values: any = {};
      medicationFields.forEach((field) => {
        if (medicationFields.includes(field)) {
          values[field] = medication[field];
        }
      });
      promise = fetch(`${apiRoot}/api/medications/${id}`, {
        method: "PATCH",
        headers: {
          Authorization: "Bearer " + token,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          values,
        }),
      });
      return promise
        .then(() => {
          // setMedications((prevMedications: any) => {
          //   return prevMedications.map((med: any) => {
          //     if (med.id === id) {
          //       return medication;
          //     } else {
          //       return med;
          //     }
          //   });
          // });
          refreshMedications();
          setError(null);
          return medication;
        })
        .catch(setError)
        .finally(() => {
          updateLoading("medications", false);
        });
    },
    [updateLoading, apiRoot, token, refreshMedications],
  );

  const updateMedicationV2 = useCallback(
    (id: string, medication: any, changedValues: any, documentId: string) => {
      let promise: Promise<any>;
      updateLoading("medications", true);
      // Take only the fields that are allowed to be updated (i.e., medicationFields)
      // let values: any = {};
      // medicationFields.forEach((field) => {
      //   if (medicationFields.includes(field)) {
      //     values[field] = medication[field];
      //   }
      // });
      promise = fetch(`${apiRoot}/api/v2/medications/${id}`, {
        method: "PATCH",
        headers: {
          Authorization: "Bearer " + token,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          medication,
          changedValues,
          documentId,
        }),
      });
      return promise
        .then((res) => {
          if (!res.ok) {
            setError(new Error(res.statusText));
            throw new Error(res.statusText);
          }
          setError(null);
          return medication;
        })
        .catch((err) => {
          setError(err);
          updateLoading("medications", false);
          throw err;
        });
    },
    [updateLoading, apiRoot, token],
  );

  const deleteMedication = useCallback(
    (id: string) => {
      let promise: Promise<any>;
      updateLoading("medications", true);
      promise = fetch(`${apiRoot}/api/medications/${id}`, {
        method: "DELETE",
        headers: {
          Authorization: "Bearer " + token,
        },
      });
      return promise
        .then(() => {
          // setMedications((prevMedications: any) => {
          //   // Set deleted to trud on the medication
          //   return prevMedications.map((med: any) => {
          //     if (med.id === id) {
          //       return { ...med, deleted: true };
          //     } else {
          //       return med;
          //     }
          //   });
          // });
          refreshMedications();
          setError(null);
        })
        .catch(setError)
        .finally(() => {
          updateLoading("medications", false);
        });
    },
    [updateLoading, apiRoot, token, refreshMedications],
  );

  const deleteMedicationV2 = useCallback(
    async (id: string, currentMed: any, documentId: string) => {
      let promise: Promise<any>;
      updateLoading("medications", true);
      promise = fetch(`${apiRoot}/api/v2/medications/${id}`, {
        method: "DELETE",
        body: JSON.stringify({
          medication: currentMed,
          documentId,
        }),
        headers: {
          Authorization: "Bearer " + token,
        },
      });
      return promise
        .then((res) => {
          // setMedications((prevMedications: any) => {
          //   // Set deleted to trud on the medication
          //   return prevMedications.map((med: any) => {
          //     if (med.id === id) {
          //       return { ...med, deleted: true };
          //     } else {
          //       return med;
          //     }
          //   });
          // });
          if (!res.ok) {
            setError(new Error(res.statusText));
            throw new Error(res.statusText);
          } else {
            localCache.clear();
            config?.orchestrationEngineVersion === "v3" ? refreshMedicationsV2(true):refreshMedicationsV4(true);
            setError(null);
          }
        })
        .catch((err) => {
          setError(err);
          throw err;
        })
        .finally(() => {
          updateLoading("medications", false);
        });
    },
    [updateLoading, apiRoot, token, refreshMedicationsV2, config, refreshMedicationsV4],
  );

  const undeleteMedication = useCallback(
    (id: string) => {
      let promise: Promise<any>;
      updateLoading("medications", true);
      promise = fetch(`${apiRoot}/api/medications/${id}/undelete`, {
        method: "POST",
        headers: {
          Authorization: "Bearer " + token,
        },
      });
      return promise
        .then(() => {
          setMedications((prevMedications: any) => {
            // Set deleted to false on the medication
            return prevMedications.map((med: any) => {
              if (med.id === id) {
                return { ...med, deleted: false };
              } else {
                return med;
              }
            });
          });
          setError(null);
        })
        .catch(setError)
        .finally(() => {
          updateLoading("medications", false);
        });
    },
    [apiRoot, setMedications, token, updateLoading],
  );

  const undeleteMedicationV2 = useCallback(
    (id: string) => {
      let promise: Promise<any>;
      updateLoading("medications", true);
      promise = fetch(`${apiRoot}/api/v2/medications/${id}/undelete`, {
        method: "POST",
        headers: {
          Authorization: "Bearer " + token,
        },
      });
      return promise
        .then(() => {
          setMedications((prevMedications: any) => {
            // Set deleted to false on the medication
            return prevMedications.map((med: any) => {
              if (med.id === id) {
                return { ...med, deleted: false };
              } else {
                return med;
              }
            });
          });
          setError(null);
        })
        .catch(setError)
        .finally(() => {
          updateLoading("medications", false);
        });
    },
    [apiRoot, setMedications, token, updateLoading],
  );

  const getEvidenceForGroupedMedications = useCallback(
    (medication: any): Promise<EvidenceInfo> => {
      if (medication.evidences?.length === 0) {
        return new Promise(async (resolve) => {
          const response = await fetch(
            `${apiRoot}/api/search_evidences?documentId=${medication.document_reference}&pageNumber=${medication.page_number}&evidenceRequestedFor=${medication.name}&pageId=${medication.page_id}`,
            { headers: { Authorization: "Bearer " + token } },
          );
          const annotations = await response.json();
          resolve({
            documentId: medication.document_reference || medication.document_id,
            pageNumber: medication.page_number,
            annotations: annotations.map((annotation: any) => {
              return {
                width: Math.abs(annotation.x2 - annotation.x1),
                height: Math.abs(annotation.y2 - annotation.y1),
                x: annotation.x1,
                y: annotation.y1,
                text: annotation.text,
                page: medication.page_number,
                orientation: annotation.orientation,
              };
            }),
          });
        });
      } else {
        return new Promise((resolve) => {
          resolve({
            documentId: medication.document_reference,
            pageNumber: medication.page_number,
            annotations: medication.evidences?.map((evidence: any) => {
              return {
                width: evidence.x2 - evidence.x1,
                height: evidence.y2 - evidence.y1,
                x: evidence.x1,
                y: evidence.y1,
                text: evidence.text,
                page: medication.page_number,
              };
            }),
          });
        });
      }
    },
    [apiRoot, token],
  );

  const getEvidence = useCallback(
    (id: string): Promise<EvidenceInfo> => {
      // TODO: We already have coarse evidence (document_id and page_id/page_number), but we'll need to fetch the actual evidence location
      const medication = medications.find((med) => med.id === id);
      if (medication?.evidences?.length === 0) {
        return new Promise(async (resolve) => {
          const response = await fetch(
            `${apiRoot}/api/search_evidences?documentId=${(medication as any).document_reference}&pageNumber=${(medication as any).page_number}&evidenceRequestedFor=${medication.name}&pageId=${(medication as any).page_id}`,
            { headers: { Authorization: "Bearer " + token } },
          );
          const annotations = await response.json();
          resolve({
            documentId: (medication as any).document_reference,
            pageNumber: (medication as any).page_number,
            annotations: annotations.map((annotation: any) => {
              return {
                width: annotation.x2 - annotation.x1,
                height: annotation.y2 - annotation.y1,
                x: annotation.x1,
                y: annotation.y1,
                text: annotation.text,
                page: (medication as any).page_number,
                orientation: annotation.orientation,
              };
            }),
          });
        });
      } else {
        return new Promise((resolve) => {
          resolve({
            documentId: (medication as any)?.document_reference,
            pageNumber: (medication as any)?.page_number,
            annotations:
              medication?.evidences?.map((evidence: any) => {
                return {
                  width: evidence.x2 - evidence.x1,
                  height: evidence.y2 - evidence.y1,
                  x: evidence.x1,
                  y: evidence.y1,
                  text: evidence.text,
                  page: (medication as any)?.page_number,
                };
              }) || [],
          });
        });
      }
    },
    [medications, apiRoot, token],
  );

  const getEvidenceV2 = useCallback(
    (
      id: string,
      signal?: AbortSignal,
      promiseSignal?: AbortSignal,
    ): Promise<EvidenceInfo> => {
      // call api to get evidence record corresponding to the extracted medication id
      const medication = medications.find((med: Medication) =>
        med.extractedMedications?.find(
          (extractedMedication: ExtractedMedication) =>
            extractedMedication?.extractedMedicationId === id,
        ),
      );
      const extractedMedication = medication?.extractedMedications?.find(
        (extractedMedication: ExtractedMedication) =>
          extractedMedication?.extractedMedicationId === id,
      ) as ExtractedMedication;
      return new Promise(async (resolve, reject) => {
        const abortListener = ({ target }: any) => {
          promiseSignal?.removeEventListener("abort", abortListener);
          reject(target.reason);
        };
        promiseSignal?.addEventListener("abort", abortListener);

        const response = await fetch(
          `${apiRoot}/api/v2/search_evidences?extractedMedicationId=${extractedMedication?.extractedMedicationId}`,
          { signal, headers: { Authorization: "Bearer " + token } },
        );
        const annotations = (await response.json()) as AnnotationRecord[];
        resolve({
          documentId: extractedMedication?.documentId,
          pageNumber: extractedMedication?.pageNumber,
          annotations: annotations.map((annotation) => {
            return {
              width: Math.abs(annotation.x2 - annotation.x1),
              height: Math.abs(annotation.y2 - annotation.y1),
              x: Math.min(annotation.x1, annotation.x2),
              y: Math.min(annotation.y1, annotation.y2),
              text: annotation.text,
              page: extractedMedication.pageNumber,
              orientation: annotation.orientation,
            } satisfies Coordinate;
          }),
        });
      });
      // return new Promise((resolve) => {
      //   resolve({
      //     documentId: medication.document_reference,
      //     pageNumber: medication.page_number,
      //     annotations: medication.evidences?.map((evidence: any) => { return { "width": evidence.x2 - evidence.x1, "height": evidence.y2 - evidence.y1, "x": evidence.x1, "y": evidence.y1, "text": evidence.text, "page": medication.page_number } }),
      //   });
      // });
    },
    [medications, apiRoot, token],
  );

  const getEvidenceV4 = useCallback(
    (
      id: string,
      signal?: AbortSignal,
      promiseSignal?: AbortSignal,
    ): Promise<EvidenceInfo> => {
      // call api to get evidence record corresponding to the extracted medication id
      const medication = medications.find((med: Medication) =>
        med.extractedMedications?.find(
          (extractedMedication: ExtractedMedication) =>
            extractedMedication?.extractedMedicationId === id,
        ),
      );
      const extractedMedication = medication?.extractedMedications?.find(
        (extractedMedication: ExtractedMedication) =>
          extractedMedication?.extractedMedicationId === id,
      ) as ExtractedMedication;
      return new Promise(async (resolve, reject) => {
        const abortListener = ({ target }: any) => {
          promiseSignal?.removeEventListener("abort", abortListener);
          reject(target.reason);
        };
        promiseSignal?.addEventListener("abort", abortListener);

        const response = await fetch(
          `${apiRoot}/api/v4/search_evidences?extractedMedicationId=${extractedMedication?.extractedMedicationId}&documentId=${extractedMedication?.documentId}`,
          { signal, headers: { Authorization: "Bearer " + token } },
        );
        const annotations = (await response.json()) as AnnotationRecord[];
        resolve({
          documentId: extractedMedication?.documentId,
          pageNumber: extractedMedication?.pageNumber,
          annotations: annotations.map((annotation) => {
            return {
              width: Math.abs(annotation.x2 - annotation.x1),
              height: Math.abs(annotation.y2 - annotation.y1),
              x: Math.min(annotation.x1, annotation.x2),
              y: Math.min(annotation.y1, annotation.y2),
              text: annotation.text,
              page: extractedMedication.pageNumber,
              orientation: annotation.orientation,
            } satisfies Coordinate;
          }),
        });
      });
      // return new Promise((resolve) => {
      //   resolve({
      //     documentId: medication.document_reference,
      //     pageNumber: medication.page_number,
      //     annotations: medication.evidences?.map((evidence: any) => { return { "width": evidence.x2 - evidence.x1, "height": evidence.y2 - evidence.y1, "x": evidence.x1, "y": evidence.y1, "text": evidence.text, "page": medication.page_number } }),
      //   });
      // });
    },
    [medications, apiRoot, token],
  );

  const getExtractedMedicationV2 = useCallback(
    (extractedMedicationId: string): Promise<any> => {
      return fetch(
        `${apiRoot}/api/v2/get_extracted_medications/${extractedMedicationId}`,
        { headers: { Authorization: "Bearer " + token } },
      ).then((response) => response.json());
    },
    [apiRoot, token],
  );

  const searchMedications = useCallback(
    (term: string, signal?: AbortSignal): Promise<Suggestion[]> => {
      return fetch(`${apiRoot}/api/medispan/search?term=${term}`, {
        signal,
        headers: { Authorization: "Bearer " + token },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.error) {
            console.error("Error searching medications:", data.error);
            throw new Error(data.error);
          }
          return data as Suggestion[];
        });
    },
    [apiRoot, token],
  );

  const importMedications = useCallback(() => {
    return fetch(`${apiRoot}/api/v2/medications/import`, {
      method: "POST",
      headers: {
        Authorization: "Bearer " + token,
        "okta-token": oktaToken,
        "ehr-token": ehrToken,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          console.error("Error importing medications:", data.error);
          throw new Error(data.error);
        }
        config?.orchestrationEngineVersion === "v3" ? refreshMedicationsV2(true): refreshMedicationsV4(true);
        return data;
      });
  }, [apiRoot, refreshMedicationsV2, token, oktaToken, ehrToken, config, refreshMedicationsV4]);

  const updateHostMedicationsV2 = useCallback(
    async (
      profileFilter: Record<string, ContextDocumentItemFilter>,
      medications: Array<Medication>,
    ) => {
      updateLoading("medications", true);
      try {
        const unSyncedMedications = medications.filter(
          (med) => !med.hostLinked,
        );
        const res = await fetch(
          `${apiRoot}/api/v2/medications/update_host_medications`,
          {
            method: "POST",
            signal: AbortSignal.timeout(20000),
            headers: {
              Authorization: "Bearer " + token,
              "okta-token": oktaToken,
              "ehr-token": ehrToken,
            },
            body: JSON.stringify({
              profileFilter: profileFilter,
              medications: unSyncedMedications,
            }),
          },
        );
        if (!res.ok) {
          throw new Error(res.statusText);
        }

        if (useLocalRefreshLogic) {
          setHasMedicationUpdates(true);
        } else {
          medWidgetInstance.dispatch("medication.save", {});
        }

        const response = await res.json();
        updateLoading("medications", false);
        if (response.error) {
          // setError(new Error(response.error));
          console.error("Error importing medications:", response.error);
          throw new Error(response.error);
        }
        setUpdateHostMedicationsResult(response);
        localCache.clear();
        config?.orchestrationEngineVersion === "v3" ? refreshMedicationsV2(true): refreshMedicationsV4(true);
        medWidgetInstance.dispatch(
          "medWidgetEvent-hostMedicationUpdatedSuccess",
        );

        return response;
      } catch (err) {
        setUpdateHostMedicationsResult({
          errored_medications: [],
          success_medications: [],
          error: "Error while updating medications",
        });
        updateLoading("medications", false);
        // setError(new Error("Error updating medications"));
        // throw new Error("Error updating medications");
        throw err;
        // return err;
      }
    },
    [
      updateLoading,
      apiRoot,
      token,
      oktaToken,
      ehrToken,
      refreshMedicationsV2,
      medWidgetInstance,
      setHasMedicationUpdates,
      config,
      refreshMedicationsV4,
    ],
  );

  const getClassificationV2 = useCallback(async () => {
    const result = await fetch(
      `${apiRoot}/api/v2/reference/external/classification`,
      {
        method: "GET",
        headers: {
          Authorization: "Bearer " + token,
          "okta-token": oktaToken,
          "ehr-token": ehrToken,
        },
      },
    ).then((res) => res.json());

    return result;
  }, [apiRoot, ehrToken, oktaToken, token]);

  // useEffect(() => {
  //   //refreshMedications();
  //   refreshMedicationsV2();
  // }, [refreshMedicationsV2]);

  useEffect(() => {
    if (!medicationClassifications.length) {
      updateLoading("medications", true);
      getClassificationV2()
        .then((result: any) => {
          const codes = result?.codes || [];
          setMedicationClassifications(codes);
        })
        .finally(() => updateLoading("medications", false));
    } else {
      updateLoading("medications", false);
    }
  }, [
    getClassificationV2,
    medicationClassifications.length,
    setMedicationClassifications,
    updateLoading,
  ]);

  return {
    medications,
    busy: loading.has("medications"),
    error,
    refreshMedications,
    refreshMedicationsV2,
    createMedication,
    createMedicationV2,
    updateMedication,
    updateMedicationV2,
    deleteMedication,
    deleteMedicationV2,
    searchMedications,
    undeleteMedication,
    undeleteMedicationV2,
    getEvidence,
    getEvidenceV2,
    getEvidenceV4,
    getEvidenceForGroupedMedications,
    getExtractedMedicationV2,
    importMedications,
    updateHostMedicationsV2,
    updateHostMedicationsResult,
    setUpdateHostMedicationsResult,
    getClassificationV2,
    medicationClassifications,
    refreshMedicationsV4
  };
};
