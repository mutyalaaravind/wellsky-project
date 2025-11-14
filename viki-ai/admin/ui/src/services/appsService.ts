export interface App {
  id: string
  name: string
  description?: string
  business_unit: string
  solution_code: string
  app_id: string
  version: string
  status: 'Active' | 'Inactive'
  created_at: string
  modified_at: string
  created_by?: string
  modified_by?: string
  active: boolean
  pipeline_count: number
  last_deployment?: string
}

export interface AppCreateRequest {
  name: string
  description?: string
  solution_code: string
  app_id: string
  version?: string
}

export interface AppUpdateRequest {
  name?: string
  description?: string
  solution_code?: string
  app_id?: string
  version?: string
  active?: boolean
}

export interface AppResponse {
  success: boolean
  message: string
  data?: App
}

export interface AppListResponse {
  success: boolean
  message: string
  data: App[]
  total: number
  page: number
  page_size: number
}

export interface AppDeleteResponse {
  success: boolean
  message: string
  deleted_id: string
}

// App Config Response from Admin API
export interface AppConfigData {
  id: string
  app_id: string
  name?: string
  description?: string
  config: {
    accounting?: {
      business_unit?: string
      solution_code?: string
    }
    [key: string]: any
  }
  active: boolean
  created_at: string
  modified_at: string
  created_by?: string
  modified_by?: string
}

export interface AppConfigListResponse {
  success: boolean
  message: string
  data: AppConfigData[]
  pagination: {
    limit: number
    offset: number
    returned: number
    has_more: boolean
  }
}

import { configService } from './configService'
import { getAuthToken } from '../utils/auth'

class AppsService {
  private async configApiCall<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const apiBaseUrl = await configService.getAdminApiUrl()
    const token = getAuthToken()
    
    const response = await fetch(`${apiBaseUrl}/api/v1/config${endpoint}`, {
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

  private mapAppConfigToApp(configData: AppConfigData): App {
    const config = configData.config
    const accounting = config.accounting || {}
    
    return {
      id: configData.id,
      name: configData.name || configData.app_id,
      description: configData.description || `Configuration for ${configData.app_id}`,
      business_unit: accounting.business_unit || 'Unknown',
      solution_code: accounting.solution_code || 'Unknown',
      app_id: configData.app_id,
      version: '1.0.0', // Default version
      status: configData.active ? 'Active' : 'Inactive',
      created_at: configData.created_at,
      modified_at: configData.modified_at,
      created_by: configData.created_by,
      modified_by: configData.modified_by,
      active: configData.active,
      pipeline_count: 1, // Default to 1 for configs
      last_deployment: configData.modified_at,
    }
  }

  async getAllApps(page = 1, pageSize = 10): Promise<AppListResponse> {
    // Calculate offset from page number (page is 1-based, offset is 0-based)
    const offset = (page - 1) * pageSize
    
    // Call the new config endpoint to get app configurations
    const configResponse = await this.configApiCall<AppConfigListResponse>(`/apps?limit=${pageSize}&offset=${offset}`)
    
    if (configResponse.success) {
      // Map app configs to App objects
      const apps = configResponse.data.map(config => this.mapAppConfigToApp(config))
      
      return {
        success: true,
        message: configResponse.message,
        data: apps,
        total: offset + configResponse.pagination.returned + (configResponse.pagination.has_more ? 1 : 0), // Estimate total
        page,
        page_size: pageSize
      }
    } else {
      throw new Error(`Failed to fetch app configurations: ${configResponse.message}`)
    }
  }

  async getApp(appId: string): Promise<AppResponse> {
    // Get all apps and find the one with matching app_id
    const configResponse = await this.configApiCall<AppConfigListResponse>('/apps?limit=250')
    
    if (configResponse.success) {
      const appConfig = configResponse.data.find(config => config.app_id === appId)
      
      if (appConfig) {
        const app = this.mapAppConfigToApp(appConfig)
        return {
          success: true,
          message: 'App found',
          data: app
        }
      } else {
        return {
          success: false,
          message: `App not found with app_id: ${appId}`,
          data: undefined
        }
      }
    } else {
      throw new Error(`Failed to fetch apps: ${configResponse.message}`)
    }
  }

  async createApp(_app: AppCreateRequest): Promise<AppResponse> {
    // TODO: Implement app creation via API
    throw new Error('App creation not yet implemented - requires backend API endpoint')
  }

  async updateApp(_id: string, _app: AppUpdateRequest): Promise<AppResponse> {
    // TODO: Implement app update via API 
    throw new Error('App update not yet implemented - requires backend API endpoint')
  }

  async deleteApp(_id: string): Promise<AppDeleteResponse> {
    // TODO: Implement app deletion via API
    throw new Error('App deletion not yet implemented - requires backend API endpoint')
  }

}

export const appsService = new AppsService()