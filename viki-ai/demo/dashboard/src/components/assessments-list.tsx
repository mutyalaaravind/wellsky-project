import { memo, useEffect, useState } from "react";
import { Button } from "antd";
import { createColumnHelper } from "@tanstack/react-table";
import { Box, VStack } from "@chakra-ui/react";
import { DataTable } from "../components/dataTable";
import { useNavigate } from "react-router-dom";

type Form = {
    formInstanceId: string;
    formTemplateId: string;
    formName: string;
}

const randomFormsData:Array<Form> = [
    {formInstanceId:"1",formTemplateId:"MEDICATION_FORM",formName:"Start of Care Assessment 1"},
    {formInstanceId:"2",formTemplateId:"COGNITIVE_FORM",formName:"Start of Care Assessment 2"}

]

export const Assessments = () => {
    const router = useNavigate();
    const columnHelper = createColumnHelper<Form>();
    
    const columns = [
        columnHelper.accessor("formInstanceId", {
            cell: (info:any) => info.getValue(),
            header: "Form Instance Id"
            }),
        columnHelper.accessor("formTemplateId", {
        cell: (info:any) => info.getValue(),
        header: "Form Template Id"
        }),
        columnHelper.accessor("formName", {
        cell: (info:any) => info.getValue(),
        header: "Form Name"
        }),
        columnHelper.accessor("formInstanceId", {
        cell: (info:any) => <>
                <Button onClick={()=>{router(`/assessment?formInstanceId=${info.getValue()}`)}}>View Form</Button>
            </>,
        header: ""
        })
    ];

    return (
        <VStack w={"100%"}>
            <Box padding={5}>
                <DataTable columns={columns} data={randomFormsData} />
            </Box>
        </VStack>
    )

    
}