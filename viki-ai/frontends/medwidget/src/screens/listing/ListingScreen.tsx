import { TwoHalves } from "components/TwoHalves";
import { DocumentFile, Env } from "types";

import { Documents } from "./Documents";
import { MedicationsV2 } from "screens/review/MedicationsV2";
import { Block } from "components/Block";
import { useMedicationsApi } from "hooks/useMedicationsApi";
import { useAuth } from "hooks/useAuth";
import { useEffect } from "react";

export const ListingScreen = ({
  env,
  onReviewPressed,
  onSubmit,
  documentsInReview,
  "data-pendo": dataPendo,
}: {
  env: Env;
  onReviewPressed: (selectedDocs: DocumentFile[]) => void;
  onSubmit: () => void;
  documentsInReview: DocumentFile[];
  "data-pendo"?: string;
}) => {
  const { patientId } = useAuth();
  const { refreshMedicationsV2 } = useMedicationsApi({
    apiRoot: env?.API_URL,
    patientId,
    documentsInReview,
  });

  useEffect(() => {
    refreshMedicationsV2(true);
  }, [refreshMedicationsV2]);

  return (
    <TwoHalves data-pendo={dataPendo}>
      <Documents env={env as any} onReviewPressed={onReviewPressed} data-pendo="widget-documents-section" />
      <Block data-pendo="widget-medications-block">
        <MedicationsV2
          env={env}
          onSubmit={onSubmit}
          documentsInReview={documentsInReview}
          onEvidenceRequested={() => {}}
          currentDocument={null}
          pageProfiles={{}}
          hideInfoText
          allowModification={false}
          data-pendo="widget-medications-section"
        />
      </Block>
    </TwoHalves>
  );
};
