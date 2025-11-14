import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box,
  Button,
  Heading,
  Text,
  VStack,
  HStack,
  Card,
  CardHeader,
  CardBody,
  Badge,
  Tag,
  TagLabel,
  Spinner,
  Alert,
  AlertIcon,
  Flex,
  Spacer,
  useToast,
  Divider,
  Collapse,
  useDisclosure,
  IconButton
} from '@chakra-ui/react'
import { FiArrowLeft, FiDownload, FiFile, FiChevronDown, FiChevronRight } from 'react-icons/fi'
import { configService } from '../services/configService'
import { getAuthToken } from '../utils/auth'
import EntitiesSection from '../components/EntitiesSection'

interface Document {
  id: string
  app_id: string
  subject_id: string
  name: string
  uri: string
  metadata: Record<string, any>
  status: string
  content_type: string
  size: number
  active: boolean
  created_at: string
  updated_at: string
}

interface Subject {
  id: string
  name: string
  active: boolean
  created_at: string
}

interface SubjectConfig {
  label: string
}


const DocumentDetailsPage: React.FC = () => {
  const { appId, subjectId, documentId } = useParams()
  const navigate = useNavigate()
  const toast = useToast()

  const [document, setDocument] = useState<Document | null>(null)
  const [subject, setSubject] = useState<Subject | null>(null)
  const [subjectConfig, setSubjectConfig] = useState<SubjectConfig>({ label: 'Subject' })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [downloadLoading, setDownloadLoading] = useState(false)
  const [fileUrl, setFileUrl] = useState<string | null>(null)
  const [fileLoading, setFileLoading] = useState(false)

  // Disclosure states for collapsible sections
  const { isOpen: isDocumentInfoOpen, onToggle: onDocumentInfoToggle } = useDisclosure({ defaultIsOpen: false })
  const { isOpen: isFileOpen, onToggle: onFileToggle } = useDisclosure({ defaultIsOpen: false })
  const { isOpen: isEntitiesOpen, onToggle: onEntitiesToggle } = useDisclosure({ defaultIsOpen: true })

  const getSubjectLabel = () => subjectConfig.label || 'Subject'

  const isImage = (contentType: string) => {
    return contentType && contentType.startsWith('image/')
  }

  const isPDF = (contentType: string) => {
    return contentType === 'application/pdf'
  }

  const isPreviewable = (contentType: string) => {
    return isImage(contentType) || isPDF(contentType)
  }

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'completed': return 'green'
      case 'processing': return 'yellow'
      case 'failed': return 'red'
      default: return 'gray'
    }
  }

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

  const fetchDocument = async () => {
    if (!appId || !subjectId || !documentId) return
    
    try {
      const apiBaseUrl = await configService.getAdminApiUrl()
      const token = getAuthToken()
      const response = await fetch(`${apiBaseUrl}/api/v1/demo/${appId}/subjects/${subjectId}/documents/${documentId}`, {
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` }),
        },
      })
      if (response.ok) {
        const data = await response.json()
        setDocument(data.data)
      } else {
        throw new Error('Document not found')
      }
    } catch (error) {
      console.error('Error fetching document:', error)
      setError(error instanceof Error ? error.message : 'Failed to load document')
    }
  }

  const loadFilePreview = async () => {
    if (!appId || !subjectId || !documentId || !document) return
    
    // Only load preview for images and PDFs
    if (!isPreviewable(document.content_type)) return
    
    setFileLoading(true)
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
          setFileUrl(data.download_url)
        } else {
          throw new Error(data.message || 'Failed to generate preview URL')
        }
      } else {
        throw new Error('Failed to generate preview URL')
      }
    } catch (error) {
      console.error('Error loading file preview:', error)
      toast({
        title: 'Preview Failed',
        description: 'Failed to load file preview',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    } finally {
      setFileLoading(false)
    }
  }

  const downloadDocument = async () => {
    if (!appId || !subjectId || !documentId || !document) return
    
    setDownloadLoading(true)
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
    } finally {
      setDownloadLoading(false)
    }
  }

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      await Promise.all([
        fetchSubjectConfig(),
        fetchSubject(),
        fetchDocument()
      ])
      setLoading(false)
    }

    fetchData()
  }, [appId, subjectId, documentId])

  // Load file preview when document is loaded
  useEffect(() => {
    if (document) {
      loadFilePreview()
    }
  }, [document])

  if (loading) {
    return (
      <VStack spacing={4} align="center" pt={8}>
        <Spinner size="lg" color="var(--palette-accent-ws-elm-500)" />
        <Text>Loading document details...</Text>
      </VStack>
    )
  }

  if (error || !document || !subject) {
    return (
      <Box>
        <Button
          leftIcon={<FiArrowLeft />}
          variant="ghost"
          onClick={() => navigate(`/apps/${appId}/subjects/${subjectId}`)}
          mb={4}
        >
          Back to {getSubjectLabel()}
        </Button>
        <Alert status="error">
          <AlertIcon />
          {error || 'Document not found'}
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
          onClick={() => navigate(`/apps/${appId}/subjects/${subjectId}`)}
          mr={4}
        >
          Back to {getSubjectLabel()}
        </Button>
        <Box>
          <Heading as="h1" size="lg" mb={1} color="var(--Secondary-ws-elm-700)">
            {document.name}
          </Heading>
          <Text color="gray.600">Document Details • {subject.name}</Text>
        </Box>
        <Spacer />
        <Button
          leftIcon={<FiDownload />}
          colorScheme="blue"
          onClick={downloadDocument}
          isLoading={downloadLoading}
          loadingText="Downloading..."
        >
          Download
        </Button>
      </Flex>

      <VStack spacing={6} align="stretch">
        {/* Document Info */}
        <Card>
          <CardHeader>
            <HStack>
              <IconButton
                aria-label="Toggle document info"
                icon={isDocumentInfoOpen ? <FiChevronDown /> : <FiChevronRight />}
                size="sm"
                variant="ghost"
                onClick={onDocumentInfoToggle}
              />
              <Heading size="md">Document Information</Heading>
            </HStack>
          </CardHeader>
          <Collapse in={isDocumentInfoOpen}>
            <CardBody>
              <VStack spacing={4} align="stretch">
                <HStack spacing={8}>
                  <Box>
                    <Text fontSize="sm" color="gray.600" mb={1}>Document ID</Text>
                    <Text fontWeight="medium" fontFamily="mono" fontSize="sm">{document.id}</Text>
                  </Box>
                  <Box>
                    <Text fontSize="sm" color="gray.600" mb={1}>File Name</Text>
                    <HStack>
                      <Box color="blue.500">
                        <FiFile size={16} />
                      </Box>
                      <Text fontWeight="medium">{document.name}</Text>
                    </HStack>
                  </Box>
                  <Box>
                    <Text fontSize="sm" color="gray.600" mb={1}>Status</Text>
                    <Badge
                      colorScheme={getStatusBadgeColor(document.status)}
                      variant="subtle"
                    >
                      {document.status}
                    </Badge>
                  </Box>
                </HStack>

                <HStack spacing={8}>
                  <Box>
                    <Text fontSize="sm" color="gray.600" mb={1}>File Size</Text>
                    <Text fontWeight="medium">{formatFileSize(document.size)}</Text>
                  </Box>
                  <Box>
                    <Text fontSize="sm" color="gray.600" mb={1}>Content Type</Text>
                    <Text fontWeight="medium">{document.content_type || 'Unknown'}</Text>
                  </Box>
                  <Box>
                    <Text fontSize="sm" color="gray.600" mb={1}>Uploaded</Text>
                    <Text fontWeight="medium">{formatDateTime(document.created_at)}</Text>
                  </Box>
                  <Box>
                    <Text fontSize="sm" color="gray.600" mb={1}>Last Modified</Text>
                    <Text fontWeight="medium">{formatDateTime(document.updated_at)}</Text>
                  </Box>
                </HStack>

                {/* Metadata */}
                {Object.keys(document.metadata).length > 0 && (
                  <>
                    <Divider />
                    <Box>
                      <Text fontSize="sm" color="gray.600" mb={2}>Metadata</Text>
                      <HStack spacing={2} flexWrap="wrap">
                        {Object.entries(document.metadata).map(([key, value]) => (
                          <Tag key={key} size="md" variant="subtle" colorScheme="gray">
                            <TagLabel>{key}: {String(value)}</TagLabel>
                          </Tag>
                        ))}
                      </HStack>
                    </Box>
                  </>
                )}
              </VStack>
            </CardBody>
          </Collapse>
        </Card>

        {/* File Preview */}
        {document && isPreviewable(document.content_type) && (
          <Card>
            <CardHeader>
              <HStack>
                <IconButton
                  aria-label="Toggle file preview"
                  icon={isFileOpen ? <FiChevronDown /> : <FiChevronRight />}
                  size="sm"
                  variant="ghost"
                  onClick={onFileToggle}
                />
                <Heading size="md">File</Heading>
                <Spacer />
                {fileLoading && (
                  <Spinner size="sm" color="var(--palette-accent-ws-elm-500)" />
                )}
              </HStack>
            </CardHeader>
            <Collapse in={isFileOpen}>
              <CardBody>
                {fileLoading ? (
                  <VStack spacing={4} align="center" py={8}>
                    <Spinner size="lg" color="var(--palette-accent-ws-elm-500)" />
                    <Text color="gray.500">Loading file preview...</Text>
                  </VStack>
                ) : fileUrl ? (
                  <Box>
                    {isImage(document.content_type) ? (
                      <Box
                        maxW="100%"
                        display="flex"
                        justifyContent="center"
                        bg="gray.50"
                        borderRadius="md"
                        p={4}
                      >
                        <Box
                          as="img"
                          src={fileUrl}
                          alt={document.name}
                          maxW="100%"
                          maxH="600px"
                          objectFit="contain"
                          borderRadius="md"
                          boxShadow="sm"
                        />
                      </Box>
                    ) : isPDF(document.content_type) ? (
                      <Box
                        w="100%"
                        h="600px"
                        border="1px solid"
                        borderColor="gray.200"
                        borderRadius="md"
                        overflow="hidden"
                      >
                        <Box
                          as="iframe"
                          src={`${fileUrl}#toolbar=1&navpanes=1&scrollbar=1`}
                          w="100%"
                          h="100%"
                          title={document.name}
                        />
                      </Box>
                    ) : null}
                  </Box>
                ) : (
                  <VStack spacing={4} align="center" py={8}>
                    <Box color="gray.400">
                      <FiFile size={24} />
                    </Box>
                    <Text color="gray.500">Unable to load file preview</Text>
                  </VStack>
                )}
              </CardBody>
            </Collapse>
          </Card>
        )}

        {/* Entities Section */}
        <Card>
          <CardHeader>
            <HStack>
              <IconButton
                aria-label="Toggle entities"
                icon={isEntitiesOpen ? <FiChevronDown /> : <FiChevronRight />}
                size="sm"
                variant="ghost"
                onClick={onEntitiesToggle}
              />
              <Heading size="md">Entities</Heading>
            </HStack>
          </CardHeader>
          <Collapse in={isEntitiesOpen}>
            <CardBody>
              <EntitiesSection
                appId={appId!}
                subjectId={subjectId!}
                documentId={documentId!}
              />
            </CardBody>
          </Collapse>
        </Card>
      </VStack>
    </Box>
  )
}

export default DocumentDetailsPage