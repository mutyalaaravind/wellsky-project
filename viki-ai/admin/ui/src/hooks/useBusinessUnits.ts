import { useState, useEffect, useCallback } from 'react'
import { referenceService, BusinessUnit } from '../services/referenceService'

interface UseBusinessUnitsResult {
  businessUnits: BusinessUnit[]
  loading: boolean
  error: string | null
  refetch: () => Promise<void>
}

export const useBusinessUnits = (): UseBusinessUnitsResult => {
  const [businessUnits, setBusinessUnits] = useState<BusinessUnit[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchBusinessUnits = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await referenceService.getBusinessUnits()

      if (response.success) {
        setBusinessUnits(response.data)
      } else {
        setError(response.message || 'Failed to fetch business units')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred')
      console.error('Error fetching business units:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchBusinessUnits()
  }, [fetchBusinessUnits])

  const refetch = useCallback(async () => {
    await fetchBusinessUnits()
  }, [fetchBusinessUnits])

  return {
    businessUnits,
    loading,
    error,
    refetch
  }
}