import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { DocumentView } from "./DocumentView";
import { Medications } from "./Medications";
import { useBack } from "hooks/useBack";
import { Env } from "types";
import { useMedicationsApi } from "hooks/useMedicationsApi";
import { Flex, Switch, Tab, TabList, Tabs } from "@chakra-ui/react";
import { MedicationsV2 } from "./MedicationsV2";
import { ContextDocumentItemFilter } from "tableOfContentsTypes";
import Allergies from "./Allergies";
import Immunizations from "./Immunizations";
import Conditions from "./Conditions";
import { useAuth } from "hooks/useAuth";
import { EvidenceInfo, DocumentFile } from "types";
import ExpandableBox from "components/ExpandableBox";
import ExpandableContainer from "components/ExpandableContainer";
import { usePatientProfileStore } from "store/patientProfileStore";
import PdfViewerProvider, {
  InstanceProvider,
} from "components/PdfViewerManager/context/PdfViewerProvider";
import DocumentsViewer from "components/PdfViewerManager/DocumentsViewer";
import { isUsingPdfViewerWidget } from "utils/constants";
import { useConfigData } from "context/AppConfigContext";

export const ReviewScreen = ({
  env,
  documentsInReview,
  onClose,
  onSubmit,
}: {
  env: Env;
  documentsInReview: DocumentFile[];
  onClose: () => void;
  onSubmit: () => void;
}) => {
  const { addBackHandler, back } = useBack();

  const documentViewRef = useRef<any>(null);

  const [currentDocument, setCurrentDocument] = useState<DocumentFile | null>(
    null,
  );
  const [newMedicationUI, setNewMedicationUI] = useState(true);
  const [showV2Switch, setShowV2Switch] = useState(false);
  const [pageProfileState, setPageProfileState] = useState<
    Record<string, ContextDocumentItemFilter>
  >({});

  const { patientId } = useAuth();
  const { refreshMedicationsV2, refreshMedicationsV4 } = useMedicationsApi({
    apiRoot: env?.API_URL,
    patientId,
    documentsInReview,
  });
  const config = useConfigData();

  const { allPageProfiles, updatePageProfileState } = usePatientProfileStore();

  const onEvidenceRequested = useCallback((evidenceInfo: EvidenceInfo) => {
    try {
      documentViewRef.current?.showDocumentPage(
        evidenceInfo.documentId,
        evidenceInfo.pageNumber,
        evidenceInfo.annotations && evidenceInfo.annotations.length > 0
          ? [evidenceInfo.annotations[0]]
          : [],
      );
    } catch (error) {
      console.error("Failed to show evidence:", error);
    }
  }, []);

  const onSwitchChange = useCallback((e: any) => {
    setNewMedicationUI(e.target.checked);
  }, []);

  const onPageProfileStateChange = useCallback(
    (pageProfileState: Record<string, ContextDocumentItemFilter>) => {
      setPageProfileState({ ...pageProfileState });
    },
    [],
  );

  const getPageProfileState = useCallback(
    (documentId: string, profileType: string, page: number) => {
      return (
        allPageProfiles?.get(documentId)?.[profileType]?.[page]?.isSelected ||
        false
      );
    },
    [allPageProfiles],
  );

  useEffect(() => {
    if (currentDocument?.id) {
      config?.orchestrationEngineVersion === "v3"
        ? refreshMedicationsV2()
        : refreshMedicationsV4();
    }
  }, [currentDocument?.id, refreshMedicationsV2, config, refreshMedicationsV4]);

  useEffect(() => {
    // addBackHandler(() => onClose());
    return addBackHandler(() => onClose());
  }, [addBackHandler, onClose]);

  useEffect(() => {
    (window as any).toggleV2Switch = () => setShowV2Switch((p) => !p);
    return () => {
      delete (window as any).toggleV2Switch;
    };
  }, []);

  const [tabIndex, setTabIndex] = useState(0);

  const tabIndexMap = useMemo(() => {
    return new Map([[0, "medication"]]);
  }, []);

  if (isUsingPdfViewerWidget) {
    return (
      <PdfViewerProvider
        documents={documentsInReview}
        env={env}
        allPageProfiles={allPageProfiles}
        extractionType={tabIndexMap.get(tabIndex)}
        updatePageProfileState={updatePageProfileState}
      >
        <ExpandableContainer>
          <ExpandableBox id="doc" buttonPlacement="right">
            <DocumentsViewer onDocumentOpened={setCurrentDocument} />
          </ExpandableBox>
          <ExpandableBox id="med" buttonPlacement="left">
            <InstanceProvider>
              {(viewerInstance) => {
                return (
                  <div
                    style={{
                      display: "flex",
                      flex: "1 1 0%",
                      flexDirection: "column",
                      overflow: "hidden",
                    }}
                  >
                    <Tabs
                      size="sm"
                      variant="enclosed"
                      colorScheme="green"
                      index={tabIndex}
                      onChange={(index) => setTabIndex(index)}
                    >
                      <TabList overflow="auto hidden">
                        <Tab
                          style={{
                            display:
                              config && config.uiHideMedicationTab
                                ? "none"
                                : "block",
                          }}
                        >
                          Medication
                        </Tab>
                        <Tab
                          style={{
                            display:
                              config && config.extractAllergies
                                ? "block"
                                : "none",
                          }}
                        >
                          Allergies
                        </Tab>
                        <Tab
                          style={{
                            display:
                              config && config.extractImmunizations
                                ? "block"
                                : "none",
                          }}
                        >
                          Immunizations
                        </Tab>
                        <Tab
                          style={{
                            display:
                              config && config.extractConditions
                                ? "block"
                                : "none",
                          }}
                        >
                          Conditions
                        </Tab>
                      </TabList>
                    </Tabs>
                    {tabIndex === 0 && (
                      <Flex direction="column" flex="1 1 0%">
                        {showV2Switch && (
                          <div style={{ paddingBottom: "5px" }}>
                            <Switch
                              colorScheme="red"
                              size="sm"
                              defaultChecked
                              onChange={onSwitchChange}
                            >
                              {" "}
                              {newMedicationUI ? "V2" : "V1"}{" "}
                            </Switch>
                          </div>
                        )}
                        {newMedicationUI ? (
                          <div
                            style={{
                              display: "flex",
                              flex: "1 1 0px",
                              flexDirection: "column",
                              gap: "1rem",
                              overflowY: "auto",
                            }}
                          >
                            <MedicationsV2
                              env={env}
                              onSubmit={onSubmit}
                              documentsInReview={documentsInReview}
                              onEvidenceRequested={onEvidenceRequested}
                              currentDocument={currentDocument}
                              pageProfiles={pageProfileState}
                              viewerInstance={viewerInstance}
                              isFilteringEnabled={config.useClientSideFiltering}
                            />
                          </div>
                        ) : (
                          <div
                            style={{
                              display: "flex",
                              flex: "1 1 0px",
                              flexDirection: "column",
                              gap: "1rem",
                              overflowY: "auto",
                            }}
                          >
                            <Medications
                              env={env}
                              onSubmit={onSubmit}
                              documentsInReview={documentsInReview}
                              onEvidenceRequested={onEvidenceRequested}
                              currentDocument={currentDocument}
                            />
                          </div>
                        )}
                      </Flex>
                    )}
                    {config && config.extractAllergies && tabIndex === 1 && (
                      <Allergies
                        env={env}
                        documentsInReview={documentsInReview}
                        currentDocument={currentDocument}
                        pageProfiles={pageProfileState}
                        onEvidenceRequested={onEvidenceRequested}
                      />
                    )}
                    {config &&
                      config.extractImmunizations &&
                      tabIndex === 2 && (
                        <Immunizations
                          env={env}
                          documentsInReview={documentsInReview}
                          currentDocument={currentDocument}
                          pageProfiles={pageProfileState}
                          onEvidenceRequested={onEvidenceRequested}
                        />
                      )}
                    {config && config.extractConditions && tabIndex === 3 && (
                      <Conditions
                        env={env}
                        documentsInReview={documentsInReview}
                        currentDocument={currentDocument}
                        pageProfiles={pageProfileState}
                        onEvidenceRequested={onEvidenceRequested}
                      />
                    )}
                  </div>
                );
              }}
            </InstanceProvider>
          </ExpandableBox>
        </ExpandableContainer>
      </PdfViewerProvider>
    );
  }

  return (
    <ExpandableContainer>
      <ExpandableBox id="doc" buttonPlacement="right">
        <DocumentView
          noBoxShadow
          ref={documentViewRef}
          documents={documentsInReview}
          env={env}
          onClose={() => {
            back();
          }}
          onDocumentOpened={setCurrentDocument}
          onPageProfileStateChange={onPageProfileStateChange}
          pageProfileState={pageProfileState}
          setPageProfileState={setPageProfileState}
          getPageProfileState={getPageProfileState}
        />
      </ExpandableBox>
      <ExpandableBox id="med" buttonPlacement="left">
        <div
          style={{
            display: "flex",
            flex: "1 1 0%",
            flexDirection: "column",
            overflow: "hidden",
          }}
        >
          <Tabs
            size="sm"
            variant="enclosed"
            colorScheme="green"
            index={tabIndex}
            onChange={(index) => setTabIndex(index)}
          >
            <TabList overflow="auto hidden">
              <Tab
                style={{
                  display:
                    config && config.uiHideMedicationTab ? "none" : "block",
                }}
              >
                Medication
              </Tab>
              <Tab
                style={{
                  display: config && config.extractAllergies ? "block" : "none",
                }}
              >
                Allergies
              </Tab>
              <Tab
                style={{
                  display:
                    config && config.extractImmunizations ? "block" : "none",
                }}
              >
                Immunizations
              </Tab>
              <Tab
                style={{
                  display:
                    config && config.extractConditions ? "block" : "none",
                }}
              >
                Conditions
              </Tab>
            </TabList>
          </Tabs>
          {tabIndex === 0 && (
            <Flex direction="column" flex="1 1 0%">
              {showV2Switch && (
                <div style={{ paddingBottom: "5px" }}>
                  <Switch
                    colorScheme="red"
                    size="sm"
                    defaultChecked
                    onChange={onSwitchChange}
                  >
                    {" "}
                    {newMedicationUI ? "V2" : "V1"}{" "}
                  </Switch>
                </div>
              )}
              {newMedicationUI ? (
                <div
                  style={{
                    display: "flex",
                    flex: "1 1 0px",
                    flexDirection: "column",
                    gap: "1rem",
                    overflowY: "auto",
                  }}
                >
                  <MedicationsV2
                    env={env}
                    onSubmit={onSubmit}
                    documentsInReview={documentsInReview}
                    onEvidenceRequested={onEvidenceRequested}
                    currentDocument={currentDocument}
                    pageProfiles={pageProfileState}
                    isFilteringEnabled={config.useClientSideFiltering}
                  />
                </div>
              ) : (
                <div
                  style={{
                    display: "flex",
                    flex: "1 1 0px",
                    flexDirection: "column",
                    gap: "1rem",
                    overflowY: "auto",
                  }}
                >
                  <Medications
                    env={env}
                    onSubmit={onSubmit}
                    documentsInReview={documentsInReview}
                    onEvidenceRequested={onEvidenceRequested}
                    currentDocument={currentDocument}
                  />
                </div>
              )}
            </Flex>
          )}
          {config && config.extractAllergies && tabIndex === 1 && (
            <Allergies
              env={env}
              documentsInReview={documentsInReview}
              currentDocument={currentDocument}
              pageProfiles={pageProfileState}
              onEvidenceRequested={onEvidenceRequested}
            />
          )}
          {config && config.extractImmunizations && tabIndex === 2 && (
            <Immunizations
              env={env}
              documentsInReview={documentsInReview}
              currentDocument={currentDocument}
              pageProfiles={pageProfileState}
              onEvidenceRequested={onEvidenceRequested}
            />
          )}
          {config && config.extractConditions && tabIndex === 3 && (
            <Conditions
              env={env}
              documentsInReview={documentsInReview}
              currentDocument={currentDocument}
              pageProfiles={pageProfileState}
              onEvidenceRequested={onEvidenceRequested}
            />
          )}
        </div>
      </ExpandableBox>
    </ExpandableContainer>
  );
};
