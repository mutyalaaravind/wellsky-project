import { Box, Center, HStack } from "@chakra-ui/react";
import { AppCard } from "./card";

export const Apps = () => {
    return (
        <HStack w={"100%"} spacing='24px' align={"center"}>
            <Box w='400px' h='100px' textAlign={"center"}>
                <AppCard title={"Oasis-E forms"} url={"/patients/"} />
            </Box>
            <Box w='400px' h='100px'>
                <AppCard title={"Medical Coding"}/>
            </Box>
        </HStack>
    );
}