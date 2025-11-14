import { useState, useEffect, useCallback } from 'react'
import { referenceService, BusinessUnit, Solution } from '../services/referenceService'

interface UseReferenceDataResult {
  businessUnits: BusinessUnit[]
  solutions: Solution[]
  loading: boolean
  error: string | null
  refetch: () => Promise<void>
  getSolutionsForBusinessUnit: (buCode: string) => Solution[]
}

export const useReferenceData = (): UseReferenceDataResult => {
  const [businessUnits, setBusinessUnits] = useState<BusinessUnit[]>([])
  const [solutions, setSolutions] = useState<Solution[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchReferenceData = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await referenceService.getAllReferenceData()

      if (response.success) {
        setBusinessUnits(response.data.business_units)
        setSolutions(response.data.solutions)
      } else {
        setError(response.message || 'Failed to fetch reference data')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred')
      console.error('Error fetching reference data:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchReferenceData()
  }, [fetchReferenceData])

  const refetch = useCallback(async () => {
    await fetchReferenceData()
  }, [fetchReferenceData])

  const getSolutionsForBusinessUnit = useCallback((buCode: string): Solution[] => {
    return solutions.filter(solution => solution.bu_code === buCode)
  }, [solutions])

  return {
    businessUnits,
    solutions,
    loading,
    error,
    refetch,
    getSolutionsForBusinessUnit
  }
}