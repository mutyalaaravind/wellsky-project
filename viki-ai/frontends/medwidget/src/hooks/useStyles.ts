import { useContext, useEffect } from "react";

import { ShadowDOMContext } from "../context/ShadowDOMContext";

export const useStyles = (styles: any) => {
  const { shadowRoot } = useContext(ShadowDOMContext);
  useEffect(() => {
    styles.use({ target: shadowRoot });
    return () => {
      styles.unuse();
    };
  }, [styles, shadowRoot]);
  if (typeof shadowRoot === "undefined" || shadowRoot === null) {
    throw new Error("useStyles must be used within a ShadowDOMProvider");
  }
};
