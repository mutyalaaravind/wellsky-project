// import logo from './logo.svg';
// import './App.css';

import { useState, useEffect, FC, memo, useMemo, useCallback } from "react";

import { PdfViewer } from "./PdfViewer";
import useEnvJson from "./hooks/useEnvJson";
import { APIStatus, Env, SettingType } from "./types";

// Import Chakra-UI tabs
import {
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  TableContainer,
  Table,
  Thead,
  Tbody,
  Tr,
  Td,
  TableCaption,
  Heading,
  IconButton,
  HStack,
  RadioGroup,
  Box,
  ChakraProvider,
  Input,
  Button,
  Text,
} from "@chakra-ui/react";
import {
  useNavigate,
  useSearchParams,
  Routes,
  Route,
  BrowserRouter,
} from "react-router-dom";
import {
  LinkButton,
  Radio,
  Spinner,
  Tag,
} from "@mediwareinc/wellsky-dls-react";
import { DeleteIcon, ReactIcon, RepeatIcon } from "@chakra-ui/icons";
import { SearchGlass } from "./SearchGlass";
import { EvidenceViewer } from "./EvidenceViewer";
import CustomFormsComponent from "./components/custom-form";
import { useSummarizer } from "./hooks/useSummarizerApi";
import { useExtractApi } from "./hooks/useExtractApi";
import { getAnnotation, setToken } from "./utils/helpers";
import { DefaultSettings, SettingsComponent } from "./components/settings";
import { FHIRSettings } from "./components/fhir-settings";
import DocumentVectorBasedSearch from "./components/document-vector-search";
import { EmbeddingsList } from "./components/embeddings-info";
import LBISearch from "./components/LBISearch";
import Markdown from "react-markdown";
import { NamedEntityExtraction } from "./components/named-entity-extraction";
import { useDocumentsApi } from "./hooks/useDocumentsApi";
import { getDocument } from "pdfjs-dist";

type PaperglassWidgetProps = {
  env: Env;
  documentId: string;
  patientId: string | null;
  settings: SettingType;
};

type DocumentAIPageData = {
  blocks: any[];
  detectedLanguages: any[];
  dimension: any;
  image: any;
  layout: any;
  lines: any[];
  pageNumber: number;
  paragraphs: any[];
  tokens: any[];
};

type DocumentAIResultData = {
  text: string;
  page: DocumentAIPageData;
  entities: any[];
};

// Labels is an map of string to string
type Label = {
  [key: string]: string;
};

