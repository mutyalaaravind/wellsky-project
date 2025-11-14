import { Accordion, AccordionButton, AccordionIcon, AccordionItem, AccordionPanel, Box, Flex, HStack, Heading, Input, InputGroup, InputLeftElement, Radio, RadioGroup, Spinner, Stack, Table, TableContainer, Tbody, Td, Thead, Tr } from "@chakra-ui/react";
import SearchBar from "./SearchBar";
import { useCallback, useEffect, useState } from "react";
import { useSearchContext } from "../context/SearchContext";
import { Search2Icon } from "@chakra-ui/icons";
import { useDocumentVectorSearchApi } from "../hooks/useSearchApi";
import useEnvJson from "../hooks/useEnvJson";
import { Env, SettingType } from "../types";
import DataTable from "./DataTable";
import InfoDrawer from "./InfoDrawer";
import { EvidenceViewerProps } from "../EvidenceViewer";

const DocumentVectorBasedSearch = (props:{patientId:string,settings:SettingType}) => {
    const {patientId,settings} = props;
    const [searchText, setSearchText] = useState<string>("");
    const [embeddingStrategy, setEmbeddingStrategy] = useState<number>(0);
    const [searchQueryStrategy, setSearchQueryStrategy] = useState<string | null>(null);
    const env:Env | null =  useEnvJson();
    const [requestedInfo, setRequestedInfo] = useState<any | null>(null);
    const [selectedDoc, setSelectedDoc] = useState<any | null>(null);
    const [evidenceViewerProps, setEvidenceViewerProps] = useState<EvidenceViewerProps | null>(null);
    
    const {searchDocumentByVectors, busy,error, documentSearchResults} = useDocumentVectorSearchApi(env);

    const onSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSearchText(event.target.value);
    }

    useEffect(()=>{
        if(selectedDoc){
            setEvidenceViewerProps({identifier:selectedDoc.document_id,substring:selectedDoc.snippets});
        }
        
    },[selectedDoc]);

    return <>
        <Box w={"100%"}>
            <HStack w={"100%"}>
                {/* <Flex p={0} direction="column"> */}
                    <InputGroup>
                        <InputLeftElement pointerEvents="none">
                        <Search2Icon color="gray.300" />
                        </InputLeftElement>
                        <Input
                            width={"100%"}
                            // type="tel"
                            size="xl"
                            placeholder="Search"
                            value={searchText}
                            onChange={onSearchChange}
                            onKeyDown={(e) => {
                                if (e.key === "Enter") {
                                    searchDocumentByVectors(patientId,searchText,settings.documentVectorSearchThreshold,embeddingStrategy,searchQueryStrategy);
                                }
                            }}
                        />
                    </InputGroup>
                    {/* </Flex> */}
            </HStack>
            <HStack paddingTop={"2"} paddingBottom={"2"}>
                    <RadioGroup value={embeddingStrategy.toString()} onChange={(e:any)=>{setEmbeddingStrategy(parseInt(e))}}>
                        <Stack direction="row">
                            <Radio value="0">DOT PRODUCT</Radio>
                            <Radio value="1">COSINE</Radio>
                        </Stack>
                    </RadioGroup>
            </HStack>
            {/* <HStack paddingTop={"2"} paddingBottom={"2"}>
                    <RadioGroup value={searchQueryStrategy || "None"} onChange={(e:any)=>{setSearchQueryStrategy(e)}}>
                        <Stack direction="row">
                            <Radio value="None">All</Radio>
                            <Radio value="question">By Question</Radio>
                            <Radio value="summary">By Summary</Radio>
                            <Radio value="details">By Details</Radio>
                        </Stack>
                    </RadioGroup>
            </HStack> */}
            <HStack paddingTop={"2"} paddingBottom={"2"}>
                {busy ? (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', padding: '1rem' }}>
                    <Spinner size="lg" style={{ marginBottom: '1rem' }} />
                    Searching
                    </div>
                ) : (
                        <>
                            {error && <Box>Error fetching results</Box>}
                            {documentSearchResults?.length ? (
                                <div>
                                <Heading style={{ margin: '2rem' }}>
                                    Results
                                </Heading>
                                <TableContainer>
                                    <Table variant="striped" maxW="1500px">
                                    <Thead>
                                        <Tr>
                                        <Td width="1%">Document</Td>
                                        <Td >Snippet Summary</Td>
                                        <Td >Snippet</Td> 
                                        <Td >Distance</Td> 
                                        <Td >Embedding Strategy</Td> 
                                        </Tr>
                                    </Thead>
                                    <Tbody >
                                        {documentSearchResults.map((result: any) => (
                                        <Tr key={result.snippets} wordBreak="break-all" onClick={()=>{setSelectedDoc(result)}}>
                                            <Td>
                                                {result.doc_url.split('/').pop()}
                                            </Td>
                                            <Td p={2}
                                                wordBreak="break-all"
                                                whiteSpace="normal"
                                            >
                                            <div >{result.snippets_summary}</div>
                                            </Td>
                                            <style type="text/css">
                                            {`.searchglass-snippet-evidence b {
                                                background-color: yellow;
                                            }`}
                                            </style>
                                            <Td className="searchglass-snippet-evidence" wordBreak="break-word" whiteSpace="normal" cursor="pointer" 
                                                //onClick={() => requestInfo(result.id, result.snippets)}
                                            >
                                            <span dangerouslySetInnerHTML={{ __html: result.snippets }} />
                                            </Td>
                                            <Td>
                                                {result.distance.toFixed(2)}
                                            </Td>
                                            <Td>
                                                {result.embedding_chunk_strategy}
                                            </Td>
                                        </Tr>
                                        ))}
                                    </Tbody>
                                    </Table>
                                </TableContainer>
                                </div>
                            ) : (<>{!busy && !error && <Box paddingTop={"4"}><b>No Results Found</b></Box>}</>)}
                        </>
                    )
                }
            </HStack>
            {selectedDoc && <InfoDrawer
                //data={selectedDoc.doc_url}
                onClose={() => setSelectedDoc(null)}
                search={searchText}
                //showEvidenceViewer={showEvidenceViewer}
                evidenceViewerProps={evidenceViewerProps}
            />}
        </Box>
    </>
}

export default DocumentVectorBasedSearch;