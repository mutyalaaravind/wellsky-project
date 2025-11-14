import {
  startTransition,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import { RepeatIcon } from "@chakra-ui/icons";
import {
  Box,
  Heading,
  HStack,
  IconButton,
  Menu,
  MenuButton,
  MenuItem,
  MenuList,
  Spinner,
  TableCellProps,
  Text,
  Badge,
  useToken,
} from "@chakra-ui/react";
import {
  Checkbox,
  DynamicTableContainer,
  PrimaryButton,
  TertiaryButton,
  Tooltip,
} from "@mediwareinc/wellsky-dls-react";

import { useDocumentsApi } from "hooks/useDocumentsApi";
import { DocumentFile, Env, PipeLineStatusEnums } from "types";
import { pluralize } from "utils/i18n";
import { Block } from "components/Block";
import { UploadArea } from "components/UploadArea";
import { useAuth } from "hooks/useAuth";
import useEnvJson from "hooks/useEnvJson";
import { documentNoDataContent } from "screens/review/constants";

import { usePatientProfileStore } from "store/patientProfileStore";
import OverlayLoader from "screens/review/OverlayLoader";
import {
  useTableOfContentsApi,
  EntityTOCSummary,
} from "hooks/useTableOfContentsApi";
import useAsyncTimeInterval from "hooks/useAsyncTimeInterval";
import { useMedWidgetInstanceContext } from "context/MedWidgetInstanceContext";
import { useImportHostDataApi } from "hooks/importHostData";
import { ClockFast, DotsVertical } from "@mediwareinc/wellsky-dls-react-icons";
import { CircularProgressWithLabel } from "components/CircularProgressWithLabel";
// import { DotsVertical } from "@mediwareinc/wellsky-dls-react-icons";

type DocumentsProps = {
  env: Env;
  onReviewPressed: (selectedDocs: DocumentFile[]) => void;
  "data-pendo"?: string;
};

const statusMap = new Map<PipeLineStatusEnums | undefined | null, string>([
  ["NOT_STARTED", "Not Started"],
  ["QUEUED", "Queued"],
  ["IN_PROGRESS", "In Progress"],
  ["COMPLETED", "Completed"],
  ["FAILED", "Failed"],
  //["UNKNOWN", "Unknown"],
  [undefined, "Unknown"],
  [null, "Unknown"],
]);

export const Documents = ({ env, onReviewPressed, "data-pendo": dataPendo }: DocumentsProps) => {
  const [tableHeaderColor] = useToken(
    // the key within the theme, in this case `theme.colors`
    "colors",
    // the subkey(s), resolving to `theme.colors.red.100`
    ["neutral.100"],
    // a single fallback or fallback array matching the length of the previous arg
  );

  const latestDate = useCallback(() => {
    return new Date(new Date().setHours(new Date().getHours() + 2));
  }, []); //This to use in pagination to get latest documents
  const earliestDate = useCallback(() => {
    return new Date(new Date().setFullYear(new Date().getFullYear() - 5));
  }, []); //This is to use in pagination to get last set of documents

  const { patientId } = useAuth();
  const [isManualRefreshing, setIsManualRefreshing] = useState(false);
  const [startAt, setStartAt] = useState<string | null>(
    latestDate().toISOString(),
  );
  const [endAt, setEndAt] = useState<string | null>(null);
  const [limit, setLimit] = useState(10);
  const [currentPage, setCurrentPage] = useState(1);
  const {
    documents,
    fetchDocumentsV2 /*extract*/,
    getDocumentStatus,
    moveToPriorityQueue,
    upsertGoldenDatasetTestcase,
  } = useDocumentsApi({
    apiRoot: env?.API_URL,
    patientId,
    env,
  });

  const {
    loading,
    updateLoading,
    allPageProfiles,
    setAllPageProfiles,
    config,
    documentStatuses,
  } = usePatientProfileStore();

  const { medWidgetInstance } = useMedWidgetInstanceContext();
  const envJson = useEnvJson<Env>();

  const enableUpload = Boolean(
    medWidgetInstance.getConfig()?.enableUpload ||
      envJson?.IS_UPLOAD_ENABLED ||
      config?.uiControlUploadEnable,
  );
  const emptyDocumentListMessage =
    medWidgetInstance.getConfig()?.emptyDocumentListMessage;

  const documentWiseMedicationCount = useMemo(() => {
    const docWiseMedCount = new Map<string, number>();
    documents.forEach((doc) => {
      const profiles = allPageProfiles?.get(doc.id);
      const count = Object.values(profiles?.medication || {})
        ?.filter((p) => p.type === "medication")
        .reduce((prev, next) => prev + next.numberOfItems, 0);
      docWiseMedCount.set(doc.id, count || 0);
    });
    return docWiseMedCount;
  }, [allPageProfiles, documents]);

  // State for entity TOC data
  const [documentEntityTOC, setDocumentEntityTOC] = useState<
    Map<string, EntityTOCSummary>
  >(new Map());

  const isDocumentStatusLoading =
    loading.has("documents_status") || loading.has("documents");

  const completedDocumentsIds = useMemo(() => {
    if (isDocumentStatusLoading) return "";
    return documents
      .filter(
        (doc) =>
          doc.status?.status === "COMPLETED" ||
          (documentStatuses &&
            documentStatuses?.[doc.id]?.status === "COMPLETED"),
      )
      .map((doc) => doc.id)
      ?.join("|");
  }, [isDocumentStatusLoading, documents, documentStatuses]);

  const { getPageProfiles, getPageProfilesV4, getEntityTOC } =
    useTableOfContentsApi({ env });

  const { importMedications, importAttachments } = useImportHostDataApi();

  const statusesLoading = loading.has("documents_status");

  useEffect(() => {
    if (completedDocumentsIds.length && !statusesLoading) {
      const callApi = async () => {
        try {
          updateLoading("medications_count", true);
          const allPromises = completedDocumentsIds
            ?.split("|")
            .map(async (id) => {
              const res =
                config?.orchestrationEngineVersion === "v3"
                  ? await getPageProfiles(id, "medication")
                  : await getPageProfilesV4(id, "medication");
              const formattedResponse = { medication: {} as typeof res };
              Object.keys(res).forEach((k) => {
                const key = Number(k);
                formattedResponse.medication[key] = res[key];
              });

              return [id, formattedResponse];
            });
          const newPageProfiles = await (
            await Promise.allSettled(allPromises)
          ).filter((p) => p.status === "fulfilled");

          const pageProfilesMap = new Map<string, any>(
            newPageProfiles?.map((p: any) => p?.value),
          );
          setAllPageProfiles(pageProfilesMap);
          updateLoading("medications_count", false);
        } catch (error) {
          console.error("newPageProfiles_error", error);
          updateLoading("medications_count", false);
        }
      };

      setTimeout(() => {
        callApi();
      }, 100);
    }
  }, [
    completedDocumentsIds,
    getPageProfiles,
    setAllPageProfiles,
    updateLoading,
    config,
    env,
    getPageProfilesV4,
    statusesLoading,
  ]);

  // Effect to fetch entity TOC data for completed documents
  useEffect(() => {
    if (completedDocumentsIds.length && !statusesLoading) {
      const callEntityTOCApi = async () => {
        try {
          const entityTOCPromises = completedDocumentsIds
            ?.split("|")
            .map(async (id) => {
              const entityTOC = await getEntityTOC(id);
              return [id, entityTOC];
            });

          const entityTOCResults = await (
            await Promise.allSettled(entityTOCPromises)
          ).filter((p) => p.status === "fulfilled");

          const entityTOCMap = new Map<string, EntityTOCSummary>(
            entityTOCResults?.map((p: any) => p?.value),
          );
          setDocumentEntityTOC(entityTOCMap);
        } catch (error) {
          console.error("entityTOC_error", error);
        }
      };

      setTimeout(() => {
        callEntityTOCApi();
      }, 150); // Slight delay after medications to avoid overwhelming the API
    }
  }, [completedDocumentsIds, getEntityTOC, statusesLoading]);

  useEffect(() => {
    const callImports = async () => {
      try {
        if (config?.enableOnDemandExternalFilesDownload) {
          await importAttachments(env as any);
        } else {
          console.log("External files download is disabled");
        }
        await importMedications(env as any);
      } catch (e) {
        console.error("Error", e);
      }
    };
    setTimeout(() => {
      callImports();
    }, 100);
  }, [
    config?.enableOnDemandExternalFilesDownload,
    env,
    importAttachments,
    importMedications,
  ]);

  const uiDocumentActionExtractEnable = Boolean(
    config?.uiDocumentActionExtractEnable,
  );

  const getDocuments = useCallback(
    async (
      { loadStatuses }: { loadStatuses: boolean } = {
        loadStatuses: false,
      },
    ) => {
      try {
        await fetchDocumentsV2({
          startAt,
          endAt,
          limit,
          useAsyncDocumentStatus: config?.useAsyncDocumentStatus,
          loadStatuses,
        });
      } finally {
      }
    },
    [fetchDocumentsV2, startAt, endAt, limit, config?.useAsyncDocumentStatus],
  );

  const refreshDocuments = useCallback(
    async (
      { loadStatuses }: { loadStatuses: boolean } = {
        loadStatuses: false,
      },
    ) => {
      try {
        updateLoading("documents", true);
        await getDocuments({ loadStatuses });
      } finally {
        startTransition(() => {
          updateLoading("documents", false);
        });
      }
    },
    [updateLoading, getDocuments],
  );

  const handleMoveToPriorityQueue = useCallback(
    async (documentId: string) => {
      try {
        updateLoading("documents", true);
        await moveToPriorityQueue(documentId);
        await refreshDocuments({ loadStatuses: false });
      } finally {
        startTransition(() => {
          updateLoading("documents", false);
        });
      }
    },
    [refreshDocuments, moveToPriorityQueue, updateLoading],
  );

  const handleUpsertGoldenDatasetTestcase = useCallback(
    async (documentId: string) => {
      try {
        updateLoading("documents", true);
        await upsertGoldenDatasetTestcase(documentId);
        await refreshDocuments({ loadStatuses: false });
      } finally {
        startTransition(() => {
          updateLoading("documents", false);
        });
      }
    },
    [refreshDocuments, upsertGoldenDatasetTestcase, updateLoading],
  );

  useAsyncTimeInterval({
    interval: 10000,
    callback: getDocuments,
  });

  useEffect(() => {
    refreshDocuments({ loadStatuses: false });
  }, [refreshDocuments, startAt, endAt]);

  const isDocumentsLoading = loading.has("documents");

  const allDocumentIdsAndStatuses = JSON.stringify(
    documents?.map((doc) => [doc.id, doc.status?.status]),
  );

  useEffect(() => {
    if (config?.useAsyncDocumentStatus && !isDocumentsLoading) {
      const callApi = async () => {
        try {
          const docDetails = JSON.parse(allDocumentIdsAndStatuses) as Array<
            [string, string]
          >;
          updateLoading("documents_status", true);
          const allPromises = docDetails
            ?.filter(([_id, status]) => status === "UNKNOWN")
            ?.map(([id]) => {
              return getDocumentStatus(id);
            });
          await Promise.allSettled(allPromises);
          setTimeout(() => {
            updateLoading("documents_status", false);
          }, 100);
        } catch (error) {}
      };
      callApi();
    }
  }, [
    allDocumentIdsAndStatuses,
    config?.useAsyncDocumentStatus,
    getDocumentStatus,
    updateLoading,
    isDocumentsLoading,
  ]);

  const [selectedDocuments, setSelectedDocuments] = useState<DocumentFile[]>(
    [],
  );

  const setDocumentSelected = useCallback(
    (doc: DocumentFile, selected: boolean) => {
      if (selected) {
        setSelectedDocuments([...selectedDocuments, doc]);
      } else {
        setSelectedDocuments(selectedDocuments.filter((d) => d.id !== doc.id));
      }
    },
    [selectedDocuments, setSelectedDocuments],
  );

  const [isUploadEnabled, setIsUploadEnabled] = useState(enableUpload);

  useEffect(() => {
    (window as any).enabledUpload = setIsUploadEnabled;

    return () => {
      delete (window as any).enabledUpload;
    };
  }, []);

  const noDataContent = useMemo(
    () => documentNoDataContent(emptyDocumentListMessage),
    [emptyDocumentListMessage],
  );
  const isUsingNewUpload = true;

  return (
    <Block style={{ padding: "0.5rem" }} data-pendo={dataPendo}>
      <div
        style={{
          display: "flex",
          flex: "1 1 0",
          flexDirection: "column",
          gap: "1rem",
        }}
      >
        {isUploadEnabled &&
          (isUsingNewUpload ? (
            <UploadArea
              env={env}
              patientId={patientId}
              onFileUploaded={(_) => {
                refreshDocuments();
              }}
              showAsButton
            />
          ) : (
            <>
              <Heading size="md">Select Document</Heading>

              <Heading size="sm">
                Upload a document or select an existing document to begin
              </Heading>

              <Block style={{ padding: "1rem", flex: "0 1 auto" }}>
                <UploadArea
                  env={env}
                  patientId={patientId}
                  onFileUploaded={(_) => refreshDocuments()}
                />
              </Block>
            </>
          ))}

        <Heading
          size="sm"
          mt={1}
          display="flex"
          data-pendoid="documents-header"
        >
          Select documents
          <IconButton
            variant="link"
            style={{ marginLeft: "1rem" }}
            size="md"
            isLoading={isManualRefreshing}
            onClick={() => {
              setIsManualRefreshing(true);
              refreshDocuments().finally(() => setIsManualRefreshing(false));
            }}
            aria-label="Refresh"
            icon={<RepeatIcon />}
            data-pendoid="refresh-documents"
          />
        </Heading>

        <Text
          color="bigStone.400"
          fontSize="small"
          lineHeight="24px"
          data-pendoid="documents-subheader"
        >
          Existing Documents
        </Text>
        <Box flex="1 1 0" position="relative" overflow="auto">
          {loading.has("documents") && <OverlayLoader />}
          <DynamicTableContainer
            data-pendoid="documents-table"
            loading={loading.has("documents")}
            noDataContent={noDataContent}
            pagination={{
              defaultPageSize: limit,
              totalRecords: documents?.[0]?.total_records || documents?.length,
              isStatic: false,
            }}
            onPageChange={(pageNumber: number) => {
              const lastPageNUmber = Math.ceil(
                (documents?.[0]?.total_records || documents?.length) / limit,
              );
              console.log("pageNumber", pageNumber, lastPageNUmber);
              if (
                pageNumber === lastPageNUmber &&
                pageNumber !== currentPage + 1
              ) {
                // if last page is clicked but not come from next page button
                console.log("last page");
                setEndAt(earliestDate().toISOString());
                setStartAt(null);
              } else if (pageNumber === 1) {
                setStartAt(latestDate().toISOString());
                setEndAt(null);
              } else if (pageNumber > currentPage) {
                setStartAt(documents[limit - 1]?.created_at);
                setEndAt(null);
              } else if (pageNumber < currentPage) {
                setEndAt(documents[0]?.created_at);
                setStartAt(null);
              }
              setCurrentPage(pageNumber);
            }}
            onPageSizeChange={(_pageNumber: number, pageSize: number) => {
              setLimit(pageSize);
              setStartAt(latestDate().toISOString());
              setEndAt(null);
              setCurrentPage(1);
            }}
            headerColor={tableHeaderColor}
            columns={[
              {
                dataIndex: "id",
                id: "id",
                sortable: false,
                render: (id, doc) => (
                  <Checkbox
                    isChecked={selectedDocuments.some((doc) => doc.id === id)}
                    // isDisabled={doc.status?.status !== "COMPLETED"}
                    onClick={(event) => {}}
                    style={{ pointerEvents: "none" }}
                    data-pendoid={`document-checkbox-${id}`}
                  />
                ),
                title: "",
                width: "40px",
              },
              {
                dataIndex: "created_at",
                id: "doc_date",
                // sortable: true,
                title: "Uploaded date",
                render: (dateStr) => {
                  const date = new Date(dateStr as string);
                  return (
                    date.toLocaleDateString() + " " + date.toLocaleTimeString()
                  );
                },
                getColumnProps: <TDProp extends any>(
                  data: DocumentFile,
                ): TDProp & TableCellProps => {
                  return {
                    "data-pendoid": `document-created_at-${data.id}`,
                  } as unknown as TDProp & TableCellProps;
                },
              },
              {
                dataIndex: "file_name",
                id: "document_file_name",
                // sortable: true,
                title: "File Name",
                render: (id, doc) => (
                  <HStack>
                    <Text>{doc.file_name}</Text>
                    {doc.metadata?.golden_data && (
                      <Badge variant="solid" colorScheme="yellow">
                        Golden Data
                      </Badge>
                    )}
                  </HStack>
                ),
                getColumnProps: <TDProp extends any>(
                  data: DocumentFile,
                ): TDProp & TableCellProps => {
                  return {
                    "data-pendoid": `document-file_name-${data.id}`,
                  } as unknown as TDProp & TableCellProps;
                },
              },
              {
                dataIndex: "page_count",
                id: "page_count",
                // sortable: true,
                title: "Pages",
                getColumnProps: <TDProp extends any>(
                  data: DocumentFile,
                ): TDProp & TableCellProps => {
                  return {
                    "data-pendoid": `document-page_count-${data.id}`,
                  } as unknown as TDProp & TableCellProps;
                },
              },
              {
                dataIndex: "id",
                id: "status",
                // sortable: true,
                title: "Status",
                getColumnProps: <TDProp extends any>(
                  data: DocumentFile,
                ): TDProp & TableCellProps => {
                  return {
                    "data-pendoid": `document-status-${data.id}`,
                  } as unknown as TDProp & TableCellProps;
                },
                render: (id, doc) => {
                  var status = doc.status?.status;
                  if (status === undefined || status === null) {
                    status = "NOT_STARTED";
                  }

                  const isStableState = [
                    "UNKNOWN",
                    "NOT_STARTED",
                    "FAILED",
                  ].includes(status);
                  const isInFlight = ["QUEUED", "IN_PROGRESS"].includes(status);

                  const canStartExtraction =
                    isStableState || (isInFlight && doc.priority !== "high");

                  // Check if the element should be disabled
                  const isDisabled = !canStartExtraction;

                  var actionExtractionLabel = "Start Extracting";
                  if (isInFlight) {
                    actionExtractionLabel = "Move to top of the queue";
                  }

                  var actionAddGoldenDatasetTestcaseLabel =
                    "Add Golden Dataset Testcase";
                  if (doc.metadata?.golden_data) {
                    actionAddGoldenDatasetTestcaseLabel =
                      "Update Golden Dataset Testcase";
                  }

                  if (doc) {
                    let prioritiseJsx = null;
                    if (uiDocumentActionExtractEnable) {
                      prioritiseJsx = (
                        <>
                          <Menu>
                            <MenuButton
                              as={DotsVertical}
                              fontSize={"32px"}
                              onClick={(e) => e.stopPropagation()}
                            >
                              &nbsp;
                            </MenuButton>
                            <MenuList p={0}>
                              <MenuItem
                                isDisabled={isDisabled}
                                onClick={() =>
                                  handleMoveToPriorityQueue(doc.id)
                                }
                              >
                                {actionExtractionLabel}
                              </MenuItem>
                              {config?.uiDocumentActionUpsertGoldenDatasetTestcaseEnable && (
                                <MenuItem
                                  onClick={() =>
                                    handleUpsertGoldenDatasetTestcase(doc.id)
                                  }
                                >
                                  {actionAddGoldenDatasetTestcaseLabel}
                                </MenuItem>
                              )}
                            </MenuList>
                          </Menu>
                        </>
                      );
                    }

                    let status = null;
                    let hasSpinner = false;

                    // Check if we should show progress indicator or indefinite spinner
                    const progress = doc.status?.progress;
                    const shouldShowProgress =
                      progress !== null &&
                      progress !== undefined &&
                      progress >= 0;

                    if (statusMap.get(doc.status?.status)) {
                      status = statusMap.get(doc.status?.status);
                    } else if (
                      config?.useAsyncDocumentStatus &&
                      documentStatuses &&
                      documentStatuses?.[doc.id]?.status === "IN_PROGRESS"
                    ) {
                      const asyncProgress = documentStatuses[doc.id]?.progress;
                      const shouldShowAsyncProgress =
                        asyncProgress !== null &&
                        asyncProgress !== undefined &&
                        asyncProgress >= 0;

                      if (!shouldShowAsyncProgress) {
                        status = (
                          <>
                            {statusMap.get(documentStatuses[doc.id]?.status)}
                            <Spinner size={"sm"}></Spinner>
                          </>
                        );
                        hasSpinner = true;
                      } else {
                        status = statusMap.get(
                          documentStatuses[doc.id]?.status,
                        );
                      }
                    } else if (
                      documentStatuses?.[doc.id] &&
                      statusMap.get(documentStatuses?.[doc.id]?.status)
                    ) {
                      status = statusMap.get(
                        documentStatuses?.[doc.id]?.status,
                      );
                    } else {
                      status = <Spinner size={"sm"}></Spinner>;
                      hasSpinner = true;
                    }

                    if (
                      ["QUEUED", "IN_PROGRESS"].includes(doc.status?.status) &&
                      !shouldShowProgress
                    ) {
                      hasSpinner = true;
                    }

                    return (
                      <HStack justifyContent={"space-between"}>
                        <div
                          style={{
                            display: "flex",
                            flexDirection: "row",
                            alignItems: "center",
                            // justifyContent: "center",
                            justifyItems: "center",
                          }}
                        >
                          <div>
                            <Tooltip
                              label={
                                doc.status?.failed > 0
                                  ? `Failed Pages: ${doc.status?.failed}`
                                  : "No Failures"
                              }
                            >
                              {status}

                              {(doc.status?.status === "COMPLETED" ||
                                (config?.useAsyncDocumentStatus &&
                                  documentStatuses?.[doc.id]?.status ===
                                    "COMPLETED")) && (
                                <>
                                  {(documentWiseMedicationCount?.get(doc?.id) ??
                                    0) > 0 && (
                                    <>
                                      <br />
                                      <span style={{ fontSize: 12 }}>
                                        <b>
                                          {
                                            documentWiseMedicationCount?.get(
                                              doc?.id,
                                            ) as number
                                          }
                                        </b>{" "}
                                        Medications found
                                      </span>
                                    </>
                                  )}
                                  {(() => {
                                    const entityTOC = documentEntityTOC.get(
                                      doc?.id,
                                    );
                                    return (
                                      entityTOC &&
                                      entityTOC.categories &&
                                      entityTOC.categories.length > 0 && (
                                        <>
                                          {entityTOC.categories.map(
                                            (cat, index) => (
                                              <span key={cat.category}>
                                                <br />
                                                <span style={{ fontSize: 12 }}>
                                                  <b>{cat.count}</b> {cat.label}{" "}
                                                  found
                                                </span>
                                              </span>
                                            ),
                                          )}
                                        </>
                                      )
                                    );
                                  })()}
                                </>
                              )}
                            </Tooltip>
                          </div>
                          <div>
                            {doc.status?.failed > 0 ? <>{""}</> : <></>}
                          </div>
                          <div>
                            {" "}
                            {["QUEUED", "IN_PROGRESS"].includes(
                              doc.status?.status,
                            ) ? (
                              <HStack gap={0}>
                                {doc.priority === "high" && (
                                  <Tooltip
                                    label={
                                      "This document is in a priority queue"
                                    }
                                  >
                                    <ClockFast fontSize={"32px"} />
                                  </Tooltip>
                                )}
                                {shouldShowProgress ? (
                                  <CircularProgressWithLabel
                                    value={progress}
                                    size="24px"
                                  />
                                ) : (
                                  <Spinner size={"sm"} />
                                )}
                              </HStack>
                            ) : (
                              <></>
                            )}
                          </div>
                          {loading.has("medications_count") && !hasSpinner && (
                            <Spinner size={"sm"} />
                          )}
                        </div>
                        {prioritiseJsx}
                      </HStack>
                    );
                  }
                  return <>{"Unknown"}</>;
                },
              },
            ]}
            dataSource={documents}
            onRowClick={(doc) => {
              // if (doc.status?.status === "COMPLETED") {
              setDocumentSelected(
                doc,
                !selectedDocuments.some((d) => d?.id === doc?.id),
              );
              // }
            }}
          />
        </Box>

        <div style={{ display: "flex", gap: "1rem" }}>
          <TertiaryButton
            onClick={() =>
              setSelectedDocuments(
                // documents.filter((doc) => doc.status?.status === "COMPLETED"),
                documents,
              )
            }
            data-pendoid="select-all-documents"
          >
            Select All
          </TertiaryButton>
          <TertiaryButton
            onClick={() => setSelectedDocuments([])}
            data-pendoid="deselect-all-documents"
          >
            Deselect All
          </TertiaryButton>
          <div style={{ flex: "1 1 0" }}></div>
          <PrimaryButton
            onClick={() => onReviewPressed(selectedDocuments)}
            isDisabled={
              selectedDocuments.length === 0 || loading.has("documents")
            }
            data-pendoid="review-selected-documents"
          >
            {selectedDocuments.length === 0
              ? "Select documents to review"
              : `Review ${selectedDocuments.length === documents.length ? "all" : ""} ${selectedDocuments.length} ${pluralize(selectedDocuments.length, "document", "documents")}`}
          </PrimaryButton>
        </div>
      </div>
    </Block>
  );
};
