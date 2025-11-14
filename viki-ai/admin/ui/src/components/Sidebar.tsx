import { Box, VStack, HStack, Text, Icon } from '@chakra-ui/react'
import { FiHome, FiSettings, FiDatabase, FiGrid } from 'react-icons/fi'
import { useNavigate, useLocation } from 'react-router-dom'
import RBACGuard from './RBACGuard'

interface SidebarItemProps {
  icon?: React.ElementType
  label: string
  path: string
  isActive: boolean
  onClick: () => void
}

const SidebarItem: React.FC<SidebarItemProps> = ({ icon, label, isActive, onClick }) => (
  <HStack
    w="full"
    p={3}
    cursor="pointer"
    borderRadius="md"
    bg={isActive ? 'var(--palette-accent-ws-elm-500)' : 'transparent'}
    color={isActive ? 'white' : 'rgba(255,255,255,0.8)'}
    _hover={{ bg: 'rgba(255,255,255,0.1)', color: 'white' }}
    onClick={onClick}
  >
    {icon && <Icon as={icon} size="20px" />}
    <Text fontSize="sm" fontWeight={isActive ? 'medium' : 'normal'}>
      {label}
    </Text>
  </HStack>
)

const Sidebar: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    { icon: FiHome, label: 'Home', path: '/' },
    { icon: FiGrid, label: 'Apps', path: '/apps', permissions: 'extract.apps' },
    { icon: FiDatabase, label: 'Entity Schemas', path: '/entity-schema', permissions: 'extract.entityschemas' },
  ]

  return (
    <Box
      w="250px"
      h="100%"
      bg="var(--wellsky-big-stone)"
      borderRightWidth="1px"
      borderColor="rgba(255,255,255,0.1)"
      p={4}
      display="flex"
      flexDirection="column"
    >
      {/* Navigation Items */}
      <VStack spacing={2} align="stretch" flex="1">
        {menuItems.map((item) => (
          <RBACGuard key={item.path} permissions={item.permissions}>
            <SidebarItem
              icon={item.icon}
              label={item.label}
              path={item.path}
              isActive={location.pathname === item.path}
              onClick={() => navigate(item.path)}
            />
          </RBACGuard>
        ))}
      </VStack>

      {/* Settings at bottom with cog icon */}
      <Box mt="auto">
        <SidebarItem
          icon={FiSettings}
          label="Settings"
          path="/settings"
          isActive={location.pathname === '/settings'}
          onClick={() => navigate('/settings')}
        />
      </Box>
    </Box>
  )
}

export default Sidebar