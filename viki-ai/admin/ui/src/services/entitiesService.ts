import { configService } from './configService'
import { getAuthToken } from '../utils/auth'

export interface EntityData {
  id: string
  app_id: string
  tenant_id: string
  patient_id: string
  document_id: string
  source_id?: string
  run_id?: string
  entity_type?: string
  entity_schema_id?: string
  callback_timestamp?: string
  callback_status?: string
  callback_metadata?: Record<string, any>
  created_at: string
  updated_at: string
  // Allow additional fields from the original entity data
  [key: string]: any
}

export interface EntityListResponse {
  success: boolean
  message: string
  data: EntityData[]
  total: number
  pagination: {
    limit: number
    offset: number
    returned: number
    has_more: boolean
  }
}

export interface ListEntitiesParams {
  app_id: string
  subject_id: string
  entity_type?: string
  source_id?: string
  limit?: number
  offset?: number
}

class EntitiesService {
  private async apiCall<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const apiBaseUrl = await configService.getAdminApiUrl()
    const token = getAuthToken()

    const response = await fetch(`${apiBaseUrl}/api/v1/entities${endpoint}`, {
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

  async listEntities(params: ListEntitiesParams): Promise<EntityListResponse> {
    const queryParams = new URLSearchParams()
    queryParams.append('app_id', params.app_id)
    queryParams.append('subject_id', params.subject_id)

    if (params.entity_type) {
      queryParams.append('entity_type', params.entity_type)
    }

    if (params.source_id) {
      queryParams.append('source_id', params.source_id)
    }

    if (params.limit) {
      queryParams.append('limit', params.limit.toString())
    }

    if (params.offset) {
      queryParams.append('offset', params.offset.toString())
    }

    const response = await this.apiCall<EntityListResponse>(`?${queryParams.toString()}`)
    return response
  }
}

export const entitiesService = new EntitiesService()