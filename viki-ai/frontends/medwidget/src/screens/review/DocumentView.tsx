import {
  forwardRef,
  useCallback,
  useContext,
  useEffect,
  useImperativeHandle,
  useMemo,
  useState,
} from "react";

import {
  Alert,
  AlertDescription,
  AlertTitle,
  Box,
  Heading,
  IconButton,
} from "@chakra-ui/react";
import { Spinner, Tabs } from "@mediwareinc/wellsky-dls-react";
import { AlertCircle, Back } from "@mediwareinc/wellsky-dls-react-icons";

import { DocumentFile, Env } from "types";
import { ContextDocumentItemFilter } from "tableOfContentsTypes";
import { Block } from "components/Block";
import { useDocumentsApi } from "hooks/useDocumentsApi";
import { PdfViewer } from "components/PdfViewer";
import { useAuth } from "hooks/useAuth";
import { useStyles } from "hooks/useStyles";

import css from "./DocumentView.css";
import { PageProfile } from "store/storeTypes";
import { ShadowDOMContext } from "context/ShadowDOMContext";
import { usePatientProfileStore } from "store/patientProfileStore";
import { produce } from "immer";

type DocumentViewProps = {
  documents: DocumentFile[];
  env: Env;
  onDocumentOpened: (document: DocumentFile) => void;
  onClose: () => void;
  onPageProfileStateChange: (
    pageProfileState: Record<string, ContextDocumentItemFilter>,
  ) => void;
  pageProfileState: Record<string, ContextDocumentItemFilter>;
  setPageProfileState: React.Dispatch<
    React.SetStateAction<Record<string, ContextDocumentItemFilter>>
  >;
  getPageProfileState: (
    documentId: string,
    profileType: string,
    page: number,
  ) => boolean;
  noBoxShadow?: boolean;
};

export const DocumentView = forwardRef(
  (
    {
      documents,
      env,
      onDocumentOpened,
      onClose,
      onPageProfileStateChange,
      pageProfileState,
      setPageProfileState,
      getPageProfileState,
      noBoxShadow = false,
    }: DocumentViewProps,
    ref: any,
  ) => {
    const { patientId } = useAuth();
    const [currentDocument, setCurrentDocument] = useState<DocumentFile>(
      documents[0],
    );
    const currentTabIndex = documents.findIndex(
      (doc) => doc.id === currentDocument.id,
    );
    const [annotations, setAnnotations] = useState<Array<any>>([]);

    useStyles(css);

    // Map of document IDs to their current page numbers
    const [documentPageNumbers, setDocumentPageNumbers] = useState<
      Record<string, number>
    >({});

    const documentPageChanged = useCallback(
      (documentId: string, pageNumber: number) => {
        if (pageNumber) {
          setDocumentPageNumbers((prev) => ({
            ...prev,
            [documentId]: pageNumber,
          }));
        }
      },
      [],
    );

    const { setAllPageProfiles } = usePatientProfileStore();

    const handlePageProfileSelection = useCallback(
      (documentId: string, pageNumber: number, isSelected: boolean) => {
        setAllPageProfiles((draft) => {
          return produce(draft, (prev) => {
            if (!prev) {
              return new Map<
                string,
                Record<string | number, Record<number, PageProfile>>
              >();
            }
            if (!prev.has(documentId)) {
              prev.set(documentId, {});
            }

            const documentProfiles = prev.get(documentId);

            if (documentProfiles && documentProfiles.medication) {
              const profile = documentProfiles.medication[pageNumber];
              if (profile) {
                profile.isSelected = isSelected;
              }
            }
          });
        });
      },
      [setAllPageProfiles],
    );

    useEffect(() => {
      onDocumentOpened(currentDocument);
    }, [currentDocument, onDocumentOpened]);

    const { shadowRoot } = useContext(ShadowDOMContext);

    useImperativeHandle(
      ref,
      () => ({
        showDocumentPage: (
          documentId: string,
          pageNumber: number,
          annotationsList: Array<any>,
        ) => {
          if (pageNumber) {
            setCurrentDocument(
              documents.find((doc) => doc.id === documentId) || documents[0],
            );
            setDocumentPageNumbers((prev) => ({
              ...prev,
              [documentId]: pageNumber,
            }));

            setTimeout(() => {
              const element = shadowRoot?.getElementById(
                `${documentId}-${pageNumber}-0`,
              );
              if (element) {
                element.scrollIntoView();
              }
            }, 500);
          }

          setAnnotations(annotationsList);
        },
      }),
      [documents, shadowRoot],
    );

    const annotationsString = JSON.stringify(annotations);

    const tabItems = useMemo(() => {
      const anno = (() => {
        try {
          return JSON.parse(annotationsString);
        } catch (error) {
          return [];
        }
      })();
      return documents?.map((doc, index) => ({
        children: (
          <DocumentTab
            env={env}
            patientId={patientId}
            document={doc}
            defaultPageNumber={documentPageNumbers[doc.id] || 1}
            onPageChange={documentPageChanged}
            annotations={anno}
            onPageProfileSelection={handlePageProfileSelection}
            pageProfileState={pageProfileState}
            getPageProfileState={getPageProfileState}
          />
        ),
        key: doc.id,
        label: (
          <div
            title={doc.file_name}
          >{`${doc.file_name.substring(0, 10)}.. [${(index + 1 + 9).toString(36).toUpperCase()}]`}</div>
        ),
      }));
    }, [
      annotationsString,
      documentPageChanged,
      documentPageNumbers,
      documents,
      env,
      getPageProfileState,
      handlePageProfileSelection,
      pageProfileState,
      patientId,
    ]);

    return (
      <Block style={noBoxShadow ? { boxShadow: "none" } : null}>
        <div
          style={{
            display: "flex",
            flexDirection: "row",
            gap: "1rem",
            alignItems: "center",
            padding: "0.5rem",
          }}
        >
          <IconButton
            aria-label="Back"
            onClick={onClose}
            variant="link"
            color="black"
          >
            <Back />
          </IconButton>
          <Heading size="md">
            Document Viewer
            {/* &mdash; {currentDocument !== null ? currentDocument.filename : '<no document>'}*/}
          </Heading>
        </div>
        {/*<div>Document ID: {documentId}</div>*/}
        <Tabs
          id="document-tabs"
          children={[]}
          isLazy={true}
          index={currentTabIndex}
          onChange={(index: number) => {
            setCurrentDocument(documents[index]);
            setDocumentPageNumbers((prev) => ({
              ...prev,
              [documents[index].id]: prev[documents[index].id] || 1,
            }));
            setAnnotations([]);
          }}
          items={tabItems}
          className={"full-height-chakra-tabs"}
          style={{ display: "flex", flexDirection: "column", flex: "1" }}
        />
      </Block>
    );
  },
);

