import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  HStack,
  Select,
  Box,
  Text,
  IconButton,
  useToast,
  Checkbox,
  CheckboxGroup,
  Stack,
  Alert,
  AlertIcon,
  Tooltip,
} from '@chakra-ui/react'
import { useState, useEffect, useMemo } from 'react'
import { FiPlus, FiTrash2 } from 'react-icons/fi'
import {
  UserProfile,
  UserProfileCreateRequest,
  UserProfileUpdateRequest,
  OrganizationData,
} from '../../services/userProfilesService'
import { useUserProfile } from '../../hooks/useUserProfile'
import { useReferenceData } from '../../hooks/useReferenceData'

interface UserModalProps {
  isOpen: boolean
  onClose: () => void
  user?: UserProfile | null
  onSave: (userData: UserProfileCreateRequest | UserProfileUpdateRequest) => Promise<{ success: boolean; error?: string }>
}

const UserModal: React.FC<UserModalProps> = ({
  isOpen,
  onClose,
  user,
  onSave,
}) => {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [organizations, setOrganizations] = useState<OrganizationData[]>([])
  const [roles, setRoles] = useState<string[]>([])
  const [active, setActive] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const toast = useToast()

  const { resolvedRoles } = useUserProfile()
  const { businessUnits, solutions, loading: referenceLoading, error: referenceError } = useReferenceData()

  // Create memoized options for business units and solutions
  const sortedBusinessUnits = useMemo(() => {
    return [...businessUnits].sort((a, b) => a.name.localeCompare(b.name))
  }, [businessUnits])

  const getSolutionsForBusinessUnit = useMemo(() => {
    return (buCode: string) => solutions.filter(solution => solution.bu_code === buCode)
  }, [solutions])

  // Create comprehensive role lists and access logic
  const userExistingRoleIds = user?.authorization.roles || []
  const currentUserAvailableRoleIds = resolvedRoles.map(role => role.id)
  const currentUserIsSuperuser = resolvedRoles.some(role => role.id.toLowerCase() === 'superuser')

  // Create a role map with both IDs and display info
  const roleInfoMap = new Map<string, { id: string; name: string }>()

  // First add user's existing roles (use their role IDs)
  userExistingRoleIds.forEach(roleId => {
    // Try to find the role info from current user's resolved roles
    const roleInfo = resolvedRoles.find(r => r.id === roleId)
    if (roleInfo) {
      roleInfoMap.set(roleId, { id: roleInfo.id, name: roleInfo.name })
    } else {
      // Fallback: use the role ID as both ID and name
      roleInfoMap.set(roleId, { id: roleId, name: roleId })
    }
  })

  // Then add current user's available roles (only if not already present)
  resolvedRoles.forEach(role => {
    if (!roleInfoMap.has(role.id)) {
      roleInfoMap.set(role.id, { id: role.id, name: role.name })
    }
  })

  // Sort by display name for consistent UI
  const allDisplayedRoleInfo = Array.from(roleInfoMap.values()).sort((a, b) => a.name.localeCompare(b.name))

  // Determine if a role should be disabled
  const isRoleDisabled = (roleId: string) => {
    // Superuser is always disabled (cannot be removed)
    if (roleId.toLowerCase() === 'superuser') return true

    // If current user is superuser, they can modify all roles except superuser
    if (currentUserIsSuperuser) return false

    // Role is disabled if user has it but current user doesn't have access to it
    const userHasRole = userExistingRoleIds.includes(roleId)
    const currentUserHasAccess = currentUserAvailableRoleIds.includes(roleId)

    return userHasRole && !currentUserHasAccess
  }

  const isEditMode = !!user

  useEffect(() => {
    if (isOpen) {
      if (user) {
        // Edit mode - populate with existing data (use role IDs)
        setName(user.user.name)
        setEmail(user.user.email)
        setOrganizations(user.organizations.length > 0 ? user.organizations : [{ business_unit: '', solution_code: '' }])
        setRoles(user.authorization.roles) // These are already role IDs
        setActive(user.active)
      } else {
        // Add mode - reset to defaults
        setName('')
        setEmail('')
        setOrganizations([{ business_unit: '', solution_code: '' }])
        setRoles([])
        setActive(true)
      }
      setErrors({})
    }
  }, [isOpen, user])

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!name.trim()) {
      newErrors.name = 'Name is required'
    }

    if (!email.trim()) {
      newErrors.email = 'Email is required'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = 'Please enter a valid email address'
    }

    if (roles.length === 0) {
      newErrors.roles = 'At least one role must be selected'
    }

    // Validate organizations
    const validOrgs = organizations.filter(org => org.business_unit.trim() || org.solution_code.trim())
    if (validOrgs.length === 0) {
      newErrors.organizations = 'At least one organization must be specified'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const addOrganization = () => {
    setOrganizations([...organizations, { business_unit: '', solution_code: '' }])
  }

  const removeOrganization = (index: number) => {
    if (organizations.length > 1) {
      setOrganizations(organizations.filter((_, i) => i !== index))
    }
  }

  const updateOrganization = (index: number, field: 'business_unit' | 'solution_code', value: string) => {
    const updated = organizations.map((org, i) =>
      i === index ? { ...org, [field]: value } : org
    )
    setOrganizations(updated)
  }

  const handleSave = async () => {
    if (!validateForm()) return

    setIsSaving(true)
    try {
      // Filter out empty organizations
      const validOrganizations = organizations.filter(org =>
        org.business_unit.trim() || org.solution_code.trim()
      ).map(org => ({
        business_unit: org.business_unit.trim() || '*',
        solution_code: org.solution_code.trim() || '*'
      }))

      let userData: UserProfileCreateRequest | UserProfileUpdateRequest

      if (isEditMode) {
        userData = {
          name: name.trim(),
          organizations: validOrganizations,
          roles,
          active,
        }
      } else {
        userData = {
          name: name.trim(),
          email: email.trim(),
          organizations: validOrganizations,
          roles,
        }
      }

      const result = await onSave(userData)
      if (result.success) {
        toast({
          title: `User ${isEditMode ? 'updated' : 'created'}`,
          description: `${name} has been successfully ${isEditMode ? 'updated' : 'created'}.`,
          status: 'success',
          duration: 3000,
          isClosable: true,
        })
        onClose()
      } else {
        toast({
          title: `${isEditMode ? 'Update' : 'Create'} failed`,
          description: result.error || `Failed to ${isEditMode ? 'update' : 'create'} user`,
          status: 'error',
          duration: 5000,
          isClosable: true,
        })
      }
    } catch (error) {
      toast({
        title: `${isEditMode ? 'Update' : 'Create'} failed`,
        description: 'An unexpected error occurred',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalOverlay />
      <ModalContent maxH="90vh" overflow="hidden">
        <ModalHeader>{isEditMode ? 'Edit User' : 'Add New User'}</ModalHeader>
        <ModalCloseButton />
        <ModalBody overflow="auto">
          <VStack spacing={4} align="stretch">
            {referenceError && (
              <Alert status="error">
                <AlertIcon />
                Failed to load reference data: {referenceError}
              </Alert>
            )}
            <FormControl isInvalid={!!errors.name} isRequired>
              <FormLabel>Name</FormLabel>
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter user's full name"
              />
              {errors.name && (
                <Text color="red.500" fontSize="sm" mt={1}>
                  {errors.name}
                </Text>
              )}
            </FormControl>

            <FormControl isInvalid={!!errors.email} isRequired>
              <FormLabel>Email</FormLabel>
              <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter user's email address"
                isDisabled={isEditMode}
              />
              {errors.email && (
                <Text color="red.500" fontSize="sm" mt={1}>
                  {errors.email}
                </Text>
              )}
              {isEditMode && (
                <Text fontSize="xs" color="gray.500" mt={1}>
                  Email cannot be changed in edit mode
                </Text>
              )}
            </FormControl>

            <FormControl isInvalid={!!errors.organizations} isRequired>
              <FormLabel>Organizations</FormLabel>
              <VStack spacing={2} align="stretch">
                {organizations.map((org, index) => (
                  <HStack key={index} spacing={2}>
                    <Select
                      placeholder="Business Unit (or * for Any BU)"
                      value={org.business_unit}
                      onChange={(e) => updateOrganization(index, 'business_unit', e.target.value)}
                      flex={1}
                      isDisabled={referenceLoading}
                    >
                      <option value="*">Any BU</option>
                      {sortedBusinessUnits.map(businessUnit => (
                        <option key={businessUnit.bu_code} value={businessUnit.bu_code}>
                          {businessUnit.name}
                        </option>
                      ))}
                    </Select>
                    <Select
                      placeholder="Solution Code (or * for Any Solution)"
                      value={org.solution_code}
                      onChange={(e) => updateOrganization(index, 'solution_code', e.target.value)}
                      flex={1}
                      isDisabled={referenceLoading}
                    >
                      <option value="*">Any Solution</option>
                      {org.business_unit && org.business_unit !== '*'
                        ? getSolutionsForBusinessUnit(org.business_unit).map(solution => (
                            <option key={solution.code} value={solution.code}>
                              {solution.name} ({solution.code})
                            </option>
                          ))
                        : solutions.map(solution => (
                            <option key={solution.code} value={solution.code}>
                              {solution.name} ({solution.code})
                            </option>
                          ))
                      }
                    </Select>
                    {organizations.length > 1 && (
                      <IconButton
                        aria-label="Remove organization"
                        icon={<FiTrash2 />}
                        size="sm"
                        variant="ghost"
                        colorScheme="red"
                        onClick={() => removeOrganization(index)}
                      />
                    )}
                  </HStack>
                ))}
                <Button
                  leftIcon={<FiPlus />}
                  variant="outline"
                  size="sm"
                  onClick={addOrganization}
                >
                  Add Organization
                </Button>
              </VStack>
              {errors.organizations && (
                <Text color="red.500" fontSize="sm" mt={1}>
                  {errors.organizations}
                </Text>
              )}
            </FormControl>

            <FormControl isInvalid={!!errors.roles} isRequired>
              <FormLabel>Roles</FormLabel>
              {allDisplayedRoleInfo.length === 0 ? (
                <Alert status="warning" size="sm">
                  <AlertIcon />
                  <Text fontSize="sm">
                    No roles available. You can only assign roles that you currently have.
                  </Text>
                </Alert>
              ) : (
                <CheckboxGroup value={roles} onChange={(value) => {
                  const newRoleIds = value as string[]
                  // Preserve disabled roles that were originally assigned to the user
                  const disabledRoleIds = userExistingRoleIds.filter(roleId => isRoleDisabled(roleId))
                  const enabledRoleIds = newRoleIds.filter(roleId => !isRoleDisabled(roleId))
                  const combinedRoleIds = [...new Set([...enabledRoleIds, ...disabledRoleIds])]
                  setRoles(combinedRoleIds)
                }}>
                  <Stack direction="column" spacing={2}>
                    {allDisplayedRoleInfo.map((roleInfo) => {
                      const disabled = isRoleDisabled(roleInfo.id)
                      const tooltipLabel = disabled
                        ? (roleInfo.id.toLowerCase() === 'superuser'
                            ? 'Superuser role cannot be removed from any user'
                            : 'This role cannot be removed as you don\'t have access to it')
                        : ''

                      return (
                        <Tooltip
                          key={roleInfo.id}
                          label={tooltipLabel}
                          isDisabled={!disabled}
                          hasArrow
                          placement="right"
                        >
                          <Box>
                            <Checkbox
                              value={roleInfo.id}
                              isDisabled={disabled}
                            >
                              <HStack spacing={2}>
                                <Text color={disabled ? 'gray.500' : 'inherit'}>{roleInfo.name}</Text>
                                {disabled && (
                                  <Text fontSize="xs" color="gray.400" fontStyle="italic">
                                    {roleInfo.id.toLowerCase() === 'superuser' ? '(protected)' : '(read-only)'}
                                  </Text>
                                )}
                              </HStack>
                            </Checkbox>
                          </Box>
                        </Tooltip>
                      )
                    })}
                  </Stack>
                </CheckboxGroup>
              )}
              {errors.roles && (
                <Text color="red.500" fontSize="sm" mt={1}>
                  {errors.roles}
                </Text>
              )}
              {isEditMode && allDisplayedRoleInfo.length > 0 && (
                <Text fontSize="xs" color="gray.600" mt={2}>
                  • You can only assign/remove roles that you have access to<br/>
                  • Roles marked as "read-only" cannot be modified<br/>
                  • Superuser roles are protected and cannot be removed
                </Text>
              )}
            </FormControl>

            {isEditMode && (
              <FormControl>
                <Checkbox isChecked={active} onChange={(e) => setActive(e.target.checked)}>
                  Active User
                </Checkbox>
                <Text fontSize="xs" color="gray.500" mt={1}>
                  Inactive users cannot access the system
                </Text>
              </FormControl>
            )}

            {Object.keys(errors).length > 0 && (
              <Alert status="error" size="sm">
                <AlertIcon />
                <Text fontSize="sm">Please correct the errors above before saving.</Text>
              </Alert>
            )}
          </VStack>
        </ModalBody>

        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose} isDisabled={isSaving}>
            Cancel
          </Button>
          <Button
            style={{ backgroundColor: 'var(--palette-accent-ws-elm-500)' }}
            color="white"
            _hover={{ backgroundColor: 'var(--Secondary-ws-elm-700)' }}
            onClick={handleSave}
            isLoading={isSaving}
            loadingText={isEditMode ? 'Updating...' : 'Creating...'}
          >
            {isEditMode ? 'Update User' : 'Create User'}
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}

export default UserModal