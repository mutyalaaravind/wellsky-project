import React from "react";

import { useScript } from 'usehooks-ts'

const ExtractAndFillBlock = (props: any) => {
  const extractAndFillEl = React.useRef<HTMLDivElement>(null);
  const status = useScript(`${props.widgetHost}/static/js/bundle.js`, {removeOnUnmount: false});

  React.useEffect(() => {
    if (status === 'ready') {
      console.log("extractAndFillEl", extractAndFillEl.current)
      return (window as any).initExtract({
        el: extractAndFillEl.current,
        transactionId: props.transactionId,
        sectionId: props.sectionId,
        transcriptText: props.transcriptText,
        setApprovedFormFieldValues: props.setApprovedFormFieldValues,
        promptTemplate: props.promptTemplate,
        componentType: props.componentType,
        onCancel: props.onCancel
      });
    }
  }, [props.extractInlineClicked,props.transactionId, props.sectionId,props.transcriptText,status]);

  return (
    <div ref={extractAndFillEl} ></div>
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

export {ExtractAndFillBlock, SectionViewerBlock};