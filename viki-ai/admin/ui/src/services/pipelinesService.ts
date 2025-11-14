// Types based on the PipelineConfig model structure
export interface TaskConfig {
  id: string
  type: 'module' | 'pipeline' | 'prompt' | 'remote' | 'publish_callback'
  module?: {
    type: string
    context?: Record<string, any>
  }
  pipelines?: Array<{
    scope: string
    id: string
    host?: string
    queue?: string
    context?: Record<string, any>
  }>
  prompt?: {
    model: string
    system_instructions?: string[]
    prompt: string
    max_output_tokens?: number
    temperature?: number
    top_p?: number
    safety_settings?: Record<string, any>
    context?: Record<string, any>
    is_add_document_uri_to_context?: boolean
  }
  remote?: {
    url: string
    method: string
    headers?: Record<string, string>
    timeout?: number
    context?: Record<string, any>
  }
  callback?: {
    enabled: boolean
    entity_schema_ref?: {
      schema_uri: string
      var_name: string
    }
    scope?: string
    pipeline_id?: string
    endpoint: {
      method: string
      url: string
      headers?: Record<string, string>
    }
  }
  params?: Record<string, any>
  post_processing?: {
    for_each?: string
  }
  entity_schema_ref?: {
    schema_uri: string
    var_name: string
  }
  invoke?: {
    queue_name?: string
  }
}

export interface Pipeline {
  id: string
  key: string
  version?: string
  name: string
  scope: string
  output_entity?: string
  tasks: TaskConfig[]
  auto_publish_entities_enabled?: boolean
  created_at: string
  updated_at: string
  created_by?: string
  modified_by?: string
  active: boolean
  // Additional fields for UI display
  solution_code?: string
  app_id?: string
  description?: string
}

export interface PipelineCreateRequest {
  key: string
  version?: string
  name: string
  scope?: string
  output_entity?: string
  tasks: TaskConfig[]
  auto_publish_entities_enabled?: boolean
  solution_code?: string
  app_id?: string
  description?: string
}

export interface PipelineUpdateRequest {
  key?: string
  version?: string
  name?: string
  scope?: string
  output_entity?: string
  tasks?: TaskConfig[]
  auto_publish_entities_enabled?: boolean
  solution_code?: string
  app_id?: string
  description?: string
  active?: boolean
}

export interface PipelineResponse {
  success: boolean
  message: string
  data?: Pipeline
}

export interface PipelineListResponse {
  success: boolean
  message: string
  data: Pipeline[]
  total: number
  page: number
  page_size: number
}

export interface PipelineDeleteResponse {
  success: boolean
  message: string
  deleted_id: string
}

import { configService } from './configService'
import { getAuthToken as getAuthTokenUtil } from '../utils/auth'

class PipelinesService {
  private getAuthToken(): string {
    return getAuthTokenUtil() || ''
  }

  private async apiCall<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const apiBaseUrl = await configService.getAdminApiUrl()
    const token = this.getAuthToken()

    const response = await fetch(`${apiBaseUrl}/api/v1/pipelines${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options?.headers,
      },
      ...options,
    })

    if (!response.ok) {
      throw new Error(`API call failed: ${response.statusText}`)
    }

    return response.json()
  }

  async getAllPipelines(filters?: { app_id?: string; labels?: string[] }): Promise<Pipeline[]> {
    try {
      const params = new URLSearchParams()
      
      if (filters?.app_id) {
        params.append('app_id', filters.app_id)
      }
      
      if (filters?.labels && filters.labels.length > 0) {
        filters.labels.forEach(label => {
          params.append('labels', label)
        })
      }

      const endpoint = params.toString() ? `?${params.toString()}` : ''
      const response = await this.apiCall<{ success: boolean; message: string; data: Pipeline[]; total: number }>(endpoint)
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch pipelines')
      }

      return response.data
    } catch (error) {
      console.error('Failed to fetch pipelines from API:', error)
      throw error
    }
  }

  async getPipeline(id: string): Promise<Pipeline> {
    try {
      const response = await this.apiCall<{ success: boolean; message: string; data: Pipeline }>(`/${id}`)
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch pipeline')
      }

      return response.data
    } catch (error) {
      console.error('Failed to fetch pipeline from API:', error)
      throw error
    }
  }

  async createPipeline(pipeline: PipelineCreateRequest): Promise<PipelineResponse> {
    try {
      const response = await this.apiCall<PipelineResponse>('', {
        method: 'POST',
        body: JSON.stringify(pipeline),
      })
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to create pipeline')
      }

      return response
    } catch (error) {
      console.error('Failed to create pipeline:', error)
      throw error
    }
  }

  async updatePipeline(id: string, pipeline: PipelineUpdateRequest): Promise<PipelineResponse> {
    try {
      const response = await this.apiCall<PipelineResponse>(`/${id}`, {
        method: 'PUT',
        body: JSON.stringify(pipeline),
      })
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to update pipeline')
      }

      return response
    } catch (error) {
      console.error('Failed to update pipeline:', error)
      throw error
    }
  }

  async deletePipeline(id: string): Promise<PipelineDeleteResponse> {
    try {
      const response = await this.apiCall<PipelineDeleteResponse>(`/${id}`, {
        method: 'DELETE',
      })
      
      if (!response.success) {
        throw new Error(response.message || 'Failed to delete pipeline')
      }

      return response
    } catch (error) {
      console.error('Failed to delete pipeline:', error)
      throw error
    }
  }

}

export const pipelinesService = new PipelinesService()