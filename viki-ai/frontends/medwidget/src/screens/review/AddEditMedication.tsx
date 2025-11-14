import {
  Spinner,
  Checkbox,
  TertiaryButton,
  SecondaryButton,
} from "@mediwareinc/wellsky-dls-react";

import css from "./Dialogs.css";

import {
  Button,
  Drawer,
  DrawerBody,
  DrawerCloseButton,
  DrawerContent,
  DrawerFooter,
  DrawerHeader,
  DrawerOverlay,
  DrawerProps,
  Flex,
  HStack,
  Text,
  VStack,
} from "@chakra-ui/react";

import { EvidenceInfo, ExtractedMedication, Medication } from "types";
import MedicationSuggestionsTable from "./MedicationSuggestionsTable";
import { Delete } from "@mediwareinc/wellsky-dls-react-icons";
import OverlayLoader from "./OverlayLoader";
import Evidences from "components/Evidences";
import { useStyles } from "hooks/useStyles";
import useAddEditMedications from "hooks/useAddEditMedications";
import { usePatientProfileStore } from "store/patientProfileStore";
import { useCallback } from "react";
// import MedicationSuggestionsTableV2 from "./MedicationSuggestionsTableV2";

type MedicationDialogProps = {
  apiRoot: string;
  medication?: Medication | null;
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
  disableKeyFields?: boolean;
  activeEvidenceId?: string;
  setActiveEvidenceId?: (id: string | ((prev: string) => string)) => void;
};

