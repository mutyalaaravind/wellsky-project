import React from "react";

import { BackContext } from "../context/BackContext";

export const useBack = () => {
  const context = React.useContext(BackContext);
  if (!context) {
    throw new Error("useBack must be used within a BackProvider");
  }
  return context;
};
