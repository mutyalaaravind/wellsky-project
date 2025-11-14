import React, {
  useRef,
  RefObject,
  useEffect,
  useState,
  useCallback,
  FC,
  memo,
  forwardRef,
  useImperativeHandle,
  useMemo,
} from "react";
import { Spinner } from "@mediwareinc/wellsky-dls-react";
import { IconButton, useToken, Icon, Tooltip } from "@chakra-ui/react";
import { ChevronUpIcon, ChevronDownIcon } from "@chakra-ui/icons";

import { Env } from "types";

import { usePdf } from "hooks/usePdf";
import { Rotate90DegCCW } from "icons/Rotate90DegCCW";
import { Rotate90DegCW } from "icons/Rotate90DegCW";
import { ZoomIn } from "icons/ZoomIn";
import { ZoomOut } from "icons/ZoomOut";
import { ZoomFit } from "icons/ZoomFit";

import { ContextDocumentItemFilter } from "tableOfContentsTypes";

import css from "./PdfViewer.css";
import { useStyles } from "hooks/useStyles";

import PageBadge from "./PageBadge";
import { usePatientProfileStore } from "store/patientProfileStore";
import { PageProfile } from "store/storeTypes";

type PdfViewerProps = {
  env: Env;
  documentId: string;
  url: string;
  annotations?: Annotation[];
  busyPages?: number[];
  defaultPage?: number;
  correction?: number;
  onPageChange?: (page: number) => void;
  getPageRotation?: (page: number) => Promise<number>;
  onPageProfileSelection: (
    documentId: string,
    pageIndex: number,
    isSelected: boolean,
  ) => void;
  pageProfileState: Record<string, ContextDocumentItemFilter>;
  getPageProfileState: (
    documentId: string,
    profileType: string,
    page: number,
  ) => boolean;
  profileType?:
    | "medication"
    | "allergy"
    | "condition"
    | "immunization"
    | string;
};

