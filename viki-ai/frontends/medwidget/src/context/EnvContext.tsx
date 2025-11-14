import React from "react";
import { Env } from "types";

export type EnvContextType = Env;

export const EnvContext = React.createContext<EnvContextType>({
    API_URL: "",
    VERSION: "",
    FORMS_WIDGETS_HOST: "",
    FORMS_API: "",
    FORMS_API_KEY: "",
    IS_UPLOAD_ENABLED: "",
    NEWRELIC_ACCOUNT_ID: "",
    NEWRELIC_TRUST_KEY: "",
    NEWRELIC_APPLICATION_ID: "",
    NEWRELIC_API_BROWSER_KEY: ""
});

export const EnvProvider: React.FC<{
  value: EnvContextType;
  children: React.ReactNode;
}> = ({ value, children }) => {
  console.log("EnvProvider value",value);
  return <EnvContext.Provider value={value}>{children}</EnvContext.Provider>;
};
