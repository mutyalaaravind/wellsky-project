import { useCallback, useEffect, useState } from "react";

import {
  Dialog,
  Select,
  Spinner,
  TextInput,
} from "@mediwareinc/wellsky-dls-react";

import {
  getMedicationStatuses,
  getMedicationStatusReasons,
  medicationFieldsLayout,
  useMedicationsApi,
} from "hooks/useMedicationsApi";
import { capitalizeWords } from "utils/i18n";
import {
  Table,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
} from "@chakra-ui/react";

import css from "./Dialogs.css";
import { useDebouncedCallback } from "use-debounce";
import { useStyles } from "hooks/useStyles";

type MedicationDialogProps = {
  apiRoot: string;
  medication?: any;
  isOpen: boolean;
  onSave: (medication: any) => void;
  onCancel: () => void;
};

type CachedSearchDict = {
  [key: string]: any[];
};

const createMedicationDialogComponent = (
  title: string,
  saveTitle: string,
): React.FC<MedicationDialogProps> => {
  return ({
    apiRoot,
    medication = null,
    onSave,
    onCancel,
    isOpen,
  }: MedicationDialogProps) => {
    const { searchMedications } = useMedicationsApi({
      apiRoot: apiRoot,
      patientId: "",
      documentsInReview: null,
    });
    const [completionBusy, setCompletionBusy] = useState(false);
    const [suggestions, setSuggestions] = useState<any[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [formError, setFormError] = useState<string | null>(null);
    const [cachedSearches, setCachedSearches] = useState<CachedSearchDict>({});

    const [values, setValues] = useState<any>({});
    const [medicationStatuses, setMedicationStatuses] = useState<any[]>([]);
    const [medicationStatusReasons, setMedicationStatusReasons] = useState<
      any[]
    >([]);
    const [medicationStatusReasonUpdated, setMedicationStatusReasonUpdated] =
      useState(false);
    const debounceSearch = useDebouncedCallback((value: string) => {
      setCompletionBusy(true);
      let promise;
      if (cachedSearches[value]) {
        promise = Promise.resolve(cachedSearches[value]);
      } else {
        promise = searchMedications(value);
      }
      promise
        .then((results) => {
          setSuggestions(results);
          setCompletionBusy(false);
          setCachedSearches({ ...cachedSearches, [value]: results });
          setError(null);
        })
        .catch((error) => {
          setSuggestions([]);
          setCompletionBusy(false);
          console.error("Error searching medications:", error);
          setError(error.toString());
        });
    }, 350);

    useEffect(() => {
      setValues(medication !== null ? medication : {});
    }, [medication]);

    useEffect(() => {
      setMedicationStatuses(getMedicationStatuses());
      setMedicationStatusReasons(
        getMedicationStatusReasons(values?.["medication_status"]),
      );

      if (
        values?.["medication_status_reason"] === "other" &&
        !medicationStatusReasonUpdated
      ) {
        //disable update button and message to fill the reason
        setFormError(
          "Please fill/update the reason for none of the above status. If already filled, please ignore",
        );
      } else {
        setFormError(null);
      }
    }, [values, medicationStatusReasonUpdated]);

    useEffect(() => {
      medicationStatusReasonUpdated && setFormError(null);
    }, [medicationStatusReasonUpdated]);

    const autoComplete = useCallback((suggestion: any) => {
      setValues((prevValues: any) => {
        let values = { ...prevValues };
        if (suggestion.generic_name) {
          values.name = suggestion.generic_name;
        }
        if (suggestion.form) {
          values.dosage =
            suggestion.strength.value + " " + suggestion.strength.unit;
        }
        if (suggestion.route) {
          values.route = suggestion.route;
        }
        return values;
      });
    }, []);

    useStyles(css);

    return (
      <Dialog
        okLabel={saveTitle}
        cancelLabel="Cancel"
        size="lg"
        title={title}
        okOnClick={() => {
          onSave(values);
          setValues({});
          setFormError("");
          setMedicationStatusReasonUpdated(false);
        }}
        cancelOnClick={onCancel}
        onClose={onCancel}
        isOpen={isOpen}
      >
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          {formError ? <div style={{ color: "red" }}>{formError}</div> : null}
          {medicationFieldsLayout.map((row) => (
            <div
              key={row.join("-")}
              style={{ display: "flex", flexDirection: "row", gap: "1rem" }}
            >
              {row.map((column) => {
                let input = (
                  <TextInput
                    key={column}
                    label={capitalizeWords(column)}
                    onInput={(event) => {
                      setValues({
                        ...values,
                        [column]: (event.target as any).value,
                      });
                      if (
                        column === "name" &&
                        (event.target as any).value.length > 0
                      ) {
                        debounceSearch((event.target as any).value);
                      }
                    }}
                    inputProps={{
                      defaultValue: "-",
                      value: values[column] || "",
                    }}
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
                      <div style={{ position: "relative" }}>
                        {input}
                        {completionBusy || debounceSearch.isPending() ? (
                          <div
                            style={{
                              position: "absolute",
                              top: "50%",
                              marginTop: "-20px",
                              right: "8px",
                              opacity: debounceSearch.isPending()
                                ? "0.25"
                                : "1",
                            }}
                          >
                            <Spinner size="lg" />
                          </div>
                        ) : null}
                      </div>
                      {suggestions.length > 0 ? (
                        <div>
                          <TableContainer className="medication-autocomplete-table">
                            <Table size="sm" variant="striped">
                              <Thead>
                                <Tr>
                                  <Th>Generic Name</Th>
                                  <Th>Brand Name</Th>
                                  <Th>Route</Th>
                                  <Th>Form</Th>
                                  <Th>Strength</Th>
                                  <Th>Packaging</Th>
                                </Tr>
                              </Thead>
                              <Tbody>
                                {suggestions.map((suggestion) => (
                                  <Tr
                                    key={suggestion.toString()}
                                    style={{ cursor: "pointer" }}
                                    onClick={() => {
                                      autoComplete(suggestion);
                                      setSuggestions([]);
                                    }}
                                  >
                                    <Td>{suggestion.generic_name}</Td>
                                    <Td>{suggestion.brand_name}</Td>
                                    <Td>{suggestion.route}</Td>
                                    <Td>{suggestion.form}</Td>
                                    <Td>
                                      {suggestion.strength.value}{" "}
                                      {suggestion.strength.unit}
                                    </Td>
                                    <Td>
                                      {suggestion.package.value}{" "}
                                      {suggestion.package.unit}
                                    </Td>
                                  </Tr>
                                ))}
                              </Tbody>
                            </Table>
                          </TableContainer>
                        </div>
                      ) : error !== null ? (
                        <div>{error}</div>
                      ) : null}
                    </div>
                  );
                }
                if (column === "medication_status") {
                  input = (
                    <>
                      <div style={{ width: "100px" }}>Medication Status</div>
                      <Select
                        width={"500px"}
                        key={column}
                        value={values?.[column]}
                        onChange={(e) => {
                          setValues({
                            ...values,
                            [column]: (e.target as any).value,
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
                if (column === "medication_status_reason") {
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
                          value={values?.[column]}
                          onChange={(e) => {
                            setValues({
                              ...values,
                              [column]: (e.target as any).value,
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
                if (column === "medication_status_reason_explaination") {
                  input = (
                    <>
                      <TextInput
                        key={column}
                        label={capitalizeWords(column)}
                        onInput={(event) => {
                          setValues({
                            ...values,
                            [column]: (event.target as any).value,
                          });
                          setMedicationStatusReasonUpdated(true);
                        }}
                        inputProps={{
                          defaultValue: "-",
                          value: values[column] || "",
                        }}
                      />
                    </>
                  );
                }
                return input;
              })}
            </div>
          ))}
        </div>
      </Dialog>
    );
  };
};

export const AddMedication = createMedicationDialogComponent(
  "Add Medication",
  "Create",
);
export const EditMedication = createMedicationDialogComponent(
  "Edit Medication",
  "Update",
);
export const DeleteMedication = ({
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
