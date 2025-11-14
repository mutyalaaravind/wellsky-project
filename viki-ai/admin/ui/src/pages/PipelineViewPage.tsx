import {
  Box,
  Heading,
  Text,
  VStack,
  HStack,
  Badge,
  Spinner,
  Alert,
  AlertIcon,
  Button,
  Flex,
  Spacer,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  FormControl,
  FormLabel,
  Input,
  Textarea,
  Switch,
  Select,
  Divider,
  useToast,
} from '@chakra-ui/react'
import { useEffect, useState, useMemo } from 'react'
import { useParams, useNavigate, useSearchParams } from 'react-router-dom'
import { FiArrowLeft, FiEdit, FiSave } from 'react-icons/fi'
import { Pipeline, pipelinesService } from '../services/pipelinesService'
import PipelineFlowDiagram from '../components/PipelineFlowDiagram'

const PipelineViewPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const toast = useToast()
  const [searchParams] = useSearchParams()
  
  const [pipeline, setPipeline] = useState<Pipeline | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [editData, setEditData] = useState<Partial<Pipeline>>({})

  // Get navigation context from URL params
  const fromApp = searchParams.get('from') === 'app'
  const appId = searchParams.get('appId')
  const appName = searchParams.get('appName')

  useEffect(() => {
    const fetchPipeline = async () => {
      if (!id) {
        setError('Pipeline ID not provided')
        setLoading(false)
        return
      }

      try {
        setLoading(true)
        setError(null)
        
        // Fetch pipeline directly by ID
        const fetchedPipeline = await pipelinesService.getPipeline(id)
        setPipeline(fetchedPipeline)
        setEditData(fetchedPipeline)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load pipeline')
      } finally {
        setLoading(false)
      }
    }

    fetchPipeline()
  }, [id])

  const formatDateTime = (dateString?: string) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleString()
  }

  const handleEdit = () => {
    setIsEditing(true)
  }

  const handleSave = () => {
    // TODO: Implement save functionality
    toast({
      title: 'Pipeline Updated',
      description: 'Pipeline changes saved successfully',
      status: 'success',
      duration: 3000,
      isClosable: true,
    })
    setIsEditing(false)
  }

  const handleCancel = () => {
    setEditData(pipeline || {})
    setIsEditing(false)
  }

  const updateField = (field: string, value: any) => {
    setEditData(prev => ({ ...prev, [field]: value }))
  }

  const handleTaskUpdate = async (updatedTask: any) => {
    if (!pipeline || !id) {
      throw new Error('Pipeline not loaded')
    }

    try {
      // Find the task index in the current pipeline
      const taskIndex = pipeline.tasks.findIndex(t => t.id === updatedTask.id)

      if (taskIndex === -1) {
        throw new Error('Task not found in pipeline')
      }

      // Create a new tasks array with the updated task
      const updatedTasks = [...pipeline.tasks]
      updatedTasks[taskIndex] = updatedTask

      // Use createPipeline since the backend POST endpoint does upsert
      const response = await pipelinesService.createPipeline({
        ...pipeline,  // Preserve ALL pipeline fields (labels, etc.)
        tasks: updatedTasks,  // Override only the tasks array with updated tasks
      })

      if (response.success) {
        // Refresh the pipeline data
        const updatedPipeline = await pipelinesService.getPipeline(id)
        setPipeline(updatedPipeline)
        setEditData(updatedPipeline)

        toast({
          title: 'Task Updated',
          description: 'Task configuration saved successfully',
          status: 'success',
          duration: 3000,
          isClosable: true,
        })
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update task'
      toast({
        title: 'Update Failed',
        description: errorMessage,
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
      throw error
    }
  }

  // Memoize tasks to prevent unnecessary PipelineFlowDiagram re-renders
  // MUST be before conditional returns to comply with Rules of Hooks
  const memoizedTasks = useMemo(() => pipeline?.tasks || [], [pipeline?.tasks])

  if (loading) {
    return (
      <VStack spacing={4} align="center" pt={8}>
        <Spinner size="lg" color="var(--palette-accent-ws-elm-500)" />
        <Text>Loading pipeline details...</Text>
      </VStack>
    )
  }

  const handleBackNavigation = () => {
    if (fromApp && appId) {
      navigate(`/apps/${appId}`)
    } else {
      navigate('/pipelines')
    }
  }

  const getBackButtonText = () => {
    if (fromApp && appName) {
      return `Back to ${decodeURIComponent(appName)}`
    }
    return 'Back to Pipelines'
  }

  if (error || !pipeline) {
    return (
      <Box>
        <Button
          leftIcon={<FiArrowLeft />}
          variant="ghost"
          onClick={handleBackNavigation}
          mb={4}
        >
          {getBackButtonText()}
        </Button>
        <Alert status="error">
          <AlertIcon />
          {error || 'Pipeline not found'}
        </Alert>
      </Box>
    )
  }

  const displayData = isEditing ? editData : pipeline

  return (
    <Box>
      {/* Header */}
      <Flex align="center" mb={6}>
        <Button
          leftIcon={<FiArrowLeft />}
          variant="ghost"
          onClick={handleBackNavigation}
          mr={4}
        >
          {getBackButtonText()}
        </Button>
        <Box>
          <Heading as="h1" size="lg" mb={1} color="var(--Secondary-ws-elm-700)">
            {displayData.name || pipeline.name}
          </Heading>
          <Text color="gray.600">{displayData.description || pipeline.description || 'No description available'}</Text>
        </Box>
        <Spacer />
        <HStack spacing={2}>
          {isEditing ? (
            <>
              <Button
                leftIcon={<FiSave />}
                colorScheme="green"
                onClick={handleSave}
              >
                Save
              </Button>
              <Button
                variant="outline"
                onClick={handleCancel}
              >
                Cancel
              </Button>
            </>
          ) : (
            <Button
              leftIcon={<FiEdit />}
              variant="outline"
              onClick={handleEdit}
            >
              Edit
            </Button>
          )}
        </HStack>
      </Flex>

      {/* Tabs */}
      <Tabs colorScheme="blue">
        <TabList>
          <Tab>General</Tab>
          <Tab>Pipeline</Tab>
          <Tab>Entity</Tab>
        </TabList>
        
        <TabPanels>
          {/* General Tab */}
          <TabPanel px={0}>
            <VStack spacing={6} align="stretch">
              {/* Basic Information */}
              <Box>
                <Heading size="md" mb={4} color="var(--Secondary-ws-elm-700)">
                  Basic Information
                </Heading>
                <VStack spacing={4} align="stretch">
                  <HStack spacing={4}>
                    <FormControl>
                      <FormLabel>App ID</FormLabel>
                      {isEditing ? (
                        <Input
                          value={editData.app_id || ''}
                          onChange={(e) => updateField('app_id', e.target.value)}
                        />
                      ) : (
                        <Text bg="gray.50" p={2} borderRadius="md">{pipeline.app_id || 'N/A'}</Text>
                      )}
                    </FormControl>
                    
                    <FormControl>
                      <FormLabel>Scope</FormLabel>
                      {isEditing ? (
                        <Select
                          value={editData.scope || ''}
                          onChange={(e) => updateField('scope', e.target.value)}
                        >
                          <option value="default">default</option>
                          <option value="healthcare">healthcare</option>
                          <option value="analysis">analysis</option>
                          <option value="custom">custom</option>
                        </Select>
                      ) : (
                        <Text bg="gray.50" p={2} borderRadius="md">{pipeline.scope}</Text>
                      )}
                    </FormControl>
                    
                    <FormControl>
                      <FormLabel>Pipeline Key</FormLabel>
                      {isEditing ? (
                        <Input
                          value={editData.key || ''}
                          onChange={(e) => updateField('key', e.target.value)}
                          isDisabled // Keys typically shouldn't be editable
                        />
                      ) : (
                        <Text bg="gray.50" p={2} borderRadius="md">{pipeline.key}</Text>
                      )}
                    </FormControl>
                    
                    <FormControl>
                      <FormLabel>Version</FormLabel>
                      {isEditing ? (
                        <Input
                          value={editData.version || ''}
                          onChange={(e) => updateField('version', e.target.value)}
                        />
                      ) : (
                        <Text bg="gray.50" p={2} borderRadius="md">{pipeline.version || 'N/A'}</Text>
                      )}
                    </FormControl>
                  </HStack>

                  <HStack spacing={4}>
                    <FormControl>
                      <FormLabel>Pipeline Name</FormLabel>
                      {isEditing ? (
                        <Input
                          value={editData.name || ''}
                          onChange={(e) => updateField('name', e.target.value)}
                        />
                      ) : (
                        <Text bg="gray.50" p={2} borderRadius="md">{pipeline.name}</Text>
                      )}
                    </FormControl>
                    
                    <FormControl>
                      <FormLabel>Description</FormLabel>
                      {isEditing ? (
                        <Textarea
                          value={editData.description || ''}
                          onChange={(e) => updateField('description', e.target.value)}
                          rows={3}
                        />
                      ) : (
                        <Text bg="gray.50" p={2} borderRadius="md">
                          {pipeline.description || 'No description'}
                        </Text>
                      )}
                    </FormControl>
                  </HStack>

                  <HStack spacing={4}>
                    <FormControl>
                      <FormLabel>Status</FormLabel>
                      {isEditing ? (
                        <HStack>
                          <Switch
                            isChecked={editData.active ?? pipeline.active}
                            onChange={(e) => updateField('active', e.target.checked)}
                            colorScheme="teal"
                          />
                          <Text fontSize="sm" color="gray.600">
                            {editData.active ?? pipeline.active ? 'Active' : 'Inactive'}
                          </Text>
                        </HStack>
                      ) : (
                        <Badge colorScheme={pipeline.active ? 'green' : 'red'} p={2}>
                          {pipeline.active ? 'Active' : 'Inactive'}
                        </Badge>
                      )}
                    </FormControl>
                  </HStack>
                </VStack>
              </Box>

              <Divider />

              {/* Settings */}
              <Box>
                <Heading size="md" mb={4} color="var(--Secondary-ws-elm-700)">
                  Settings
                </Heading>
                <VStack spacing={4} align="stretch">
                  <HStack justify="space-between">
                    <Text>Auto-publish entities</Text>
                    {isEditing ? (
                      <Switch
                        isChecked={editData.auto_publish_entities_enabled ?? pipeline.auto_publish_entities_enabled}
                        onChange={(e) => updateField('auto_publish_entities_enabled', e.target.checked)}
                        colorScheme="teal"
                      />
                    ) : (
                      <Badge colorScheme={pipeline.auto_publish_entities_enabled ? 'green' : 'gray'}>
                        {pipeline.auto_publish_entities_enabled ? 'Enabled' : 'Disabled'}
                      </Badge>
                    )}
                  </HStack>
                </VStack>
              </Box>

              <Divider />

              {/* Audit */}
              <Box>
                <Heading size="md" mb={4} color="var(--Secondary-ws-elm-700)">
                  Audit
                </Heading>
                <HStack spacing={4}>
                  <FormControl>
                    <FormLabel>Created</FormLabel>
                    <Text bg="gray.50" p={2} borderRadius="md">{formatDateTime(pipeline.created_at)}</Text>
                  </FormControl>
                  
                  <FormControl>
                    <FormLabel>Created By</FormLabel>
                    <Text bg="gray.50" p={2} borderRadius="md">{pipeline.created_by || 'Unknown'}</Text>
                  </FormControl>
                  
                  <FormControl>
                    <FormLabel>Modified</FormLabel>
                    <Text bg="gray.50" p={2} borderRadius="md">{formatDateTime(pipeline.updated_at)}</Text>
                  </FormControl>
                  
                  <FormControl>
                    <FormLabel>Modified By</FormLabel>
                    <Text bg="gray.50" p={2} borderRadius="md">{pipeline.modified_by || 'Unknown'}</Text>
                  </FormControl>
                </HStack>
              </Box>
            </VStack>
          </TabPanel>

          {/* Pipeline Tab */}
          <TabPanel px={0}>
            <VStack spacing={6} align="stretch">
              {/* Pipeline Flow Visualization */}
              <Box>
                <HStack justify="space-between" align="center" mb={4}>
                  <Heading size="md" color="var(--Secondary-ws-elm-700)">
                    Pipeline Flow Visualization
                  </Heading>
                  <Text fontSize="xs" color="gray.500" fontStyle="italic">
                    💡 Visual representation of pipeline execution flow
                  </Text>
                </HStack>
                
                {pipeline.tasks && pipeline.tasks.length > 0 ? (
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
                      tasks={memoizedTasks}
                      pipelineId={pipeline.id}
                      onTaskUpdate={handleTaskUpdate}
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
                        This pipeline has no configured tasks
                      </Text>
                    </VStack>
                  </Box>
                )}
              </Box>

              <Divider />

              {/* Task List */}
              <Box>
                <HStack justify="space-between" align="center" mb={4}>
                  <Heading size="md" color="var(--Secondary-ws-elm-700)">
                    Pipeline Tasks ({pipeline.tasks?.length || 0})
                  </Heading>
                  <Button
                    size="sm"
                    style={{ backgroundColor: 'var(--palette-accent-ws-elm-500)' }}
                    color="white"
                    _hover={{ backgroundColor: 'var(--Secondary-ws-elm-700)' }}
                    onClick={() => {
                      toast({
                        title: 'Task Management',
                        description: 'Task editing interface coming soon...',
                        status: 'info',
                        duration: 3000,
                        isClosable: true,
                      })
                    }}
                  >
                    Manage Tasks
                  </Button>
                </HStack>
                
                {pipeline.tasks && pipeline.tasks.length > 0 ? (
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
                      >
                        <HStack justify="space-between" align="start">
                          <VStack align="start" spacing={1}>
                            <Text fontWeight="medium">{task.id}</Text>
                            <Badge colorScheme="blue" variant="outline">
                              {task.type}
                            </Badge>
                            {task.post_processing?.for_each && (
                              <Badge colorScheme="orange" variant="subtle" fontSize="xs">
                                For Each: {task.post_processing.for_each}
                              </Badge>
                            )}
                          </VStack>
                          <HStack>
                            <Text fontSize="xs" color="gray.400">
                              Task {index + 1}
                            </Text>
                            <Button size="xs" variant="ghost" colorScheme="blue">
                              View Details
                            </Button>
                          </HStack>
                        </HStack>
                      </Box>
                    ))}
                  </VStack>
                ) : (
                  <Box
                    p={6}
                    bg="gray.50"
                    borderRadius="md"
                    textAlign="center"
                  >
                    <Text color="gray.500" fontSize="sm">
                      No tasks configured yet. Tasks define the processing steps for this pipeline.
                    </Text>
                  </Box>
                )}
              </Box>
            </VStack>
          </TabPanel>

          {/* Entity Tab */}
          <TabPanel px={0}>
            <VStack spacing={6} align="stretch">
              <Box>
                <Heading size="md" mb={4} color="var(--Secondary-ws-elm-700)">
                  Entity Configuration
                </Heading>
                <VStack spacing={4} align="center" py={8}>
                  <Box color="gray.400">
                    <Text fontSize="4xl">🏗️</Text>
                  </Box>
                  <VStack spacing={2} align="center">
                    <Text color="gray.500" fontWeight="medium">Entity management coming soon</Text>
                    <Text color="gray.400" fontSize="sm" textAlign="center">
                      This section will allow you to configure entity extraction rules, 
                      custom entities, and processing settings for this pipeline.
                    </Text>
                  </VStack>
                  <Badge colorScheme="orange" variant="subtle" mt={4}>
                    Under Development
                  </Badge>
                </VStack>
              </Box>
            </VStack>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  )
}

export default PipelineViewPage