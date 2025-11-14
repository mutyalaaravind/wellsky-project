import { useState, useEffect, useCallback } from 'react'
import { 
  loggingService, 
  LogEntry, 
  LogSearchParams, 
  LogConfiguration,
  LogAnalytics
} from '../services/loggingService'

export const useLogs = (appId: string) => {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [totalCount, setTotalCount] = useState(0)
  const [hasMore, setHasMore] = useState(false)
  const [nextPageToken, setNextPageToken] = useState<string | undefined>()

  const searchLogs = useCallback(async (params: Omit<LogSearchParams, 'app_id'>) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await loggingService.searchLogs({ ...params, app_id: appId })
      setLogs(response.entries)
      setTotalCount(response.total_count)
      setHasMore(response.has_more)
      setNextPageToken(response.next_page_token)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to search logs')
    } finally {
      setLoading(false)
    }
  }, [appId])

  const refreshLogs = useCallback(async () => {
    await searchLogs({})
  }, [searchLogs])

  // Load initial logs
  useEffect(() => {
    refreshLogs()
  }, [refreshLogs])

  return {
    logs,
    loading,
    error,
    totalCount,
    hasMore,
    nextPageToken,
    searchLogs,
    refreshLogs
  }
}

export const useLogConfiguration = (appId: string) => {
  const [config, setConfig] = useState<LogConfiguration | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadConfiguration = useCallback(async () => {
    setLoading(true)
    setError(null)
    
    try {
      const configuration = await loggingService.getLogConfiguration(appId)
      setConfig(configuration)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load log configuration')
    } finally {
      setLoading(false)
    }
  }, [appId])

  const updateConfiguration = useCallback(async (newConfig: LogConfiguration) => {
    setLoading(true)
    setError(null)
    
    try {
      await loggingService.updateLogConfiguration(appId, newConfig)
      setConfig(newConfig)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update log configuration')
    } finally {
      setLoading(false)
    }
  }, [appId])

  useEffect(() => {
    loadConfiguration()
  }, [loadConfiguration])

  return {
    config,
    loading,
    error,
    updateConfiguration,
    refreshConfiguration: loadConfiguration
  }
}

export const useLogAnalytics = (appId: string) => {
  const [analytics, setAnalytics] = useState<LogAnalytics | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadAnalytics = useCallback(async () => {
    setLoading(true)
    setError(null)
    
    try {
      const analyticsData = await loggingService.getLogAnalytics(appId)
      setAnalytics(analyticsData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load log analytics')
    } finally {
      setLoading(false)
    }
  }, [appId])

  useEffect(() => {
    loadAnalytics()
  }, [loadAnalytics])

  return {
    analytics,
    loading,
    error,
    refreshAnalytics: loadAnalytics
  }
}