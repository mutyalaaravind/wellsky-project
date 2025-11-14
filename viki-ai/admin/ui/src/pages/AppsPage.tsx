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
  useToast,
  Flex,
  Spacer,
  Link as ChakraLink,
  Stat,
  StatLabel,
  StatNumber,
} from '@chakra-ui/react'
import { Link as RouterLink } from 'react-router-dom'
import { FiEdit, FiTrash2, FiPlus, FiExternalLink } from 'react-icons/fi'
import { useApps } from '../hooks/useApps'
import { App } from '../services/appsService'
import RBACGuard from '../components/RBACGuard'
import { useRBAC } from '../hooks/useRBAC'

const AppsPage: React.FC = () => {
  const {
    apps,
    loading,
    error,
    total,
    page,
    pageSize,
    setPage,
    deleteApp,
  } = useApps()

  const { hasPermission } = useRBAC()
  
  const toast = useToast()

  const handleDelete = async (app: App) => {
    if (window.confirm(`Are you sure you want to delete "${app.name}"?`)) {
      const result = await deleteApp(app.id)
      if (result.success) {
        toast({
          title: 'App deleted',
          description: `${app.name} has been successfully deleted.`,
          status: 'success',
          duration: 3000,
          isClosable: true,
        })
      } else {
        toast({
          title: 'Delete failed',
          description: result.error || 'Failed to delete app',
          status: 'error',
          duration: 5000,
          isClosable: true,
        })
      }
    }
  }

  const handleEdit = () => {
    // TODO: Implement edit functionality
    toast({
      title: 'Edit App',
      description: 'Edit functionality coming soon',
      status: 'info',
      duration: 3000,
      isClosable: true,
    })
  }

  const handleAddApp = () => {
    // TODO: Implement add functionality
    toast({
      title: 'Add App',
      description: 'Add functionality coming soon',
      status: 'info',
      duration: 3000,
      isClosable: true,
    })
  }


  if (loading) {
    return (
      <VStack spacing={4} align="center" pt={8}>
        <Spinner size="lg" color="var(--palette-accent-ws-elm-500)" />
        <Text>Loading apps...</Text>
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
            Apps
          </Heading>
          <Text color="gray.600">
            Create and manage your applications.
          </Text>
        </Box>
        <Spacer />
        <RBACGuard permissions="extract.apps.action.add">
          <Button
            leftIcon={<FiPlus />}
            style={{ backgroundColor: 'var(--palette-accent-ws-elm-500)' }}
            color="white"
            _hover={{ backgroundColor: 'var(--Secondary-ws-elm-700)' }}
            onClick={handleAddApp}
          >
            Add App
          </Button>
        </RBACGuard>
      </Flex>

      {apps.length === 0 ? (
        <Alert status="info">
          <AlertIcon />
          No apps found. Click "Add App" to create your first application.
        </Alert>
      ) : (
        <Box overflowX="auto" bg="white" borderRadius="md" boxShadow="sm">
          <Table variant="simple">
            <Thead bg="gray.50">
              <Tr>
                <Th>App ID</Th>
                <Th>App Name</Th>
                <Th>BU</Th>
                <Th>Solution Code</Th>
                <Th>Version</Th>
                <Th>Status</Th>
                <Th>Pipelines</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {apps.map((app) => (
                <Tr key={app.id} _hover={{ bg: 'gray.50' }}>
                  <Td>
                    <Text fontWeight="medium">{app.app_id}</Text>
                  </Td>
                  <Td>
                    <VStack align="start" spacing={1}>
                      {hasPermission('extract.apps.action.view') ? (
                        <ChakraLink
                          as={RouterLink}
                          to={`/apps/${app.app_id}`}
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
                          {app.name}
                          <FiExternalLink size={12} />
                        </ChakraLink>
                      ) : (
                        <Text fontWeight="medium">{app.name}</Text>
                      )}
                      {app.description && (
                        <Text fontSize="sm" color="gray.500" noOfLines={1} maxW="200px">
                          {app.description}
                        </Text>
                      )}
                    </VStack>
                  </Td>
                  <Td>
                    <Badge variant="outline" colorScheme="orange">
                      {app.business_unit}
                    </Badge>
                  </Td>
                  <Td>
                    <Badge variant="outline" colorScheme="blue">
                      {app.solution_code}
                    </Badge>
                  </Td>
                  <Td>
                    <Badge variant="outline" colorScheme="purple">
                      {app.version}
                    </Badge>
                  </Td>
                  <Td>
                    <Badge
                      colorScheme={app.active ? 'green' : 'red'}
                      variant="subtle"
                    >
                      {app.status}
                    </Badge>
                  </Td>
                  <Td>
                    <Stat size="sm">
                      <StatNumber fontSize="sm">{app.pipeline_count}</StatNumber>
                      <StatLabel fontSize="xs">pipelines</StatLabel>
                    </Stat>
                  </Td>
                  <Td>
                    <HStack spacing={2}>
                      <RBACGuard permissions="extract.apps.action.edit">
                        <IconButton
                          aria-label="Edit app"
                          icon={<FiEdit />}
                          size="sm"
                          variant="ghost"
                          onClick={() => handleEdit()}
                        />
                      </RBACGuard>
                      <RBACGuard permissions="extract.apps.action.delete">
                        <IconButton
                          aria-label="Delete app"
                          icon={<FiTrash2 />}
                          size="sm"
                          variant="ghost"
                          colorScheme="red"
                          onClick={() => handleDelete(app)}
                        />
                      </RBACGuard>
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
            Showing {apps.length} of {total} apps
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
              isDisabled={apps.length < pageSize}
              onClick={() => setPage(page + 1)}
            >
              Next
            </Button>
          </HStack>
        </Flex>
      )}
    </Box>
  )
}

export default AppsPage