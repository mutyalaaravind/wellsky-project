export interface BusinessUnit {
  bu_code: string
  name: string
}

export interface Solution {
  solution_id: string
  code: string
  name: string
  description?: string
  bu_code: string
}

export interface BusinessUnitsResponse {
  success: boolean
  message: string
  data: BusinessUnit[]
}

export interface SolutionsResponse {
  success: boolean
  message: string
  data: Solution[]
}

export interface AllReferenceDataResponse {
  success: boolean
  message: string
  data: {
    business_units: BusinessUnit[]
    solutions: Solution[]
  }
}

import { configService } from './configService'
import { getAuthToken } from '../utils/auth'

class ReferenceService {
  private async apiCall<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const apiBaseUrl = await configService.getAdminApiUrl()
    const token = getAuthToken()

    const response = await fetch(`${apiBaseUrl}/api/v1/reference-lists${endpoint}`, {
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

  async getBusinessUnits(): Promise<BusinessUnitsResponse> {
    try {
      const response = await this.apiCall<BusinessUnitsResponse>('/business-units')
      return response
    } catch (error) {
      console.error('Error fetching business units:', error)
      throw new Error(`Failed to fetch business units: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  async getSolutions(buCode?: string): Promise<SolutionsResponse> {
    try {
      const endpoint = buCode
        ? `/solutions?bu_code=${encodeURIComponent(buCode)}`
        : '/solutions'

      const response = await this.apiCall<SolutionsResponse>(endpoint)
      return response
    } catch (error) {
      console.error('Error fetching solutions:', error)
      throw new Error(`Failed to fetch solutions: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  async getSolutionsByBusinessUnit(buCode: string): Promise<SolutionsResponse> {
    try {
      const response = await this.apiCall<SolutionsResponse>(`/solutions/${encodeURIComponent(buCode)}`)
      return response
    } catch (error) {
      console.error('Error fetching solutions by business unit:', error)
      throw new Error(`Failed to fetch solutions for business unit ${buCode}: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }

  async getAllReferenceData(): Promise<AllReferenceDataResponse> {
    try {
      const response = await this.apiCall<AllReferenceDataResponse>('/all')
      return response
    } catch (error) {
      console.error('Error fetching all reference data:', error)
      throw new Error(`Failed to fetch reference data: ${error instanceof Error ? error.message : 'Unknown error'}`)
    }
  }
}

export const referenceService = new ReferenceService()