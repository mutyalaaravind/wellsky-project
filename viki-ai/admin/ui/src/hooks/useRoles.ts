import { useState, useEffect, useCallback } from 'react'
import { rolesService, Role, RolePermissionsResponse } from '../services/rolesService'

export const useRoles = () => {
  const [roles, setRoles] = useState<Role[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [total, setTotal] = useState(0)
  const [effectivePermissions, setEffectivePermissions] = useState<Record<string, string[]>>({})

  const fetchRoles = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await rolesService.getAllRoles(true, 500, 0) // Get all active roles
      setRoles(response.data)
      setTotal(response.total)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch roles')
    } finally {
      setLoading(false)
    }
  }, [])

  const getRolePermissions = useCallback(async (roleId: string): Promise<string[]> => {
    try {
      const response: RolePermissionsResponse = await rolesService.getRolePermissions(roleId)
      return response.effective_permissions
    } catch (err) {
      console.error(`Failed to fetch permissions for role ${roleId}:`, err)
      return []
    }
  }, [])

  useEffect(() => {
    fetchRoles()
  }, [fetchRoles])

  useEffect(() => {
    if (roles.length === 0) return

    const loadEffectivePermissions = async () => {
      const permissionsPromises = roles.map(async (role) => {
        try {
          const response: RolePermissionsResponse = await rolesService.getRolePermissions(role.id)
          return { roleId: role.id, permissions: response.effective_permissions }
        } catch (err) {
          console.error(`Failed to fetch permissions for role ${role.id}:`, err)
          return { roleId: role.id, permissions: [] }
        }
      })

      try {
        const results = await Promise.all(permissionsPromises)
        const permissionsMap = results.reduce((acc, { roleId, permissions }) => {
          acc[roleId] = permissions
          return acc
        }, {} as Record<string, string[]>)

        setEffectivePermissions(permissionsMap)
      } catch (err) {
        console.error('Failed to load effective permissions:', err)
      }
    }

    loadEffectivePermissions()
  }, [roles])

  return {
    roles,
    loading,
    error,
    total,
    effectivePermissions,
    fetchRoles,
    getRolePermissions,
  }
}