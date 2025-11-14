import '@fontsource/roboto/300.css'
import '@fontsource/roboto/400.css'
import '@fontsource/roboto/500.css'
import {
  PropsWithChildren,
  ReactElement,
  ReactNode,
  useCallback,
  useEffect,
  useState,
} from 'react'
import type { NextPage } from 'next'
import type { AppProps } from 'next/app'
import { ChakraProvider } from '@chakra-ui/react'
import { lightTheme } from '@mediwareinc/wellsky-dls-react'

//configureLogin()

export type NextPageWithLayout<P = PropsWithChildren, IP = P> = NextPage<
  P,
  IP
> & {
  getLayout?: (page: ReactElement) => ReactNode
}

type AppPropsWithLayout = AppProps & {
  Component: NextPageWithLayout
}

export default function App({ Component, pageProps }: AppPropsWithLayout) {
  // Use the layout defined at the page level, if available
  const [rendered, setIsrendered] = useState(false)

  useEffect(() => {
    setIsrendered(true)
  }, [])

  // const defaultGetLayout = useCallback(
  //   (page: ReactElement): ReactNode => <AuthLayout>{page}</AuthLayout>,
  //   [],
  // )

  const defaultGetLayout = useCallback(
    (page: ReactElement): ReactNode => <div>{page}</div>,
    [],
  )

  const getLayout = Component.getLayout ?? defaultGetLayout

  return (
    <>
      {/* <SEO title='WellSky Member Access Portal' /> */}
      {rendered && (
        <ChakraProvider theme={lightTheme}>
          {getLayout(<Component {...pageProps} />)}
        </ChakraProvider>
      )}
    </>
  )
}
