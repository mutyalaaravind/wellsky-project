import { createContext, ReactNode, useContext, useMemo } from "react";
import { MedWidgetInstanceContextType } from "types";

// import { MedWidgetInstanceContextType } from "./types";

export const MedWidgetInstanceContext = createContext<
  Partial<MedWidgetInstanceContextType>
>({});

export const MedWidgetInstanceContextProvider = ({
  children,
  medWidgetInstance,
}: {
  children?: ReactNode;
  medWidgetInstance: MedWidgetInstanceContextType["medWidgetInstance"];
}) => {
  const value: MedWidgetInstanceContextType = useMemo(() => {
    return {
      medWidgetInstance,
    };
  }, [medWidgetInstance]);

  return (
    <MedWidgetInstanceContext.Provider value={value}>
      {children}
    </MedWidgetInstanceContext.Provider>
  );
};

export const useMedWidgetInstanceContext = () => {
  return useContext(MedWidgetInstanceContext) as MedWidgetInstanceContextType;
};
