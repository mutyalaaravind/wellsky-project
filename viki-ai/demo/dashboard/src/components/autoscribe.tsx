import React from "react";

import { useScript } from 'usehooks-ts'

const AutoScribeBlock = (props: any) => {
  const autoScribeWidgetEl = React.useRef<HTMLDivElement>(null);
  const status = useScript(`${props.widgetHost}/static/js/bundle.js`, {removeOnUnmount: false});

  React.useEffect(() => {
    if (status === 'ready') {
      return (window as any).initAutoScribeBubble({
        el: props.el ? props.el : autoScribeWidgetEl.current,
        onConfirm: props.onConfirm,
        onCancel: props.onCancel,
        transactionId: props.transactionId,
        sectionId: props.sectionId,
      });
    }
  }, [props.onConfirm, status, props.el]);

  return (
    <div ref={autoScribeWidgetEl} ></div>
  );
}

const AutoScribeFixedBlock = (props: any) => {
  const autoScribeWidgetEl = React.useRef<HTMLDivElement>(null);
  const status = useScript(`${props.widgetHost}/static/js/bundle.js`, {removeOnUnmount: false});

  React.useEffect(() => {
    if (status === 'ready') {
      return (window as any).initAutoScribeWidget({
        el: props.el ? props.el : autoScribeWidgetEl.current,
        onConfirm: props.onConfirm,
        onCancel: props.onCancel,
        transactionId: props.transactionId,
        sectionId: props.sectionId,
      });
    }
  }, [props.onConfirm, status, props.el]);

  return (
    <div ref={autoScribeWidgetEl} ></div>
  );
}

export {AutoScribeFixedBlock, AutoScribeBlock};
