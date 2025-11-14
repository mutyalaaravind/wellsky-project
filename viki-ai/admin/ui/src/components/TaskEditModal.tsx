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
  VStack,
  HStack,
  Text,
  Divider,
  useToast,
  FormErrorMessage,
  Select,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Badge,
} from '@chakra-ui/react'
import { useState, useEffect } from 'react'
import { TaskConfig } from '../services/pipelinesService'
import { useLLMModels } from '../hooks/useLLMModels'

interface TaskEditModalProps {
  isOpen: boolean
  onClose: () => void
  onSave: (task: TaskConfig) => Promise<void>
  task?: TaskConfig
}

const TaskEditModal: React.FC<TaskEditModalProps> = ({
  isOpen,
  onClose,
  onSave,
  task,
}) => {
  const toast = useToast()
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  // Fetch registered LLM models
  const { models, loading: modelsLoading } = useLLMModels()
  const activeModels = models.filter(m => m.active)

  // Determine if we're in edit mode
  const isEditMode = !!task

  // Form state
  const [formData, setFormData] = useState({
    id: '',
    type: 'module' as 'module' | 'pipeline' | 'prompt' | 'remote' | 'publish_callback',
    // Module fields
    moduleType: '',
    // Prompt fields
    model: '',
    prompt: '',
    maxOutputTokens: 2000,
    temperature: 0.1,
    systemInstructions: '',
    // Remote fields
    url: '',
    method: 'POST',
    headers: '',
    timeout: 30,
  })

  // Initialize form data when modal opens or task changes
  useEffect(() => {
    if (isOpen) {
      if (!task) {
        // Handle case where no task is provided
        return
      }
      setFormData({
        id: task.id,
        type: task.type,
        moduleType: task.module?.type || '',
        model: task.prompt?.model || '',
        prompt: task.prompt?.prompt || '',
        maxOutputTokens: task.prompt?.max_output_tokens || 2000,
        temperature: parseFloat((task.prompt?.temperature ?? 0.1).toFixed(1)),
        systemInstructions: task.prompt?.system_instructions?.join('\n') || '',
        url: task.remote?.url || '',
        method: task.remote?.method || 'POST',
        headers: task.remote?.headers ? JSON.stringify(task.remote.headers, null, 2) : '',
        timeout: task.remote?.timeout || 30,
      })
      setErrors({})
    }
  }, [isOpen, task])

  const validateForm = () => {
    const newErrors: Record<string, string> = {}
    
    if (!formData.id.trim()) newErrors.id = 'Task ID is required'
    
    if (formData.type === 'module' && !formData.moduleType.trim()) {
      newErrors.moduleType = 'Module type is required'
    }
    
    if (formData.type === 'prompt') {
      if (!formData.model.trim()) newErrors.model = 'Model is required'
      if (!formData.prompt.trim()) newErrors.prompt = 'Prompt is required'
    }
    
    if (formData.type === 'remote') {
      if (!formData.url.trim()) newErrors.url = 'URL is required'
      try {
        new URL(formData.url)
      } catch {
        newErrors.url = 'Invalid URL format'
      }
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async () => {
    if (!validateForm()) return
    
    setLoading(true)
    try {
      const updatedTask: TaskConfig = {
        ...task,  // Preserve ALL existing fields first (entity_schema_ref, invoke, callback, params, etc.)
        id: formData.id,
        type: formData.type,
        ...(formData.type === 'module' && {
          module: {
            type: formData.moduleType,
            context: task?.module?.context || {}  // Preserve existing context
          }
        }),
        ...(formData.type === 'prompt' && {
          prompt: {
            ...task?.prompt,  // Preserve existing prompt config fields
            model: formData.model,
            prompt: formData.prompt,
            max_output_tokens: formData.maxOutputTokens,
            temperature: parseFloat(formData.temperature.toFixed(1)),
            ...(formData.systemInstructions && {
              system_instructions: formData.systemInstructions.split('\n').filter(line => line.trim())
            })
          }
        }),
        ...(formData.type === 'remote' && {
          remote: {
            ...task?.remote,  // Preserve existing remote config fields
            url: formData.url,
            method: formData.method,
            timeout: formData.timeout,
            ...(formData.headers && {
              headers: JSON.parse(formData.headers)
            })
          }
        })
      }

      await onSave(updatedTask)
      
      toast({
        title: 'Task updated',
        description: `${formData.id} has been successfully updated.`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
      onClose()
    } catch (error) {
      toast({
        title: 'Update failed',
        description: error instanceof Error ? error.message : 'Failed to update task',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
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

  const getTaskIcon = (type: string) => {
    switch (type) {
      case 'module': return '⚙️'
      case 'pipeline': return '🔗'
      case 'prompt': return '🤖'
      case 'remote': return '🌐'
      case 'publish_callback': return '📡'
      default: return '📋'
    }
  }

  const getTaskTypeColor = (type: string) => {
    switch (type) {
      case 'module': return 'blue'
      case 'pipeline': return 'purple'
      case 'prompt': return 'green'
      case 'remote': return 'orange'
      case 'publish_callback': return 'pink'
      default: return 'gray'
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl" scrollBehavior="inside">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>
          <HStack>
            <Text fontSize="lg">{getTaskIcon(formData.type)}</Text>
            <Text>{isEditMode ? 'Edit Task Configuration' : 'Create Task Configuration'}</Text>
            <Badge colorScheme={getTaskTypeColor(formData.type)} size="sm">
              {formData.type}
            </Badge>
          </HStack>
        </ModalHeader>
        <ModalCloseButton />
        
        <ModalBody>
          <VStack spacing={4} align="stretch">
            {/* Basic Information */}
            <Text fontWeight="semibold" color="var(--Secondary-ws-elm-700)">
              Basic Information
            </Text>
            
            <HStack spacing={4}>
              <FormControl isInvalid={!!errors.id}>
                <FormLabel>Task ID</FormLabel>
                <Input
                  value={formData.id}
                  onChange={(e) => handleInputChange('id', e.target.value)}
                  placeholder="e.g., SPLIT_PAGES"
                  isReadOnly={isEditMode}
                  bg={isEditMode ? 'gray.50' : 'white'}
                />
                <FormErrorMessage>{errors.id}</FormErrorMessage>
              </FormControl>
              
              <FormControl>
                <FormLabel>Task Type</FormLabel>
                <Select
                  value={formData.type}
                  onChange={(e) => handleInputChange('type', e.target.value)}
                  isDisabled={isEditMode}
                >
                  <option value="module">Module</option>
                  <option value="prompt">Prompt</option>
                  <option value="remote">Remote</option>
                  <option value="pipeline">Pipeline</option>
                  <option value="publish_callback">Publish Callback</option>
                </Select>
              </FormControl>
            </HStack>

            <Divider />

            {/* Type-specific configuration */}
            {formData.type === 'module' && (
              <>
                <Text fontWeight="semibold" color="var(--Secondary-ws-elm-700)">
                  Module Configuration
                </Text>
                <FormControl isInvalid={!!errors.moduleType}>
                  <FormLabel>Module Type</FormLabel>
                  <Input
                    value={formData.moduleType}
                    onChange={(e) => handleInputChange('moduleType', e.target.value)}
                    placeholder="e.g., split_pages"
                  />
                  <FormErrorMessage>{errors.moduleType}</FormErrorMessage>
                </FormControl>
              </>
            )}

            {formData.type === 'prompt' && (
              <>
                <Text fontWeight="semibold" color="var(--Secondary-ws-elm-700)">
                  Prompt Configuration
                </Text>
                <FormControl isInvalid={!!errors.model}>
                  <FormLabel>Model</FormLabel>
                  <Select
                    value={formData.model}
                    onChange={(e) => handleInputChange('model', e.target.value)}
                    isDisabled={modelsLoading}
                  >
                    <option value="">Select model</option>
                    {(() => {
                      // Check if current model is in the list of registered models
                      const registeredModelIds = activeModels.map(m => m.model_id)
                      const isCurrentModelUnregistered = formData.model &&
                        !registeredModelIds.includes(formData.model)

                      return (
                        <>
                          {isCurrentModelUnregistered && (
                            <option value={formData.model}>
                              {formData.model} (unregistered)
                            </option>
                          )}
                          {activeModels.map(model => (
                            <option key={model.id} value={model.model_id}>
                              {model.name}
                            </option>
                          ))}
                        </>
                      )
                    })()}
                  </Select>
                  <FormErrorMessage>{errors.model}</FormErrorMessage>
                </FormControl>

                <FormControl isInvalid={!!errors.prompt}>
                  <FormLabel>Prompt</FormLabel>
                  <Textarea
                    value={formData.prompt}
                    onChange={(e) => handleInputChange('prompt', e.target.value)}
                    placeholder="Enter the prompt for the AI model"
                    rows={4}
                  />
                  <FormErrorMessage>{errors.prompt}</FormErrorMessage>
                </FormControl>

                <FormControl>
                  <FormLabel>System Instructions (optional)</FormLabel>
                  <Textarea
                    value={formData.systemInstructions}
                    onChange={(e) => handleInputChange('systemInstructions', e.target.value)}
                    placeholder="Enter system instructions (one per line)"
                    rows={3}
                  />
                </FormControl>

                <HStack spacing={4}>
                  <FormControl>
                    <FormLabel>Max Output Tokens</FormLabel>
                    <NumberInput
                      value={formData.maxOutputTokens}
                      onChange={(_, value) => handleInputChange('maxOutputTokens', value || 2000)}
                      min={1}
                      max={10000}
                    >
                      <NumberInputField />
                      <NumberInputStepper>
                        <NumberIncrementStepper />
                        <NumberDecrementStepper />
                      </NumberInputStepper>
                    </NumberInput>
                  </FormControl>

                  <FormControl>
                    <FormLabel>Temperature</FormLabel>
                    <NumberInput
                      value={formData.temperature}
                      onChange={(_, value) => handleInputChange('temperature', parseFloat((value ?? 0.1).toFixed(1)))}
                      min={0}
                      max={2}
                      step={0.1}
                      precision={1}
                      format={(val) => Number(val).toFixed(1)}
                      parse={(val) => val}
                    >
                      <NumberInputField />
                      <NumberInputStepper>
                        <NumberIncrementStepper />
                        <NumberDecrementStepper />
                      </NumberInputStepper>
                    </NumberInput>
                  </FormControl>
                </HStack>
              </>
            )}

            {formData.type === 'remote' && (
              <>
                <Text fontWeight="semibold" color="var(--Secondary-ws-elm-700)">
                  Remote Configuration
                </Text>
                <FormControl isInvalid={!!errors.url}>
                  <FormLabel>URL</FormLabel>
                  <Input
                    value={formData.url}
                    onChange={(e) => handleInputChange('url', e.target.value)}
                    placeholder="https://api.example.com/endpoint"
                  />
                  <FormErrorMessage>{errors.url}</FormErrorMessage>
                </FormControl>

                <HStack spacing={4}>
                  <FormControl>
                    <FormLabel>Method</FormLabel>
                    <Select
                      value={formData.method}
                      onChange={(e) => handleInputChange('method', e.target.value)}
                    >
                      <option value="GET">GET</option>
                      <option value="POST">POST</option>
                      <option value="PUT">PUT</option>
                      <option value="DELETE">DELETE</option>
                    </Select>
                  </FormControl>

                  <FormControl>
                    <FormLabel>Timeout (seconds)</FormLabel>
                    <NumberInput
                      value={formData.timeout}
                      onChange={(_, value) => handleInputChange('timeout', value || 30)}
                      min={1}
                      max={300}
                    >
                      <NumberInputField />
                      <NumberInputStepper>
                        <NumberIncrementStepper />
                        <NumberDecrementStepper />
                      </NumberInputStepper>
                    </NumberInput>
                  </FormControl>
                </HStack>

                <FormControl>
                  <FormLabel>Headers (JSON format)</FormLabel>
                  <Textarea
                    value={formData.headers}
                    onChange={(e) => handleInputChange('headers', e.target.value)}
                    placeholder='{"Authorization": "Bearer token", "Content-Type": "application/json"}'
                    rows={3}
                  />
                </FormControl>
              </>
            )}

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
            loadingText={isEditMode ? 'Updating...' : 'Creating...'}
          >
            {isEditMode ? 'Update Task' : 'Create Task'}
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}

export default TaskEditModal