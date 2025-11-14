import { useState, useEffect } from 'react'
import { 
  Pipeline, 
  PipelineCreateRequest, 
  PipelineUpdateRequest,
  pipelinesService 
} from '../services/pipelinesService'

interface UsePipelinesResult {
  pipelines: Pipeline[]
  loading: boolean
  error: string | null
  total: number
  page: number
  pageSize: number
  setPage: (page: number) => void
  createPipeline: (pipeline: PipelineCreateRequest) => Promise<{ success: boolean; error?: string }>
  updatePipeline: (id: string, pipeline: PipelineUpdateRequest) => Promise<{ success: boolean; error?: string }>
  deletePipeline: (id: string) => Promise<{ success: boolean; error?: string }>
  refreshPipelines: () => Promise<void>
}

export const usePipelines = (): UsePipelinesResult => {
  const [pipelines, setPipelines] = useState<Pipeline[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const pageSize = 10

  const fetchPipelines = async () => {
    try {
      setLoading(true)
      setError(null)
      const pipelinesData = await pipelinesService.getAllPipelines()
      
      setPipelines(pipelinesData)
      setTotal(pipelinesData.length)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const createPipeline = async (pipeline: PipelineCreateRequest): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await pipelinesService.createPipeline(pipeline)
      if (response.success) {
        await fetchPipelines() // Refresh the list
        return { success: true }
      } else {
        return { success: false, error: 'Failed to create pipeline' }
      }
    } catch (err) {
      return { 
        success: false, 
        error: err instanceof Error ? err.message : 'An error occurred' 
      }
    }
  }

  const updatePipeline = async (id: string, pipeline: PipelineUpdateRequest): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await pipelinesService.updatePipeline(id, pipeline)
      if (response.success) {
        await fetchPipelines() // Refresh the list
        return { success: true }
      } else {
        return { success: false, error: 'Failed to update pipeline' }
      }
    } catch (err) {
      return { 
        success: false, 
        error: err instanceof Error ? err.message : 'An error occurred' 
      }
    }
  }

  const deletePipeline = async (id: string): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await pipelinesService.deletePipeline(id)
      if (response.success) {
        await fetchPipelines() // Refresh the list
        return { success: true }
      } else {
        return { success: false, error: 'Failed to delete pipeline' }
      }
    } catch (err) {
      return { 
        success: false, 
        error: err instanceof Error ? err.message : 'An error occurred' 
      }
    }
  }

  const refreshPipelines = async () => {
    await fetchPipelines()
  }

  useEffect(() => {
    fetchPipelines()
  }, [page])

  return {
    pipelines,
    loading,
    error,
    total,
    page,
    pageSize,
    setPage,
    createPipeline,
    updatePipeline,
    deletePipeline,
    refreshPipelines,
  }
}