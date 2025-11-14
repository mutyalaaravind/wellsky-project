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
  HStack,
  VStack
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
import Icon from "@ant-design/icons/lib/components/Icon";
import { StepBackwardOutlined, StepForwardOutlined } from "@ant-design/icons";

export const EvidenceGuide = (props:{evidences:Array<any>, onPageNumberChange?:(pageNumber: number)=>void}) => {
    
    const [evidences,setEvidences] = useState<Array<any>>(props.evidences || []);
    const [currentPage, setCurrentPage] = useState<number>(0);

    useEffect(() => {
        setEvidences(props.evidences || []);
        props.onPageNumberChange?.(currentPage);
    }, [currentPage, props.evidences]);

    useEffect(() => {
        //setCurrentPage(1);
    },[evidences])

    return (
        <>  
            {(evidences && evidences.length > 0) && 
                <>
                <HStack>
                    <Box>
                        {currentPage > 1 && <StepBackwardOutlined  onClick={()=>{props.onPageNumberChange?.(currentPage-1);setCurrentPage(currentPage-1)}}/>}
                    </Box>
                    <Box>
                        <HStack align={"center"}>
                            <Box color={"red"}>
                                {/* {`[${currentPage}] of [${evidences.length}] Confidence Score: ${(evidences[currentPage-1]?.distance*100).toFixed(2)} %`} */}
                                {`Highlight Evidence: [${currentPage}] of [${evidences.length}]`}
                            </Box>
                        </HStack>
                    </Box>
                    <Box>
                        {currentPage < evidences.length && <StepForwardOutlined onClick={()=>{props.onPageNumberChange?.(currentPage+1);setCurrentPage(currentPage+1)}} />}
                    </Box>
                </HStack>
                </>
            }
            {(evidences && evidences.length === 0 ) && <Box>{`Fetching citations..`}</Box>}
        </>
    )
}