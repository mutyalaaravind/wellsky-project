import React from "react";

export type AuthContextType = {
  token: string;
  ehrToken: string;
  oktaToken: string;
  patientId: string;
};

export const AuthContext = React.createContext<AuthContextType>({
  token: "",
  patientId: "",
  ehrToken: "",
  oktaToken: "",
});

export const AuthProvider: React.FC<{
  value: AuthContextType;
  children: React.ReactNode;
}> = ({ value, children }) => {
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
