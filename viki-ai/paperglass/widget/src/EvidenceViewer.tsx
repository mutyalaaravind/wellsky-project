import { Spinner } from "@mediwareinc/wellsky-dls-react";
import { FC, useEffect, useState } from "react";
import { PdfViewer } from "./PdfViewer";
import { Env } from "./types";
import useEnvJson from "./hooks/useEnvJson";

export type EvidenceViewerProps = {
  identifier: string;
  substring: string;
};

export const EvidenceViewer: FC<EvidenceViewerProps> = ({ identifier, substring }: EvidenceViewerProps) => {
  const [pdfUrl, setPdfUrl] = useState<string>('');
  const [annotations, setAnnotations] = useState<any[]>([]);
  const [busy, setBusy] = useState<boolean>(false);
  const env = useEnvJson<Env>();

  useEffect(() => {
    // // Fetch the document data from the server
    // if (env == null) {
    //   return;
    // }
    // // Fetch the document data from the server
    // fetch(`${env.API_URL}/api/documents/${identifier}`)
    //   .then((response) => response.json())
    //   .then((data) => {
    //     console.log('Document data:', data);
    //     setDocumentData(data);
    //     setBusyPages(data.pages.map((page: any) => page.number));
    //   })
    //   .catch((error) => {
    //     console.error('Document data error:', error);
    //   });
    // // Fetch document PDF URL
    fetch(`${env?.API_URL}/api/documents/${identifier}/pdf-url`).then(
      (response) => response.json()
    ).then((data) => {
      console.log('PDF URL:', data);
      setPdfUrl(data);
    });
  }, [env, identifier]);

  useEffect(() => {
    // Search evidence of a substring
    setBusy(true);
    fetch(`${env?.API_URL}/api/documents/${identifier}/find-evidence?substring=${substring}`).then(
      (response) => response.json()
    ).then((data) => {
      setAnnotations(data);
      setBusy(false);
    });
  }, [env, identifier, substring]);

  // useEffect(() => {
  //   // Fetch OCR from the server
  //   fetch(`${env.API_URL}/api/documents/${identifier}/ocr`).then((response) => response.json()).then((data) => {
  // }, [env, identifier, substring]);

  if (!pdfUrl) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', padding: '1rem' }}>
        <Spinner size="lg" style={{ marginBottom: '1rem' }} />
        Loading PDF
      </div>
    );
  }

  if (busy) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', padding: '1rem' }}>
        <Spinner size="lg" style={{ marginBottom: '1rem' }} />
        Searching Evidence
      </div>
    );
  }

  return (
    <div style={{ flex: '1 1 0' }}>
      <div style={{ display: 'flex', overflowY: 'scroll', height: "100vh",
              justifyContent: "center",
              alignItems: "flex-start", }}>
        <PdfViewer url={pdfUrl} annotations={annotations} defaultPage={annotations.length > 0 ? annotations[0].page : 1} />
      </div>
    </div>
  );
};
