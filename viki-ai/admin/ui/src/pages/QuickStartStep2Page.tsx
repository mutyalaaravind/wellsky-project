import { 
  Box, 
  VStack, 
  Text, 
  Button, 
  Card,
  CardHeader,
  CardBody,
  Heading,
  SimpleGrid,
  HStack,
  Spinner,
  Alert,
  AlertIcon
} from '@chakra-ui/react'
import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { configService } from '../services/configService'
import { getAuthToken } from '../utils/auth'

interface Template {
  id: string
  app_id: string
  scope: string
  key: string
  name: string
  description: string
  labels: string[]
}

const QuickStartStep2Page: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [selectedTemplate, setSelectedTemplate] = useState<string>('')
  const [templates, setTemplates] = useState<Template[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Validate required parameters from Step 1
  useEffect(() => {
    const businessUnit = searchParams.get('businessUnit')
    const solutionId = searchParams.get('solutionId')
    const name = searchParams.get('name')
    const appId = searchParams.get('appId')

    if (!businessUnit || !solutionId || !name || !appId) {
      // Missing required parameters, redirect back to Step 1
      navigate('/quick-start', { replace: true })
      return
    }
  }, [searchParams, navigate])

  // Fetch templates from Admin API
  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        setIsLoading(true)
        setError(null)
        
        // Get the Admin API base URL from config
        const adminApiUrl = await configService.getAdminApiUrl()
        const token = getAuthToken()
        const response = await fetch(`${adminApiUrl}/api/v1/templates`, {
          headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` }),
          },
        })
        
        if (!response.ok) {
          throw new Error(`Failed to fetch templates: ${response.status} ${response.statusText}`)
        }
        
        const data = await response.json()
        
        if (data.success) {
          setTemplates(data.data)
        } else {
          throw new Error(data.message || 'Failed to fetch templates')
        }
        
      } catch (err) {
        console.error('Error fetching templates:', err)
        setError(err instanceof Error ? err.message : 'Failed to load templates')
      } finally {
        setIsLoading(false)
      }
    }

    fetchTemplates()
  }, [])

  const handleTemplateSelect = (templateId: string) => {
    setSelectedTemplate(templateId)
  }

  const handleNext = () => {
    if (selectedTemplate) {
      // Navigate to Step 3 with all previous data plus selected template
      const params = new URLSearchParams(searchParams)
      params.set('template', selectedTemplate)
      navigate(`/quick-start/step-3?${params.toString()}`)
    }
  }

  const handleBack = () => {
    navigate('/quick-start')
  }

  return (
    <Box maxW="1200px" mx="auto" p={6}>
      <Card>
        <CardHeader>
          <Heading size="lg" color="gray.800">
            Step 2: Choose a Template
          </Heading>
          <Text color="gray.600" mt={2}>
            Select a template that best matches your extraction needs. You can customize it further in the next steps.
          </Text>
        </CardHeader>
        
        <CardBody>
          <VStack spacing={6} align="stretch">
            {isLoading && (
              <VStack spacing={4} py={8}>
                <Spinner size="lg" color="blue.500" />
                <Text color="gray.600">Loading templates...</Text>
              </VStack>
            )}

            {error && (
              <Alert status="error">
                <AlertIcon />
                {error}
              </Alert>
            )}

            {!isLoading && !error && templates.length === 0 && (
              <Alert status="warning">
                <AlertIcon />
                No templates available. Please check your configuration.
              </Alert>
            )}

            {!isLoading && !error && templates.length > 0 && (
              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                {templates.map(template => (
                  <Card
                    key={template.id}
                    variant={selectedTemplate === template.id ? 'filled' : 'outline'}
                    cursor="pointer"
                    onClick={() => handleTemplateSelect(template.id)}
                    _hover={{ 
                      shadow: 'md',
                      borderColor: selectedTemplate === template.id ? 'blue.500' : 'blue.200'
                    }}
                    borderColor={selectedTemplate === template.id ? 'blue.500' : 'gray.200'}
                    borderWidth="2px"
                    bg={selectedTemplate === template.id ? 'blue.50' : 'white'}
                  >
                    <CardBody>
                      <VStack align="start" spacing={3}>
                        <Heading size="md" color="gray.800">
                          {template.name}
                        </Heading>
                        <Text fontSize="sm" color="gray.600" lineHeight="1.5">
                          {template.description}
                        </Text>
                        <Text fontSize="xs" color="blue.600" fontWeight="medium" textTransform="uppercase">
                          {template.scope}
                        </Text>
                      </VStack>
                    </CardBody>
                  </Card>
                ))}
              </SimpleGrid>
            )}

            <HStack justify="space-between" pt={4}>
              <Button
                variant="outline"
                size="lg"
                onClick={handleBack}
              >
                Back
              </Button>
              
              <Button
                colorScheme="blue"
                size="lg"
                onClick={handleNext}
                isDisabled={!selectedTemplate || isLoading}
                isLoading={isLoading}
              >
                Next Step
              </Button>
            </HStack>
          </VStack>
        </CardBody>
      </Card>
    </Box>
  )
}

export default QuickStartStep2Page