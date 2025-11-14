import { usePdfViewerContext } from "../context/PdfViewerContext";
import { PdfStoreState } from "./storeTypes";
import { create } from "zustand";
import { devtools } from "zustand/middleware";
import { immer } from "zustand/middleware/immer";
import { enableMapSet } from "immer";
import InstanceManager from "utils/InstanceManager";
import { Coordinate, DocumentFile, SetStateLikeAction } from "types";
import { genericSetState, genericSetStateV2 } from "utils/helpers";
import { useMemo } from "react";

enableMapSet();

const defaultState: Pick<
  PdfStoreState,
  | "storeId"
  | "documents"
  | "env"
  | "allPageProfiles"
  | "loading"
  | "currentDocumentId"
  | "documentInfo"
  | "blob"
  | "index"
  | "extractionType"
> = {
  storeId: "",
  documents: [] as PdfStoreState["documents"],
  env: {} as PdfStoreState["env"],
  allPageProfiles: new Map() as PdfStoreState["allPageProfiles"],
  loading: false,
  currentDocumentId: null,
  documentInfo: new Map() as PdfStoreState["documentInfo"],
  blob: new Map() as PdfStoreState["blob"],
  index: 0,
  extractionType: "medication",
};

const storeCreator = (storeId: string) =>
  create<
    PdfStoreState,
    [["zustand/devtools", never], ["zustand/immer", never]]
  >(
    devtools(
      immer(
        (set, get): PdfStoreState => ({
          ...defaultState,

          setStoreId: genericSetState<
            SetStateLikeAction<PdfStoreState["storeId"]>,
            PdfStoreState
          >("storeId", set, get),

          setDocuments: genericSetStateV2<PdfStoreState, "documents">(
            "documents",
            set,
            get,
          ),

          setPdfUrlForDocument: (documentId: string, url: string) => {
            set((state) => {
              const doc = state.documents.find((d) => d.id === documentId);
              if (doc) {
                doc.pdfUrl = url;
              }
            });
          },

          setEnv: genericSetState<
            SetStateLikeAction<PdfStoreState["env"]>,
            PdfStoreState
          >("env", set, get),

          setAllPageProfiles: genericSetState<
            SetStateLikeAction<PdfStoreState["allPageProfiles"]>,
            PdfStoreState
          >("allPageProfiles", set, get),

          addAnnotation: (documentId, pageNumber, coordinates) => {
            set((state) => {
              let docInfo = state.documentInfo.get(documentId);

              const index = state.documents.findIndex(
                (d) => d.id === documentId,
              );

              if (index === -1) {
                return;
              }

              state.index = index;

              if (!docInfo) {
                state.documentInfo.set(documentId, {
                  doc: state.documents.find(
                    (d) => d.id === documentId,
                  ) as DocumentFile,
                  currentPage: pageNumber || 1,
                  totalPages: 0,
                  pages: new Map<number, { annotations: Coordinate[] }>([
                    [pageNumber, { annotations: coordinates }],
                  ]),
                });

                return;
              }

              if (docInfo) {
                docInfo.currentPage = pageNumber;
                docInfo.pages.set(pageNumber, { annotations: coordinates });
              }
            });
          },

          removeAnnotation: (documentId, pageNumber, clearAll = false) => {
            set((state) => {
              const docInfo = state.documentInfo.get(documentId);
              if (docInfo) {
                if (clearAll) {
                  docInfo.pages.clear();
                } else {
                  docInfo.pages.set(pageNumber, {
                    annotations: [],
                  });
                }
              }
            });
          },

          updateDocumentInfo: (documentId, currentPage, totalPages) => {
            set((state) => {
              const doc = state.documents.find(
                (d) => d.id === documentId,
              ) as DocumentFile;

              const existingDocInfo = state.documentInfo.get(documentId);

              state.documentInfo.set(documentId, {
                doc,
                currentPage,
                totalPages: totalPages || existingDocInfo?.totalPages || 0,
                pages:
                  existingDocInfo?.pages ||
                  new Map<number, { annotations: Coordinate[] }>(),
              });
            });
          },

          setBlob: (documentId, blob) => {
            set((state) => {
              state.blob.set(documentId, blob);
            });
          },

          setIndex: genericSetStateV2<PdfStoreState, "index">(
            "index",
            set,
            get,
          ),

          setExtractionType: genericSetStateV2<PdfStoreState, "extractionType">(
            "extractionType",
            set,
            get,
          ),

          resetStore: () => {
            set((state) => {
              for (const k of Object.keys(defaultState) as Array<
                keyof typeof defaultState
              >) {
                (state[k] as PdfStoreState[keyof PdfStoreState]) =
                  defaultState[k];
              }
            });
          },

          destroyStore: () => {
            storeManagerInstance.removeInstance(storeId);
          },
        }),
      ),
    ),
  );

const storeManagerInstance = new InstanceManager<
  ReturnType<typeof storeCreator>
>();

function usePdfManagerStore(storeId: string | null | undefined): PdfStoreState;
function usePdfManagerStore<T = any>(
  storeId: string | null | undefined,
  cb?: (state: PdfStoreState) => T,
): T;

function usePdfManagerStore(
  storeId: string | null | undefined,
  cb?: (state: PdfStoreState) => unknown,
) {
  if (!storeId) {
    throw new Error(
      "Error binding store. Can not initialize out side of PdfViewerProvider",
    );
  }

  const useStore = storeManagerInstance.getOrCreate(storeId + "pdfStore", () =>
    storeCreator(storeId),
  );

  if (!useStore) {
    throw new Error("Error binding store");
  }

  const callBack = useMemo(() => cb, [cb]);

  const store = useStore();

  return callBack ? callBack(store) : store;
}

export function usePdfWidgetStore(): PdfStoreState;
export function usePdfWidgetStore<T = any>(cb: (state: PdfStoreState) => T): T;

export function usePdfWidgetStore(cb?: (state: PdfStoreState) => unknown) {
  const { storeId } = usePdfViewerContext();

  if (!storeId) {
    throw new Error(
      "Error binding store. Can not initialize out side of PdfViewerProvider",
    );
  }

  return usePdfManagerStore(storeId, cb);
}
