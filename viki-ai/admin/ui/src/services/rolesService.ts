import { getAuthToken } from '../utils/auth'
import { configService } from './configService'

export interface Role {
  id: string
  name: string
  description: string
  permissions: string[]
  inherits: string[]
  active: boolean
}

export interface RoleCreateRequest {
  id: string
  name: string
  description: string
  permissions: string[]
  inherits: string[]
}

export interface RoleUpdateRequest {
  name?: string
  description?: string
  permissions?: string[]
  inherits?: string[]
  active?: boolean
}

export interface RoleResponse {
  success: boolean
  message: string
  data: Role
}

export interface RoleListResponse {
  success: boolean
  message: string
  data: Role[]
  total: number
  pagination: {
    limit: number
    offset: number
    returned: number
    has_more: boolean
  }
}

export interface RoleDeleteResponse {
  success: boolean
  message: string
  deleted_id: string
}

export interface RolePermissionsResponse {
  success: boolean
  message: string
  role_id: string
  effective_permissions: string[]
}

class RolesService {
  private baseUrl = '/api/v1/roles'

  private async apiCall<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const apiBaseUrl = await configService.getAdminApiUrl()
    const token = getAuthToken()

    const response = await fetch(`${apiBaseUrl}${this.baseUrl}${endpoint}`, {
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

  async getAllRoles(
    activeOnly: boolean = true,
    limit: number = 100,
    offset: number = 0
  ): Promise<RoleListResponse> {
    const params = new URLSearchParams({
      active_only: activeOnly.toString(),
      limit: limit.toString(),
      offset: offset.toString()
    })

    return this.apiCall<RoleListResponse>(`?${params}`)
  }

  async getRole(roleId: string): Promise<RoleResponse> {
    return this.apiCall<RoleResponse>(`/${encodeURIComponent(roleId)}`)
  }

  async createRole(roleData: RoleCreateRequest): Promise<RoleResponse> {
    return this.apiCall<RoleResponse>('', {
      method: 'POST',
      body: JSON.stringify(roleData)
    })
  }

  async updateRole(roleId: string, roleData: RoleUpdateRequest): Promise<RoleResponse> {
    return this.apiCall<RoleResponse>(`/${encodeURIComponent(roleId)}`, {
      method: 'PUT',
      body: JSON.stringify(roleData)
    })
  }

  async deleteRole(roleId: string): Promise<RoleDeleteResponse> {
    return this.apiCall<RoleDeleteResponse>(`/${encodeURIComponent(roleId)}`, {
      method: 'DELETE'
    })
  }

  async getRolePermissions(roleId: string): Promise<RolePermissionsResponse> {
    return this.apiCall<RolePermissionsResponse>(`/${encodeURIComponent(roleId)}/permissions`)
  }

  async searchRoles(searchTerm: string, activeOnly: boolean = true): Promise<RoleListResponse> {
    const params = new URLSearchParams({
      search_term: searchTerm,
      active_only: activeOnly.toString()
    })

    return this.apiCall<RoleListResponse>(`/search?${params}`)
  }

  // Helper method to get available roles for dropdowns
  async getAvailableRoles(): Promise<Role[]> {
    try {
      const response = await this.getAllRoles(true, 500, 0) // Get all active roles
      return response.success ? response.data : []
    } catch (error) {
      console.error('Failed to fetch available roles:', error)
      return []
    }
  }

  // Helper method to format role for display
  formatRoleForDisplay(role: Role): string {
    return `${role.name} (${role.id})`
  }

  // Helper method to get role by ID from a list
  getRoleFromList(roles: Role[], roleId: string): Role | undefined {
    return roles.find(role => role.id === roleId)
  }
}

export const rolesService = new RolesService()