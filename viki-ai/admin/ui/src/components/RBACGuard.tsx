import React, { ReactNode } from 'react'
import { useRBAC } from '../hooks/useRBAC'

interface RBACGuardProps {
  children: ReactNode
  permissions?: string | string[]
  requireAll?: boolean
  fallback?: ReactNode
}

export const RBACGuard: React.FC<RBACGuardProps> = ({
  children,
  permissions = [],
  requireAll = true,
  fallback = null
}) => {
  const { hasPermission, hasAnyPermission, loading } = useRBAC()

  if (loading) {
    return <>{fallback}</>
  }

  if (!permissions || (Array.isArray(permissions) && permissions.length === 0)) {
    return <>{children}</>
  }

  const hasRequiredPermissions = requireAll
    ? hasPermission(permissions)
    : hasAnyPermission(permissions)

  return hasRequiredPermissions ? <>{children}</> : <>{fallback}</>
}

export default RBACGuard