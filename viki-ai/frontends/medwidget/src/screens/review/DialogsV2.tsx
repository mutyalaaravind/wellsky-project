import {
  startTransition,
  useCallback,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import {
  Dialog,
  Select,
  Spinner,
  TextArea,
  TextInput,
  Checkbox,
  Tooltip,
  SubHeading4,
  DialogProps,
  TertiaryButton,
  Para3R,
  SecondaryButton,
} from "@mediwareinc/wellsky-dls-react";

import {
  getMedicationStatuses,
  getMedicationStatusReasons,
  useMedicationsApi,
} from "hooks/useMedicationsApi";
import { capitalizeWords } from "utils/i18n";
import {
  Box,
  Button,
  Drawer,
  DrawerBody,
  DrawerCloseButton,
  DrawerContent,
  DrawerFooter,
  DrawerHeader,
  DrawerProps,
  Flex,
  FormControl,
  Heading,
  HStack,
  Input,
  Text,
  useToast,
  VStack,
} from "@chakra-ui/react";

import css from "./Dialogs.css";
import { useDebouncedCallback } from "use-debounce";
import { useStyles } from "hooks/useStyles";
import {
  Env,
  EvidenceInfo,
  ExtractedMedication,
  KeyOfMap,
  Medication,
} from "types";
import { validateMedication } from "utils/helpers";
import { useConfigData } from "context/AppConfigContext";
import MedicationSuggestionsTable from "./MedicationSuggestionsTable";
import {
  ChevronDoubleUp,
  CloseCircleOutline,
  Delete,
} from "@mediwareinc/wellsky-dls-react-icons";
import OverlayLoader from "./OverlayLoader";
import Evidences from "components/Evidences";
import { Block } from "components/Block";
import { UploadArea } from "components/UploadArea";
// import MedicationSuggestionsTableV2 from "./MedicationSuggestionsTableV2";

type MedicationDialogProps = {
  apiRoot: string;
  medication?: any;
  isOpen: boolean;
  onSave: (medication: any, changedValues: any | null, cb?: () => void) => void;
  onCancel: () => void;
  isDrawer?: true | false;
  reviewInProgress?: true | false;

  totalReviewsCount?: number;
  currentReview?: number;
  errorMessages?: string[];
  loadEvidence?: (id: string) => void;
  onEvidenceRequested?: (evidenceInfo: EvidenceInfo) => void;
  groupByDocument?: (
    extractedMedications: Array<ExtractedMedication>,
  ) => Record<string, Array<ExtractedMedication>>;
  onDelete?: (cb?: () => void) => void;
};

type CachedSearchDict = {
  [key: string]: any[];
};

export const medicationFieldsLayout = [
  ["name"],
  ["strength", "route", "form"],
  ["dosage"],
  ["instructions"],
  ["startDate", "discontinuedDate"],
  ["medicationClassification"],
];

type validateFormType = () => {
  success: boolean;
  errors: string[];
  fieldWiseErrors?:
    | Map<
        Partial<
          | "name"
          | "dosage"
          | "startDate"
          | "endDate"
          | "classification"
          | "medispanId"
          | "statusReason"
        >,
        string[]
      >
    | undefined;
};

const getComponent = ({ isDrawer = true }: { isDrawer?: boolean }) => {
  const DrawerWrapper = (
    props: DrawerProps & {
      okOnClick: () => void;
      reviewInProgress?: boolean;
      currentReview?: number;
      totalReviewsCount?: number;
      loadEvidence?: (id: string, cb?: () => void) => void;
      onEvidenceRequested?: (evidenceInfo: EvidenceInfo) => void;
      groupByDocument?: (
        extractedMedications: Array<ExtractedMedication>,
      ) => Record<string, Array<ExtractedMedication>>;
      medicationInAction?: Medication;
      validateForm: validateFormType;
      title?: string;
      saveTitle?: string;
      onClose: (cb?: () => void) => void;
      apiLoading?: boolean;
    },
  ) => {
    const {
      loadEvidence,
      onEvidenceRequested,
      totalReviewsCount,
      currentReview,
      okOnClick,
      reviewInProgress,
      groupByDocument,
      medicationInAction,
      validateForm,
      title,
      saveTitle,
      onClose,
      apiLoading,
      ...rest
    } = props;

    const [loading, setLoading] = useState(false);

    const [activeEvidenceId, setActiveEvidenceId] = useState<string>("");

    const { success, errors: errorMessages } = useMemo(validateForm, [
      validateForm,
    ]);

    const onCloseClick = useCallback(
      () =>
        onClose(() => {
          startTransition(() => {
            setActiveEvidenceId("");
            onEvidenceRequested?.({
              documentId:
                medicationInAction?.extractedMedications?.[0]?.documentId || "",
              pageNumber: 0,
              annotations: [],
            });
          });
        }),
      [medicationInAction?.extractedMedications, onClose, onEvidenceRequested],
    );

    return (
      <Drawer
        placement="right"
        {...rest}
        onClose={onCloseClick}
        closeOnOverlayClick={false}
      >
        {/* <DrawerOverlay /> */}
        <DrawerContent>
          <DrawerCloseButton />
          <DrawerHeader padding="16px 24px">
            {reviewInProgress
              ? `Review Medications (${currentReview}/${totalReviewsCount})`
              : title}
          </DrawerHeader>
          {reviewInProgress && (
            <VStack mb={2} alignItems="flex-start" px="24px">
              {errorMessages?.map((message) => (
                <Text
                  fontSize="16px"
                  fontWeight="400"
                  color="var(--Status-ws-status-200, var(--palette-status-ws-status-200, #B02828))"
                  key={message}
                >
                  * {message}
                </Text>
              ))}

              {!errorMessages?.length ? (
                <Text fontSize="16px" fontWeight="400" color="elm.900">
                  Resolved!
                </Text>
              ) : null}
            </VStack>
          )}
          {loading && (
            <OverlayLoader style={{ gap: 0, padding: 0 }} size="xs">
              {null}
            </OverlayLoader>
          )}
          {medicationInAction && loadEvidence && onEvidenceRequested ? (
            <Evidences
              medication={medicationInAction}
              loadEvidence={loadEvidence}
              onEvidenceRequested={onEvidenceRequested}
              onLoading={(loading) => setLoading(Boolean(loading))}
              activeEvidenceId={activeEvidenceId}
              setActiveEvidenceId={setActiveEvidenceId}
              selectFirstByDefault
            />
          ) : null}

          <DrawerBody>{props.children}</DrawerBody>

          <DrawerFooter justifyContent="space-between">
            <TertiaryButton onClick={onCloseClick}>Cancel</TertiaryButton>
            <Button
              colorScheme="blue"
              isDisabled={apiLoading || (reviewInProgress ? !success : false)}
              onClick={okOnClick}
            >
              {reviewInProgress
                ? (currentReview || 0) < (totalReviewsCount || 0)
                  ? "Save & Next"
                  : "Complete Review"
                : saveTitle}
            </Button>
          </DrawerFooter>
        </DrawerContent>
      </Drawer>
    );
  };
  return isDrawer ? DrawerWrapper : Dialog;
};

const createMedicationDialogComponentV2 = (
  title: string,
  saveTitle: string,
  disableKeyFields: boolean,
  isDrawer: true | false = false,
): React.FC<MedicationDialogProps> => {
  return ({
    apiRoot,
    medication = null,
    onSave,
    onCancel,
    isOpen,
    reviewInProgress,
    totalReviewsCount,
    currentReview,
    errorMessages,
    loadEvidence,
    onEvidenceRequested,
    onDelete,
  }: MedicationDialogProps) => {
    const {
      searchMedications,
      getExtractedMedicationV2,
      medicationClassifications,
      busy,
    } = useMedicationsApi({
      apiRoot: apiRoot,
      patientId: "",
      documentsInReview: null,
    });

    const [searchValue, setSearchValue] = useState("");
    const [completionBusy, setCompletionBusy] = useState(false);
    const [apiLoading, setApiLoading] = useState(false);
    const [isMiniMized, setIsMiniMized] = useState(false);
    const [suggestions, setSuggestions] = useState<any[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [formError, setFormError] = useState<string | null>(null);
    const [cachedSearches, setCachedSearches] = useState<CachedSearchDict>({});

    const [medicationInAction, setMedicationInAction] = useState<
      Medication | Partial<Medication> | null
    >(null);

    const [medicationStatuses, setMedicationStatuses] = useState<any[]>([]);

    const [medicationStatusReasons, setMedicationStatusReasons] = useState<
      any[]
    >([]);
    const [medicationStatusReasonUpdated, setMedicationStatusReasonUpdated] =
      useState(false);
    const [changedValues, setChangedValues] = useState<{}>({});

    const controller = useRef<AbortController>();

    const debounceSearch = useDebouncedCallback((value: string) => {
      if (!value?.trim()) {
        setCompletionBusy(false);
        setSuggestions([]);
        setError(null);
        controller.current?.abort("Aborting ongloing request.");
        return;
      }
      setCompletionBusy(true);
      let promise;
      if (cachedSearches[value]) {
        promise = Promise.resolve(cachedSearches[value]);
        controller.current?.abort("Aborting ongloing request.");
      } else {
        // abort any existing call before putting new one.
        controller.current?.abort("Aborting ongloing request.");
        controller.current = new AbortController();
        const signal = controller.current.signal;

        promise = searchMedications(value, signal);
      }

      promise
        .then((results) => {
          setSuggestions(results);
          setCompletionBusy(false);
          setCachedSearches({ ...cachedSearches, [value]: results });
          if (results.length) {
            setError(null);
          } else {
            setError(
              "No Search found. Please try editing search term or mark Unlisted.",
            );
          }
        })
        .catch((error) => {
          if (error === "Aborting ongloing request.") {
            return;
          }
          setSuggestions([]);
          setCompletionBusy(false);
          console.error("Error searching medications:", error);
          setError(error.toString());
        });
    }, 350);

    const searchRef = useRef<any>();

    useEffect(() => {
      setMedicationInAction(medication !== null ? medication : {});
      if (
        (medication as Medication)?.extractedMedications?.[0]
          ?.extractedMedicationId
      ) {
        getExtractedMedicationV2(
          (medication as Medication).extractedMedications[0]
            .extractedMedicationId,
        ).then((response) => {
          setTimeout(() => {
            if (searchRef.current) {
              setSearchValue(response?.medication?.name);
              searchRef.current.focus();
            }
          }, 200);
        });
      } else if (medication?.name?.trim()) {
        setTimeout(() => {
          if (searchRef.current) {
            setSearchValue(medication.name);
            searchRef.current.focus();
          }
        }, 200);
      }
    }, [medication, getExtractedMedicationV2]);

    useEffect(() => {
      setMedicationStatuses(getMedicationStatuses());
      if (medicationInAction?.medicationStatus?.status) {
        setMedicationStatusReasons(
          getMedicationStatusReasons(
            medicationInAction?.medicationStatus?.status,
          ),
        );
      }

      if (
        medicationInAction?.medicationStatus?.statusReason === "other" &&
        !medicationStatusReasonUpdated
      ) {
        //disable update button and message to fill the reason
        setFormError(
          "Please fill/update the reason for none of the above status. If already filled, please ignore",
        );
      } else {
        setFormError(null);
      }
    }, [medicationInAction, medicationStatusReasonUpdated]);

    const config = useConfigData();

    const validateForm: validateFormType = useCallback(() => {
      return validateMedication(
        medicationInAction as Medication,
        config.validationRules || undefined,
      );
    }, [medicationInAction, config.validationRules]);

    useEffect(() => {
      medicationStatusReasonUpdated && setFormError(null);
    }, [medicationStatusReasonUpdated]);

    const autoComplete = useCallback((suggestion: any) => {
      setMedicationInAction((prevValues) => {
        let medicationInAction = { ...prevValues } as Medication;

        medicationInAction.isUnlisted = false;

        if (suggestion.id !== undefined) {
          let medispanId = "" + Math.floor(suggestion.id);
          medicationInAction.medispanId = medispanId;
        } else {
          medicationInAction.medispanId = null;
        }

        if (suggestion.generic_name) {
          medicationInAction.name = suggestion.generic_name;
        }
        if (suggestion.form) {
          medicationInAction.form = suggestion.form;
          medicationInAction.strength =
            suggestion.strength.value + " " + suggestion.strength.unit;
        }
        if (suggestion.route) {
          medicationInAction.route = suggestion.route;
        }

        // setChanged values in case of medication change.
        const tempChangedValues: any = {};
        medicationFieldsLayout.forEach((row) => {
          row.forEach((_column) => {
            const column = _column as keyof Medication;
            if (
              column in medicationInAction &&
              medicationInAction[column] !== null
            ) {
              tempChangedValues[column] = medicationInAction[column];
            }
          });
        });

        setChangedValues(tempChangedValues);
        return medicationInAction;
      });
    }, []);

    useStyles(css);

    const resetStateValues = () => {
      setSuggestions([]);
      setCompletionBusy(false);
      setSuggestions([]);
      setError(null);
      setFormError(null);
      setCachedSearches({});
      setMedicationInAction({} as Medication);
      setMedicationStatuses([]);
      setMedicationStatusReasons([]);
      setMedicationStatusReasonUpdated(false);
      setChangedValues({});
    };

    const checkDisabled = (isUnlisted: boolean, column: string) => {
      if (isUnlisted) {
        return false;
      }

      return ["name", "strength", "route", "form"].includes(column);
    };

    const toast = useToast();

    const clearSearch = useCallback(() => {
      setSuggestions([]);
      controller.current?.abort("Aborting ongloing request.");
      setCompletionBusy(false);
      setSearchValue("");
    }, []);

    const [doTransition, setTransition] = useState(false);

    useLayoutEffect(() => {
      startTransition(() => {
        setTransition(isMiniMized);
      });
    }, [isMiniMized]);

    if (isMiniMized) {
      return (
        <div
          style={{
            position: "fixed",
            right: "44%",
            bottom: "45%",
            zIndex: "100",
            backgroundColor: "white",
            border: "1px solid #ccc",
            borderRadius: "4px",
            padding: "1rem",
            boxShadow: "0 0 10px rgba(0, 0, 0, 0.1)",
            transition: "all 0.5s",
            ...(doTransition ? { right: "10px", bottom: "10px" } : {}),
          }}
        >
          <HStack>
            <Box>
              <SubHeading4>{title}</SubHeading4>
            </Box>
            <Box>
              <Tooltip label="Maximize">
                <ChevronDoubleUp
                  onClick={() => setIsMiniMized(false)}
                  style={{ cursor: "pointer" }}
                />
              </Tooltip>
            </Box>
          </HStack>
        </div>
      );
    }

    const Component = useMemo(
      () => getComponent({ isDrawer }) as React.FC<DrawerProps | DialogProps>,
      [],
    );

    let componentProps: typeof isDrawer extends true
      ? Omit<DrawerProps, "children" | "onClose"> & {
          okOnClick: () => void;
          reviewInProgress?: boolean;
          currentReview?: number;
          totalReviewsCount?: number;
          loadEvidence?: (id: string) => void;
          onEvidenceRequested?: (evidenceInfo: EvidenceInfo) => void;
          medication: Medication;
          medicationInAction: Medication;
          validateForm: validateFormType;
          onClose: (cb?: () => void) => void;
          apiLoading?: boolean;
        }
      : Omit<DialogProps, "children"> = useMemo(() => {
      if (isDrawer) {
        return {
          loadEvidence,
          onEvidenceRequested,
          reviewInProgress,
          currentReview,
          totalReviewsCount,
          placement: "right",
          size: "lg",
          isOpen,
          apiLoading,
          onClose: (cb?: () => void) => {
            resetStateValues();
            onCancel();
            cb?.();
          },
          okOnClick: () => {
            if (apiLoading) {
              return toast({
                title: `Please wait until the current operation finished.`,
                status: "info",
                duration: 5000,
                isClosable: true,
              });
            }
            const { success, errors } = validateForm();

            if (!success) {
              toast({
                title: `Please fix below errors.`,
                description: (
                  <ul>{errors?.map((e) => <li key={e}>{e}</li>)}</ul>
                ),
                status: "error",
                duration: 5000,
                isClosable: true,
              });

              toast({
                title: `Hint.`,
                description:
                  "If error field is disabled, Then try checking Unlisted and fill in details.",
                status: "info",
                duration: 5000,
                isClosable: true,
              });
              return;
            }

            if (reviewInProgress) {
              setApiLoading(true);
              onSave(medicationInAction, changedValues, () => {
                setApiLoading(false);
              });
            } else {
              setApiLoading(true);
              onSave(medicationInAction, changedValues);
              setFormError("");
              setMedicationStatusReasonUpdated(false);
            }
          },
          errorMessages,
          medication,
          validateForm,
          title,
          saveTitle,
          medicationInAction,
        };
      } else {
        return {
          okLabel: saveTitle,
          cancelLabel: "Cancel",
          size: "lg",
          title,
          okOnClick: () => {
            if (apiLoading) {
              return toast({
                title: `Please wait until the current operation finished.`,
                status: "info",
                duration: 5000,
                isClosable: true,
              });
            }
            const { success, errors } = validateForm();

            if (!success) {
              toast({
                title: `Please fix below errors.`,
                description: (
                  <ul>{errors?.map((e) => <li key={e}>{e}</li>)}</ul>
                ),
                status: "error",
                duration: 5000,
                isClosable: true,
              });

              toast({
                title: `Hint.`,
                description:
                  "If error field is disabled, Then try checking Unlisted and fill in details.",
                status: "info",
                duration: 5000,
                isClosable: true,
              });
              return;
            }
            // if (reviewInProgress) {
            //   updateQueue?.current?.push({
            //     func: onSave,
            //     args: [medicationInAction, changedValues],
            //   });
            // } else {
            if (reviewInProgress) {
              onSave(medicationInAction, changedValues);
            } else {
              setApiLoading(true);
              onSave(medicationInAction, changedValues);
              setFormError("");
              setMedicationStatusReasonUpdated(false);
            }

            // }
          },
          cancelOnClick: () => {
            resetStateValues();
            onCancel();
          },
          onClose: () => {
            resetStateValues();
            onCancel();
          },
          isOpen,
        };
      }
    }, [
      apiLoading,
      changedValues,
      currentReview,
      errorMessages,
      isOpen,
      loadEvidence,
      medication,
      medicationInAction,
      onCancel,
      onEvidenceRequested,
      onSave,
      reviewInProgress,
      toast,
      totalReviewsCount,
      validateForm,
    ]);

    const defaultErrorMap = useMemo(
      () => new Map() as ReturnType<validateFormType>["fieldWiseErrors"],
      [],
    );

    const children = useMemo(() => {
      const { fieldWiseErrors: mainFieldWiseErrors } = validateForm();

      const fieldWiseErrors = reviewInProgress
        ? mainFieldWiseErrors
        : defaultErrorMap;

      return (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "1rem",
            position: "relative",
          }}
        >
          <Flex w="100%" direction="column">
            {(apiLoading || busy) && (
              <div
                style={{
                  position: "absolute",
                  inset: "0",
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                  height: "100%",
                  flexDirection: "column",
                  gap: "1rem",
                  padding: "2rem",
                  backgroundColor: "rgba(255, 255, 255, 0.8)",
                  zIndex: "2",
                }}
              >
                <HStack mb={2}>
                  <Spinner
                    thickness="4px"
                    speed="0.65s"
                    emptyColor="gray.200"
                    color="elm.500"
                    size="sm"
                  />
                  <Text>Please wait...</Text>
                </HStack>
              </div>
            )}
            {medication && medication?.isUnlisted ? (
              <HStack>
                <Text color="#B02828">Unlisted / Off Market</Text>
                <Text>
                  Medication was not found in the database so it was classified
                  as an Unlisted/Off Market medication
                </Text>
              </HStack>
            ) : null}
            <HStack w="100%">
              <Checkbox
                isChecked={Boolean(medicationInAction?.isUnlisted)}
                onChange={(event) => {
                  const checked = event.target.checked;
                  if (checked) {
                    if (searchRef.current) {
                      searchRef.current.value = "";
                    }

                    setMedicationInAction((prev) => {
                      return {
                        ...(prev || {}),
                        medispanId: undefined,
                        isUnlisted: true,
                      };
                    });

                    setSuggestions([]);
                  } else {
                    const {
                      id,
                      evidences,
                      extractedMedications,
                      deleted,
                      hostLinked,
                      medicationStatus,
                      medicationType,
                      modifiedBy,
                      origin,
                    } = (medication || {}) as Medication;

                    setMedicationInAction({
                      id,
                      evidences,
                      extractedMedications,
                      isUnlisted: false,
                      deleted,
                      hostLinked,
                      medicationStatus,
                      medicationType,
                      modifiedBy,
                      origin,
                      classification: undefined,
                    } as Medication);

                    setChangedValues((prev: any) => {
                      return {
                        ...prev,
                        classification: null,
                      };
                    });
                  }
                }}
              >
                Unlisted
              </Checkbox>
              <Flex position="relative" w="full">
                <TextInput
                  label="Search"
                  onChange={(event) => {
                    setSearchValue((event.target as any).value);
                    debounceSearch((event.target as any).value);
                  }}
                  onKeyDown={(e) => {
                    if (
                      searchValue &&
                      (e.code === "Escape" || e.key === "Escape")
                    ) {
                      e.preventDefault();
                      e.stopPropagation();
                      clearSearch();
                    }
                  }}
                  inputProps={{
                    ref: searchRef,
                    value: searchValue,
                    defaultValue: "-",
                    isInvalid: fieldWiseErrors?.has("medispanId"),
                  }}
                  isInvalid={fieldWiseErrors?.has("medispanId")}
                  // helpText="Search for medication by name"
                  errorMessage={fieldWiseErrors?.get("medispanId")?.[0]}
                />
                {completionBusy || debounceSearch.isPending() ? (
                  <div
                    style={{
                      position: "absolute",
                      top: "50%",
                      marginTop: "-20px",
                      right: "8px",
                      opacity: debounceSearch.isPending() ? "0.25" : "1",
                    }}
                  >
                    <Spinner size="lg" />
                  </div>
                ) : searchValue ? (
                  <div
                    style={{
                      position: "absolute",
                      top: "50%",
                      marginTop: "-20px",
                      right: "8px",
                      opacity: debounceSearch.isPending() ? "0.25" : "1",
                    }}
                  >
                    <CloseCircleOutline
                      style={{
                        cursor: "pointer",
                        fontSize: "40px",
                      }}
                      onClick={clearSearch}
                    />
                  </div>
                ) : null}
              </Flex>
            </HStack>
            {suggestions.length > 0 ? (
              <div>
                {/* <MedicationSuggestionsTableV2 suggestions={suggestions} /> */}
                <MedicationSuggestionsTable
                  suggestions={suggestions}
                  onSelect={(suggestion) => {
                    autoComplete(suggestion);
                    setSearchValue("");
                    setSuggestions([]);
                  }}
                />
              </div>
            ) : error !== null ? (
              <div>{error}</div>
            ) : null}
          </Flex>

          {formError ? <div style={{ color: "red" }}>{formError}</div> : null}
          {medicationInAction &&
            medicationFieldsLayout.map((row) => (
              <div
                key={row.join("-")}
                style={{ display: "flex", flexDirection: "row", gap: "1rem" }}
              >
                {row.map((column) => {
                  const value =
                    medicationInAction[
                      column as keyof typeof medicationInAction
                    ];

                  let input = (
                    <TextInput
                      isDisabled={
                        disableKeyFields ||
                        checkDisabled(
                          Boolean(medicationInAction?.isUnlisted),
                          column,
                        )
                      }
                      isRequired={[
                        "name",
                        medicationInAction?.isUnlisted ? "" : "dosage",
                      ].includes(column)}
                      key={column}
                      label={
                        column === "dosage"
                          ? "Amount/Dose"
                          : capitalizeWords(column)
                      }
                      onInput={(event) => {
                        let value = (event.target as any).value;
                        let medicationInActionTemp = {
                          ...medicationInAction,
                          [column]: value,
                        };
                        setMedicationInAction(medicationInActionTemp);
                        setChangedValues({
                          ...changedValues,
                          [column]: value.trim(),
                        });
                      }}
                      inputProps={{
                        defaultValue: "-",
                        value: value?.toString() || "",
                        isInvalid: fieldWiseErrors?.has(
                          column as KeyOfMap<typeof fieldWiseErrors>,
                        ),
                      }}
                      isInvalid={fieldWiseErrors?.has(
                        column as KeyOfMap<typeof fieldWiseErrors>,
                      )}
                      errorMessage={
                        fieldWiseErrors?.get(
                          column as KeyOfMap<typeof fieldWiseErrors>,
                        )?.[0]
                      }
                    />
                  );
                  if (column === "name") {
                    return (
                      <div
                        style={{
                          display: "flex",
                          flex: "1",
                          flexDirection: "column",
                        }}
                        key={column}
                      >
                        <div style={{ position: "relative" }}>{input}</div>
                      </div>
                    );
                  }
                  if (column === "startDate" || column === "discontinuedDate") {
                    const value =
                      medicationInAction[
                        column as keyof typeof medicationInAction
                      ];

                    let dateValue;
                    try {
                      dateValue = value
                        ? new Date(value?.toString())
                            .toISOString()
                            .substr(0, 10)
                        : "";
                    } catch (error) {
                      dateValue = "";
                    }
                    input = (
                      <FormControl>
                        <label
                          style={{
                            fontSize: "13px",
                            color: "var(--chakra-colors-bigStone-400)",
                          }}
                        >
                          {capitalizeWords(column)}
                          {column === "startDate" ? (
                            <span
                              style={{
                                color: "red",
                                fontSize: "10",
                                marginLeft: "4",
                              }}
                            >
                              *
                            </span>
                          ) : null}
                        </label>
                        <Input
                          isDisabled={disableKeyFields}
                          size="md"
                          type="date"
                          key={column}
                          placeholder={capitalizeWords(column)}
                          isRequired={"startDate" === column}
                          onInput={(event) => {
                            let value: string | null = null;
                            if ((event.target as any).value) {
                              value = (event.target as any).value.replace(
                                /-/g,
                                "/",
                              ) as string;
                              value = new Date(value).toLocaleDateString(
                                "en-US",
                                {
                                  year: "numeric",
                                  month: "2-digit",
                                  day: "2-digit",
                                },
                              );
                            }

                            let medicationInActionTemp = {
                              ...medicationInAction,
                              [column]: value?.trim(),
                            };
                            setMedicationInAction(medicationInActionTemp);
                            setChangedValues({
                              ...changedValues,
                              [column]: value?.trim(),
                            });
                          }}
                          value={dateValue}
                          isInvalid={fieldWiseErrors?.has(
                            column as KeyOfMap<typeof fieldWiseErrors>,
                          )}
                        />
                        {fieldWiseErrors?.has(
                          column as KeyOfMap<typeof fieldWiseErrors>,
                        ) && (
                          <div>
                            <Box ms="1.5" mt="0.5">
                              <Para3R color="status.200">
                                {
                                  fieldWiseErrors?.get(
                                    column as KeyOfMap<typeof fieldWiseErrors>,
                                  )?.[0]
                                }
                              </Para3R>
                            </Box>
                          </div>
                        )}{" "}
                      </FormControl>
                    );
                  }
                  if (column === "instructions_textarea") {
                    input = (
                      <TextArea
                        key={column}
                        label={capitalizeWords(column)}
                        onInput={(event) => {
                          let value = (event.target as any).value;
                          let medicationInActionTemp = {
                            ...medicationInAction,
                            [column as any]: value,
                          };
                          setMedicationInAction(medicationInActionTemp);
                          setChangedValues({
                            ...changedValues,
                            [column]: value.trim(),
                          });
                        }}
                      />
                    );
                  }
                  if (column === "medicationClassification") {
                    input = medicationInAction?.isUnlisted ? (
                      <div style={{ width: "100%" }}>
                        <Select
                          label="Medication Classification"
                          placeholder="Medication Classification"
                          width="100%"
                          isRequired
                          key={column}
                          value={medicationInAction?.classification}
                          onChange={(e) => {
                            let value = (e.target as any).value;
                            let medicationInActionTemp = {
                              ...medicationInAction,
                              classification: value,
                            };
                            setMedicationInAction(medicationInActionTemp);
                            setChangedValues({
                              ...changedValues,
                              classification: value,
                            });
                          }}
                        >
                          {medicationClassifications?.map((code) => {
                            return (
                              <option value={code.code} key={code.code}>
                                {code.value}
                              </option>
                            );
                          })}
                        </Select>
                        {fieldWiseErrors?.has("classification") && (
                          <div>
                            <Box ms="1.5" mt="0.5">
                              <Para3R color="status.200">
                                {fieldWiseErrors?.get("classification")?.[0]}
                              </Para3R>
                            </Box>
                          </div>
                        )}{" "}
                      </div>
                    ) : (
                      <></>
                    );
                  }
                  if (column === "Status") {
                    input = (
                      <>
                        <div style={{ width: "100px" }}>Medication Status</div>
                        <Select
                          width={"500px"}
                          key={column}
                          value={medicationInAction?.medicationStatus?.status}
                          onChange={(e) => {
                            let value = (e.target as any).value;
                            let medicationInActionTemp = {
                              ...medicationInAction,
                              medicationStatus: {
                                ...medicationInAction.medicationStatus,
                                statusReasonExplaination:
                                  medicationInAction.medicationStatus
                                    ?.statusReasonExplaination || "",
                                status: value || "",
                                statusReason:
                                  medicationInAction.medicationStatus
                                    ?.statusReason || "",
                              },
                            };
                            setMedicationInAction(medicationInActionTemp);
                            setChangedValues({
                              ...changedValues,
                              [column]: value,
                            });
                          }}
                        >
                          <>
                            <option value="not_annotated_yet">--</option>
                            {medicationStatuses?.map((reason: any) => {
                              return (
                                <>
                                  <option value={reason.value}>
                                    {reason.text}
                                  </option>
                                </>
                              );
                            })}
                          </>
                        </Select>
                      </>
                    );
                  }
                  if (column === "StatusReason") {
                    if (
                      medicationStatusReasons &&
                      medicationStatusReasons.length > 0
                    ) {
                      input = (
                        <>
                          <div style={{ width: "100px" }}>
                            Medication Status Reason
                          </div>
                          <Select
                            width={"500px"}
                            key={column}
                            value={
                              medicationInAction?.medicationStatus?.statusReason
                            }
                            onChange={(e) => {
                              let value = (e.target as any).value;
                              let medicationInActionTemp = {
                                ...medicationInAction,
                                medicationStatus: {
                                  ...medicationInAction.medicationStatus,
                                  statusReasonExplaination:
                                    medicationInAction.medicationStatus
                                      ?.statusReasonExplaination || "",
                                  status:
                                    medicationInAction.medicationStatus
                                      ?.status || "",
                                  statusReason: value || "",
                                },
                              };
                              setMedicationInAction(medicationInActionTemp);
                              setChangedValues({
                                ...changedValues,
                                [column]: value,
                              });
                            }}
                          >
                            <>
                              <option value="">--</option>
                              {medicationStatusReasons?.map((reason: any) => {
                                return (
                                  <>
                                    <option value={reason.value}>
                                      {reason.text}
                                    </option>
                                  </>
                                );
                              })}
                            </>
                          </Select>
                        </>
                      );
                    } else {
                      input = <></>;
                    }
                  }
                  if (column === "StatusReasonExplaination") {
                    input = (
                      <>
                        <TextInput
                          key={column}
                          label={capitalizeWords(column)}
                          onInput={(e) => {
                            let value = (e.target as any).value;
                            let medicationInActionTemp = {
                              ...medicationInAction,
                              medicationStatus: {
                                ...medicationInAction.medicationStatus,
                                statusReasonExplaination: value || "",
                                status:
                                  medicationInAction.medicationStatus?.status ||
                                  "",
                                statusReason:
                                  medicationInAction.medicationStatus
                                    ?.statusReason || "",
                              },
                            };

                            setMedicationInAction(medicationInActionTemp);
                            setMedicationStatusReasonUpdated(true);
                            setChangedValues({
                              ...changedValues,
                              [column]: value,
                            });
                          }}
                          inputProps={{
                            defaultValue: "-",
                            value:
                              medicationInAction.medicationStatus
                                ?.statusReasonExplaination || "",
                          }}
                        />
                      </>
                    );
                  }
                  return input;
                })}
              </div>
            ))}
          {medicationInAction && onDelete && (
            <Flex justify="flex-end">
              <SecondaryButton
                color="elm.500"
                onClick={() => {
                  setApiLoading(true);
                  onDelete?.(() => {
                    setApiLoading(false);
                  });
                }}
              >
                <Delete />
                Delete Medication
              </SecondaryButton>
            </Flex>
          )}
        </div>
      );
    }, [
      validateForm,
      reviewInProgress,
      defaultErrorMap,
      apiLoading,
      busy,
      medication,
      medicationInAction,
      searchValue,
      completionBusy,
      debounceSearch,
      clearSearch,
      suggestions,
      error,
      formError,
      onDelete,
      autoComplete,
      changedValues,
      medicationClassifications,
      medicationStatuses,
      medicationStatusReasons,
    ]);

    return <Component {...componentProps}>{children}</Component>;
  };
};

