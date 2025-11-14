import { useCallback, useEffect, useState } from "react";
import { Env, Patient } from "../types";
import { Box, Button, ChakraProvider, Input, Modal } from "@chakra-ui/react";
import { useNavigate } from "react-router-dom";
import { createColumnHelper } from "@tanstack/react-table";
import { DataTable } from "./dataTable";
import { usePatientsApi } from "../hooks/usePatientsApi";
import useEnvJson from "../hooks/useEnvJson";
import { ModalComponent } from "./modal";
import { MedWidgetBlock } from "./paperglass";



const setSelectedPatient = (patients: Array<Patient>, id: string) => {
    const selectedPatient = patients.find((patient: Patient) => patient.id === id);
    if (selectedPatient) {
        localStorage.setItem("patientId", JSON.stringify(selectedPatient));
    }
}

const CreatePatient = (props: { onPatientChange: (patient: Patient) => void }) => {
    const [patient, setPatient] = useState<Patient>({ firstName: "", lastName: "", dob: "", updatedAt: "", id: "", tenantId: "", appId: "" });

    return <>
        <Box padding={2}>
            <Input placeholder="First Name" onChange={(e) => setPatient({ ...patient, firstName: e.target.value })} />
        </Box>
        <Box padding={2}>
            <Input placeholder="Last Name" onChange={(e) => setPatient({ ...patient, lastName: e.target.value })} />
        </Box>
        <Box padding={2}>
            <Input placeholder="Date of Birth (mm/dd/yyyy)" onChange={(e) => setPatient({ ...patient, dob: e.target.value })} />
        </Box>
        <Box padding={2}>
            <Button onClick={() => props.onPatientChange(patient)}>Create New Patient</Button>
        </Box>
    </>
}

export const PatientsList = () => {
    const router = useNavigate();
    const env: Env | null = useEnvJson();
    const { patients, createPatient, getPatients } = usePatientsApi();
    const [patientId, setPatientId] = useState<string>("");
    //const [patients, setPatients] = useState<Patient[]>(dummyPatients);

    const onPatientChange = useCallback((patient: Patient) => { if (env) { createPatient(env, patient); getPatients(env); } }, [env]);

    const columnHelper = createColumnHelper<Patient>();

    const columns = [
        columnHelper.accessor("firstName", {
            cell: (info) => info.getValue(),
            header: "First Name"
        }),
        columnHelper.accessor("lastName", {
            cell: (info) => info.getValue(),
            header: "Last Name"
        }),
        columnHelper.accessor("dob", {
            cell: (info) => info.getValue(),
            header: "Date of Birth"
        }),
        columnHelper.accessor("updatedAt", {
            cell: (info) => info.getValue(),
            header: "Last Modified"
        }),
        columnHelper.accessor("id", {
            cell: (info) => <>
                <Button onClick={() => { setSelectedPatient(patients, info.getValue()); router(`/assessments?patientId=${info.getValue()}`) }}>Assessments</Button>
                &nbsp;
                <Button onClick={() => { setSelectedPatient(patients, info.getValue()); router(`/documents?patientId=${info.getValue()}`) }}>Documents</Button>
                &nbsp;
                <Button onClick={() => { setSelectedPatient(patients, info.getValue()); setPatientId(info.getValue()); router(`/medications?patientId=${info.getValue()}`) }}>Extract</Button>
                {/* {env && <><MedWidgetBlock widgetHost={env?.MED_WIDGET_HOST} identifier={info.getValue()} /></>} */}
                {/* <Button onClick={()=>{setSelectedPatient(info.getValue());router(`/intake?patientId=${info.getValue()}`)}}>Intake</Button> */}
            </>,
            header: ""
        })
    ];

    useEffect(() => {
        if (env) {
            getPatients(env);
        }

    }, [env])

    useEffect(() => {
        console.log("setting patients")
        localStorage.setItem("patients", JSON.stringify(patients));
    }, [patients])

    return (
        <>
            {/* <Box padding={5} float={"right"}>
                <Button>Add New Patient</Button>
            </Box> */}
            <Box>
                {env && patientId && <><MedWidgetBlock widgetHost={env?.MED_WIDGET_HOST} identifier={patientId} /></>}
            </Box>
            <Box padding={5} float={"right"}>
                <ModalComponent children={<><CreatePatient onPatientChange={onPatientChange} /></>} openModalText="Create New Patient" modalTitle={"New Patient"} />
            </Box>
            <Box paddingLeft={5} paddingRight={5}>
                <DataTable columns={columns} data={patients} />
            </Box>
        </>
    )
}
