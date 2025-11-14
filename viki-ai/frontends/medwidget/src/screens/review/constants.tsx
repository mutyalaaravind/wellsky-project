import { Flex, Box, Text } from "@chakra-ui/react";
import Documents02LargeIcon from "./Documents02LargeIcon";
import Medications02LargeIcon from "./Medications02LargeIcon";
import { ReactNode } from "react";

export const emptyContent = ({
  title = "No data found",
  icon = <Documents02LargeIcon />,
  message = "There were no records found",
}: {
  title?: ReactNode;
  icon?: ReactNode;
  message?: ReactNode;
}) => {
  return (
    <Flex gap={1} direction="column" justifyItems="center" alignItems="center">
      <Box p="0.5">{icon}</Box>
      <Box>
        <Text
          color="bigStone.400"
          fontSize="14px"
          fontWeight={500}
          lineHeight="21px"
        >
          {title}
        </Text>
      </Box>
      <Box>
        <Text
          color="bigStone.900"
          fontSize="12px"
          fontWeight={400}
          lineHeight="18px"
        >
          {message}
        </Text>
      </Box>
    </Flex>
  );
};

export const documentNoDataContent = (
  message: ReactNode = "Upload relevant documents in Episode Manager or directly in the medication profile.",
) => {
  return emptyContent({
    title: "There were no documents found",
    icon: <Documents02LargeIcon />,
    message,
  });
};

export const medicationNoDataContent = (
  message: ReactNode = "Select a document to extract medications",
) => {
  return emptyContent({
    title: "There are no medications listed",
    icon: <Medications02LargeIcon />,
    message,
  });
};
