import { Flex } from "@chakra-ui/react";
import { useMemo } from "react";
import { ExpandableBoxProps } from "./types";
import ArrowRight from "./ArrowRight";
import ArrowLeft from "./ArrowLeft";

// CSS for responsive height adjustments
const expandableBoxStyles = `
  @media screen and (orientation: landscape) and (max-width: 1024px) {
    .expandable-box-content {
      max-height: calc(100vh - 55px - 50px) !important;
    }
  }
  
  @media screen and (orientation: landscape) and (max-width: 834px) {
    .expandable-box-content {
      max-height: calc(100vh - 55px - 45px) !important;
    }
  }
`;

// Inject styles if not already present
if (typeof document !== 'undefined' && !document.getElementById('expandable-box-styles')) {
  const style = document.createElement('style');
  style.id = 'expandable-box-styles';
  style.textContent = expandableBoxStyles;
  document.head.appendChild(style);
}

function ExpandableBox({
  children,
  buttonPlacement = "left",
  isOpen = true,
  toggle,
  id,
  hideToggleButton,
}: ExpandableBoxProps) {
  const toggleButton = useMemo(() => {
    if (hideToggleButton) {
      return null;
    }
    return (
      <Flex
        direction="column"
        justify="center"
        height="100%"
        maxW="24px"
        cursor="pointer"
        background="var(--Neutral-ws-neutral-100, #F7F7F7)"
        onClick={() => toggle?.()}
        data-pendoid={`expandable-box-toggle-button-${buttonPlacement}`}
      >
        {buttonPlacement === "right" ? (
          <ArrowRight style={{ fontSize: "20px" }} />
        ) : (
          <ArrowLeft style={{ fontSize: "20px" }} />
        )}
      </Flex>
    );
  }, [buttonPlacement, hideToggleButton, toggle]);

  return useMemo(
    () => (
      <Flex
        transition="flex 0.3s ease-in-out"
        width={isOpen ? "auto" : "20px"}
        maxW="calc(50%-8px)"
        overflow="hidden"
        data-id={id}
        gap="1px"
        align="flex-start"
        justify="space-between"
        flex={isOpen ? "1 1 0%" : "none"}
        background="var(--Neutral-ws-neutral-50, #FFF)"
        boxShadow={
          buttonPlacement === "right"
            ? "0px 2px 1px -1px rgba(0, 0, 0, 0.20), 0px 1px 1px 0px rgba(0, 0, 0, 0.14), 0px 1px 3px 0px rgba(0, 0, 0, 0.12)"
            : "0px 2px 1px -1px rgba(0, 0, 0, 0.20), 0px 1px 1px 0px rgba(0, 0, 0, 0.14), 0px 1px 3px 0px rgba(0, 0, 0, 0.12)"
        }
        data-pendoid={`expandable-box-${buttonPlacement}`}
      >
        {buttonPlacement === "left" && toggleButton}
        <Flex
          transition="width 0.5s ease-in-out"
          flex={isOpen ? "1 1 0%" : "none"}
          overflow={isOpen ? "inherit" : "hidden"}
          width={isOpen ? "inherit" : 0}
          height="-webkit-fill-available"
          padding={isOpen ? "2px" : 0}
          maxH="calc(100vh - 55px - 60px)" /* Reserve space for sticky footer */
          h={"100%"}
          className="expandable-box-content"
          data-pendoid={`expandable-box-${buttonPlacement}-content`}
        >
          {children}
        </Flex>
        {buttonPlacement === "right" && toggleButton}
      </Flex>
    ),
    [buttonPlacement, children, id, isOpen, toggleButton],
  );
}

export default ExpandableBox;
