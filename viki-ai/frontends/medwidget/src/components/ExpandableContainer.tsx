import { Flex } from "@chakra-ui/react";
import { useExpandableContext } from "context/ExpandableContext";
import React from "react";
import { ExpandableBoxProps } from "./types";

interface ExpandableContainerProps {
  children?: React.ReactNode;
}

function ExpandableContainer({ children }: ExpandableContainerProps) {
  const { collapsedBoxes, toggleBox } = useExpandableContext();

  const childrenArray = React.Children.map(children, (child, index) => {
    if (React.isValidElement<ExpandableBoxProps>(child)) {
      return React.cloneElement(child, {
        isOpen: !collapsedBoxes.has(index === 0 ? 1 : 0),
        toggle: () => toggleBox(index),
        hideToggleButton:
          collapsedBoxes.size === 1 && collapsedBoxes.has(index),
      });
    }
    return child;
  });

  return (
    <Flex direction="row" padding="1rem" gap="1rem" flex="1 1 0%">
      {childrenArray}
    </Flex>
  );
}

export default ExpandableContainer;
