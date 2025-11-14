import { FormControl, Input, Box, useToast } from "@chakra-ui/react";
import {
  TextArea,
  TextInput,
  Para3R,
  Select,
} from "@mediwareinc/wellsky-dls-react";
import {
  useCallback,
  OptionHTMLAttributes,
  useEffect,
  useMemo,
  useState,
  startTransition,
} from "react";
import {
  EvidenceInfo,
  Medication,
  MedicationFormFields,
  validateFormType,
} from "types";
import { capitalizeWords } from "utils/i18n";
import {
  getMedicationStatuses,
  getMedicationStatusReasons,
  medicationFieldsLayout,
  useMedicationsApi,
} from "./useMedicationsApi";
import { validateMedication } from "utils/helpers";
import useSearchMedication from "./useSearchMedication";
import { useConfigData } from "context/AppConfigContext";

function useAddEditMedications({
  medication,
  reviewInProgress,
  onSave,
  onCancel,
  disableKeyFields,
  apiRoot,
  onEvidenceRequested,
  activeEvidenceId,
  setActiveEvidenceId,
}: {
  medication: Medication | null;
  reviewInProgress?: boolean;
  onSave: (medication: any, changedValues: any | null, cb?: () => void) => void;
  onCancel: () => void;
  onEvidenceRequested?: (evidenceInfo: EvidenceInfo) => void;
  disableKeyFields?: boolean;
  apiRoot: string;
  activeEvidenceId: string;
  setActiveEvidenceId: (id: string | ((prev: string) => string)) => void;
}) {
  const isRealMedication = Object.keys(medication || {}).length > 0;
  const [loading, setLoading] = useState(false);
  const [apiLoading, setApiLoading] = useState(false);

  const [formError, setFormError] = useState<string | null>(null);

  const [medicationInAction, setMedicationInAction] = useState<
    Medication | Partial<Medication> | null
  >(null);

  const [medicationStatuses, setMedicationStatuses] = useState<any[]>([]);

  const [medicationStatusReasons, setMedicationStatusReasons] = useState<any[]>(
    [],
  );
  const [medicationStatusReasonUpdated, setMedicationStatusReasonUpdated] =
    useState(false);
  const [changedValues, setChangedValues] = useState<{}>({});

  const config = useConfigData();

  const validateForm: validateFormType = useCallback(() => {
    return validateMedication(
      medicationInAction as Medication,
      config.validationRules,
    );
  }, [medicationInAction, config.validationRules]);

  const { success, errors: errorMessages } = useMemo(validateForm, [
    validateForm,
  ]);

  const defaultErrorMap = useMemo(
    () => new Map() as ReturnType<validateFormType>["fieldWiseErrors"],
    [],
  );

  const { fieldWiseErrors: mainFieldWiseErrors } = validateForm();

  const fieldWiseErrors =
    reviewInProgress && isRealMedication
      ? mainFieldWiseErrors
      : defaultErrorMap;

  const checkDisabled = useCallback((isUnlisted: boolean, column: string) => {
    if (isUnlisted) {
      return false;
    }

    return ["name", "strength", "route", "form"].includes(column);
  }, []);

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

  const {
    suggestions,
    renderSearchInput,
    searchRef,
    setSearchValue,
    clearSuggestions,
    error,
  } = useSearchMedication({
    searchMedications,
  });

  const toast = useToast();

  const okOnClick = useCallback(() => {
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
        description: <ul>{errors?.map((e) => <li key={e}>{e}</li>)}</ul>,
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
        setSearchValue("");
        setApiLoading(false);
      });
    } else {
      setApiLoading(true);
      onSave(medicationInAction, changedValues);
      setFormError("");
      setMedicationStatusReasonUpdated(false);
    }
  }, [
    apiLoading,
    changedValues,
    medicationInAction,
    onSave,
    reviewInProgress,
    setSearchValue,
    toast,
    validateForm,
  ]);

  useEffect(() => {
    setMedicationInAction(medication !== null ? medication : {});

    setTimeout(() => {
      if (searchRef.current) {
        setSearchValue((medication?.name ?? medication?.name_original) || "");
        searchRef.current.focus();
      }
    }, 200);
  }, [medication, getExtractedMedicationV2, searchRef, setSearchValue]);

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

  const autoComplete = useCallback((suggestion: any) => {
    setMedicationInAction((prevValues) => {
      let medicationInAction = { ...prevValues } as Medication;

      medicationInAction.isUnlisted = false;

      if (suggestion.id !== undefined) {
        const numericId = Number(suggestion.id);
        let medispanId = isNaN(numericId)
          ? suggestion.id.toString()
          : "" + Math.floor(numericId);
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

  const generateTextInput = useCallback(
    (
      column: Exclude<
        MedicationFormFields,
        "statusReason" | "startDate" | "classification" | "discontinuedDate"
      >,
      label?: string,
      isTextArea?: boolean,
    ) => {
      const fieldValue = medicationInAction?.[column];

      const Component = isTextArea ? TextArea : TextInput;

      return (
        <Component
          isDisabled={
            disableKeyFields ||
            checkDisabled(Boolean(medicationInAction?.isUnlisted), column)
          }
          isRequired={
            (column === "name" && config.validationRules?.validateName) ||
            (column === "dosage" &&
              config.validationRules?.validateDosage &&
              !medicationInAction?.isUnlisted &&
              !medicationInAction?.isNonStandardDose)
          }
          label={label || capitalizeWords(column)}
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
            value: fieldValue?.toString() || "",
            isInvalid: fieldWiseErrors?.has(column),
          }}
          isInvalid={fieldWiseErrors?.has(column)}
          errorMessage={fieldWiseErrors?.get(column)?.[0]}
        />
      );
    },
    [
      changedValues,
      checkDisabled,
      config.validationRules?.validateDosage,
      config.validationRules?.validateName,
      disableKeyFields,
      fieldWiseErrors,
      medicationInAction,
    ],
  );

  const generateDateInput = useCallback(
    (
      column: Extract<MedicationFormFields, "startDate" | "discontinuedDate">,
      label?: string | null,
    ) => {
      const value = medicationInAction?.[column];

      const isRequired =
        column === "startDate" &&
        config.validationRules?.validateDates &&
        !medicationInAction?.isLongStanding;

      let dateValue;
      try {
        dateValue = value
          ? new Date(value?.toString()).toISOString().substr(0, 10)
          : "";
      } catch (error) {
        dateValue = "";
      }
      const input = (
        <FormControl padding="4px 8px" backgroundColor="rgba(0, 0, 0, 0.04)">
          <label
            style={{
              fontSize: "13px",
              color: "var(--chakra-colors-bigStone-400)",
              fontWeight: "500",
            }}
          >
            {label || capitalizeWords(column)}
            {isRequired ? (
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
            border="none"
            padding={0}
            key={column}
            focusBorderColor="none"
            _focusVisible={{
              boxShadow: "none",
            }}
            placeholder={capitalizeWords(column)}
            isRequired={"startDate" === column}
            onInput={(event) => {
              let value: string | null = null;
              if ((event.target as any).value) {
                value = (event.target as any).value.replace(
                  /-/g,
                  "/",
                ) as string;
                value = new Date(value).toLocaleDateString("en-US", {
                  year: "numeric",
                  month: "2-digit",
                  day: "2-digit",
                });
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
            isInvalid={fieldWiseErrors?.has(column)}
          />
          {fieldWiseErrors?.has(column) && (
            <div>
              <Box ms="1.5" mt="0.5">
                <Para3R color="status.200">
                  {fieldWiseErrors?.get(column)?.[0]}
                </Para3R>
              </Box>
            </div>
          )}{" "}
        </FormControl>
      );
      return input;
    },
    [
      changedValues,
      config.validationRules?.validateDates,
      disableKeyFields,
      fieldWiseErrors,
      medicationInAction,
    ],
  );

  const generateSelectInput = useCallback(
    (
      column: Extract<MedicationFormFields, "classification">,
      label?: string | null,
      options?: {
        label: string | number;
        value: OptionHTMLAttributes<any>["value"];
      }[],
      isRequired?: boolean,
    ) => {
      const labelText = label || capitalizeWords(column);
      const placeholderText = isRequired
        ? `Select ${labelText} *`
        : `Select ${labelText}`;
      return (
        <div style={{ width: "100%" }}>
          <Select
            label={labelText}
            placeholder={placeholderText}
            width="100%"
            isRequired={Boolean(isRequired)}
            key={column}
            value={medicationInAction?.[column]}
            onChange={(e) => {
              let value = (e.target as any).value;
              let medicationInActionTemp = {
                ...medicationInAction,
                [column]: value,
              };
              setMedicationInAction(medicationInActionTemp);
              setChangedValues({
                ...changedValues,
                [column]: value,
              });
            }}
          >
            {options?.map((code, index) => {
              return (
                <option
                  value={code.value}
                  key={JSON.stringify(code.value) || index}
                >
                  {code.label}
                </option>
              );
            })}
          </Select>
          {fieldWiseErrors?.has(column) && (
            <div>
              <Box ms="1.5" mt="0.5">
                <Para3R color="status.200">
                  {fieldWiseErrors?.get(column)?.[0]}
                </Para3R>
              </Box>
            </div>
          )}{" "}
        </div>
      );
    },
    [changedValues, fieldWiseErrors, medicationInAction],
  );

  const resetStateValues = useCallback(() => {
    setFormError(null);
    setMedicationInAction({} as Medication);
    setMedicationStatuses([]);
    setMedicationStatusReasons([]);
    setMedicationStatusReasonUpdated(false);
    setChangedValues({});
  }, []);

  const onCloseClick = useCallback(() => {
    resetStateValues();
    onCancel();
    startTransition(() => {
      setActiveEvidenceId("");
      onEvidenceRequested?.({
        documentId:
          medicationInAction?.extractedMedications?.filter(
            (m) => m.extractedMedicationId === activeEvidenceId,
          )?.[0]?.documentId || "",
        pageNumber: 0,
        annotations: [],
      });
    });
  }, [
    activeEvidenceId,
    medicationInAction?.extractedMedications,
    onCancel,
    onEvidenceRequested,
    resetStateValues,
    setActiveEvidenceId,
  ]);

  return {
    medicationInAction,
    setMedicationInAction,
    autoComplete,
    generateTextInput,
    generateDateInput,
    generateSelectInput,
    okOnClick,
    onCloseClick,
    renderSearchInput,
    suggestions,
    error,
    loading,
    formError,
    medicationStatuses,
    medicationStatusReasons,
    setMedicationStatusReasons,
    setMedicationStatusReasonUpdated,
    activeEvidenceId,
    setActiveEvidenceId,
    resetStateValues,
    errorMessages,
    setLoading,
    setSearchValue,
    clearSuggestions,
    apiLoading,
    busy,
    medicationClassifications,
    searchRef,
    setChangedValues,
    setApiLoading,
    success,
    isRealMedication,
  };
}

export default useAddEditMedications;
