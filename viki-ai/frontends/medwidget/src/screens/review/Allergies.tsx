import { RepeatIcon } from "@chakra-ui/icons";
import {
  Box,
  Button,
  Center,
  Flex,
  Heading,
  IconButton,
  useToken,
} from "@chakra-ui/react";
import {
  DynamicTableContainer,
  LinkButton,
  Tooltip,
} from "@mediwareinc/wellsky-dls-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { ContextDocumentItemFilter } from "tableOfContentsTypes";
import { DocumentFile, Env } from "types";
import { usePatientProfileStore } from "store/patientProfileStore";
import useClinicalDataApi from "hooks/useClinicalDataApi";
import OverlayLoader from "./OverlayLoader";
import useEvidenceApi from "hooks/useEvidenceApi";
import { Allergies, ClinicalDataReference } from "store/storeTypes";

interface AllergiesListProps {
  env: Env;
  currentDocument: DocumentFile | null;
  documentsInReview: DocumentFile[];
  pageProfiles?: Record<string, ContextDocumentItemFilter>;
  onEvidenceRequested?: (evidenceInfo: any) => void;
}

const AllergiesList = ({
  currentDocument,
  env,
  documentsInReview,
  pageProfiles,
  onEvidenceRequested,
}: AllergiesListProps) => {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [tableHeaderColor, deletedColor] = useToken(
    // the key within the theme, in this case `theme.colors`
    "colors",
    // the subkey(s), resolving to `theme.colors.red.100`
    ["neutral.100", "elm.500"],
    // a single fallback or fallback array matching the length of the previous arg
  );
  const [evidenceClicked, setEvidenceClicked] = useState<string | null>(null);
  const allowModification = false;
  const { getEvidence, evidence } = useEvidenceApi();

  useEffect(() => {
    onEvidenceRequested && onEvidenceRequested(evidence);
  }, [evidence, onEvidenceRequested]);

  const columns = useMemo(() => {
    return [
      {
        dataIndex: "clinicalDataId",
        id: "clinicalDataId",
        title: "",
        sortable: false,
        render: (id: any, record: Allergies) => {
          return (
            <div
              style={{
                display: "flex",
                justifyContent: "left",
              }}
            >
              {/* <MagicSparkle
              fontSize={24}
              animated={false}
              onClick={() => { getEvidence(env, record.references[0].clinicalDataId, record.data.substance || record.data.reaction, record.references[0].documentId, record.references[0].pageNumber); }}
            /> */}

              {record.references.map((reference: ClinicalDataReference) => {
                return (
                  <>
                    <Tooltip label="Click to highlight source">
                      <Button
                        id={reference?.evidenceMarkId}
                        height={"15px"}
                        backgroundColor={
                          evidenceClicked === reference?.evidenceMarkId
                            ? "green"
                            : "gray"
                        }
                        size={"xs"}
                        borderRadius={"1000000px"}
                        onClick={(e: any) => {
                          setEvidenceClicked(reference?.evidenceMarkId || "");
                          getEvidence(
                            env,
                            reference?.clinicalDataId,
                            record.data.substance || record.data.reaction,
                            reference?.documentId,
                            reference?.pageNumber,
                          );
                        }}
                      >
                        {reference?.pageNumber}
                      </Button>
                    </Tooltip>
                  </>
                );
              })}
            </div>
          );
        },
      },
      {
        dataIndex: "substance",
        id: "substance",
        sortable: false,
        title: "Substance",
        render: (id: any, record: Allergies) => {
          return (
            <div
              style={{
                display: "flex",
                justifyContent: "left",
              }}
            >
              {record.data.substance}
            </div>
          );
        },
      },
      {
        dataIndex: "reaction",
        id: "reaction",
        sortable: false,
        title: "Reaction",
        render: (id: any, record: Allergies) => {
          return (
            <div
              style={{
                display: "flex",
                justifyContent: "left",
              }}
            >
              {record.data.reaction}
            </div>
          );
        },
      },
    ];
  }, [env, getEvidence, evidenceClicked]);

  const { loading, allergies } = usePatientProfileStore();

  const { fetchAllergies } = useClinicalDataApi();

  useEffect(() => {
    if (currentDocument?.id) {
      fetchAllergies(currentDocument?.id);
    }
  }, [currentDocument?.id, fetchAllergies]);

  const refetch = useCallback(async () => {
    if (currentDocument?.id) {
      await fetchAllergies(currentDocument.id);
    }
  }, [currentDocument?.id, fetchAllergies]);

  return (
    <Flex flex="1 1 0%" overflow="auto" direction="column">
      <Heading size="sm" my="2" display="flex" flexDirection="row">
        Allergies
        <IconButton
          variant="link"
          style={{ marginLeft: "1rem" }}
          size="lg"
          onClick={refetch}
          aria-label="Refresh"
          icon={<RepeatIcon />}
        />
        <div style={{ flex: "1 1 0" }}></div>
        {allowModification && (
          <LinkButton onClick={() => {}}>Add Allergies</LinkButton>
        )}
      </Heading>
      <Box flex="1 1 0" position="relative" overflow="auto">
        {loading.has("allergies") && <OverlayLoader />}
        <DynamicTableContainer
          headerColor={tableHeaderColor}
          rowKey={(data) => data.data.substance}
          columns={columns}
          dataSource={allergies}
          noDataContent={
            <Center>
              <Heading size="md">No Data</Heading>
            </Center>
          }
          pagination={{
            isStatic: true,
            defaultPageSize: 25,
          }}
        />
      </Box>
    </Flex>
  );
};

export default AllergiesList;