const PaperglassWidget: FC<PaperglassWidgetProps> = memo(
  ({ env, documentId, settings, patientId }: PaperglassWidgetProps) => {
    const memoEnv = useMemo(() => env, [JSON.stringify(env)]);
    const [documentData, setDocumentData] = useState<any>({});
    const [pageResults, setPageResults] = useState<any>({});
    const [documentAIResultIds, setDocumentAIResultIds] = useState<any>({});
    const [busyPages, setBusyPages] = useState<number[]>([]);
    const [summaryList, setSummaryList] = useState<any[]>([]);
    const [currentPage, setCurrentPage] = useState<number>(1);
    const [labels, setLabels] = useState<Array<Label>>([]);
    const [documentEvents, setDocumentEvents] = useState<any[]>([]);
    // Results for document_ai processing. Key is page number. Value is DocumentAIResultData
    // const [hccResults, setHccResults] = useState<
    //   Map<number, DocumentAIResultData>
    // >(new Map());
    // const [summarizerResults, setSummarizerResults] = useState<
    //   Map<number, DocumentAIResultData>
    // >(new Map());

    const [annotations, setAnnotations] = useState<any[]>([]);
    const [pdfUrl, setPdfUrl] = useState<string>("");

    // const pdfUrl = `${env.API_URL}/api/documents/${documentId}/pdf`;
    const { findEvidences, evidences, evidenceApiStatus } = useSummarizer(env);

    const { extract, results, busy } = useExtractApi(env);

    // const summaries = useCallback(() => {
    //   const summaries: any = [];
    //   Object.entries(summarizerResults).forEach(([pageNumber, result]) => {
    //     if (result == null) {
    //       return;
    //     }
    //     summaries.push({
    //       page: parseInt(pageNumber),
    //       text: result.entities[0].mentionText,
    //     });
    //   });
    //   return summaries;
    // }, [summarizerResults]);

    useEffect(() => {
      // Fetch the document data from the server
      if (env == null) {
        return;
      }
      // Fetch the document data from the server
      fetch(`${env.API_URL}/api/documents/${documentId}`, {
        headers: { authorization: `Bearer ${localStorage.getItem("token")}` },
      })
        .then((response) => response.json())
        .then((data) => {
          console.log("Document data:", data);
          setDocumentData(data);
          //setBusyPages(data.pages.map((page: any) => page.number));
        })
        .catch((error) => {
          console.error("Document data error:", error);
        });
      // Fetch document PDF URL
      fetch(`${env.API_URL}/api/documents/${documentId}/pdf-url`, {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      })
        .then((response) => response.json())
        .then((data) => {
          console.log("PDF URL:", data);
          setPdfUrl(data);
        });
    }, [JSON.stringify(env), documentId]);

    const fetchLabels = useCallback(() => {
      if (env == null) {
        return;
      }
      setLabels([]);
      // TODO: This assumes that each chunk has exactly 1 page!
      fetch(
        `${env.API_URL}/api/documents/${documentId}/pagenumber/${currentPage}/labels`,
        {
          headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
        },
      )
        .then((response) => response.json())
        .then((data) => {
          setLabels(data);
        })
        .catch((error) => {
          console.error("Error fetching labels:", error);
        });
    }, [JSON.stringify(env), documentId, currentPage]);
    useEffect(() => {
      fetchLabels();
    }, [fetchLabels]);

    // Fetch document events
    const fetchDocumentEvents = useCallback(() => {
      if (env == null) {
        return;
      }
      setDocumentEvents([]);
      fetch(`${env.API_URL}/api/documents/${documentId}/events`)
        .then((response) => response.json())
        .then((data) => {
          console.log("Document events:", data);
          setDocumentEvents(data);
        })
        .catch((error) => {
          console.error("Error fetching document events:", error);
        });
    }, [JSON.stringify(env), documentId]);
    useEffect(() => {
      fetchDocumentEvents();
    }, [fetchDocumentEvents]);

    useEffect(() => {
      setCurrentPage(1);
    }, []);

    if (documentData == null) {
      return <div>Loading document data...</div>;
    }
    if (pdfUrl == null) {
      return <div>Loading PDF URL...</div>;
    }

    return (
      <>
        <div>
          {env && (
            <>
              <div
                style={{
                  // height: "100vh",
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "flex-start",
                  // backgroundColor: '#222222',
                  // color: '#ffffff',
                }}
              >
                {evidenceApiStatus === APIStatus.PROCESSING && (
                  <div
                    style={{
                      position: "absolute",
                      inset: 0,
                      backgroundColor: "rgba(0, 0, 0, 0.5)",
                      display: "flex",
                      flexDirection: "column",
                      gap: "0.5rem",
                      justifyContent: "center",
                      alignItems: "center",
                      zIndex: "1000",
                    }}
                  >
                    <Spinner />
                    Searching for Evidence..
                  </div>
                )}
                <div style={{ width: "70%" }}>
                  <PdfViewer
                    documentId={documentId}
                    url={pdfUrl}
                    annotations={
                      // https://www.ti.com/lit/sg/scyt129g/scyt129g.pdf
                      annotations
                    }
                    busyPages={busyPages}
                    env={memoEnv}
                    correction={settings.correction}
                    onPageChange={(pageNumber: number) => {
                      setCurrentPage(pageNumber);
                    }}
                  />
                </div>
                <div style={{ width: "30%" }}>
                  <Tabs defaultIndex={0}>
                    <TabList>
                      <Tab>Medications</Tab>
                      <Tab
                        style={{
                          display: settings.enableLBISearch ? "block" : "none",
                        }}
                      >
                        Labels
                      </Tab>
                      {/* <Tab>Form</Tab> */}
                      <Tab
                        style={{
                          display: settings.enableLBISearch ? "block" : "none",
                        }}
                      >
                        Document events
                      </Tab>
                    </TabList>
                    <TabPanels>
                      <TabPanel id="medication">
                        {/* <Heading style={{ margin: "1rem" }}>Embeddings</Heading> */}
                        <Box>
                          <NamedEntityExtraction
                            documentId={documentId}
                            env={env}
                            patientId={patientId}
                            entityType={"medications"}
                            setAnnotations={setAnnotations}
                            currentPage={currentPage}
                          />
                        </Box>
                      </TabPanel>
                      <TabPanel id="labels">
                        <Heading style={{ margin: "2rem" }}>
                          Labels
                          <IconButton
                            aria-label="Refresh"
                            style={{ float: "right" }}
                            variant="link"
                          >
                            <RepeatIcon onClick={fetchLabels} />
                          </IconButton>
                        </Heading>
                        <TableContainer>
                          <Table variant="simple" size="sm">
                            <Thead>
                              <Tr>
                                <Td width="1%">Label</Td>
                                <Td>Content</Td>
                              </Tr>
                            </Thead>
                            <Tbody>
                              {labels?.map((label: Label) =>
                                Object.entries(label).map(
                                  ([label, content]) => {
                                    if (label === "page") return null;
                                    return (
                                      <Tr key={label}>
                                        <Td valign="top">
                                          <Tag>{label}</Tag>
                                        </Td>
                                        <Td whiteSpace="pre-line">
                                          <Markdown>{content}</Markdown>
                                        </Td>
                                      </Tr>
                                    );
                                  },
                                ),
                              )}
                            </Tbody>
                          </Table>
                        </TableContainer>
                      </TabPanel>
                      <TabPanel id="doc_events">
                        <Heading style={{ margin: "2rem" }}>
                          Document events
                          <IconButton
                            aria-label="Refresh"
                            style={{ float: "right" }}
                            variant="link"
                          >
                            <RepeatIcon onClick={fetchDocumentEvents} />
                          </IconButton>
                        </Heading>
                        <TableContainer>
                          <Table variant="simple" size="sm">
                            <Thead>
                              <Tr>
                                <Td width="1%">Timestamp</Td>
                                <Td>Type</Td>
                              </Tr>
                            </Thead>
                            <Tbody>
                              {documentEvents.map((event) => (
                                <Tr key={event.id}>
                                  <Td>{event.created}</Td>
                                  <Td>
                                    <Tag>{event.type}</Tag>
                                  </Td>
                                </Tr>
                              ))}
                            </Tbody>
                          </Table>
                        </TableContainer>
                      </TabPanel>
                    </TabPanels>
                  </Tabs>
                </div>
              </div>
            </>
          )}
        </div>
      </>
    );
  },
  (prevProps, nextProps) => {
    return (
      prevProps.documentId === nextProps.documentId &&
      JSON.stringify(prevProps.env) === JSON.stringify(nextProps.env) &&
      JSON.stringify(prevProps.settings) === JSON.stringify(nextProps.settings)
    );
  },
);

