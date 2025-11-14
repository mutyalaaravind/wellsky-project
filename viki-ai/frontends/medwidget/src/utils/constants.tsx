export const isLocal =
  process.env.NODE_ENV === "development" &&
  window.location.hostname === "localhost";

const enablePdfViewerWidget = false;

export const isUsingPdfViewerWidget =
  isLocal && window.location.port === "13001" && enablePdfViewerWidget;

export const isUseNewDesign = true;

const enableApiCaching = false;

export const isUsingApiCaching = isLocal && enableApiCaching;
