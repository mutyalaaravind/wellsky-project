import { DocumentFile } from "types";

export type pdfViewerInstanceType = {
  totalPages: number;
  currentPage: number;
  gotoPage: (page: number) => void;
  isLoading?: boolean;
};

export type PdfViewerProps = {
  defaultCurrentPage?: number;
  document: DocumentFile;
  blob: Blob;
};
