import React from "react";

// currentScript is <host>/<path>/static/js/bundle.js
// env.js is in <host>/<path>/config/env.ison
// Calculate path that's 2 levels up from currentScript
const root = (document as any).currentScript.src
  .split("/")
  .slice(0, -3)
  .join("/");

const useEnvJson = <T>(): T | null => {
  const [envJson, setEnvJson] = React.useState(null);

  React.useEffect(() => {
    fetch(`${root}/config/env.json`)
      .then((res) => res.json())
      .then((data) => {
        console.log("medwidget: env.json:", data);
        setEnvJson(data);
      });
  }, []);

  return envJson !== null ? (envJson as T) : null;
};

export default useEnvJson;
