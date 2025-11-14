import React from 'react';

const root = new URL((document as any).currentScript?.src || window.location.origin).origin;

const useEnvJson = <T>(): (T | null) => {
  const [envJson, setEnvJson] = React.useState(null);

  React.useEffect(() => {
    fetch(`${root}/config/env.json`).then(res => res.json()).then(data => {
      console.log('admin env.json:', data)
      setEnvJson(data);
    }).catch(error => {
      console.error('Failed to load admin env.json:', error);
    });
  }, []);

  return envJson !== null ? envJson as T : null;
};

export default useEnvJson;