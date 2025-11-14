import { PageProfile } from "store/storeTypes";
import {
  DocumentFile,
  Env,
  SetStateLikeAction,
  SetStateActionCallBack,
  Coordinate,
} from "types";

export type PdfStoreState = {
  storeId: string;
  documents: DocumentFile[];
  env: any | Env;
  allPageProfiles: Map<
    string,
    Record<string | number, Record<number, PageProfile>>
  >;
  loading: boolean;
  currentDocumentId: string | null;
  documentInfo: Map<
    string,
    {
      doc: DocumentFile;
      currentPage: number;
      totalPages: number;
      pages: Map<
        number,
        {
          annotations: Coordinate[]; // Annotation coordinates
        }
      >;
    }
  >;
  blob: Map<string, Blob>;
  index: number;
  extractionType: string;

  setStoreId: (id: SetStateLikeAction<PdfStoreState["storeId"]>) => void;
  setDocuments: SetStateActionCallBack<PdfStoreState["documents"]>;
  setEnv: SetStateActionCallBack<PdfStoreState["env"]>;
  setAllPageProfiles: SetStateActionCallBack<PdfStoreState["allPageProfiles"]>;

  addAnnotation: (
    documentId: string,
    pageNumber: number,
    coordinates: Coordinate[],
  ) => void;

  removeAnnotation: (
    documentId: string,
    pageNumber: number,
    clearAll?: boolean,
  ) => void;

  updateDocumentInfo: (
    documentId: string,
    currentPage: number,
    totalPages?: number,
  ) => void;

  setPdfUrlForDocument: (documentId: string, url: string) => void;
  setBlob: (documentId: string, blob: Blob) => void;
  setIndex: SetStateActionCallBack<PdfStoreState["index"]>;
  setExtractionType: SetStateActionCallBack<PdfStoreState["extractionType"]>;
  destroyStore: () => void;
  resetStore: () => void;
};
