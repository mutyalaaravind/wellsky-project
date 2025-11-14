import { useState, useEffect, useCallback, useRef } from 'react'
import { configService } from '../services/configService'
import { getAuthToken as getAuthTokenUtil } from '../utils/auth'

export interface OnboardTask {
  id: string
  name: string
  description: string
  status: 'NOT_STARTED' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED'
  progress_percentage: number
}

export interface OnboardProgress {
  job_id: string
  app_id: string
  status: 'NOT_STARTED' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED' | 'CANCELLED'
  current_task?: string
  current_task_name?: string
  overall_progress_percentage: number
  tasks: OnboardTask[]
  created_at: string
  updated_at: string
  error_message?: string
}

interface UseOnboardProgressOptions {
  jobId: string | null
  enabled?: boolean
  pollingInterval?: number
  onComplete?: (progress: OnboardProgress) => void
  onError?: (error: string) => void
}

interface UseOnboardProgressReturn {
  progress: OnboardProgress | null
  isLoading: boolean
  error: string | null
  startPolling: () => void
  stopPolling: () => void
  cancelJob: () => Promise<void>
  retry: () => void
}

export const useOnboardProgress = ({
  jobId,
  enabled = true,
  pollingInterval = 2000, // Poll every 2 seconds
  onComplete,
  onError
}: UseOnboardProgressOptions): UseOnboardProgressReturn => {
  const [progress, setProgress] = useState<OnboardProgress | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [_isPolling, setIsPolling] = useState(false)
  
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const abortControllerRef = useRef<AbortController | null>(null)
  
  // Use refs to store callbacks to avoid dependency issues
  const onCompleteRef = useRef(onComplete)
  const onErrorRef = useRef(onError)
  
  // Create stable refs for functions to avoid dependency issues
  const startPollingRef = useRef<() => void>()
  const stopPollingRef = useRef<() => void>()
  
  // Update refs when callbacks change
  onCompleteRef.current = onComplete
  onErrorRef.current = onError

  const getAuthToken = useCallback((): string => {
    return getAuthTokenUtil() || ''
  }, [])

  const fetchProgress = useCallback(async (signal?: AbortSignal): Promise<OnboardProgress | null> => {
    if (!jobId) return null

    try {
      const adminApiUrl = await configService.getAdminApiUrl()
      const token = getAuthToken()
      
      const response = await fetch(`${adminApiUrl}/api/v1/onboard/progress/${jobId}`, {
        signal,
        headers: {
          ...(token && { 'Authorization': `Bearer ${token}` })
        }
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || `HTTP ${response.status}: Failed to fetch progress`)
      }

      const progressData: OnboardProgress = await response.json()
      return progressData
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        return null // Request was cancelled, don't treat as error
      }
      throw err
    }
  }, [jobId, getAuthToken])

  const startPolling = useCallback(() => {
    if (!jobId) return

    setIsPolling(true)
    setError(null)

    const poll = async () => {
      try {
        setIsLoading(true)
        
        // Create new abort controller for this polling cycle
        abortControllerRef.current = new AbortController()
        
        const progressData = await fetchProgress(abortControllerRef.current.signal)
        
        if (progressData) {
          setProgress(progressData)
          
          // Check if job is complete or failed
          if (progressData.status === 'COMPLETED') {
            stopPolling()
            onCompleteRef.current?.(progressData)
          } else if (progressData.status === 'FAILED') {
            stopPolling()
            const errorMsg = progressData.error_message || 'Job failed'
            setError(errorMsg)
            onErrorRef.current?.(errorMsg)
          } else if (progressData.status === 'CANCELLED') {
            stopPolling()
            setError('Job was cancelled')
          }
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to fetch progress'
        setError(errorMessage)
        onErrorRef.current?.(errorMessage)
        stopPolling()
      } finally {
        setIsLoading(false)
      }
    }

    // Start immediate fetch
    poll()

    // Set up polling interval
    intervalRef.current = setInterval(poll, pollingInterval)
  }, [jobId, pollingInterval, fetchProgress])

  const stopPolling = useCallback(() => {
    setIsPolling(false)
    
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
    
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
    }
  }, [])

  const cancelJob = useCallback(async (): Promise<void> => {
    if (!jobId) return

    try {
      const adminApiUrl = await configService.getAdminApiUrl()
      const token = getAuthToken()
      
      const response = await fetch(`${adminApiUrl}/api/v1/onboard/cancel/${jobId}`, {
        method: 'POST',
        headers: {
          ...(token && { 'Authorization': `Bearer ${token}` })
        }
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to cancel job')
      }

      // Stop polling after successful cancellation
      stopPolling()
      setError('Job cancelled by user')
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to cancel job'
      setError(errorMessage)
      throw new Error(errorMessage)
    }
  }, [jobId, stopPolling, getAuthToken])

  const retry = useCallback(() => {
    setError(null)
    setProgress(null)
    if (jobId && enabled) {
      startPollingRef.current?.()
    }
  }, [jobId, enabled])

  // Update the refs whenever functions change
  startPollingRef.current = startPolling
  stopPollingRef.current = stopPolling

  // Auto-start polling when enabled and jobId is available
  useEffect(() => {
    if (enabled && jobId) {
      // Always start polling when we get a valid jobId, regardless of current polling state
      startPolling()
    } else if (!enabled || !jobId) {
      stopPolling()
    }
    
    return () => {
      stopPolling()
    }
  }, [enabled, jobId, startPolling, stopPolling])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopPollingRef.current?.()
    }
  }, [])

  return {
    progress,
    isLoading,
    error,
    startPolling,
    stopPolling,
    cancelJob,
    retry
  }
}