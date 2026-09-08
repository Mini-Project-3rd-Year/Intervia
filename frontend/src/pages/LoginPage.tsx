/**
 * frontend/src/pages/LoginPage.tsx
 * Phase 1 — Login page using Supabase Auth via authStore.
 */

import { useState, useEffect, type FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { authService } from "../services/authService";
import { useAuthStore } from "../store/authStore";

export default function LoginPage() {
  const navigate = useNavigate();
  const { isAuthenticated, setAuth } = useAuthStore();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/dashboard", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const validate = (): boolean => {
    const trimmedEmail = email.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!trimmedEmail) {
      setValidationError("Email is required.");
      return false;
    }
    if (!emailRegex.test(trimmedEmail)) {
      setValidationError("Please enter a valid email address.");
      return false;
    }
    if (!password || password.length < 8) {
      setValidationError("Password must be at least 8 characters long.");
      return false;
    }

    setValidationError(null);
    return true;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSubmitError(null);
    if (!validate()) return;

    setSubmitting(true);
    try {
      const response = await authService.login(email.trim(), password);
      setAuth(response.user, response.access_token);
      navigate("/dashboard", { replace: true });
    } catch (error: unknown) {
      const message =
        error && typeof error === "object" && "response" in error
          ? (error as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : null;
      setSubmitError(message || "Invalid email or password. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const displayError = validationError || submitError;

  return (
    <div className="auth-page">
      <div className="auth-card">
        {/* Logo / Brand */}
        <div className="auth-brand">
          <span className="auth-brand-icon">🎯</span>
          <span className="auth-brand-name">Intervia</span>
        </div>

        <h1 className="auth-title">Welcome back</h1>
        <p className="auth-subtitle">Sign in to continue your interview prep</p>

        {displayError && (
          <div className="auth-error" role="alert">
            {displayError}
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form" noValidate>
          <div className="auth-field">
            <label htmlFor="login-email" className="auth-label">
              Email
            </label>
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
            />
          </div>

          <div className="auth-field">
            <label htmlFor="login-password" className="auth-label">
              Password
            </label>
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
            />
          </div>

          <button
            id="login-submit"
            type="submit"
            className="auth-btn auth-btn-primary"
            disabled={submitting}
          >
            {submitting ? (
              <>
                <span className="auth-spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
                <span>Signing in…</span>
              </>
            ) : (
              "Sign In"
            )}
          </button>
        </form>

        <p className="auth-footer-text">
          Don&apos;t have an account?{" "}
          <Link to="/register" className="auth-link">
            Create one
          </Link>
        </p>
      </div>
    </div>
  );
}
