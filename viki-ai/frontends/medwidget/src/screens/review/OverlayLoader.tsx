import { SpinnerProps } from "@chakra-ui/react";
import { Spinner } from "@mediwareinc/wellsky-dls-react";
import { CSSProperties, ReactNode } from "react";

type Props = {
  children?: ReactNode;
  size?: SpinnerProps["size"];
  style?: CSSProperties;
};

const OverlayLoader = ({
  children = "working on it...",
  size,
  style,
}: Props) => {
  return (
    <div
      style={{
        position: "absolute",
        inset: "0",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100%",
        flexDirection: "column",
        gap: "1rem",
        padding: "2rem",
        backgroundColor: "rgba(255, 255, 255, 0.8)",
        zIndex: "2",
        ...style,
      }}
      data-pendoid="overlay-loader"
    >
      <Spinner size={size} />
      {children}
    </div>
  );
};

export default OverlayLoader;
