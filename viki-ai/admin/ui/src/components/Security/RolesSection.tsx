import {
  Box,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Spinner,
  Alert,
  AlertIcon,
  VStack,
  Text,
  Badge,
  Heading,
  Wrap,
  WrapItem,
  Tooltip,
  Collapse,
  IconButton
} from '@chakra-ui/react'
import { FiChevronDown, FiChevronRight } from 'react-icons/fi'
import { useState } from 'react'
import { useRoles } from '../../hooks/useRoles'
import { Role } from '../../services/rolesService'

const RolesSection: React.FC = () => {
  const { roles, loading, error, effectivePermissions } = useRoles()
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set())

  const toggleRowExpansion = (roleId: string) => {
    setExpandedRows(prev => {
      const newSet = new Set(prev)
      if (newSet.has(roleId)) {
        newSet.delete(roleId)
      } else {
        newSet.add(roleId)
      }
      return newSet
    })
  }

  const formatPermissions = (permissions: string[]) => {
    if (permissions.length === 0) {
      return <Text color="gray.500" fontSize="sm">None</Text>
    }

    const sortedPermissions = [...permissions].sort((a, b) => a.localeCompare(b))

    return (
      <VStack align="start" spacing={1}>
        {sortedPermissions.map((permission, index) => (
          <Badge
            key={index}
            colorScheme="blue"
            variant="subtle"
            fontSize="xs"
            px={2}
            py={1}
          >
            {permission}
          </Badge>
        ))}
      </VStack>
    )
  }

  const formatInheritance = (inherits: string[]) => {
    if (inherits.length === 0) {
      return <Text color="gray.500" fontSize="sm">None</Text>
    }

    return (
      <Wrap spacing={1}>
        {inherits.map((roleId, index) => {
          const inheritedRole = roles.find(r => r.id === roleId)
          const displayName = inheritedRole ? inheritedRole.name : roleId

          return (
            <WrapItem key={index}>
              <Badge
                colorScheme="purple"
                variant="outline"
                fontSize="xs"
                px={2}
                py={1}
              >
                <Tooltip label={`Role ID: ${roleId}`} hasArrow>
                  {displayName}
                </Tooltip>
              </Badge>
            </WrapItem>
          )
        })}
      </Wrap>
    )
  }

  if (loading) {
    return (
      <Box
        w="full"
        h="400px"
        display="flex"
        alignItems="center"
        justifyContent="center"
        bg="white"
        borderRadius="lg"
        boxShadow="sm"
        border="1px"
        borderColor="gray.200"
      >
        <VStack spacing={4}>
          <Spinner size="xl" color="blue.500" />
          <Text color="gray.600">Loading roles...</Text>
        </VStack>
      </Box>
    )
  }

  if (error) {
    return (
      <Alert status="error" borderRadius="lg">
        <AlertIcon />
        <Box>
          <Text fontWeight="medium">Failed to load roles</Text>
          <Text fontSize="sm">{error}</Text>
        </Box>
      </Alert>
    )
  }

  if (roles.length === 0) {
    return (
      <Box
        w="full"
        h="400px"
        bg="white"
        borderRadius="lg"
        boxShadow="sm"
        p={6}
        display="flex"
        alignItems="center"
        justifyContent="center"
        border="1px"
        borderColor="gray.200"
      >
        <VStack spacing={2}>
          <Text color="gray.400" fontSize="lg">No roles found</Text>
          <Text color="gray.500" fontSize="sm">
            There are currently no roles configured in the system.
          </Text>
        </VStack>
      </Box>
    )
  }

  return (
    <VStack align="start" spacing={6} w="full">
      <Box>
        <Heading as="h3" size="md" mb={2}>
          Roles
        </Heading>
        <Text color="gray.600" fontSize="sm">
          System roles and their permissions. Click on a role to view effective permissions including inherited ones.
        </Text>
      </Box>

      <Box
        w="full"
        bg="white"
        borderRadius="lg"
        boxShadow="sm"
        border="1px"
        borderColor="gray.200"
        overflow="hidden"
      >
        <Table variant="simple">
          <Thead bg="gray.50">
            <Tr>
              <Th width="40px"></Th>
              <Th>Role Name</Th>
              <Th>Role ID</Th>
              <Th>Description</Th>
              <Th>Direct Permissions</Th>
              <Th>Inherits From</Th>
              <Th>Status</Th>
            </Tr>
          </Thead>
          <Tbody>
            {roles.map((role: Role) => {
              const isExpanded = expandedRows.has(role.id)
              const roleEffectivePermissions = effectivePermissions[role.id] || []

              return (
                <>
                  <Tr key={role.id} _hover={{ bg: "gray.50" }}>
                    <Td>
                      <IconButton
                        aria-label={isExpanded ? "Collapse" : "Expand"}
                        icon={isExpanded ? <FiChevronDown /> : <FiChevronRight />}
                        size="sm"
                        variant="ghost"
                        onClick={() => toggleRowExpansion(role.id)}
                      />
                    </Td>
                    <Td>
                      <Text fontWeight="medium" color="gray.900">
                        {role.name}
                      </Text>
                    </Td>
                    <Td>
                      <Text fontFamily="mono" fontSize="sm" color="gray.600">
                        {role.id}
                      </Text>
                    </Td>
                    <Td maxW="200px">
                      <Text fontSize="sm" color="gray.700" noOfLines={2}>
                        {role.description}
                      </Text>
                    </Td>
                    <Td maxW="300px">
                      {formatPermissions(role.permissions)}
                    </Td>
                    <Td maxW="200px">
                      {formatInheritance(role.inherits)}
                    </Td>
                    <Td>
                      <Badge
                        colorScheme={role.active ? "green" : "red"}
                        variant="subtle"
                      >
                        {role.active ? "Active" : "Inactive"}
                      </Badge>
                    </Td>
                  </Tr>

                  <Tr>
                    <Td colSpan={7} p={0} border="none">
                      <Collapse in={isExpanded}>
                        <Box bg="blue.50" p={4} borderTop="1px" borderColor="gray.200">
                          <VStack align="start" spacing={3}>
                            <Text fontWeight="medium" color="blue.800" fontSize="sm">
                              Effective Permissions (including inherited):
                            </Text>
                            {roleEffectivePermissions.length > 0 ? (
                              <Box maxW="full">
                                {formatPermissions(roleEffectivePermissions)}
                              </Box>
                            ) : (
                              <Text color="gray.500" fontSize="sm" fontStyle="italic">
                                Loading effective permissions...
                              </Text>
                            )}
                          </VStack>
                        </Box>
                      </Collapse>
                    </Td>
                  </Tr>
                </>
              )
            })}
          </Tbody>
        </Table>
      </Box>

      <Box>
        <Text color="gray.500" fontSize="sm">
          Total: {roles.length} role{roles.length !== 1 ? 's' : ''}
        </Text>
      </Box>
    </VStack>
  )
}

export default RolesSection