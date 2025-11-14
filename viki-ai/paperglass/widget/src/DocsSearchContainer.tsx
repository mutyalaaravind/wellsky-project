import { Accordion, AccordionButton, AccordionIcon, AccordionItem, AccordionPanel, Box, Heading, Table, TableContainer, Tbody, Td, Thead, Tr } from "@chakra-ui/react";
import {
  Flex,
  HStack,
  Input,
  InputGroup,
  InputLeftElement,
  Tag,
  TagLabel,
  TagLeftIcon,
} from "@chakra-ui/react";
import { AddIcon, CloseIcon, Search2Icon } from "@chakra-ui/icons";
import { useSearchApi } from "./hooks/useSearchApi";
import React, { useEffect } from "react";
import { Env } from "./types";
import { EvidenceViewer } from "./EvidenceViewer";
import { LinkButton, Spinner } from "@mediwareinc/wellsky-dls-react";

type DocSearchContainerProps = {
  env: Env;
  identifier: string;
  searchText: string;
  onSearchResults: (results: any, summary: any) => void;

}

function DocsSearchContainer({ env, identifier, searchText, onSearchResults }: DocSearchContainerProps) {
  const { search, results, busy, summary, error } = useSearchApi(env);
  //const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => { setSearchText(event.target.value) };
  const [requestedInfo, setRequestedInfo] = React.useState<any | null>(null);

  const requestInfo = React.useCallback((documentId: string, snippets: string) => {
    // Extract text between <b></b> tags
    const re = /<b>(.*?)<\/b>/g;
    const matches = snippets.match(re);
    console.log(documentId, snippets, matches);
    if (matches) {
      const substring = matches.map((match) => match.replace(/<\/?b>/g, '')).join(' ');
      setRequestedInfo({ documentId, substring });
    }
  }, []);

  useEffect(() => {
    search(identifier, searchText);
  },[ search, identifier, searchText ]);

  useEffect(() => {
    onSearchResults(results, summary);
  },[results,summary]);

  return (
    <Box>
      <Flex direction="row">
        <Box flex="1 1 0" width={"30%"}>
          {/* <Flex p={2} direction="column">
            <InputGroup>
              <InputLeftElement pointerEvents="none">
                <Search2Icon color="gray.300" />
              </InputLeftElement>
              <Input
                type="tel"
                placeholder="Search"
                value={searchText}
                onChange={handleSearchChange}
                disabled={busy}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    search(identifier, searchText);
                  }
                }}
              />
            </InputGroup>
          </Flex> */}
          {busy ? (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', padding: '1rem' }}>
              <Spinner size="lg" style={{ marginBottom: '1rem' }} />
              Searching
            </div>
          ) : null}
          
          {error && <Box>Error fetching results</Box>}
          {results?.length ? (
            <div>
              <Box>
              <Heading style={{ margin: '2rem' }}>
                Summary
              </Heading>
              {summary && busy === false && <Box>{summary.summaryWithMetadata ? summary.summaryWithMetadata.summary: summary.summaryText}</Box>}
              <Accordion allowToggle>
                  <AccordionItem>
                    <h2>
                      <AccordionButton>
                        <Box flex="1" textAlign="left">
                          References
                        </Box>
                        <AccordionIcon />
                      </AccordionButton>
                      <AccordionPanel pb={4}>
                      <TableContainer>
                        <Table variant="simple" size="sm">
                          <Thead>
                            <Tr>
                              <Td width="1%"></Td>
                              {/* <Td>Snippet</Td> */}
                            </Tr>
                          </Thead>
                          <Tbody>
                            {summary.summaryWithMetadata?.references.map((citation: any) => (
                              <Tr key={citation.title}>
                                <Td>
                                  {citation.title}
                                </Td>
                                <style type="text/css">
                                  {`.searchglass-snippet-evidence b {
                                    background-color: yellow;
                                  }`}
                                </style>
                                {/* <Td className="searchglass-snippet-evidence" wordBreak="break-word" whiteSpace="normal" cursor="pointer" onClick={() => requestInfo(result.id, result.snippets)}>
                                  <span dangerouslySetInnerHTML={{ __html: result.snippets }} />
                                </Td> */}
                              </Tr>
                            ))}
                          </Tbody>
                        </Table>
                      </TableContainer>
                      </AccordionPanel>
                    </h2>
                  </AccordionItem>
                </Accordion>
              </Box>
              <Heading style={{ margin: '2rem' }}>
                Results
              </Heading>
              <TableContainer>
                <Table variant="simple" size="sm">
                  <Thead>
                    <Tr>
                      <Td width="1%">Document</Td>
                      <Td>Snippet</Td>
                    </Tr>
                  </Thead>
                  <Tbody>
                    {results.map((result: any) => (
                      <Tr key={result.snippets}>
                        <Td>
                          {result.doc_url.split('/').pop()}
                        </Td>
                        <style type="text/css">
                          {`.searchglass-snippet-evidence b {
                            background-color: yellow;
                          }`}
                        </style>
                        <Td className="searchglass-snippet-evidence" wordBreak="break-word" whiteSpace="normal" cursor="pointer" onClick={() => requestInfo(result.id, result.snippets)}>
                          <span dangerouslySetInnerHTML={{ __html: result.snippets }} />
                        </Td>
                      </Tr>
                    ))}
                  </Tbody>
                </Table>
              </TableContainer>
            </div>
          ) : null}
        </Box>
        <Box flex="1 1 0" width={"70%"}>
          {requestedInfo && (
            <EvidenceViewer identifier={requestedInfo.documentId} substring={requestedInfo.substring} />
          )}
        </Box>
      </Flex>
    </Box>
  );
}

export default DocsSearchContainer;
