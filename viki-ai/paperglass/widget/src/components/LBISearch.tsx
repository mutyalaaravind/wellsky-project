import { Search2Icon } from "@chakra-ui/icons";
import { Box, Flex, Heading, Input, InputGroup, InputLeftElement, Spinner, Text } from "@chakra-ui/react";
import { Select } from "@mediwareinc/wellsky-dls-react";
import { useState, useEffect, useCallback } from "react";
import { Env } from "../types";

// TODO: Temporary
const labels = [
  'demographics',
  'medications',
  'diagnoses',
  'procedures',
  'symptoms',
  'medical_history',
  'family_history',
  'allergies',
  'vitals',
  'visits',
  'lab_results',
  'risk_factors',
  'follow_up_plans',
  'patient_education',
];

type LBISearchProps = {
  env: Env;
  patientId: string;
};

export default function LBISearch({ env, patientId }: LBISearchProps) {
  const [busy, setBusy] = useState(false);
  const [label, setLabel] = useState(labels[0]);
  const [question, setQuestion] = useState("");
  const [matchedPages, setMatchedPages] = useState([]);
  const [result, setResult] = useState("");

  const prompt = useCallback((label: string, question: string) => {
    return fetch(`${env.API_URL}/api/prompt-lbi`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ patientId, label, question }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log('Success:', data);
        return data;
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  }, []);

  return (
    <>
      <Flex p={2} direction="row" >
        <Select onChange={(e: any) => { setLabel(e.target.value); }} value={label} isDisabled={busy}>
          {labels.map((label) => (
            <option key={label} value={label}>{label}</option>
          ))}
        </Select>
        <InputGroup>
          <InputLeftElement pointerEvents="none">
            <Search2Icon color="gray.300" />
          </InputLeftElement>
          <Input
            type="text"
            placeholder="Search"
            disabled={busy}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                setBusy(true);
                prompt(label, question).then(data => {
                  setBusy(false);
                  setMatchedPages(data.matched_pages);
                  setResult(data.result);
                });
              }
            }}
          />
        </InputGroup>
      </Flex>
      {busy ? (
        < div style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', gap: '1rem' }
        }>
          <Spinner size="lg" />
          <Text>Prompting for "{question}"</Text>
        </div >

      ) : (
        <div>
          {(result && result.length > 0) ? (
            <div>
              <Box p={4}>
                <Heading size="md">Results</Heading>
                {result.split('\n').map(line => (
                  <Text key={line}>{line}</Text>
                ))}
              </Box>
              <Box p={4}>
                <Heading size="md">Matched Pages</Heading>
                {matchedPages.length ? matchedPages.map((id_parts: any) => (
                  <Text key={JSON.stringify(id_parts)}>Document: {id_parts[0]}, Chunk: {id_parts[1]}, Page: {id_parts[2]}</Text>
                )) : <p>No pages were matched</p>}
              </Box>
            </div>
          ) : null}
        </div>
      )}
    </>
  );
}
