import { useState, useEffect, useCallback } from 'react'
import { referenceService, Solution } from '../services/referenceService'

interface UseSolutionsResult {
  solutions: Solution[]
  loading: boolean
  error: string | null
  refetch: (buCode?: string) => Promise<void>
}

export const useSolutions = (buCode?: string): UseSolutionsResult => {
  const [solutions, setSolutions] = useState<Solution[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchSolutions = useCallback(async (businessUnitCode?: string) => {
    try {
      setLoading(true)
      setError(null)

      const response = await referenceService.getSolutions(businessUnitCode)

      if (response.success) {
        setSolutions(response.data)
      } else {
        setError(response.message || 'Failed to fetch solutions')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred')
      console.error('Error fetching solutions:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchSolutions(buCode)
  }, [fetchSolutions, buCode])

  const refetch = useCallback(async (businessUnitCode?: string) => {
    await fetchSolutions(businessUnitCode || buCode)
  }, [fetchSolutions, buCode])

  return {
    solutions,
    loading,
    error,
    refetch
  }
}