type DocumentUploaderProps = {
  env: Env;
  patientId: string;
  onDocumentUploaded: (documentId: string) => void;
};

const DocumentUploader: FC<DocumentUploaderProps> = ({
  env,
  patientId,
  onDocumentUploaded,
}: DocumentUploaderProps) => {
  const [busy, setBusy] = useState<boolean>(false);
  const [filename, setFilename] = useState<string | null>(null);
  return (
    <div>
      <Heading style={{ margin: "2rem" }}>Upload Document</Heading>

      <div style={{ margin: "0 2rem" }}>
        {busy ? (
          <div
            style={{
              display: "flex",
              flexDirection: "row",
              alignItems: "center",
              gap: "1rem",
            }}
          >
            <Spinner size="lg" />
            <Text>Uploading {filename}...</Text>
          </div>
        ) : (
          <input
            type="file"
            accept=".pdf"
            disabled={busy}
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file == null) {
                return;
              }
              setBusy(true);
              setFilename(file.name);

              // Upload file
              const formData = new FormData();
              formData.append("file", file);
              formData.append("patientId", patientId);
              fetch(`${env.API_URL}/api/documents`, {
                method: "POST",
                body: formData,
                headers: {
                  Authorization: `Bearer ${localStorage.getItem("token")}`,
                },
              })
                .then((response) => response.json())
                // Uncomment to simulate slow upload
                // .then((data) => {
                //   return new Promise(resolve => setTimeout(() => resolve(data), 1000));
                // })
                .then((data: any) => {
                  console.log("Upload PDF success:", data);
                  onDocumentUploaded(data.id);
                })
                .catch((error) => {
                  console.error("Upload PDF error:", error);
                })
                .finally(() => {
                  setBusy(false);
                });
            }}
          />
        )}
      </div>
    </div>
  );
};

