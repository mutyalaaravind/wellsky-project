import React from 'react';

const root = new URL((document as any).currentScript.src).origin;

const useEnvJson = <T>(): (T | null) => {
  const [envJson, setEnvJson] = React.useState(null);

  React.useEffect(() => {
    fetch(`${root}/config/env.json`).then(res => res.json()).then(data => {
      console.log('env.json:', data)
      setEnvJson(data);
    });
  }, []);

  return envJson !== null ? envJson as T : null;
};

export default useEnvJson;
