import { HStack, Badge } from '@chakra-ui/react'

interface RoleChipsProps {
  roles: string[]
}

const RoleChips: React.FC<RoleChipsProps> = ({ roles }) => {
  const getRoleColorScheme = (role: string): string => {
    switch (role.toLowerCase()) {
      case 'superuser':
        return 'red'
      case 'admin':
        return 'orange'
      case 'manager':
        return 'purple'
      case 'user':
        return 'blue'
      default:
        return 'gray'
    }
  }

  if (roles.length === 0) {
    return (
      <Badge variant="outline" colorScheme="gray">
        No Roles
      </Badge>
    )
  }

  return (
    <HStack spacing={1} wrap="wrap">
      {roles.map((role, index) => (
        <Badge
          key={`${role}-${index}`}
          variant="solid"
          colorScheme={getRoleColorScheme(role)}
          fontSize="xs"
          textTransform="capitalize"
        >
          {role}
        </Badge>
      ))}
    </HStack>
  )
}

export default RoleChips