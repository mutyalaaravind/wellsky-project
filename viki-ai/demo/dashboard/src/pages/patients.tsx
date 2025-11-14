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
import { useNavigate } from 'react-router-dom'
import { PatientsList } from '../components/patients-list'
import { Apps } from '../components/apps'
import { HStack } from '@chakra-ui/react'
import { BreadCrumProps, BreadCrumType } from '../components/bread-crum'

const PatientsPage = () => {
  //const router = useRouter()
  const router = useNavigate();
  const currentUser = { username: 'john.doe' }
  const breadCrumbs:Array<BreadCrumType> = [
      {moduleName: 'Patients', linkUrl: '/patients'}
    ]

  return (
    <div >
      <PortalHeader breadCrums={breadCrumbs}/>
      <PatientsList />
    </div>
  )
}

export default PatientsPage