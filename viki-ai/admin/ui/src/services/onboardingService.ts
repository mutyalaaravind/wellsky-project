import { configService } from './configService'
import { getAuthToken as getAuthTokenUtil } from '../utils/auth'

// Request interfaces for onboarding API
export interface OnboardSaveRequest {
  app_id: string
  business_unit: string
  solution_code: string
  app_name?: string
  app_description?: string
  entity_schema?: object
  extraction_prompt?: string
  pipeline_template?: string
}

export interface OnboardSaveResponse {
  success: boolean
  message: string
  app_id: string
  config_created: boolean
}

export interface OnboardProgressResponse {
  job_id: string
  app_id: string
  status: string
  current_task?: string
  current_task_name?: string
  overall_progress_percentage: number
  tasks: Array<{
    id: string
    name: string
    description: string
    status: string
    progress_percentage: number
  }>
  created_at: string
  updated_at: string
  error_message?: string
}

class OnboardingService {
  private getAuthToken(): string {
    return getAuthTokenUtil() || ''
  }

  private async apiCall<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const apiBaseUrl = await configService.getAdminApiUrl()
    const token = this.getAuthToken()
    
    const response = await fetch(`${apiBaseUrl}/api/v1/onboard${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options?.headers,
      },
      ...options,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  /**
   * Save the onboarding configuration and create the app config
   * @param request The onboarding save request data
   * @returns Promise with the save response
   */
  async saveOnboardingConfig(request: OnboardSaveRequest): Promise<OnboardSaveResponse> {
    try {
      console.log('Saving onboarding config:', request)
      return await this.apiCall<OnboardSaveResponse>('/save', {
        method: 'POST',
        body: JSON.stringify(request),
      })
    } catch (error) {
      console.error('Error saving onboarding config:', error)
      throw error
    }
  }

  /**
   * Get the progress of an onboarding job
   * @param jobId The job ID to check progress for
   * @returns Promise with the progress response
   */
  async getOnboardingProgress(jobId: string): Promise<OnboardProgressResponse> {
    try {
      return await this.apiCall<OnboardProgressResponse>(`/progress/${jobId}`)
    } catch (error) {
      console.error('Error getting onboarding progress:', error)
      throw error
    }
  }

  /**
   * Cancel an onboarding job
   * @param jobId The job ID to cancel
   * @returns Promise with cancellation result
   */
  async cancelOnboardingJob(jobId: string): Promise<{ success: boolean; message: string; job_id: string }> {
    try {
      return await this.apiCall<{ success: boolean; message: string; job_id: string }>(`/cancel/${jobId}`, {
        method: 'POST',
      })
    } catch (error) {
      console.error('Error cancelling onboarding job:', error)
      throw error
    }
  }
}

export const onboardingService = new OnboardingService()