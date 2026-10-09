/**
 * frontend/src/pages/LoginPage.tsx
 * Phase 1 — Login page using Supabase Auth via authStore.
 * UI updated to design system v2.
 */

import { useState, useEffect, type FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuthStore } from "../features/auth/authStore";

export default function LoginPage() {
  const navigate = useNavigate();
  const { login, session, loading, error, clearError } = useAuthStore();

  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  // If already logged in, redirect to dashboard
  useEffect(() => {
    if (!loading && session) {
      navigate("/dashboard", { replace: true });
    }
  }, [session, loading, navigate]);

  const validate = (): boolean => {
    if (!email.trim()) { setValidationError("Email is required."); return false; }
    if (!password)     { setValidationError("Password is required."); return false; }
    setValidationError(null);
    return true;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    clearError();
    if (!validate()) return;
    setSubmitting(true);
    try {
      await login(email.trim(), password);
      navigate("/dashboard", { replace: true });
    } catch {
      // error is set in the store
    } finally {
      setSubmitting(false);
    }
  };

  const displayError = validationError || error;

  return (
    <div className="auth-page">
      <div className="auth-card">
        {/* Brand */}
        <Link to="/" style={{ textDecoration: "none" }}>
          <div className="auth-brand">
            <div style={{ width: 30, height: 30, borderRadius: 8, background: "var(--blue)", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800, color: "white", fontSize: "0.875rem", flexShrink: 0 }}>I</div>
            <span className="auth-brand-name">Intervia</span>
          </div>
        </Link>

        <h1 className="auth-title">Welcome back</h1>
        <p className="auth-subtitle">Sign in to continue your interview prep</p>

        {displayError && (
          <div className="auth-error" role="alert">{displayError}</div>
        )}

        <form onSubmit={handleSubmit} className="auth-form" noValidate>
          <div className="auth-field">
            <label htmlFor="login-email" className="auth-label">Email</label>
            <input
              id="login-email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="auth-input"
              required
              disabled={submitting}
              aria-required="true"
            />
          </div>

          <div className="auth-field">
            <label htmlFor="login-password" className="auth-label">Password</label>
            <input
              id="login-password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="auth-input"
              required
              disabled={submitting}
              aria-required="true"
            />
          </div>

          <button
            id="login-submit"
            type="submit"
            className="auth-btn auth-btn-primary"
            disabled={submitting}
            aria-label="Sign in to your account"
          >
            {submitting ? "Signing in…" : "Sign In"}
          </button>

          <div className="auth-divider"><span>or</span></div>

          <button
            id="login-demo"
            type="button"
            className="auth-btn auth-btn-demo"
            disabled={submitting}
            aria-label="Sign in as a guest for a quick demo"
            onClick={async () => {
              setSubmitting(true);
              clearError();
              try {
                const { loginDemo } = useAuthStore.getState();
                await loginDemo();
                navigate("/dashboard", { replace: true });
              } catch {
                // error handled in store
              } finally {
                setSubmitting(false);
              }
            }}
          >
            Try Demo — No Account Needed
          </button>
        </form>

        <p className="auth-footer-text">
          Don&apos;t have an account?{" "}
          <Link to="/register" className="auth-link">Create one free</Link>
        </p>
      </div>
    </div>
  );
}
