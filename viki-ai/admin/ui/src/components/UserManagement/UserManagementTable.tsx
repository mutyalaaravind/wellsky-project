import {
  Box,
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
  IconButton,
  Flex,
  Text,
  Badge,
  Input,
  InputGroup,
  InputLeftElement,
  Select,
  Spacer,
} from '@chakra-ui/react'
import { FiEdit, FiTrash2, FiPlus, FiSearch } from 'react-icons/fi'
import { useState } from 'react'
import { useUserProfiles, UserProfileFilters } from '../../hooks/useUserProfiles'
import { UserProfile, UserProfileCreateRequest, UserProfileUpdateRequest } from '../../services/userProfilesService'
import OrganizationChips from './OrganizationChips'
import RoleChips from './RoleChips'
import UserModal from './UserModal'
import DeleteUserModal from './DeleteUserModal'

const UserManagementTable: React.FC = () => {
  const {
    userProfiles,
    loading,
    error,
    total,
    page,
    pageSize,
    setPage,
    createUserProfile,
    updateUserProfile,
    deleteUserProfile,
    setFilters,
  } = useUserProfiles()

  const [isUserModalOpen, setIsUserModalOpen] = useState(false)
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false)
  const [selectedUser, setSelectedUser] = useState<UserProfile | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const [activeFilter, setActiveFilter] = useState('true')

  const handleAddUser = () => {
    setSelectedUser(null)
    setIsUserModalOpen(true)
  }

  const handleEditUser = (user: UserProfile) => {
    setSelectedUser(user)
    setIsUserModalOpen(true)
  }

  const handleDeleteUser = (user: UserProfile) => {
    setSelectedUser(user)
    setIsDeleteModalOpen(true)
  }

  const handleSaveUser = async (userData: UserProfileCreateRequest | UserProfileUpdateRequest) => {
    if (selectedUser) {
      // Edit mode
      return await updateUserProfile(selectedUser.id, userData as UserProfileUpdateRequest)
    } else {
      // Add mode
      return await createUserProfile(userData as UserProfileCreateRequest)
    }
  }

  const handleDeleteConfirm = async (userId: string) => {
    return await deleteUserProfile(userId)
  }

  const handleFiltersChange = () => {
    const filters: UserProfileFilters = {
      activeOnly: activeFilter === 'true',
      role: roleFilter || undefined,
    }
    setFilters(filters)
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString()
  }

  if (loading) {
    return (
      <VStack spacing={4} align="center" pt={8}>
        <Spinner size="lg" color="var(--palette-accent-ws-elm-500)" />
        <Text>Loading users...</Text>
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
      {/* Header with filters and add button */}
      <Flex align="center" mb={4} gap={4} wrap="wrap">
        <InputGroup maxW="300px">
          <InputLeftElement pointerEvents="none">
            <FiSearch color="gray.300" />
          </InputLeftElement>
          <Input
            placeholder="Search users..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </InputGroup>

        <Select
          placeholder="All Roles"
          value={roleFilter}
          onChange={(e) => {
            setRoleFilter(e.target.value)
            handleFiltersChange()
          }}
          maxW="200px"
        >
          <option value="superuser">Superuser</option>
          <option value="admin">Admin</option>
          <option value="manager">Manager</option>
          <option value="user">User</option>
        </Select>

        <Select
          value={activeFilter}
          onChange={(e) => {
            setActiveFilter(e.target.value)
            handleFiltersChange()
          }}
          maxW="150px"
        >
          <option value="true">Active Only</option>
          <option value="false">All Users</option>
        </Select>

        <Spacer />

        <Button
          leftIcon={<FiPlus />}
          style={{ backgroundColor: 'var(--palette-accent-ws-elm-500)' }}
          color="white"
          _hover={{ backgroundColor: 'var(--Secondary-ws-elm-700)' }}
          onClick={handleAddUser}
        >
          Add User
        </Button>
      </Flex>

      {userProfiles.length === 0 ? (
        <Alert status="info">
          <AlertIcon />
          No users found. Click "Add User" to create the first user.
        </Alert>
      ) : (
        <Box overflowX="auto" bg="white" borderRadius="md" boxShadow="sm">
          <Table variant="simple">
            <Thead bg="gray.50">
              <Tr>
                <Th>User</Th>
                <Th>Email</Th>
                <Th>Organizations</Th>
                <Th>Roles</Th>
                <Th>Status</Th>
                <Th>Created</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {userProfiles.map((user) => (
                <Tr key={user.id} _hover={{ bg: 'gray.50' }}>
                  <Td>
                    <VStack align="start" spacing={1}>
                      <Text fontWeight="medium">{user.user.name}</Text>
                      <Text fontSize="xs" color="gray.500">
                        ID: {user.id}
                      </Text>
                    </VStack>
                  </Td>
                  <Td>
                    <Text fontSize="sm">{user.user.email}</Text>
                  </Td>
                  <Td>
                    <OrganizationChips organizations={user.organizations} />
                  </Td>
                  <Td>
                    <RoleChips roles={user.authorization.roles} />
                  </Td>
                  <Td>
                    <Badge
                      colorScheme={user.active ? 'green' : 'red'}
                      variant="subtle"
                    >
                      {user.active ? 'Active' : 'Inactive'}
                    </Badge>
                  </Td>
                  <Td>
                    <VStack align="start" spacing={1}>
                      <Text fontSize="sm">
                        {formatDate(user.audit?.created_on)}
                      </Text>
                      {user.audit?.created_by && (
                        <Text fontSize="xs" color="gray.500">
                          by {user.audit.created_by}
                        </Text>
                      )}
                    </VStack>
                  </Td>
                  <Td>
                    <HStack spacing={1}>
                      <IconButton
                        aria-label="Edit user"
                        icon={<FiEdit />}
                        size="sm"
                        variant="ghost"
                        onClick={() => handleEditUser(user)}
                      />
                      <IconButton
                        aria-label="Delete user"
                        icon={<FiTrash2 />}
                        size="sm"
                        variant="ghost"
                        colorScheme="red"
                        onClick={() => handleDeleteUser(user)}
                      />
                    </HStack>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>
      )}

      {/* Pagination */}
      {total > 0 && (
        <Flex justify="space-between" align="center" mt={4}>
          <Text fontSize="sm" color="gray.600">
            Showing {userProfiles.length} of {total} users
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
              isDisabled={userProfiles.length < pageSize}
              onClick={() => setPage(page + 1)}
            >
              Next
            </Button>
          </HStack>
        </Flex>
      )}

      {/* User Modal */}
      <UserModal
        isOpen={isUserModalOpen}
        onClose={() => setIsUserModalOpen(false)}
        user={selectedUser}
        onSave={handleSaveUser}
      />

      {/* Delete Confirmation Modal */}
      <DeleteUserModal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        user={selectedUser}
        onDelete={handleDeleteConfirm}
      />
    </Box>
  )
}

export default UserManagementTable