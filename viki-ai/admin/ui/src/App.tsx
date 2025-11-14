import { Routes, Route, BrowserRouter } from 'react-router-dom'
import { LoginCallback } from '@okta/okta-react'
import { Box, Flex } from '@chakra-ui/react'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import AppBreadcrumb from './components/Breadcrumb'
import HomePage from './pages/HomePage'
import QuickStartPage from './pages/QuickStartPage'
import QuickStartStep2Page from './pages/QuickStartStep2Page'
import QuickStartStep3Page from './pages/QuickStartStep3Page'
import QuickStartStep4Page from './pages/QuickStartStep4Page'
import AppsPage from './pages/AppsPage'
import AppDetailPage from './pages/AppDetailPage'
import EntitySchemaPage from './pages/EntitySchemaPage'
import PipelinesPage from './pages/PipelinesPage'
import PipelineViewPage from './pages/PipelineViewPage'
import SubjectViewPage from './pages/SubjectViewPage'
import DocumentDetailsPage from './pages/DocumentDetailsPage'
import TestingPage from './pages/TestingPage'
import SettingsPage from './pages/SettingsPage'
import { OktaAuthProvider } from './providers/OktaAuthProvider'
import { UserProfileProvider } from './contexts/UserProfileContext'
import useEnvJson from './hooks/useEnvJson'
import { Env } from './types/env'

function App() {
  const env = useEnvJson<Env>();
  if (env === null) {
    return <div>Loading configuration...</div>;
  }
  return (
    <BrowserRouter>
      <OktaAuthProvider env={env}>
        <Routes>
          <Route path="/login/callback" element={<LoginCallback loadingElement={<div>Loading...</div>} />} />
          <Route path="*" element={<MainLayout />} />
        </Routes>
      </OktaAuthProvider>
    </BrowserRouter>
  )
}

function MainLayout() {
  return (
    <UserProfileProvider>
      <Box h="100vh" bg="var(--wellsky-bg-secondary)" display="flex" flexDirection="column">
        {/* Top Navigation Bar */}
        <Header />

        {/* Main Content Area with Sidebar */}
        <Flex flex="1" overflow="hidden">
          <Sidebar />
          <Box flex="1" p={6} overflow="auto">
            <AppBreadcrumb />
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/quick-start" element={<QuickStartPage />} />
              <Route path="/quick-start/step-2" element={<QuickStartStep2Page />} />
              <Route path="/quick-start/step-3" element={<QuickStartStep3Page />} />
              <Route path="/quick-start/step-4" element={<QuickStartStep4Page />} />
              <Route path="/apps" element={<AppsPage />} />
              <Route path="/apps/:id" element={<AppDetailPage />} />
              <Route path="/apps/:appId/subjects/:subjectId" element={<SubjectViewPage />} />
              <Route path="/apps/:appId/subjects/:subjectId/documents/:documentId" element={<DocumentDetailsPage />} />
              <Route path="/entity-schema" element={<EntitySchemaPage />} />
                <Route path="/pipelines" element={<PipelinesPage />} />
              <Route path="/pipelines/:id" element={<PipelineViewPage />} />
              <Route path="/testing" element={<TestingPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </Box>
        </Flex>
      </Box>
    </UserProfileProvider>
  )
}

export default App