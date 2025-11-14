import {
  startTransition,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import {
  Alert,
  AlertDescription,
  AlertTitle,
  Badge,
  Box,
  CloseButton,
  Heading,
  HStack,
  IconButton,
  TableCellProps,
  TableRowProps,
  Tooltip,
  useDisclosure,
  useToast,
  useToken,
} from "@chakra-ui/react";
import { DeleteIcon, EditIcon, RepeatIcon } from "@chakra-ui/icons";
import {
  DynamicTableContainer,
  DynamicTableContainerProps,
  LinkButton,
  PrimaryButton,
  SecondaryButton,
  Spinner,
} from "@mediwareinc/wellsky-dls-react";
import {
  AccountEdit,
  AlertCircle,
  AlertOutline,
  CheckboxMarkedCircleOutline,
  History,
  Warning,
} from "@mediwareinc/wellsky-dls-react-icons";

import { Block } from "components/Block";
import { capitalizeWords } from "utils/i18n";
import {
  Env,
  EvidenceInfo,
  ExtractedMedication,
  Medication,
  OriginType,
  DocumentFile,
} from "types";
import { useMedicationsApi } from "hooks/useMedicationsApi";

import { MagicSparkle } from "icons/MagicSparkle";
import { useAuth } from "hooks/useAuth";

import { ContextDocumentItemFilter } from "tableOfContentsTypes";
import { medicationNoDataContent } from "./constants";
import { validateMedication } from "utils/helpers";
import OverlayLoader from "./OverlayLoader";
import { usePatientProfileStore } from "store/patientProfileStore";

import css from "./Medications.css";
import { useStyles } from "hooks/useStyles";
import { useExpandableContext } from "context/ExpandableContext";
import Evidences from "components/Evidences";
import ViewerInstance from "components/PdfViewerManager/store/ViewerInstance";
import AddMedicationV2 from "./AddEditMedication";
import EditMedicationV2 from "./AddEditMedication";
import { useMedWidgetInstanceContext } from "context/MedWidgetInstanceContext";
import { useConfigData } from "context/AppConfigContext";

class AlertMessage {
  message: string;
  type: string;
  details: string[];

  constructor(message: string, type: string, details: string[]) {
    this.message = message;
    this.type = type;
    if (!details || details.length === 0) {
      this.details = [];
    } else {
      this.details = details;
    }
  }
}

const vikiAPI = {
  log: (message: string): void => {
    console.log(message);
  },
  getMedicationAlerts: () => {},
  hasValidationErrors: () => {},
  setMedicationAlert: (
    medicationId: string,
    message: string,
    type: string,
    details: string[],
  ) => {},
  clearAllMedicationAlerts: () => {},
};

declare global {
  interface Window {
    vikiAPI: typeof vikiAPI;
  }
}

window.vikiAPI = vikiAPI;

type SortMap = Parameters<
  NonNullable<DynamicTableContainerProps<Medication[]>["onSortChange"]>
>[0];

export const MedicationsV2 = ({
  env,
  onSubmit,
  documentsInReview,
  currentDocument,
  onEvidenceRequested,
  hideInfoText = false,
  allowModification = true,
  viewerInstance,
  isFilteringEnabled = false,
  "data-pendo": dataPendo,
}: {
  env: Env;
  onSubmit: () => void;
  documentsInReview: DocumentFile[];
  currentDocument: DocumentFile | null;
  onEvidenceRequested: (evidenceInfo: EvidenceInfo) => void;
  pageProfiles?: Record<string, ContextDocumentItemFilter>;
  hideInfoText?: boolean;
  allowModification?: boolean;
  viewerInstance?: ViewerInstance;
  isFilteringEnabled?: boolean;
  "data-pendo"?: string;
}) => {
  const topInfo = useDisclosure({ defaultIsOpen: true });
  const [tableHeaderColor, deletedColor] = useToken(
    // the key within the theme, in this case `theme.colors`
    "colors",
    // the subkey(s), resolving to `theme.colors.red.100`
    ["neutral.100", "elm.500"],
    // a single fallback or fallback array matching the length of the previous arg
  );
  useStyles(css);

  const { patientId } = useAuth();
  const {
    // medications: medicationsFromState,
    medications,
    busy,
    error,
    refreshMedicationsV2,
    refreshMedicationsV4,
    createMedicationV2,
    updateMedicationV2,
    deleteMedicationV2,
    undeleteMedicationV2,
    getEvidenceV2,
    getEvidenceV4,
    updateHostMedicationsV2,
    updateHostMedicationsResult,
    setUpdateHostMedicationsResult,
  } = useMedicationsApi({
    apiRoot: env?.API_URL,
    patientId,
    documentsInReview,
  });

  const [busyMedicationId, setBusyMedicationId] = useState<string>("");
  const { cachedEvidences, setCachedEvidences, allPageProfiles } =
    usePatientProfileStore();
  const [reviewInProgress, setReviewInProgress] = useState<boolean>(false);
  const [currentReview, setCurrentReview] = useState<number>(1);
  const [totalReviews, setTotalReviews] = useState<number>(1);
  const [currentReviewIds, setCurrentReviewIds] = useState<string[]>();
  const { resetCollapsedBoxes } = useExpandableContext();
  const [sorting, setSorting] = useState<SortMap>([]);

  const config = useConfigData();

  useEffect(() => {
    viewerInstance?.addEventListener?.(
      "pdfViewer_documentChanged",
      (data: any) => {
        console.log("pdfViewer_documentChanged", data);
      },
    );
  }, [viewerInstance]);

  const onClearEvidence = useCallback(
    (docId?: string) => {
      viewerInstance?.removeAnnotations?.(
        docId || currentDocument?.id || "",
        1,
      );
    },
    [currentDocument?.id, viewerInstance],
  );

  const filteredMedications = useMemo(() => {
    const filteredMedicationsTemp = medications?.filter(
      (medication: Medication) => {
        if (allowModification === false) {
          return (
            medication?.origin === OriginType.IMPORTED
            // || medication?.origin === OriginType.USER_ENTERED
          );
        }

        if (
          medication?.deleted &&
          medication?.origin === OriginType.USER_ENTERED &&
          !medication?.extractedMedications?.length
        ) {
          return false;
        }

        if (medication?.origin !== OriginType.EXTRACTED) {
          return true; // non extracted medications need to show all the time
        }

        return medication?.extractedMedications?.some(
          (extractedMedication: ExtractedMedication) => {
            const isMatch =
              allPageProfiles?.get(extractedMedication.documentId)
                ?.medication?.[extractedMedication.pageNumber]?.isSelected ||
              false;

            return isMatch;
          },
        );
      },
    );

    if (sorting?.length && isFilteringEnabled) {
      let sortedResults = filteredMedicationsTemp || [];
      sorting
        .filter((s) => Boolean(s.sortType))
        .forEach((sort) => {
          const sortKey = sort.sortKey as keyof Medication;
          sortedResults = sortedResults.sort((a, b) => {
            const prev = a[sortKey];
            const next = b[sortKey];
            if (sort.sortType === "asc") {
              if (
                prev !== null &&
                prev !== undefined &&
                next !== null &&
                next !== undefined
              ) {
                // eslint-disable-next-line
                return prev > next ? 1 : -1;
              }
              return 0;
            } else {
              if (
                prev !== null &&
                prev !== undefined &&
                next !== null &&
                next !== undefined
              ) {
                // eslint-disable-next-line
                return prev < next ? 1 : -1;
              }
              return 0;
            }
          });
        });

      return sortedResults;
    }

    return filteredMedicationsTemp || [];
  }, [
    medications,
    sorting,
    isFilteringEnabled,
    allowModification,
    allPageProfiles,
  ]);

  const [evidenceClicked, setEvidenceClicked] = useState<string>("");

  const excludeColumns = [
    "id",
    "reference",
    "evidence",
    "app_id",
    "document_reference",
    "document_id",
    "tenant_id",
  ];
  let columns = (medications.length ? Object.keys(medications[0]) : []).filter(
    (column) => !excludeColumns.includes(column),
  );
  columns = ["dosage", "instructions", "startDate", "discontinuedDate"];

  const [addingMedication, setAddingMedication] = useState(false);
  const [editingMedication, setEditingMedication] = useState<any | null>(null);
  const [genericMessage, setGenericMessage] = useState<string>("");
  const { medWidgetInstance } = useMedWidgetInstanceContext();
  const emptyMedicationListMessage =
    medWidgetInstance?.getConfig()?.emptyMedicationListMessage;

  // TODO: Remove below code after new implementation witn helper function.
  // @deprecated
  const [medicationAlerts, setMedicationAlerts] = useState<{
    [key: string]: AlertMessage;
  }>({});

  const validationErrors = useMemo(() => {
    return new Map(
      filteredMedications?.map((medication) => [
        medication.id,
        {
          ...validateMedication(
            medication,
            config.validationRules || undefined,
          ),
          deleted: medication.deleted,
        },
      ]),
    );
  }, [filteredMedications, config.validationRules]);

  const currentErrors = useMemo(() => {
    return new Map(
      Array.from(validationErrors).filter(
        ([_, validatedObj]) => !validatedObj.success && !validatedObj.deleted,
      ),
    );
  }, [validationErrors]);

  const startReview = useCallback(() => {
    setCurrentReviewIds(Array.from(currentErrors).map(([id]) => id));
    setReviewInProgress(true);
    setCurrentReview(1);
    setEditingMedication(
      filteredMedications.find(
        (m) => m.id === Array.from(currentErrors)[currentReview - 1][0],
      ),
    );
    setTotalReviews(currentErrors.size);
  }, [currentErrors, currentReview, filteredMedications]);

  const stopReview = useCallback(() => {
    setReviewInProgress(false);
    setCurrentReview(1);
    setTotalReviews(0);
    setCurrentReviewIds([]);
    setEditingMedication(null);
  }, []);

  const filteredMedicationsIds = useMemo(
    () => filteredMedications?.map((med) => med.id),
    [filteredMedications],
  );

  const hasValidationErrors = filteredMedicationsIds.some((id) => {
    const validatedObj = validationErrors.get(id);
    if (validatedObj) {
      return !validatedObj.success && !validatedObj.deleted;
    }
    return false;
  });

  const noOfUnsyncedMedication = filteredMedications.filter(
    (med) => !med.hostLinked && !med.deleted,
  ).length;

  useEffect(() => {}, [medicationAlerts]);

  // Exposed API functions -----------------------------------------------------------------------------------------------------------
  const getMedicationAlerts = () => {
    return medicationAlerts;
  };

  const getIsValidationError = () => {
    return hasValidationErrors;
  };

  const setMedicationAlert = useCallback(
    (
      medicationId: string,
      alert_message: string,
      alert_type: string,
      alert_details: string[],
    ) => {
      const alertMessage = new AlertMessage(
        alert_message,
        alert_type,
        alert_details,
      );

      setMedicationAlerts((prev) => {
        return {
          ...prev,
          [medicationId]: alertMessage,
        };
      });
    },
    [],
  );

  const clearAllMedicationAlerts = () => {
    setMedicationAlerts({});
  };

  vikiAPI.getMedicationAlerts = getMedicationAlerts;
  vikiAPI.hasValidationErrors = getIsValidationError;
  vikiAPI.setMedicationAlert = setMedicationAlert;
  vikiAPI.clearAllMedicationAlerts = clearAllMedicationAlerts;
  const controller = useRef<AbortController>();
  const promiseController = useRef<AbortController>();

  // End exposed API functions -----------------------------------------------------------------------------------------------------------

  const loadEvidence = useCallback(
    (id: string, onLoadComplete?: () => void) => {
      setBusyMedicationId(id);
      let promise: Promise<EvidenceInfo>;
      if (cachedEvidences[id]) {
        promise = Promise.resolve(cachedEvidences[id]);
        controller.current?.abort("Terminate");
        promiseController.current?.abort("Terminate");
      } else {
        controller.current?.abort("Terminate");
        promiseController.current?.abort("Terminate");

        controller.current = new AbortController();
        promiseController.current = new AbortController();

        const signal = controller.current.signal;
        const promiseSignal = controller.current.signal;

        promise =
          config?.orchestrationEngineVersion === "v3"
            ? getEvidenceV2(id, signal, promiseSignal)
            : getEvidenceV4(id, signal, promiseSignal);
      }

      promise
        .then((evidenceInfo: EvidenceInfo) => {
          viewerInstance?.hightlightAnnotation(
            evidenceInfo.documentId,
            evidenceInfo.pageNumber,
            evidenceInfo.annotations,
          );
          onEvidenceRequested(evidenceInfo);
          setCachedEvidences(id, evidenceInfo);
          setBusyMedicationId("");
          resetCollapsedBoxes?.();
          onLoadComplete?.();
        })
        .catch((e) => {
          if (e !== "Terminate") {
            setBusyMedicationId("");
          }
          onLoadComplete?.();
        })
        .finally(() => {
          // setBusyMedicationId("");
        });
    },
    [
      cachedEvidences,
      getEvidenceV2,
      onEvidenceRequested,
      resetCollapsedBoxes,
      setCachedEvidences,
      viewerInstance,
      getEvidenceV4,
      config,
    ],
  );

  useEffect(() => {
    if (updateHostMedicationsResult) {
      if (updateHostMedicationsResult.error) {
        setGenericMessage(updateHostMedicationsResult.error);
      } else {
        // let error: string = `No. of Medications updated sucessfully: ${updateHostMedicationsResult?.success_medications.length}, No. of medications failed to update: ${updateHostMedicationsResult?.errored_medications.length}`;
        const tMedAlerts: any = [];
        updateHostMedicationsResult?.errored_medications?.forEach(
          (medication_err: any) => {
            const id = medication_err.medication.id;
            const alert_msg = "Error updating medication: ";
            const alert_type = "error";
            const alert_details: string[] = [];
            medication_err?.error?.forEach((err: string) => {
              alert_details.push(err);
            });
            tMedAlerts[id] = new AlertMessage(
              alert_msg,
              alert_type,
              alert_details,
            );
          },
        );

        setMedicationAlerts(tMedAlerts);

        // setGenericMessage(error);
      }
    }
  }, [updateHostMedicationsResult]);

  const renderCell = (
    content: any,
    _obj: any,
    _useStrikeThrough: boolean = false,
  ) => {
    return content;
  };

  const coalesceString = (values: Array<string>) => {
    let result = values
      .filter((value) => value !== null && value !== undefined && value !== "")
      .join(" ");
    return result;
  };
  const toast = useToast();

  const showNoData = !allowModification && filteredMedications?.length <= 0;

  const noDataContent = useMemo(
    () => medicationNoDataContent(emptyMedicationListMessage),
    [emptyMedicationListMessage],
  );

  return (
    <Block style={{ position: "relative", gap: "1rem" }} data-pendo={dataPendo}>
      {addingMedication && (
        <AddMedicationV2
          apiRoot={env.API_URL}
          isOpen={addingMedication}
          onSave={async (medication, changedValues) => {
            try {
              await createMedicationV2(currentDocument?.id || "", medication);
            } catch (e: any) {
              toast({
                title: `Something went wrong.`,
                description: e.message,
                status: "error",
                duration: 5000,
                isClosable: true,
              });
            } finally {
              config?.orchestrationEngineVersion === "v3"
                ? refreshMedicationsV2(true)
                : refreshMedicationsV4(true);
              setAddingMedication(false);
            }
          }}
          onCancel={() => {
            setAddingMedication(false);
          }}
        />
      )}

      {editingMedication && (
        <EditMedicationV2
          activeEvidenceId={evidenceClicked}
          setActiveEvidenceId={setEvidenceClicked}
          loadEvidence={loadEvidence}
          onEvidenceRequested={onEvidenceRequested}
          errorMessages={currentErrors?.get(editingMedication?.id)?.errors}
          currentReview={currentReview}
          totalReviewsCount={totalReviews}
          reviewInProgress={reviewInProgress}
          apiRoot={env.API_URL}
          isOpen={Boolean(editingMedication)}
          medication={editingMedication}
          onSave={async (newValues, changedValues, cb) => {
            const id = editingMedication.id;

            const saveAction = async () => {
              await updateMedicationV2(
                id,
                newValues,
                changedValues,
                currentDocument?.id || "",
              );
              setEvidenceClicked("");
            };

            if (reviewInProgress) {
              try {
                await saveAction();

                config?.orchestrationEngineVersion === "v3"
                  ? await refreshMedicationsV2(true)
                  : await refreshMedicationsV4(true);
                toast({
                  title: `Medications updated successfully.`,
                  status: "success",
                  duration: 5000,
                  isClosable: true,
                });
                cb?.();

                // updateQueue.current.push({
                //   id: editingMedication.id,
                //   saveAction,
                // });
                const next = currentReviewIds?.[currentReview];

                if (next) {
                  setCurrentReview((prev) => prev + 1);
                  setEditingMedication({});
                  setTimeout(() => {
                    setEditingMedication(
                      filteredMedications.find((m) => m.id === next),
                    );
                  }, 200);
                } else {
                  try {
                    setEditingMedication(null);
                  } catch (error: any) {
                    toast({
                      title: `Something went wrong.`,
                      description: error.message,
                      status: "error",
                      duration: 5000,
                      isClosable: true,
                    });
                  } finally {
                    stopReview();
                  }
                }
              } catch (error) {
                toast({
                  title: `Something went wrong while updating Medication.`,
                  status: "error",
                  duration: 5000,
                  isClosable: true,
                });
              } finally {
                cb?.();
              }

              return;
            }

            try {
              await saveAction();
              toast({
                title: `Medication updated successfully.`,
                status: "success",
                duration: 5000,
                isClosable: true,
              });
            } catch (e: any) {
              toast({
                title: `Something went wrong.`,
                description: e.message,
                status: "error",
                duration: 5000,
                isClosable: true,
              });
            } finally {
              config?.orchestrationEngineVersion === "v3"
                ? refreshMedicationsV2(true)
                : refreshMedicationsV4(true);
              setEditingMedication(null);
            }
          }}
          onDelete={async (onFinish) => {
            try {
              const deleteCall = async () => {
                await deleteMedicationV2(
                  editingMedication.id,
                  editingMedication,
                  currentDocument?.id || "",
                );
              };
              await deleteCall();
              config?.orchestrationEngineVersion === "v3"
                ? await refreshMedicationsV2(true)
                : await refreshMedicationsV4(true);
              if (reviewInProgress) {
                toast({
                  title: `Medication deleted successfully.`,
                  status: "success",
                  duration: 5000,
                  isClosable: true,
                });

                const next = currentReviewIds?.[currentReview];

                if (next) {
                  setCurrentReview((prev) => prev + 1);
                  setEditingMedication(null);
                  startTransition(() => {
                    setEditingMedication(
                      filteredMedications.find((m) => m.id === next),
                    );
                  });
                } else {
                  setEditingMedication(null);
                  stopReview();
                }

                return;
              } else {
                toast({
                  title: `Medication deleted successfully.`,
                  status: "success",
                  duration: 5000,
                  isClosable: true,
                });
                setEditingMedication(null);
              }
            } catch (error: any) {
              toast({
                title: `Something went wrong while deleting medication.`,
                description: error.message,
                status: "error",
                duration: 5000,
                isClosable: true,
              });
            } finally {
              config?.orchestrationEngineVersion === "v3"
                ? await refreshMedicationsV2(true)
                : await refreshMedicationsV4(true);
              onFinish?.();
            }
          }}
          onCancel={() => {
            stopReview();
          }}
        />
      )}
      {!hideInfoText && topInfo.isOpen && (
        <Alert
          px="16px"
          py="8px"
          overflow="initial"
          status="warning"
          border="1px solid #97449C"
          backgroundColor="#F9F4F9"
          data-pendoid="medication-errors-alert"
        >
          <HStack alignItems="flex-start" spacing="16px" width="100%">
            <Box flexShrink={0}>
              <MagicSparkle fontSize={48} />
            </Box>
            <AlertDescription
              fontSize="16px"
              lineHeight="24px"
              flex="1"
              data-pendoid="medication-errors-alert-description"
            >
              The information provided was generated by Artificial Intelligence.
              The following medications were extracted from the selected
              documents. You can review, edit, or remove medications before
              completing the patient record. Select a medication to view the
              source within the document.
            </AlertDescription>
            <CloseButton
              flexShrink={0}
              alignSelf="flex-start"
              onClick={topInfo.onClose}
            />
          </HStack>
        </Alert>
      )}
      {hasValidationErrors && allowModification && (
        <Alert
          status="error"
          padding="8px 16px"
          data-pendoid="medication-errors"
        >
          <AlertOutline style={{ color: "#B02828" }} />
          <HStack justifyContent="space-between" flex="1 1 0%">
            <AlertTitle fontSize="16px" fontWeight="medium">
              {reviewInProgress ? totalReviews : currentErrors?.size}{" "}
              Medications alerts
            </AlertTitle>
            <SecondaryButton
              bgColor="white"
              onClick={startReview}
              data-pendoid="medication-review-button"
            >
              Review
            </SecondaryButton>
          </HStack>
        </Alert>
      )}
      <Heading
        size="sm"
        style={{ margin: "2rem", display: "flex", flexDirection: "row" }}
        data-pendoid="medication-heading"
      >
        Medications
        <IconButton
          variant="link"
          style={{ marginLeft: "1rem" }}
          size="lg"
          onClick={() =>
            config?.orchestrationEngineVersion === "v3"
              ? refreshMedicationsV2(true)
              : refreshMedicationsV4(true)
          }
          aria-label="Refresh"
          icon={<RepeatIcon />}
          data-pendoid="medication-refresh-button"
        />
        <div style={{ flex: "1 1 0" }}></div>
        {allowModification && (
          <LinkButton
            onClick={() => {
              setEditingMedication(null);
              setAddingMedication(true);
            }}
            data-pendoid="medication-add-button"
          >
            Add Medication
          </LinkButton>
        )}
      </Heading>
      {busy && <OverlayLoader />}
      {(updateHostMedicationsResult?.success_medications?.length || 0) > 0 && (
        <Alert
          status="success"
          padding="8px 16px"
          data-pendoid="medication-success-alert"
        >
          <CheckboxMarkedCircleOutline style={{ color: "green" }} />
          <Box flex="1">
            <AlertTitle fontSize="16px" fontWeight="medium">
              {updateHostMedicationsResult?.success_medications?.length}{" "}
              successfully added to the medication profile.
            </AlertTitle>
          </Box>
          <CloseButton
            onClick={() => {
              setUpdateHostMedicationsResult((prev: any) => {
                return {
                  ...prev,
                  success_medications: [],
                };
              });
            }}
          ></CloseButton>
        </Alert>
      )}
      {(updateHostMedicationsResult?.errored_medications?.length || 0) > 0 && (
        <Alert
          status="error"
          padding="8px 16px"
          data-pendoid="host-medication-error"
        >
          <AlertOutline style={{ color: "#B02828" }} />
          <Box flex="1">
            <AlertTitle fontSize="16px" fontWeight="medium">
              {updateHostMedicationsResult?.errored_medications?.length}{" "}
              medications failed to be added to the medication profile.
            </AlertTitle>
          </Box>
          <CloseButton
            onClick={() => {
              setUpdateHostMedicationsResult((prev: any) => {
                return {
                  ...prev,
                  errored_medications: [],
                };
              });
            }}
          ></CloseButton>
        </Alert>
      )}
      <div
        style={{
          display: "flex",
          flex: "1 1 0px",
          flexDirection: "column",
          gap: "1rem",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            flex: "1 1 0px",
            overflowY: "auto",
            display: "flex",
            flexDirection: "column",
            gap: "1rem",
          }}
        >
          {genericMessage !== "" && (
            <Alert status="error" data-pendoid="generic-error">
              <Warning style={{ color: "red" }} />
              {/* <AlertCircle /> */}
              <Box>
                <AlertDescription>{genericMessage.toString()}</AlertDescription>
              </Box>
            </Alert>
          )}

          {error !== null ? (
            <Alert status="error" data-pendoid="medication-loading-error">
              <AlertCircle />
              <Box>
                <AlertTitle>An error occured</AlertTitle>
                <AlertDescription>Failed to fetch medications</AlertDescription>
              </Box>
            </Alert>
          ) : (
            <>
              {showNoData ? (
                noDataContent
              ) : (
                <DynamicTableContainer
                  data-pendoid="medication-table"
                  getRowProps={(data, _index): TableRowProps & any => {
                    if (data.deleted) {
                      return {
                        color: deletedColor,
                        opacity: 0.5,
                      };
                    }
                    return {};
                  }}
                  onSortChange={(sorting) => {
                    setSorting(sorting);
                  }}
                  rowKey={(data) => data.id}
                  noDataContent={noDataContent}
                  hideConditions={{
                    actions: !allowModification,
                    id: !allowModification,
                  }}
                  pagination={{
                    isStatic: true,
                    defaultPageSize: 25,
                  }}
                  tableProps={{ size: "sm", className: "medication-table" }}
                  headerColor={tableHeaderColor}
                  columns={[
                    {
                      dataIndex: "id",
                      id: "evidence-button",
                      sortable: false,
                      getColumnProps: <TDProp extends any>(
                        data: Medication,
                      ): TDProp & TableCellProps => {
                        return {
                          "data-pendoid": `document-id-${data.id}`,
                        } as unknown as TDProp & TableCellProps;
                      },
                      render: (id: any, currentMed: Medication) => {
                        if (
                          currentMed?.origin === OriginType.USER_ENTERED ||
                          currentMed?.hostLinked
                        ) {
                          const iconColor =
                            currentMed?.origin === OriginType.USER_ENTERED
                              ? "#E99346"
                              : "#3D5463";
                          return (
                            <div
                              style={{
                                display: "flex",
                                justifyContent: "center",
                              }}
                            >
                              <AccountEdit
                                style={{
                                  color: iconColor,
                                  fontSize: 40,
                                }}
                              />
                            </div>
                          );
                        }

                        if (busyMedicationId.includes(id)) {
                          return (
                            <div
                              style={{
                                width: "24px",
                                height: "24px",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                              }}
                            >
                              <Spinner size="sm" />
                            </div>
                          );
                        }

                        return (
                          <div
                            style={{
                              display: "flex",
                              justifyContent: "center",
                            }}
                          >
                            <MagicSparkle
                              fontSize={32}
                              animated={false}
                              onClick={() => {}}
                            />
                          </div>
                        );
                      },
                      title: "",
                      width: "40px",
                    },
                    {
                      dataIndex: "id",
                      id: "profile",
                      sortable: false,
                      render: (id: any, currentMed: any) => {
                        return renderCell(
                          <div
                            style={{ display: "flex", justifyContent: "center" }}
                          >
                            <Tooltip label={currentMed?.medication_status}>
                              <div>
                                {currentMed?.medication_status?.[0]?.toUpperCase()}
                              </div>
                            </Tooltip>
                          </div>,
                          currentMed,
                        );
                      },
                      title: "",
                      width: "40px",
                    },
                    {
                      dataIndex: "id",
                      id: "id",
                      sortable: false,
                      getColumnProps: <TDProp extends any>(
                        data: Medication,
                      ): TDProp & TableCellProps => {
                        return {
                          "data-pendoid": `document-evidences-${data.id}`,
                        } as unknown as TDProp & TableCellProps;
                      },
                      render: (id: any, currentMed: Medication) => {
                        return renderCell(
                          <Evidences
                            medication={currentMed}
                            loadEvidence={loadEvidence}
                            onEvidenceRequested={onEvidenceRequested}
                            activeEvidenceId={evidenceClicked}
                            setActiveEvidenceId={setEvidenceClicked}
                            onClearEvidence={onClearEvidence}
                            compact
                          />,
                          currentMed,
                          false,
                        );
                      },
                      title: "Source",
                      width: "40px",
                    },
                    {
                      dataIndex: "medispanMatchStatus",
                      id: "score",
                      getColumnProps: <TDProp extends any>(
                        data: Medication,
                      ): TDProp & TableCellProps => {
                        return {
                          "data-pendoid": `document-medispanMatchStatus-${data.id}`,
                        } as unknown as TDProp & TableCellProps;
                      },
                      render: (
                        medispanMatchStatus: any,
                        currentMed: Medication,
                      ) => {
                        const alert = validationErrors.get(currentMed.id);
                        const hasErrors = Boolean(alert?.errors?.length);

                        return (
                          <Box
                            display="flex"
                            alignItems="center"
                            justifyContent="flex-start"
                          >
                            {alert && hasErrors && (
                              <Tooltip
                                label={
                                  alert.errors && (
                                    <ul>
                                      {alert.errors?.map((detail) => {
                                        return (
                                          <li
                                            key={detail + currentMed.id}
                                            style={{
                                              listStyle: "none",
                                            }}
                                          >
                                            <span>{detail}</span>
                                          </li>
                                        );
                                      })}
                                    </ul>
                                  )
                                }
                              >
                                <AlertOutline
                                  style={{
                                    color: "#B02828",
                                    fontSize: 34,
                                  }}
                                />
                              </Tooltip>
                            )}
                            {currentMed?.isUnlisted ? (
                              <span
                                style={{
                                  color:
                                    "var(--palette-status-ws-status-200, #B02828)",
                                  fontStyle: "italic",
                                }}
                              >
                                (Unlisted)
                              </span>
                            ) : null}
                          </Box>
                        );
                      },
                      title: "Medication Type",
                    },
                    {
                      dataIndex: "id",
                      id: "fullDesc",
                      sortable: false,
                      getColumnProps: <TDProp extends any>(
                        data: Medication,
                      ): TDProp & TableCellProps => {
                        return {
                          "data-pendoid": `document-fullDesc-${data.id}`,
                        } as unknown as TDProp & TableCellProps;
                      },
                      render: (id: any, currentMed: Medication) => {
                        return renderCell(
                          <div>
                            <div
                              style={{ display: "flex", justifyContent: "left" }}
                            >
                              {coalesceString([
                                currentMed.name_original,
                                `(${currentMed.name})`,
                                currentMed.route,
                                currentMed.form,
                                currentMed.strength,
                              ])}
                            </div>
                          </div>,
                          currentMed,
                        );
                      },
                      title: "Drug/Route/Form/Strength",
                      width: "40px",
                    },
                    ...columns.map((column) => ({
                      dataIndex: column,
                      id: column,
                      // sortable: true,
                      title:
                        column === "dosage"
                          ? "Amount/Dose"
                          : capitalizeWords(column),
                      getColumnProps: <TDProp extends any>(
                        data: Medication,
                      ): TDProp & TableCellProps => {
                        return {
                          "data-pendoid": `document-dosage-${data.id}`,
                        } as unknown as TDProp & TableCellProps;
                      },
                      render: (value: any, obj: any) => {
                        return renderCell(
                          column === "startDate" && obj.isLongStanding ? (
                            <HStack spacing={2}>
                              <Badge
                                colorScheme="blue"
                                fontSize="0.8em"
                                px={2}
                                py={0.5}
                                borderRadius="md"
                              >
                                LS
                              </Badge>
                              {value && <span>{value}</span>}
                            </HStack>
                          ) : (
                            <span
                              style={{
                                fontWeight:
                                  !obj.deleted && column === "name"
                                    ? "bold"
                                    : "normal",
                              }}
                            >
                              {value}
                            </span>
                          ),
                          obj,
                          column === "name",
                        );
                      },
                    })),
                    {
                      dataIndex: "id",
                      id: "actions",
                      sortable: false,
                      getColumnProps(data): any {
                        return {
                          "data-pendoid": `medication-actions-${data.id}`,
                          position: "sticky",
                          right: "0px",
                          paddingRight: "20px",
                          zIndex: 2,
                          background: "white",
                          _before: {
                            boxShadow: "-5px 0px 7px 0px rgb(0 0 0 / 15%)",
                            content: `''`,
                            position: "absolute",
                            top: 0,
                            left: 0,
                            bottom: "-1px",
                            width: "8px",
                            transform: "translateX(100%)",
                          },
                        };
                      },
                      render: (id: any, currentMed: Medication) => {
                        if (!allowModification) {
                          return;
                        }

                        if (currentMed.origin === OriginType.IMPORTED) {
                          return null;
                        }

                        const isDeleted =
                          currentMed !== null && currentMed.deleted;
                        return (
                          <div
                            style={{
                              display: "flex",
                              gap: "0.5rem",
                              flexDirection: "row",
                            }}
                          >
                            <IconButton
                              variant="link"
                              aria-label="Edit"
                              icon={<EditIcon />}
                              onClick={() => {
                                setEditingMedication(null);
                                setAddingMedication(false);
                                stopReview();

                                startTransition(() => {
                                  setEditingMedication(currentMed || null);
                                });
                              }}
                              style={{
                                opacity: isDeleted ? 0 : 1,
                                pointerEvents: isDeleted ? "none" : "auto",
                              }}
                            />
                            {isDeleted ? (
                              <IconButton
                                variant="link"
                                aria-label="Undelete"
                                icon={<History fontSize="24" />}
                                onClick={() => {
                                  undeleteMedicationV2(id);
                                }}
                              />
                            ) : (
                              (currentMed?.hostLinked
                                ? config?.uiHostLinkedDeleteEnable
                                : true) && (
                                <IconButton
                                  variant="link"
                                  aria-label="Delete"
                                  icon={<DeleteIcon />}
                                  onClick={async () => {
                                    try {
                                      await deleteMedicationV2(
                                        currentMed.id,
                                        currentMed,
                                        currentDocument?.id || "",
                                      );
                                      toast({
                                        title: `Medication deleted successfully.`,
                                        status: "success",
                                        duration: 5000,
                                        isClosable: true,
                                      });
                                    } catch (error: any) {
                                      toast({
                                        title: `Something went wrong while deleting medication.`,
                                        description: error.message,
                                        status: "error",
                                        duration: 5000,
                                        isClosable: true,
                                      });
                                    } finally {
                                      config?.orchestrationEngineVersion === "v3"
                                        ? await refreshMedicationsV2()
                                        : await refreshMedicationsV4();
                                    }
                                  }}
                                />
                              )
                            )}
                          </div>
                        );
                      },
                      title: "Actions",
                    },
                  ]}
                  dataSource={filteredMedications}
                  onRowClick={(column) => {}}
                />
              )}
            </>
          )}
        </div>
        {allowModification && (
          <div
            className="medication-footer"
            style={{
              position: "sticky",
              bottom: "0",
              backgroundColor: "white",
              borderTop: "1px solid #E2E8F0",
              boxShadow: "0 -2px 4px rgba(0, 0, 0, 0.1)",
              padding: "1rem",
              display: "flex",
              justifyContent: "flex-end",
              gap: "1rem",
              zIndex: 10,
            }}
          >
            <PrimaryButton
              onClick={async () => {
                try {
                  await updateHostMedicationsV2(
                    allPageProfiles?.get(currentDocument?.id || "")?.medication ||
                      ({} as any),
                    filteredMedications.filter((med) => !med.deleted),
                  );
                } catch (error: any) {
                  toast({
                    title: error.message,
                    status: "error",
                    duration: 5000,
                    isClosable: true,
                  });
                }
              }}
              isDisabled={hasValidationErrors || noOfUnsyncedMedication === 0}
              data-pendoid="medication-update-button"
            >
              Update Medication Profile
            </PrimaryButton>
          </div>
        )}
      </div>
    </Block>
  );
};
