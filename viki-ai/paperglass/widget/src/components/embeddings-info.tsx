import { Box, Button, HStack, Heading, Input, Radio, RadioGroup, Spinner, Stack, Table, TableContainer, Tbody, Td, Thead, Tr } from "@chakra-ui/react"
import { useEmbeddingsApi } from "../hooks/useEmbeddings";
import useEnvJson from "../hooks/useEnvJson";
import { Env } from "../types";
import { useEffect, useState } from "react";
import { SubHeading1 } from "@mediwareinc/wellsky-dls-react";

const EmbeddingsList = (props:{env:Env,patientId:string | null,documentId: string}) => {
    const {env,patientId,documentId} = props;
    const [chunkIndex, setChunkIndex] = useState<number>(0);
    const [embeddingStrategy, setEmbeddingStrategy] = useState<number>(0);
    const [embeddingChunkingStrategy, setEmbeddingChunkingStrategy] = useState<number>(1);
    const {getDocumentEmbeddings,reindexDocumentEmbeddings, updateDocumentEmbeddingStrategy,busy,error, documentEmbeddings} = useEmbeddingsApi(env);

    useEffect(()=>{
        if(patientId){
            getDocumentEmbeddings(patientId,documentId,embeddingStrategy,embeddingChunkingStrategy);
        }
    },[getDocumentEmbeddings,patientId,documentId,embeddingStrategy,embeddingChunkingStrategy])

    return (
        <>
        {busy && <div style={{ position: 'absolute', top: '0', left: '0', right: '0', bottom: '0', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: 'rgba(255, 255, 255, 0.8)', zIndex: '1000' }}>
                    <Spinner />
                    <div style={{ marginTop: '1rem' }}>Fetching Embeddings </div>
        </div>}
        {!busy && 
            <>
            <HStack>
                <Heading size={"sm"} paddingTop={"2"} paddingBottom={"2"}>Embedding Settings</Heading>
            </HStack>
            <HStack paddingTop={"2"} paddingBottom={"2"}>
                <Box>Embedding Strategy:</Box>
                <Box>
                    <RadioGroup value={embeddingStrategy.toString()} onChange={(e:any)=>{setEmbeddingStrategy(parseInt(e))}}>
                        <Stack direction="row">
                            <Radio value="0">DOT PRODUCT</Radio>
                            <Radio value="1">COSINE</Radio>
                        </Stack>
                    </RadioGroup>
                </Box>
            </HStack>
            <HStack paddingTop={"2"} paddingBottom={"2"}>
                <Box>Embedding Chunking Strategy:</Box>
                <Box>
                    <RadioGroup value={embeddingChunkingStrategy.toString()} onChange={(e:any)=>{( setEmbeddingChunkingStrategy(parseInt(e)))}}>
                        <Stack direction="row">
                            <Radio value="0">MULTI MODAL</Radio>
                            <Radio value="1">MARKDOWN_TEXT_SPLITTER</Radio>
                            <Radio value="2">NLTK_TEXT_SPLITTER</Radio>
                        </Stack>
                    </RadioGroup>
                </Box>
            </HStack>
            <HStack paddingTop={"2"} paddingBottom={"2"}>
                <Box>Reindex for Chunk:</Box>
                <Box>
                    <Input width={"50px"} value={chunkIndex} onChange={(e:any) => setChunkIndex(e.target.value)} /> <Button onClick={()=>{updateDocumentEmbeddingStrategy(documentId,embeddingStrategy,embeddingChunkingStrategy);reindexDocumentEmbeddings(documentId,chunkIndex)}}>Reindex</Button>
                </Box>
            </HStack>
            <HStack paddingTop={"2"} paddingBottom={"2"}>
                <Heading size={"sm"} >Embeddings</Heading><Button onClick={()=>{getDocumentEmbeddings(patientId || "",documentId,embeddingStrategy,embeddingChunkingStrategy)}} >Refresh</Button>
            </HStack>
            <HStack paddingTop={"2"} paddingBottom={"2"}>
                {documentEmbeddings && <TableContainer>
                    <Table variant="simple" size="sm">
                        <Thead>
                        <Tr>
                            <Td>Data</Td>
                            <Td width="1%">id</Td>
                        </Tr>
                        </Thead>
                        <Tbody>
                        {documentEmbeddings?.map((embeddings:any) => (
                            <Tr key={embeddings.id}>
                            <Td>{embeddings.data}</Td>
                            <Td>{embeddings.id}</Td>
                            </Tr>
                        ))}
                        </Tbody>
                    </Table>
                </TableContainer>}
            </HStack>
            </>
        }
        </>
    )
}

export {EmbeddingsList}