type DocumentListProps = {
  env: Env;
  patientId: string;
  onSelectDocument: (documentId: string) => void;
};

const DocumentList: FC<DocumentListProps> = ({
  env,
  patientId,
  onSelectDocument,
}: DocumentListProps) => {
  const [documents, setDocuments] = useState<any[]>([]);
  const [refresh, setRefresh] = useState<number>(0);
  const { busy, documentList, getDocuments } = useDocumentsApi();
  console.log("Document list:", documentList);
  const deleteDocument = useCallback((documentId: string) => {
    fetch(`${env.API_URL}/api/documents/${documentId}`, {
      method: "DELETE",
    }).then(() => {
      getDocuments(env, patientId);
      //setDocuments(documents.filter((doc) => doc.id !== documentId));
    });
  }, []);
  useEffect(() => {
    // Fetch the list of documents from the server
    // fetch(`${env.API_URL}/api/documents?patientId=${patientId}`)
    //   .then((response) => response.json())
    //   .then((data) => {
    //     console.log("Document list:", data);
    //     setDocuments(data);
    //   });
    getDocuments(env, patientId);
  }, [env, patientId, refresh]);

  useEffect(() => {
    setDocuments(documentList);
  }, [documentList]);
  // Render Chakra UI table of documents
  return (
    <div>
      <Heading style={{ margin: "2rem" }}>
        Document list
        <IconButton
          variant="link"
          style={{ marginLeft: "1rem" }}
          size="lg"
          onClick={() => {
            setDocuments([]);
            setRefresh(Math.random());
          }}
          aria-label="Refresh"
          icon={<RepeatIcon />}
        />
      </Heading>
      {busy && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            backgroundColor: "rgba(0, 0, 0, 0.5)",
            display: "flex",
            flexDirection: "column",
            gap: "0.5rem",
            justifyContent: "center",
            alignItems: "center",
            zIndex: "1000",
          }}
        >
          <Spinner />
          fetching documents..
        </div>
      )}
      <TableContainer>
        <Table variant="simple" size="sm">
          <Thead>
            <Tr>
              <Td width="1%">Document ID</Td>
              <Td>Document Name</Td>
              <Td width="1%">Created at</Td>
              <Td width="1%">Page count</Td>
              {/* <Td width="1%">Chunk count</Td> */}
            </Tr>
          </Thead>
          <Tbody>
            {documents?.map((document: any) => (
              <Tr key={document.id}>
                <Td>{document.id}</Td>
                <Td>
                  <LinkButton onClick={() => onSelectDocument(document.id)}>
                    {document.file_name}
                  </LinkButton>
                </Td>
                <Td>{document.created_at}</Td>
                <Td>{document.page_count}</Td>
                {/* <Td>{document.pages.length}</Td> */}
                <Td>
                  <IconButton
                    aria-label="delete"
                    style={{ float: "right" }}
                    variant="link"
                  >
                    <DeleteIcon
                      onClick={() => {
                        deleteDocument(document.id);
                      }}
                    />
                  </IconButton>
                </Td>
              </Tr>
            ))}
            {documents?.length === 0 && (
              <Tr>
                <Td colSpan={5}>No documents found</Td>
              </Tr>
            )}
          </Tbody>
        </Table>
      </TableContainer>
    </div>
  );
};

