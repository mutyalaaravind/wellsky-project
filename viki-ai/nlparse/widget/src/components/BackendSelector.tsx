import React from 'react';

import { Select } from '@mediwareinc/wellsky-dls-react';

type BackendSelectorProps = {
  onChange: (text: string) => any,
};
export const BackendSelector: React.FC<BackendSelectorProps> = ({ onChange }: BackendSelectorProps) => {
  const [currentBackend, setCurrentBackend] = React.useState<string>('google_v1');
  React.useEffect(() => {
    onChange(currentBackend)
  }, [currentBackend, onChange]);
  const onBackendSelected = React.useCallback((e: any) => {
    setCurrentBackend(e.target.value);
  }, []);
  return (
    <Select style={{ width: '100%' }} defaultValue="google_v1" onChange={onBackendSelected} label="Backend">
      <option value="google_v1">Google (V1)</option>
      <option value="aws_transcribe">AWS Transcribe</option>
    </Select>
  );
};


