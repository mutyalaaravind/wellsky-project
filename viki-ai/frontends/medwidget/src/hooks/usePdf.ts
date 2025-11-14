import { useEffect, useState, useCallback, useRef } from "react";
import {
  GlobalWorkerOptions,
  getDocument,
  PDFDocumentProxy,
  PDFPageProxy,
} from "pdfjs-dist";
import { RenderParameters } from "pdfjs-dist/types/src/display/api";

const localCache = new Map<string, any>();

export const usePdf = (
  canvasRef: React.RefObject<HTMLCanvasElement>,
  url: string = "",
  defaultPage: number = 1,
) => {
  GlobalWorkerOptions.workerSrc =
    "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.0.379/pdf.worker.min.mjs"; // TODO: Version is hard-coded!
  const [pdf, setPdf] = useState<PDFDocumentProxy>();
  const [currentPage, setCurrentPage] = useState(defaultPage);
  const [pageCount, setPageCount] = useState(0);
  const [pageWidth, setPageWidth] = useState(0);
  const [pageHeight, setPageHeight] = useState(0);
  const [zoom, setZoom] = useState<number>(1.0);
  const [rotation, setRotation] = useState<number>(0);
  const renderQueueRef = useRef<Promise<void>>(Promise.resolve());

  useEffect(() => {
    setCurrentPage(defaultPage);
  }, [defaultPage]);

  const renderPreview = useCallback(
    (pageNum: any, targetCanvas: HTMLCanvasElement) => {
      pdf &&
        pdf.getPage(pageNum).then(function (page: PDFPageProxy) {
          const viewport = page.getViewport({ scale: 0.5 });
          targetCanvas.height = viewport.height;
          targetCanvas.width = viewport.width;
          const ctx = targetCanvas.getContext("2d");
          if (ctx === null) {
            console.error("Failed to get canvas context");
            return;
          }
          const renderContext: RenderParameters = {
            canvasContext: ctx,
            viewport: viewport,
          };
          // renderQueueRef.current = renderQueueRef.current.then(() => {
          // return
          page.render(renderContext).promise.then(() => {
            console.warn("Preview rendered");
          });
          // });
        });
    },
    [pdf],
  );

  const prevPage = useCallback(() => {
    if (pdf && currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  }, [pdf, currentPage]);

  const nextPage = useCallback(() => {
    if (pdf && currentPage < pdf.numPages) {
      setCurrentPage(currentPage + 1);
    }
  }, [pdf, currentPage]);

  useEffect(() => {
    // Called when pdf is set
    pdf &&
      pdf.getPage(currentPage).then(function (page: PDFPageProxy) {
        if (!canvasRef.current) {
          console.error("Canvas ref not ready");
          return;
        } else {
        }
        const viewport = page.getViewport({ scale: zoom, rotation });
        const canvas = canvasRef.current;
        canvas.height = viewport.height;
        canvas.width = viewport.width;
        setPageWidth(viewport.width);
        setPageHeight(viewport.height);
        const ctx = canvas.getContext("2d");
        if (ctx === null) {
          console.error("Failed to get canvas context");
          return;
        }
        const renderContext: RenderParameters = {
          canvasContext: ctx,
          viewport: viewport,
        };
        renderQueueRef.current = renderQueueRef.current.then(() => {
          console.log("Rendering page");
          return page.render(renderContext).promise.then(() => {
            console.log("Page rendered");
          });
        });
      });
  }, [pdf, currentPage, canvasRef, zoom, rotation]);

  useEffect(() => {
    if (url !== "") {
      if (localCache.has(url)) {
        const loadedPdf: PDFDocumentProxy = localCache.get(url);
        setPdf(loadedPdf);
        setPageCount(loadedPdf.numPages);
        return;
      }

      const loadingTask = getDocument(url);
      loadingTask.promise.then(
        (loadedPdf: PDFDocumentProxy) => {
          setPdf(loadedPdf);
          setPageCount(loadedPdf.numPages);
          localCache.set(url, loadedPdf);
        },
        function (reason: any) {
          console.error("Failed to load PDF:", reason);
        },
      );
    }
  }, [url]);

  return {
    currentPage,
    prevPage,
    nextPage,
    setCurrentPage,
    zoom,
    setZoom,
    rotation,
    setRotation,
    pageCount,
    pageWidth,
    pageHeight,
    renderPreview,
  };
};
