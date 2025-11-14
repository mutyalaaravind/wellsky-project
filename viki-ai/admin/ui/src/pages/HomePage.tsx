import { Box, VStack, Text, Button, Center } from '@chakra-ui/react'
import { useNavigate } from 'react-router-dom'

const HomePage: React.FC = () => {
  const navigate = useNavigate()

  const handleGetStarted = () => {
    navigate('/quick-start')
  }

  return (
    <Center h="full" w="full">
      <Box
        bg="white"
        p={8}
        borderRadius="lg"
        boxShadow="md"
        textAlign="center"
        maxW="400px"
        border="1px"
        borderColor="gray.200"
      >
        <VStack spacing={4}>
          <Text fontSize="2xl" fontWeight="bold" color="gray.800">
            Get Started!
          </Text>
          
          <Text fontSize="md" color="gray.600" lineHeight="1.6">
            Build your extraction pipeline and get extracting in minutes
          </Text>
          
          <Button
            colorScheme="blue"
            size="lg"
            onClick={handleGetStarted}
            mt={4}
            borderRadius="full"
          >
            Get Started
          </Button>
        </VStack>
      </Box>
    </Center>
  )
}

export default HomePage