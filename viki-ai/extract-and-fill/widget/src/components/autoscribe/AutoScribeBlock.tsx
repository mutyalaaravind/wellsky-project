import React from "react";

import { useScript } from 'usehooks-ts'

export function AutoScribeWidgetBlock(props: any) {
  const autoScribeWidgetEl = React.useRef<HTMLDivElement>(null);
  const status = useScript(`${props.widgetHost}/static/js/bundle.js`, { removeOnUnmount: false });
  // We use reactRoot to keep track of the root element of foreign React app (AutoScribe) and be able to re-render it without nuking it every time
  const reactRoot = React.useRef<any>(null);

  React.useEffect(() => {
    console.log("AutoScribeWidgetBlock:useEffect:status", status, props.widgetHost)
    if (status === 'ready' && props.widgetHost !== undefined) {
      // Render AutoScribe widget. If reactRoot is not null, it means that we have already rendered the widget and we just need to re-render it
      reactRoot.current = (window as any).renderAutoScribeReadonlyWidget({
        reactRoot: reactRoot.current,
        el: autoScribeWidgetEl.current,
        transactionId: props.transactionId,
        sectionId: props.sectionId,
        inlineWidgetEmbedding: props.inlineWidgetEmbedding,
        onConfirm: props.onConfirm,
        evidences: props.evidences,
        verbatimSourceEvidence: props.verbatimSourceEvidence,
      });
    }
  }, [status, props.widgetHost, props.evidences, props.verbatimSourceEvidence, props.transactionId, props.sectionId, props.inlineWidgetEmbedding, props.onConfirm]);

  return (
    <div ref={autoScribeWidgetEl} style={{
      display: 'flex',
      flex: '1 1 0',  // "flex: 1" by default expands to "1 1 0%", but we need specifically 0. Don't ask me why, please. I've spent way too much time on this. CSS is a mess.
      minHeight: 0
    }}></div>
  );
}

function AutoScribeWidgetBubble(props: any) {
  const autoScribeWidgetEl = React.useRef<HTMLDivElement>(null);
  const status = useScript(`${props.widgetHost}/static/js/bundle.js`, { removeOnUnmount: false });
  // We use reactRoot to keep track of the root element of foreign React app (AutoScribe) and be able to re-render it without nuking it every time
  const reactRoot = React.useRef<any>(null);

  React.useEffect(() => {
    console.log("AutoScribeWidgetBubble:useEffect:status", status, props.widgetHost)
    if (status === 'ready' && props.widgetHost !== undefined) {
      // Render AutoScribe widget. If reactRoot is not null, it means that we have already rendered the widget and we just need to re-render it
      reactRoot.current = (window as any).initAutoScribeBubble({
        reactRoot: null,
        el: autoScribeWidgetEl.current,
        transactionId: props.transactionId,
        sectionId: props.sectionId,
        onConfirm: props.onConfirm,
        onCancel: props.onCancel,
      });
    }
  }, [status, props.widgetHost, props.onCancel,props.evidences, props.verbatimSourceEvidence, props.transactionId, props.sectionId, props.inlineWidgetEmbedding, props.onConfirm]);

  return (
    <div ref={autoScribeWidgetEl} style={{
      display: 'flex',
      flex: '1 1 0',  // "flex: 1" by default expands to "1 1 0%", but we need specifically 0. Don't ask me why, please. I've spent way too much time on this. CSS is a mess.
      minHeight: 0
    }}></div>
  );
}

export { AutoScribeWidgetBlock as default,AutoScribeWidgetBubble }
