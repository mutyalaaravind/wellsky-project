import { Heading } from "@chakra-ui/react";
import { useState } from "react";
import { Env } from "../types";
import { set } from "lodash";

type FHIRSettingsProp = {
    patientId: string;
    env:Env;
}

export const FHIRSettings = ({env, patientId}:FHIRSettingsProp) => {
    const [busy, setBusy] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);
    return (
        <div>
        <Heading style={{ margin: "2rem" }}>Upload FHIR Bundle</Heading>

        <input
            type="file"
            accept=".json"
            disabled={busy}
            onChange={(e) => {
                setSuccess(null);
                setError(null);
            const file = e.target.files?.[0];
            if (file == null) {
                return;
            }

            // Upload file
            const formData = new FormData();
            formData.append("file", file);
            formData.append("patientId", patientId);
            fetch(`${env.API_URL}/api/fhir-bundle`, {
                method: "POST",
                body: formData,
            })
                .then((response) => response.json())
                .then((data) => {
                    setSuccess("data.message");
                })
                .catch((error) => {
                    console.error("Upload FHIR resources error:", error);
                    setError(error.message);
                })
                .finally(() => {
                setBusy(false);
                });
            }}
        /><br/>
        {error && <div>upload resulted in error: {error}</div>}
        {success && <div>upload resulted in success</div>}
        </div>
    );
}