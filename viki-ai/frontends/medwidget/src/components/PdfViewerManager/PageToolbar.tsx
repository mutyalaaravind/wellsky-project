import { IconButton } from "@chakra-ui/react";
import { ZoomOut, ZoomIn } from "@mediwareinc/wellsky-dls-react-icons";
import { Rotate90DegCCW } from "icons/Rotate90DegCCW";
import { Rotate90DegCW } from "icons/Rotate90DegCW";
import { ZoomFit } from "icons/ZoomFit";
import React from "react";
import { positiveModulo } from "utils/helpers";

type PageToolbarProps = {
  currentPage: number;
  totalPages: number;
  rotation: number;
  setRotation: React.Dispatch<React.SetStateAction<number>>;
  zoom: number;
  setZoom: React.Dispatch<React.SetStateAction<number>>;
};

const PageToolbar = ({
  currentPage,
  totalPages,
  rotation,
  setRotation,
  zoom,
  setZoom,
}: PageToolbarProps) => {
  return (
    <div
      style={{
        display: "flex",
        flex: 1,
        flexDirection: "column",
        minWidth: 0,
        fontSize: "12px",
      }}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
          gap: "0.5rem",
          padding: "0 0.5rem",
          color: "#FFFFFF",
          backgroundColor: "#10222F",
        }}
      >
        <span>
          Page {currentPage} of {totalPages}
        </span>

        <div style={{ flex: 1 }}></div>

        <IconButton
          variant="link"
          aria-label="Zoom To Fit"
          onClick={() => {
            setZoom(1);
          }}
        >
          <ZoomFit />
        </IconButton>
        <div>&nbsp;</div>
        <IconButton
          variant="link"
          aria-label="Zoom Out"
          onClick={() => setZoom(Math.max(0.1, zoom - 0.1))}
          color={"#fff"}
        >
          <ZoomOut />
        </IconButton>
        <span style={{ width: "3rem", textAlign: "center" }}>
          {Math.round(zoom * 100)}%
        </span>
        <IconButton
          variant="link"
          aria-label="Zoom In"
          onClick={() => setZoom(Math.min(2, zoom + 0.1))}
          color={"#fff"}
        >
          <ZoomIn />
        </IconButton>

        <div>&nbsp;</div>
        <div>&nbsp;</div>

        <IconButton
          variant="link"
          aria-label="Rotate 90° Counter-Clockwise"
          onClick={() => setRotation(rotation - 90)}
        >
          <Rotate90DegCCW />
        </IconButton>
        <span style={{ width: "3rem", textAlign: "center" }}>
          {positiveModulo(rotation, 360)}°
        </span>
        <IconButton
          variant="link"
          aria-label="Rotate 90° Clockwise"
          onClick={() => setRotation(rotation + 90)}
        >
          <Rotate90DegCW />
        </IconButton>
      </div>
    </div>
  );
};

export default PageToolbar;
