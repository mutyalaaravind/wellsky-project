import { useState, useCallback } from 'react'
import { documentsService, DocumentStatus } from '../services/documentsService'

export const useDocumentStatus = (appId: string, subjectId: string, documentId: string) => {
  const [status, setStatus] = useState<DocumentStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchStatus = useCallback(async () => {
    if (!appId || !subjectId || !documentId) {
      return
    }

    setLoading(true)
    setError(null)

    try {
      const documentStatus = await documentsService.getDocumentStatus(appId, subjectId, documentId)
      setStatus(documentStatus)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch document status'
      console.error('Failed to fetch document status:', err)
      setError(errorMessage)
      // Don't clear existing status on error to avoid flickering
    } finally {
      setLoading(false)
    }
  }, [appId, subjectId, documentId])

  const refreshStatus = useCallback(async () => {
    await fetchStatus()
  }, [fetchStatus])

  return {
    status,
    loading,
    error,
    refreshStatus,
    fetchStatus
  }
}