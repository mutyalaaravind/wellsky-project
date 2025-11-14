import { HStack, Badge } from '@chakra-ui/react'
import { OrganizationData } from '../../services/userProfilesService'

interface OrganizationChipsProps {
  organizations: OrganizationData[]
}

const OrganizationChips: React.FC<OrganizationChipsProps> = ({ organizations }) => {
  const formatOrganizationLabel = (org: OrganizationData): string => {
    const businessUnit = org.business_unit === '*' ? 'Any BU' : org.business_unit
    const solutionCode = org.solution_code === '*' ? 'Any Solution' : org.solution_code
    return `${businessUnit}:${solutionCode}`
  }

  if (organizations.length === 0) {
    return (
      <Badge variant="outline" colorScheme="gray">
        No Organizations
      </Badge>
    )
  }

  return (
    <HStack spacing={1} wrap="wrap">
      {organizations.map((org, index) => (
        <Badge
          key={`${org.business_unit}-${org.solution_code}-${index}`}
          variant="outline"
          colorScheme={org.business_unit === '*' || org.solution_code === '*' ? 'green' : 'blue'}
          fontSize="xs"
        >
          {formatOrganizationLabel(org)}
        </Badge>
      ))}
    </HStack>
  )
}

export default OrganizationChips