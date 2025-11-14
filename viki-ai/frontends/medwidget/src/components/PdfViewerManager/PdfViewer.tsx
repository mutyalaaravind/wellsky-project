import { memo, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import PreviewList from "./PreviewList";
import { Box, Flex } from "@chakra-ui/react";
import css from "./PdfViewer.css";
import { DocumentCallback } from "react-pdf/dist/cjs/shared/types";
import { PdfViewerProps } from "./types";

import OverlayLoader from "screens/review/OverlayLoader";
import { usePdfWidgetStore } from "./store/pdfViewerStore";
import { useStyles } from "hooks/useStyles";
import PageToolbar from "./PageToolbar";

// pdfjs.GlobalWorkerOptions.workerSrc = new URL(
//   "pdfjs-dist/build/pdf.worker.min.mjs",
//   import.meta.url,
// ).toString();

pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

const options = {
  cMapUrl: `https://unpkg.com/pdfjs-dist@${pdfjs.version}/cmaps/`,
  standardFontDataUrl: `https://unpkg.com/pdfjs-dist@${pdfjs.version}/standard_fonts`,
};

const PdfViewer = memo(
  ({ defaultCurrentPage = 1, document, blob }: PdfViewerProps) => {
    useStyles(css);
    const [pdf, setPdf] = useState<DocumentCallback>();
    const canvasRef = useRef<HTMLCanvasElement>(null);

    const {
      updateDocumentInfo,
      documentInfo,
      allPageProfiles,
      extractionType,
    } = usePdfWidgetStore();

    const [rotation, setRotation] = useState(0);
    const [zoom, setZoom] = useState(1);
    const [size, setSize] = useState({ height: 0, width: 0 });

    const currentDocumentInfo = documentInfo.get(document.id);

    const currentDocumentPageProfile = allPageProfiles.get(document.id);

    function onDocumentLoadSuccess(
      loadedDoc: DocumentCallback | undefined,
    ): void {
      if (loadedDoc) {
        setPdf(loadedDoc);
        updateDocumentInfo(
          document?.id as string,
          currentDocumentInfo?.currentPage || defaultCurrentPage,
          loadedDoc.numPages,
        );
      }
    }

    const setPageNumber = useCallback(
      (pageNumber: number) => {
        updateDocumentInfo(
          document?.id as string,
          pageNumber,
          currentDocumentInfo?.totalPages || 0,
        );
      },
      [document?.id, currentDocumentInfo?.totalPages, updateDocumentInfo],
    );

    const renderPreview = useCallback(
      (pageNumber: number, ref: HTMLCanvasElement, callBack?: () => void) => {
        if (!pdf) {
          return;
        }
        if (!ref) {
          console.error("No ref");
          return;
        }
        pdf
          ?.getPage?.(pageNumber)
          ?.then?.((page) => {
            const viewport = page.getViewport({ scale: 0.5 });
            const canvas = ref;
            const context = canvas.getContext("2d");

            if (!context) {
              console.error("No context");
              return;
            }
            canvas.height = viewport.height;
            canvas.width = viewport.width;
            page
              .render({ canvasContext: context, viewport })
              .promise.then(() => {
                ref.dataset.docId = document?.id as string;
                callBack?.();
              });
          })
          .finally(() => {
            callBack?.();
          });
      },
      [pdf, document?.id],
    );

    const [unmounting, setUnmounting] = useState(false);

    useEffect(() => {
      setTimeout(() => {
        setUnmounting(false);
      }, 500);
      return () => {
        setUnmounting(true);
      };
    }, [currentDocumentInfo?.currentPage]);

    const annos = useMemo(
      () =>
        currentDocumentInfo?.pages.get(currentDocumentInfo.currentPage)
          ?.annotations,
      [currentDocumentInfo?.currentPage, currentDocumentInfo?.pages],
    );

    const isPageDirectionWiseRotationEnabled = true;

    const annotationRotation = useMemo(() => {
      if (!isPageDirectionWiseRotationEnabled) {
        return 0;
      }

      const orientation = annos?.[0]?.orientation || "PAGE_UP";

      let mainRotation = 0;

      if (orientation === "PAGE_RIGHT") {
        mainRotation = 90;
      } else if (orientation === "PAGE_DOWN") {
        mainRotation = 180;
      } else if (orientation === "PAGE_LEFT") {
        mainRotation = 270;
      }

      return mainRotation;
    }, [annos, isPageDirectionWiseRotationEnabled]);

    if (unmounting && false) {
      return null;
    }

    return (
      <Flex
        direction="row"
        maxH="85vh"
        overflow="hidden"
        paddingTop="8px"
        gap={1}
      >
        <PreviewList
          pageNumber={currentDocumentInfo?.currentPage || 1}
          onPageChange={setPageNumber}
          totalPages={currentDocumentInfo?.totalPages || 0}
          renderPreview={renderPreview}
          documentId={document?.id}
          currentDocumentPageProfile={currentDocumentPageProfile}
          extractionType={extractionType}
        />

        <Document
          className={"pdf-document"}
          // file={file}
          file={blob}
          onLoadSuccess={onDocumentLoadSuccess}
          options={options}
          loading={<OverlayLoader>Loading PDF...</OverlayLoader>}
        >
          <PageToolbar
            currentPage={currentDocumentInfo?.currentPage || 1}
            totalPages={currentDocumentInfo?.totalPages || 0}
            rotation={rotation}
            setRotation={setRotation}
            zoom={zoom}
            setZoom={setZoom}
          />
          <Box
            w={"100%"}
            maxH="calc(100% - 40px)"
            height={"100%"}
            overflow="auto"
          >
            <Box
              minH={"min-content"}
              minW={"min-content"}
              transform={`rotate(${rotation}deg)`}
            >
              <Page
                className={"pdf-page"}
                pageNumber={currentDocumentInfo?.currentPage}
                scale={zoom}
                renderTextLayer
                renderAnnotationLayer
                canvasRef={canvasRef}
                onLoadSuccess={(page) => {
                  const viewport = page.getViewport({ scale: zoom });

                  setSize({
                    height: viewport.height,
                    width: viewport.width,
                  });
                }}
              >
                <Box
                  position="absolute"
                  height={size.height || "100%"}
                  width={size.width || "100%"}
                  top={0}
                  left={0}
                  transform={`rotate(${annotationRotation}deg)`}
                  transformOrigin={"center"}
                  zIndex={2}
                >
                  {annos?.map(
                    (anno) =>
                      anno && (
                        <div
                          key={`${anno.x}-${anno.y}-${anno.width}-${anno.height}`}
                          id={`${anno.x}-${anno.y}-${anno.width}-${anno.height}`}
                          ref={(ref) => {
                            setTimeout(() => {
                              if (ref) {
                                ref.scrollIntoView({
                                  block: "center",
                                  behavior: "smooth",
                                  inline: "center",
                                });
                              }
                            }, 500);
                          }}
                          className="left-annotation"
                          style={{
                            position: "absolute",
                            left: `calc(${anno.x * 100}% - 2px)`,
                            top: `calc(${anno.y * 100}% - 2px)`,
                            width: `calc(${anno.width * 100}% + 4px)`,
                            height: `calc(${anno.height * 100}% + 4px)`,
                            border: "1px solid red",
                            zIndex: 1,
                          }}
                        ></div>
                      ),
                  )}
                </Box>
              </Page>
            </Box>
          </Box>
        </Document>
      </Flex>
    );
  },
);

export default PdfViewer;
