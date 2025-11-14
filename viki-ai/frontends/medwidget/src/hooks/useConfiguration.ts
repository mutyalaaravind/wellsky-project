import { useCallback, useContext } from "react";
import { Env } from "types";
import { AuthContext } from "context/AuthContext";
import { usePatientProfileStore } from "store/patientProfileStore";

const useConfigurationApi = () => {
  //const env = useEnvJson<Env>();
  const authContext = useContext(AuthContext);
  const token = authContext.token;
  const oktaToken = authContext.oktaToken;

  const { config, setConfig } = usePatientProfileStore();

  // Fetch allergies from an API or any other data source
  const getConfig = useCallback(
    async (env: Env) => {
      if (!env?.API_URL) {
        console.log("getConfig: API_URL not found in env");
        return;
      }
      try {
        const response = await fetch(`${env?.API_URL}/api/v2/configuration`, {
          headers: {
            Authorization: "Bearer " + token,
            "Okta-Token": oktaToken,
          },
        });
        const data = await response.json();

        setConfig({
          extractAllergies: data.extract_allergies,
          extractImmunizations: data.extract_immunizations,
          extractConditions: data.extract_conditions,
          extractionPersistedToMedicationProfile:
            data.extraction_persisted_to_medication_profile,
          usePagination: data.use_pagination,
          uiControlUploadEnable: data.ui_control_upload_enable,
          uiNonstandardDoseEnable: data.ui_nonstandard_dose_enable,
          uiHostLinkedDeleteEnable: data.ui_host_linked_delete_enable ?? true,
          uiLongstandingEnable: data.ui_longstanding_enable ?? true,
          uiClassificationEnable: data.ui_classification_enable ?? true,
          enableOnDemandExternalFilesDownload:
            data.on_demand_external_files_config?.enabled || false,
          uiHideMedicationTab: data.ui_hide_medication_tab,
          useAsyncDocumentStatus: data.use_async_document_status,
          useClientSideFiltering: data.use_client_side_filtering,
          orchestrationEngineVersion: data.orchestration_engine_version,
          uiDocumentActionExtractEnable: data.ui_document_action_extract_enable,
          uiDocumentActionUpsertGoldenDatasetTestcaseEnable:
            data.ui_document_action_upsert_golden_dataset_test_enable,
          validationRules: data.validation_rules || null,
          ocrTriggerConfig: {
            enabled: data.ocr_trigger_config?.enabled || false,
            touchPoints: {
              bubbleClick:
                data.ocr_trigger_config?.touch_points?.bubble_click || false,
              evidenceLinkClick:
                data.ocr_trigger_config?.touch_points?.evidence_link_click ||
                false,
              pageClick:
                data.ocr_trigger_config?.touch_points?.page_click || false,
            },
          },
        });
      } catch (error) {
        console.error("Error fetching configuration:", error);
      } finally {
      }
    },
    [oktaToken, setConfig, token],
  );

  return {
    getConfig,
    config,
  };
};

export default useConfigurationApi;
