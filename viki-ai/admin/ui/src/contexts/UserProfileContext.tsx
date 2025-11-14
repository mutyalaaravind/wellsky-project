import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { UserProfile, Role, userProfilesService } from '../services/userProfilesService'

interface UserProfileContextValue {
  userProfile: UserProfile | null
  resolvedRoles: Role[]
  resolvedPermissions: string[]
  loading: boolean
  error: string | null
  refetchProfile: () => Promise<void>
}

const UserProfileContext = createContext<UserProfileContextValue | undefined>(undefined)

interface UserProfileProviderProps {
  children: ReactNode
}

export const UserProfileProvider: React.FC<UserProfileProviderProps> = ({ children }) => {
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null)
  const [resolvedRoles, setResolvedRoles] = useState<Role[]>([])
  const [resolvedPermissions, setResolvedPermissions] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchProfile = async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await userProfilesService.getMyProfile()

      if (response.success && response.data) {
        setUserProfile(response.data.profile)
        setResolvedRoles(response.data.resolvedRoles || [])
        setResolvedPermissions(response.data.resolvedPermissions || [])
      } else {
        setError(response.message || 'Failed to fetch user profile')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while fetching user profile')
    } finally {
      setLoading(false)
    }
  }

  const refetchProfile = async () => {
    await fetchProfile()
  }

  useEffect(() => {
    fetchProfile()
  }, [])

  const value: UserProfileContextValue = {
    userProfile,
    resolvedRoles,
    resolvedPermissions,
    loading,
    error,
    refetchProfile
  }

  return (
    <UserProfileContext.Provider value={value}>
      {children}
    </UserProfileContext.Provider>
  )
}

export const useUserProfileContext = (): UserProfileContextValue => {
  const context = useContext(UserProfileContext)
  if (!context) {
    throw new Error('useUserProfileContext must be used within a UserProfileProvider')
  }
  return context
}