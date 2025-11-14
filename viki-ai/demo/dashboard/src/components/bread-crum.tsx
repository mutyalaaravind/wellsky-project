import { Box, HStack, VStack } from "@chakra-ui/react"
import { LinkButton } from "@mediwareinc/wellsky-dls-react"
import { useNavigate } from "react-router-dom"
import * as ts from "typescript";

export type BreadCrumType = {
    moduleName: string;
    linkUrl: string;
}

export type BreadCrumProps = {
    breadCrums: Array<BreadCrumType>;
}

const getPatientName = (patientId: string) => {
    const patients = JSON.parse(localStorage.getItem('patients') || '{}');
    console.log("getPatientName", patients, patientId);
    const selectedPatient = patients.find((patient: any) => patient.id === patientId);
    if (selectedPatient) {
        return `${selectedPatient.firstName} ${selectedPatient.lastName}`;
    }
    else {
        return 'unknown';
    }
}

export const BreadCrum = ({ breadCrums }: BreadCrumProps) => {
    const router = useNavigate();
    const transformBreadCrumb = (breadCrumb: BreadCrumType) => {
        if (breadCrumb.moduleName.includes('getPatientName')) {
            const patientId = breadCrumb.moduleName.replace('getPatientName(', '').replace(')', '');
            return { moduleName: getPatientName(patientId), linkUrl: breadCrumb.linkUrl }
        }
        return breadCrumb;
    }
    return (
        <>
            <HStack paddingLeft={5}>
                {breadCrums.map((breadCrumb: BreadCrumType, index: number) => {
                    const transformedBreadCrumb = transformBreadCrumb(breadCrumb);
                    return (
                        // <VStack alignContent={"left"} >
                        <Box alignContent={"left"} key={breadCrumb.moduleName}>
                            {index !== 0 ? (
                                <>
                                    <Box display="inline">{'>>'}</Box>
                                    <LinkButton onClick={() => { router(transformedBreadCrumb.linkUrl) }}>{transformedBreadCrumb.moduleName}</LinkButton>
                                </>
                            ) : (
                                <LinkButton onClick={() => { router(transformedBreadCrumb.linkUrl) }}>{transformedBreadCrumb.moduleName}</LinkButton>
                            )}
                        </Box>
                        // </VStack>
                    )
                })
                }
            </HStack>
        </>
    )
}
