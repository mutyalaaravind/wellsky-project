export interface DocumentStatus {
  status?: {
    progress?: number | null
    status?: string
    run_id?: string
    timestamp?: string
    [key: string]: any
  }
  [key: string]: any
}

export interface DocumentStatusResponse {
  success: boolean
  message?: string
  data?: DocumentStatus
}

import { configService } from './configService'
import { getAuthToken } from '../utils/auth'

class DocumentsService {

  private async apiCall<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const apiBaseUrl = await configService.getAdminApiUrl()
    const token = getAuthToken()

    const response = await fetch(`${apiBaseUrl}/api/v1/demo${endpoint}`, {
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

  async getDocumentStatus(appId: string, subjectId: string, documentId: string): Promise<DocumentStatus> {
    const response = await this.apiCall<DocumentStatus>(`/${appId}/subjects/${subjectId}/documents/${documentId}/status`)
    return response
  }

}

export const documentsService = new DocumentsService()