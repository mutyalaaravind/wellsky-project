import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Button,
  FormControl,
  FormLabel,
  Input,
  Textarea,
  Switch,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  VStack,
  HStack,
  Text,
  Divider,
  useToast,
  FormErrorMessage,
  Tag,
  TagLabel,
  TagCloseButton,
  Wrap,
  WrapItem,
  Select,
  Box,
} from '@chakra-ui/react'
import { useState, useEffect } from 'react'
import { LLMModel, LLMModelCreateRequest, LLMModelUpdateRequest } from '../services/llmModelsService'

interface LLMModelModalProps {
  isOpen: boolean
  onClose: () => void
  onSave: (model: LLMModelCreateRequest | LLMModelUpdateRequest) => Promise<{ success: boolean; error?: string }>
  model?: LLMModel
  mode: 'create' | 'edit'
}

const LLMModelModal: React.FC<LLMModelModalProps> = ({
  isOpen,
  onClose,
  onSave,
  model,
  mode,
}) => {
  const toast = useToast()
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})
  
  // Form state
  // Available type options
  const AVAILABLE_TYPES = ['text', 'code', 'image', 'audio', 'video']
  
  // Available regions for provisioned throughput
  const AVAILABLE_REGIONS = [
    { value: 'us-central1', label: 'US Central 1' }
    // Add more regions here in the future
  ]
  
  const [formData, setFormData] = useState({
    family: '',
    name: '',
    model_id: '',
    version: '',
    description: '',
    per_second_throughput_per_gsu: 100,
    units: 'tokens',
    minimum_gsu_purchase_increment: 1,
    knowledge_cutoff_date: '',
    priority: 1.0,
    active: true,
    // Support profile
    input_types: ['text'] as string[],
    output_types: ['text'] as string[],
    new_input_type: '',
    new_output_type: '',
    // Provisioned throughput
    provisioned_throughput: [] as Array<{ region: string; gsus: number }>,
    new_region: '',
    new_gsus: 1,
    // Burndown rate factors
    input_text_token: 1.0,
    input_image_token: 1.0,
    input_video_token: 1.0,
    input_audio_token: 3.0,
    output_response_text_token: 4.0,
    output_reasoning_text_token: 4.0,
    // Lifecycle
    google_available_date: '',
    google_sunset_date: '',
    wsky_available_date: '',
    wsky_sunset_date: '',
  })

  // Initialize form data when modal opens or model changes
  useEffect(() => {
    if (isOpen) {
      if (mode === 'edit' && model) {
        setFormData({
          family: model.family,
          name: model.name,
          model_id: model.model_id,
          version: model.version,
          description: model.description,
          per_second_throughput_per_gsu: model.per_second_throughput_per_gsu,
          units: model.units,
          minimum_gsu_purchase_increment: model.minimum_gsu_purchase_increment,
          knowledge_cutoff_date: model.knowledge_cutoff_date,
          priority: model.priority,
          active: model.active,
          input_types: model.support_profile.input,
          output_types: model.support_profile.output,
          new_input_type: '',
          new_output_type: '',
          provisioned_throughput: model.provisioned_throughput || [],
          new_region: '',
          new_gsus: 1,
          input_text_token: model.burndown_rate_factors.input_text_token,
          input_image_token: model.burndown_rate_factors.input_image_token,
          input_video_token: model.burndown_rate_factors.input_video_token,
          input_audio_token: model.burndown_rate_factors.input_audio_token,
          output_response_text_token: model.burndown_rate_factors.output_response_text_token,
          output_reasoning_text_token: model.burndown_rate_factors.output_reasoning_text_token,
          google_available_date: model.lifecycle.google?.available_date || '',
          google_sunset_date: model.lifecycle.google?.sunset_date || '',
          wsky_available_date: model.lifecycle.wsky?.available_date || '',
          wsky_sunset_date: model.lifecycle.wsky?.sunset_date || '',
        })
      } else {
        // Reset form for create mode
        setFormData({
          family: '',
          name: '',
          model_id: '',
          version: '',
          description: '',
          per_second_throughput_per_gsu: 100,
          units: 'tokens',
          minimum_gsu_purchase_increment: 1,
          knowledge_cutoff_date: '',
          priority: 1.0,
          active: true,
          input_types: ['text'],
          output_types: ['text'],
          new_input_type: '',
          new_output_type: '',
          provisioned_throughput: [],
          new_region: '',
          new_gsus: 1,
          input_text_token: 1.0,
          input_image_token: 1.0,
          input_video_token: 1.0,
          input_audio_token: 3.0,
          output_response_text_token: 4.0,
          output_reasoning_text_token: 4.0,
          google_available_date: '',
          google_sunset_date: '',
          wsky_available_date: '',
          wsky_sunset_date: '',
        })
      }
      setErrors({})
    }
  }, [isOpen, mode, model])

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.family.trim()) newErrors.family = 'Family is required'
    if (!formData.name.trim()) newErrors.name = 'Name is required'
    if (!formData.model_id.trim()) {
      newErrors.model_id = 'Model ID is required'
    } else if (!/^[a-z0-9]+([.-][a-z0-9]+)*$/.test(formData.model_id)) {
      newErrors.model_id = 'Model ID must be lowercase alphanumeric with hyphens and periods (e.g., gemini-2.5-flash-lite)'
    }
    if (!formData.version.trim()) newErrors.version = 'Version is required'
    if (!formData.description.trim()) newErrors.description = 'Description is required'
    if (!formData.knowledge_cutoff_date.trim()) newErrors.knowledge_cutoff_date = 'Knowledge cutoff date is required'
    
    // Validate Google lifecycle dates
    if (formData.google_available_date && !formData.google_sunset_date) {
      newErrors.google_sunset_date = 'Google sunset date is required when available date is set'
    }
    if (!formData.google_available_date && formData.google_sunset_date) {
      newErrors.google_available_date = 'Google available date is required when sunset date is set'
    }
    if (formData.google_available_date && formData.google_sunset_date) {
      if (new Date(formData.google_sunset_date) <= new Date(formData.google_available_date)) {
        newErrors.google_sunset_date = 'Google sunset date must be after available date'
      }
    }
    
    // Validate Wellsky lifecycle dates
    if (formData.wsky_available_date && !formData.wsky_sunset_date) {
      newErrors.wsky_sunset_date = 'Wellsky sunset date is required when available date is set'
    }
    if (!formData.wsky_available_date && formData.wsky_sunset_date) {
      newErrors.wsky_available_date = 'Wellsky available date is required when sunset date is set'
    }
    if (formData.wsky_available_date && formData.wsky_sunset_date) {
      if (new Date(formData.wsky_sunset_date) <= new Date(formData.wsky_available_date)) {
        newErrors.wsky_sunset_date = 'Wellsky sunset date must be after available date'
      }
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async () => {
    if (!validateForm()) return
    
    setLoading(true)
    try {
      const modelData = {
        family: formData.family,
        name: formData.name,
        model_id: formData.model_id,
        version: formData.version,
        description: formData.description,
        support_profile: {
          input: formData.input_types,
          output: formData.output_types,
        },
        per_second_throughput_per_gsu: formData.per_second_throughput_per_gsu,
        units: formData.units,
        minimum_gsu_purchase_increment: formData.minimum_gsu_purchase_increment,
        burndown_rate_factors: {
          input_text_token: formData.input_text_token,
          input_image_token: formData.input_image_token,
          input_video_token: formData.input_video_token,
          input_audio_token: formData.input_audio_token,
          output_response_text_token: formData.output_response_text_token,
          output_reasoning_text_token: formData.output_reasoning_text_token,
        },
        knowledge_cutoff_date: formData.knowledge_cutoff_date,
        lifecycle: {
          ...(formData.google_available_date && formData.google_sunset_date ? {
            google: {
              available_date: formData.google_available_date,
              sunset_date: formData.google_sunset_date,
            }
          } : {}),
          ...(formData.wsky_available_date && formData.wsky_sunset_date ? {
            wsky: {
              available_date: formData.wsky_available_date,
              sunset_date: formData.wsky_sunset_date,
            }
          } : {})
        },
        provisioned_throughput: formData.provisioned_throughput,
        priority: formData.priority,
        active: formData.active,
      }

      const result = await onSave(modelData)
      
      if (result.success) {
        toast({
          title: `Model ${mode === 'create' ? 'created' : 'updated'}`,
          description: `${formData.name} has been successfully ${mode === 'create' ? 'created' : 'updated'}.`,
          status: 'success',
          duration: 3000,
          isClosable: true,
        })
        onClose()
      } else {
        toast({
          title: 'Operation failed',
          description: result.error || `Failed to ${mode} model`,
          status: 'error',
          duration: 5000,
          isClosable: true,
        })
      }
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  const addInputType = () => {
    if (formData.new_input_type && 
        AVAILABLE_TYPES.includes(formData.new_input_type) && 
        !formData.input_types.includes(formData.new_input_type)) {
      setFormData(prev => ({
        ...prev,
        input_types: [...prev.input_types, prev.new_input_type],
        new_input_type: ''
      }))
    }
  }

  const removeInputType = (type: string) => {
    setFormData(prev => ({
      ...prev,
      input_types: prev.input_types.filter(t => t !== type)
    }))
  }

  const addOutputType = () => {
    if (formData.new_output_type && 
        AVAILABLE_TYPES.includes(formData.new_output_type) && 
        !formData.output_types.includes(formData.new_output_type)) {
      setFormData(prev => ({
        ...prev,
        output_types: [...prev.output_types, prev.new_output_type],
        new_output_type: ''
      }))
    }
  }

  const removeOutputType = (type: string) => {
    setFormData(prev => ({
      ...prev,
      output_types: prev.output_types.filter(t => t !== type)
    }))
  }

  const getAvailableInputTypes = () => {
    return AVAILABLE_TYPES.filter(type => !formData.input_types.includes(type))
  }

  const getAvailableOutputTypes = () => {
    return AVAILABLE_TYPES.filter(type => !formData.output_types.includes(type))
  }

  const addProvisionedThroughput = () => {
    if (formData.new_region && 
        formData.new_gsus > 0 && 
        !formData.provisioned_throughput.some(pt => pt.region === formData.new_region)) {
      setFormData(prev => ({
        ...prev,
        provisioned_throughput: [...prev.provisioned_throughput, {
          region: prev.new_region,
          gsus: prev.new_gsus
        }],
        new_region: '',
        new_gsus: 1
      }))
    }
  }

  const removeProvisionedThroughput = (region: string) => {
    setFormData(prev => ({
      ...prev,
      provisioned_throughput: prev.provisioned_throughput.filter(pt => pt.region !== region)
    }))
  }

  const getAvailableRegions = () => {
    return AVAILABLE_REGIONS.filter(region => 
      !formData.provisioned_throughput.some(pt => pt.region === region.value)
    )
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl" scrollBehavior="inside">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>
          {mode === 'create' ? 'Create LLM Model' : 'Edit LLM Model'}
        </ModalHeader>
        <ModalCloseButton />
        
        <ModalBody>
          <VStack spacing={4} align="stretch">
            {/* Basic Information */}
            <Text fontWeight="semibold" color="var(--Secondary-ws-elm-700)">
              Basic Information
            </Text>

            <FormControl isInvalid={!!errors.name}>
              <FormLabel>Name</FormLabel>
              <Input
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                placeholder="e.g., Gemini 1.5 Pro"
              />
              <FormErrorMessage>{errors.name}</FormErrorMessage>
            </FormControl>

            <HStack spacing={4} align="start">
              <FormControl isInvalid={!!errors.model_id}>
                <FormLabel>Model ID</FormLabel>
                <Input
                  value={formData.model_id}
                  onChange={(e) => handleInputChange('model_id', e.target.value)}
                  placeholder="e.g., gemini-2.5-flash-lite"
                />
                <Text fontSize="xs" color="gray.600" mt={1}>
                  API identifier (lowercase alphanumeric with hyphens and periods)
                </Text>
                <FormErrorMessage>{errors.model_id}</FormErrorMessage>
              </FormControl>

              <FormControl isInvalid={!!errors.family}>
                <FormLabel>Family</FormLabel>
                <Input
                  value={formData.family}
                  onChange={(e) => handleInputChange('family', e.target.value)}
                  placeholder="e.g., gemini, claude"
                />
                <FormErrorMessage>{errors.family}</FormErrorMessage>
              </FormControl>
            </HStack>

            <HStack spacing={4}>
              <FormControl isInvalid={!!errors.version}>
                <FormLabel>Version</FormLabel>
                <Input
                  value={formData.version}
                  onChange={(e) => handleInputChange('version', e.target.value)}
                  placeholder="e.g., 1.5"
                />
                <FormErrorMessage>{errors.version}</FormErrorMessage>
              </FormControl>

              <FormControl>
                <FormLabel>Priority</FormLabel>
                <NumberInput
                  value={formData.priority}
                  onChange={(_, value) => handleInputChange('priority', value)}
                  step={0.1}
                  min={0}
                >
                  <NumberInputField />
                  <NumberInputStepper>
                    <NumberIncrementStepper />
                    <NumberDecrementStepper />
                  </NumberInputStepper>
                </NumberInput>
              </FormControl>
            </HStack>

            <FormControl isInvalid={!!errors.description}>
              <FormLabel>Description</FormLabel>
              <Textarea
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="Describe the model's capabilities and use cases"
                rows={3}
              />
              <FormErrorMessage>{errors.description}</FormErrorMessage>
            </FormControl>

            <FormControl isInvalid={!!errors.knowledge_cutoff_date}>
              <FormLabel>Knowledge Cutoff Date</FormLabel>
              <Input
                type="date"
                value={formData.knowledge_cutoff_date}
                onChange={(e) => handleInputChange('knowledge_cutoff_date', e.target.value)}
              />
              <FormErrorMessage>{errors.knowledge_cutoff_date}</FormErrorMessage>
            </FormControl>

            <Divider />

            {/* Performance Settings */}
            <Text fontWeight="semibold" color="var(--Secondary-ws-elm-700)">
              Performance Settings
            </Text>

            <HStack spacing={4}>
              <FormControl>
                <FormLabel>Throughput per GSU</FormLabel>
                <NumberInput
                  value={formData.per_second_throughput_per_gsu}
                  onChange={(_, value) => handleInputChange('per_second_throughput_per_gsu', value)}
                  min={1}
                >
                  <NumberInputField />
                  <NumberInputStepper>
                    <NumberIncrementStepper />
                    <NumberDecrementStepper />
                  </NumberInputStepper>
                </NumberInput>
              </FormControl>

              <FormControl>
                <FormLabel>Units</FormLabel>
                <Input
                  value={formData.units}
                  onChange={(e) => handleInputChange('units', e.target.value)}
                  placeholder="tokens"
                />
              </FormControl>
            </HStack>

            <FormControl>
              <FormLabel>Minimum GSU Purchase Increment</FormLabel>
              <NumberInput
                value={formData.minimum_gsu_purchase_increment}
                onChange={(_, value) => handleInputChange('minimum_gsu_purchase_increment', value)}
                min={1}
              >
                <NumberInputField />
                <NumberInputStepper>
                  <NumberIncrementStepper />
                  <NumberDecrementStepper />
                </NumberInputStepper>
              </NumberInput>
            </FormControl>

            <Divider />

            {/* Support Profile */}
            <Text fontWeight="semibold" color="var(--Secondary-ws-elm-700)">
              Support Profile
            </Text>

            <VStack spacing={4} align="stretch">
              <FormControl>
                <FormLabel>Input Types</FormLabel>
                <VStack align="stretch" spacing={3}>
                  <Wrap spacing={2}>
                    {formData.input_types.map((type) => (
                      <WrapItem key={type}>
                        <Tag
                          size="md"
                          borderRadius="full"
                          variant="solid"
                          style={{ backgroundColor: 'var(--palette-accent-ws-elm-500)' }}
                          color="white"
                        >
                          <TagLabel>{type}</TagLabel>
                          <TagCloseButton onClick={() => removeInputType(type)} />
                        </Tag>
                      </WrapItem>
                    ))}
                  </Wrap>
                  <HStack>
                    <Select
                      value={formData.new_input_type}
                      onChange={(e) => handleInputChange('new_input_type', e.target.value)}
                      placeholder="Select input type to add"
                      size="sm"
                    >
                      {getAvailableInputTypes().map((type) => (
                        <option key={type} value={type}>
                          {type}
                        </option>
                      ))}
                    </Select>
                    <Button
                      onClick={addInputType}
                      size="sm"
                      style={{ backgroundColor: 'var(--Secondary-ws-elm-700)' }}
                      color="white"
                      _hover={{ backgroundColor: 'var(--palette-accent-ws-elm-500)' }}
                      isDisabled={!formData.new_input_type || getAvailableInputTypes().length === 0}
                    >
                      Add
                    </Button>
                  </HStack>
                </VStack>
              </FormControl>

              <FormControl>
                <FormLabel>Output Types</FormLabel>
                <VStack align="stretch" spacing={3}>
                  <Wrap spacing={2}>
                    {formData.output_types.map((type) => (
                      <WrapItem key={type}>
                        <Tag
                          size="md"
                          borderRadius="full"
                          variant="solid"
                          style={{ backgroundColor: 'var(--palette-accent-ws-elm-500)' }}
                          color="white"
                        >
                          <TagLabel>{type}</TagLabel>
                          <TagCloseButton onClick={() => removeOutputType(type)} />
                        </Tag>
                      </WrapItem>
                    ))}
                  </Wrap>
                  <HStack>
                    <Select
                      value={formData.new_output_type}
                      onChange={(e) => handleInputChange('new_output_type', e.target.value)}
                      placeholder="Select output type to add"
                      size="sm"
                    >
                      {getAvailableOutputTypes().map((type) => (
                        <option key={type} value={type}>
                          {type}
                        </option>
                      ))}
                    </Select>
                    <Button
                      onClick={addOutputType}
                      size="sm"
                      style={{ backgroundColor: 'var(--Secondary-ws-elm-700)' }}
                      color="white"
                      _hover={{ backgroundColor: 'var(--palette-accent-ws-elm-500)' }}
                      isDisabled={!formData.new_output_type || getAvailableOutputTypes().length === 0}
                    >
                      Add
                    </Button>
                  </HStack>
                </VStack>
              </FormControl>
            </VStack>

            <Divider />

            {/* Provisioned Throughput */}
            <Text fontWeight="semibold" color="var(--Secondary-ws-elm-700)">
              Provisioned Throughput
            </Text>

            <VStack spacing={4} align="stretch">
              <Text fontSize="sm" color="gray.600">
                Configure provisioned throughput by region for guaranteed capacity.
              </Text>
              
              {/* Existing provisioned throughput */}
              {formData.provisioned_throughput.length > 0 && (
                <VStack align="stretch" spacing={2}>
                  <Text fontSize="sm" fontWeight="medium">Current Provisioned Throughput:</Text>
                  {formData.provisioned_throughput.map((pt) => (
                    <Box
                      key={pt.region}
                      p={3}
                      borderWidth="1px"
                      borderColor="gray.200"
                      borderRadius="md"
                      bg="gray.50"
                    >
                      <HStack justify="space-between" align="center">
                        <VStack align="start" spacing={1}>
                          <Text fontSize="sm" fontWeight="medium">
                            {AVAILABLE_REGIONS.find(r => r.value === pt.region)?.label || pt.region}
                          </Text>
                          <Text fontSize="sm" color="gray.600">
                            {pt.gsus} GSUs
                          </Text>
                        </VStack>
                        <Button
                          size="sm"
                          variant="ghost"
                          colorScheme="red"
                          onClick={() => removeProvisionedThroughput(pt.region)}
                        >
                          Remove
                        </Button>
                      </HStack>
                    </Box>
                  ))}
                </VStack>
              )}

              {/* Add new provisioned throughput */}
              <Box p={4} borderWidth="1px" borderColor="gray.200" borderRadius="md">
                <Text fontWeight="medium" mb={3}>Add Provisioned Throughput</Text>
                <VStack spacing={3}>
                  <HStack spacing={4} w="full">
                    <FormControl>
                      <FormLabel fontSize="sm">Region</FormLabel>
                      <Select
                        value={formData.new_region}
                        onChange={(e) => handleInputChange('new_region', e.target.value)}
                        placeholder="Select region"
                        size="sm"
                      >
                        {getAvailableRegions().map((region) => (
                          <option key={region.value} value={region.value}>
                            {region.label}
                          </option>
                        ))}
                      </Select>
                    </FormControl>
                    <FormControl>
                      <FormLabel fontSize="sm">GSUs</FormLabel>
                      <NumberInput
                        value={formData.new_gsus}
                        onChange={(_, value) => handleInputChange('new_gsus', value)}
                        min={1}
                        size="sm"
                      >
                        <NumberInputField />
                        <NumberInputStepper>
                          <NumberIncrementStepper />
                          <NumberDecrementStepper />
                        </NumberInputStepper>
                      </NumberInput>
                    </FormControl>
                  </HStack>
                  <Button
                    onClick={addProvisionedThroughput}
                    size="sm"
                    style={{ backgroundColor: 'var(--Secondary-ws-elm-700)' }}
                    color="white"
                    _hover={{ backgroundColor: 'var(--palette-accent-ws-elm-500)' }}
                    isDisabled={!formData.new_region || formData.new_gsus <= 0 || getAvailableRegions().length === 0}
                    alignSelf="flex-start"
                  >
                    Add Provisioned Throughput
                  </Button>
                </VStack>
              </Box>
            </VStack>

            <Divider />

            {/* Burndown Rate Factors */}
            <Text fontWeight="semibold" color="var(--Secondary-ws-elm-700)">
              Burndown Rate Factors
            </Text>

            <VStack spacing={4} align="stretch">
              <Text fontSize="sm" color="gray.600">
                Configure token consumption rates for different input and output types.
              </Text>

              {/* Quick Preset Buttons */}
              <Box p={3} bg="gray.50" borderRadius="md">
                <HStack spacing={3} align="center">
                  <Text fontSize="sm" fontWeight="medium">Quick Presets:</Text>
                  <Button
                    size="xs"
                    variant="outline"
                    onClick={() => {
                      setFormData(prev => ({
                        ...prev,
                        input_text_token: 1.0,
                        input_image_token: 1.0,
                        input_video_token: 1.0,
                        input_audio_token: 3.0,
                        output_response_text_token: 4.0,
                        output_reasoning_text_token: 4.0,
                      }))
                    }}
                  >
                    Default Rates
                  </Button>
                  <Button
                    size="xs"
                    variant="outline"
                    onClick={() => {
                      setFormData(prev => ({
                        ...prev,
                        input_text_token: 1.0,
                        input_image_token: 1.0,
                        input_video_token: 1.0,
                        input_audio_token: 1.0,
                        output_response_text_token: 1.0,
                        output_reasoning_text_token: 1.0,
                      }))
                    }}
                  >
                    Uniform Rate (1.0)
                  </Button>
                  <Button
                    size="xs"
                    variant="outline"
                    onClick={() => {
                      setFormData(prev => ({
                        ...prev,
                        input_text_token: 0.5,
                        input_image_token: 2.0,
                        input_video_token: 5.0,
                        input_audio_token: 3.0,
                        output_response_text_token: 8.0,
                        output_reasoning_text_token: 12.0,
                      }))
                    }}
                  >
                    High-Compute Model
                  </Button>
                </HStack>
              </Box>

              {/* Input Token Rates */}
              <Box p={4} borderWidth="1px" borderColor="gray.200" borderRadius="md">
                <Text fontWeight="medium" mb={3} color="gray.700">
                  Input Token Rates
                </Text>
                <VStack spacing={3}>
                  <HStack spacing={4} w="full">
                    <FormControl>
                      <FormLabel fontSize="sm">Text Tokens</FormLabel>
                      <NumberInput
                        value={formData.input_text_token}
                        onChange={(_, value) => handleInputChange('input_text_token', value || 1.0)}
                        step={0.1}
                        min={0}
                        precision={1}
                        size="sm"
                      >
                        <NumberInputField />
                        <NumberInputStepper>
                          <NumberIncrementStepper />
                          <NumberDecrementStepper />
                        </NumberInputStepper>
                      </NumberInput>
                    </FormControl>
                    <FormControl>
                      <FormLabel fontSize="sm">Image Tokens</FormLabel>
                      <NumberInput
                        value={formData.input_image_token}
                        onChange={(_, value) => handleInputChange('input_image_token', value || 1.0)}
                        step={0.1}
                        min={0}
                        precision={1}
                        size="sm"
                      >
                        <NumberInputField />
                        <NumberInputStepper>
                          <NumberIncrementStepper />
                          <NumberDecrementStepper />
                        </NumberInputStepper>
                      </NumberInput>
                    </FormControl>
                  </HStack>
                  <HStack spacing={4} w="full">
                    <FormControl>
                      <FormLabel fontSize="sm">Video Tokens</FormLabel>
                      <NumberInput
                        value={formData.input_video_token}
                        onChange={(_, value) => handleInputChange('input_video_token', value || 1.0)}
                        step={0.1}
                        min={0}
                        precision={1}
                        size="sm"
                      >
                        <NumberInputField />
                        <NumberInputStepper>
                          <NumberIncrementStepper />
                          <NumberDecrementStepper />
                        </NumberInputStepper>
                      </NumberInput>
                    </FormControl>
                    <FormControl>
                      <FormLabel fontSize="sm">Audio Tokens</FormLabel>
                      <NumberInput
                        value={formData.input_audio_token}
                        onChange={(_, value) => handleInputChange('input_audio_token', value || 3.0)}
                        step={0.1}
                        min={0}
                        precision={1}
                        size="sm"
                      >
                        <NumberInputField />
                        <NumberInputStepper>
                          <NumberIncrementStepper />
                          <NumberDecrementStepper />
                        </NumberInputStepper>
                      </NumberInput>
                    </FormControl>
                  </HStack>
                </VStack>
              </Box>

              {/* Output Token Rates */}
              <Box p={4} borderWidth="1px" borderColor="gray.200" borderRadius="md">
                <Text fontWeight="medium" mb={3} color="gray.700">
                  Output Token Rates
                </Text>
                <VStack spacing={3}>
                  <HStack spacing={4} w="full">
                    <FormControl>
                      <FormLabel fontSize="sm">Response Text Tokens</FormLabel>
                      <NumberInput
                        value={formData.output_response_text_token}
                        onChange={(_, value) => handleInputChange('output_response_text_token', value || 4.0)}
                        step={0.1}
                        min={0}
                        precision={1}
                        size="sm"
                      >
                        <NumberInputField />
                        <NumberInputStepper>
                          <NumberIncrementStepper />
                          <NumberDecrementStepper />
                        </NumberInputStepper>
                      </NumberInput>
                    </FormControl>
                    <FormControl>
                      <FormLabel fontSize="sm">Reasoning Text Tokens</FormLabel>
                      <NumberInput
                        value={formData.output_reasoning_text_token}
                        onChange={(_, value) => handleInputChange('output_reasoning_text_token', value || 4.0)}
                        step={0.1}
                        min={0}
                        precision={1}
                        size="sm"
                      >
                        <NumberInputField />
                        <NumberInputStepper>
                          <NumberIncrementStepper />
                          <NumberDecrementStepper />
                        </NumberInputStepper>
                      </NumberInput>
                    </FormControl>
                  </HStack>
                </VStack>
              </Box>

            </VStack>

            <Divider />

            {/* Lifecycle Management */}
            <Text fontWeight="semibold" color="var(--Secondary-ws-elm-700)">
              Lifecycle Management
            </Text>

            <VStack spacing={4} align="stretch">
              {/* Google Lifecycle */}
              <Box p={4} borderWidth="1px" borderColor="gray.200" borderRadius="md">
                <Text fontWeight="medium" mb={3} color="gray.700">
                  Google Provider
                </Text>
                <HStack spacing={4}>
                  <FormControl isInvalid={!!errors.google_available_date}>
                    <FormLabel fontSize="sm">Available Date</FormLabel>
                    <Input
                      type="date"
                      value={formData.google_available_date}
                      onChange={(e) => handleInputChange('google_available_date', e.target.value)}
                      size="sm"
                    />
                    <FormErrorMessage>{errors.google_available_date}</FormErrorMessage>
                  </FormControl>
                  <FormControl isInvalid={!!errors.google_sunset_date}>
                    <FormLabel fontSize="sm">Sunset Date</FormLabel>
                    <Input
                      type="date"
                      value={formData.google_sunset_date}
                      onChange={(e) => handleInputChange('google_sunset_date', e.target.value)}
                      size="sm"
                    />
                    <FormErrorMessage>{errors.google_sunset_date}</FormErrorMessage>
                  </FormControl>
                </HStack>
              </Box>

              {/* Wellsky Lifecycle */}
              <Box p={4} borderWidth="1px" borderColor="gray.200" borderRadius="md">
                <Text fontWeight="medium" mb={3} color="gray.700">
                  Wellsky Provider
                </Text>
                <HStack spacing={4}>
                  <FormControl isInvalid={!!errors.wsky_available_date}>
                    <FormLabel fontSize="sm">Available Date</FormLabel>
                    <Input
                      type="date"
                      value={formData.wsky_available_date}
                      onChange={(e) => handleInputChange('wsky_available_date', e.target.value)}
                      size="sm"
                    />
                    <FormErrorMessage>{errors.wsky_available_date}</FormErrorMessage>
                  </FormControl>
                  <FormControl isInvalid={!!errors.wsky_sunset_date}>
                    <FormLabel fontSize="sm">Sunset Date</FormLabel>
                    <Input
                      type="date"
                      value={formData.wsky_sunset_date}
                      onChange={(e) => handleInputChange('wsky_sunset_date', e.target.value)}
                      size="sm"
                    />
                    <FormErrorMessage>{errors.wsky_sunset_date}</FormErrorMessage>
                  </FormControl>
                </HStack>
              </Box>
            </VStack>

            <Divider />

            {/* Status */}
            <HStack justify="space-between">
              <Text fontWeight="semibold" color="var(--Secondary-ws-elm-700)">
                Active Status
              </Text>
              <FormControl display="flex" alignItems="center" w="auto">
                <FormLabel mb="0">Active</FormLabel>
                <Switch
                  isChecked={formData.active}
                  onChange={(e) => handleInputChange('active', e.target.checked)}
                  colorScheme="teal"
                />
              </FormControl>
            </HStack>
          </VStack>
        </ModalBody>

        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose}>
            Cancel
          </Button>
          <Button
            style={{ backgroundColor: 'var(--palette-accent-ws-elm-500)' }}
            color="white"
            _hover={{ backgroundColor: 'var(--Secondary-ws-elm-700)' }}
            onClick={handleSubmit}
            isLoading={loading}
            loadingText={mode === 'create' ? 'Creating...' : 'Updating...'}
          >
            {mode === 'create' ? 'Create Model' : 'Update Model'}
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}

export default LLMModelModal