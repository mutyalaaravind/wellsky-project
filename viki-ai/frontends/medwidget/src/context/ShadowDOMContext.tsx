import { createContext } from "react";

type ShadowDOMContextType = {
  shadowRoot: ShadowRoot | null;
};

export const ShadowDOMContext = createContext<ShadowDOMContextType>({
  shadowRoot: null,
});
