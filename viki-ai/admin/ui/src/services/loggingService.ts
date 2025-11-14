import { configService } from './configService'
import { getAuthToken as getAuthTokenUtil } from '../utils/auth'

export interface LogEntry {
  timestamp: string
  level: string
  message: string
  source: string
  app_id?: string
  pipeline_id?: string
  metadata: Record<string, any>
}

export interface LogSearchParams {
  app_id: string
  start_time?: string
  end_time?: string
  level?: string
  limit?: number
  query?: string
}

export interface LogSearchResponse {
  entries: LogEntry[]
  total_count: number
  has_more: boolean
  next_page_token?: string
}

export interface LogConfiguration {
  app_id: string
  log_level: string
  retention_days: number
  format: string
  storage_location: string
  enabled: boolean
}

export interface LogAnalytics {
  app_id: string
  total_entries_today: number
  error_count_24h: number
  warning_count_24h: number
  error_rate_24h: number
  storage_size_mb: number
}


class LoggingService {
  
  private getAuthToken(): string {
    return getAuthTokenUtil() || ''
  }

  async searchLogs(params: LogSearchParams): Promise<LogSearchResponse> {
    const searchParams = new URLSearchParams()
    
    if (params.start_time) searchParams.append('start_time', params.start_time)
    if (params.end_time) searchParams.append('end_time', params.end_time)
    if (params.level) searchParams.append('level', params.level)
    if (params.limit) searchParams.append('limit', params.limit.toString())
    if (params.query) searchParams.append('query', params.query)
    
    const apiBaseUrl = await configService.getAdminApiUrl()
    const token = this.getAuthToken()
    
    const response = await fetch(
      `${apiBaseUrl}/api/v1/logs/apps/${params.app_id}/logs?${searchParams.toString()}`,
      {
        headers: {
          ...(token && { 'Authorization': `Bearer ${token}` })
        }
      }
    )
    
    if (!response.ok) {
      throw new Error(`Failed to search logs: ${response.statusText}`)
    }
    
    return response.json()
  }
  
  async getLogConfiguration(appId: string): Promise<LogConfiguration> {
    const apiBaseUrl = await configService.getAdminApiUrl()
    const token = this.getAuthToken()
    
    const response = await fetch(`${apiBaseUrl}/api/v1/logs/apps/${appId}/logs/config`, {
      headers: {
        ...(token && { 'Authorization': `Bearer ${token}` })
      }
    })
    
    if (!response.ok) {
      throw new Error(`Failed to get log configuration: ${response.statusText}`)
    }
    
    return response.json()
  }
  
  async updateLogConfiguration(appId: string, config: LogConfiguration): Promise<void> {
    const apiBaseUrl = await configService.getAdminApiUrl()
    const token = this.getAuthToken()
    
    const response = await fetch(`${apiBaseUrl}/api/v1/logs/apps/${appId}/logs/config`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
      },
      body: JSON.stringify(config),
    })
    
    if (!response.ok) {
      throw new Error(`Failed to update log configuration: ${response.statusText}`)
    }
  }
  
  async getLogAnalytics(appId: string): Promise<LogAnalytics> {
    const apiBaseUrl = await configService.getAdminApiUrl()
    const token = this.getAuthToken()
    
    const response = await fetch(`${apiBaseUrl}/api/v1/logs/apps/${appId}/logs/analytics`, {
      headers: {
        ...(token && { 'Authorization': `Bearer ${token}` })
      }
    })
    
    if (!response.ok) {
      throw new Error(`Failed to get log analytics: ${response.statusText}`)
    }
    
    return response.json()
  }
  
  async exportLogs(params: LogSearchParams): Promise<{ export_id: string; status: string }> {
    const apiBaseUrl = await configService.getAdminApiUrl()
    const token = this.getAuthToken()
    
    const response = await fetch(`${apiBaseUrl}/api/v1/logs/apps/${params.app_id}/logs/export`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
      },
      body: JSON.stringify(params),
    })
    
    if (!response.ok) {
      throw new Error(`Failed to export logs: ${response.statusText}`)
    }
    
    return response.json()
  }
}

export const loggingService = new LoggingService()