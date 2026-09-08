/**
 * frontend/src/components/auth/ProtectedRoute.tsx
 * Phase 1 — Route guard for authenticated pages.
 *
 * Behavior:
 *   loading  → shows a full-screen spinner
 *   no session → redirects to /login
 *   authenticated → renders children
 */

import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuthStore } from "../../store/authStore";

interface ProtectedRouteProps {
  children: ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, initialized } = useAuthStore();

  if (!initialized) {
    return (
      <div
        style={{
          minHeight: "100vh",
          background: "#050c1a",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <div className="auth-spinner" aria-label="Loading…" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

export default ProtectedRoute;
