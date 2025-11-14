import React from "react";

export const BackContext = React.createContext({
  addBackHandler: (_: () => void) => {},
  back: () => {},
});

export const BackProvider = ({ children }: { children: React.ReactNode }) => {
  const [callbacks, setCallbacks] = React.useState<(() => void)[]>([]);

  React.useEffect(() => {
    const handleEscapeKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        if (callbacks.length) {
          const callback = callbacks[callbacks.length - 1];
          if (callback) {
            callback();
          }
        }
      }
    };
    window.addEventListener("keydown", handleEscapeKey);
    return () => window.removeEventListener("keydown", handleEscapeKey);
  }, [callbacks]);

  const addBackHandler = React.useCallback((callback: () => void) => {
    setCallbacks((prev) => [...prev, callback]);
    return () => {
      setCallbacks((prev) => prev.filter((cb) => cb !== callback));
    };
  }, []);

  const back = React.useCallback(() => {
    if (callbacks.length === 0) {
      throw new Error("No back callbacks registered");
    }
    const callback = callbacks[callbacks.length - 1];
    if (callback) {
      callback();
    } else {
      throw new Error('"Back" callback is undefined');
    }
  }, [callbacks]);

  return (
    <BackContext.Provider value={{ addBackHandler, back }}>
      {children}
    </BackContext.Provider>
  );
};
