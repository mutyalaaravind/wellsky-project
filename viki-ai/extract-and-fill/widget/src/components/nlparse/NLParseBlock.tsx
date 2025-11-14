import React from "react";

import { useScript } from 'usehooks-ts'

export function NLParseBlock(props: any) {
  const nlParseWidgetEl = React.useRef<HTMLDivElement>(null);
  const status = useScript(`${props.widgetHost}/static/js/bundle.js`, {removeOnUnmount: false});

  React.useEffect(() => {
    if (status === 'ready') {
      return (window as any).initNLParseWidget({
        el: nlParseWidgetEl.current,
        text: props.text,
      });
    }
  }, [props.onConfirm, status]);

  return (
    <div ref={nlParseWidgetEl} ></div>
  );
}
