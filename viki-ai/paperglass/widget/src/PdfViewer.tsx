import "./PdfViewer.css";

import { useRef, useEffect, useState, useCallback, FC, memo } from "react";

import { usePdf } from "./hooks/usePdf";
import { Spinner } from "@mediwareinc/wellsky-dls-react";
import {
  Grid,
  GridItem,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
} from "@chakra-ui/react";
import DataTable from "./components/DataTable";
import { APIStatus, Env } from "./types";
import { useSummarizer } from "./hooks/useSummarizerApi";
import { useExtractApi } from "./hooks/useExtractApi";
import CustomFormsComponent, {
  CustomFormsComponentProps,
} from "./components/custom-form";
import { getDebugValue } from "./utils/helpers";

type PdfViewerProps = {
  url: string;
  annotations?: Annotation[];
  showPreviews?: boolean;
  summaries?: Summary[];
  busyPages?: number[];
  defaultPage?: number;
  env?: Env;
  documentId?: string;
  correction?: number;
  showPage?: number;
  onPageChange?: (page: number) => void;
};

type Annotation = {
  x: number;
  y: number;
  width: number;
  height: number;
  text: string;
  page: number;
};

type Summary = {
  text: string;
  page: number;
};

type Vector2 = {
  x: number;
  y: number;
};

const annotationKey = (annotation: Annotation) =>
  `a-${annotation.x}-${annotation.y}-${annotation.width}-${annotation.height}`.replace(
    /\./g,
    "_",
  );

export const PdfViewer: FC<PdfViewerProps> = ({
  env,
  url,
  documentId,
  showPage,
  onPageChange,
  annotations = [],
  showPreviews = false,
  busyPages = [],
  defaultPage = 1,
  correction = 0.00,

}: PdfViewerProps) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const {
    currentPage,
    prevPage,
    nextPage,
    isRendering,
    pageCount,
    pageWidth,
    pageHeight,
    setCurrentPage,
    renderPreview,
  } = usePdf(canvasRef, url, defaultPage);
  const debug = getDebugValue();

  const [scale, setScale] = useState<Vector2>({ x: 1, y: 1 });
  const [size, setSize] = useState<Vector2>({ x: 0, y: 0 });
  const previousHighlightedAnnotationRef = useRef<Annotation | null>(null);
  const [highlightedAnnotation, setHighlightedAnnotation] =
    useState<Annotation | null>(null);
  const [highlightedSummaryText, setHighlightedSummaryText] =
    useState<string>("");

  const leftAnnotationsRef = useRef<HTMLDivElement>(null);
  const rightAnnotationsRef = useRef<HTMLDivElement>(null);
  // Here's an actuall mess with zero-indexed page numbers mixed with one-indexed page numbers.
  // Please forgive me for this. I did not have time to fix this. - Andrew

  const MemoizedCustomForm = memo(
    CustomFormsComponent,
    (
      prevProps: Readonly<CustomFormsComponentProps>,
      nextprops: Readonly<CustomFormsComponentProps>,
    ) => {
      //console.log("memoprops", prevProps.originalData, nextprops.originalData, prevProps.newData, nextprops.newData, prevProps.originalData === nextprops.originalData, prevProps.newData === nextprops.newData);
      return (
        JSON.stringify(prevProps.newData) === JSON.stringify(nextprops.newData)
      );
    },
  );

  const updateScale = useCallback(() => {
    // Calculates ratio of canvas width to page width
    const newScale = {
      x:
        (canvasRef.current ? canvasRef.current.offsetWidth : 0) /
        (pageWidth ? pageWidth : 1),
      y:
        (canvasRef.current ? canvasRef.current.offsetHeight : 0) /
        (pageHeight ? pageHeight : 1),
    };
    setScale(newScale);
    setSize({
      x: canvasRef.current ? canvasRef.current.offsetWidth : 0,
      y: canvasRef.current ? canvasRef.current.offsetHeight : 0,
    });
    console.log("New scale", newScale);
  }, [pageWidth, pageHeight, canvasRef]);

  useEffect(() => {
    // Update scale when window is resized
    window.addEventListener("resize", updateScale);
    return () => {
      window.removeEventListener("resize", updateScale);
    };
  }, [updateScale]);

  useEffect(() => {
    // Update scale when page changes
    updateScale();
    onPageChange && onPageChange(currentPage);
  }, [currentPage, updateScale]);

  useEffect(() => {
    if (previousHighlightedAnnotationRef.current !== null) {
      if (leftAnnotationsRef.current) {
        const el: HTMLDivElement | null =
          leftAnnotationsRef.current.querySelector(
            `.${annotationKey(previousHighlightedAnnotationRef.current)}`,
          );
        if (el !== null) {
          el.classList.remove("highlighted");
        }
      }
      if (rightAnnotationsRef.current) {
        const el: HTMLDivElement | null =
          rightAnnotationsRef.current.querySelector(
            `.${annotationKey(previousHighlightedAnnotationRef.current)}`,
          );
        if (el !== null) {
          el.classList.remove("highlighted");
        }
      }
    }
    if (highlightedAnnotation !== null) {
      if (leftAnnotationsRef.current) {
        const el: HTMLDivElement | null =
          leftAnnotationsRef.current.querySelector(
            `.${annotationKey(highlightedAnnotation)}`,
          );
        if (el !== null) {
          el.classList.add("highlighted");
        }
      }
      if (rightAnnotationsRef.current) {
        const el: HTMLDivElement | null =
          rightAnnotationsRef.current.querySelector(
            `.${annotationKey(highlightedAnnotation)}`,
          );
        if (el !== null) {
          el.classList.add("highlighted");
        }
      }
    }
    previousHighlightedAnnotationRef.current = highlightedAnnotation;
  }, [highlightedAnnotation]);

  useEffect(() => {
    console.log("correction applied", correction);
  }, [correction])

  useEffect(() => {
    if (annotations.length > 0) {
      console.log("annotations", annotations);
      const annotation = annotations[0];
      setCurrentPage(annotation.page);
    }
  }, [annotations]);

  const showChakraGrid = true;
  if (showChakraGrid) {
    return (
      <Grid templateColumns="repeat(12, 1fr)" gap={1} width="100%">
        <GridItem w="100%" colSpan={2} h="10">
          <PreviewList
            pageCount={pageCount}
            currentPage={currentPage}
            setCurrentPage={setCurrentPage}
            renderPreview={renderPreview}
            busyPages={busyPages}
          />
        </GridItem>
        <GridItem w="100%" colSpan={5} h="10">
          <div style={{ position: "relative" }}>
            <canvas
              ref={canvasRef}
              style={{
                height: "100%", // Stretch the canvas visually without affecting the aspect ratio and its underlying context size
              }}
            ></canvas>
            <div
              style={{ position: "absolute", inset: 0 }}
              ref={leftAnnotationsRef}
            >
              {annotations
                ?.map((annotation) => (
                  annotation.page === currentPage && (
                    <div
                      key={annotationKey(annotation)}
                      className={`left-annotation ${annotationKey(annotation)}`}
                      style={{
                        position: "absolute",
                        left: (annotation.x * size.x) + correction,
                        top: (annotation.y * size.y) + correction,
                        minWidth: (annotation.width * size.x) + correction,
                        minHeight: (annotation.height * size.y) + correction,
                        // left: annotation.x * scale.x,
                        // top: annotation.y * scale.y,
                        // minWidth: annotation.width * scale.x,
                        // minHeight: annotation.height * scale.y,
                        // border: "2px solid rgba(255, 0, 0, 0.75)",
                        // Do not wrap text
                        //whiteSpace: 'nowrap',
                        // backgroundColor: 'rgba(255, 255, 0, 0.5)',
                      }}
                      onMouseEnter={(e) => {
                        setHighlightedAnnotation(annotation);
                        // console.log(e.target);
                        // (e as any).target.style.backgroundColor = 'rgba(255, 255, 0, 0.75)';
                        // (e as any).target.style.color = '#000000';
                      }}
                      onMouseLeave={(e) => {
                        setHighlightedAnnotation(null);
                        // (e as any).target.style.backgroundColor = 'transparent';
                        // (e as any).target.style.color = 'transparent';
                      }}
                    >
                      {/*{annotation.text}*/}
                    </div>)
                ))}
            </div>
          </div>
        </GridItem>
      </Grid>
    );
  }
};