const AddEditMedication = (
  props: Omit<DrawerProps, "onClose" | "children"> & {
    reviewInProgress?: boolean;
    currentReview?: number;
    totalReviewsCount?: number;
    loadEvidence?: (id: string, cb?: () => void) => void;
    onEvidenceRequested?: (evidenceInfo: EvidenceInfo) => void;
    groupByDocument?: (
      extractedMedications: Array<ExtractedMedication>,
    ) => Record<string, Array<ExtractedMedication>>;
    medicationInAction?: Medication;
    apiLoading?: boolean;
  } & MedicationDialogProps,
) => {
  const {
    loadEvidence,
    onEvidenceRequested,
    totalReviewsCount,
    currentReview,
    reviewInProgress,
    groupByDocument,
    apiRoot,
    medication = null,
    onSave,
    onCancel,
    isOpen,
    onDelete,
    disableKeyFields = false,
    ...rest
  } = props;

  const title = Boolean(medication) ? "Edit Medication" : "Add Medication";
  const saveTitle = Boolean(medication) ? "Update" : "Create";
  const { config } = usePatientProfileStore();

  const {
    suggestions,
    autoComplete,
    error,
    onCloseClick,
    errorMessages,
    medicationInAction,
    activeEvidenceId,
    formError,
    generateDateInput,
    generateSelectInput,
    generateTextInput,
    loading,
    okOnClick,
    renderSearchInput,
    setActiveEvidenceId,
    setLoading,
    setMedicationInAction,
    setSearchValue,
    clearSuggestions,
    apiLoading,
    busy,
    searchRef,
    medicationClassifications,
    setChangedValues,
    setApiLoading,
    success,
    isRealMedication,
  } = useAddEditMedications({
    medication,
    onSave,
    onCancel,
    apiRoot,
    disableKeyFields,
    reviewInProgress,
    onEvidenceRequested,
    activeEvidenceId: rest.activeEvidenceId || "",
    setActiveEvidenceId: rest.setActiveEvidenceId || (() => {}),
  });

  useStyles(css);

  const showDrawerOverlay = false;

  const enableNonstandardDosageCheckbox = config?.uiNonstandardDoseEnable;
  const onEvidenceLoading = useCallback(
    (loading?: Boolean) => setLoading(Boolean(loading)),
    [setLoading],
  );

  return (
    <Drawer
      isOpen={isOpen}
      placement="right"
      size="lg"
      {...rest}
      onClose={onCloseClick}
      closeOnOverlayClick={false}
    >
      {showDrawerOverlay && <DrawerOverlay />}
      <DrawerContent
        data-pendoid={`${title.toLocaleLowerCase().replace(" ", "-")}-drawer-content`}
      >
        <DrawerCloseButton data-pendoid="modal-close-button" />
        <DrawerHeader padding="16px 24px">
          {reviewInProgress
            ? `Review Medications (${currentReview}/${totalReviewsCount})`
            : title}
        </DrawerHeader>
        {reviewInProgress && isRealMedication && (
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
        {Boolean(medicationInAction?.extractedMedications?.length) &&
        loadEvidence &&
        onEvidenceRequested ? (
          <Evidences
            medication={medicationInAction as Medication}
            loadEvidence={loadEvidence}
            onEvidenceRequested={onEvidenceRequested}
            onLoading={onEvidenceLoading}
            activeEvidenceId={activeEvidenceId}
            setActiveEvidenceId={setActiveEvidenceId}
            selectFirstByDefault
            data-pendoid="evidences"
          />
        ) : null}

        <DrawerBody>
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
                    Medication was not found in the database so it was
                    classified as an Unlisted/Off Market medication
                  </Text>
                </HStack>
              ) : null}

              <Flex w="100%" justify="flex-end" direction="row" gap={2} mb={2}>
                {enableNonstandardDosageCheckbox &&
                  !medicationInAction?.isUnlisted && (
                    <Checkbox
                      isChecked={Boolean(medicationInAction?.isNonStandardDose)}
                      onChange={(event) => {
                        const checked = event.target.checked;
                        setChangedValues((prev: any) => {
                          return {
                            ...prev,
                            isNonStandardDose: checked,
                          };
                        });
                        setMedicationInAction((prev) => {
                          return {
                            ...(prev || {}),
                            isNonStandardDose: checked,
                          } satisfies Partial<Medication>;
                        });
                      }}
                    >
                      Nonstandard Dose
                    </Checkbox>
                  )}
                {config?.uiLongstandingEnable && (
                  <Checkbox
                    data-pendoid="longstanding-checkbox"
                    isChecked={Boolean(medicationInAction?.isLongStanding)}
                    onChange={(event) => {
                      const checked = event.target.checked;
                      setChangedValues((prev: any) => {
                        return {
                          ...prev,
                          startDate: checked ? undefined : prev?.startDate,
                          isLongStanding: checked,
                        };
                      });
                      setMedicationInAction((prev) => {
                        return {
                          ...(prev || {}),
                          startDate: checked ? undefined : prev?.startDate,
                          isLongStanding: checked,
                        } satisfies Partial<Medication>;
                      });
                    }}
                  >
                    Longstanding
                  </Checkbox>
                )}
              </Flex>

              <HStack w="100%">
                <Checkbox
                  data-pendoid="unlisted-checkbox"
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
                {renderSearchInput()}
              </HStack>
              {suggestions.length > 0 ? (
                <div>
                  <MedicationSuggestionsTable
                    suggestions={suggestions}
                    onSelect={(suggestion) => {
                      autoComplete(suggestion);
                      setSearchValue("");
                      clearSuggestions();
                    }}
                  />
                </div>
              ) : error !== null ? (
                <div>{error}</div>
              ) : null}
            </Flex>

            {formError ? <div style={{ color: "red" }}>{formError}</div> : null}
            {medicationInAction && (
              <>
                <HStack w="100%" gap="1rem">
                  {generateTextInput("name")}
                </HStack>
                <HStack w="100%" gap="1rem">
                  {generateTextInput("strength")}
                  {generateTextInput("route")}
                  {generateTextInput("form")}
                </HStack>
                <HStack w="100%" gap="1rem">
                  {generateTextInput("dosage", "Amount/Dose")}
                </HStack>
                <HStack w="100%" gap="1rem">
                  {generateTextInput("instructions")}
                </HStack>
                <HStack w="100%" gap="1rem">
                  {generateDateInput("startDate")}
                  {generateDateInput("discontinuedDate")}
                </HStack>
                <HStack w="100%" gap="1rem">
                  {medicationInAction?.isUnlisted &&
                    config?.uiClassificationEnable &&
                    generateSelectInput(
                      "classification",
                      "Medication Classification",
                      medicationClassifications?.map((code) => {
                        return {
                          label: code.value,
                          value: code.code,
                        };
                      }),
                      config?.validationRules?.validateClassification,
                    )}
                </HStack>
              </>
            )}

            {medicationInAction?.id &&
              onDelete &&
              (medication?.hostLinked
                ? config?.uiHostLinkedDeleteEnable
                : true) && (
                <Flex justify="flex-end">
                  <SecondaryButton
                    color="elm.500"
                    onClick={() => {
                      setApiLoading(true);
                      onDelete?.(() => {
                        setApiLoading(false);
                      });
                    }}
                    data-pendoid="delete-medication-button"
                  >
                    <Delete />
                    Delete Medication
                  </SecondaryButton>
                </Flex>
              )}
          </div>
        </DrawerBody>

        <DrawerFooter justifyContent="space-between">
          <TertiaryButton
            onClick={onCloseClick}
            data-pendoid="modal-cancel-button"
          >
            Cancel
          </TertiaryButton>
          <Button
            colorScheme="blue"
            isDisabled={apiLoading || (reviewInProgress ? !success : false)}
            onClick={okOnClick}
            data-pendoid="modal-save-button"
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

export default AddEditMedication;
