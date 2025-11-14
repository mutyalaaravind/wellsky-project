import React from 'react';
import ReactDOM from 'react-dom/client';
import Formographer from './Formographer';
import reportWebVitals from './reportWebVitals';
import { ConfigProvider } from 'antd';
import { StyleProvider } from '@ant-design/cssinjs';

type InitArgs = {
  el: HTMLElement;
}

declare global {
  interface Window {
    initFormographer: (args: InitArgs) => void;
  }
}

window.initFormographer = ({ el }: InitArgs) => {
  const shadowRoot = el.attachShadow({ mode: 'open' });
  const root = ReactDOM.createRoot(shadowRoot);
  // Create div for pop-ups and add it to shadowRoot
  const popups = document.createElement('div');
  shadowRoot.appendChild(popups);
  root.render(
    <React.StrictMode>
      <ConfigProvider getPopupContainer={_node => popups}>
        <StyleProvider container={shadowRoot}>
          <Formographer root={shadowRoot} />
        </StyleProvider>
      </ConfigProvider>
    </React.StrictMode>
  );
};

reportWebVitals();
