import {
  createContext,
  memo,
  useCallback,
  useContext,
  useMemo,
  useState,
} from "react";

export const ExpandableContext = createContext(
  {} as {
    toggleBox: (id: string | number) => void;
    collapsedBoxes: Set<string | number>;
    resetCollapsedBoxes: () => void;
  },
);

export const ExpandableContextProvider = memo(
  ({ children }: { children: React.ReactNode }) => {
    const [collapsedBoxes, setCollapsedBoxes] = useState<Set<string | number>>(
      new Set(),
    );

    const resetCollapsedBoxes = useCallback(() => {
      setCollapsedBoxes((prev) => {
        if (prev.size === 0) {
          return prev;
        }
        return new Set();
      });
    }, []);

    const toggleBox = useCallback((id: string | number) => {
      setCollapsedBoxes((prev) => {
        let newSet = new Set(prev);
        if (newSet.size === 1) {
          if (newSet.has(id)) {
            newSet.delete(id);
          } else {
            newSet.clear();
            // newSet.add(id);
          }
        } else if (newSet.size > 1) {
          newSet.clear();
          newSet.add(id);
        } else {
          newSet.add(id);
        }
        // if (newSet.has(id)) {
        //   newSet.delete(id);
        // } else {
        //   newSet.add(id);
        // }
        return newSet;
      });
    }, []);

    const value = useMemo(
      () => ({ collapsedBoxes, toggleBox, resetCollapsedBoxes }),
      [collapsedBoxes, toggleBox, resetCollapsedBoxes],
    );

    return (
      <ExpandableContext.Provider value={value}>
        {children}
      </ExpandableContext.Provider>
    );
  },
);

export const useExpandableContext = () => {
  return useContext(ExpandableContext);
};