const Main = ({ identifier }: { identifier: string }) => {
  const [searchParams, setSearchParams] = useSearchParams();
  const token = searchParams.get("token");
  if (token) {
    setToken(token);
  }
  const patientId = token ? JSON.parse(atob(token)).patientId : null;
  const env = useEnvJson<Env>();
  const [activeDocumentId, setActiveDocumentId] = useState<string | null>(null);
  const [settings, setSettings] = useState<SettingType>(DefaultSettings);
  const [currentTab, setCurrentTab] = useState<number>(1);
  const openDocument = useCallback((documentId: string) => {
    setActiveDocumentId(documentId);
    setCurrentTab(1);
  }, []);
  if (env == null) {
    return <div>Loading configuration...</div>;
  }
  return (
    <>
      <div style={{ width: "100%", alignItems: "stretch" }}>
        <HStack width={"100%"}>
          <Box width={"100%"}>
            <Text fontSize="lg" fontWeight="bold">
              SkyDocs
            </Text>
          </Box>
          <Box style={{ float: "right" }}>
            {patientId && env && (
              <SettingsComponent
                onSettingsChange={(settings) => {
                  setSettings(settings);
                }}
                patientId={patientId}
                env={env}
              />
            )}
          </Box>
        </HStack>
        <HStack align={"top"} width={"100%"}>
          <Box width={"100%"}>
            <Tabs
              index={currentTab}
              flexDirection="column"
              flex="1 1 1"
              onChange={setCurrentTab}
              // height="100vh"
              // maxHeight="100vh"
              // overflowY="auto"
            >
              <TabList>
                <Tab>Upload new</Tab>
                <Tab>Documents</Tab>
                {/* Using style to hide tab here to avoid current tab index skew when SearchGlass suddenly appears */}
                <Tab
                  style={{
                    display: settings.enableSearchGlass ? "block" : "none",
                  }}
                >
                  SearchGlass
                </Tab>
                <Tab
                  style={{
                    display: settings.enableSearchGlass ? "block" : "none",
                  }}
                >
                  FHIR Settings
                </Tab>
                {/* <Tab>EvidenceViewer</Tab> */}
                <Tab
                  style={{
                    display: settings.enableDocumentVectorBasedSearch
                      ? "block"
                      : "none",
                  }}
                >
                  Document Search
                </Tab>
                <Tab
                  style={{
                    display: settings.enableLBISearch ? "block" : "none",
                  }}
                >
                  LBI Search
                </Tab>
              </TabList>

              <TabPanels flex="1 1 0">
                <TabPanel>
                  <DocumentUploader
                    env={env}
                    onDocumentUploaded={openDocument}
                    patientId={patientId || identifier}
                  />
                </TabPanel>
                <TabPanel>
                  {!activeDocumentId && (
                    <DocumentList
                      env={env}
                      onSelectDocument={setActiveDocumentId}
                      patientId={patientId || identifier}
                    />
                  )}
                  {activeDocumentId && (
                    <>
                      <LinkButton
                        onClick={() => {
                          setActiveDocumentId(null);
                        }}
                      >
                        Back
                      </LinkButton>
                      <PaperglassWidget
                        env={env}
                        documentId={activeDocumentId}
                        settings={settings}
                        patientId={patientId}
                      />
                    </>
                  )}
                </TabPanel>
                <TabPanel>
                  <SearchGlass env={env} identifier={patientId || identifier} />
                </TabPanel>
                <TabPanel>
                  <>
                    <FHIRSettings
                      patientId={patientId || identifier}
                      env={env}
                    />{" "}
                  </>
                </TabPanel>
                <TabPanel>
                  {patientId && (
                    <Box w={"100%"}>
                      <DocumentVectorBasedSearch
                        patientId={patientId}
                        settings={settings}
                      />
                    </Box>
                  )}
                </TabPanel>
                <TabPanel>
                  <LBISearch env={env} patientId={patientId || identifier} />
                </TabPanel>
              </TabPanels>
            </Tabs>
          </Box>
        </HStack>
      </div>
    </>
  );
};

function App({ identifier }: { identifier: string }) {
  // 2 tabs: DocumentUploader and DocumentLister
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Main identifier={identifier} />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
