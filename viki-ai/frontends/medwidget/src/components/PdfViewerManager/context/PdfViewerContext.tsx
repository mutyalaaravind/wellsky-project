import { createContext, ReactNode, useContext, useMemo } from "react";
import { PdfViewerContextType } from "types";

// import { PdfViewerContextType } from "./types";

export const PdfViewerContext = createContext<PdfViewerContextType>({
  storeId: null,
  patientId: null,
  updatePageProfileState: undefined,
});

export const PdfViewerContextProvider = ({
  children,
  storeId,
  patientId,
  updatePageProfileState,
}: {
  children?: ReactNode;
  storeId: string;
  patientId: string;
  updatePageProfileState: PdfViewerContextType["updatePageProfileState"];
}) => {
  const value: PdfViewerContextType = useMemo(() => {
    return {
      storeId,
      patientId,
      updatePageProfileState,
    };
  }, [storeId, patientId, updatePageProfileState]);

  return (
    <PdfViewerContext.Provider value={value}>
      {children}
    </PdfViewerContext.Provider>
  );
};

export const usePdfViewerContext = () => {
  return useContext(PdfViewerContext);
};
