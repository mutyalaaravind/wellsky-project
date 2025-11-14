import { RepeatIcon } from "@chakra-ui/icons";
import {
  Box,
  Button,
  Center,
  Flex,
  Heading,
  IconButton,
  Radio,
  RadioGroup,
  Stack,
  useToken,
} from "@chakra-ui/react";
import {
  DynamicTableContainer,
  DynamicTableContainerProps,
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
import { Immunizations, ClinicalDataReference } from "store/storeTypes";

interface ImmunizationsListProps {
  env: Env;
  currentDocument: DocumentFile | null;
  documentsInReview: DocumentFile[];
  pageProfiles?: Record<string, ContextDocumentItemFilter>;
  onEvidenceRequested?: (evidenceInfo: any) => void;
}

const ImmunizationsList = ({
  currentDocument,
  env,
  documentsInReview,
  pageProfiles,
  onEvidenceRequested,
}: ImmunizationsListProps) => {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [tableHeaderColor, deletedColor] = useToken(
    // the key within the theme, in this case `theme.colors`
    "colors",
    // the subkey(s), resolving to `theme.colors.red.100`
    ["neutral.100", "elm.500"],
    // a single fallback or fallback array matching the length of the previous arg
  );
  const { getEvidence, evidence } = useEvidenceApi();
  const allowModification = false;
  const [evidenceClicked, setEvidenceClicked] = useState<string | null>(null);

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
        render: (id: any, record: Immunizations) => {
          return (
            <div
              style={{
                display: "flex",
                justifyContent: "left",
              }}
            >
              {record.references.map((reference: ClinicalDataReference) => {
                return (
                  <>
                    <Tooltip label="Click to highlight source">
                      <Button
                        id={reference?.clinicalDataId}
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
                            record.data.originalExtractedString
                              ? record.data.originalExtractedString
                              : record.data.name,
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
        dataIndex: "name",
        id: "name",
        sortable: false,
        title: "Name",
        render(value, record) {
          return <div>{record.data.name}</div>;
        },
      },
      {
        dataIndex: "status",
        id: "status",
        sortable: false,
        title: "Status",
        render(value, record) {
          return (
            <RadioGroup value={record.data.status as string}>
              <Stack direction="row">
                <Radio value="yes">Yes</Radio>
                <Radio value="no">No</Radio>
                <Radio value="unknown">Unknown</Radio>
              </Stack>
            </RadioGroup>
          );
        },
      },
      {
        dataIndex: "date",
        id: "date",
        sortable: false,
        title: "Date",
        render(value, record) {
          return (
            // <Input
            //   size="md"
            //   type="date"
            //   placeholder="Date"
            //   value={value as string}
            // />
            <div>{record.data.date ? record.data.date : ""}</div>
          );
        },
      },
    ] as DynamicTableContainerProps<Immunizations>["columns"];
  }, [env, getEvidence, evidenceClicked]);

  const { loading, immunizations } = usePatientProfileStore();

  const { fetchImmunizations } = useClinicalDataApi();

  useEffect(() => {
    if (currentDocument?.id) {
      fetchImmunizations(currentDocument.id);
    }
  }, [currentDocument?.id, fetchImmunizations]);

  const refetch = useCallback(async () => {
    if (currentDocument?.id) {
      await fetchImmunizations(currentDocument.id);
    }
  }, [currentDocument?.id, fetchImmunizations]);

  return (
    <Flex flex="1 1 0%" direction="column" p={1}>
      <Heading size="sm" my="2" display="flex" flexDirection="row">
        Immunizations
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
          <LinkButton onClick={() => {}}>Add Immunizations</LinkButton>
        )}
      </Heading>
      <Box flex="1 1 0" position="relative" overflow="auto">
        {loading.has("immunizations") && <OverlayLoader />}
        <DynamicTableContainer
          tableProps={{ size: "sm" }}
          rowKey={(data) => data.id}
          headerColor={tableHeaderColor}
          columns={columns}
          dataSource={immunizations}
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

export default ImmunizationsList;
