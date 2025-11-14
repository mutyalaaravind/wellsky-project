import {
  memo,
  startTransition,
  Suspense,
  useCallback,
  useEffect,
  useState,
} from "react";
import {
  Tabs,
  TabList,
  Tab,
  TabPanels,
  Text,
  Tooltip,
  Box,
} from "@chakra-ui/react";
import { usePdfWidgetStore } from "./store/pdfViewerStore";
import { useDocumentsApi } from "hooks/useDocumentsApi";
import { usePdfViewerContext } from "./context/PdfViewerContext";
import OverlayLoader from "screens/review/OverlayLoader";
import PdfViewer from "./PdfViewer";
import acss from "react-pdf/dist/Page/AnnotationLayer.css";
import tcss from "react-pdf/dist/Page/TextLayer.css";

import { useStyles } from "hooks/useStyles";
import { DocumentFile } from "types";
import { getDocumentTabLabel } from "utils/helpers";
import useViewerInstance from "./context/useViewerInstance";

type Props = {
  onDocumentOpened: React.Dispatch<React.SetStateAction<DocumentFile | null>>;
};

const DocumentsViewer = memo(({ onDocumentOpened }: Props) => {
  useStyles(acss);
  useStyles(tcss);

  const {
    documents,
    env,
    setPdfUrlForDocument,
    blob,
    setBlob,
    index,
    setIndex,
  } = usePdfWidgetStore();
  const { patientId } = usePdfViewerContext();
  const [loading, setLoading] = useState(false);

  const { getPdfUrl } = useDocumentsApi({
    apiRoot: env?.API_URL,
    patientId: patientId as string,
    env,
  });

  useEffect(() => {
    if (documents.length > 0) {
      const doc = documents[index];

      const loadData = async () => {
        let pdfUrl = doc.pdfUrl;

        try {
          onDocumentOpened(doc);
          if (!pdfUrl) {
            setLoading(true);
            pdfUrl = await getPdfUrl(doc.id);
            setPdfUrlForDocument(doc.id, pdfUrl);
          }

          if (!blob.has(doc.id)) {
            setLoading(true);
            const res = await fetch(pdfUrl);
            const blob = await res.blob();
            setBlob(doc.id, blob);
            setLoading(false);
          }
        } catch (error) {
          console.error(error);
        } finally {
          setLoading(false);
        }
      };

      loadData();
    }
  }, [
    blob,
    documents,
    getPdfUrl,
    index,
    onDocumentOpened,
    setBlob,
    setPdfUrlForDocument,
  ]);

  const viewerInstance = useViewerInstance();

  const onTabChange = useCallback(
    (index: number) => {
      startTransition(() => {
        setLoading(true);
        setTimeout(() => {
          setIndex(index);
          setTimeout(() => {
            viewerInstance?.dispatchEvent?.(
              "pdfViewer_documentChanged",
              documents[index],
            );
            setLoading(false);
          }, 200);
        }, 300);
      });
    },
    [documents, setIndex, viewerInstance],
  );

  return (
    <Tabs maxW="100%" onChange={onTabChange} index={index} p={0} flex={1}>
      <TabList overflow="auto hidden" py="4px">
        {documents?.map((doc, index) => {
          return (
            <Tab
              id={doc.id}
              key={doc.id}
              data-pendoid={`pdf-document-${index}`}
              data-pendo-fullname={`${doc.file_name}`}
              data-pendo-displayname={`${getDocumentTabLabel(doc.file_name, index)}`}
            >
              <Tooltip
                label={doc.file_name}
                data-pendoid={`pdf-document-${index}-tooltip`}
              >
                <Text
                  noOfLines={3}
                  data-pendoid={`pdf-document-${index}-label`}
                >
                  {getDocumentTabLabel(doc.file_name, index)}
                </Text>
              </Tooltip>
            </Tab>
          );
        })}
      </TabList>

      <TabPanels p="0">
        <link rel="stylesheet" href="react-pdf/dist/Page/AnnotationLayer.css" />
        {loading || !blob.has(documents?.[index]?.id) ? (
          <Box h={"100%"} w={"100%"}>
            <OverlayLoader />
          </Box>
        ) : (
          <Suspense fallback={"Loading..."}>
            <PdfViewer
              document={documents?.[index]}
              blob={blob.get(documents?.[index]?.id) as Blob}
            />
          </Suspense>
        )}
      </TabPanels>
    </Tabs>
  );
});

export default DocumentsViewer;
