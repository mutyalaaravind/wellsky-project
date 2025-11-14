import { useCallback } from "react";
import { useOktaAuth } from "@okta/okta-react";
import useEnvJson from "./useEnvJson";
import { Env } from "../types/env";

export const useAuth = () => {
  const oktaAuthResult = useOktaAuth();
  const env = useEnvJson<Env>();

  // Check if Okta is disabled (useOktaAuth returns null when bypassed)
  const isOktaDisabled = oktaAuthResult === null;

  // Provide mock authentication state when Okta is disabled
  if (isOktaDisabled) {
    // Use OKTA_DISABLE_MOCK_USER if available, otherwise fall back to defaults
    const mockUserEmail = env?.OKTA_DISABLE_MOCK_USER || 'admin@localhost';
    const mockUserName = env?.OKTA_DISABLE_MOCK_USER
      ? env.OKTA_DISABLE_MOCK_USER.split('@')[0]
          .split('.')
          .map(token => token.charAt(0).toUpperCase() + token.slice(1))
          .join(' ') + ' (MOCK)'
      : 'Admin User (MOCK)';

    const mockUserClaims = {
      name: mockUserName,
      email: mockUserEmail,
      sub: mockUserEmail,
      'group-roles': 'superuser'
    };

    const mockAuthState = {
      isAuthenticated: true,
      idToken: {
        claims: mockUserClaims
      }
    };

    return {
      authState: mockAuthState,
      oktaAuth: null,
      getUserId: () => mockUserEmail,
      signOut: () => console.log('Mock sign out'),
      signIn: () => console.log('Mock sign in'),
      isAuthenticated: true,
      isLoading: false,
      userClaims: mockUserClaims,
    };
  }

  // Use real Okta authentication when enabled
  const { oktaAuth, authState } = oktaAuthResult;

  const getUserId = useCallback(() => {
    return authState?.idToken?.claims.email ||
           authState?.idToken?.claims.sub ||
           "admin";
  }, [authState]);

  const signOut = useCallback(() => {
    oktaAuth.signOut();
  }, [oktaAuth]);

  const signIn = useCallback(() => {
    oktaAuth.setOriginalUri("/");
    oktaAuth.signInWithRedirect();
  }, [oktaAuth]);

  return {
    authState,
    oktaAuth,
    getUserId,
    signOut,
    signIn,
    isAuthenticated: authState?.isAuthenticated || false,
    isLoading: !authState,
    userClaims: authState?.idToken?.claims,
  };
};