type Annotation = {
  x: number;
  y: number;
  width: number;
  height: number;
  text: string;
  page: number;
  orientation?: "PAGE_RIGHT" | "PAGE_DOWN" | "PAGE_LEFT" | "PAGE_UP";
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

const positiveModulo = (dividend: number, divisor: number) =>
  ((dividend % divisor) + divisor) % divisor;

export const PdfViewer = forwardRef(
  (
    {
      env,
      documentId,
      url,
      annotations = [],
      busyPages = [],
      defaultPage = 1,
      correction = 0.0,
      onPageChange,
      getPageRotation = () => Promise.resolve(0),
      onPageProfileSelection,
      pageProfileState,
      getPageProfileState,
      profileType = "medication",
    }: PdfViewerProps,
    ref: any,
  ) => {
    const [panelColor] = useToken(
      // the key within the theme, in this case `theme.colors`
      "colors",
      // the subkey(s), resolving to `theme.colors.red.100`
      ["elm.700"],
      // a single fallback or fallback array matching the length of the previous arg
    );

    const canvasRef = useRef<HTMLCanvasElement>(null);
    const {
      currentPage,
      // prevPage,
      // nextPage,
      // isRendering,
      pageCount,
      pageWidth,
      pageHeight,
      setCurrentPage,
      renderPreview,
      zoom,
      setZoom,
      // Commented out in favor of CSS transforms
      // rotation,
      // setRotation,
    } = usePdf(canvasRef, url, defaultPage);

    useStyles(css);

    useImperativeHandle(
      ref,
      () => ({
        currentPage,
        setCurrentPage,
      }),
      [currentPage, setCurrentPage],
    );

    const [, setScale] = useState<Vector2>({ x: 1, y: 1 });
    const [rotation, setRotation] = useState<number>(0);
    const [size, setSize] = useState<Vector2>({ x: 0, y: 0 });
    const previousHighlightedAnnotationRef = useRef<Annotation | null>(null);
    const [highlightedAnnotation, setHighlightedAnnotation] =
      useState<Annotation | null>(null);

    const leftAnnotationsRef = useRef<HTMLDivElement>(null);
    const rightAnnotationsRef = useRef<HTMLDivElement>(null);
    // Here's an actuall mess with zero-indexed page numbers mixed with one-indexed page numbers.
    // Please forgive me for this. I did not have time to fix this. - Andrew

    const isHoverRef = useRef(false);
    const isDraggingRef = useRef(false);
    const [isDragging, setIsDragging] = useState(false);
    const dragStartRef = useRef<Vector2 | null>(null);
    const [translation, setTranslation] = useState<Vector2>({ x: 0, y: 0 });

    //Temporary page profile.  This will be replaced with a call to the backend.

    const { allPageProfiles } = usePatientProfileStore();

    const pageProfiles = allPageProfiles?.get(documentId)?.[profileType] || {};

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
    }, [currentPage, updateScale, onPageChange]);

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
      // correction
    }, [correction]);

    const annotationsString = JSON.stringify(annotations);

    useEffect(() => {
      try {
        const annotations = JSON.parse(annotationsString);
        if (annotations.length > 0) {
          const annotation = annotations[0];
          setCurrentPage(annotation.page);
        }
      } catch (error) {}
    }, [annotationsString, setCurrentPage]);

    useEffect(() => {
      // isMouseEngaged is true if the mouse is hovering over the viewer or if the user is dragging the canvas.
      // In other words, the user is focused on the PDF viewer and expects to interact with it.
      const isMouseEngaged = isHoverRef.current || isDraggingRef.current;

      const mouseMoveHandler = (e: MouseEvent) => {
        e.preventDefault();
        if (isDraggingRef.current && dragStartRef.current) {
          const dx = e.clientX - dragStartRef.current.x;
          const dy = e.clientY - dragStartRef.current.y;
          setTranslation((prev) => ({
            x: prev.x + dx,
            y: prev.y + dy,
          }));
          dragStartRef.current = { x: e.clientX, y: e.clientY };
        }
      };
      const mouseUpHandler = (e: MouseEvent) => {
        e.preventDefault();
        isDraggingRef.current = false;
        setIsDragging(false);
        dragStartRef.current = null;
      };
      const keyPressHandler = (e: KeyboardEvent) => {
        if (isMouseEngaged) {
          if (e.key === "+" || e.key === "=") {
            setZoom((prev) => Math.min(2, prev + 0.1));
          } else if (e.key === "-") {
            setZoom((prev) => Math.max(0.5, prev - 0.1));
          }
        }
      };
      // const keyDownHandler = (e: any) => {
      //   if (isMouseEngaged && e.ctrlKey && (e.which == 61 || e.which == 107 || e.which == 173 || e.which == 109 || e.which == 187 || e.which == 189)) {
      //     // Prevent the default browser zoom action (zoom in/out)
      //     console.log("Preventing default zoom action");
      //     e.preventDefault();
      //   }
      // };
      // const zoomPreventionHandler = (e: any) => {
      //   console.log('===', isMouseEngaged, e.ctrlKey);
      //   if (isMouseEngaged && (e.ctrlKey || e.metaKey)) {
      //     // Prevent the default browser zoom action (zoom in/out)
      //     console.log("Preventing default zoom action");
      //     e.preventDefault();
      //   }
      // }
      window.addEventListener("mousemove", mouseMoveHandler);
      window.addEventListener("mouseup", mouseUpHandler);
      window.addEventListener("keypress", keyPressHandler);
      // window.addEventListener("keydown", keyDownHandler);
      // window.addEventListener("mousewheel", zoomPreventionHandler);
      // window.addEventListener("wheel", zoomPreventionHandler);
      // window.addEventListener("DOMMouseScroll", zoomPreventionHandler);
      return () => {
        window.removeEventListener("mousemove", mouseMoveHandler);
        window.removeEventListener("mouseup", mouseUpHandler);
        window.removeEventListener("keypress", keyPressHandler);
        // window.removeEventListener("keydown", keyDownHandler);
        // window.removeEventListener("mousewheel", zoomPreventionHandler);
        // window.removeEventListener("wheel", zoomPreventionHandler);
        // window.removeEventListener("DOMMouseScroll", zoomPreventionHandler);
      };
    }, [setZoom]);

    useEffect(() => {
      if (getPageRotation) {
        getPageRotation(currentPage).then((rotation) => {
          setRotation(rotation);
        });
      }
    }, [currentPage, getPageRotation]);

    const annotationPadding = 4;

    const isPageDirectionWiseRotationEnabled = true;

    const rotateDegree = useMemo(() => {
      if (!isPageDirectionWiseRotationEnabled) {
        return 0;
      }

      if (annotations?.[0]?.orientation === "PAGE_RIGHT") {
        return 90;
      } else if (annotations?.[0]?.orientation === "PAGE_DOWN") {
        return 180;
      } else if (annotations?.[0]?.orientation === "PAGE_LEFT") {
        return 270;
      } else {
        return 0;
      }
    }, [annotations, isPageDirectionWiseRotationEnabled]);

    const annotationChangeFlag = useMemo(() => {
      if (annotations?.length) {
        return Date.now();
      }
      return 0;
    }, [annotations]);

    return pageCount ? (
      <div
        style={{
          display: "flex",
          flexDirection: "row",
          gap: "1rem",
          minHeight: 0,
        }}
      >
        <div style={{ minWidth: "100px", maxWidth: "10vw" }}>
          <PreviewList
            env={env}
            documentId={documentId}
            pageCount={pageCount}
            currentPage={currentPage}
            setCurrentPage={setCurrentPage}
            renderPreview={renderPreview}
            busyPages={busyPages}
            pageProfiles={pageProfiles}
            onPageProfileSelection={onPageProfileSelection}
            pageProfileState={pageProfileState}
            getPageProfileState={getPageProfileState}
            annotationChangeFlag={annotationChangeFlag}
          />
        </div>
        <div
          style={{
            display: "flex",
            flex: 1,
            minWidth: 0 /* minWidth is required to prevent overflow */,
          }}
        >
          <div
            style={{
              display: "flex",
              flex: 1,
              flexDirection: "column",
              minWidth: 0,
            }}
          >
            <div
              style={{
                background: panelColor,
                display: "flex",
                flexDirection: "row",
                alignItems: "center",
                gap: "0.5rem",
                padding: "0.5rem",
                color: "#FFFFFF",
                backgroundColor: "#10222F",
              }}
            >
              <span data-pendoid="page-count">
                Page {currentPage} of {pageCount}
              </span>

              <div style={{ flex: 1 }}></div>

              <IconButton
                variant="link"
                aria-label="Zoom To Fit"
                onClick={() => {
                  setZoom(1);
                  setTranslation({ x: 0, y: 0 });
                }}
                data-pendoid="zoom-to-fit"
              >
                <ZoomFit />
              </IconButton>
              <div>&nbsp;</div>
              <IconButton
                variant="link"
                aria-label="Zoom Out"
                onClick={() => setZoom(Math.max(0.5, zoom - 0.1))}
                data-pendoid="zoom-out"
              >
                <ZoomOut />
              </IconButton>
              <span style={{ width: "3rem", textAlign: "center" }}>
                {Math.round(zoom * 100)}%
              </span>
              <IconButton
                variant="link"
                aria-label="Zoom In"
                onClick={() => setZoom(Math.min(2, zoom + 0.1))}
                data-pendoid="zoom-in"
              >
                <ZoomIn />
              </IconButton>

              <div>&nbsp;</div>
              <div>&nbsp;</div>

              <IconButton
                variant="link"
                aria-label="Rotate 90° Counter-Clockwise"
                onClick={() => setRotation(rotation - 90)}
                data-pendoid="rotate-counter-clockwise"
              >
                <Rotate90DegCCW />
              </IconButton>
              <span style={{ width: "3rem", textAlign: "center" }}>
                {positiveModulo(rotation, 360)}°
              </span>
              <IconButton
                variant="link"
                aria-label="Rotate 90° Clockwise"
                onClick={() => setRotation(rotation + 90)}
                data-pendoid="rotate-clockwise"
              >
                <Rotate90DegCW />
              </IconButton>
            </div>
            <div
              style={{
                position: "relative",
                height: "100%",
                backgroundColor: "rgba(0, 0, 0, 0.1)",
                // overflow: "hidden",
                overflow: "auto",
                textAlign: "center",
                cursor: isDragging ? "all-scroll" : "default", // Use all-scroll cursor when dragging
              }}
              onWheel={(e: React.WheelEvent<HTMLDivElement>) => {
                // e.preventDefault();
                // if (e.deltaY < 0) {
                //   setZoom(Math.min(2, zoom + 0.1));
                // } else if (e.deltaY > 0) {
                //   setZoom(Math.max(0.5, zoom - 0.1));
                // }
              }}
              onContextMenu={(e) => {
                e.preventDefault();
              }}
              onMouseEnter={() => {
                isHoverRef.current = true;
              }}
              onMouseLeave={() => {
                isHoverRef.current = false;
              }}
              onMouseDown={(e) => {
                // If right button...
                if (e.button === 0) {
                  e.preventDefault();
                  isDraggingRef.current = true;
                  setIsDragging(true);
                  dragStartRef.current = { x: e.clientX, y: e.clientY };
                }
              }}
            >
              <div
                style={{
                  transform: `translate(${translation.x}px, ${translation.y}px) rotate(${rotation}deg)`,
                  transformOrigin: "center",
                  transition: isDragging
                    ? "none"
                    : "transform 0.15s ease-in-out", // Do not apply transitions when dragging - it feels jerky
                  // margin: "0 auto",
                  display: "inline-block",
                  textAlign: "left",
                }}
                ref={leftAnnotationsRef}
              >
                <canvas
                  data-pendoid="pdf-canvas"
                  ref={canvasRef}
                  style={
                    {
                      // height: "100%", // Stretch the canvas visually without affecting the aspect ratio and its underlying context size
                    }
                  }
                  // Mouse scroll event
                ></canvas>
                <div
                  style={{
                    position: "absolute",
                    height: "100%",
                    width: "100%",
                    zIndex: 1,
                    top: 0,
                    left: 0,
                  }}
                >
                  <div
                    style={{
                      display: "inline-block",
                      position: "absolute",
                      height: "100%",
                      width: "100%",
                      transform: `rotate(${rotateDegree}deg)`,
                      transformOrigin: "center",
                    }}
                  >
                    {annotations?.map(
                      (annotation, index) =>
                        annotation &&
                        annotation.page === currentPage && (
                          <div
                            id={`${documentId}-${annotation.page}-${index}`}
                            key={annotationKey(annotation)}
                            className={`left-annotation ${annotationKey(annotation)}`}
                            style={{
                              position: "absolute",
                              left:
                                annotation.x * size.x +
                                correction -
                                annotationPadding,
                              top:
                                annotation.y * size.y +
                                correction -
                                annotationPadding,
                              minWidth:
                                annotation.width * size.x +
                                correction +
                                annotationPadding * 2,
                              minHeight:
                                annotation.height * size.y +
                                correction +
                                annotationPadding * 2,
                            }}
                            onMouseEnter={() => {
                              setHighlightedAnnotation(annotation);
                            }}
                            onMouseLeave={() => {
                              setHighlightedAnnotation(null);
                            }}
                          >
                            {/*{annotation.text}*/}
                          </div>
                        ),
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    ) : (
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
        Rendering document...
      </div>
    );
  },
);

