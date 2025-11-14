import { useOktaAuth } from "@okta/okta-react";
import React from "react";

import { useScript } from "usehooks-ts";

const PaperGlassBlock = (props: any) => {
  const extractAndFillEl = React.useRef<HTMLDivElement>(null);
  const status = useScript(`${props.widgetHost}/static/js/bundle.js`, {
    removeOnUnmount: false,
  });

  React.useEffect(() => {
    if (status === "ready") {
      console.log(
        "PaperGlassBlockEl",
        extractAndFillEl.current,
        props.identifier,
      );
      return (window as any).initSearchGlass({
        el: extractAndFillEl.current,
        identifier: props.identifier,
      });
    }
  }, [status]);

  return <div ref={extractAndFillEl}></div>;
};

const PaperGlassFrame = (props: any) => {
  // ToDo: get the token from server
  const jwtToken = btoa(
    JSON.stringify({
      patientId: props.identifier,
      tenantId: "54321",
      appId: "007",
      role: "patient",
    }),
  );
  const url = `${props.widgetHost}?token=${jwtToken}`;
  const [busy, setBusy] = React.useState<boolean>(true);
  const handleIfrmeLoad = () => {
    console.log("iframe loaded");
    setBusy(false);
  };
  return (
    <>
      {
        <iframe
          onLoad={handleIfrmeLoad}
          title={"paperglass"}
          src={url}
          style={{ width: "100%", height: "850px" }}
        ></iframe>
      }
      {busy && <div>Loading...</div>}
    </>
  );
};

const MedWidgetBlock = (props: any) => {
  const MedWidgetBlockEl = React.useRef<HTMLDivElement>(null);
  const status = useScript(`${props.widgetHost}/static/js/bundle.js`, {
    removeOnUnmount: false,
  });
  const { oktaAuth, authState } = useOktaAuth();
  const { token, ehrToken, oktaToken } = props.tokens;

  React.useEffect(() => {
    if (status === "ready" && props.identifier) {
      console.log(
        "MedWidgetBlockEl",
        MedWidgetBlockEl.current,
        props,
        authState,
      );
      // const jwtToken = btoa(JSON.stringify({
      //   "patientId": props.identifier,
      //   "tenantId": props.patient?.tenantId || "54321",
      //   "appId": props.patient?.appId || "007",
      //   "role": "patient",
      //   "userId": authState?.idToken?.claims.email || authState?.idToken?.claims.sub || "12345",
      // }));
      const widget = (window as any).initMedWidgetButton({
        el: MedWidgetBlockEl.current,
        token: token,
        ehrToken: ehrToken,
        oktaToken: oktaToken,
        options: {
          enableUpload: true,
          emptyMedicationListMessage:
            "Select a document to extract medications.",
          emptyDocumentListMessage:
            "Upload relevant documents in Episode Manager or directly in the medication profile.",
        },
      });

      return () => {
        widget?.unmount?.();
      };
    }
  }, [status]);

  return <div ref={MedWidgetBlockEl} id={props.identifier}></div>;
};

export { PaperGlassBlock, PaperGlassFrame, MedWidgetBlock };
