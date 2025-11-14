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
import { Assessments } from '../components/assessments-list'
import { Apps } from '../components/apps'
import { Box, HStack } from '@chakra-ui/react'
import { PaperGlassBlock, PaperGlassFrame } from '../components/paperglass'
import useEnvJson from '../hooks/useEnvJson'
import { BreadCrumType } from '../components/bread-crum'

const DocumentsPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const router = useNavigate();
  const currentUser = { username: 'john.doe' }
  const env:any = useEnvJson<Env>();
  const patientId = searchParams.get("patientId");
  const breadCrumbs:Array<BreadCrumType> = [
    {moduleName: 'Patients', linkUrl: '/patients'},
    {moduleName: `getPatientName(${patientId})`, linkUrl: '/'},
    {moduleName: 'Documents', linkUrl: '/documents?patientId='+patientId},
  ]


  return (
    <Box style={{width:"100%" }}>
      <PortalHeader breadCrums={breadCrumbs} />
      {/* {env && <PaperGlassBlock widgetHost={env?.PAPERGLASS_WIDGET_HOST} identifier={patientId}/>} */}
      {env && <Box paddingLeft={5} ><PaperGlassFrame widgetHost={env?.PAPERGLASS_WIDGET_HOST} identifier={patientId}/> </Box>}
    </Box>
  )
}

export default DocumentsPage;