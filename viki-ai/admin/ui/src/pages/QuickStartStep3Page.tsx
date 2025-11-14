import { 
  Box, 
  VStack, 
  Text, 
  Button, 
  FormControl, 
  FormLabel, 
  Input,
  Textarea,
  Card,
  CardHeader,
  CardBody,
  Heading,
  HStack,
  FormHelperText,
  useToast
} from '@chakra-ui/react'
import { useState, useRef, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { configService } from '../services/configService'
import OnboardProgressModal from '../components/OnboardProgressModal'
import type { OnboardProgress } from '../hooks/useOnboardProgress'
import { getAuthToken } from '../utils/auth'

interface Step3FormData {
  sampleFile: File | null
  metaPrompt: string
}

interface GenerateResponse {
  success: boolean
  message: string
  data: any
  job_id?: string
}

const QuickStartStep3Page: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const toast = useToast()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [formData, setFormData] = useState<Step3FormData>({
    sampleFile: null,
    metaPrompt: ''
  })

  // Progress modal state
  const [isProgressModalOpen, setIsProgressModalOpen] = useState(false)
  const [currentJobId, setCurrentJobId] = useState<string | null>(null)

  // Validate required parameters from previous steps
  useEffect(() => {
    const businessUnit = searchParams.get('businessUnit')
    const solutionId = searchParams.get('solutionId')
    const name = searchParams.get('name')
    const appId = searchParams.get('appId')
    const template = searchParams.get('template')

    if (!businessUnit || !solutionId || !name || !appId || !template) {
      // Missing required parameters, redirect back to Step 1
      navigate('/quick-start', { replace: true })
      return
    }
  }, [searchParams, navigate])

  // Supported file types - matches backend PDF converter supported formats
  const supportedFormats = {
    'application/pdf': 'PDF',
    'image/jpeg': 'JPEG',
    'image/jpg': 'JPG',
    'image/png': 'PNG', 
    'image/tiff': 'TIFF',
    'image/tif': 'TIF',
    'image/bmp': 'BMP',
    'image/gif': 'GIF',
    'image/webp': 'WEBP'
  }

  const allowedTypes = Object.keys(supportedFormats)

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      // Validate file type
      if (!allowedTypes.includes(file.type)) {
        const formatsList = Object.values(supportedFormats).join(', ')
        toast({
          title: 'Invalid file type',
          description: `Please upload a supported file format: ${formatsList}`,
          status: 'error',
          duration: 5000,
          isClosable: true,
        })
        return
      }

      // Validate file size (max 10MB)
      const maxSize = 10 * 1024 * 1024; // 10MB in bytes
      if (file.size > maxSize) {
        toast({
          title: 'File too large',
          description: 'Please upload a file smaller than 10MB.',
          status: 'error',
          duration: 5000,
          isClosable: true,
        })
        return
      }

      setFormData(prev => ({ ...prev, sampleFile: file }))
    }
  }

  const handleRemoveFile = () => {
    setFormData(prev => ({ ...prev, sampleFile: null }))
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleMetaPromptChange = (value: string) => {
    setFormData(prev => ({ ...prev, metaPrompt: value }))
  }

  const handleNext = async () => {
    if (!formData.sampleFile) {
      toast({
        title: 'Missing file',
        description: 'Please upload a sample document before proceeding.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
      return
    }

    // Generate job ID on frontend: {app_id}:{random_guid}
    const solutionId = searchParams.get('solutionId') || 'unknown'
    const randomGuid = crypto.randomUUID()
    const jobId = `${solutionId}:${randomGuid}`
    console.log('Generated job ID:', jobId)
    
    // Set job ID and open modal immediately
    setCurrentJobId(jobId)
    setIsProgressModalOpen(true)
    
    try {
      console.log('Starting onboard generation...')
      // Get the admin API base URL from config
      const adminApiUrl = await configService.getAdminApiUrl()
      console.log('Admin API URL:', adminApiUrl)

      // Prepare form data for API call
      const formDataToSend = new FormData()
      formDataToSend.append('businessUnit', searchParams.get('businessUnit') || '')
      formDataToSend.append('solutionId', searchParams.get('solutionId') || '')
      formDataToSend.append('name', searchParams.get('name') || '')
      formDataToSend.append('description', searchParams.get('description') || '')
      formDataToSend.append('template', searchParams.get('template') || '')
      formDataToSend.append('metaPrompt', formData.metaPrompt)
      formDataToSend.append('sampleFile', formData.sampleFile)
      formDataToSend.append('jobId', jobId)  // Pass the predetermined job ID

      console.log('Making API call...')
      // Call the onboard generate API with progress tracking
      const token = getAuthToken()
      const response = await fetch(`${adminApiUrl}/api/v1/onboard/generate-with-progress`, {
        method: 'POST',
        headers: {
          ...(token && { 'Authorization': `Bearer ${token}` }),
        },
        body: formDataToSend
      })

      console.log('Response status:', response.status)
      if (!response.ok) {
        const errorData = await response.json()

        // Handle validation errors with multiple error messages
        if (errorData.detail && typeof errorData.detail === 'object' && errorData.detail.errors) {
          throw new Error(JSON.stringify(errorData.detail))
        }

        throw new Error(errorData.detail || 'Failed to start configuration generation')
      }

      const result: GenerateResponse = await response.json()
      console.log('API Response:', result)
      
      if (result.success && result.data) {
        console.log('Generation completed successfully, navigating to Step 4')
        // Close modal and navigate to Step 4 with the generated data
        setIsProgressModalOpen(false)
        
        const params = new URLSearchParams(searchParams)
        params.set('metaPrompt', formData.metaPrompt)
        params.set('sampleFileName', formData.sampleFile?.name || '')
        params.set('jobId', jobId)
        params.set('appId', result.data.configuration?.appId || 'unknown')
        params.set('generatedConfig', JSON.stringify(result.data))
        
        navigate(`/quick-start/step-4?${params.toString()}`)
      } else {
        throw new Error(result.message || 'Failed to start configuration generation')
      }

    } catch (error) {
      console.error('Error starting onboard generation:', error)
      // Close modal and reset state on error
      setIsProgressModalOpen(false)
      setCurrentJobId(null)

      // Parse error message for better display
      let errorMessage = 'Failed to start configuration generation. Please try again.'

      if (error instanceof Error) {
        try {
          // Try to parse as API validation error response
          const errorData = JSON.parse(error.message)
          if (errorData.errors && Array.isArray(errorData.errors)) {
            errorMessage = `Validation failed:\n• ${errorData.errors.join('\n• ')}`
          } else {
            errorMessage = error.message
          }
        } catch {
          // If parsing fails, use the original error message
          errorMessage = error.message
        }
      }

      toast({
        title: 'Configuration Error',
        description: errorMessage,
        status: 'error',
        duration: 8000,
        isClosable: true,
      })
    }
  }

  const handleProgressComplete = (progress: OnboardProgress) => {
    // When generation is complete, navigate to Step 4 with the generated data
    // The generated data should be included in the progress response
    const params = new URLSearchParams(searchParams)
    params.set('metaPrompt', formData.metaPrompt)
    params.set('sampleFileName', formData.sampleFile?.name || '')
    params.set('jobId', progress.job_id)
    params.set('appId', progress.app_id)
    
    // Close the modal and navigate
    setIsProgressModalOpen(false)
    navigate(`/quick-start/step-4?${params.toString()}`)
  }

  const handleProgressCancel = () => {
    // Reset state when user cancels
    setCurrentJobId(null)
    setIsProgressModalOpen(false)
  }

  const handleBack = () => {
    navigate(`/quick-start/step-2?${searchParams.toString()}`)
  }

  const isFormValid = () => {
    return formData.sampleFile !== null && 
           formData.metaPrompt.trim() !== ''
  }


  return (
    <Box maxW="800px" mx="auto" p={6}>
      <Card>
        <CardHeader>
          <Heading size="lg" color="gray.800">
            Step 3: Configure Extraction
          </Heading>
          <Text color="gray.600" mt={2}>
            Upload a sample document, describe what data to extract, and set your expected processing volume.
          </Text>
        </CardHeader>
        
        <CardBody>
          <VStack spacing={6} align="stretch">
            <FormControl isRequired>
              <FormLabel>Sample Document</FormLabel>
              <VStack align="stretch" spacing={3}>
                <Input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileUpload}
                  accept=".pdf,.jpg,.jpeg,.png,.tiff,.tif,.bmp,.gif,.webp"
                  display="none"
                />
                
                {formData.sampleFile ? (
                  <HStack 
                    p={4} 
                    border="2px solid" 
                    borderColor="green.200" 
                    borderRadius="md"
                    bg="green.50"
                    justify="space-between"
                  >
                    <VStack align="start" spacing={1}>
                      <Text fontWeight="medium" color="green.800">
                        {formData.sampleFile.name}
                      </Text>
                      <Text fontSize="sm" color="green.600">
                        {(formData.sampleFile.size / 1024 / 1024).toFixed(2)} MB
                      </Text>
                    </VStack>
                    <Button 
                      size="sm" 
                      colorScheme="red" 
                      variant="outline"
                      onClick={handleRemoveFile}
                    >
                      Remove
                    </Button>
                  </HStack>
                ) : (
                  <Button
                    onClick={() => fileInputRef.current?.click()}
                    variant="outline"
                    borderStyle="dashed"
                    borderWidth="2px"
                    h="100px"
                    _hover={{ bg: "gray.50" }}
                  >
                    <VStack>
                      <Text>Click to upload sample document</Text>
                      <Text fontSize="sm" color="gray.500">
                        Supported formats: {Object.values(supportedFormats).join(', ')} (max 10MB)
                      </Text>
                    </VStack>
                  </Button>
                )}
              </VStack>
              <FormHelperText>
                Upload a representative sample of the documents you'll be processing. This helps optimize the extraction model.
                <br />
                Supported formats: {Object.values(supportedFormats).join(', ')} • Maximum file size: 10MB
              </FormHelperText>
            </FormControl>

            <FormControl isRequired>
              <FormLabel>Data Extraction Description</FormLabel>
              <Textarea
                placeholder="Describe what specific data you want to extract from your documents. For example: 'Extract patient name, date of birth, insurance ID, diagnosis codes, and medication list from medical forms.'"
                value={formData.metaPrompt}
                onChange={(e) => handleMetaPromptChange(e.target.value)}
                rows={6}
                resize="vertical"
              />
              <FormHelperText>
                Be as specific as possible about the data fields and information you need extracted. This meta prompt guides the AI extraction process.
              </FormHelperText>
            </FormControl>


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
                isDisabled={!isFormValid()}
              >
                Review
              </Button>
            </HStack>
          </VStack>
        </CardBody>
      </Card>

      {/* Progress Modal */}
      <OnboardProgressModal
        isOpen={isProgressModalOpen}
        onClose={() => setIsProgressModalOpen(false)}
        jobId={currentJobId}
        onComplete={handleProgressComplete}
        onCancel={handleProgressCancel}
        title="Generating Configuration"
      />
    </Box>
  )
}

export default QuickStartStep3Page