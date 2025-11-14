import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Button,
  Text,
  VStack,
  HStack,
  Alert,
  AlertIcon,
  useToast,
} from '@chakra-ui/react'
import { useState } from 'react'
import { UserProfile } from '../../services/userProfilesService'
import OrganizationChips from './OrganizationChips'
import RoleChips from './RoleChips'

interface DeleteUserModalProps {
  isOpen: boolean
  onClose: () => void
  user: UserProfile | null
  onDelete: (userId: string) => Promise<{ success: boolean; error?: string }>
}

const DeleteUserModal: React.FC<DeleteUserModalProps> = ({
  isOpen,
  onClose,
  user,
  onDelete,
}) => {
  const [isDeleting, setIsDeleting] = useState(false)
  const toast = useToast()

  const handleDelete = async () => {
    if (!user) return

    setIsDeleting(true)
    try {
      const result = await onDelete(user.id)
      if (result.success) {
        toast({
          title: 'User deleted',
          description: `${user.user.name} has been successfully deleted.`,
          status: 'success',
          duration: 3000,
          isClosable: true,
        })
        onClose()
      } else {
        toast({
          title: 'Delete failed',
          description: result.error || 'Failed to delete user',
          status: 'error',
          duration: 5000,
          isClosable: true,
        })
      }
    } catch (error) {
      toast({
        title: 'Delete failed',
        description: 'An unexpected error occurred',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setIsDeleting(false)
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="md">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader color="red.600">Delete User</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <VStack spacing={4} align="stretch">
            <Alert status="warning">
              <AlertIcon />
              <Text fontSize="sm">
                This action will permanently delete the user. This cannot be undone.
              </Text>
            </Alert>

            {user && (
              <VStack spacing={3} align="stretch" bg="gray.50" p={4} borderRadius="md">
                <HStack justify="space-between">
                  <Text fontSize="sm" fontWeight="medium" color="gray.600">
                    Name:
                  </Text>
                  <Text fontSize="sm">{user.user.name}</Text>
                </HStack>

                <HStack justify="space-between">
                  <Text fontSize="sm" fontWeight="medium" color="gray.600">
                    Email:
                  </Text>
                  <Text fontSize="sm">{user.user.email}</Text>
                </HStack>

                <VStack align="stretch" spacing={2}>
                  <Text fontSize="sm" fontWeight="medium" color="gray.600">
                    Organizations:
                  </Text>
                  <OrganizationChips organizations={user.organizations} />
                </VStack>

                <VStack align="stretch" spacing={2}>
                  <Text fontSize="sm" fontWeight="medium" color="gray.600">
                    Roles:
                  </Text>
                  <RoleChips roles={user.authorization.roles} />
                </VStack>
              </VStack>
            )}

            <Text fontSize="sm" color="gray.600">
              Are you sure you want to delete this user?
            </Text>
          </VStack>
        </ModalBody>

        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose} isDisabled={isDeleting}>
            Cancel
          </Button>
          <Button
            colorScheme="red"
            onClick={handleDelete}
            isLoading={isDeleting}
            loadingText="Deleting..."
          >
            Delete User
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}

export default DeleteUserModal