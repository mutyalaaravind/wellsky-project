import React, { useState } from 'react'
import {
  Box,
  VStack,
  HStack,
  Card,
  CardHeader,
  CardBody,
  Heading,
  Text,
  Button,
  Badge,
  Code,
  Alert,
  AlertIcon,
  Flex,
  Spacer,
  Input,
  InputGroup,
  InputLeftElement,
  Select,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  Spinner,
  useToast,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  FormControl,
  FormLabel,
  Switch,
  NumberInput,
  NumberInputField,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
} from '@chakra-ui/react'
import { 
  FiSearch, 
  FiRefreshCw, 
  FiDownload, 
  FiSettings, 
  FiFilter,
  FiMoreVertical,
  FiCopy,
  FiExternalLink
} from 'react-icons/fi'
import { useLogs, useLogConfiguration, useLogAnalytics } from '../hooks/useLogs'
import { LogEntry } from '../services/loggingService'

interface LoggingTabProps {
  appId: string
}

const LoggingTab: React.FC<LoggingTabProps> = ({ appId }) => {
  const toast = useToast()
  const { isOpen: isConfigOpen, onOpen: onConfigOpen, onClose: onConfigClose } = useDisclosure()
  
  // State for log search
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedLevel, setSelectedLevel] = useState('')
  const [timeRange, setTimeRange] = useState('24h')
  
  // Hooks for data
  const { logs, loading: logsLoading, error: logsError, searchLogs, refreshLogs } = useLogs(appId)
  const { config, loading: configLoading, updateConfiguration } = useLogConfiguration(appId)
  const { analytics, loading: analyticsLoading, refreshAnalytics } = useLogAnalytics(appId)

  const handleSearch = () => {
    const searchParams: any = {}
    
    if (searchQuery.trim()) {
      searchParams.query = searchQuery.trim()
    }
    
    if (selectedLevel) {
      searchParams.level = selectedLevel
    }
    
    // Add time range logic
    if (timeRange !== 'all') {
      const now = new Date()
      let startTime: Date
      
      switch (timeRange) {
        case '1h':
          startTime = new Date(now.getTime() - 60 * 60 * 1000)
          break
        case '24h':
          startTime = new Date(now.getTime() - 24 * 60 * 60 * 1000)
          break
        case '7d':
          startTime = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
          break
        default:
          startTime = new Date(now.getTime() - 24 * 60 * 60 * 1000)
      }
      
      searchParams.start_time = startTime.toISOString()
      searchParams.end_time = now.toISOString()
    }
    
    searchLogs(searchParams)
  }

  const handleExportLogs = async () => {
    try {
      // This would trigger an export - for now just show a toast
      toast({
        title: 'Export Started',
        description: 'Log export is being prepared. You will receive a download link when ready.',
        status: 'info',
        duration: 5000,
        isClosable: true,
      })
    } catch (error) {
      toast({
        title: 'Export Failed',
        description: 'Failed to start log export',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    }
  }

  const copyLogEntry = (logEntry: LogEntry) => {
    const logText = `[${logEntry.timestamp}] ${logEntry.level}: ${logEntry.message}`
    navigator.clipboard.writeText(logText)
    toast({
      title: 'Copied',
      description: 'Log entry copied to clipboard',
      status: 'success',
      duration: 2000,
      isClosable: true,
    })
  }

  const getLevelColor = (level: string) => {
    switch (level.toUpperCase()) {
      case 'ERROR':
        return 'red'
      case 'WARN':
        return 'yellow'
      case 'INFO':
        return 'blue'
      case 'DEBUG':
        return 'gray'
      default:
        return 'gray'
    }
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString()
  }

  return (
    <VStack spacing={6} align="stretch">
      {/* Log Analytics */}
      <Card>
        <CardHeader>
          <Flex align="center">
            <Heading size="md">Log Analytics</Heading>
            <Spacer />
            <Button
              size="sm"
              variant="outline"
              leftIcon={<FiRefreshCw />}
              onClick={refreshAnalytics}
              isLoading={analyticsLoading}
            >
              Refresh
            </Button>
          </Flex>
        </CardHeader>
        <CardBody>
          {analyticsLoading ? (
            <Flex justify="center">
              <Spinner />
            </Flex>
          ) : analytics ? (
            <SimpleGrid columns={{ base: 2, md: 4 }} spacing={6}>
              <Stat>
                <StatLabel>Total Entries Today</StatLabel>
                <StatNumber>{analytics.total_entries_today.toLocaleString()}</StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Error Rate (24h)</StatLabel>
                <StatNumber color="red.500">{analytics.error_rate_24h}%</StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Warnings (24h)</StatLabel>
                <StatNumber color="yellow.500">{analytics.warning_count_24h}</StatNumber>
              </Stat>
              <Stat>
                <StatLabel>Storage Size</StatLabel>
                <StatNumber>{analytics.storage_size_mb.toFixed(1)} MB</StatNumber>
              </Stat>
            </SimpleGrid>
          ) : (
            <Alert status="info">
              <AlertIcon />
              No analytics data available
            </Alert>
          )}
        </CardBody>
      </Card>

      {/* Log Search and Filters */}
      <Card>
        <CardHeader>
          <Flex align="center">
            <Heading size="md">Search Logs</Heading>
            <Spacer />
            <HStack spacing={2}>
              <Button
                size="sm"
                variant="outline"
                leftIcon={<FiSettings />}
                onClick={onConfigOpen}
              >
                Configure
              </Button>
              <Button
                size="sm"
                variant="outline"
                leftIcon={<FiDownload />}
                onClick={handleExportLogs}
              >
                Export
              </Button>
            </HStack>
          </Flex>
        </CardHeader>
        <CardBody>
          <VStack spacing={4} align="stretch">
            <HStack spacing={4}>
              <InputGroup flex={1}>
                <InputLeftElement pointerEvents="none">
                  <FiSearch color="gray.300" />
                </InputLeftElement>
                <Input
                  placeholder="Search log messages..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                />
              </InputGroup>
              
              <Select
                placeholder="All Levels"
                value={selectedLevel}
                onChange={(e) => setSelectedLevel(e.target.value)}
                w="150px"
              >
                <option value="DEBUG">DEBUG</option>
                <option value="INFO">INFO</option>
                <option value="WARN">WARN</option>
                <option value="ERROR">ERROR</option>
              </Select>
              
              <Select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
                w="100px"
              >
                <option value="1h">1 Hour</option>
                <option value="24h">24 Hours</option>
                <option value="7d">7 Days</option>
                <option value="all">All Time</option>
              </Select>
              
              <Button
                leftIcon={<FiFilter />}
                colorScheme="blue"
                onClick={handleSearch}
                isLoading={logsLoading}
              >
                Search
              </Button>
            </HStack>
          </VStack>
        </CardBody>
      </Card>

      {/* Log Entries */}
      <Card>
        <CardHeader>
          <Flex align="center">
            <Heading size="md">Log Entries</Heading>
            <Spacer />
            <Button
              size="sm"
              variant="outline"
              leftIcon={<FiRefreshCw />}
              onClick={refreshLogs}
              isLoading={logsLoading}
            >
              Refresh
            </Button>
          </Flex>
        </CardHeader>
        <CardBody>
          {logsError ? (
            <Alert status="error">
              <AlertIcon />
              {logsError}
            </Alert>
          ) : logsLoading ? (
            <Flex justify="center" py={8}>
              <Spinner size="lg" />
            </Flex>
          ) : logs.length === 0 ? (
            <Alert status="info">
              <AlertIcon />
              No log entries found for the selected criteria
            </Alert>
          ) : (
            <VStack spacing={4} align="stretch">
              {logs.map((log, index) => {
                // Create full log entry object for JSON view - prioritize original payload if available
                const fullLogEntry = log.metadata.original_json_payload || {
                  timestamp: log.timestamp,
                  level: log.level,
                  message: log.message,
                  source: log.source,
                  app_id: log.app_id,
                  pipeline_id: log.pipeline_id,
                  metadata: log.metadata
                }

                return (
                  <Box
                    key={index}
                    p={4}
                    bg="white"
                    borderRadius="md"
                    border="1px"
                    borderColor="gray.200"
                    shadow="sm"
                  >
                    {/* Header with metadata and actions */}
                    <HStack justify="space-between" mb={3}>
                      <HStack spacing={3}>
                        <Badge colorScheme={getLevelColor(log.level)} variant="subtle">
                          {log.level}
                        </Badge>
                        <Text fontSize="xs" color="gray.500">
                          {formatTimestamp(log.timestamp)}
                        </Text>
                        <Text fontSize="xs" color="gray.500">
                          {log.source}
                        </Text>
                        {log.pipeline_id && (
                          <Badge variant="outline" size="sm">
                            {log.pipeline_id}
                          </Badge>
                        )}
                      </HStack>
                      <Menu>
                        <MenuButton
                          as={Button}
                          size="xs"
                          variant="ghost"
                        >
                          <FiMoreVertical />
                        </MenuButton>
                        <MenuList>
                          <MenuItem icon={<FiCopy />} onClick={() => copyLogEntry(log)}>
                            Copy Message
                          </MenuItem>
                          <MenuItem 
                            icon={<FiCopy />} 
                            onClick={() => {
                              navigator.clipboard.writeText(JSON.stringify(fullLogEntry, null, 2))
                              toast({
                                title: 'Copied',
                                description: 'Full log entry copied to clipboard',
                                status: 'success',
                                duration: 2000,
                                isClosable: true,
                              })
                            }}
                          >
                            Copy Full Entry
                          </MenuItem>
                          <MenuItem icon={<FiExternalLink />}>
                            View in Console
                          </MenuItem>
                        </MenuList>
                      </Menu>
                    </HStack>
                    
                    {/* Primary Message Display */}
                    <Box mb={3}>
                      <Text
                        fontSize="md"
                        lineHeight="1.5"
                        color="gray.800"
                        fontFamily="mono"
                        whiteSpace="pre-wrap"
                        wordBreak="break-word"
                      >
                        {log.message}
                      </Text>
                    </Box>

                    {/* Collapsible JSON Details */}
                    <Accordion allowToggle>
                      <AccordionItem border="none">
                        <AccordionButton
                          px={0}
                          py={2}
                          _hover={{ bg: 'gray.50' }}
                          borderRadius="md"
                        >
                          <Box flex="1" textAlign="left">
                            <Text fontSize="sm" color="gray.600" fontWeight="medium">
                              {log.metadata.original_json_payload ? 'View Original JSON' : 'View Full Log Entry'}
                            </Text>
                          </Box>
                          <AccordionIcon />
                        </AccordionButton>
                        <AccordionPanel px={0} pb={0}>
                          <Code
                            fontSize="xs"
                            display="block"
                            whiteSpace="pre"
                            bg="gray.50"
                            p={3}
                            borderRadius="md"
                            border="1px"
                            borderColor="gray.200"
                            maxHeight="300px"
                            overflowY="auto"
                            fontFamily="mono"
                          >
                            {JSON.stringify(fullLogEntry, null, 2)}
                          </Code>
                        </AccordionPanel>
                      </AccordionItem>
                    </Accordion>
                  </Box>
                )
              })}
            </VStack>
          )}
        </CardBody>
      </Card>

      {/* Configuration Modal */}
      <Modal isOpen={isConfigOpen} onClose={onConfigClose} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Log Configuration</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            {configLoading ? (
              <Flex justify="center" py={8}>
                <Spinner />
              </Flex>
            ) : config ? (
              <VStack spacing={4} align="stretch">
                <FormControl>
                  <FormLabel>Logging Enabled</FormLabel>
                  <Switch
                    isChecked={config.enabled}
                    onChange={(e) =>
                      updateConfiguration({ ...config, enabled: e.target.checked })
                    }
                  />
                </FormControl>
                
                <FormControl>
                  <FormLabel>Log Level</FormLabel>
                  <Select
                    value={config.log_level}
                    onChange={(e) =>
                      updateConfiguration({ ...config, log_level: e.target.value })
                    }
                  >
                    <option value="DEBUG">DEBUG</option>
                    <option value="INFO">INFO</option>
                    <option value="WARN">WARN</option>
                    <option value="ERROR">ERROR</option>
                  </Select>
                </FormControl>
                
                <FormControl>
                  <FormLabel>Retention Period (days)</FormLabel>
                  <NumberInput
                    value={config.retention_days}
                    onChange={(_, valueAsNumber) =>
                      updateConfiguration({ ...config, retention_days: valueAsNumber || 30 })
                    }
                    min={1}
                    max={365}
                  >
                    <NumberInputField />
                  </NumberInput>
                </FormControl>
                
                <Box>
                  <Text fontWeight="medium" mb={2}>Storage Location</Text>
                  <Text color="gray.600" fontSize="sm">{config.storage_location}</Text>
                </Box>
                
                <Box>
                  <Text fontWeight="medium" mb={2}>Log Format</Text>
                  <Text color="gray.600" fontSize="sm">{config.format}</Text>
                </Box>
              </VStack>
            ) : (
              <Alert status="error">
                <AlertIcon />
                Failed to load configuration
              </Alert>
            )}
          </ModalBody>
        </ModalContent>
      </Modal>
    </VStack>
  )
}

export default LoggingTab