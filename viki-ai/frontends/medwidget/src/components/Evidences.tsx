import { HStack, Box, Flex, Badge, Text } from "@chakra-ui/react";
import { useConfigData } from "context/AppConfigContext";
import { usePageOcrApi } from "hooks/usePageOcr";
import { MagicSparkle } from "icons/MagicSparkle";
import {
  startTransition,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import OverlayLoader from "screens/review/OverlayLoader";
import { usePatientProfileStore } from "store/patientProfileStore";
import { EvidenceInfo, ExtractedMedication, Medication } from "types";
import { groupByDocument } from "utils/helpers";

type EvidencesProps = {
  medication: Medication;
  loadEvidence: (id: string, onLoadComplete?: () => void) => void;
  onEvidenceRequested: (evidenceInfo: EvidenceInfo) => void;
  onLoading?: (loading?: boolean) => void;
  activeEvidenceId?: string;
  setActiveEvidenceId?: (id: string | ((prev: string) => string)) => void;
  compact?: boolean;
  selectFirstByDefault?: boolean;
  onClearEvidence?: (documentId?: string) => void;
  "data-pendoid"?: string;
};

const Evidences = ({
  medication,
  loadEvidence,
  onEvidenceRequested,
  onLoading,
  activeEvidenceId: _activeEvidenceId,
  setActiveEvidenceId: _setActiveEvidenceId,
  compact = false,
  selectFirstByDefault = false,
  onClearEvidence,
  "data-pendoid": dataPendoid,
}: EvidencesProps) => {
  const [documentsInReview] = usePatientProfileStore(
    useCallback((state) => [state.documentsInReview], []),
  );

  const [loading, setLoading] = useState(false);
  const [internalActiveEvidenceId, setInternalActiveEvidenceId] =
    useState<string>();
  const [evidenceRequestedFor, setEvidenceRequestedFor] =
    useState<ExtractedMedication>();
  const [pageOcrPollIntervalId, setPageOcrPollIntervalId] = useState<any>();

  const config = useConfigData();

  const { triggerOcr, getPageOcrStatus } = usePageOcrApi();

  const { pageOcrStatus } = usePatientProfileStore();

  const activeEvidenceId = _activeEvidenceId ?? internalActiveEvidenceId;
  const setActiveEvidenceId =
    _setActiveEvidenceId ?? setInternalActiveEvidenceId;

  const documentPages: Record<string, ExtractedMedication[]> | undefined =
    useMemo(
      () =>
        groupByDocument(
          medication?.extractedMedications,
          documentsInReview || [],
        ),
      [documentsInReview, medication],
    );

  const firstSelected = useRef(false);
  const firstSelectedEnded = useRef(false);
  const firstEvidenceDocumentId = useRef("");
  const isAlreadySelectedFromList = medication?.extractedMedications?.some(
    (evidence) => evidence.extractedMedicationId === activeEvidenceId,
  );

  useEffect(() => {
    if (
      firstSelected.current === false &&
      selectFirstByDefault &&
      !isAlreadySelectedFromList &&
      !firstSelectedEnded.current &&
      medication?.extractedMedications?.length
    ) {
      firstSelected.current = true;
      const firstEvidence = medication.extractedMedications[0];
      firstEvidenceDocumentId.current = firstEvidence.documentId;
      firstSelectedEnded.current = true;
      startTransition(() => {
        (onLoading || setLoading)(true);
        if (
          config?.ocrTriggerConfig.enabled &&
          config.ocrTriggerConfig.touchPoints.evidenceLinkClick
        ) {
          if (
            pageOcrStatus[firstEvidence?.documentId]?.[
              firstEvidence?.pageNumber
            ] === "COMPLETED"
          ) {
            loadEvidence?.(firstEvidence.extractedMedicationId, () => {
              startTransition(() => {
                setActiveEvidenceId(firstEvidence.extractedMedicationId);
                firstSelectedEnded.current = true;
                (onLoading || setLoading)(false);
              });
            });
          } else {
            console.log("triggering ocr for first evidence", firstEvidence);
            triggerOcr(firstEvidence?.documentId, firstEvidence?.pageNumber);
            setEvidenceRequestedFor(firstEvidence);
          }
        } else {
          loadEvidence?.(firstEvidence.extractedMedicationId, () => {
            startTransition(() => {
              setActiveEvidenceId(firstEvidence.extractedMedicationId);
              firstSelectedEnded.current = true;
              (onLoading || setLoading)(false);
            });
          });
        }
      });
    }
  }, [
    medication,
    selectFirstByDefault,
    loadEvidence,
    setActiveEvidenceId,
    onLoading,
    onEvidenceRequested,
    onClearEvidence,
    config,
    pageOcrStatus,
    triggerOcr,
    isAlreadySelectedFromList,
  ]);

  useEffect(() => {
    if (medication.extractedMedications?.length) {
      getPageOcrStatus(
        medication.extractedMedications[0]?.documentId,
        medication.extractedMedications[0]?.pageNumber,
      );
    }
  }, [medication, getPageOcrStatus]);

  useEffect(() => {
    const intervalId = setInterval(() => {
      if (evidenceRequestedFor) {
        console.log("evidenceRequestedFor", evidenceRequestedFor);
        try {
          getPageOcrStatus(
            evidenceRequestedFor?.documentId,
            evidenceRequestedFor?.pageNumber,
          );
        } catch (error) {
          console.error("error while getting page ocr status", error);
          setPageOcrPollIntervalId(intervalId);
        }
      }
    }, 500);
    setPageOcrPollIntervalId(intervalId);
    return () => {
      clearInterval(intervalId);
    };
  }, [evidenceRequestedFor, getPageOcrStatus]);

  useEffect(() => {
    if (evidenceRequestedFor) {
      if (
        pageOcrStatus[evidenceRequestedFor?.documentId]?.[
          evidenceRequestedFor?.pageNumber
        ] === "COMPLETED"
      ) {
        clearInterval(pageOcrPollIntervalId);
        loadEvidence?.(evidenceRequestedFor?.extractedMedicationId, () => {
          (onLoading || setLoading)(false);
        });
        setEvidenceRequestedFor(undefined);
      }
    }
  }, [
    pageOcrStatus,
    evidenceRequestedFor,
    loadEvidence,
    onLoading,
    pageOcrPollIntervalId,
  ]);

  return (medication as Medication)?.extractedMedications?.length ? (
    <HStack px="16px" position="relative" data-pendoid={dataPendoid}>
      {loading && (
        <OverlayLoader style={{ gap: 0, padding: 0 }} size="xs">
          {null}
        </OverlayLoader>
      )}
      {!compact && (
        <>
          <Box>
            <MagicSparkle fontSize={24} />
          </Box>
          <Text>View Source:</Text>
        </>
      )}

      {documentPages &&
        Object.entries(documentPages)?.map(([docAlphabet, evidences]) => {
          return (
            <Flex gap="4px" key={docAlphabet} alignItems="center">
              [{docAlphabet}]
              {evidences?.map((evidence) => {
                const isActive =
                  activeEvidenceId === evidence.extractedMedicationId;
                return (
                  <Badge
                    key={evidence.extractedMedicationId}
                    border={isActive ? "none" : "1px solid #5F727E"}
                    bgColor={isActive ? "#228189" : "#FFF"}
                    borderRadius="50%"
                    display="flex"
                    alignItems="center"
                    justifyContent="center"
                    h="6"
                    w="6"
                    p="0"
                    color={isActive ? "white" : "black"}
                    cursor="pointer"
                    onClick={() => {
                      if (isActive) {
                        setActiveEvidenceId("");
                        console.log(
                          "config.ocrTriggerConfig",
                          config.ocrTriggerConfig,
                        );
                        onEvidenceRequested?.({
                          documentId: evidence.documentId,
                          pageNumber: 0,
                          annotations: [],
                        });

                        onClearEvidence?.(evidence.documentId);
                        return;
                      }
                      (onLoading || setLoading)(true);

                      setActiveEvidenceId(evidence.extractedMedicationId);
                      console.log(
                        "config.ocrTriggerConfig",
                        config.ocrTriggerConfig,
                      );
                      if (
                        config &&
                        config.ocrTriggerConfig.enabled &&
                        config.ocrTriggerConfig.touchPoints.evidenceLinkClick
                      ) {
                        console.log("page ocr status", pageOcrStatus);
                        if (
                          pageOcrStatus[evidence?.documentId]?.[
                            evidence?.pageNumber
                          ] === "COMPLETED"
                        ) {
                          console.log("page ocr is ready");
                          loadEvidence?.(
                            evidence?.extractedMedicationId,
                            () => {
                              (onLoading || setLoading)(false);
                            },
                          );
                        } else {
                          console.log(
                            "page ocr is not ready. trigger for on demand ocr",
                          );
                          setEvidenceRequestedFor(evidence);
                          triggerOcr(
                            evidence?.documentId,
                            evidence?.pageNumber,
                          );
                        }
                      } else {
                        loadEvidence?.(evidence?.extractedMedicationId, () => {
                          (onLoading || setLoading)(false);
                        });
                      }
                    }}
                    data-pendoid={`evidence-${evidence.extractedMedicationId}`}
                  >
                    {evidence?.pageNumber}
                  </Badge>
                );
              })}
            </Flex>
          );
        })}
    </HStack>
  ) : null;
};

export default Evidences;
