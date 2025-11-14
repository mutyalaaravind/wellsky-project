import { ReactNode } from "react";

export interface ExpandableBoxProps {
  children?: ReactNode;
  buttonPlacement?: "left" | "right";
  isOpen?: boolean;
  toggle?: (index?: number) => void;
  id?: string;
  hideToggleButton?: boolean;
}