type PreviewListProps = {
  pageCount: number;
  currentPage: number;
  setCurrentPage: (page: number) => void;
  renderPreview: (page: number, ref: HTMLCanvasElement) => void;
  busyPages: number[];
};

const PreviewList: FC<PreviewListProps> = ({
  pageCount,
  currentPage,
  setCurrentPage,
  renderPreview,
  busyPages,
}: PreviewListProps) => {
  return (
    <div
      style={{
        // maxHeight: "100vh",
        // overflow: "scroll",
      }}
    >
      {Array.from({ length: pageCount }, (_, i) => i).map((page) => (
        <div
          key={page}
          style={{
            display: "flex",
            justifyContent: "center",
            margin: "0 0 1rem",
            position: "relative",
            padding: "1rem",
            background:
              page + 1 === currentPage ? "rgba(0, 128, 128, 1)" : "transparent",
          }}
        >
          <a
            href="#page"
            onClick={(event) => {
              event.preventDefault();
              setCurrentPage(page + 1);
            }}
          >
            <Preview pageNumber={page + 1} renderPreview={renderPreview} />
          </a>
          {busyPages.includes(page + 1) ? (
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
                pointerEvents: "none",
              }}
            >
              <Spinner color="white" />
              <div>PROCESSING</div>
            </div>
          ) : null}
          <div
            style={{
              position: "absolute",
              bottom: "1rem",
              right: "1rem",
              backgroundColor: "rgba(0, 0, 0, 0.5)",
              color: "white",
              padding: "0.25rem 1rem",
              fontSize: "1.5rem",
            }}
          >
            {page + 1}
          </div>
        </div>
      ))}
    </div>
  );
};

type PreviewProps = {
  pageNumber: number;
  renderPreview: (page: number, ref: HTMLCanvasElement) => void;
};

// Using memo to prevent duplicate rendering of previews (pdf.js does not like it when multiple render calls are made on the same canvas)
const Preview: FC<PreviewProps> = memo(({ pageNumber, renderPreview }) => {
  return (
    <canvas
      ref={(ref) => {
        console.log("Triggering render of preview for page " + pageNumber);
        ref && renderPreview(pageNumber, ref);
      }}
      style={{
        width: "100%",
        border: "1px solid rgba(0, 0, 0, 0.5)",
        boxShadow: "0 0 1rem rgba(0, 0, 0, 0.5)",
      }}
    />
  );
});
