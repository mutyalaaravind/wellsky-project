import ReactDOM from 'react-dom/client';
import { NLParseWidget } from './NLParse';
import reportWebVitals from './reportWebVitals';
import { ChakraProvider } from '@chakra-ui/react'
import { lightTheme } from '@mediwareinc/wellsky-dls-react'
// import audioPlayerCSS from '!!css-loader?{"sourceMap":false,"exportType":"string"}!react-h5-audio-player/lib/styles.css';  // https://stackoverflow.com/a/77251140/3455614

type InitWidgetArgs = {
  el: HTMLElement;
  text: string;
  onConfirm?: (text: string) => void;
}

declare global {
  interface Window {
    initNLParseWidget: (args: InitWidgetArgs) => void;
  }
}

window.initNLParseWidget = ({ el, text }: InitWidgetArgs) => {
  // AutoScribe widget
  const reactRoot = ReactDOM.createRoot(el);
  reactRoot.render(
    <ChakraProvider theme={lightTheme}>
      <NLParseWidget text={text} />
    </ChakraProvider>
  );
  return () => reactRoot.unmount();
};

reportWebVitals();
