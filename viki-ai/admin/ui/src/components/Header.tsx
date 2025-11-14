import { Box, Flex, Text, Avatar, Image, Button, Menu, MenuButton, MenuList, MenuItem } from '@chakra-ui/react'
import { FiChevronDown } from 'react-icons/fi'
import { useAuth } from '../hooks/useAuth'
import useEnvJson from '../hooks/useEnvJson'
import { Env } from '../types/env'
import { useEffect } from 'react'

const Header: React.FC = () => {
  const env = useEnvJson<Env>();
  const { authState, signIn, signOut, isAuthenticated, isLoading, userClaims } = useAuth();

  useEffect(() => {
    if (!authState || !env) {
      return;
    }

    if (!authState?.isAuthenticated && !env.OKTA_DISABLE) {
      signIn();
    }

    if (!env.OKTA_DISABLE && authState?.isAuthenticated) {
      // User is authenticated, no action needed
    }
  }, [authState, env, signIn]);

  if (!authState || (!authState?.isAuthenticated && !env?.OKTA_DISABLE)) {
    return (
      <Box
        w="full"
        bg="white"
        borderBottomWidth="1px"
        borderColor="gray.200"
        px={6}
        py={4}
        boxShadow="sm"
      >
        <Flex justify="center" align="center">
          <Text>Checking authentication...</Text>
        </Flex>
      </Box>
    );
  }

  // Show loading state while checking authentication
  if (isLoading || (!env?.OKTA_DISABLE && !isAuthenticated)) {
    return (
      <Box
        w="full"
        bg="white"
        borderBottomWidth="1px"
        borderColor="gray.200"
        px={6}
        py={4}
        boxShadow="sm"
      >
        <Flex justify="center" align="center">
          <Text>Checking authentication...</Text>
        </Flex>
      </Box>
    );
  }

  const getUserInitials = () => {
    if (userClaims?.name) {
      return userClaims.name.split(' ').map((n: string) => n[0]).join('').toUpperCase();
    }
    if (userClaims?.email) {
      return userClaims.email.substring(0, 2).toUpperCase();
    }
    return 'AD'; // Admin default
  };

  const getUserName = () => {
    return userClaims?.name || userClaims?.email || 'Admin User';
  };

  return (
    <Box
      w="full"
      bg="white"
      borderBottomWidth="1px"
      borderColor="gray.200"
      px={6}
      py={4}
      boxShadow="sm"
    >
      <Flex justify="space-between" align="center">
        <Flex align="center" gap={4}>
          <Image
            src="/wellsky-logo.png"
            alt="Wellsky Logo"
            height="28px"
            objectFit="contain"
          />
          <Text fontSize="xl" fontWeight="semibold" style={{ color: 'var(--Secondary-ws-elm-700)' }}>
            SkySenseOS Admin
          </Text>
        </Flex>
        
        {/* User Profile Menu */}
        <Menu>
          <MenuButton as={Button} variant="ghost" rightIcon={<FiChevronDown />}>
            <Flex align="center" gap={2}>
              <Avatar
                size="sm"
                name={getUserInitials()}
                style={{ backgroundColor: 'var(--palette-accent-ws-elm-500)' }}
                color="white"
                fontWeight="bold"
              />
              <Text fontSize="sm">{getUserName()}</Text>
            </Flex>
          </MenuButton>
          <MenuList>
            {isAuthenticated && (
              <MenuItem onClick={signOut}>
                Sign Out
              </MenuItem>
            )}
            {!isAuthenticated && env?.OKTA_DISABLE && (
              <MenuItem onClick={signIn}>
                Sign In
              </MenuItem>
            )}
          </MenuList>
        </Menu>
      </Flex>
    </Box>
  )
}

export default Header