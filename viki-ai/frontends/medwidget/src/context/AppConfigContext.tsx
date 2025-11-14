import React, { useEffect, useMemo } from "react";
import { Configuration, Env } from "types";
import useConfigurationApi from "hooks/useConfiguration";
import { Spinner } from "@chakra-ui/react";
import useEnvJson from "hooks/useEnvJson";

export type AppConfigContextType = Configuration;

export const AppConfigContext = React.createContext<AppConfigContextType>({
  extractAllergies: false,
  extractImmunizations: false,
  extractConditions: false,
  extractionPersistedToMedicationProfile: false,
  usePagination: true,
  enableOnDemandExternalFilesDownload: false,
  uiControlUploadEnable: false,
  uiNonstandardDoseEnable: false,
  uiHideMedicationTab: false,
  uiDocumentActionExtractEnable: false,
  uiDocumentActionUpsertGoldenDatasetTestcaseEnable: false,
  useAsyncDocumentStatus: false,
  useClientSideFiltering: false,
  orchestrationEngineVersion: "v3",
  validationRules: null,
  ocrTriggerConfig: {
    enabled: false,
    touchPoints: {
      bubbleClick: false,
      evidenceLinkClick: false,
      pageClick: false,
    },
  },
  uiHostLinkedDeleteEnable: true,
  uiLongstandingEnable: true,
  uiClassificationEnable: true,
});

export const AppConfigProvider: React.FC<{
  children: React.ReactNode;
}> = ({ children }) => {
  const { getConfig, config } = useConfigurationApi();
  const env = useEnvJson<Env>();

  useEffect(() => {
    if (env) {
      getConfig(env);
      console.log("configprovider called");
    } else {
      console.log("configprovider:env not found");
    }
  }, [env, getConfig]);

  const memoizedConfigData = useMemo(() => config, [config]);

  return memoizedConfigData ? (
    <AppConfigContext.Provider value={memoizedConfigData}>
      {children}
    </AppConfigContext.Provider>
  ) : (
    <Spinner />
  );
};

export const useConfigData = () => {
  return React.useContext(AppConfigContext);
};
