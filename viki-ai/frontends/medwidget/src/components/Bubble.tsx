import React from "react";

import { useToken } from "@chakra-ui/react";

export const Bubble = ({
  score,
  text,
  selected,
  onClick,
}: {
  score: number;
  text: string;
  selected: boolean;
  onClick: () => void;
}) => {
  const [inactiveColor, activeColor] = useToken("colors", [
    "neutral.100",
    "elm.700",
  ]);
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "0.5rem",
        alignItems: "center",
        justifyContent: "center",
        cursor: "pointer",
      }}
      onClick={onClick}
    >
      <div
        style={{
          width: "64px",
          height: "64px",
          borderRadius: "50%",
          backgroundColor: selected ? activeColor : inactiveColor,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: "1.5rem",
          color: selected ? "white" : "black",
          transition: "all 0.2s ease-in-out",
        }}
      >
        {score}
      </div>
      <div>{text}</div>
    </div>
  );
};
