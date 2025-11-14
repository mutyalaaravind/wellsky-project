import { getAuthToken } from '../utils/auth'
import { configService } from './configService'

export interface OrganizationData {
  business_unit: string
  solution_code: string
}

export interface AuthorizationData {
  roles: string[]
}

export interface SettingsData {
  extract: Record<string, any>
}

export interface AuditData {
  created_by: string
  created_on: string
  modified_by: string
  modified_on: string
}

export interface UserData {
  name: string
  email: string
}

export interface Role {
  id: string
  name: string
  description: string
  permissions: string[]
  inherits: string[]
  active: boolean
}

export interface UserProfile {
  id: string
  user: UserData
  organizations: OrganizationData[]
  authorization: AuthorizationData
  settings: SettingsData
  active: boolean
  audit?: AuditData
  resolvedRoles?: Role[]
  resolvedPermissions?: string[]
}

export interface UserProfileCreateRequest {
  name: string
  email: string
  organizations: OrganizationData[]
  roles: string[]
  settings?: SettingsData
}

export interface UserProfileUpdateRequest {
  name?: string
  organizations?: OrganizationData[]
  roles?: string[]
  settings?: SettingsData
  active?: boolean
}

export interface UserProfileResponse {
  success: boolean
  message: string
  data: {
    profile: UserProfile
    resolvedRoles: Role[]
    resolvedPermissions: string[]
  }
}

export interface UserProfileListResponse {
  success: boolean
  message: string
  data: UserProfile[]
  total: number
  pagination: {
    limit: number
    offset: number
    returned: number
    has_more: boolean
  }
}

export interface UserProfileDeleteResponse {
  success: boolean
  message: string
  deleted_id: string
}

class UserProfilesService {
  private baseUrl = '/api/v1/profiles'

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


  async getAllUserProfiles(
    activeOnly: boolean = true,
    businessUnit?: string,
    solutionCode?: string,
    role?: string,
    limit: number = 100,
    offset: number = 0
  ): Promise<UserProfileListResponse> {
    const params = new URLSearchParams({
      active_only: activeOnly.toString(),
      limit: limit.toString(),
      offset: offset.toString()
    })

    if (businessUnit) params.append('business_unit', businessUnit)
    if (solutionCode) params.append('solution_code', solutionCode)
    if (role) params.append('role', role)

    return this.apiCall<UserProfileListResponse>(`?${params}`)
  }

  async getUserProfile(profileId: string): Promise<UserProfileResponse> {
    return this.apiCall<UserProfileResponse>(`/${encodeURIComponent(profileId)}`)
  }

  async getMyProfile(): Promise<UserProfileResponse> {
    return this.apiCall<UserProfileResponse>('/myprofile')
  }

  async createUserProfile(profileData: UserProfileCreateRequest): Promise<UserProfileResponse> {
    return this.apiCall<UserProfileResponse>('', {
      method: 'POST',
      body: JSON.stringify(profileData)
    })
  }

  async updateUserProfile(profileId: string, profileData: UserProfileUpdateRequest): Promise<UserProfileResponse> {
    return this.apiCall<UserProfileResponse>(`/${encodeURIComponent(profileId)}`, {
      method: 'PUT',
      body: JSON.stringify(profileData)
    })
  }

  async deleteUserProfile(profileId: string): Promise<UserProfileDeleteResponse> {
    return this.apiCall<UserProfileDeleteResponse>(`/${encodeURIComponent(profileId)}`, {
      method: 'DELETE'
    })
  }

  async searchUserProfiles(searchTerm: string, activeOnly: boolean = true): Promise<UserProfileListResponse> {
    const params = new URLSearchParams({
      search_term: searchTerm,
      active_only: activeOnly.toString()
    })

    return this.apiCall<UserProfileListResponse>(`/search?${params}`, {
      method: 'POST'
    })
  }
}

export const userProfilesService = new UserProfilesService()