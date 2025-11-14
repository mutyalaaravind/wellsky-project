import { useState, useEffect, useCallback } from 'react'
import {
  UserProfile,
  UserProfileCreateRequest,
  UserProfileUpdateRequest,
  userProfilesService
} from '../services/userProfilesService'

interface UseUserProfilesResult {
  userProfiles: UserProfile[]
  loading: boolean
  error: string | null
  total: number
  page: number
  pageSize: number
  setPage: (page: number) => void
  createUserProfile: (profile: UserProfileCreateRequest) => Promise<{ success: boolean; error?: string }>
  updateUserProfile: (id: string, profile: UserProfileUpdateRequest) => Promise<{ success: boolean; error?: string }>
  deleteUserProfile: (id: string) => Promise<{ success: boolean; error?: string }>
  refreshUserProfiles: () => Promise<void>
  getUserProfile: (id: string) => Promise<UserProfile | null>
  searchUserProfiles: (searchTerm: string) => Promise<{ success: boolean; data?: UserProfile[]; error?: string }>
  setFilters: (filters: UserProfileFilters) => void
}

export interface UserProfileFilters {
  activeOnly?: boolean
  businessUnit?: string
  solutionCode?: string
  role?: string
}

export const useUserProfiles = (): UseUserProfilesResult => {
  const [userProfiles, setUserProfiles] = useState<UserProfile[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const pageSize = 25
  const [filters, setFilters] = useState<UserProfileFilters>({
    activeOnly: true
  })

  const fetchUserProfiles = async () => {
    try {
      setLoading(true)
      setError(null)
      const offset = (page - 1) * pageSize

      const response = await userProfilesService.getAllUserProfiles(
        filters.activeOnly,
        filters.businessUnit,
        filters.solutionCode,
        filters.role,
        pageSize,
        offset
      )

      if (response.success) {
        setUserProfiles(response.data)
        setTotal(response.total)
      } else {
        setError(response.message || 'Failed to fetch user profiles')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const createUserProfile = async (profile: UserProfileCreateRequest): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await userProfilesService.createUserProfile(profile)
      if (response.success) {
        await fetchUserProfiles() // Refresh the list
        return { success: true }
      } else {
        return { success: false, error: response.message || 'Failed to create user profile' }
      }
    } catch (err) {
      return {
        success: false,
        error: err instanceof Error ? err.message : 'An error occurred'
      }
    }
  }

  const updateUserProfile = async (id: string, profile: UserProfileUpdateRequest): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await userProfilesService.updateUserProfile(id, profile)
      if (response.success) {
        await fetchUserProfiles() // Refresh the list
        return { success: true }
      } else {
        return { success: false, error: response.message || 'Failed to update user profile' }
      }
    } catch (err) {
      return {
        success: false,
        error: err instanceof Error ? err.message : 'An error occurred'
      }
    }
  }

  const deleteUserProfile = async (id: string): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await userProfilesService.deleteUserProfile(id)
      if (response.success) {
        await fetchUserProfiles() // Refresh the list
        return { success: true }
      } else {
        return { success: false, error: response.message || 'Failed to delete user profile' }
      }
    } catch (err) {
      return {
        success: false,
        error: err instanceof Error ? err.message : 'An error occurred'
      }
    }
  }

  const getUserProfile = useCallback(async (id: string): Promise<UserProfile | null> => {
    try {
      const response = await userProfilesService.getUserProfile(id)
      if (response.success && response.data) {
        return response.data.profile
      }
      return null
    } catch (err) {
      return null
    }
  }, [])

  const searchUserProfiles = useCallback(async (searchTerm: string): Promise<{ success: boolean; data?: UserProfile[]; error?: string }> => {
    try {
      const response = await userProfilesService.searchUserProfiles(searchTerm, filters.activeOnly)
      if (response.success) {
        return { success: true, data: response.data }
      } else {
        return { success: false, error: response.message || 'Search failed' }
      }
    } catch (err) {
      return {
        success: false,
        error: err instanceof Error ? err.message : 'An error occurred during search'
      }
    }
  }, [filters.activeOnly])

  const refreshUserProfiles = async () => {
    await fetchUserProfiles()
  }

  const handleSetFilters = useCallback((newFilters: UserProfileFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }))
    setPage(1) // Reset to first page when filters change
  }, [])

  useEffect(() => {
    fetchUserProfiles()
  }, [page, filters])

  return {
    userProfiles,
    loading,
    error,
    total,
    page,
    pageSize,
    setPage,
    createUserProfile,
    updateUserProfile,
    deleteUserProfile,
    refreshUserProfiles,
    getUserProfile,
    searchUserProfiles,
    setFilters: handleSetFilters,
  }
}