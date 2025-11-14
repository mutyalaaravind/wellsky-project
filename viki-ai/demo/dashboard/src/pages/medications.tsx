import { useEffect, useState } from "react";
import { PortalHeader } from "../components/portal-header";
// import { useRouter } from 'next/router'
import { Env } from "../types";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Box, Heading } from "@chakra-ui/react";
import useEnvJson from "../hooks/useEnvJson";
import { BreadCrumType } from "../components/bread-crum";
import { MedWidgetBlock } from "../components/paperglass";
import { useTokenApi } from "../hooks/useTokenApi";
import { usePatientsApi } from "../hooks/usePatientsApi";

const MedicationsPage = () => {
  //const router = useRouter()
  const [patient, setPatient] = useState({});
  const [searchParams, setSearchParams] = useSearchParams();
  const router = useNavigate();
  const { getToken, tokens } = useTokenApi();
  const { getPatient } = usePatientsApi();
  const currentUser = { username: "john.doe" };
  const env: Env | null = useEnvJson();
  const patientId = searchParams.get("patientId");
  const breadCrumbs: Array<BreadCrumType> = [
    { moduleName: "Patients", linkUrl: "/patients" },
    { moduleName: `getPatientName(${patientId})`, linkUrl: "/" },
    {
      moduleName: "Assessment",
      linkUrl: `/assessments?patientId=${patientId}`,
    },
  ];

  const getPatientFromLocal = (patientId: string) => {
    if (patientId && localStorage.getItem("patientId")) {
      return JSON.parse(localStorage.getItem("patientId") || "{}");
    }
  };

  useEffect(() => {
    if (patientId && env) {
      getToken(env, patientId);
    }
  }, [patientId, env]);

  return (
    <Box style={{ width: "100%" }}>
      <PortalHeader breadCrums={breadCrumbs} />
      {env && patientId && tokens && (
        <Box paddingLeft={5}>
          <MedWidgetBlock
            tokens={tokens}
            widgetHost={env?.MED_WIDGET_HOST}
            identifier={patientId}
            patient={getPatient(env, patientId)}
          />
        </Box>
      )}
      {!env && <div>Loading...</div>}
      <Heading as="h1" size="lg" paddingLeft={5} paddingTop={5}>
        Medications
      </Heading>
      <Box paddingLeft={5} paddingTop={5}>
        Please click icon on the right
      </Box>
      {/* <img src={medicationsDummyPage} alt="medication profile" /> */}
    </Box>
  );
};

export default MedicationsPage;
