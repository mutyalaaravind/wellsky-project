import { Box, Button, HStack, VStack } from "@chakra-ui/react";
import { createColumnHelper } from "@tanstack/react-table";
import { DataTable } from "../dataTable";
import { Spinner } from "@mediwareinc/wellsky-dls-react";

export type Section = {
    sectionName: string;
    sectionId: string;
    extractionStatus: string;
    customFormTemplateName?: string;
}

export const SectionList = (props:{sections: Array<Section>, onFormViewEvent:(sectionId:string)=>void}) => {

    const columnHelper = createColumnHelper<Section>();
    
    const columns = [
        columnHelper.accessor("sectionId", {
            cell: (info:any) => info.getValue().split(".")[0],
            header: "Section Id"
            }),
        columnHelper.accessor("sectionName", {
        cell: (info:any) => info.getValue(),
        header: "Section Name"
        }),
        columnHelper.accessor("extractionStatus", {
        cell: (info:any) => <>{info.getValue() !== "Not Started"  && info.getValue() !== "Completed" &&  info.getValue() !== "Errored" ? <>{info.getValue()} <Spinner /></>:info.getValue() }</>,
        header: "Extraction Status"
        }),
        columnHelper.accessor((row:any) => `${row.sectionId}.${row.extractionStatus}`, {
            header: '',
            id: 'sectionId', //id is required when using accessorFn
            cell:(row:any) => <>{<Button isDisabled={row.getValue().split(".")[1] !== "Completed" ? false:false} onClick={()=>{props.onFormViewEvent(row.getValue().split(".")[0])}}>View Form</Button>}</>
        })
        // columnHelper.accessor("sectionId", {
        // cell: (info:any) => <>
        //         <Button onClick={()=>{props.onFormViewEvent(info.getValue())}}>View Form</Button>
        //     </>,
        // header: ""
        // })
    ];

    return (
        <VStack w={"100%"}>
            <Box borderBlock={"1"}>
                <DataTable columns={columns} data={props.sections} />
            </Box>
        </VStack>
    )
};