type PreviewListProps = {
  env: Env;
  profileType?: string;
  documentId: string;
  pageCount: number;
  currentPage: number;
  setCurrentPage: (page: number) => void;
  renderPreview: (page: number, ref: HTMLCanvasElement) => void;
  busyPages: number[];
  pageProfiles: Record<number, PageProfile>;
  onPageProfileSelection: (
    documentId: string,
    pageIndex: number,
    isSelected: boolean,
  ) => void;
  pageProfileState: Record<string, ContextDocumentItemFilter>;
  getPageProfileState: (
    documentId: string,
    profileType: string,
    page: number,
  ) => boolean;
  annotationChangeFlag?: number;
};

const PreviewList: FC<PreviewListProps> = ({
  env,
  documentId,
  pageCount,
  currentPage,
  setCurrentPage,
  renderPreview,
  busyPages,
  pageProfiles,
  onPageProfileSelection,
  pageProfileState,
  getPageProfileState,
  annotationChangeFlag,
}: PreviewListProps) => {
  const [bgColor, panelColor] = useToken(
    // the key within the theme, in this case `theme.colors`
    "colors",
    // the subkey(s)
    ["neutral.100", "elm.700"],
  );

  const elementRefs = useRef(new Array(pageCount).fill(null));

  const thumbnailListRef: RefObject<HTMLDivElement> =
    useRef<HTMLDivElement>(null);

  const scanNextPageOfInterest = (direction: string) => {
    const targetPage = -1;

    if (currentPage < pageCount && direction === "next") {
      for (let i = currentPage + 1; i < pageCount + 1; i++) {
        if (pageProfiles[i]?.hasItems) {
          return i;
        }
      }
    } else if (currentPage > 0 && direction === "previous") {
      for (let i = currentPage - 1; i >= 0; i--) {
        if (pageProfiles[i]?.hasItems) {
          return i;
        }
      }
    }
    return targetPage;
  };

  const findNextPageOfIntrest = (direction: string) => {
    const targetPage = scanNextPageOfInterest(direction);

    if (direction === "next") {
      if (targetPage !== -1 && currentPage < pageCount) {
        setCurrentPage(targetPage);
        scrollToPage(targetPage);
      }
    } else if (direction === "previous") {
      if (targetPage !== -1 && currentPage > -1) {
        setCurrentPage(targetPage);
        scrollToPage(targetPage);
      }
    } else {
      // Invalid direction.  Only 'next' or 'previous' are allowed.
    }
  };

  const scrollToPage = useCallback(
    (page: number) => {
      if (page === 1 && thumbnailListRef && thumbnailListRef.current) {
        thumbnailListRef.current.scrollTop = 0;
      } else if (
        page > 1 &&
        page <= pageCount &&
        elementRefs.current[page - 1]
      ) {
        elementRefs.current[page - 1].scrollIntoView({
          behavior: "smooth",
          block: "nearest",
        });
      } else {
      }
    },
    [pageCount],
  );

  useEffect(() => {
    if (thumbnailListRef.current) {
      setTimeout(() => {
        scrollToPage(currentPage);
      }, 500);
    }
  }, [currentPage, scrollToPage, annotationChangeFlag]);

  return (
    <div
      id="thumbnail-container"
      style={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <div
        id="thumbnail-menubar"
        style={{
          background: panelColor,
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "center",
          gap: "0.5rem",
          height: "40px",
          padding: "0.5rem",
          color: "#FFFFFF",
          backgroundColor: "#10222F",
        }}
      >
        <Tooltip
          label="Select previous page of interest"
          aria-label="A tooltip"
        >
          <IconButton
            variant="link"
            aria-label="Previous Page"
            onClick={() => {
              findNextPageOfIntrest("previous");
            }}
            isDisabled={currentPage === 1}
            style={{
              color: "white",
              transform: "scale(2)",
            }}
            data-pendoid="previous-page"
          >
            <Icon as={ChevronUpIcon} />
          </IconButton>
        </Tooltip>

        <Tooltip label="Select next page of interest" aria-label="A tooltip">
          <IconButton
            variant="link"
            aria-label="Next Page"
            onClick={() => {
              findNextPageOfIntrest("next");
            }}
            isDisabled={currentPage === pageCount}
            style={{
              color: "white",
              transform: "scale(2)",
            }}
            data-pendoid="next-page"
          >
            <Icon as={ChevronDownIcon} />
          </IconButton>
        </Tooltip>
      </div>

      <div
        id="thumbnail-list"
        style={{
          background: bgColor,
          overflowY: "auto",
          height: "100%",
          // maxHeight: "100vh",
          // overflow: "scroll",
        }}
        ref={thumbnailListRef}
      >
        {Array.from({ length: pageCount }, (_, i) => i).map(
          (page) => {
            const pageNumber: number = page + 1;
            const pageProfile = pageProfiles[pageNumber];

            return (
              <div
                key={page}
                style={{
                  display: "flex",
                  justifyContent: "center",
                  margin: "0 0 1rem",
                  position: "relative",
                  padding: "1rem",
                  // background:
                  //   page + 1 === currentPage ? "rgba(0, 128, 128, 1)" : "transparent",
                }}
              >
                <a
                  href="#page"
                  onClick={(event) => {
                    event.preventDefault();
                    setCurrentPage(page + 1);
                  }}
                  data-pendoid={`pdf-thumbnail-${pageNumber}`}
                >
                  <div ref={(el) => (elementRefs.current[page] = el)}>
                    <Preview
                      pageNumber={page + 1}
                      renderPreview={renderPreview}
                      highlighted={page + 1 === currentPage}
                    />
                  </div>
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

                {pageProfiles[pageNumber]?.hasItems && (
                  <PageBadge
                    documentId={documentId}
                    page={page}
                    pageProfile={pageProfile}
                    onPageProfileSelection={onPageProfileSelection}
                    pageProfileState={pageProfileState}
                    getPageProfileState={getPageProfileState}
                    data-pendoid={`page-profile-${pageNumber}`}
                  />
                )}

                <div
                  style={{
                    position: "absolute",
                    bottom: "1rem",
                    margin: "4px auto",
                    width: "2rem",
                    textAlign: "center",
                    backgroundColor: "rgba(0, 0, 0, 0.5)",
                    color: "white",
                    padding: "0",
                    fontSize: "1.25rem",
                  }}
                >
                  {page + 1}
                </div>
              </div>
            ); //End of JSX
          }, //End of Array
        )}
      </div>
    </div>
  );
};

type PreviewProps = {
  pageNumber: number;
  renderPreview: (page: number, ref: HTMLCanvasElement) => void;
  highlighted: boolean;
};

// Using memo to prevent duplicate rendering of previews (pdf.js does not like it when multiple render calls are made on the same canvas)
const Preview: FC<PreviewProps> = memo(
  ({ pageNumber, renderPreview, highlighted = false }) => {
    const [pageHighlightColor] = useToken(
      // the key within the theme, in this case `theme.colors`
      "colors",
      // the subkey(s), resolving to `theme.colors.red.100`
      ["elm.700"],
      // a single fallback or fallback array matching the length of the previous arg
    );

    // Get current div height

    return (
      <canvas
        ref={(ref) => {
          ref && renderPreview(pageNumber, ref);
        }}
        style={{
          width: "100%",
          borderTop: "1px solid rgba(0, 0, 0, 0.5)",
          borderBottom: "1px solid rgba(0, 0, 0, 0.5)",
          boxShadow: highlighted ? `0 0 16px ${pageHighlightColor}` : "none",
        }}
      />
    );
  },
);
