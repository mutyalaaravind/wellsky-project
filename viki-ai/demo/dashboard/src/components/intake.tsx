import { TextArea } from "@mediwareinc/wellsky-dls-react";
import React from "react";

import { useScript } from 'usehooks-ts'

const IntakeBlock = (props: any) => {
    const intakeEl = React.useRef<HTMLDivElement>(null);
    const status = useScript(`${props.widgetHost}/static/js/bundle.js`, {removeOnUnmount: false});
  
    React.useEffect(() => {
      if (status === 'ready') {
        console.log("intakeEl", intakeEl.current, props.identifier);
        return (window as any).initSearchGlass({
          el: intakeEl.current,
          identifier: props.identifier
        });
      }
    }, [status]);
  
    return (
      <div ref={intakeEl} ></div>
    );
  }


const SectionViewerBlock = (props:any) => {
  
  const extractAndFillEl = React.useRef<HTMLDivElement>(null);
  const status = useScript(`${props.widgetHost}/static/js/bundle.js`, {removeOnUnmount: false});

  React.useEffect(() => {
    if (status === 'ready') {
      console.log("extractAndFillEl", extractAndFillEl.current)
      return (window as any).initSectionViewer({
        el: extractAndFillEl.current,
        transactionId: props.transactionId,
        sectionsSchema: props.sectionsSchema
      });
    }
  }, [props.transactionId,props.sectionsSchema,status]);

  return (
    <div ref={extractAndFillEl} ></div>
  );
}

export {IntakeBlock, SectionViewerBlock};