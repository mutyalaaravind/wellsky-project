import { useCallback, useState } from 'react'
import Head from 'next/head'
import type { NextPageWithLayout } from './_app'
import { PortalHeader } from './components/portal-header'
import { HomeScreenTemplate } from '@mediwareinc/wellsky-dls-react'
import {
  ClipboardText,
  DocumentText,
  Email,
} from '@mediwareinc/wellsky-dls-react-icons'
// import { useRouter } from 'next/router'
import { Env } from './types'
import { useNavigate } from 'react-router-dom'
import { Apps } from './components/apps'
import { HStack } from '@chakra-ui/react'
import { BreadCrumType } from './components/bread-crum'

const Home = () => {
  //const router = useRouter()
  const router = useNavigate();
  const currentUser = { username: 'john.doe' }
  const breadCrumbs:Array<BreadCrumType> = [
    {moduleName: 'Home', linkUrl: '/'}
  ]

  return (
    <div style={{"width":"100%"}} >
      <PortalHeader  breadCrums={breadCrumbs} />
      <HStack w={"100%"} h={"100%"} alignContent={"center"} padding={100} spacing={10}>
          <Apps />
      </HStack>
    </div>
  )
}

export default Home