type DocumentTabProps = {
  env: Env;
  patientId: string;
  document: DocumentFile;
  defaultPageNumber: number;
  onPageChange: (documentId: string, pageNumber: number) => void;
  annotations: Array<any>;
  onPageProfileSelection: (
    documentId: string,
    pageNubmer: number,
    isSelected: boolean,
  ) => void;
  pageProfileState: Record<string, ContextDocumentItemFilter>;
  getPageProfileState: (
    documentId: string,
    profileType: string,
    page: number,
  ) => boolean;
};

const DocumentTab = ({
  env,
  patientId,
  document,
  defaultPageNumber,
  onPageChange,
  annotations,
  onPageProfileSelection,
  pageProfileState,
  getPageProfileState,
}: DocumentTabProps) => {
  const [pdfUrl, setPdfUrl] = useState<string>("");
  const { getPdfUrl, getPage } = useDocumentsApi({
    apiRoot: env?.API_URL,
    patientId: patientId,
  });
  const [error, setError] = useState<Error | null>(null);

  // const pdfViewerRef = useRef<any>(null);

  useEffect(() => {
    getPdfUrl(document.id)
      .then((url) => setPdfUrl(url))
      .catch(setError);
  }, [document.id, getPdfUrl]);

  const onPageChanged = useCallback(
    (pageNumber: number) => {
      onPageChange(document.id, pageNumber);
    },
    [document, onPageChange],
  );

  const getPageRotation = useCallback(
    (pageNumber: number) => {
      return getPage(document.id, pageNumber)
        .then((page) => {
          if (
            typeof page === "undefined" ||
            page === null ||
            !page.hasOwnProperty("rotation")
          ) {
            return 0;
          }
          // Rount to nearest 90 degrees
          let rotationDegrees = (page.rotation / Math.PI) * 180;
          if (rotationDegrees < 0) {
            rotationDegrees += 360;
          }
          return Math.round(rotationDegrees / 90) * 90;
        })
        .catch((error) => {
          console.log(`error in getRotation: ${error}`);
          return 0;
        });
    },
    [document, getPage],
  );

  return (
    <>
      <div dangerouslySetInnerHTML={{ __html: "<!-- DocumentTab -->" }} />
      {pdfUrl !== "" ? (
        // PDF URL is available
        <PdfViewer
          env={env}
          documentId={document.id}
          url={pdfUrl}
          defaultPage={defaultPageNumber}
          onPageChange={onPageChanged}
          annotations={annotations}
          onPageProfileSelection={onPageProfileSelection}
          pageProfileState={pageProfileState}
          getPageProfileState={getPageProfileState}
          getPageRotation={getPageRotation}
        />
      ) : error !== null ? (
        // Error fetching PDF URL
        <Alert status="error">
          <AlertCircle />
          <Box>
            <AlertTitle>An error occured</AlertTitle>
            <AlertDescription>
              Failed to fetch PDF
              {/* URL: {error.toString()} */}
            </AlertDescription>
          </Box>
        </Alert>
      ) : (
        // Still loading
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            height: "100%",
            flexDirection: "column",
            gap: "1rem",
            padding: "2rem",
          }}
        >
          <Spinner />
          Loading document URL...
        </div>
      )}
      <div dangerouslySetInnerHTML={{ __html: "<!-- /DocumentTab -->" }} />
    </>
  );
};
