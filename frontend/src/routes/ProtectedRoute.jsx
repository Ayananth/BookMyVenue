import { Navigate, useLocation } from "react-router-dom"
import { useAuth } from "../contexts/AuthContext"

function AuthLoading() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <p className="text-sm text-muted-foreground">Loading...</p>
    </div>
  )
}

export function ProtectedRoute({
  children,
  requiredRole,
  loginPath = "/venue/auth",
}) {
  const { user, loading, isAuthenticated } = useAuth()
  const location = useLocation()

  if (loading) {
    return <AuthLoading />
  }

  if (!isAuthenticated) {
    return <Navigate to={loginPath} state={{ from: location }} replace />
  }

  if (requiredRole && user?.role !== requiredRole) {
    return (
      <Navigate
        to={loginPath}
        state={{ wrongRole: true, from: location }}
        replace
      />
    )
  }

  return children
}

export function GuestRoute({
  children,
  allowedRole,
  redirectTo = "/venue",
}) {
  const { user, loading, isAuthenticated } = useAuth()

  if (loading) {
    return <AuthLoading />
  }

  if (isAuthenticated && user?.role === allowedRole) {
    return <Navigate to={redirectTo} replace />
  }

  return children
}
