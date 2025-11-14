import { LoginCallback } from '@okta/okta-react';
import { Routes, Route, BrowserRouter } from 'react-router-dom';
import { OktaAuthProvider } from './providers/auth';
import LegacyHome from './legacyHome';
import Home from './home';
import useEnvJson from './hooks/useEnvJson';
import { Env } from './types';
import PatientsPage from './pages/patients';
import AssessmentsPage from './pages/assessments';
import AssessmentPage from './pages/assessment';
import DocumentsPage from './pages/documents';
import IntakePage from './pages/intake';
import { GlobalWorkerOptions, getDocument, PDFDocumentProxy, PDFPageProxy } from "pdfjs-dist";
import { RenderParameters } from 'pdfjs-dist/types/src/display/api';
import * as pdfjsLib from 'pdfjs-dist/webpack'
import MedicationsPage from './pages/medications';


const App = () => {
  const env = useEnvJson<Env>();
  if (env === null) {
    return <div>Loading configuration...</div>;
  }
  return (
    <BrowserRouter>
      <OktaAuthProvider env={env}>
        <Routes>
          <Route path="/login/callback" element={<LoginCallback loadingElement={<div>Loading...</div>} />} />
          <Route path="/" element={<PatientsPage />} />
          <Route path="/patients" element={<PatientsPage />} />
          {/* <Route path="/assessments" element={<AssessmentsPage />} /> */}
          <Route path="/assessments" element={<AssessmentPage />} />
          <Route path="/documents" element={<DocumentsPage />} />
          <Route path="/intake" element={<IntakePage />} />
          <Route path="/medications" element={<MedicationsPage />} />
        </Routes>
      </OktaAuthProvider>
    </BrowserRouter>
  );
};

export default App;
