// import { DynamicTableContainer } from "@mediwareinc/wellsky-dls-react";
import { getColumnsFromData } from "../utils/helpers";
import {
  Flex,
  HStack,
  Table,
  TableContainer,
  Tbody,
  Td,
  Text,
  Th,
  Thead,
  Tr,
  VStack,
  useToast,
} from "@chakra-ui/react";
import { Display1 } from "@mediwareinc/wellsky-dls-react";
import { get } from "lodash";
import { useState } from "react";
import InfoDrawer from "./InfoDrawer";
import { EvidenceViewer,EvidenceViewerProps } from "../EvidenceViewer";
import useEnvJson from "../hooks/useEnvJson";
import { Env } from "../types";

export interface DataTableProps {
  data?: Record<string, any>[];
  heading?: string;
  search?: string;
}

function DataTable(props: DataTableProps) {
  const [drawerData, setDrawerData] = useState<any>(null);
  // Import the missing type declaration
  const env = useEnvJson<Env>();
  const [evidenceViewerProps, setEvidenceViewerProps] = useState<EvidenceViewerProps | null>(null);
  const [showEvidenceViewer, setShowEvidenceViewer] = useState<boolean>(false);
  const toast = useToast();
  if (!props.data) return null;
  console.log("props.data", props.data);
  const columns = getColumnsFromData(props.data, {
    hideColumns: ["id", "infoData"],
    columnStyles: {
      medication: {
        fontWeight: "bold",
      },

      // doseForm: {
      //   fontStyle: "italic",
      //   fontSize: "larger",
      //   fontWeight: "bold",
      // },
    },
  });
  return (
    <>
    <VStack align="flex-start" p={2}>
      <Display1 fontSize="x-large">{props.heading}</Display1>
      <Flex direction="row">
        {/* <DynamicTableContainer columns={columns} dataSource={data} /> */}
        <TableContainer>
          <Table variant="striped" maxW="1500px">
            <Thead>
              <Tr>
                {columns.map((col) => {
                  return (
                    <Th key={col.id} textAlign="left" p={2} {...col.cssProps}>
                      {col.title}
                    </Th>
                  );
                })}
              </Tr>
            </Thead>
            <Tbody>
              {props.data?.map((d, index) => {
                return (
                  <Tr
                    key={d.id || index}
                    onClick={() => {
                      if (d.infoData && d.infoData.includes("gs://")) {
                        // setShowEvidenceViewer(true);
                        setEvidenceViewerProps({substring:d.snippets.substring(d.snippets.indexOf("<b>")+3,d.snippets.indexOf("</b>")), identifier:d.id});
                      }else{
                        setEvidenceViewerProps(null);
                      }
                      if (d.infoData) {
                        setDrawerData(d.infoData);
                      }
                      // toast({
                      //   title: `Row ${d.id || index} clicked!`,
                      //   description: <pre>{JSON.stringify(d, null, 2)}</pre>,
                      //   status: "success",
                      //   duration: 1500,
                      //   isClosable: true,
                      // });
                    }}
                    wordBreak="break-all"
                    // wordWrap="break-word"
                  >
                    {columns.map((col, idx) => {
                      return (
                        <Td
                          key={(d.id || index) + idx}
                          p={2}
                          {...col.cssProps}
                          wordBreak="break-all"
                          wordWrap="break-word"
                        >
                          <span
                            style={{
                              textWrap: "wrap",
                              maxWidth: "200px",
                              fontSize: "12px",
                            }}
                            dangerouslySetInnerHTML={{
                              __html: get(d, col.dataIndex),
                            }}
                          ></span>
                        </Td>
                      );
                    })}
                  </Tr>
                );
              })}
            </Tbody>
          </Table>
        </TableContainer>
        {/* {showEvidenceViewer && <EvidenceViewer identifier={evidenceViewerProps?.identifier || ""} substring={evidenceViewerProps?.substring || ""} />} */}
      </Flex>
      {drawerData && (
        <InfoDrawer
          data={drawerData}
          onClose={() => setDrawerData(null)}
          search={props.search}
          //showEvidenceViewer={showEvidenceViewer}
          evidenceViewerProps={evidenceViewerProps}
        />
      )}
    </VStack>
    </>
  );
}

export default DataTable;
