import { useCallback, useState } from 'react'
import Head from 'next/head'
import type { NextPageWithLayout } from '../_app'
import { PortalHeader } from '../components/portal-header'
import { HomeScreenTemplate } from '@mediwareinc/wellsky-dls-react'
import {
  ClipboardText,
  DocumentText,
  Email,
} from '@mediwareinc/wellsky-dls-react-icons'
// import { useRouter } from 'next/router'
import { Env } from '../types'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { PatientsList } from '../components/patients-list'
import { Apps } from '../components/apps'
import { Box, HStack } from '@chakra-ui/react'
import { SectionViewerBlock } from '../components/extract'
import { schema } from '../assets/hhh/schema'
import useEnvJson from '../hooks/useEnvJson'
import { BreadCrumType } from '../components/bread-crum'

const AssessmentPage = () => {
  //const router = useRouter()
  const [searchParams, setSearchParams] = useSearchParams();
  const router = useNavigate();
  const currentUser = { username: 'john.doe' }
  const env:Env | null = useEnvJson();
  const patientId = searchParams.get("patientId");
  const breadCrumbs:Array<BreadCrumType> = [
    {moduleName: 'Patients', linkUrl: '/patients'},
    {moduleName: `getPatientName(${patientId})`, linkUrl: '/'},
    {moduleName: 'Assessment', linkUrl: `/assessments?patientId=${patientId}`}
  ]


  return (
    <Box style={{"width":"100%"}}>
      <PortalHeader breadCrums={breadCrumbs} />
      {env && <Box  paddingLeft={5}><SectionViewerBlock widgetHost={env?.EXTRACT_WIDGET_HOST} transactionId={patientId} sectionsSchema={schema} /></Box>}
      {!env && <div>Loading...</div>}
    </Box>
  )
}

export default AssessmentPage