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
  IconButton,
  useDisclosure,
  useToast,
  Flex,
  Spacer,
} from '@chakra-ui/react'
import { useState } from 'react'
import { FiEdit, FiTrash2, FiPlus } from 'react-icons/fi'
import { useLLMModels } from '../hooks/useLLMModels'
import { LLMModel } from '../services/llmModelsService'
import LLMModelModal from '../components/LLMModelModal'

const LLMModelsPage: React.FC = () => {
  const {
    models,
    loading,
    error,
    total,
    page,
    pageSize,
    setPage,
    createModel,
    updateModel,
    deleteModel,
  } = useLLMModels()
  
  const toast = useToast()
  const { isOpen, onOpen, onClose } = useDisclosure()
  const [selectedModel, setSelectedModel] = useState<LLMModel | undefined>()
  const [modalMode, setModalMode] = useState<'create' | 'edit'>('create')

  const handleDelete = async (model: LLMModel) => {
    if (window.confirm(`Are you sure you want to delete "${model.name}"?`)) {
      const result = await deleteModel(model.id)
      if (result.success) {
        toast({
          title: 'Model deleted',
          description: `${model.name} has been successfully deleted.`,
          status: 'success',
          duration: 3000,
          isClosable: true,
        })
      } else {
        toast({
          title: 'Delete failed',
          description: result.error || 'Failed to delete model',
          status: 'error',
          duration: 5000,
          isClosable: true,
        })
      }
    }
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A'
    // Parse date as local date to avoid timezone conversion
    const [year, month, day] = dateString.split('-')
    const date = new Date(parseInt(year), parseInt(month) - 1, parseInt(day))
    return date.toLocaleDateString()
  }

  if (loading) {
    return (
      <VStack spacing={4} align="center" pt={8}>
        <Spinner size="lg" color="var(--palette-accent-ws-elm-500)" />
        <Text>Loading LLM models...</Text>
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
            LLM Models
          </Heading>
          <Text color="gray.600">
            Manage and configure Large Language Models for the Extract platform.
          </Text>
        </Box>
        <Spacer />
        <Button
          leftIcon={<FiPlus />}
          style={{ backgroundColor: 'var(--palette-accent-ws-elm-500)' }}
          color="white"
          _hover={{ backgroundColor: 'var(--Secondary-ws-elm-700)' }}
          onClick={() => {
            setModalMode('create')
            setSelectedModel(undefined)
            onOpen()
          }}
        >
          Add Model
        </Button>
      </Flex>

      {models.length === 0 ? (
        <Alert status="info">
          <AlertIcon />
          No LLM models found. Click "Add Model" to create your first model.
        </Alert>
      ) : (
        <Box overflowX="auto" bg="white" borderRadius="md" boxShadow="sm">
          <Table variant="simple">
            <Thead bg="gray.50">
              <Tr>
                <Th>Name</Th>
                <Th>Family</Th>
                <Th>Version</Th>
                <Th>Status</Th>
                <Th>Priority</Th>
                <Th>Throughput/GSU</Th>
                <Th>WSky Sunset</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {models.map((model) => (
                <Tr key={model.id} _hover={{ bg: 'gray.50' }}>
                  <Td>
                    <VStack align="start" spacing={1}>
                      <Text fontWeight="medium">{model.name}</Text>
                      <Text fontSize="sm" color="gray.600" noOfLines={1}>
                        {model.description}
                      </Text>
                    </VStack>
                  </Td>
                  <Td>{model.family}</Td>
                  <Td>
                    <Badge variant="outline" colorScheme="blue">
                      {model.version}
                    </Badge>
                  </Td>
                  <Td>
                    <Badge
                      colorScheme={model.active ? 'green' : 'red'}
                      variant="subtle"
                    >
                      {model.active ? 'Active' : 'Inactive'}
                    </Badge>
                  </Td>
                  <Td>{model.priority}</Td>
                  <Td>
                    {model.per_second_throughput_per_gsu} {model.units}/s
                  </Td>
                  <Td>{formatDate(model.lifecycle.wsky?.sunset_date)}</Td>
                  <Td>
                    <HStack spacing={2}>
                      <IconButton
                        aria-label="Edit model"
                        icon={<FiEdit />}
                        size="sm"
                        variant="ghost"
                        onClick={() => {
                          setModalMode('edit')
                          setSelectedModel(model)
                          onOpen()
                        }}
                      />
                      <IconButton
                        aria-label="Delete model"
                        icon={<FiTrash2 />}
                        size="sm"
                        variant="ghost"
                        colorScheme="red"
                        onClick={() => handleDelete(model)}
                      />
                    </HStack>
                  </Td>
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
            Showing {models.length} of {total} models
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
              isDisabled={models.length < pageSize}
              onClick={() => setPage(page + 1)}
            >
              Next
            </Button>
          </HStack>
        </Flex>
      )}

      {/* Modal for creating/editing models */}
      <LLMModelModal
        isOpen={isOpen}
        onClose={onClose}
        onSave={async (modelData) => {
          if (modalMode === 'create') {
            return await createModel(modelData as any)
          } else {
            return await updateModel(selectedModel!.id, modelData as any)
          }
        }}
        model={selectedModel}
        mode={modalMode}
      />
    </Box>
  )
}

export default LLMModelsPage