export const AddMedicationV2 = createMedicationDialogComponentV2(
  "Add Medication",
  "Create",
  false,
  true,
);
export const EditMedicationV2 = createMedicationDialogComponentV2(
  "Edit Medication",
  "Update",
  false,
  true,
);
export const DeleteMedicationV2 = ({
  medication,
  onDelete,
  onCancel,
}: {
  medication: any;
  onDelete: (medication: any) => void;
  onCancel: () => void;
}) => {
  return (
    <Dialog
      okLabel="Confirm deletion"
      cancelLabel="Cancel"
      okOnClick={() => onDelete(medication)}
      cancelOnClick={onCancel}
      onClose={onCancel}
      title="Delete Medication"
      size="sm"
      isOpen={medication !== null}
    >
      {medication !== null ? (
        <div>Are you sure you want to delete "{medication.name}"?</div>
      ) : null}
    </Dialog>
  );
};

export const ExitConfirmation = ({
  isOpen,
  onOk,
  onCancel,
}: {
  isOpen: boolean;
  onOk: () => void;
  onCancel: () => void;
}) => {
  return (
    <Dialog
      okLabel="Exit"
      cancelLabel="Cancel"
      okOnClick={onOk}
      cancelOnClick={onCancel}
      onClose={onCancel}
      title="Exit"
      size="sm"
      isOpen={isOpen}
    >
      {isOpen ? <div>Are you sure you want to Exit?</div> : null}
    </Dialog>
  );
};

export const UploadDialog = ({
  isOpen,
  onOk,
  onCancel,
  env,
  patientId,
  onFileUploaded,
}: {
  isOpen: boolean;
  onOk: () => void;
  onCancel: () => void;
  env: Env;
  patientId: string;
  onFileUploaded?: (file: File) => void;
}) => {
  return (
    <Dialog
      okLabel={undefined}
      cancelLabel="Cancel"
      okOnClick={onOk}
      cancelOnClick={onCancel}
      onClose={onCancel}
      title="Select Document"
      size="lg"
      isOpen={isOpen}
    >
      <Flex direction={"column"} gap={"1rem"}>
        <Heading size="sm">
          Upload a document or select an existing document to begin
        </Heading>

        <Block style={{ padding: "1rem", flex: "0 1 auto" }}>
          <UploadArea
            env={env}
            patientId={patientId}
            onFileUploaded={onFileUploaded}
          />
        </Block>
      </Flex>
    </Dialog>
  );
};
