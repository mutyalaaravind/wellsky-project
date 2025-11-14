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
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  useToast,
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
  Input,
  IconButton,
  Tooltip,
  Tag,
  TagLabel,
  TagCloseButton,
  Progress,
  Link,
} from '@chakra-ui/react'
import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate, Link as RouterLink } from 'react-router-dom'
import { FiArrowLeft, FiUpload, FiDownload, FiTrash2, FiRefreshCw, FiFile, FiPlus } from 'react-icons/fi'
import { configService } from '../services/configService'
import { getAuthToken } from '../utils/auth'
import { useDocumentStatus } from '../hooks/useDocumentStatus'
import useAsyncTimeInterval from '../hooks/useAsyncTimeInterval'
import { CircularProgressWithLabel } from '../components/CircularProgressWithLabel'

interface Document {
  id: string
  name: string
  uri: string
  metadata: Record<string, string>
  status: 'NOT_STARTED' | 'QUEUED' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED' | 'new' | 'processing' | 'completed' | 'failed'
  created_at: string
  updated_at: string
  size?: number
  content_type?: string
}

interface Subject {
  id: string
  app_id: string
  name: string
  created_at: string
  updated_at: string
  active: boolean
}

interface DocumentStatusDisplayProps {
  document: Document
  appId: string
  subjectId: string
}

const DocumentStatusDisplay: React.FC<DocumentStatusDisplayProps> = ({ document, appId, subjectId }) => {
  const { status, refreshStatus } = useDocumentStatus(appId, subjectId, document.id)

  // Helper function to determine if status is in-flight (should show progress bar)
  const isInFlightStatus = (statusValue: string | undefined): boolean => {
    if (!statusValue) return false
    const lowerStatus = statusValue.toLowerCase()
    return lowerStatus === 'in_progress' || lowerStatus === 'queued'
  }

  // Helper function to determine if status is final (no more updates needed)
  const isFinalStatus = (statusValue: string | undefined): boolean => {
    if (!statusValue) return false
    const lowerStatus = statusValue.toLowerCase()
    return lowerStatus === 'completed' || lowerStatus === 'failed'
  }

  // Poll for status updates every 2 seconds, but only if not in final state
  const pollStatus = useCallback(async () => {
    const currentStatus = status?.status?.status || document.status
    // Only make API call if status is not final
    if (!isFinalStatus(currentStatus)) {
      await refreshStatus()
    }
  }, [refreshStatus, status?.status?.status, document.status, isFinalStatus])

  // Continue polling but make it conditional inside the callback
  useAsyncTimeInterval({ interval: 2000, callback: pollStatus })

  // Show progress bar only for in-flight states with progress data
  if (status?.status?.progress !== null &&
      status?.status?.progress !== undefined &&
      isInFlightStatus(status?.status?.status)) {
    return (
      <HStack spacing={2}>
        <Badge
          colorScheme={
            (status?.status?.status || document.status) === 'completed' || (status?.status?.status || document.status) === 'COMPLETED' ? 'green' :
            (status?.status?.status || document.status) === 'failed' || (status?.status?.status || document.status) === 'FAILED' ? 'red' :
            'blue'
          }
          variant="subtle"
        >
          {status?.status?.status || document.status}
        </Badge>
        <CircularProgressWithLabel value={status.status.progress} size="24px" />
      </HStack>
    )
  }

  // Fallback to regular status badge
  const getStatusBadgeColor = (statusValue: string) => {
    if (!statusValue) return 'gray'

    switch (statusValue.toLowerCase()) {
      case 'completed':
        return 'green'
      case 'processing':
      case 'in_progress':
      case 'queued':
        return 'blue'
      case 'failed':
        return 'red'
      case 'new':
      case 'not_started':
      default:
        return 'gray'
    }
  }

  // The API returns a nested structure: { status: { status: "completed", progress: 1.0 } }
  const apiStatus = status?.status?.status
  const currentStatus = apiStatus || document.status

  // Ensure we have a valid string for the status
  const displayStatus = typeof currentStatus === 'string' ? currentStatus : document.status

  return (
    <Badge
      colorScheme={getStatusBadgeColor(displayStatus)}
      variant="subtle"
    >
      {displayStatus}
    </Badge>
  )
}

