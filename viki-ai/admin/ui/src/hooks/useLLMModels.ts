import { useState, useEffect, useCallback } from 'react'
import { llmModelsService, LLMModel, LLMModelCreateRequest, LLMModelUpdateRequest } from '../services/llmModelsService'

export const useLLMModels = () => {
  const [models, setModels] = useState<LLMModel[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)

  const fetchModels = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await llmModelsService.getAllModels(page, pageSize)
      setModels(response.data)
      setTotal(response.total)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch models')
    } finally {
      setLoading(false)
    }
  }, [page, pageSize])

  const createModel = useCallback(async (model: LLMModelCreateRequest) => {
    try {
      setError(null)
      await llmModelsService.createModel(model)
      await fetchModels()
      return { success: true }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create model'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    }
  }, [fetchModels])

  const updateModel = useCallback(async (id: string, model: LLMModelUpdateRequest) => {
    try {
      setError(null)
      await llmModelsService.updateModel(id, model)
      await fetchModels()
      return { success: true }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update model'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    }
  }, [fetchModels])

  const deleteModel = useCallback(async (id: string) => {
    try {
      setError(null)
      await llmModelsService.deleteModel(id)
      await fetchModels()
      return { success: true }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete model'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    }
  }, [fetchModels])

  useEffect(() => {
    fetchModels()
  }, [fetchModels])

  return {
    models,
    loading,
    error,
    total,
    page,
    pageSize,
    setPage,
    setPageSize,
    fetchModels,
    createModel,
    updateModel,
    deleteModel,
  }
}