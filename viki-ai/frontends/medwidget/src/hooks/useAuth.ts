import { useContext } from "react";

import { AuthContext, AuthContextType } from "../context/AuthContext";

type UseAuthType = () => AuthContextType;

export const useAuth: UseAuthType = () => {
  const authContext: AuthContextType = useContext(AuthContext);
  return authContext;
};
