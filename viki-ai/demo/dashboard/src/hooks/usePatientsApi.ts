import { get } from "lodash";
import { Env, Patient } from "../types"
import { useCallback, useState } from "react"

const dummyPatients: Array<Patient> = [
    { id: "c70ee241-126a-719b-4b53-c48e5ae3716c", firstName: "Minnie", lastName: "Mouse", dob: "01/01/1970", updatedAt: "01/01/2021", tenantId: "54321", appId: "007" },
    { id: "c70ee241-126a-719b-4b53-c48e5ae3716d", firstName: "James", lastName: "M", dob: "01/03/1970", updatedAt: "01/01/2021", tenantId: "54321", appId: "007" },
    { id: "c70ee241-126a-719b-4b53-c48e5ae3716e", firstName: "Tom", lastName: "M", dob: "01/05/1970", updatedAt: "01/01/2021", tenantId: "54321", appId: "007" },
    { id: "c70ee241-126a-719b-4b53-c48e5ae3716f", firstName: "Jerry", lastName: "M", dob: "01/09/1970", updatedAt: "01/01/2021", tenantId: "54321", appId: "007" },
    { id: "c70ee241-126a-719b-4b53-c48e5ae3716g", firstName: "Jack", lastName: "Repear", dob: "01/09/1955", updatedAt: "01/01/2022", tenantId: "54321", appId: "007" },
    { id: "c70ee241-126a-719b-4b53-c48e5ae3716i", firstName: "Mary", lastName: "Jane", dob: "01/09/1955", updatedAt: "01/01/2022", tenantId: "54321", appId: "007" },
    { id: "patrick-mouse-id-2", firstName: "Patrick", lastName: "Mouse", dob: "01/09/1955", updatedAt: "01/01/2022", tenantId: "54321", appId: "007" },
    { id: "michael-p-2", firstName: "Michael", lastName: "P", dob: "01/09/1955", updatedAt: "01/01/2022", tenantId: "54321", appId: "007" }
]

export const usePatientsApi = () => {

    const [patients, setPatients] = useState<Array<Patient>>([]);

    const getPatients = useCallback(async (env: Env) => {
        const response = await fetch(`${env.DEMO_API}/patients`);
        const data = await response.json();
        console.log("patients api", data);
        setPatients(data)
    }, []);

    const getPatient = useCallback(async (env: Env, id: string) => {
        const response = await fetch(`${env.DEMO_API}/patients/${id}`);
        const data = await response.json();
        console.log("get patient", data);
        return data;
    }, []);

    const createPatient = useCallback(async (env: Env, patient: Patient) => {
        const response = await fetch(`${env.DEMO_API}/create_patient`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(patient)
        });
        const data = await response.json();
        console.log("create patient", data);
        getPatients(env);
        //setPatients([...patients, data])
    }, []);

    return { getPatients, createPatient, getPatient, patients }
}