// Types based on the API contracts
export interface SupportProfile {
  input: string[]
  output: string[]
}

export interface BurndownRateFactors {
  input_text_token: number
  input_image_token: number
  input_video_token: number
  input_audio_token: number
  output_response_text_token: number
  output_reasoning_text_token: number
}

export interface LifecycleProvider {
  available_date: string
  sunset_date: string
}

export interface Lifecycle {
  google?: LifecycleProvider
  wsky?: LifecycleProvider
}

export interface ProvisionedThroughput {
  region: string
  gsus: number
}

export interface LLMModel {
  id: string
  model_id: string
  family: string
  name: string
  version: string
  description: string
  support_profile: SupportProfile
  per_second_throughput_per_gsu: number
  units: string
  minimum_gsu_purchase_increment: number
  burndown_rate_factors: BurndownRateFactors
  knowledge_cutoff_date: string
  lifecycle: Lifecycle
  provisioned_throughput: ProvisionedThroughput[]
  priority: number
  active: boolean
  created_at?: string
  updated_at?: string
  deleted_at?: string
}

export interface LLMModelCreateRequest {
  family: string
  name: string
  model_id: string
  version: string
  description: string
  support_profile: SupportProfile
  per_second_throughput_per_gsu: number
  units?: string
  minimum_gsu_purchase_increment?: number
  burndown_rate_factors: BurndownRateFactors
  knowledge_cutoff_date: string
  lifecycle: Lifecycle
  provisioned_throughput?: ProvisionedThroughput[]
  priority: number
  active?: boolean
}

export interface LLMModelUpdateRequest {
  family?: string
  name?: string
  model_id?: string
  version?: string
  description?: string
  support_profile?: SupportProfile
  per_second_throughput_per_gsu?: number
  units?: string
  minimum_gsu_purchase_increment?: number
  burndown_rate_factors?: BurndownRateFactors
  knowledge_cutoff_date?: string
  lifecycle?: Lifecycle
  provisioned_throughput?: ProvisionedThroughput[]
  priority?: number
  active?: boolean
}

export interface LLMModelResponse {
  success: boolean
  message: string
  data?: LLMModel
}

export interface LLMModelListResponse {
  success: boolean
  message: string
  data: LLMModel[]
  total: number
  page: number
  page_size: number
}

export interface LLMModelDeleteResponse {
  success: boolean
  message: string
  deleted_id: string
}

import { configService } from './configService'
import { getAuthToken as getAuthTokenUtil } from '../utils/auth'

class LLMModelsService {
  private getAuthToken(): string {
    return getAuthTokenUtil() || ''
  }

  private async apiCall<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const apiBaseUrl = await configService.getAdminApiUrl()
    const token = this.getAuthToken()

    const response = await fetch(`${apiBaseUrl}/api/v1/llm-models${endpoint}`, {
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

  async getAllModels(page = 1, pageSize = 10): Promise<LLMModelListResponse> {
    return this.apiCall<LLMModelListResponse>(`?page=${page}&page_size=${pageSize}`)
  }

  async getModel(id: string): Promise<LLMModelResponse> {
    return this.apiCall<LLMModelResponse>(`/${id}`)
  }

  async createModel(model: LLMModelCreateRequest): Promise<LLMModelResponse> {
    return this.apiCall<LLMModelResponse>('', {
      method: 'POST',
      body: JSON.stringify(model),
    })
  }

  async updateModel(id: string, model: LLMModelUpdateRequest): Promise<LLMModelResponse> {
    return this.apiCall<LLMModelResponse>(`/${id}`, {
      method: 'PUT',
      body: JSON.stringify(model),
    })
  }

  async deleteModel(id: string): Promise<LLMModelDeleteResponse> {
    return this.apiCall<LLMModelDeleteResponse>(`/${id}`, {
      method: 'DELETE',
    })
  }

  async searchModels(query?: string, family?: string, active?: boolean, page = 1, pageSize = 10): Promise<LLMModelListResponse> {
    return this.apiCall<LLMModelListResponse>('/search', {
      method: 'POST',
      body: JSON.stringify({
        query,
        family,
        active,
        page,
        page_size: pageSize,
      }),
    })
  }
}

export const llmModelsService = new LLMModelsService()