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
  Card,
  CardBody,
  CardHeader,
  Flex,
  Spacer,
  Input,
  InputGroup,
  InputLeftElement,
  ButtonGroup,
  Code,
  Stat,
  StatLabel,
  StatNumber,
  StatGroup,
  Divider,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  useToast,
  Link as ChakraLink,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  SimpleGrid,
  Progress,
  Select,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  useDisclosure,
  FormControl,
  FormLabel,
  List,
  ListItem,
  IconButton,
  Tooltip,
  AlertDialog,
  AlertDialogOverlay,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogBody,
  AlertDialogFooter,
  Switch,
} from '@chakra-ui/react'
import { useEffect, useState, useRef } from 'react'
import { useParams, useNavigate, Link as RouterLink } from 'react-router-dom'
import { FiArrowLeft, FiEdit, FiPlay, FiRefreshCw, FiExternalLink, FiSearch, FiList, FiCode, FiX, FiTrash2, FiUser } from 'react-icons/fi'
import { cloneDeep } from 'lodash'
import { useApps } from '../hooks/useApps'
import { App } from '../services/appsService'
import { Pipeline, pipelinesService } from '../services/pipelinesService'
import ConfigRenderer from '../components/ConfigRenderer'
import LoggingTab from '../components/LoggingTab'
import MetricChart from '../components/MetricChart'
import { configService } from '../services/configService'
import { getAuthToken } from '../utils/auth'

const AppDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const toast = useToast()
  const { getApp } = useApps()
  
  const [app, setApp] = useState<App | null>(null)
  const [appConfig, setAppConfig] = useState<any>(null)
  const [pipelines, setPipelines] = useState<Pipeline[]>([])
  const [pipelinesLoading, setPipelinesLoading] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isEditMode, setIsEditMode] = useState(false)
  const [filterText, setFilterText] = useState('')
  const [viewMode, setViewMode] = useState<'tree' | 'json'>('tree')
  const [originalAppConfig, setOriginalAppConfig] = useState<any>(null)
  const [subjectName, setSubjectName] = useState('')
  
  // Metrics tab state
  const [metricsHoursBack, setMetricsHoursBack] = useState(24)
  const [metricsAggregationPeriod, setMetricsAggregationPeriod] = useState(60)
  const [subjects, setSubjects] = useState([])
  const [subjectsLoading, setSubjectsLoading] = useState(false)
  const [subjectToDelete, setSubjectToDelete] = useState<{id: string, name: string} | null>(null)
  const [subjectConfig, setSubjectConfig] = useState<{label: string} | null>(null)
  const [editLabel, setEditLabel] = useState('')
  const [isEditingLabel, setIsEditingLabel] = useState(false)
  const { isOpen: isAddSubjectOpen, onOpen: onAddSubjectOpen, onClose: onAddSubjectClose } = useDisclosure()
  const { isOpen: isDeleteOpen, onOpen: onDeleteOpen, onClose: onDeleteClose } = useDisclosure()
  const cancelRef = useRef<HTMLButtonElement>(null)
  
  // Check if there are unsaved changes
  const hasUnsavedChanges = originalAppConfig && appConfig && 
    JSON.stringify(originalAppConfig.config) !== JSON.stringify(appConfig.config)

  const fetchSubjectConfig = async () => {
    if (!id) return
    
    try {
      const apiBaseUrl = await configService.getAdminApiUrl()
      const token = getAuthToken()
      const response = await fetch(`${apiBaseUrl}/api/v1/demo/${id}/config`, {
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` }),
        },
      })
      if (response.ok) {
        const data = await response.json()
        setSubjectConfig(data.data || { label: 'Subject' })
      } else {
        console.error('Failed to fetch subject config:', response.statusText)
        setSubjectConfig({ label: 'Subject' })
      }
    } catch (error) {
      console.error('Error fetching subject config:', error)
      setSubjectConfig({ label: 'Subject' })
    }
  }

  const fetchSubjects = async () => {
    if (!id) return
    
    try {
      setSubjectsLoading(true)
      const apiBaseUrl = await configService.getAdminApiUrl()
      const token = getAuthToken()
      const response = await fetch(`${apiBaseUrl}/api/v1/demo/${id}/subjects`, {
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` }),
        },
      })
      if (response.ok) {
        const data = await response.json()
        setSubjects(data.data || [])
      } else {
        console.error('Failed to fetch subjects:', response.statusText)
      }
    } catch (error) {
      console.error('Error fetching subjects:', error)
    } finally {
      setSubjectsLoading(false)
    }
  }

  const fetchPipelines = async () => {
    if (!id) return
    
    try {
      setPipelinesLoading(true)
      const appPipelines = await pipelinesService.getAllPipelines({ app_id: id })
      setPipelines(appPipelines)
    } catch (error) {
      console.error('Error fetching pipelines:', error)
      toast({
        title: 'Error',
        description: 'Failed to load pipelines from API',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setPipelinesLoading(false)
    }
  }

  useEffect(() => {
    const fetchApp = async () => {
      if (!id) {
        setError('App ID not provided')
        setLoading(false)
        return
      }

      try {
        setLoading(true)
        setError(null)
        const appData = await getApp(id)
        if (appData) {
          setApp(appData)
          // Fetch the raw config data
          const apiBaseUrl = await configService.getAdminApiUrl()
          const token = getAuthToken()
          const configResponse = await fetch(`${apiBaseUrl}/api/v1/config/app/${appData.app_id}`, {
            headers: {
              'Content-Type': 'application/json',
              ...(token && { 'Authorization': `Bearer ${token}` }),
            },
          })
          if (configResponse.ok) {
            const configData = await configResponse.json()
            setAppConfig(configData.data)
            setOriginalAppConfig(configData.data)
          }
          // Fetch subjects, pipelines, and config for this app
          fetchSubjects()
          fetchSubjectConfig()
          fetchPipelines()
        } else {
          setError('App not found')
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load app')
      } finally {
        setLoading(false)
      }
    }

    fetchApp()
  }, [id, getApp])

  const formatDateTime = (dateString?: string) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleString()
  }

  // Helper functions for dynamic labels
  const getSubjectLabel = () => {
    return subjectConfig?.label || 'Subject'
  }

  const getSubjectLabelPlural = () => {
    const label = getSubjectLabel()
    // Simple pluralization - add 's' if doesn't already end with 's'
    return label.toLowerCase().endsWith('s') ? label : `${label}s`
  }

  const getSubjectLabelLowerPlural = () => {
    return getSubjectLabelPlural().toLowerCase()
  }

  const saveSubjectLabel = async (newLabel: string) => {
    if (!id) return
    
    // Strip trailing 's' to make label singular
    const singularLabel = newLabel.trim().toLowerCase().endsWith('s') 
      ? newLabel.trim().slice(0, -1) 
      : newLabel.trim()
    
    try {
      const apiBaseUrl = await configService.getAdminApiUrl()
      const token = getAuthToken()
      const response = await fetch(`${apiBaseUrl}/api/v1/demo/${id}/config`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` }),
        },
        body: JSON.stringify({
          label: singularLabel
        })
      })

      if (response.ok) {
        const data = await response.json()
        setSubjectConfig(data.data)
        toast({
          title: 'Success',
          description: 'Label updated successfully',
          status: 'success',
          duration: 3000,
          isClosable: true,
        })
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: `Failed to update label: ${error instanceof Error ? error.message : 'Unknown error'}`,
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    }
  }


  if (loading) {
    return (
      <VStack spacing={4} align="center" pt={8}>
        <Spinner size="lg" color="var(--palette-accent-ws-elm-500)" />
        <Text>Loading app details...</Text>
      </VStack>
    )
  }

  if (error || !app) {
    return (
      <Box>
        <Button
          leftIcon={<FiArrowLeft />}
          variant="ghost"
          onClick={() => navigate('/apps')}
          mb={4}
        >
          Back to Apps
        </Button>
        <Alert status="error">
          <AlertIcon />
          {error || 'App not found'}
        </Alert>
      </Box>
    )
  }


  return (
    <Box>
      {/* Header */}
      <Flex align="center" mb={6}>
        <Button
          leftIcon={<FiArrowLeft />}
          variant="ghost"
          onClick={() => navigate('/apps')}
          mr={4}
        >
          Back to Apps
        </Button>
        <Box>
          <Heading as="h1" size="lg" mb={1} color="var(--Secondary-ws-elm-700)">
            {app.name}
          </Heading>
          <Text color="gray.600">{app.description || 'No description available'}</Text>
        </Box>
        <Spacer />
        <Button
          variant="outline"
          onClick={() => {
            if (appConfig) {
              const dataStr = JSON.stringify(appConfig.config.config, null, 2)
              const dataBlob = new Blob([dataStr], {type: 'application/json'})
              const url = URL.createObjectURL(dataBlob)
              const link = document.createElement('a')
              link.href = url
              link.download = `config-${appConfig.app_id}-data.json`
              link.click()
              URL.revokeObjectURL(url)
              toast({
                title: 'Configuration Exported',
                description: 'Configuration data downloaded as JSON file',
                status: 'success',
                duration: 3000,
                isClosable: true,
              })
            }
          }}
        >
          Export JSON
        </Button>
      </Flex>

      {/* Tabs */}
      <Tabs colorScheme="blue">
        <TabList>
          <Tab>General</Tab>
          <Tab>Experiment</Tab>
          <Tab>Integration</Tab>
          <Tab>Reports</Tab>
          <Tab>Cost</Tab>
          <Tab>Testing</Tab>
          <Tab>Metrics</Tab>
          <Tab>Logging</Tab>
          <Tab>Config</Tab>
        </TabList>
        
        <TabPanels>
          {/* General Tab */}
          <TabPanel px={0}>
            <VStack spacing={6} align="stretch">
        {/* Status and Basic Info */}
        <Card>
          <CardHeader>
            <Heading size="md">App Overview</Heading>
          </CardHeader>
          <CardBody>
            <StatGroup>
              <Stat>
                <StatLabel>App ID</StatLabel>
                <StatNumber fontSize="md">{app.app_id}</StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Solution Code</StatLabel>
                <StatNumber>
                  <Badge variant="outline" colorScheme="blue" fontSize="sm">
                    {app.solution_code}
                  </Badge>
                </StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Version</StatLabel>
                <StatNumber>
                  <Badge variant="outline" colorScheme="purple" fontSize="sm">
                    {app.version}
                  </Badge>
                </StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Status</StatLabel>
                <StatNumber>
                  <Badge
                    colorScheme={app.active ? 'green' : 'red'}
                    variant="subtle"
                    fontSize="sm"
                  >
                    {app.status}
                  </Badge>
                </StatNumber>
              </Stat>
            </StatGroup>
            
            <Divider my={4} />
            
            <StatGroup>
              <Stat>
                <StatLabel>Created</StatLabel>
                <StatNumber fontSize="md">{formatDateTime(app.created_at)}</StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Created By</StatLabel>
                <StatNumber fontSize="md">{app.created_by || 'Unknown'}</StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Modified</StatLabel>
                <StatNumber fontSize="md">{formatDateTime(app.modified_at)}</StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Modified By</StatLabel>
                <StatNumber fontSize="md">{app.modified_by || 'Unknown'}</StatNumber>
              </Stat>
            </StatGroup>
          </CardBody>
        </Card>

        {/* Pipelines */}
        <Card>
          <CardHeader>
            <Flex align="center">
              <Heading size="md">Pipelines ({pipelines.length})</Heading>
              <Spacer />
              <Button
                size="sm"
                leftIcon={<FiRefreshCw />}
                variant="outline"
                isLoading={pipelinesLoading}
                onClick={() => {
                  fetchPipelines()
                  toast({
                    title: 'Refresh',
                    description: 'Refreshing pipeline data...',
                    status: 'info',
                    duration: 2000,
                    isClosable: true,
                  })
                }}
              >
                Refresh
              </Button>
            </Flex>
          </CardHeader>
          <CardBody>
            {pipelinesLoading ? (
              <Flex justify="center" py={4}>
                <Spinner size="md" color="var(--palette-accent-ws-elm-500)" />
                <Text ml={3}>Loading pipelines...</Text>
              </Flex>
            ) : pipelines.length === 0 ? (
              <Alert status="info">
                <AlertIcon />
                No pipelines configured for this app.
              </Alert>
            ) : (
              <Table variant="simple">
                <Thead>
                  <Tr>
                    <Th>Pipeline Name</Th>
                    <Th>Scope</Th>
                    <Th>Key</Th>
                    <Th>Number of Steps</Th>
                    <Th>Invokes other pipelines</Th>
                    <Th>Status</Th>
                    <Th>Modified</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {pipelines.map((pipeline) => (
                    <Tr key={pipeline.id}>
                      <Td>
                        <VStack align="start" spacing={1}>
                          <ChakraLink
                            as={RouterLink}
                            to={`/pipelines/${encodeURIComponent(pipeline.id)}?from=app&appId=${app.app_id}&appName=${encodeURIComponent(app.name)}`}
                            fontWeight="medium"
                            color="var(--palette-accent-ws-elm-500)"
                            _hover={{ 
                              color: 'var(--Secondary-ws-elm-700)',
                              textDecoration: 'underline'
                            }}
                            display="flex"
                            alignItems="center"
                            gap={1}
                          >
                            {pipeline.name}
                            <FiExternalLink size={12} />
                          </ChakraLink>
                          {pipeline.description && (
                            <Tooltip label={pipeline.description} placement="top" hasArrow>
                              <Text fontSize="sm" color="gray.500" noOfLines={1} maxW="300px" cursor="help">
                                {pipeline.description}
                              </Text>
                            </Tooltip>
                          )}
                        </VStack>
                      </Td>
                      <Td>
                        <Text fontSize="sm">{pipeline.scope}</Text>
                      </Td>
                      <Td>
                        <Code fontSize="sm" colorScheme="gray">{pipeline.key}</Code>
                      </Td>
                      <Td>
                        <Text fontSize="sm">{pipeline.tasks.length}</Text>
                      </Td>
                      <Td>
                        <Badge
                          colorScheme={pipeline.tasks.some(task => task.type === 'pipeline') ? 'blue' : 'gray'}
                          variant="subtle"
                          fontSize="xs"
                        >
                          {pipeline.tasks.some(task => task.type === 'pipeline') ? 'Yes' : 'No'}
                        </Badge>
                      </Td>
                      <Td>
                        <Badge
                          colorScheme={pipeline.active ? 'green' : 'gray'}
                          variant="subtle"
                        >
                          {pipeline.active ? 'Active' : 'Inactive'}
                        </Badge>
                      </Td>
                      <Td>
                        <Text fontSize="sm">{formatDateTime(pipeline.updated_at)}</Text>
                      </Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            )}
          </CardBody>
        </Card>

            </VStack>
          </TabPanel>

          {/* Experiment Tab */}
          <TabPanel px={0}>
            <VStack spacing={6} align="stretch">
              <Card>
                <CardHeader>
                  <Flex align="center">
                    <HStack spacing={2}>
                      {isEditingLabel ? (
                        <HStack spacing={2}>
                          <Input
                            value={editLabel}
                            onChange={(e) => setEditLabel(e.target.value)}
                            size="md"
                            fontSize="lg"
                            fontWeight="semibold"
                            placeholder="Enter label name"
                            autoFocus
                            onKeyPress={(e) => {
                              if (e.key === 'Enter') {
                                if (editLabel.trim()) {
                                  saveSubjectLabel(editLabel)
                                  setIsEditingLabel(false)
                                }
                              } else if (e.key === 'Escape') {
                                setIsEditingLabel(false)
                                setEditLabel('')
                              }
                            }}
                          />
                          <IconButton
                            aria-label="Save label"
                            icon={<FiPlay />}
                            size="sm"
                            colorScheme="green"
                            variant="ghost"
                            onClick={() => {
                              if (editLabel.trim()) {
                                saveSubjectLabel(editLabel)
                                setIsEditingLabel(false)
                              }
                            }}
                            isDisabled={!editLabel.trim()}
                          />
                          <IconButton
                            aria-label="Cancel edit"
                            icon={<FiX />}
                            size="sm"
                            variant="ghost"
                            onClick={() => {
                              setIsEditingLabel(false)
                              setEditLabel('')
                            }}
                          />
                        </HStack>
                      ) : (
                        <HStack spacing={2}>
                          <Heading size="md">{getSubjectLabelPlural()}</Heading>
                          <Tooltip label="Edit label">
                            <IconButton
                              aria-label="Edit label"
                              icon={<FiEdit />}
                              size="sm"
                              variant="ghost"
                              onClick={() => {
                                setEditLabel(getSubjectLabel())
                                setIsEditingLabel(true)
                              }}
                            />
                          </Tooltip>
                        </HStack>
                      )}
                    </HStack>
                    <Spacer />
                    <Button
                      colorScheme="blue"
                      size="sm"
                      onClick={onAddSubjectOpen}
                    >
                      Add {getSubjectLabel()}
                    </Button>
                  </Flex>
                </CardHeader>
                <CardBody>
                  <Text color="gray.600" mb={4}>
                    Manage experiment {getSubjectLabelLowerPlural()} for testing and evaluation purposes.
                    You can change the label Subject to a different label that is relevant for your use case (e.g. Patient, Contract, etc.).
                  </Text>
                  
                  {subjectsLoading ? (
                    <Flex justify="center" py={4}>
                      <Spinner size="md" color="var(--palette-accent-ws-elm-500)" />
                      <Text ml={3}>Loading {getSubjectLabelLowerPlural()}...</Text>
                    </Flex>
                  ) : subjects.length === 0 ? (
                    <Alert status="info">
                      <AlertIcon />
                      No {getSubjectLabelLowerPlural()} have been created yet. Click "Add {getSubjectLabel()}" to get started.
                    </Alert>
                  ) : (
                    <List spacing={3}>
                      {subjects.map((subject: any) => (
                        <ListItem key={subject.id}>
                          <Card variant="outline" size="sm">
                            <CardBody>
                              <Flex align="center" justify="space-between">
                                <HStack>
                                  <Box
                                    p={2}
                                    bg="blue.50"
                                    borderRadius="md"
                                    color="blue.600"
                                  >
                                    <FiUser size={16} />
                                  </Box>
                                  <VStack align="start" spacing={0}>
                                    <ChakraLink
                                      as={RouterLink}
                                      to={`/apps/${id}/subjects/${subject.id}`}
                                      fontWeight="medium"
                                      color="var(--palette-accent-ws-elm-500)"
                                      _hover={{ 
                                        color: 'var(--Secondary-ws-elm-700)',
                                        textDecoration: 'underline'
                                      }}
                                    >
                                      {subject.name}
                                    </ChakraLink>
                                    <Text fontSize="sm" color="gray.500">
                                      Created {formatDateTime(subject.created_at)}
                                    </Text>
                                  </VStack>
                                </HStack>
                                <HStack spacing={2}>
                                  <Tooltip label={`Delete ${getSubjectLabel().toLowerCase()}`}>
                                    <IconButton
                                      aria-label={`Delete ${getSubjectLabel().toLowerCase()}`}
                                      icon={<FiTrash2 />}
                                      size="sm"
                                      variant="ghost"
                                      colorScheme="red"
                                      onClick={() => {
                                        setSubjectToDelete(subject)
                                        onDeleteOpen()
                                      }}
                                    />
                                  </Tooltip>
                                </HStack>
                              </Flex>
                            </CardBody>
                          </Card>
                        </ListItem>
                      ))}
                    </List>
                  )}
                </CardBody>
              </Card>
            </VStack>
          </TabPanel>

          {/* Integration Tab */}
          <TabPanel px={0}>
            <VStack spacing={6} align="stretch">
              <Card>
                <CardHeader>
                  <Flex align="center">
                    <Heading size="md">Integration Settings</Heading>
                    <Spacer />
                    {appConfig?.config && (
                      <Button
                        size="sm"
                        colorScheme="green"
                        leftIcon={<FiPlay />}
                        onClick={async () => {
                          if (!appConfig || !id || !app) return

                          try {
                            const apiBaseUrl = await configService.getAdminApiUrl()
                            const token = getAuthToken()

                            // Step 1: Fetch the absolute latest config from the API to ensure we have all current data
                            const latestConfigResponse = await fetch(`${apiBaseUrl}/api/v1/config/app/${app.app_id}`, {
                              headers: {
                                'Content-Type': 'application/json',
                                ...(token && { 'Authorization': `Bearer ${token}` }),
                              },
                            })

                            if (!latestConfigResponse.ok) {
                              throw new Error(`Failed to fetch latest config: ${latestConfigResponse.status}`)
                            }

                            const latestConfigData = await latestConfigResponse.json()
                            const latestConfig = latestConfigData.data.config

                            // Step 2: Build config that merges ONLY the integration section into the latest config
                            const mergedConfig = {
                              ...latestConfig,  // All sections from latest config (accounting, etc.)
                              integration: appConfig.config.integration  // Replace ONLY integration with our changes
                            }

                            const savePayload = {
                              config: mergedConfig,
                              name: app.name,
                              description: app.description,
                              archive_current: true,
                              version_comment: `Integration config updated at ${new Date().toISOString()}`
                            }

                            // Step 3: Save the merged config
                            const response = await fetch(`${apiBaseUrl}/api/v1/config/app/${app.app_id}`, {
                              method: 'PUT',
                              headers: {
                                'Content-Type': 'application/json',
                                ...(token && { 'Authorization': `Bearer ${token}` }),
                              },
                              body: JSON.stringify(savePayload)
                            })

                            if (response.ok) {
                              // Step 4: Refresh the config from API to get the saved state
                              const configResponse = await fetch(`${apiBaseUrl}/api/v1/config/app/${app.app_id}`, {
                                headers: {
                                  'Content-Type': 'application/json',
                                  ...(token && { 'Authorization': `Bearer ${token}` }),
                                },
                              })
                              if (configResponse.ok) {
                                const configData = await configResponse.json()
                                setAppConfig(configData.data)
                                setOriginalAppConfig(configData.data)
                              }

                              toast({
                                title: 'Integration Config Saved',
                                description: 'Integration configuration has been saved successfully',
                                status: 'success',
                                duration: 5000,
                                isClosable: true,
                              })
                            } else {
                              const errorText = await response.text()
                              console.error('Save failed with response:', errorText)
                              throw new Error(`HTTP ${response.status}: ${response.statusText}`)
                            }
                          } catch (error) {
                            console.error('Save failed:', error)
                            toast({
                              title: 'Save Failed',
                              description: `Failed to save integration configuration: ${error instanceof Error ? error.message : 'Unknown error'}`,
                              status: 'error',
                              duration: 5000,
                              isClosable: true,
                            })
                          }
                        }}
                      >
                        Save Integration Config
                      </Button>
                    )}
                  </Flex>
                </CardHeader>
                <CardBody>
                  <Text color="gray.600" mb={6}>
                    Configure integrations with external systems and services. These settings control how the application communicates with external APIs.
                  </Text>

                  {!appConfig?.config ? (
                    <Alert status="info">
                      <AlertIcon />
                      Loading configuration data...
                    </Alert>
                  ) : (
                    <VStack spacing={6} align="stretch">
                      {/* Base URL */}
                      <FormControl>
                        <FormLabel fontWeight="semibold">Base URL</FormLabel>
                        <Text fontSize="sm" color="gray.600" mb={2}>
                          The base URL for external API integrations
                        </Text>
                        <Input
                          value={appConfig.config?.integration?.base_url || ''}
                          onChange={(e) => {
                            const newConfig = cloneDeep(appConfig)
                            if (!newConfig.config) newConfig.config = {}
                            if (!newConfig.config.integration) {
                              newConfig.config.integration = {}
                            }
                            newConfig.config.integration.base_url = e.target.value
                            setAppConfig(newConfig)
                          }}
                          placeholder="https://api.example.com"
                          size="md"
                        />
                      </FormControl>

                      <Divider />

                      {/* Callback Configuration */}
                      <Box>
                        <Heading size="sm" mb={4}>Callback Configuration</Heading>

                        <VStack spacing={4} align="stretch">
                          {/* Callback Enabled */}
                          <FormControl display="flex" alignItems="center">
                            <FormLabel mb="0" flex="1">
                              <VStack align="start" spacing={0}>
                                <Text fontWeight="medium">Enable Callback</Text>
                                <Text fontSize="sm" color="gray.600">
                                  Enable callbacks to external systems
                                </Text>
                              </VStack>
                            </FormLabel>
                            <Switch
                              isChecked={appConfig.config?.integration?.callback?.enabled || false}
                              onChange={(e) => {
                                const newConfig = cloneDeep(appConfig)
                                if (!newConfig.config) newConfig.config = {}
                                if (!newConfig.config.integration) {
                                  newConfig.config.integration = {}
                                }
                                if (!newConfig.config.integration.callback) {
                                  newConfig.config.integration.callback = {}
                                }
                                newConfig.config.integration.callback.enabled = e.target.checked
                                setAppConfig(newConfig)
                              }}
                              colorScheme="blue"
                            />
                          </FormControl>

                          {/* Callback Endpoint */}
                          <FormControl>
                            <FormLabel fontWeight="medium">Callback Endpoint</FormLabel>
                            <Text fontSize="sm" color="gray.600" mb={2}>
                              The endpoint path to invoke for callbacks (relative to base URL)
                            </Text>
                            <Input
                              value={appConfig.config?.integration?.callback?.endpoint || ''}
                              onChange={(e) => {
                                const newConfig = cloneDeep(appConfig)
                                if (!newConfig.config) newConfig.config = {}
                                if (!newConfig.config.integration) {
                                  newConfig.config.integration = {}
                                }
                                if (!newConfig.config.integration.callback) {
                                  newConfig.config.integration.callback = {}
                                }
                                newConfig.config.integration.callback.endpoint = e.target.value
                                setAppConfig(newConfig)
                              }}
                              placeholder="/api/v1/callback"
                              size="md"
                              isDisabled={!appConfig.config?.integration?.callback?.enabled}
                            />
                          </FormControl>

                          {/* Callback Embed Entities */}
                          <FormControl display="flex" alignItems="center">
                            <FormLabel mb="0" flex="1">
                              <VStack align="start" spacing={0}>
                                <Text fontWeight="medium">Callback Embed Entities</Text>
                                <Text fontSize="sm" color="gray.600">
                                  Include extracted entities in callback payload
                                </Text>
                              </VStack>
                            </FormLabel>
                            <Switch
                              isChecked={appConfig.config?.integration?.callback?.embed_entities_enabled || false}
                              onChange={(e) => {
                                const newConfig = cloneDeep(appConfig)
                                if (!newConfig.config) newConfig.config = {}
                                if (!newConfig.config.integration) {
                                  newConfig.config.integration = {}
                                }
                                if (!newConfig.config.integration.callback) {
                                  newConfig.config.integration.callback = {}
                                }
                                newConfig.config.integration.callback.embed_entities_enabled = e.target.checked
                                setAppConfig(newConfig)
                              }}
                              colorScheme="blue"
                              isDisabled={!appConfig.config?.integration?.callback?.enabled}
                            />
                          </FormControl>

                          {/* Status Callback */}
                          <FormControl>
                            <FormLabel fontWeight="medium">Status Callback Endpoint</FormLabel>
                            <Text fontSize="sm" color="gray.600" mb={2}>
                              The endpoint path for status update callbacks
                            </Text>
                            <Input
                              value={appConfig.config?.integration?.callback?.status_callback || ''}
                              onChange={(e) => {
                                const newConfig = cloneDeep(appConfig)
                                if (!newConfig.config) newConfig.config = {}
                                if (!newConfig.config.integration) {
                                  newConfig.config.integration = {}
                                }
                                if (!newConfig.config.integration.callback) {
                                  newConfig.config.integration.callback = {}
                                }
                                newConfig.config.integration.callback.status_callback = e.target.value
                                setAppConfig(newConfig)
                              }}
                              placeholder="/api/v1/status"
                              size="md"
                              isDisabled={!appConfig.config?.integration?.callback?.enabled}
                            />
                          </FormControl>

                          {/* HTTP Headers */}
                          <Box>
                            <FormLabel fontWeight="medium">HTTP Headers</FormLabel>
                            <Text fontSize="sm" color="gray.600" mb={3}>
                              Custom HTTP headers to include in API requests
                            </Text>

                            <VStack spacing={3} align="stretch">
                              {Object.entries(appConfig.config?.integration?.callback?.headers || {}).map(([key, value], index) => (
                                <HStack key={index} spacing={2}>
                                  <Input
                                    value={key}
                                    onChange={(e) => {
                                      const newConfig = cloneDeep(appConfig)
                                      if (!newConfig.config) newConfig.config = {}
                                      if (!newConfig.config.integration) {
                                        newConfig.config.integration = {}
                                      }
                                      if (!newConfig.config.integration.callback) {
                                        newConfig.config.integration.callback = {}
                                      }
                                      if (!newConfig.config.integration.callback.headers) {
                                        newConfig.config.integration.callback.headers = {}
                                      }

                                      // Remove old key and add new key
                                      const headers = {...newConfig.config.integration.callback.headers}
                                      delete headers[key]
                                      headers[e.target.value] = value
                                      newConfig.config.integration.callback.headers = headers
                                      setAppConfig(newConfig)
                                    }}
                                    placeholder="Header name"
                                    size="sm"
                                    flex="1"
                                    isDisabled={!appConfig.config?.integration?.callback?.enabled}
                                  />
                                  <Input
                                    value={value as string}
                                    onChange={(e) => {
                                      const newConfig = cloneDeep(appConfig)
                                      if (!newConfig.config) newConfig.config = {}
                                      if (!newConfig.config.integration) {
                                        newConfig.config.integration = {}
                                      }
                                      if (!newConfig.config.integration.callback) {
                                        newConfig.config.integration.callback = {}
                                      }
                                      if (!newConfig.config.integration.callback.headers) {
                                        newConfig.config.integration.callback.headers = {}
                                      }
                                      newConfig.config.integration.callback.headers[key] = e.target.value
                                      setAppConfig(newConfig)
                                    }}
                                    placeholder="Header value"
                                    size="sm"
                                    flex="2"
                                    isDisabled={!appConfig.config?.integration?.callback?.enabled}
                                  />
                                  <IconButton
                                    aria-label="Delete header"
                                    icon={<FiTrash2 />}
                                    size="sm"
                                    colorScheme="red"
                                    variant="ghost"
                                    onClick={() => {
                                      const newConfig = cloneDeep(appConfig)
                                      if (newConfig.config?.integration?.callback?.headers) {
                                        const headers = {...newConfig.config.integration.callback.headers}
                                        delete headers[key]
                                        newConfig.config.integration.callback.headers = headers
                                        setAppConfig(newConfig)
                                      }
                                    }}
                                    isDisabled={!appConfig.config?.integration?.callback?.enabled}
                                  />
                                </HStack>
                              ))}

                              <Button
                                size="sm"
                                variant="outline"
                                leftIcon={<FiEdit />}
                                onClick={() => {
                                  const newConfig = cloneDeep(appConfig)
                                  if (!newConfig.config) newConfig.config = {}
                                  if (!newConfig.config.integration) {
                                    newConfig.config.integration = {}
                                  }
                                  if (!newConfig.config.integration.callback) {
                                    newConfig.config.integration.callback = {}
                                  }
                                  if (!newConfig.config.integration.callback.headers) {
                                    newConfig.config.integration.callback.headers = {}
                                  }

                                  // Add a new empty header
                                  let i = 1
                                  while (newConfig.config.integration.callback.headers[`new-header-${i}`]) {
                                    i++
                                  }
                                  newConfig.config.integration.callback.headers[`new-header-${i}`] = ''
                                  setAppConfig(newConfig)
                                }}
                                isDisabled={!appConfig.config?.integration?.callback?.enabled}
                              >
                                Add Header
                              </Button>
                            </VStack>
                          </Box>

                          {/* Cloud Task Enabled */}
                          <FormControl display="flex" alignItems="center">
                            <FormLabel mb="0" flex="1">
                              <VStack align="start" spacing={0}>
                                <Text fontWeight="medium">Cloud Task Enabled</Text>
                                <Text fontSize="sm" color="gray.600">
                                  Use Cloud Tasks for callback delivery
                                </Text>
                              </VStack>
                            </FormLabel>
                            <Switch
                              isChecked={appConfig.config?.integration?.callback?.cloudtask_enabled || false}
                              onChange={(e) => {
                                const newConfig = cloneDeep(appConfig)
                                if (!newConfig.config) newConfig.config = {}
                                if (!newConfig.config.integration) {
                                  newConfig.config.integration = {}
                                }
                                if (!newConfig.config.integration.callback) {
                                  newConfig.config.integration.callback = {}
                                }
                                newConfig.config.integration.callback.cloudtask_enabled = e.target.checked
                                setAppConfig(newConfig)
                              }}
                              colorScheme="blue"
                              isDisabled={!appConfig.config?.integration?.callback?.enabled}
                            />
                          </FormControl>
                        </VStack>
                      </Box>

                      {/* Current Configuration Display */}
                      {appConfig.config?.integration && (
                        <Box>
                          <Heading size="sm" mb={2}>Current Configuration</Heading>
                          <Code
                            display="block"
                            whiteSpace="pre-wrap"
                            fontSize="sm"
                            p={4}
                            borderRadius="md"
                            bg="gray.50"
                          >
                            {JSON.stringify(appConfig.config.integration, null, 2)}
                          </Code>
                        </Box>
                      )}
                    </VStack>
                  )}
                </CardBody>
              </Card>
            </VStack>
          </TabPanel>

          {/* Reports Tab */}
          <TabPanel px={0}>
            <VStack spacing={6} align="stretch">
              <Card>
                <CardHeader>
                  <Heading size="md">Reports & Analytics</Heading>
                </CardHeader>
                <CardBody>
                  <Text color="gray.600" mb={4}>
                    Generate and view detailed reports about your app's performance, usage, and operational metrics.
                  </Text>
                  <Alert status="info">
                    <AlertIcon />
                    Report generation functionality is coming soon. You'll be able to create custom reports and export data.
                  </Alert>
                </CardBody>
              </Card>
            </VStack>
          </TabPanel>

          {/* Cost Tab */}
          <TabPanel px={0}>
            <VStack spacing={6} align="stretch">
              <Card>
                <CardHeader>
                  <Heading size="md">Cost Analysis</Heading>
                </CardHeader>
                <CardBody>
                  <Text color="gray.600" mb={4}>
                    Monitor and analyze costs associated with your application's resource usage and operations.
                  </Text>
                  <Alert status="info">
                    <AlertIcon />
                    Cost tracking and analysis features are coming soon. You'll be able to view detailed cost breakdowns and usage forecasts.
                  </Alert>
                </CardBody>
              </Card>
            </VStack>
          </TabPanel>

          {/* Testing Tab */}
          <TabPanel px={0}>
            <VStack spacing={6} align="stretch">
              {/* Test Suites */}
              <Card>
                <CardHeader>
                  <Flex align="center">
                    <Heading size="md">Test Suites</Heading>
                    <Spacer />
                    <Button 
                      size="sm" 
                      colorScheme="blue"
                      onClick={() => {
                        toast({
                          title: 'Run Tests',
                          description: 'Test execution functionality coming soon',
                          status: 'info',
                          duration: 3000,
                          isClosable: true,
                        })
                      }}
                    >
                      Run All Tests
                    </Button>
                  </Flex>
                </CardHeader>
                <CardBody>
                  <VStack spacing={4} align="stretch">
                    <Box p={4} border="1px" borderColor="gray.200" borderRadius="md">
                      <HStack justify="space-between" mb={3}>
                        <VStack align="start" spacing={1}>
                          <Text fontWeight="medium">Integration Tests</Text>
                          <Text fontSize="sm" color="gray.600">End-to-end pipeline testing</Text>
                        </VStack>
                        <VStack align="end" spacing={1}>
                          <Badge colorScheme="green" variant="subtle">PASSED</Badge>
                          <Text fontSize="xs" color="gray.500">24/24 tests</Text>
                        </VStack>
                      </HStack>
                      <Progress value={100} colorScheme="green" size="sm" />
                    </Box>

                    <Box p={4} border="1px" borderColor="gray.200" borderRadius="md">
                      <HStack justify="space-between" mb={3}>
                        <VStack align="start" spacing={1}>
                          <Text fontWeight="medium">Unit Tests</Text>
                          <Text fontSize="sm" color="gray.600">Component and function testing</Text>
                        </VStack>
                        <VStack align="end" spacing={1}>
                          <Badge colorScheme="yellow" variant="subtle">PARTIAL</Badge>
                          <Text fontSize="xs" color="gray.500">67/72 tests</Text>
                        </VStack>
                      </HStack>
                      <Progress value={93} colorScheme="yellow" size="sm" />
                    </Box>

                    <Box p={4} border="1px" borderColor="gray.200" borderRadius="md">
                      <HStack justify="space-between" mb={3}>
                        <VStack align="start" spacing={1}>
                          <Text fontWeight="medium">Performance Tests</Text>
                          <Text fontSize="sm" color="gray.600">Load and stress testing</Text>
                        </VStack>
                        <VStack align="end" spacing={1}>
                          <Badge colorScheme="green" variant="subtle">PASSED</Badge>
                          <Text fontSize="xs" color="gray.500">12/12 tests</Text>
                        </VStack>
                      </HStack>
                      <Progress value={100} colorScheme="green" size="sm" />
                    </Box>

                    <Box p={4} border="1px" borderColor="gray.200" borderRadius="md">
                      <HStack justify="space-between" mb={3}>
                        <VStack align="start" spacing={1}>
                          <Text fontWeight="medium">Security Tests</Text>
                          <Text fontSize="sm" color="gray.600">Vulnerability and penetration testing</Text>
                        </VStack>
                        <VStack align="end" spacing={1}>
                          <Badge colorScheme="red" variant="subtle">FAILED</Badge>
                          <Text fontSize="xs" color="gray.500">3/5 tests</Text>
                        </VStack>
                      </HStack>
                      <Progress value={60} colorScheme="red" size="sm" />
                    </Box>
                  </VStack>
                </CardBody>
              </Card>

              {/* Test Coverage */}
              <Card>
                <CardHeader>
                  <Heading size="md">Test Coverage</Heading>
                </CardHeader>
                <CardBody>
                  <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6}>
                    <Box>
                      <Text fontWeight="medium" mb={2}>Code Coverage</Text>
                      <Progress value={87} colorScheme="green" size="lg" />
                      <Text fontSize="sm" color="gray.600" mt={1}>87% of codebase</Text>
                    </Box>
                    <Box>
                      <Text fontWeight="medium" mb={2}>Pipeline Coverage</Text>
                      <Progress value={92} colorScheme="green" size="lg" />
                      <Text fontSize="sm" color="gray.600" mt={1}>92% of pipelines</Text>
                    </Box>
                    <Box>
                      <Text fontWeight="medium" mb={2}>API Coverage</Text>
                      <Progress value={75} colorScheme="yellow" size="lg" />
                      <Text fontSize="sm" color="gray.600" mt={1}>75% of endpoints</Text>
                    </Box>
                  </SimpleGrid>
                </CardBody>
              </Card>

              {/* Recent Test Results */}
              <Card>
                <CardHeader>
                  <Heading size="md">Recent Test Results</Heading>
                </CardHeader>
                <CardBody>
                  <VStack spacing={3} align="stretch">
                    <HStack justify="space-between" p={3} bg="green.50" borderRadius="md">
                      <HStack>
                        <Badge colorScheme="green">PASSED</Badge>
                        <Text fontWeight="medium">Integration Test Suite</Text>
                      </HStack>
                      <Text fontSize="sm" color="gray.600">2 minutes ago</Text>
                    </HStack>
                    <HStack justify="space-between" p={3} bg="yellow.50" borderRadius="md">
                      <HStack>
                        <Badge colorScheme="yellow">SKIPPED</Badge>
                        <Text fontWeight="medium">Load Test - Peak Hours</Text>
                      </HStack>
                      <Text fontSize="sm" color="gray.600">15 minutes ago</Text>
                    </HStack>
                    <HStack justify="space-between" p={3} bg="red.50" borderRadius="md">
                      <HStack>
                        <Badge colorScheme="red">FAILED</Badge>
                        <Text fontWeight="medium">Security Vulnerability Scan</Text>
                      </HStack>
                      <Text fontSize="sm" color="gray.600">1 hour ago</Text>
                    </HStack>
                  </VStack>
                </CardBody>
              </Card>
            </VStack>
          </TabPanel>

          {/* Metrics Tab */}
          <TabPanel px={0}>
            <VStack spacing={6} align="stretch">
              {/* Universal Time Range Controls */}
              <Card>
                <CardBody>
                  <HStack spacing={6} wrap="wrap" align="center">
                    <Text fontWeight="medium" color="var(--Secondary-ws-elm-700)">
                      Time Range Settings:
                    </Text>
                    <HStack>
                      <Text fontSize="sm" color="gray.600">Time Range:</Text>
                      <Select
                        size="sm"
                        value={metricsHoursBack}
                        onChange={(e) => setMetricsHoursBack(Number(e.target.value))}
                        w="auto"
                        minW="120px"
                      >
                        <option value={6}>6 hours</option>
                        <option value={12}>12 hours</option>
                        <option value={24}>24 hours</option>
                        <option value={48}>48 hours</option>
                        <option value={168}>7 days</option>
                      </Select>
                    </HStack>
                    
                    <HStack>
                      <Text fontSize="sm" color="gray.600">Aggregation:</Text>
                      <Select
                        size="sm"
                        value={metricsAggregationPeriod}
                        onChange={(e) => setMetricsAggregationPeriod(Number(e.target.value))}
                        w="auto"
                        minW="120px"
                      >
                        <option value={15}>15 min</option>
                        <option value={30}>30 min</option>
                        <option value={60}>1 hour</option>
                        <option value={240}>4 hours</option>
                        <option value={1440}>1 day</option>
                      </Select>
                    </HStack>
                  </HStack>
                </CardBody>
              </Card>

              {/* Metric Charts Grid */}
              <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
                <MetricChart
                  metricName="pipeline_start_metric"
                  title="Pipeline Starts"
                  description="Number of pipeline executions started over time"
                  color="#3182CE"
                  hoursBack={metricsHoursBack}
                  aggregationPeriod={metricsAggregationPeriod}
                />

                <MetricChart
                  metricName="pipeline_success_metric"
                  title="Pipeline Successes"
                  description="Number of successful pipeline completions over time"
                  color="#38A169"
                  hoursBack={metricsHoursBack}
                  aggregationPeriod={metricsAggregationPeriod}
                />

                <MetricChart
                  metricName="pipeline_failed_metric"
                  title="Pipeline Failures"
                  description="Number of failed pipeline executions over time"
                  color="#E53E3E"
                  hoursBack={metricsHoursBack}
                  aggregationPeriod={metricsAggregationPeriod}
                />
              
              {/* Placeholder for additional metric charts */}
              <Box>
                <Card>
                  <CardHeader>
                    <Heading size="md" color="gray.400">Resource Usage</Heading>
                  </CardHeader>
                  <CardBody>
                    <VStack spacing={4} align="center" py={12}>
                      <Text fontSize="4xl">💾</Text>
                      <VStack spacing={2} align="center">
                        <Text color="gray.500" fontWeight="medium">Chart coming soon</Text>
                        <Text color="gray.400" fontSize="sm" textAlign="center">
                          This will show CPU, memory, and storage usage metrics
                        </Text>
                      </VStack>
                      <Badge colorScheme="orange" variant="subtle">
                        Under Development
                      </Badge>
                    </VStack>
                  </CardBody>
                </Card>
              </Box>
              </SimpleGrid>
            </VStack>
          </TabPanel>

          {/* Logging Tab */}
          <TabPanel px={0}>
            {id && <LoggingTab appId={id} />}
          </TabPanel>

          {/* Config Tab */}
          <TabPanel px={0}>
            <VStack spacing={6} align="stretch">
              {/* Configuration Settings */}
              <Card>
                <CardHeader>
                  <VStack spacing={4} align="stretch">
                    <Flex align="center">
                      <Heading size="md">Configuration Settings</Heading>
                      <Spacer />
                    <HStack spacing={3}>
                      {isEditMode && (
                        <Button
                          leftIcon={<FiX />}
                          size="sm"
                          variant="outline"
                          colorScheme="red"
                          onClick={() => {
                            if (originalAppConfig) {
                              setAppConfig(cloneDeep(originalAppConfig))
                            }
                            setIsEditMode(false)
                            toast({
                              title: 'Changes Cancelled',
                              description: 'All unsaved changes have been reverted',
                              status: 'info',
                              duration: 2000,
                              isClosable: true,
                            })
                          }}
                        >
                          Cancel
                        </Button>
                      )}
                      <Button
                        leftIcon={<FiEdit />}
                        size="sm"
                        variant={isEditMode ? "solid" : "outline"}
                        colorScheme={isEditMode ? "blue" : "gray"}
                        onClick={() => {
                          if (!isEditMode && appConfig) {
                            // Store the current config as backup when entering edit mode
                            setOriginalAppConfig(cloneDeep(appConfig))
                          }
                          setIsEditMode(!isEditMode)
                          toast({
                            title: isEditMode ? 'Edit Mode Disabled' : 'Edit Mode Enabled',
                            description: isEditMode ? 'Configuration is now read-only' : 'You can now edit configuration values',
                            status: 'info',
                            duration: 2000,
                            isClosable: true,
                          })
                        }}
                      >
                        {isEditMode ? 'Done' : 'Edit'}
                      </Button>
                      {!isEditMode && hasUnsavedChanges && (
                        <Button
                          leftIcon={<FiPlay />}
                          size="sm"
                          colorScheme="green"
                          onClick={async () => {
                            if (!appConfig || !id) return
                            
                            try {
                              const savePayload = {
                                config: appConfig.config.config,
                                archive_current: true,
                                version_comment: `Configuration updated at ${new Date().toISOString()}`
                              }

                              const apiBaseUrl = await configService.getAdminApiUrl()
                              const token = getAuthToken()
                              const response = await fetch(`${apiBaseUrl}/api/v1/config/app/${app?.app_id}`, {
                                method: 'PUT',
                                headers: {
                                  'Content-Type': 'application/json',
                                  ...(token && { 'Authorization': `Bearer ${token}` }),
                                },
                                body: JSON.stringify(savePayload)
                              })

                              if (response.ok) {
                                // Instead of relying on response data, refresh from API
                                const configResponse = await fetch(`${apiBaseUrl}/api/v1/config/app/${app?.app_id}`, {
                                  headers: {
                                    'Content-Type': 'application/json',
                                    ...(token && { 'Authorization': `Bearer ${token}` }),
                                  },
                                })
                                if (configResponse.ok) {
                                  const configData = await configResponse.json()
                                  setAppConfig(configData.data)
                                  setOriginalAppConfig(configData.data)
                                }
                                
                                toast({
                                  title: 'Configuration Saved',
                                  description: 'Configuration has been saved with version increment and current config archived',
                                  status: 'success',
                                  duration: 5000,
                                  isClosable: true,
                                })
                              } else {
                                throw new Error(`HTTP ${response.status}: ${response.statusText}`)
                              }
                            } catch (error) {
                              console.error('Save failed:', error)
                              toast({
                                title: 'Save Failed',
                                description: `Failed to save configuration: ${error instanceof Error ? error.message : 'Unknown error'}`,
                                status: 'error',
                                duration: 5000,
                                isClosable: true,
                              })
                            }
                          }}
                        >
                          Save
                        </Button>
                      )}
                      <Button
                        leftIcon={<FiRefreshCw />}
                        size="sm"
                        variant="outline"
                        onClick={() => {
                          const fetchAppConfig = async () => {
                            try {
                              const apiBaseUrl = await configService.getAdminApiUrl()
                              const token = getAuthToken()
                              const configResponse = await fetch(`${apiBaseUrl}/api/v1/config/app/${app?.app_id}`, {
                                headers: {
                                  'Content-Type': 'application/json',
                                  ...(token && { 'Authorization': `Bearer ${token}` }),
                                },
                              })
                              if (configResponse.ok) {
                                const configData = await configResponse.json()
                                setAppConfig(configData.data)
                                setOriginalAppConfig(configData.data)
                                toast({
                                  title: 'Configuration Refreshed',
                                  description: 'Configuration data has been updated',
                                  status: 'success',
                                  duration: 3000,
                                  isClosable: true,
                                })
                              }
                            } catch (error) {
                              toast({
                                title: 'Refresh Failed',
                                description: 'Failed to refresh configuration data',
                                status: 'error',
                                duration: 3000,
                                isClosable: true,
                              })
                            }
                          }
                          fetchAppConfig()
                        }}
                      >
                        Refresh
                      </Button>
                    </HStack>
                  </Flex>
                  
                  {/* Filter and View Controls */}
                  <Flex align="center" gap={4}>
                    <InputGroup maxW="300px">
                      <InputLeftElement pointerEvents="none">
                        <FiSearch color="gray.300" />
                      </InputLeftElement>
                      <Input
                        placeholder="Filter configuration..."
                        value={filterText}
                        onChange={(e) => setFilterText(e.target.value)}
                        size="sm"
                      />
                    </InputGroup>
                    
                    <ButtonGroup isAttached size="sm">
                      <Button
                        leftIcon={<FiList />}
                        variant={viewMode === 'tree' ? 'solid' : 'outline'}
                        onClick={() => setViewMode('tree')}
                      >
                        Tree
                      </Button>
                      <Button
                        leftIcon={<FiCode />}
                        variant={viewMode === 'json' ? 'solid' : 'outline'}
                        onClick={() => setViewMode('json')}
                      >
                        JSON
                      </Button>
                    </ButtonGroup>
                  </Flex>
                  </VStack>
                </CardHeader>
                <CardBody>
                  {!appConfig ? (
                    <Alert status="info">
                      <AlertIcon />
                      Loading configuration data...
                    </Alert>
                  ) : (
                    <Box
                      bg="gray.50"
                      borderRadius="md"
                      border="1px"
                      borderColor="gray.200"
                      maxH="600px"
                      overflowY="auto"
                      p={4}
                    >
                      {viewMode === 'tree' ? (
                        <ConfigRenderer
                          data={appConfig.config}
                          isEditable={isEditMode}
                          filterText={filterText}
                          onUpdate={(path, value) => {
                            // Create a deep copy of the config
                            const newConfig = cloneDeep(appConfig)

                            // Navigate to the correct nested location and update the value
                            let current = newConfig.config.config
                            for (let i = 0; i < path.length - 1; i++) {
                              current = current[path[i]]
                            }
                            current[path[path.length - 1]] = value

                            setAppConfig(newConfig)

                            toast({
                              title: 'Configuration Updated',
                              description: `Updated ${path.join('.')} to ${typeof value === 'object' ? 'object' : value}`,
                              status: 'success',
                              duration: 2000,
                              isClosable: true,
                            })
                          }}
                        />
                      ) : (
                        <Code
                          display="block"
                          whiteSpace="pre-wrap"
                          fontSize="sm"
                          fontFamily="mono"
                          bg="white"
                          p={4}
                          borderRadius="md"
                        >
                          {JSON.stringify(appConfig.config, null, 2)}
                        </Code>
                      )}
                    </Box>
                  )}
                </CardBody>
              </Card>
            </VStack>
          </TabPanel>
        </TabPanels>
      </Tabs>

      {/* Add Subject Modal */}
      <Modal isOpen={isAddSubjectOpen} onClose={onAddSubjectClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Add {getSubjectLabel()}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <FormControl>
              <FormLabel>{getSubjectLabel()} Name</FormLabel>
              <Input
                placeholder={`Enter ${getSubjectLabel().toLowerCase()} name`}
                value={subjectName}
                onChange={(e) => setSubjectName(e.target.value)}
              />
            </FormControl>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={() => {
              setSubjectName('')
              onAddSubjectClose()
            }}>
              Cancel
            </Button>
            <Button 
              colorScheme="blue" 
              onClick={async () => {
                if (!subjectName.trim()) {
                  toast({
                    title: 'Error',
                    description: `${getSubjectLabel()} name is required`,
                    status: 'error',
                    duration: 3000,
                    isClosable: true,
                  })
                  return
                }
                
                try {
                  const apiBaseUrl = await configService.getAdminApiUrl()
                  const token = getAuthToken()
                  const response = await fetch(`${apiBaseUrl}/api/v1/demo/${id}/subjects`, {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json',
                      ...(token && { 'Authorization': `Bearer ${token}` }),
                    },
                    body: JSON.stringify({
                      name: subjectName.trim()
                    })
                  })

                  if (response.ok) {
                    toast({
                      title: 'Success',
                      description: `${getSubjectLabel()} created successfully`,
                      status: 'success',
                      duration: 3000,
                      isClosable: true,
                    })
                    setSubjectName('')
                    onAddSubjectClose()
                    // Refresh subjects list
                    fetchSubjects()
                  } else {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
                  }
                } catch (error) {
                  toast({
                    title: 'Error',
                    description: `Failed to create ${getSubjectLabel().toLowerCase()}: ${error instanceof Error ? error.message : 'Unknown error'}`,
                    status: 'error',
                    duration: 5000,
                    isClosable: true,
                  })
                }
              }}
              isDisabled={!subjectName.trim()}
            >
              Save
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Delete Confirmation Dialog */}
      <AlertDialog
        isOpen={isDeleteOpen}
        leastDestructiveRef={cancelRef}
        onClose={onDeleteClose}
      >
        <AlertDialogOverlay>
          <AlertDialogContent>
            <AlertDialogHeader fontSize="lg" fontWeight="bold">
              Delete {getSubjectLabel()}
            </AlertDialogHeader>

            <AlertDialogBody>
              Are you sure you want to delete "{subjectToDelete?.name}"? This action cannot be undone.
            </AlertDialogBody>

            <AlertDialogFooter>
              <Button ref={cancelRef} onClick={onDeleteClose}>
                Cancel
              </Button>
              <Button 
                colorScheme="red" 
                onClick={async () => {
                  if (!subjectToDelete) return
                  
                  try {
                    const apiBaseUrl = await configService.getAdminApiUrl()
                    const token = getAuthToken()
                    const response = await fetch(`${apiBaseUrl}/api/v1/demo/${id}/subjects/${subjectToDelete.id}`, {
                      method: 'DELETE',
                      headers: {
                        'Content-Type': 'application/json',
                        ...(token && { 'Authorization': `Bearer ${token}` }),
                      },
                    })
                    if (response.ok) {
                      toast({
                        title: 'Success',
                        description: `${getSubjectLabel()} deleted successfully`,
                        status: 'success',
                        duration: 3000,
                        isClosable: true,
                      })
                      fetchSubjects()
                      onDeleteClose()
                      setSubjectToDelete(null)
                    } else {
                      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
                    }
                  } catch (error) {
                    toast({
                      title: 'Error',
                      description: `Failed to delete ${getSubjectLabel().toLowerCase()}: ${error instanceof Error ? error.message : 'Unknown error'}`,
                      status: 'error',
                      duration: 5000,
                      isClosable: true,
                    })
                  }
                }} 
                ml={3}
              >
                Delete
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>
    </Box>
  )
}

export default AppDetailPage