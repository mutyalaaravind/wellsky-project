import { MagicSparkle } from "./MagicSparkle";
import { IconButton, IconButtonProps } from "@chakra-ui/react";
import { Close } from "@mediwareinc/wellsky-dls-react-icons";

interface SparkleButtonProps extends Omit<IconButtonProps, "aria-label"> {
  mode?: "open" | "close";
  "data-pendo"?: string;
}

const SparkleButton = (props: SparkleButtonProps) => {
  const { mode, "data-pendo": dataPendo, ...rest } = props;

  // Generate default data-pendo attributes based on mode if not provided
  const defaultDataPendo =
    mode === "close" ? "widget-close-button" : "widget-open-button";

  return (
    <IconButton
      icon={
        mode === "open" ? (
          <MagicSparkle fontSize={40} animated={true} />
        ) : (
          <Close />
        )
      }
      aria-label={"Medication extraction widget"}
      onClick={props.onClick}
      position={mode === "open" ? "fixed" : "absolute"}
      top={"84px"}
      zIndex={1401}
      borderRadius={"50% 0 0 50%"}
      width={"40px"}
      height={"40px"}
      bgColor={"white"}
      color={"initial"}
      boxShadow={mode === "open" ? "dark-lg" : "none"}
      boxSizing="border-box"
      data-pendo={dataPendo || defaultDataPendo}
      {...(mode === "open" ? { right: 0 } : { left: "-40px" })}
      {...rest}
    />
  );
};

export default SparkleButton;
