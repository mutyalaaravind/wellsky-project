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
  Select,
  Alert,
  AlertIcon,
  Spinner
} from '@chakra-ui/react'
import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useReferenceData } from '../hooks/useReferenceData'
import { useUserProfile } from '../hooks/useUserProfile'

interface QuickStartFormData {
  businessUnit: string
  solutionId: string
  name: string
  description: string
}

const QuickStartPage: React.FC = () => {
  const navigate = useNavigate()
  const { businessUnits, solutions, loading: referenceLoading, error: referenceError } = useReferenceData()
  const { userProfile, loading: profileLoading, error: profileError } = useUserProfile()
  const [formData, setFormData] = useState<QuickStartFormData>({
    businessUnit: '',
    solutionId: '',
    name: '',
    description: ''
  })

  // Function to generate 8 random characters (alphanumeric)
  const generateRandomString = (length: number = 8): string => {
    const chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    let result = ''
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length))
    }
    return result
  }

  // Get allowed business units based on user organizations
  const allowedBusinessUnits = useMemo(() => {
    if (!userProfile?.organizations || userProfile.organizations.length === 0) {
      return []
    }

    const allowedBUs = new Set<string>()
    userProfile.organizations.forEach(org => {
      if (org.business_unit === "*") {
        // Add all business units
        businessUnits.forEach(bu => allowedBUs.add(bu.bu_code))
      } else {
        allowedBUs.add(org.business_unit)
      }
    })

    return businessUnits
      .filter(bu => allowedBUs.has(bu.bu_code))
      .sort((a, b) => a.name.localeCompare(b.name))
  }, [userProfile, businessUnits])

  // Get allowed solutions based on user organizations and selected business unit
  const allowedSolutions = useMemo(() => {
    if (!userProfile?.organizations || !formData.businessUnit) {
      return []
    }

    // Find organizations that allow access to the selected business unit
    const relevantOrgs = userProfile.organizations.filter(org =>
      org.business_unit === "*" || org.business_unit === formData.businessUnit
    )

    if (relevantOrgs.length === 0) {
      return []
    }

    const allowedSolCodes = new Set<string>()
    relevantOrgs.forEach(org => {
      if (org.solution_code === "*") {
        // Add all solutions for this business unit
        solutions
          .filter(sol => sol.bu_code === formData.businessUnit)
          .forEach(sol => allowedSolCodes.add(sol.code))
      } else {
        allowedSolCodes.add(org.solution_code)
      }
    })

    return solutions
      .filter(sol => sol.bu_code === formData.businessUnit && allowedSolCodes.has(sol.code))
      .sort((a, b) => a.name.localeCompare(b.name))
  }, [userProfile, solutions, formData.businessUnit])

  const handleInputChange = (field: keyof QuickStartFormData, value: string) => {
    setFormData(prev => {
      const newData = { ...prev, [field]: value }

      // Reset solution when business unit changes
      if (field === 'businessUnit') {
        newData.solutionId = ''
      }

      return newData
    })
  }

  const handleSubmit = () => {
    // Generate a unique app_id
    const appId = `vk-${formData.businessUnit}-${formData.solutionId}-${generateRandomString()}`

    // Navigate to QuickStart Step 2 with form data as URL parameters
    const params = new URLSearchParams({
      businessUnit: formData.businessUnit,
      solutionId: formData.solutionId,
      name: formData.name,
      description: formData.description,
      appId: appId
    })
    navigate(`/quick-start/step-2?${params.toString()}`)
  }

  const isFormValid = formData.businessUnit && formData.solutionId && formData.name

  // Check if we're still loading data
  const isLoading = referenceLoading || profileLoading

  // Combine errors
  const hasError = referenceError || profileError
  const errorMessage = referenceError || profileError

  // Check if user has no access to any business units
  const hasNoAccess = !isLoading && userProfile && allowedBusinessUnits.length === 0

  if (isLoading) {
    return (
      <VStack spacing={4} align="center" pt={8}>
        <Spinner size="lg" color="var(--palette-accent-ws-elm-500)" />
        <Text>Loading data...</Text>
      </VStack>
    )
  }

  return (
    <VStack spacing={8} align="stretch" maxW="600px" mx="auto" p={4}>
      <Box>
        <Heading as="h1" size="lg" mb={4} color="var(--Secondary-ws-elm-700)">
          Quick Start
        </Heading>
        <Text color="gray.600" mb={6}>
          Get started by entering your basic information below.
        </Text>
        {hasError && (
          <Alert status="error" mb={4}>
            <AlertIcon />
            Failed to load data: {errorMessage}
          </Alert>
        )}
        {hasNoAccess && (
          <Alert status="warning" mb={4}>
            <AlertIcon />
            You don't have access to create applications in any business units. Please contact your administrator.
          </Alert>
        )}
      </Box>

      <Card>
        <CardHeader>
          <Heading size="md">Application Information</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={4}>
            <FormControl isRequired>
              <FormLabel>Business Unit</FormLabel>
              <Select
                placeholder={isLoading ? "Loading business units..." : hasNoAccess ? "No access to business units" : "Select business unit"}
                value={formData.businessUnit}
                onChange={(e) => handleInputChange('businessUnit', e.target.value)}
                isDisabled={isLoading || !!hasNoAccess}
              >
                {allowedBusinessUnits.map(businessUnit => (
                  <option key={businessUnit.bu_code} value={businessUnit.bu_code}>
                    {businessUnit.name}
                  </option>
                ))}
              </Select>
            </FormControl>
            <FormControl isRequired>
              <FormLabel>Solution ID</FormLabel>
              <Select
                placeholder={isLoading ? "Loading solutions..." : !formData.businessUnit ? "Select business unit first" : "Select solution ID"}
                value={formData.solutionId}
                onChange={(e) => handleInputChange('solutionId', e.target.value)}
                isDisabled={!formData.businessUnit || isLoading || !!hasNoAccess}
              >
                {allowedSolutions.map(solution => (
                  <option key={solution.code} value={solution.code}>
                    {solution.name} ({solution.code.toUpperCase()})
                  </option>
                ))}
              </Select>
            </FormControl>
            <FormControl isRequired>
              <FormLabel>Name</FormLabel>
              <Input
                placeholder="Enter name"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
              />
            </FormControl>
            <FormControl>
              <FormLabel>Description</FormLabel>
              <Textarea
                placeholder="Enter description"
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
              />
            </FormControl>
            <Button
              style={{ backgroundColor: 'var(--palette-accent-ws-elm-500)' }}
              color="white"
              _hover={{ backgroundColor: 'var(--Secondary-ws-elm-700)' }}
              size="lg"
              width="full"
              onClick={handleSubmit}
              isDisabled={!isFormValid || !!hasNoAccess}
            >
              Continue
            </Button>
          </VStack>
        </CardBody>
      </Card>
    </VStack>
  )
}

export default QuickStartPage