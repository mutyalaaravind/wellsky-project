import React from 'react';
import { useNavigate } from 'react-router-dom';
import { OktaAuth, toRelativeUrl } from '@okta/okta-auth-js';
import { Security } from '@okta/okta-react';
import { Env } from '../types/env';

type OktaAuthProviderProps = {
  env: Env,
  children: React.ReactNode,
};

export const OktaAuthProvider: React.FC<OktaAuthProviderProps> = ({ env, children }: OktaAuthProviderProps) => {
  const [oktaAuth, setOktaAuth] = React.useState<OktaAuth | null>(null);
  const navigate = useNavigate();
  const restoreOriginalUri = (_oktaAuth: any, originalUri: string) => {
    navigate(toRelativeUrl(originalUri || '/', window.location.origin));
  };

  // If Okta is disabled, render children directly without authentication
  if (env && env.OKTA_DISABLE) {
    return <>{children}</>;
  }

  React.useEffect(() => {
    if (env && !env.OKTA_DISABLE) {
      const redirectUri = `${window.location.protocol}//${window.location.host}/login/callback`;
      console.log('Okta Redirect URI:', redirectUri);

      setOktaAuth(new OktaAuth({
        issuer: env.OKTA_ISSUER,
        clientId: env.OKTA_CLIENT_ID,
        redirectUri: redirectUri,
        scopes: ['openid', 'email', 'profile'].concat(env.OKTA_SCOPES),
      }));
    }
  }, [env]);
  if (oktaAuth === null) {
    return <div>Loading configuration...</div>;
  }
  (window as any).oktaAuth = oktaAuth;
  return (
    <Security oktaAuth={oktaAuth} restoreOriginalUri={restoreOriginalUri}>
      {children}
    </Security>
  );
};

