import { useConst } from "@chakra-ui/react";
import React, { ReactNode, useEffect, useRef } from "react";
import { PdfViewerContextProvider } from "./PdfViewerContext";

import { DocumentFile, Env } from "types";
import { usePdfWidgetStore } from "../store/pdfViewerStore";
import { useAuth } from "hooks/useAuth";
import ViewerInstance from "../store/ViewerInstance";
import useViewerInstance from "./useViewerInstance";
import { PageProfile } from "store/storeTypes";

type PdfViewerManagerProps = {
  children?: React.ReactNode;
  documents: DocumentFile[];
  env: any | Env;
  allPageProfiles?: Map<
    string,
    Record<string | number, Record<number, PageProfile>>
  >;
  extractionType?: string;
  storeId?: string;
  updatePageProfileState?: (
    documentId: string,
    extractionType: string,
    pageNumber: number,
    pageProfileState: Partial<PageProfile>,
  ) => void;
};

const StoreGenerator = ({
  children,
  documents,
  env,
  allPageProfiles = new Map(),
  storeId,
  extractionType = "medication",
}: PdfViewerManagerProps & {
  storeId: string;
}) => {
  // Generating the store for the first time
  const {
    setDocuments,
    setEnv,
    setAllPageProfiles,
    destroyStore,
    setStoreId,
    setExtractionType,
  } = usePdfWidgetStore();

  useEffect(() => {
    setDocuments(documents);
    setEnv(env);
    setAllPageProfiles(allPageProfiles);
    setStoreId(storeId);
    setExtractionType(extractionType);
    return () => {
      setExtractionType("");
      setDocuments([]);
      setEnv({});
      setAllPageProfiles(new Map());
      setStoreId("");
    };
  }, [
    documents,
    env,
    allPageProfiles,
    setDocuments,
    setEnv,
    setAllPageProfiles,
    setStoreId,
    storeId,
    setExtractionType,
    extractionType,
  ]);

  const isMounted = useRef(false);

  useEffect(() => {
    isMounted.current = true;
  }, []);

  useEffect(() => {
    return () => {
      if (!isMounted.current) return;
      destroyStore();
    };
  }, [destroyStore]);

  return <>{children}</>;
};

const PdfViewerProvider = (props: PdfViewerManagerProps) => {
  const storeId = useConst(() => {
    return props.storeId || crypto.randomUUID();
  });

  const { patientId } = useAuth();

  const { updatePageProfileState } = props;

  return (
    <PdfViewerContextProvider
      storeId={storeId}
      patientId={patientId}
      updatePageProfileState={updatePageProfileState}
    >
      <StoreGenerator
        documents={props.documents}
        env={props.env}
        allPageProfiles={props.allPageProfiles}
        storeId={storeId}
      >
        {props.children}
      </StoreGenerator>
    </PdfViewerContextProvider>
  );
};

export const InstanceProvider = ({
  children,
}: {
  children?: ReactNode | ((viewerInstance: ViewerInstance) => ReactNode);
}) => {
  const viewerInstance = useViewerInstance();

  let enhancedChildren = null;

  if (typeof children !== "function") {
    enhancedChildren = React.Children.map(children, (child) => {
      if (!React.isValidElement<{ viewerInstance: ViewerInstance }>(child)) {
        return child;
      }
      return React.cloneElement(child as React.ReactElement, {
        viewerInstance,
      });
    });
  }

  return (
    <>
      {typeof children === "function"
        ? (children as (viewerInstance: ViewerInstance) => ReactNode)(
            viewerInstance,
          )
        : enhancedChildren}
    </>
  );
};

export default PdfViewerProvider;
