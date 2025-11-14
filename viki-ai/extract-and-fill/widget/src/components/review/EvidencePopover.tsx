import { scrollToCustomFormField } from "../../utils/helpers";

import { EvidenceGuide } from "./EvidenceGuide";
import { Box, extendTheme, Popover as ChakraPopover, PopoverTrigger, PopoverContent, PopoverHeader, PopoverArrow, PopoverCloseButton, PopoverBody } from "@chakra-ui/react";
import ExclamationCircleOutlined from "@ant-design/icons/lib/icons/ExclamationCircleOutlined";
import React from "react";
import { Env } from "../../types";


type EvidencePopoverProps = {
    field: any;
    mount?: string;
    env: Env | null;
    transcriptId?: string | null | undefined;
    transcriptText?: string | null | undefined;
    extractedText?: string | null | undefined;
    onEvidenceReceived: (evidence: any) => void;

}


export const EvidencePopover = (props:EvidencePopoverProps) => {

    const [evidences, setEvidences] = React.useState<Array<any>>([]);

    return <>
    <Box zIndex="popover">
    <ChakraPopover>
      <PopoverTrigger>
        <ExclamationCircleOutlined onClick={ () => scrollToCustomFormField(props.mount || "", props.field, props.env, props.transcriptId || "", props.transcriptText || "", props.extractedText || "", setEvidences)} />
      </PopoverTrigger>
      <PopoverContent maxW={{ base: "75%"  }}>
        <PopoverHeader fontWeight='semibold'>Evidences</PopoverHeader>
        <PopoverArrow bg='green.500' />
        <PopoverCloseButton bg='green.500' />
        <PopoverBody>
          <EvidenceGuide evidences={evidences} onPageNumberChange={(pageNo:number)=>{props.onEvidenceReceived(evidences[pageNo])}}  />
        </PopoverBody>
      </PopoverContent>
    </ChakraPopover>
    </Box>
    </>
  }