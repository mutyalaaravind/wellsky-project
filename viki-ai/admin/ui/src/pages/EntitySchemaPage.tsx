import { Box, Text, VStack } from '@chakra-ui/react'

const EntitySchemaPage: React.FC = () => {
  return (
    <Box>
      <VStack spacing={4} align="start">
        <Text fontSize="lg" color="gray.600">
          Manage entity schemas for your extraction pipelines.
        </Text>
        
        <Box
          w="full"
          h="400px"
          bg="white"
          borderRadius="lg"
          boxShadow="sm"
          p={6}
          display="flex"
          alignItems="center"
          justifyContent="center"
          border="1px"
          borderColor="gray.200"
        >
          <Text color="gray.400" fontSize="lg">
            Entity Schema management coming soon...
          </Text>
        </Box>
      </VStack>
    </Box>
  )
}

export default EntitySchemaPage