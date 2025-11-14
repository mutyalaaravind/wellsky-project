import { useState } from "react";

import { Heading } from "@chakra-ui/react";
import { FaxOutlined } from "@mediwareinc/wellsky-dls-react-icons";

import { Block } from "components/Block";
import { AddMedication } from "screens/review/Dialogs";
import useEnvJson from "hooks/useEnvJson";
import { Env } from "types";

export const NoMedications = () => {
  const [addingMedication, setAddingMedication] = useState(false);
  const env = useEnvJson<Env>();

  return (
    <Block style={{ alignItems: "center", justifyContent: "center" }}>
      <AddMedication
        apiRoot={env?.API_URL || ""}
        isOpen={addingMedication}
        onSave={(medication) => {
          setAddingMedication(false);
          alert("TODO");
        }}
        onCancel={() => {
          setAddingMedication(false);
        }}
      />

      <FaxOutlined fontSize="20vh" />
      <Heading size="sm" style={{ margin: "1rem" }}>
        There are no medications listed
      </Heading>
      <div style={{ marginBottom: "1rem" }}>
        Select document to extract or add medications
      </div>
      {/*
      <PrimaryButton onClick={() => setAddingMedication(true)}>Add Medication</PrimaryButton>
      */}
    </Block>
  );
};
