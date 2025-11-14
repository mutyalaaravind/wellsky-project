import ReactDOM from 'react-dom/client';
import { AutoScribeBubble, AutoScribeReadonlyWidget, AutoScribeWidget } from './AutoScribe';
import reportWebVitals from './reportWebVitals';
import { ChakraProvider } from '@chakra-ui/react'
import { lightTheme } from '@mediwareinc/wellsky-dls-react'
import { v1 as uuidv1 } from 'uuid';
import { TextSentence } from './types';
// import audioPlayerCSS from '!!css-loader?{"sourceMap":false,"exportType":"string"}!react-h5-audio-player/lib/styles.css';  // https://stackoverflow.com/a/77251140/3455614

type InitBubbleArgs = {
  onOpen?: () => void;
  onConfirm?: (textSentences: Array<TextSentence>) => void;
  onCancel?: () => void;
  transactionId?: string;
  sectionId?: string;
  el: HTMLElement;
  reactRoot: any;
}

type InitWidgetArgs = {
  el: HTMLElement;
  reactRoot: any;
  onConfirm?: (textSentences: Array<TextSentence>) => void;
  transactionId?: string;
  sectionId?: string;
  inlineWidgetEmbedding?: boolean;
  evidences?: Array<string>;
  verbatimSourceEvidence?: string;
}

type InitReadonlyWidgetArgs = {
  el: HTMLElement;
  reactRoot: any;
  transactionId: string;
  sectionId?: string;
  evidences?: Array<string>;
  verbatimSourceEvidence?: string;
}

declare global {
  interface Window {
    initAutoScribeBubble: (args: InitBubbleArgs) => void;
    initAutoScribeWidget: (args: InitWidgetArgs) => void;
    renderAutoScribeReadonlyWidget: (args: InitReadonlyWidgetArgs) => void;

    // AutoScribeBubble: typeof AutoScribeBubble;
    // AutoScribeWidget: typeof AutoScribeWidget;
    AutoScribeReadonlyWidget: typeof AutoScribeReadonlyWidget;
    // FooBar: (props: any) => JSX.Element;
  }
}

window.initAutoScribeBubble = ({ reactRoot = null,el, onOpen, onConfirm, onCancel, transactionId, sectionId }: InitBubbleArgs) => {
  // AutoScribe bubble
  if (typeof el === 'undefined') {
    // Create new global div element
    el = document.createElement('div');
    document.body.appendChild(el);
  }
  if (reactRoot === null) {
      reactRoot = ReactDOM.createRoot(el);
      console.log('AutoScribeBubble: initial render',reactRoot);
  }
  else{
    // const root = document.createElement('div');
    // document.body.appendChild(root);
    // const reactRoot = ReactDOM.createRoot(root);
    console.log('AutoScribeBubble: re-render',reactRoot);
  }
  
  reactRoot.render(
    <ChakraProvider theme={lightTheme}>
      <AutoScribeBubble onOpen={onOpen} onConfirm={onConfirm} onCancel={onCancel} transactionId={transactionId || uuidv1()} sectionId={sectionId || 'default'} />
    </ChakraProvider>
  );
  return () => reactRoot.unmount();
};

window.initAutoScribeWidget = ({ reactRoot = null, el, onConfirm, transactionId, sectionId, inlineWidgetEmbedding, evidences, verbatimSourceEvidence }: InitWidgetArgs) => {
  // AutoScribe widget
  if (reactRoot === null) {
    reactRoot = ReactDOM.createRoot(el);
    console.log('AutoScribeReadonlyWidget: initial render');
  } else {
    console.log('AutoScribeReadonlyWidget: re-render');
  }
  reactRoot.render(
    <ChakraProvider theme={lightTheme}>
      <AutoScribeWidget onConfirm={onConfirm} transactionId={transactionId || uuidv1()} sectionId={sectionId || 'default'} inlineWidgetEmbedding={inlineWidgetEmbedding} evidences={evidences} verbatimSourceEvidence={verbatimSourceEvidence} />
    </ChakraProvider>
  );
  return reactRoot;
  // return () => reactRoot.unmount();
};

window.renderAutoScribeReadonlyWidget = ({ reactRoot = null, el, transactionId, sectionId, evidences, verbatimSourceEvidence }: InitReadonlyWidgetArgs) => {
  // AutoScribe widget
  if (reactRoot === null) {
    reactRoot = ReactDOM.createRoot(el);
    console.log('AutoScribeReadonlyWidget: initial render');
  } else {
    console.log('AutoScribeReadonlyWidget: re-render');
  }
  reactRoot.render(
    <ChakraProvider theme={lightTheme}>
      <AutoScribeReadonlyWidget transactionId={transactionId} sectionId={sectionId || 'default'} evidences={evidences} verbatimSourceEvidence={verbatimSourceEvidence} />
    </ChakraProvider>
  );
  return reactRoot;
  //return () => reactRoot.unmount();
};

// window.AutoScribeBubble = AutoScribeBubble;
// window.AutoScribeWidget = (props: any) => {
//   // Unused
//   return (
//     <ChakraProvider theme={lightTheme}>
//       <AutoScribeWidget {...props} />
//     </ChakraProvider>
//   );
// };
window.AutoScribeReadonlyWidget = (props: any) => {
  return (
    <ChakraProvider theme={lightTheme}>
      <AutoScribeReadonlyWidget {...props} />
    </ChakraProvider>
  );
}

reportWebVitals();
