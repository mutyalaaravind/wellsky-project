import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'

export interface AuthenticationState {
  loading: boolean
  user: any
  error: any
  getOrganizationId: () => string
  getPatientId: () => string
  getCustomFormsToken: () => string
  setData: (user: any, error?: any) => void
  resetStore: () => void
  setLoading: (loading: boolean) => void
  setError: (error: any) => void
}

export const useAuthStore = create<
  AuthenticationState,
  [
    ['zustand/devtools', never],
    ['zustand/persist', unknown],
    ['zustand/immer', never]
  ]
>(
  devtools(
    persist(
      immer(
        (set, get): AuthenticationState => ({
          loading: false,
          user: null,
          error: null,
          setData: (user, error = null) => {
            set((state) => {
              state.user = user
              state.loading = Boolean(user?.loading)
              state.error = error
            })
          },
          getOrganizationId: () => {
            return get()?.user?.metaData?.viewer?.careCordinationMember
              ?.organizationId as string
          },
          getPatientId: () => {
            return get()?.user?.metaData?.viewer?.careCordinationMember
              ?.id as string
          },
          getCustomFormsToken: () => {
            return get()?.user?.metaData?.viewer?.careCordinationMember
              ?.customFormToken?.token as string
          },
          resetStore: () => {
            set((state) => {
              state.loading = false
              state.user = null
              state.error = null
            })
          },
          setLoading: (loading) => {
            set((state) => {
              state.loading = loading
            })
          },
          setError: (error) => {
            set((state) => {
              state.error = error
            })
          },
        })
      ),
      {
        name: 'MAPauthData',
      }
    )
  )
)
