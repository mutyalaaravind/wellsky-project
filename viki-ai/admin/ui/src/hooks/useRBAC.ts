import { useUserProfile } from './useUserProfile'

export const useRBAC = () => {
  const { resolvedPermissions, loading } = useUserProfile()

  const hasPermission = (requiredPermissions: string | string[]): boolean => {
    if (loading) {
      return false
    }

    const permissions = Array.isArray(requiredPermissions)
      ? requiredPermissions
      : requiredPermissions.split(' ').filter(p => p.trim())

    return permissions.every(permission =>
      resolvedPermissions.includes(permission.trim())
    )
  }

  const hasAnyPermission = (requiredPermissions: string | string[]): boolean => {
    if (loading) {
      return false
    }

    const permissions = Array.isArray(requiredPermissions)
      ? requiredPermissions
      : requiredPermissions.split(' ').filter(p => p.trim())

    return permissions.some(permission =>
      resolvedPermissions.includes(permission.trim())
    )
  }

  return {
    hasPermission,
    hasAnyPermission,
    resolvedPermissions,
    loading
  }
}