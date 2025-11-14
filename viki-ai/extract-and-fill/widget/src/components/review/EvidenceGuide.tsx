import React, { ChangeEvent, useEffect, useState } from "react";
import {
  Grid,
  Center,
  Select,
  ButtonProps,
  Text,
  Button,
  ChakraProvider,
  Box,
  HStack
} from "@chakra-ui/react";
import {
    Pagination,
    usePagination,
    PaginationNext,
    PaginationPage,
    PaginationPrevious,
    PaginationContainer,
    PaginationPageGroup,
    PaginationSeparator,
  } from "@ajna/pagination";

export const EvidenceGuide = (props:{evidences:Array<any>, onPageNumberChange?:(pageNumber: number)=>void}) => {
    

    const {
        currentPage,
        setCurrentPage,
        pagesCount,
        pages
      } = usePagination({
        pagesCount: props.evidences?.length || 0,
        initialState: { currentPage: 1 },
      });

      useEffect(() => {
        props.onPageNumberChange?.(currentPage);
      }, [currentPage,props.evidences]);

    return (
       props.evidences  && <>
                <Pagination
                    pagesCount={pagesCount}
                    currentPage={currentPage}
                    onPageChange={setCurrentPage}
                >
                    <PaginationContainer
                        align="center"
                        justify="space-between"
                        p={4}
                        w="full"
                    >
                    <PaginationPrevious
                        _hover={{
                            bg: "yellow.400"
                            }}
                        bg="yellow.300"
                    >Previous</PaginationPrevious>
                    <PaginationPageGroup
                        isInline
                        align="center"
                        separator={
                          <PaginationSeparator
                            bg="blue.300"
                            fontSize="sm"
                            w={7}
                            jumpSize={11}
                          />
                        }
                    >
                        <Box width={"5px"}></Box>
                        {/* {props.evidences?.map((evidence: any, index:number) => (
                        <PaginationPage 
                            w={7}
                            bg="red.300"
                            key={`pagination_page_${evidence?.sentence_id}`} 
                            page={index} 
                            fontSize="sm"
                            _hover={{
                                bg: "green.300"
                            }}
                            _current={{
                                bg: "green.300",
                                fontSize: "sm",
                                w: 7
                            }}
                        />
                        ))} */}
                    </PaginationPageGroup>
                    <PaginationNext
                        _hover={{
                            bg: "yellow.400"
                          }}
                        bg="yellow.300"
                    >Next</PaginationNext>
                    </PaginationContainer>
                </Pagination>
            
                {(props.evidences && props.evidences.length > 0) && 
                <>
                <HStack>
                    <Box>
                        {`Highlighting Citation: [${currentPage}] of [${props.evidences.length}]`}
                    </Box>
                </HStack>
                <HStack>
                    <Box>
                        {`Confidence Score: ${(props.evidences[currentPage-1]?.distance*100).toFixed(2)} %`}
                    </Box>
                </HStack>
                </>
                }
                {(props.evidences && props.evidences.length === 0 ) && <Box>{`Fetching citations..`}</Box>}
        </>
    )
}