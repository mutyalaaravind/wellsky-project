import React from "react";
import { CircularProgress, CircularProgressLabel } from "@chakra-ui/react";

interface CircularProgressWithLabelProps {
  value: number | null;
  size?: string;
  thickness?: string;
  color?: string;
}

export const CircularProgressWithLabel: React.FC<
  CircularProgressWithLabelProps
> = ({ value, size = "40px", thickness = "4px", color = "blue.400" }) => {
  // Handle null values and convert decimal (0.0-1.0) to percentage (0-100)
  const percentageValue = value === null ? 0 : Math.round(value * 100);

  return (
    <CircularProgress
      value={percentageValue}
      size={size}
      thickness={thickness}
      color={color}
    >
      <CircularProgressLabel fontSize="xs">
        {`${percentageValue}%`}
      </CircularProgressLabel>
    </CircularProgress>
  );
};