import React from 'react';

import './Formographer.css';

import { FloatButton, Drawer, Button } from 'antd';

type FormographerProps = {
  root: ShadowRoot,
};

function Formographer({ root }: FormographerProps) {
  const [isOpen, setIsOpen] = React.useState(false);

  const open = React.useCallback(() => {
    setIsOpen(true);
  }, []);

  const onClose = React.useCallback(() => {
    setIsOpen(false);
  }, []);

  return (
    <>
      <FloatButton tooltip="AI Form Completion" onClick={open} type="primary" />
      <Drawer placement="right" onClose={onClose} open={isOpen} mask={false}>
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
          <div style={{ flex: 1 }}>
            Hello world!
          </div>
          <div>
            <Button
              type={'primary'}
              size="large"
              onClick={() => alert(':)')}
              block
            >
              Test button
            </Button>
          </div>
        </div>
      </Drawer>
    </>
  );
};

export default Formographer;
