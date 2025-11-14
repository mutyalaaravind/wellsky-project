// import { HStack, VStack } from "@chakra-ui/react";
import React from "react";

export const TwoHalves = ({ children, "data-pendo": dataPendo }: { children: [any, any]; "data-pendo"?: string }) => {
  // return (
  //   <HStack h="100%" alignItems="stretch" gap={2} padding={2}>
  //     {children}
  //   </HStack>
  // Icons/Alerts/alert-outline
  // );
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "row",
        height: "100%",
        flex: "1 0 0",
        minHeight: "0",
        alignItems: "stretch",
        gap: "1rem",
        padding: "0.5rem",
      }}
      data-pendo={dataPendo}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          width: "calc(50% - 0.5rem)",

          borderRadius: "4px",
          background: "var(--Neutral-ws-neutral-50, #FFF)",

          boxShadow:
            "0px 2px 1px -1px rgba(0, 0, 0, 0.20), 0px 1px 1px 0px rgba(0, 0, 0, 0.14), 0px 1px 3px 0px rgba(0, 0, 0, 0.12)",
        }}
        data-pendo="widget-left-panel"
      >
        {children[0]}
      </div>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          width: "calc(50% - 0.5rem)",
          paddingRight: "0.5rem",

          borderRadius: "4px",
          background: "var(--Neutral-ws-neutral-50, #FFF)",

          boxShadow:
            "0px 2px 1px -1px rgba(0, 0, 0, 0.20), 0px 1px 1px 0px rgba(0, 0, 0, 0.14), 0px 1px 3px 0px rgba(0, 0, 0, 0.12)",
        }}
        data-pendo="widget-right-panel"
      >
        {children[1]}
      </div>
    </div>
  );
};
