import {
  Box,
  Text,
  VStack,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Heading,
} from '@chakra-ui/react'
import UserManagementTable from '../components/UserManagement/UserManagementTable'
import LLMModelsTab from '../components/LLMModelsTab'
import RolesSection from '../components/Security/RolesSection'
import { useRBAC } from '../hooks/useRBAC'

const SettingsPage: React.FC = () => {
  const { hasPermission } = useRBAC()

  // Define available tabs with their permissions
  const availableTabs = [
    {
      id: 'user-management',
      label: 'User Management',
      component: <UserManagementTable />,
      permission: null // Always available
    },
    {
      id: 'llm-models',
      label: 'LLM Models',
      component: <LLMModelsTab />,
      permission: 'admin.settings.llmmodels'
    },
    {
      id: 'system-settings',
      label: 'System Settings',
      component: (
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
          <Text color="gray.400" fontSize="lg">
            System settings coming soon...
          </Text>
        </Box>
      ),
      permission: 'admin.settings.system'
    },
    {
      id: 'security',
      label: 'Security',
      component: <RolesSection />,
      permission: 'admin.settings.security'
    }
  ]

  // Filter tabs based on permissions
  const visibleTabs = availableTabs.filter(tab =>
    !tab.permission || hasPermission(tab.permission)
  )

  return (
    <Box>
      <VStack spacing={6} align="start">
        <Box>
          <Heading as="h1" size="lg" mb={2} color="var(--Secondary-ws-elm-700)">
            Settings
          </Heading>
          <Text fontSize="lg" color="gray.600">
            Configure your admin settings and preferences.
          </Text>
        </Box>

        <Box w="full">
          <Tabs variant="enclosed" colorScheme="blue">
            <TabList>
              {visibleTabs.map(tab => (
                <Tab key={tab.id}>{tab.label}</Tab>
              ))}
            </TabList>

            <TabPanels>
              {visibleTabs.map(tab => (
                <TabPanel key={tab.id} px={0} py={6}>
                  {tab.component}
                </TabPanel>
              ))}
            </TabPanels>
          </Tabs>
        </Box>
      </VStack>
    </Box>
  )
}

export default SettingsPage