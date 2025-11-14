import { Box, Text, VStack } from '@chakra-ui/react'

const TestingPage: React.FC = () => {
  return (
    <Box>
      <VStack spacing={4} align="start">
        <Text fontSize="lg" color="gray.600">
          Manage testing and experimentation workflows.
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
            Testing management coming soon...
          </Text>
        </Box>
      </VStack>
    </Box>
  )
}

export default TestingPage