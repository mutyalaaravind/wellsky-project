import React from 'react';
import ReactDOM from 'react-dom/client';
import reportWebVitals from './reportWebVitals';
import { ChakraProvider } from '@chakra-ui/react'
import { lightTheme } from '@mediwareinc/wellsky-dls-react'
import App from './app';

type InitArgs = {
  el: HTMLElement;
}

declare global {
  interface Window {
    init: (args: InitArgs) => void;
  }
}

const root = ReactDOM.createRoot(document.getElementById('clinical-saver-demo-root') as HTMLElement);
root.render(
  <ChakraProvider theme={lightTheme}>
    <App />
  </ChakraProvider>
);

reportWebVitals();
