import {
  Box,
  Heading,
  Text,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Button,
  HStack,
  VStack,
  Spinner,
  Alert,
  AlertIcon,
  Badge,
  useDisclosure,
  Flex,
  Spacer,
  Link as ChakraLink,
} from '@chakra-ui/react'
import { useState } from 'react'
import { Link as RouterLink } from 'react-router-dom'
import { FiPlus, FiExternalLink } from 'react-icons/fi'
import { usePipelines } from '../hooks/usePipelines'
import { Pipeline } from '../services/pipelinesService'
import PipelineModal from '../components/PipelineModal'

const PipelinesPage: React.FC = () => {
  const {
    pipelines,
    loading,
    error,
    total,
    page,
    pageSize,
    setPage,
    createPipeline,
  } = usePipelines()
  
  const { isOpen, onOpen, onClose } = useDisclosure()
  const [selectedPipeline, setSelectedPipeline] = useState<Pipeline | undefined>()
  const [modalMode, setModalMode] = useState<'create' | 'edit'>('create')


  const handleAddPipeline = () => {
    setModalMode('create')
    setSelectedPipeline(undefined)
    onOpen()
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString()
  }

  if (loading) {
    return (
      <VStack spacing={4} align="center" pt={8}>
        <Spinner size="lg" color="var(--palette-accent-ws-elm-500)" />
        <Text>Loading pipelines...</Text>
      </VStack>
    )
  }

  if (error) {
    return (
      <Alert status="error">
        <AlertIcon />
        {error}
      </Alert>
    )
  }

  return (
    <Box>
      <Flex align="center" mb={6}>
        <Box>
          <Heading as="h1" size="lg" mb={2} color="var(--Secondary-ws-elm-700)">
            Pipelines
          </Heading>
          <Text color="gray.600">
            Create and manage your extraction pipelines.
          </Text>
        </Box>
        <Spacer />
        <Button
          leftIcon={<FiPlus />}
          style={{ backgroundColor: 'var(--palette-accent-ws-elm-500)' }}
          color="white"
          _hover={{ backgroundColor: 'var(--Secondary-ws-elm-700)' }}
          onClick={handleAddPipeline}
        >
          Add Pipeline
        </Button>
      </Flex>

      {pipelines.length === 0 ? (
        <Alert status="info">
          <AlertIcon />
          No pipelines found. Click "Add Pipeline" to create your first pipeline.
        </Alert>
      ) : (
        <Box overflowX="auto" bg="white" borderRadius="md" boxShadow="sm">
          <Table variant="simple">
            <Thead bg="gray.50">
              <Tr>
                <Th>Solution Code</Th>
                <Th>App ID</Th>
                <Th>Name</Th>
                <Th>Description</Th>
                <Th>Version</Th>
                <Th>Status</Th>
                <Th>Created</Th>
              </Tr>
            </Thead>
            <Tbody>
              {pipelines.map((pipeline) => (
                <Tr key={pipeline.id} _hover={{ bg: 'gray.50' }}>
                  <Td>
                    <Badge variant="outline" colorScheme="blue">
                      {pipeline.solution_code || 'N/A'}
                    </Badge>
                  </Td>
                  <Td>
                    <Text fontWeight="medium">{pipeline.app_id || 'N/A'}</Text>
                  </Td>
                  <Td>
                    <VStack align="start" spacing={1}>
                      <ChakraLink
                        as={RouterLink}
                        to={`/pipelines/${encodeURIComponent(pipeline.id)}`}
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
                      <Text fontSize="sm" color="gray.500">
                        {pipeline.key}
                      </Text>
                    </VStack>
                  </Td>
                  <Td>
                    <Text fontSize="sm" color="gray.600" noOfLines={2} maxW="200px">
                      {pipeline.description || 'No description'}
                    </Text>
                  </Td>
                  <Td>
                    <Badge variant="outline" colorScheme="purple">
                      {pipeline.version || '1.0.0'}
                    </Badge>
                  </Td>
                  <Td>
                    <Badge
                      colorScheme={pipeline.active ? 'green' : 'red'}
                      variant="subtle"
                    >
                      {pipeline.active ? 'Active' : 'Inactive'}
                    </Badge>
                  </Td>
                  <Td>{formatDate(pipeline.created_at)}</Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>
      )}

      {/* Pagination info */}
      {total > 0 && (
        <Flex justify="space-between" align="center" mt={4}>
          <Text fontSize="sm" color="gray.600">
            Showing {pipelines.length} of {total} pipelines
          </Text>
          <HStack spacing={2}>
            <Button
              size="sm"
              variant="outline"
              isDisabled={page <= 1}
              onClick={() => setPage(page - 1)}
            >
              Previous
            </Button>
            <Text fontSize="sm">
              Page {page}
            </Text>
            <Button
              size="sm"
              variant="outline"
              isDisabled={pipelines.length < pageSize}
              onClick={() => setPage(page + 1)}
            >
              Next
            </Button>
          </HStack>
        </Flex>
      )}

      {/* Modal for creating/editing pipelines */}
      <PipelineModal
        isOpen={isOpen}
        onClose={onClose}
        onSave={async (pipelineData) => {
          return await createPipeline(pipelineData as any)
        }}
        pipeline={selectedPipeline}
        mode={modalMode}
      />
    </Box>
  )
}

export default PipelinesPage