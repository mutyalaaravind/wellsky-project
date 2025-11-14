import { useState, useCallback } from "react";

type SessionStateHook<T> = [T, (value: T) => void];

export const useSessionState = <T>(
  key: string,
  defaultValue: T,
): SessionStateHook<T> => {
  // Similar to useState, but keeps the state in sessionStorage
  const [state, setState] = useState<T>(() => {
    const storedValue = sessionStorage.getItem(key);
    return storedValue ? JSON.parse(storedValue) : defaultValue;
  });

  const setSessionState = useCallback(
    (value: T) => {
      sessionStorage.setItem(key, JSON.stringify(value));
      setState(value);
    },
    [key],
  );

  return [state, setSessionState];
};
