import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'

export interface SignupState {
  currentAuthStep:
    | 'PERSONAL_INFORMATION'
    | 'ACCOUNT_INFORMATION'
    | 'TERMS_OF_SERVICE'
    | 'ACCOUNT_CREATED'
  error: any
  loading: boolean
  campaignDetails: any
  personalInformation?: {
    firstName?: string
    lastName?: string
    dob?: string
    medicareId?: string
    inviteCode?: string
  } | null
  accountInformation?: {
    userName?: string
    email?: string
    password?: string
    phoneNumber?: string
  } | null
  patientDetails?: any
  isValidCampaign?: boolean | null
  resetStore: () => void
  setLoading: (loading: boolean) => void
  setError: (error: any) => void
  setCampaignDetails: (data: any) => void
  setCurrentAuthStep: (authStep: SignupState['currentAuthStep']) => void
  setPersonalInformation: (data: SignupState['personalInformation']) => void
  setAccountInformation: (data: SignupState['accountInformation']) => void
  setPatientDetails: (data: any) => void
  setIsValidCampaign: (data: boolean) => void
}

export const useSignupStore = create<
  SignupState,
  [['zustand/devtools', never], ['zustand/immer', never]]
>(
  devtools(
    immer(
      (set, get): SignupState => ({
        currentAuthStep: 'PERSONAL_INFORMATION',
        loading: false,
        campaignDetails: null,
        personalInformation: null,
        accountInformation: null,
        error: null,
        patientDetails: null,
        isValidCampaign: null,
        resetStore: () => {
          set((state) => {
            state.currentAuthStep = 'PERSONAL_INFORMATION'
            state.loading = false
            state.campaignDetails = null
            state.personalInformation = null
            state.accountInformation = null
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
        setCampaignDetails: (data) => {
          set((state) => {
            state.campaignDetails = data
          })
        },
        setPersonalInformation: (data) => {
          set((state) => {
            state.personalInformation = data
          })
        },
        setCurrentAuthStep: (authStep) => {
          set((state) => {
            state.currentAuthStep = authStep
          })
        },
        setAccountInformation: (data) => {
          set((state) => {
            state.accountInformation = data
          })
        },
        setPatientDetails: (data) => {
          set((state) => {
            state.patientDetails = data
          })
        },
        setIsValidCampaign: (data) => {
          set((state) => {
            state.isValidCampaign = data
          })
        },
      }),
    ),
  ),
)
