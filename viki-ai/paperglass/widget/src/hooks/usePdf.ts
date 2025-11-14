import { useEffect, useState, useCallback } from 'react';
import { GlobalWorkerOptions, getDocument, PDFDocumentProxy, PDFPageProxy } from "pdfjs-dist";
import { RenderParameters } from 'pdfjs-dist/types/src/display/api';
import * as pdfjsLib from 'pdfjs-dist/webpack'

export const usePdf = (canvasRef: React.RefObject<HTMLCanvasElement>, url: string = '', defaultPage: number = 1) => {
  GlobalWorkerOptions.workerSrc = pdfjsLib;
  const [pdfRef, setPdfRef] = useState<PDFDocumentProxy>();
  const [currentPage, setCurrentPage] = useState(1);
  const [isRendering, setIsRendering] = useState(false);
  const [pageCount, setPageCount] = useState(0);
  const [pageWidth, setPageWidth] = useState(0);
  const [pageHeight, setPageHeight] = useState(0);

  useEffect(() => {
    setCurrentPage(defaultPage);
  }, [defaultPage]);

  const renderPage = useCallback((pageNum: any, pdf = pdfRef) => {
    // Called when pdfRef is set
    pdf && pdf.getPage(pageNum).then(function(page: PDFPageProxy) {
      if (!canvasRef.current) {
        console.error('Canvas ref not ready');
        return;
      } else {
        console.log('Canvas ref ready');
      }
      const viewport = page.getViewport({ scale: 1 });
      const canvas = canvasRef.current;
      console.log("viewport",viewport);
      canvas.height = viewport.height;
      canvas.width = viewport.width;
      setPageWidth(viewport.width);
      setPageHeight(viewport.height);
      const ctx = canvas.getContext('2d')
      if (ctx === null) {
        console.error('Failed to get canvas context');
        return;
      }
      const renderContext: RenderParameters = {
        canvasContext: ctx,
        viewport: viewport
      };
      setIsRendering(true);
      page.render(renderContext).promise.then(() => {
        console.log('Page rendered');
        setIsRendering(false);
      });
    });
  }, [pdfRef, canvasRef]);

  const renderPreview = useCallback((pageNum: any, targetCanvas: HTMLCanvasElement, pdf = pdfRef) => {
    pdf && pdf.getPage(pageNum).then(function(page: PDFPageProxy) {
      const viewport = page.getViewport({ scale: 0.5 });
      targetCanvas.height = viewport.height;
      targetCanvas.width = viewport.width;
      const ctx = targetCanvas.getContext('2d')
      if (ctx === null) {
        console.error('Failed to get canvas context');
        return;
      }
      const renderContext: RenderParameters = {
        canvasContext: ctx,
        viewport: viewport
      };
      page.render(renderContext).promise.then(() => {
        console.log('Preview rendered');
      });
    });
  }, [pdfRef]);

  const prevPage = useCallback(() => {
    if (pdfRef && currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  }, [pdfRef, currentPage]);

  const nextPage = useCallback(() => {
    if (pdfRef && currentPage < pdfRef.numPages) {
      setCurrentPage(currentPage + 1);
    }
  }, [pdfRef, currentPage]);

  useEffect(() => {
    renderPage(currentPage, pdfRef);
  }, [pdfRef, currentPage, renderPage]);

  useEffect(() => {
    if (url !== '') {
      const loadingTask = getDocument(url);
      loadingTask.promise.then((loadedPdf: PDFDocumentProxy) => {
        setPdfRef(loadedPdf);
        setPageCount(loadedPdf.numPages);
      }, function(reason: any) {
        console.error('Failed to load PDF:', reason);
      });
    }
  }, [url]);

  return {
    currentPage,
    prevPage,
    nextPage,
    setCurrentPage,
    isRendering,
    pageCount,
    pageWidth,
    pageHeight,
    renderPreview,
  };
}
