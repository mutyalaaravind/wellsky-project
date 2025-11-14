import { Box, Button, HStack, Heading, IconButton, Input, Radio, RadioGroup, Spinner, Stack, Table, TableContainer, Tbody, Td, Thead, Tr } from "@chakra-ui/react"
import { useEmbeddingsApi } from "../hooks/useEmbeddings";
import useEnvJson from "../hooks/useEnvJson";
import { Env } from "../types";
import { useCallback, useEffect, useState } from "react";
import { SubHeading1 } from "@mediwareinc/wellsky-dls-react";
import { useNamedEntityExtractionApi } from "../hooks/useNamedEntityExtraction";
import { RepeatIcon } from "@chakra-ui/icons";

const NamedEntityExtraction = (props: { env: Env, documentId: string, patientId: string | null, entityType: string, setAnnotations: any, currentPage: number }) => {
    const { env, patientId, entityType, setAnnotations, documentId, currentPage } = props;

    const { getNamedEntityExtraction, busy, error, namedEntityExtractions } = useNamedEntityExtractionApi(env);

    useEffect(() => {
        if (patientId) {
            getNamedEntityExtraction(patientId, entityType, documentId, currentPage);
        }
    }, [getNamedEntityExtraction, patientId, entityType, currentPage]);

    useEffect(() => {
        console.log("namedEntityExtractions", namedEntityExtractions);
        // setAnnotations([{
        //   x: 0.067,
        //   y: 0.175,
        //   width: 0.33 - 0.067,
        //   height: 0.182 - 0.175,
        //   text: 'BETHANECHOL CHLORIDE',
        //   page: 3,
        // }]);
    }, [namedEntityExtractions]);

    const onEvidenceClick = useCallback((namedEntity: any) => {
        console.log("onEvidenceClick", namedEntity);
        setAnnotations([{
            x: namedEntity.evidence?.x1,
            y: namedEntity.evidence?.y1,
            width: namedEntity.evidence?.x2 - namedEntity.evidence?.x1,
            height: namedEntity.evidence?.y2 - namedEntity.evidence?.y1,
            text: namedEntity.evidence?.text,
            page: namedEntity.reference?.chunk ? parseInt(namedEntity.reference?.chunk) + 1 : 1,
        }]);
    }, [setAnnotations]);

    return (
        <>
            {busy && <div style={{ position: 'absolute', top: '0', left: '0', right: '0', bottom: '0', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: 'rgba(255, 255, 255, 0.8)', zIndex: '1000' }}>
                <Spinner />
                <div style={{ marginTop: '1rem' }}>Fetching Entities Extracted </div>
            </div>}
            {!busy &&
                <>
                    <HStack>
                        <Heading size={"sm"} paddingTop={"2"} paddingBottom={"2"}>{entityType}</Heading>
                        <IconButton aria-label="Refresh" style={{ float: 'right' }} variant="link">
                            <RepeatIcon onClick={() => getNamedEntityExtraction(patientId || "", entityType, documentId, currentPage)} />
                        </IconButton>
                    </HStack>
                    {namedEntityExtractions && namedEntityExtractions.length > 0 ? <HStack paddingTop={"2"} paddingBottom={"2"}>
                        <TableContainer>
                            <Table variant="simple" size="sm">
                                <Thead>
                                    <Tr>
                                        <Td>Name</Td>
                                        <Td>Dosage</Td>
                                        <Td>Frequency</Td>
                                        <Td>Route</Td>
                                        <Td>Reason</Td>
                                        <Td>Start Date</Td>
                                        <Td>End Date</Td>
                                        {/* <Td>References</Td> */}
                                        <Td>Evidence</Td>
                                    </Tr>
                                </Thead>
                                <Tbody>
                                    {namedEntityExtractions?.map((namedEntity: any) => (
                                        <Tr key={namedEntity.name} onClick={() => { onEvidenceClick(namedEntity) }}>
                                            <Td>{namedEntity.name}</Td>
                                            <Td>{namedEntity.dosage}</Td>
                                            <Td>{namedEntity.frequency}</Td>
                                            <Td>{namedEntity.route}</Td>
                                            <Td>{namedEntity.reason}</Td>
                                            <Td>{namedEntity.start_date}</Td>
                                            <Td>{namedEntity.end_date}</Td>
                                            {/* <Td>doc:{namedEntity.reference?.document}, chunk: {namedEntity.reference?.chunk}</Td> */}
                                            <Td>{namedEntity.evidence?.text}</Td>
                                        </Tr>
                                    ))}
                                </Tbody>
                            </Table>
                        </TableContainer>
                    </HStack> : <HStack><Box> No {entityType} found</Box></HStack>}
                    {error && <HStack>{error}</HStack>}
                </>
            }
        </>
    )
}

export { NamedEntityExtraction }