const SubjectViewPage: React.FC = () => {
  const { appId, subjectId } = useParams<{ appId: string; subjectId: string }>()
  const navigate = useNavigate()
  const toast = useToast()
  
  const [subject, setSubject] = useState<Subject | null>(null)
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)
  const [subjectConfig, setSubjectConfig] = useState<{label: string} | null>(null)
  
  // Upload modal state
  const { isOpen: isUploadOpen, onOpen: onUploadOpen, onClose: onUploadClose } = useDisclosure()
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [metadata, setMetadata] = useState<Array<{key: string, value: string}>>([])
  const [newMetadataKey, setNewMetadataKey] = useState('')
  const [newMetadataValue, setNewMetadataValue] = useState('')

  const fetchSubjectConfig = async () => {
    if (!appId) return
    
    try {
      const apiBaseUrl = await configService.getAdminApiUrl()
      const token = getAuthToken()
      const response = await fetch(`${apiBaseUrl}/api/v1/demo/${appId}/config`, {
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` }),
        },
      })
      if (response.ok) {
        const data = await response.json()
        setSubjectConfig(data.data || { label: 'Subject' })
      } else {
        setSubjectConfig({ label: 'Subject' })
      }
    } catch (error) {
      console.error('Error fetching subject config:', error)
      setSubjectConfig({ label: 'Subject' })
    }
  }

  const fetchSubject = async () => {
    if (!appId || !subjectId) return
    
    try {
      const apiBaseUrl = await configService.getAdminApiUrl()
      const token = getAuthToken()
      const response = await fetch(`${apiBaseUrl}/api/v1/demo/${appId}/subjects/${subjectId}`, {
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` }),
        },
      })
      if (response.ok) {
        const data = await response.json()
        setSubject(data.data)
      } else {
        throw new Error('Subject not found')
      }
    } catch (error) {
      console.error('Error fetching subject:', error)
      setError(error instanceof Error ? error.message : 'Failed to load subject')
    }
  }

  const fetchDocuments = async () => {
    if (!appId || !subjectId) return
    
    try {
      const apiBaseUrl = await configService.getAdminApiUrl()
      const token = getAuthToken()
      const response = await fetch(`${apiBaseUrl}/api/v1/demo/${appId}/subjects/${subjectId}/documents`, {
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` }),
        },
      })
      if (response.ok) {
        const data = await response.json()
        setDocuments(data.data || [])
      } else {
        console.error('Failed to fetch documents:', response.statusText)
        setDocuments([])
      }
    } catch (error) {
      console.error('Error fetching documents:', error)
      setDocuments([])
    }
  }

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      await Promise.all([
        fetchSubjectConfig(),
        fetchSubject(),
        fetchDocuments()
      ])
      setLoading(false)
    }

    fetchData()
  }, [appId, subjectId])

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString()
  }

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return 'Unknown'
    const units = ['B', 'KB', 'MB', 'GB']
    let size = bytes
    let unitIndex = 0

    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024
      unitIndex++
    }

    return `${size.toFixed(1)} ${units[unitIndex]}`
  }

  const getSubjectLabel = () => {
    return subjectConfig?.label || 'Subject'
  }

  const addMetadataItem = () => {
    if (newMetadataKey.trim() && newMetadataValue.trim()) {
      setMetadata([...metadata, { key: newMetadataKey.trim(), value: newMetadataValue.trim() }])
      setNewMetadataKey('')
      setNewMetadataValue('')
    }
  }

  const removeMetadataItem = (index: number) => {
    setMetadata(metadata.filter((_, i) => i !== index))
  }

  const handleFileUpload = async () => {
    if (!selectedFile || !appId || !subjectId) {
      toast({
        title: 'Error',
        description: 'Please select a file to upload',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
      return
    }

    setUploading(true)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      
      // Add metadata
      const metadataObj = metadata.reduce((acc, item) => {
        acc[item.key] = item.value
        return acc
      }, {} as Record<string, string>)
      
      formData.append('metadata', JSON.stringify(metadataObj))

      const apiBaseUrl = await configService.getAdminApiUrl()
      const token = getAuthToken()
      const response = await fetch(`${apiBaseUrl}/api/v1/demo/${appId}/subjects/${subjectId}/documents`, {
        method: 'POST',
        headers: {
          ...(token && { 'Authorization': `Bearer ${token}` }),
        },
        body: formData
      })

      if (response.ok) {
        toast({
          title: 'Success',
          description: 'Document uploaded successfully',
          status: 'success',
          duration: 3000,
          isClosable: true,
        })
        
        // Reset form
        setSelectedFile(null)
        setMetadata([])
        onUploadClose()
        
        // Refresh documents list
        fetchDocuments()
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
    } catch (error) {
      toast({
        title: 'Upload Failed',
        description: `Failed to upload document: ${error instanceof Error ? error.message : 'Unknown error'}`,
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setUploading(false)
    }
  }

  const deleteDocument = async (documentId: string) => {
    try {
      const apiBaseUrl = await configService.getAdminApiUrl()
      const token = getAuthToken()
      const response = await fetch(`${apiBaseUrl}/api/v1/demo/${appId}/subjects/${subjectId}/documents/${documentId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` }),
        },
      })

      if (response.ok) {
        toast({
          title: 'Success',
          description: 'Document deleted successfully',
          status: 'success',
          duration: 3000,
          isClosable: true,
        })
        fetchDocuments()
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: `Failed to delete document: ${error instanceof Error ? error.message : 'Unknown error'}`,
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    }
  }

  const downloadDocument = async (documentId: string) => {
    try {
      const apiBaseUrl = await configService.getAdminApiUrl()
      const token = getAuthToken()
      const response = await fetch(`${apiBaseUrl}/api/v1/demo/${appId}/subjects/${subjectId}/documents/${documentId}/download`, {
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` }),
        },
      })
      if (response.ok) {
        const data = await response.json()
        if (data.success && data.download_url) {
          // Open download URL in new tab
          window.open(data.download_url, '_blank')
          toast({
            title: 'Download Started',
            description: 'Document download has been initiated',
            status: 'success',
            duration: 3000,
            isClosable: true,
          })
        } else {
          throw new Error(data.message || 'Failed to generate download URL')
        }
      } else {
        throw new Error('Failed to generate download URL')
      }
    } catch (error) {
      console.error('Error downloading document:', error)
      toast({
        title: 'Download Failed',
        description: error instanceof Error ? error.message : 'Failed to download document',
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
        <Text>Loading {getSubjectLabel().toLowerCase()} details...</Text>
      </VStack>
    )
  }

  if (error || !subject) {
    return (
      <Box>
        <Button
          leftIcon={<FiArrowLeft />}
          variant="ghost"
          onClick={() => navigate(`/apps/${appId}`)}
          mb={4}
        >
          Back to App
        </Button>
        <Alert status="error">
          <AlertIcon />
          {error || `${getSubjectLabel()} not found`}
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
          onClick={() => navigate(`/apps/${appId}`)}
          mr={4}
        >
          Back to App
        </Button>
        <Box>
          <Heading as="h1" size="lg" mb={1} color="var(--Secondary-ws-elm-700)">
            {subject.name}
          </Heading>
          <Text color="gray.600">{getSubjectLabel()} Details</Text>
        </Box>
        <Spacer />
        <Button
          leftIcon={<FiUpload />}
          colorScheme="blue"
          onClick={onUploadOpen}
        >
          Upload Document
        </Button>
      </Flex>

      <VStack spacing={6} align="stretch">
        {/* Subject Info */}
        <Card>
          <CardHeader>
            <Heading size="md">{getSubjectLabel()} Information</Heading>
          </CardHeader>
          <CardBody>
            <HStack spacing={8}>
              <Box>
                <Text fontSize="sm" color="gray.600" mb={1}>ID</Text>
                <Text fontWeight="medium">{subject.id}</Text>
              </Box>
              <Box>
                <Text fontSize="sm" color="gray.600" mb={1}>Name</Text>
                <Text fontWeight="medium">{subject.name}</Text>
              </Box>
              <Box>
                <Text fontSize="sm" color="gray.600" mb={1}>Created</Text>
                <Text fontWeight="medium">{formatDate(subject.created_at)}</Text>
              </Box>
              <Box>
                <Text fontSize="sm" color="gray.600" mb={1}>Status</Text>
                <Badge colorScheme={subject.active ? 'green' : 'red'} variant="subtle">
                  {subject.active ? 'Active' : 'Inactive'}
                </Badge>
              </Box>
            </HStack>
          </CardBody>
        </Card>

        {/* Documents */}
        <Card>
          <CardHeader>
            <Flex align="center">
              <Heading size="md">Documents ({documents.length})</Heading>
              <Spacer />
              <Button
                leftIcon={<FiRefreshCw />}
                variant="outline"
                size="sm"
                onClick={fetchDocuments}
              >
                Refresh
              </Button>
            </Flex>
          </CardHeader>
          <CardBody>
            {documents.length === 0 ? (
              <Alert status="info">
                <AlertIcon />
                No documents have been uploaded yet. Click "Upload Document" to get started.
              </Alert>
            ) : (
              <Table variant="simple">
                <Thead>
                  <Tr>
                    <Th>Document Name</Th>
                    <Th>Status</Th>
                    <Th>Size</Th>
                    <Th>Type</Th>
                    <Th>Uploaded</Th>
                    <Th>Metadata</Th>
                    <Th>Actions</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {documents.map((doc) => (
                    <Tr key={doc.id}>
                      <Td>
                        <HStack>
                          <Box color="blue.500">
                            <FiFile size={16} />
                          </Box>
                          <Link
                            as={RouterLink}
                            to={`/apps/${appId}/subjects/${subjectId}/documents/${doc.id}`}
                            fontWeight="medium"
                            color="blue.600"
                            _hover={{ textDecoration: 'underline' }}
                          >
                            {doc.name}
                          </Link>
                        </HStack>
                      </Td>
                      <Td>
                        <DocumentStatusDisplay
                          document={doc}
                          appId={appId!}
                          subjectId={subjectId!}
                        />
                      </Td>
                      <Td>{formatFileSize(doc.size)}</Td>
                      <Td>{doc.content_type || 'Unknown'}</Td>
                      <Td>{formatDateTime(doc.created_at)}</Td>
                      <Td>
                        {Object.keys(doc.metadata).length > 0 ? (
                          <HStack spacing={1} flexWrap="wrap">
                            {Object.entries(doc.metadata).slice(0, 2).map(([key, value]) => (
                              <Tag key={key} size="sm" variant="subtle" colorScheme="gray">
                                <TagLabel>{key}: {value}</TagLabel>
                              </Tag>
                            ))}
                            {Object.keys(doc.metadata).length > 2 && (
                              <Tag size="sm" variant="subtle" colorScheme="blue">
                                <TagLabel>+{Object.keys(doc.metadata).length - 2} more</TagLabel>
                              </Tag>
                            )}
                          </HStack>
                        ) : (
                          <Text fontSize="sm" color="gray.500">None</Text>
                        )}
                      </Td>
                      <Td>
                        <HStack spacing={1}>
                          <Tooltip label="Download document">
                            <IconButton
                              aria-label="Download document"
                              icon={<FiDownload />}
                              size="sm"
                              variant="ghost"
                              onClick={() => downloadDocument(doc.id)}
                            />
                          </Tooltip>
                          <Tooltip label="Delete document">
                            <IconButton
                              aria-label="Delete document"
                              icon={<FiTrash2 />}
                              size="sm"
                              variant="ghost"
                              colorScheme="red"
                              onClick={() => deleteDocument(doc.id)}
                            />
                          </Tooltip>
                        </HStack>
                      </Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            )}
          </CardBody>
        </Card>
      </VStack>

      {/* Upload Document Modal */}
      <Modal isOpen={isUploadOpen} onClose={onUploadClose} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Upload Document</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4} align="stretch">
              <FormControl>
                <FormLabel>Select File</FormLabel>
                <Input
                  type="file"
                  accept="*/*"
                  onChange={(e) => {
                    const file = e.target.files?.[0]
                    setSelectedFile(file || null)
                  }}
                  padding={1}
                />
                {selectedFile && (
                  <Text fontSize="sm" color="gray.600" mt={2}>
                    Selected: {selectedFile.name} ({formatFileSize(selectedFile.size)})
                  </Text>
                )}
              </FormControl>

              <FormControl>
                <FormLabel>Metadata (Optional)</FormLabel>
                <Text fontSize="sm" color="gray.600" mb={3}>
                  Add key-value pairs to store additional information about this document.
                </Text>
                
                {/* Existing metadata tags */}
                {metadata.length > 0 && (
                  <Box mb={3}>
                    <Text fontSize="sm" fontWeight="medium" mb={2}>Added Metadata:</Text>
                    <HStack spacing={2} flexWrap="wrap">
                      {metadata.map((item, index) => (
                        <Tag key={index} size="md" variant="subtle" colorScheme="blue">
                          <TagLabel>{item.key}: {item.value}</TagLabel>
                          <TagCloseButton onClick={() => removeMetadataItem(index)} />
                        </Tag>
                      ))}
                    </HStack>
                  </Box>
                )}

                {/* Add new metadata */}
                <HStack spacing={2}>
                  <Input
                    placeholder="Key"
                    value={newMetadataKey}
                    onChange={(e) => setNewMetadataKey(e.target.value)}
                    size="sm"
                  />
                  <Input
                    placeholder="Value"
                    value={newMetadataValue}
                    onChange={(e) => setNewMetadataValue(e.target.value)}
                    size="sm"
                  />
                  <IconButton
                    aria-label="Add metadata"
                    icon={<FiPlus />}
                    size="sm"
                    colorScheme="blue"
                    variant="outline"
                    onClick={addMetadataItem}
                    isDisabled={!newMetadataKey.trim() || !newMetadataValue.trim()}
                  />
                </HStack>
              </FormControl>

              {uploading && (
                <Box>
                  <Text fontSize="sm" mb={2}>Uploading...</Text>
                  <Progress isIndeterminate size="sm" colorScheme="blue" />
                </Box>
              )}
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onUploadClose} isDisabled={uploading}>
              Cancel
            </Button>
            <Button
              colorScheme="blue"
              onClick={handleFileUpload}
              isLoading={uploading}
              loadingText="Uploading..."
              isDisabled={!selectedFile}
            >
              Upload
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  )
}

export default SubjectViewPage