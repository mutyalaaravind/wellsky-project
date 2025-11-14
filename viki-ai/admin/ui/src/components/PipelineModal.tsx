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
  VStack,
  HStack,
  Text,
  Divider,
  useToast,
  FormErrorMessage,
  Select,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Box,
} from '@chakra-ui/react'
import { useState, useEffect } from 'react'
import { Pipeline, PipelineCreateRequest, PipelineUpdateRequest } from '../services/pipelinesService'
import PipelineFlowDiagram from './PipelineFlowDiagram'

interface PipelineModalProps {
  isOpen: boolean
  onClose: () => void
  onSave: (pipeline: PipelineCreateRequest | PipelineUpdateRequest) => Promise<{ success: boolean; error?: string }>
  pipeline?: Pipeline
  mode: 'create' | 'edit'
}

const PipelineModal: React.FC<PipelineModalProps> = ({
  isOpen,
  onClose,
  onSave,
  pipeline,
  mode,
}) => {
  const toast = useToast()
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})
  
  // Form state
  const [formData, setFormData] = useState({
    key: '',
    name: '',
    version: '',
    scope: 'default',
    solution_code: '',
    app_id: '',
    description: '',
    output_entity: '',
    auto_publish_entities_enabled: true,
    active: true,
  })

  // Initialize form data when modal opens or pipeline changes
  useEffect(() => {
    if (isOpen) {
      if (mode === 'edit' && pipeline) {
        setFormData({
          key: pipeline.key,
          name: pipeline.name,
          version: pipeline.version || '',
          scope: pipeline.scope,
          solution_code: pipeline.solution_code || '',
          app_id: pipeline.app_id || '',
          description: pipeline.description || '',
          output_entity: pipeline.output_entity || '',
          auto_publish_entities_enabled: pipeline.auto_publish_entities_enabled ?? true,
          active: pipeline.active,
        })
      } else {
        // Reset form for create mode
        setFormData({
          key: '',
          name: '',
          version: '1.0.0',
          scope: 'default',
          solution_code: '',
          app_id: '',
          description: '',
          output_entity: '',
          auto_publish_entities_enabled: true,
          active: true,
        })
      }
      setErrors({})
    }
  }, [isOpen, mode, pipeline])

  const validateForm = () => {
    const newErrors: Record<string, string> = {}
    
    if (!formData.key.trim()) newErrors.key = 'Pipeline key is required'
    if (!formData.name.trim()) newErrors.name = 'Pipeline name is required'
    if (!formData.scope.trim()) newErrors.scope = 'Scope is required'
    
    // Validate key format (should be lowercase with underscores/hyphens)
    if (formData.key && !/^[a-z0-9_-]+$/.test(formData.key)) {
      newErrors.key = 'Key must contain only lowercase letters, numbers, underscores, and hyphens'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async () => {
    if (!validateForm()) return
    
    setLoading(true)
    try {
      const pipelineData = {
        key: formData.key,
        name: formData.name,
        version: formData.version,
        scope: formData.scope,
        solution_code: formData.solution_code,
        app_id: formData.app_id,
        description: formData.description,
        output_entity: formData.output_entity,
        auto_publish_entities_enabled: formData.auto_publish_entities_enabled,
        active: formData.active,
        tasks: mode === 'create' ? [] : undefined, // Only include tasks for create mode
      }

      const result = await onSave(pipelineData)
      
      if (result.success) {
        toast({
          title: `Pipeline ${mode === 'create' ? 'created' : 'updated'}`,
          description: `${formData.name} has been successfully ${mode === 'create' ? 'created' : 'updated'}.`,
          status: 'success',
          duration: 3000,
          isClosable: true,
        })
        onClose()
      } else {
        toast({
          title: 'Operation failed',
          description: result.error || `Failed to ${mode} pipeline`,
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

  return (
    <Modal isOpen={isOpen} onClose={onClose} scrollBehavior="inside">
      <ModalOverlay />
      <ModalContent maxW="90vw" w="90vw">
        <ModalHeader>
          {mode === 'create' ? 'Create Pipeline' : 'Edit Pipeline'}
        </ModalHeader>
        <ModalCloseButton />
        
        <ModalBody>
          <Tabs colorScheme="blue">
            <TabList>
              <Tab>Basic Information</Tab>
              <Tab>Pipeline</Tab>
            </TabList>
            
            <TabPanels>
              {/* Basic Information Tab */}
              <TabPanel px={0}>
                <VStack spacing={4} align="stretch">
                  <HStack spacing={4}>
                    <FormControl isInvalid={!!errors.key}>
                      <FormLabel>Pipeline Key</FormLabel>
                      <Input
                        value={formData.key}
                        onChange={(e) => handleInputChange('key', e.target.value)}
                        placeholder="e.g., document_prep"
                        isDisabled={mode === 'edit'} // Don't allow changing key in edit mode
                      />
                      <FormErrorMessage>{errors.key}</FormErrorMessage>
                    </FormControl>
                    
                    <FormControl isInvalid={!!errors.name}>
                      <FormLabel>Pipeline Name</FormLabel>
                      <Input
                        value={formData.name}
                        onChange={(e) => handleInputChange('name', e.target.value)}
                        placeholder="e.g., Document Preparation Pipeline"
                      />
                      <FormErrorMessage>{errors.name}</FormErrorMessage>
                    </FormControl>
                  </HStack>

                  <HStack spacing={4}>
                    <FormControl>
                      <FormLabel>Version</FormLabel>
                      <Input
                        value={formData.version}
                        onChange={(e) => handleInputChange('version', e.target.value)}
                        placeholder="e.g., 1.0.0"
                      />
                    </FormControl>
                    
                    <FormControl isInvalid={!!errors.scope}>
                      <FormLabel>Scope</FormLabel>
                      <Select
                        value={formData.scope}
                        onChange={(e) => handleInputChange('scope', e.target.value)}
                      >
                        <option value="default">default</option>
                        <option value="healthcare">healthcare</option>
                        <option value="analysis">analysis</option>
                        <option value="custom">custom</option>
                      </Select>
                      <FormErrorMessage>{errors.scope}</FormErrorMessage>
                    </FormControl>
                  </HStack>

                  <FormControl>
                    <FormLabel>Description</FormLabel>
                    <Textarea
                      value={formData.description}
                      onChange={(e) => handleInputChange('description', e.target.value)}
                      placeholder="Describe what this pipeline does"
                      rows={3}
                    />
                  </FormControl>

                  <Divider />

                  {/* Application Information */}
                  <Text fontWeight="semibold" color="var(--Secondary-ws-elm-700)">
                    Application Information
                  </Text>

                  <HStack spacing={4}>
                    <FormControl>
                      <FormLabel>Solution Code</FormLabel>
                      <Input
                        value={formData.solution_code}
                        onChange={(e) => handleInputChange('solution_code', e.target.value)}
                        placeholder="e.g., WELLSKY_CORE"
                      />
                    </FormControl>
                    
                    <FormControl>
                      <FormLabel>App ID</FormLabel>
                      <Input
                        value={formData.app_id}
                        onChange={(e) => handleInputChange('app_id', e.target.value)}
                        placeholder="e.g., app_001"
                      />
                    </FormControl>
                  </HStack>

                  <FormControl>
                    <FormLabel>Output Entity</FormLabel>
                    <Input
                      value={formData.output_entity}
                      onChange={(e) => handleInputChange('output_entity', e.target.value)}
                      placeholder="e.g., processed_document"
                    />
                  </FormControl>

                  <Divider />

                  {/* Settings */}
                  <Text fontWeight="semibold" color="var(--Secondary-ws-elm-700)">
                    Settings
                  </Text>

                  <VStack spacing={4} align="stretch">
                    <HStack justify="space-between">
                      <Text fontSize="sm">Auto-publish entities</Text>
                      <FormControl display="flex" alignItems="center" w="auto">
                        <FormLabel mb="0" fontSize="sm">Enabled</FormLabel>
                        <Switch
                          isChecked={formData.auto_publish_entities_enabled}
                          onChange={(e) => handleInputChange('auto_publish_entities_enabled', e.target.checked)}
                          colorScheme="teal"
                        />
                      </FormControl>
                    </HStack>

                    <HStack justify="space-between">
                      <Text fontSize="sm">Pipeline status</Text>
                      <FormControl display="flex" alignItems="center" w="auto">
                        <FormLabel mb="0" fontSize="sm">Active</FormLabel>
                        <Switch
                          isChecked={formData.active}
                          onChange={(e) => handleInputChange('active', e.target.checked)}
                          colorScheme="teal"
                        />
                      </FormControl>
                    </HStack>
                  </VStack>

                  {mode === 'create' && (
                    <>
                      <Divider />
                      <Text fontSize="sm" color="gray.600" fontStyle="italic">
                        Note: After creating the pipeline, you can configure tasks and advanced settings in the Pipeline tab.
                      </Text>
                    </>
                  )}
                </VStack>
              </TabPanel>

              {/* Pipeline Tab */}
              <TabPanel px={0}>
                <VStack spacing={4} align="stretch">
                  <HStack justify="space-between" align="center">
                    <Text fontWeight="semibold" color="var(--Secondary-ws-elm-700)">
                      Pipeline Flow Visualization
                    </Text>
                    <Text fontSize="xs" color="gray.500" fontStyle="italic">
                      💡 Drag from connection points to create custom flows
                    </Text>
                  </HStack>
                  
                  {pipeline && pipeline.tasks && pipeline.tasks.length > 0 ? (
                    <Box
                      w="full"
                      minH="500px"
                      bg="white"
                      borderRadius="lg"
                      border="1px"
                      borderColor="gray.200"
                      p={6}
                      position="relative"
                      overflow="auto"
                    >
                      <PipelineFlowDiagram
                        tasks={pipeline.tasks}
                        pipelineId={pipeline.id}
                        onTaskUpdate={async (updatedTask) => {
                          // Task update handler - to be implemented
                          console.log('Task updated:', updatedTask)
                        }}
                      />
                    </Box>
                  ) : (
                    <Box
                      w="full"
                      h="400px"
                      bg="gray.50"
                      borderRadius="lg"
                      border="2px dashed"
                      borderColor="gray.300"
                      p={6}
                      display="flex"
                      alignItems="center"
                      justifyContent="center"
                    >
                      <VStack spacing={4}>
                        <Text color="gray.500" fontSize="lg" textAlign="center">
                          No Pipeline Tasks
                        </Text>
                        <Text color="gray.400" fontSize="sm" textAlign="center">
                          Add tasks to see the pipeline flow visualization
                        </Text>
                        <Text color="gray.400" fontSize="xs" textAlign="center" maxW="400px">
                          Tasks will be displayed as connected nodes showing the execution flow and dependencies.
                        </Text>
                      </VStack>
                    </Box>
                  )}

                  <Divider />

                  <HStack justify="space-between" align="center">
                    <Text fontWeight="semibold" color="var(--Secondary-ws-elm-700)">
                      Task Management
                    </Text>
                    <Button
                      size="sm"
                      style={{ backgroundColor: 'var(--palette-accent-ws-elm-500)' }}
                      color="white"
                      _hover={{ backgroundColor: 'var(--Secondary-ws-elm-700)' }}
                      onClick={() => {
                        toast({
                          title: 'Add Task',
                          description: 'Task creation interface coming soon...',
                          status: 'info',
                          duration: 3000,
                          isClosable: true,
                        })
                      }}
                    >
                      + Add Task
                    </Button>
                  </HStack>
                  
                  {pipeline && pipeline.tasks && pipeline.tasks.length > 0 ? (
                    <VStack spacing={3} align="stretch">
                      {pipeline.tasks.map((task, index) => (
                        <Box
                          key={task.id}
                          p={4}
                          bg="white"
                          borderRadius="md"
                          border="1px"
                          borderColor="gray.200"
                          _hover={{ borderColor: 'var(--palette-accent-ws-elm-500)', bg: 'gray.50' }}
                          cursor="pointer"
                        >
                          <HStack justify="space-between" align="start">
                            <VStack align="start" spacing={1}>
                              <Text fontWeight="medium">{task.id}</Text>
                              <Text fontSize="sm" color="gray.600">
                                Type: {task.type}
                              </Text>
                              {task.post_processing?.for_each && (
                                <Text fontSize="xs" color="orange.600" bg="orange.50" px={2} py={1} borderRadius="md">
                                  For Each: {task.post_processing.for_each}
                                </Text>
                              )}
                            </VStack>
                            <HStack>
                              <Text fontSize="xs" color="gray.400">
                                Task {index + 1}
                              </Text>
                              <Button size="xs" variant="ghost" colorScheme="blue">
                                Edit
                              </Button>
                            </HStack>
                          </HStack>
                        </Box>
                      ))}
                    </VStack>
                  ) : (
                    <Box
                      p={4}
                      bg="gray.50"
                      borderRadius="md"
                      textAlign="center"
                    >
                      <Text color="gray.500" fontSize="sm">
                        No tasks configured yet. Click "Add Task" to create your first task.
                      </Text>
                    </Box>
                  )}
                </VStack>
              </TabPanel>
            </TabPanels>
          </Tabs>
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
            {mode === 'create' ? 'Create Pipeline' : 'Update Pipeline'}
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}

export default PipelineModal