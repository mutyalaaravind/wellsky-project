// import { useAuthStore } from '../store/use-auth-store'
// import { useTaskStore } from '../store/task-store'
// import React, { ReactNode } from 'react'
// import Link from "next/link";
import {
  Box,
  Button,
  ButtonGroup,
  Container,
  Flex,
  HStack,
  IconButton,
  VStack,
  useBreakpointValue,
} from "@chakra-ui/react";
import logo from "../images/wellsky-logo.png";
import { FiMenu } from "react-icons/fi";
import { useEffect } from "react";
import { useOktaAuth } from "@okta/okta-react";
import useEnvJson from "../hooks/useEnvJson";
import { Env } from "../types";
import { useNavigate } from "react-router-dom";
import { BreadCrum, BreadCrumProps, BreadCrumType } from "./bread-crum";

export const PortalHeader = (props: BreadCrumProps) => {
  const env: Env | null = useEnvJson();
  const router = useNavigate();
  const { oktaAuth, authState } = useOktaAuth();
  const currentUser = { username: "john.doe" }; //useAuthStore((state) => state.user)
  // const resetData = useAuthStore((state:any) => state.resetStore)
  // const resetTaskStore = useTaskStore((state:any) => state.resetTaskStore)

  const logOut = () => {
    //resetData()
    //resetTaskStore()
    //router.push('/sign-in')
  };

  const navigate = (props: { item: string }) => {
    //router.push('/' + props.item.toLowerCase())
  };

  const isDesktop = true; //useBreakpointValue({ base: false, lg: true })

  useEffect(() => {
    if (!authState) {
      return;
    }

    if (env && !authState?.isAuthenticated && !env?.OKTA_DISABLE) {
      // const originalUri = toRelativeUrl(window.location.href, window.location.origin);
      oktaAuth.setOriginalUri("/");
      oktaAuth.signInWithRedirect();
    }

    if (env && !env?.OKTA_DISABLE && authState?.isAuthenticated) {
      oktaAuth.getUser().then((info: any) => {});
    }
  }, [env, oktaAuth, authState, authState?.isAuthenticated, env?.OKTA_DISABLE]);

  const menus = [
    { label: "Patients", path: "/patients" },
    { label: "Assessments", path: "/patients" },
    { label: "Documents", path: "/patients" },
  ];

  if (!authState || (!authState?.isAuthenticated && !env?.OKTA_DISABLE)) {
    return <div>Checking login...</div>;
  }

  return (
    <>
      <HStack
        align="center"
        w="100%"
        position="sticky"
        top={0}
        zIndex={9999999}
        backgroundColor="white"
      >
        <VStack width="15%" alignItems="left">
          <Box alignItems="left">
            <img src={logo} alt="wellsky" />
          </Box>
        </VStack>
        <VStack width="50%" alignItems="left">
          <Box alignItems="left" style={{ fontSize: "18px" }}>
            Sky Health
          </Box>
        </VStack>

        <HStack width="100%" alignItems="right" justifyContent="end">
          {authState?.isAuthenticated ? (
            <>
              <Box>Signed in as {authState?.idToken?.claims.name}</Box>
              <Box style={{ paddingRight: "1rem" }}>
                <Button onClick={() => oktaAuth.signOut()}>Log out</Button>
              </Box>
            </>
          ) : null}
        </HStack>
      </HStack>
      <HStack>
        <VStack alignItems="left" justifyContent={"flex-start"}>
          {/* <Box as='section' pb={{ base: '1', md: '2' }}> */}
          <Box as="nav" bg="bg.surface" boxShadow="sm" alignItems="left">
            <Container py={{ base: "1", lg: "1" }}>
              <HStack spacing="1" justify="left">
                {isDesktop ? (
                  <Flex justify="left" flex="1">
                    <ButtonGroup variant="text" colorScheme="gray" spacing="2">
                      {menus.map((item: any) => (
                        <Button
                          style={{ fontSize: "24px" }}
                          key={item.label}
                          onClick={() => {
                            router(item.path);
                          }}
                        >
                          {item.label}
                        </Button>
                      ))}
                    </ButtonGroup>
                  </Flex>
                ) : (
                  <IconButton
                    variant="tertiary"
                    icon={<FiMenu fontSize="1.25rem" />}
                    aria-label="Open Menu"
                  />
                )}
              </HStack>
            </Container>
          </Box>
          {/* </Box> */}
        </VStack>
      </HStack>
      <HStack
        align="center"
        w="100%"
        position="sticky"
        top={0}
        zIndex={-1}
        backgroundColor="white"
      >
        <BreadCrum breadCrums={props.breadCrums} />
      </HStack>
    </>
  );
};
