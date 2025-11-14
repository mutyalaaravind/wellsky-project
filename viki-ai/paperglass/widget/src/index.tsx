import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import { ChakraProvider } from "@chakra-ui/react";
import { lightTheme } from '@mediwareinc/wellsky-dls-react'
import App from './App';
import reportWebVitals from './reportWebVitals';
import { SearchGlass } from './SearchGlass';
import useEnvJson from './hooks/useEnvJson';
import CustomFormsComponent from './components/custom-form';
import { Env } from './types';
import { CustomFormContainer } from './components/custom-form-container';

// const root = ReactDOM.createRoot(
//   document.getElementById('root') as HTMLElement
// );
// root.render(
//   <ChakraProvider theme={lightTheme}>
//     <App />
//   </ChakraProvider>
// );

(window as any).initSearchGlass = ({ el, identifier }: any) => {
  const reactRoot = ReactDOM.createRoot(el);
  reactRoot.render(
    <ChakraProvider>
      <App identifier={identifier} />
    </ChakraProvider>
  );
  return () => reactRoot.unmount();
}

(window as any).initCustomForm = ({ el, newData, formTemplateId, formInstanceId }: any) => {
  const reactRoot = ReactDOM.createRoot(el);
  reactRoot.render(
    <ChakraProvider>
      <CustomFormContainer newData={newData} formInstanceId={formInstanceId} formTemplateId={formTemplateId} />
    </ChakraProvider>
  );
  return () => reactRoot.unmount();
}

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
