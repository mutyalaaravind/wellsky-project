import { useState, useEffect, useCallback } from 'react'
import { 
  App, 
  AppCreateRequest, 
  AppUpdateRequest,
  appsService 
} from '../services/appsService'

interface UseAppsResult {
  apps: App[]
  loading: boolean
  error: string | null
  total: number
  page: number
  pageSize: number
  setPage: (page: number) => void
  createApp: (app: AppCreateRequest) => Promise<{ success: boolean; error?: string }>
  updateApp: (id: string, app: AppUpdateRequest) => Promise<{ success: boolean; error?: string }>
  deleteApp: (id: string) => Promise<{ success: boolean; error?: string }>
  refreshApps: () => Promise<void>
  getApp: (id: string) => Promise<App | null>
}

export const useApps = (): UseAppsResult => {
  const [apps, setApps] = useState<App[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const pageSize = 10

  const fetchApps = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await appsService.getAllApps(page, pageSize)
      
      if (response.success) {
        setApps(response.data)
        setTotal(response.total)
      } else {
        setError('Failed to fetch apps')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const createApp = async (app: AppCreateRequest): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await appsService.createApp(app)
      if (response.success) {
        await fetchApps() // Refresh the list
        return { success: true }
      } else {
        return { success: false, error: 'Failed to create app' }
      }
    } catch (err) {
      return { 
        success: false, 
        error: err instanceof Error ? err.message : 'An error occurred' 
      }
    }
  }

  const updateApp = async (id: string, app: AppUpdateRequest): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await appsService.updateApp(id, app)
      if (response.success) {
        await fetchApps() // Refresh the list
        return { success: true }
      } else {
        return { success: false, error: 'Failed to update app' }
      }
    } catch (err) {
      return { 
        success: false, 
        error: err instanceof Error ? err.message : 'An error occurred' 
      }
    }
  }

  const deleteApp = async (id: string): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await appsService.deleteApp(id)
      if (response.success) {
        await fetchApps() // Refresh the list
        return { success: true }
      } else {
        return { success: false, error: 'Failed to delete app' }
      }
    } catch (err) {
      return { 
        success: false, 
        error: err instanceof Error ? err.message : 'An error occurred' 
      }
    }
  }

  const getApp = useCallback(async (id: string): Promise<App | null> => {
    try {
      const response = await appsService.getApp(id)
      if (response.success && response.data) {
        return response.data
      }
      return null
    } catch (err) {
      return null
    }
  }, [])

  const refreshApps = async () => {
    await fetchApps()
  }

  useEffect(() => {
    fetchApps()
  }, [page])

  return {
    apps,
    loading,
    error,
    total,
    page,
    pageSize,
    setPage,
    createApp,
    updateApp,
    deleteApp,
    refreshApps,
    getApp,
  }
}