import { 
  Box, 
  VStack, 
  Text, 
  Button, 
  Card,
  CardHeader,
  CardBody,
  Heading,
  HStack,
  Divider,
  Badge,
  Code,
  Table,
  Tbody,
  Tr,
  Td,
  TableContainer,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Textarea,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  useToast,
} from '@chakra-ui/react'
import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useLLMModels } from '../hooks/useLLMModels'
import { onboardingService, OnboardSaveRequest } from '../services/onboardingService'

interface ReviewData {
  billingTokens: number
  entitySchema: object
  extractionPrompt: string
  preferredModel: string
  gsuCount: number
  throughputSettings: {
    documentsPerMinute: number
    tokensPerDocument: number
  }
}

const QuickStartStep4Page: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [documentsPerMinute] = useState<number>(10)
  const [extractionPrompt, setExtractionPrompt] = useState<string>('')
  const [isCompletingSetup, setIsCompletingSetup] = useState<boolean>(false)
  const [setupError, setSetupError] = useState<string>('')
  const { models, loading: modelsLoading } = useLLMModels()
  const toast = useToast()

  // Validate required parameters from previous steps
  useEffect(() => {
    const businessUnit = searchParams.get('businessUnit')
    const solutionId = searchParams.get('solutionId')
    const name = searchParams.get('name')
    const appId = searchParams.get('appId')
    const template = searchParams.get('template')
    const metaPrompt = searchParams.get('metaPrompt')

    if (!businessUnit || !solutionId || !name || !appId || !template || !metaPrompt) {
      // Missing required parameters, redirect back to Step 1
      navigate('/quick-start', { replace: true })
      return
    }
  }, [searchParams, navigate])

  // Extract data from previous steps
  const stepData = {
    businessUnit: searchParams.get('businessUnit') || '',
    solutionId: searchParams.get('solutionId') || '',
    appId: searchParams.get('appId') || '',
    name: searchParams.get('name') || '',
    description: searchParams.get('description') || '',
    template: searchParams.get('template') || '',
    metaPrompt: searchParams.get('metaPrompt') || '',
    sampleFileName: searchParams.get('sampleFileName') || ''
  }

  // Get generated config from API
  const getGeneratedConfig = () => {
    const configParam = searchParams.get('generatedConfig')
    if (configParam) {
      try {
        return JSON.parse(configParam)
      } catch (error) {
        console.error('Error parsing generated config:', error)
        return null
      }
    }
    return null
  }

  const generatedConfig = getGeneratedConfig()

  // Initialize extraction prompt from generated config when available
  useEffect(() => {
    if (generatedConfig?.extractionPrompt && !extractionPrompt) {
      // Convert \n escape sequences to actual line breaks for proper formatting
      const formattedPrompt = generatedConfig.extractionPrompt.replace(/\\n/g, '\n')
      setExtractionPrompt(formattedPrompt)
    }
  }, [generatedConfig, extractionPrompt])

  // Calculate review data based on configuration
  const calculateReviewData = (): ReviewData => {
    // Use generated config from API if available, otherwise fall back to mock data
    if (generatedConfig) {
      return {
        billingTokens: 0, // Not used anymore since we removed billing section
        entitySchema: generatedConfig.entitySchema,
        extractionPrompt: extractionPrompt || '',
        preferredModel: generatedConfig.preferredModel,
        gsuCount: generatedConfig.gsuCount,
        throughputSettings: {
          documentsPerMinute: documentsPerMinute,
          tokensPerDocument: generatedConfig.tokensPerDocument
        }
      }
    }

    // Fallback mock data if no generated config
    const avgTokensPerDocument = 2500
    const billingTokens = documentsPerMinute * avgTokensPerDocument * 60 * 24 * 30 // Monthly tokens
    
    // Generate sample entity schema based on meta prompt
    const entitySchema = {
      type: "object",
      properties: {
        patient_name: {
          type: "string",
          description: "Full name of the patient"
        },
        date_of_birth: {
          type: "string",
          format: "date",
          description: "Patient's date of birth"
        },
        insurance_id: {
          type: "string",
          description: "Insurance identification number"
        },
        diagnosis_codes: {
          type: "array",
          items: {
            type: "string"
          },
          description: "List of ICD-10 diagnosis codes"
        },
        medications: {
          type: "array",
          items: {
            type: "object",
            properties: {
              name: { type: "string" },
              dosage: { type: "string" },
              frequency: { type: "string" }
            }
          },
          description: "List of prescribed medications"
        }
      },
      required: ["patient_name", "date_of_birth"]
    }

    // Get highest priority model from registered LLM models
    const getPreferredModel = () => {
      if (modelsLoading || models.length === 0) {
        return 'Loading...'
      }
      
      // Filter active models and find the one with highest priority (lowest priority number)
      const activeModels = models.filter(model => model.active)
      if (activeModels.length === 0) {
        return 'No active models'
      }
      
      const highestPriorityModel = activeModels.reduce((highest, current) => 
        current.priority < highest.priority ? current : highest
      )
      
      return highestPriorityModel.name
    }
    
    const preferredModel = getPreferredModel()
    
    // Calculate GSUs needed based on actual throughput requirements
    const calculateGSUs = () => {
      if (modelsLoading || models.length === 0) {
        return 0
      }
      
      // Find the selected model object to get its throughput specs
      const activeModels = models.filter(model => model.active)
      if (activeModels.length === 0) {
        return 0
      }
      
      const selectedModel = activeModels.reduce((highest, current) => 
        current.priority < highest.priority ? current : highest
      )
      
      // Calculate tokens per second from documents per minute
      const tokensPerSecond = (documentsPerMinute * avgTokensPerDocument) / 60
      
      // Calculate virtual GSUs needed based on model's per_second_throughput_per_gsu
      const virtualGSUs = tokensPerSecond / selectedModel.per_second_throughput_per_gsu
      
      // Round up to next whole GSU
      return Math.ceil(virtualGSUs)
    }
    
    const gsuCount = calculateGSUs()

    return {
      billingTokens,
      entitySchema,
      extractionPrompt: extractionPrompt || 'No extraction prompt available',
      preferredModel,
      gsuCount,
      throughputSettings: {
        documentsPerMinute: documentsPerMinute,
        tokensPerDocument: avgTokensPerDocument
      }
    }
  }

  const reviewData = calculateReviewData()

  const handleComplete = async () => {
    setIsCompletingSetup(true)
    setSetupError('')

    try {
      // Get the app_id from generated config or stepData
      const appId = generatedConfig?.configuration?.appId || stepData.appId
      
      if (!appId) {
        throw new Error('App ID is required to complete setup')
      }

      // Prepare the save request
      const saveRequest: OnboardSaveRequest = {
        app_id: appId,
        business_unit: stepData.businessUnit,
        solution_code: stepData.solutionId,
        app_name: stepData.name,
        app_description: stepData.description,
        entity_schema: reviewData.entitySchema,
        extraction_prompt: extractionPrompt,
        pipeline_template: stepData.template,
      }

      console.log('Saving onboarding configuration:', saveRequest)

      // Call the save API
      const response = await onboardingService.saveOnboardingConfig(saveRequest)

      if (response.success) {
        // Show success toast
        toast({
          title: 'Setup Complete!',
          description: response.message,
          status: 'success',
          duration: 5000,
          isClosable: true,
        })

        // Navigate to app detail page for the newly created app
        navigate(`/apps/${appId}`)
      } else {
        throw new Error(response.message || 'Failed to complete setup')
      }
    } catch (error) {
      console.error('Error completing setup:', error)
      const errorMessage = error instanceof Error ? error.message : 'An unexpected error occurred'
      setSetupError(errorMessage)
      
      toast({
        title: 'Setup Failed',
        description: errorMessage,
        status: 'error',
        duration: 8000,
        isClosable: true,
      })
    } finally {
      setIsCompletingSetup(false)
    }
  }

  const handleBack = () => {
    navigate(`/quick-start/step-3?${searchParams.toString()}`)
  }

  return (
    <Box maxW="1000px" mx="auto" p={6}>
      <Card>
        <CardHeader>
          <Heading size="lg" color="gray.800">
            Step 4: Review Configuration
          </Heading>
          <Text color="gray.600" mt={2}>
            Review your pipeline configuration details before completing setup.
          </Text>
        </CardHeader>
        
        <CardBody>
          <VStack spacing={6} align="stretch">
            
            {/* Configuration Summary */}
            <Card variant="outline">
              <CardHeader pb={2}>
                <Heading size="md">Pipeline Configuration</Heading>
              </CardHeader>
              <CardBody pt={2}>
                <TableContainer>
                  <Table size="sm" variant="simple">
                    <Tbody>
                      <Tr>
                        <Td fontWeight="medium" width="200px">Business Unit:</Td>
                        <Td>{stepData.businessUnit.toUpperCase()}</Td>
                      </Tr>
                      <Tr>
                        <Td fontWeight="medium">Solution ID:</Td>
                        <Td>{stepData.solutionId.toUpperCase()}</Td>
                      </Tr>
                      <Tr>
                        <Td fontWeight="medium">App ID:</Td>
                        <Td>{generatedConfig?.configuration?.appId || stepData.appId}</Td>
                      </Tr>
                      <Tr>
                        <Td fontWeight="medium">Pipeline Name:</Td>
                        <Td>{stepData.name}</Td>
                      </Tr>
                      <Tr>
                        <Td fontWeight="medium">Template:</Td>
                        <Td>
                          <Badge colorScheme="blue" variant="subtle">
                            {stepData.template}
                          </Badge>
                        </Td>
                      </Tr>
                      <Tr>
                        <Td fontWeight="medium">Sample File:</Td>
                        <Td>{stepData.sampleFileName || 'None uploaded'}</Td>
                      </Tr>
                    </Tbody>
                  </Table>
                </TableContainer>
              </CardBody>
            </Card>


            {/* Extraction Configuration Tabs */}
            <Card variant="outline">
              <CardHeader pb={2}>
                <Heading size="md">Extraction Configuration</Heading>
              </CardHeader>
              <CardBody pt={2}>
                <Tabs colorScheme="blue" variant="enclosed">
                  <TabList>
                    <Tab>Extracted Data</Tab>
                    <Tab>Prompt</Tab>
                    <Tab>Schema</Tab>
                  </TabList>
                  
                  <TabPanels>
                    {/* Extracted Data Tab */}
                    <TabPanel px={0} py={4}>
                      {generatedConfig?.extractedEntity ? (
                        <VStack spacing={3} align="stretch">
                          <Text color="gray.600" fontSize="sm">
                            This is the data extracted from your sample document using the generated prompt and schema.
                          </Text>
                          <Code 
                            p={4} 
                            borderRadius="md" 
                            display="block" 
                            whiteSpace="pre-wrap"
                            fontSize="sm"
                            bg="gray.50"
                            overflowX="auto"
                            minH="300px"
                          >
                            {JSON.stringify(generatedConfig.extractedEntity, null, 2)}
                          </Code>
                        </VStack>
                      ) : (
                        <Box 
                          p={4} 
                          borderRadius="md" 
                          bg="gray.50"
                          minH="200px"
                          display="flex"
                          alignItems="center"
                          justifyContent="center"
                        >
                          <Text color="gray.500" fontSize="md">
                            Extracted data will be displayed here after running the extraction prompt on your sample document.
                          </Text>
                        </Box>
                      )}
                    </TabPanel>
                    
                    {/* Prompt Tab */}
                    <TabPanel px={0} py={4}>
                      <VStack spacing={3} align="stretch">
                        <Text color="gray.600" fontSize="sm">
                          Review and refine the generated extraction prompt. This prompt will be used to extract data from similar documents.
                        </Text>
                        <Textarea
                          value={extractionPrompt}
                          onChange={(e) => setExtractionPrompt(e.target.value)}
                          placeholder="Extraction prompt will be generated automatically..."
                          minH="300px"
                          fontSize="sm"
                          fontFamily="mono"
                          resize="vertical"
                        />
                      </VStack>
                    </TabPanel>
                    
                    {/* Schema Tab */}
                    <TabPanel px={0} py={4}>
                      <VStack spacing={3} align="stretch">
                        <Text color="gray.600" fontSize="sm">
                          The JSON Schema defines the structure of data to be extracted from documents.
                        </Text>
                        <Code 
                          p={4} 
                          borderRadius="md" 
                          display="block" 
                          whiteSpace="pre-wrap"
                          fontSize="sm"
                          bg="gray.50"
                          overflowX="auto"
                          minH="300px"
                        >
                          {JSON.stringify(reviewData.entitySchema, null, 2)}
                        </Code>
                      </VStack>
                    </TabPanel>
                  </TabPanels>
                </Tabs>
              </CardBody>
            </Card>


            {/* Error Alert */}
            {setupError && (
              <Alert status="error" borderRadius="md">
                <AlertIcon />
                <Box>
                  <AlertTitle>Setup Failed!</AlertTitle>
                  <AlertDescription>{setupError}</AlertDescription>
                </Box>
              </Alert>
            )}

            <Divider />

            <HStack justify="space-between" pt={4}>
              <Button
                variant="outline"
                size="lg"
                onClick={handleBack}
                isDisabled={isCompletingSetup}
              >
                Back
              </Button>
              
              <Button
                colorScheme="blue"
                size="lg"
                onClick={handleComplete}
                isLoading={isCompletingSetup}
                loadingText="Completing Setup..."
                isDisabled={isCompletingSetup}
              >
                Complete Setup
              </Button>
            </HStack>
          </VStack>
        </CardBody>
      </Card>
    </Box>
  )
}

export default QuickStartStep4Page