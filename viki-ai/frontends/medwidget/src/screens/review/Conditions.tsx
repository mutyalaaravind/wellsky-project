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
import { Condition } from "store/storeTypes";

interface ConditionListProps {
  env: Env;
  currentDocument: DocumentFile | null;
  documentsInReview: DocumentFile[];
  pageProfiles?: Record<string, ContextDocumentItemFilter>;
  onEvidenceRequested?: (evidenceInfo: any) => void;
}

const ConditionsList = ({
  currentDocument,
  env,
  documentsInReview,
  pageProfiles,
  onEvidenceRequested,
}: ConditionListProps) => {
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
  const { getConditionsEvidence, evidence } = useEvidenceApi();

  useEffect(() => {
    onEvidenceRequested && onEvidenceRequested(evidence);
  }, [evidence, onEvidenceRequested]);

  const columns = useMemo(() => {
    return [
      {
        title: "Source",
        id: "category",
        dataIndex: "category",
        sortable: true,
        render: (category: any, record: Condition) => {
          return (
            <>
              <div
                style={{
                  display: "flex",
                  justifyContent: "left",
                }}
              >
                {record.evidences.map((evidence, index) => {
                  return (
                    <>
                      <Tooltip label="Click to highlight source">
                        <Button
                          id={evidence?.markerId}
                          height={"15px"}
                          backgroundColor={
                            evidenceClicked === evidence?.markerId
                              ? "green"
                              : "gray"
                          }
                          size={"xs"}
                          borderRadius={"1000000px"}
                          onClick={(e: any) => {
                            setEvidenceClicked(evidence?.markerId || "");
                            getConditionsEvidence(
                              env,
                              evidence?.evidenceSnippet || "",
                              evidence?.startPosition || 0,
                              evidence?.endPosition || 0,
                              evidence?.evidenceReference,
                              evidence?.documentId || "",
                              evidence?.pageNumber || 0,
                            );
                            //getEvidence(env, reference?.clinicalDataId, record.data.substance || record.data.reaction, reference?.documentId, reference?.pageNumber);
                          }}
                        >
                          {evidence?.pageNumber}
                        </Button>
                      </Tooltip>
                    </>
                  );
                })}
              </div>
            </>
          );
        },
      },
      {
        title: "Category",
        id: "category",
        dataIndex: "category",
        sortable: true,
        render: (category: any, record: Condition) => {
          return category;
        },
      },
      {
        title: "Codes",
        id: "icd10Codes",
        dataIndex: "icd10Codes",
        sortable: true,
        render: (icd10Codes: any, record: Condition) => {
          return record.icd10Codes
            .map((code, index) => {
              return code.icdCode;
            })
            .join(", ");
        },
      },
    ];
  }, [env, getConditionsEvidence, evidenceClicked]);

  const { loading, conditions } = usePatientProfileStore();

  const { fetchConditions } = useClinicalDataApi();

  useEffect(() => {
    if (currentDocument?.id) {
      fetchConditions(currentDocument.id);
    }
  }, [currentDocument?.id, fetchConditions]);

  const refetch = useCallback(async () => {
    if (currentDocument?.id) {
      await fetchConditions(currentDocument.id);
    }
  }, [currentDocument?.id, fetchConditions]);

  return (
    <Flex flex="1 1 0%" overflow="auto" direction="column">
      <Heading size="sm" my="2" display="flex" flexDirection="row">
        Conditions
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
          <LinkButton onClick={() => {}}>Add Conditions</LinkButton>
        )}
      </Heading>
      <Box flex="1 1 0" position="relative" overflow="auto">
        {loading.has("conditions") && <OverlayLoader />}
        <DynamicTableContainer
          headerColor={tableHeaderColor}
          rowKey={(data) => data.category}
          columns={columns}
          dataSource={conditions}
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

export default ConditionsList;
