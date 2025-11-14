import { useCallback, useState } from "react";
import { Env } from "../types";
import { useOktaAuth } from "@okta/okta-react";

export const useTokenApi = () => {
  const [tokens, setTokens] = useState<string | null>(null);
  const { oktaAuth, authState } = useOktaAuth();
  const getToken = useCallback(async (env: Env, patientId: string) => {
    const response = await fetch(`${env.DEMO_API}/tokens/${patientId}`, {
      headers: {
        userId:
          authState?.idToken?.claims.email ||
          authState?.idToken?.claims.sub ||
          "12345",
      },
    });
    const data = await response.json();

    setTokens(data);
  }, []);

  return { getToken, tokens };
};
