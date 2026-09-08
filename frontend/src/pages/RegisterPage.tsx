/**
 * frontend/src/pages/RegisterPage.tsx
 * Phase 1 — Registration page using Supabase Auth via authStore.
 */

import { useState, useEffect, type FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { authService } from "../services/authService";
import { useAuthStore } from "../store/authStore";

export default function RegisterPage() {
  const navigate = useNavigate();
  const { isAuthenticated, setAuth } = useAuthStore();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/resume", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const validate = (): boolean => {
    const trimmedEmail = email.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!fullName.trim()) {
      setValidationError("Full name is required.");
      return false;
    }
    if (!trimmedEmail) {
      setValidationError("Email is required.");
      return false;
    }
    if (!emailRegex.test(trimmedEmail)) {
      setValidationError("Please enter a valid email address.");
      return false;
    }
    if (password.length < 8) {
      setValidationError("Password must be at least 8 characters.");
      return false;
    }
    if (password !== confirm) {
      setValidationError("Passwords do not match.");
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
      const response = await authService.register(fullName.trim(), email.trim(), password);
      setAuth(response.user, response.access_token);
      navigate("/resume", { replace: true });
    } catch (error: unknown) {
      const message =
        error && typeof error === "object" && "response" in error
          ? (error as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : null;
      setSubmitError(message || "Unable to create your account. Please try again.");
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

        <h1 className="auth-title">Create your account</h1>
        <p className="auth-subtitle">Start your AI-powered interview journey</p>

        {displayError && (
          <div className="auth-error" role="alert">
            {displayError}
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form" noValidate>
          <div className="auth-field">
            <label htmlFor="register-fullname" className="auth-label">
              Full Name
            </label>
            <input
              id="register-fullname"
              type="text"
              autoComplete="name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Jane Smith"
              className="auth-input"
              required
              disabled={submitting}
            />
          </div>

          <div className="auth-field">
            <label htmlFor="register-email" className="auth-label">
              Email
            </label>
            <input
              id="register-email"
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
            <label htmlFor="register-password" className="auth-label">
              Password
              <span className="auth-label-hint"> (min 8 characters)</span>
            </label>
            <input
              id="register-password"
              type="password"
              autoComplete="new-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="auth-input"
              required
              disabled={submitting}
            />
          </div>

          <div className="auth-field">
            <label htmlFor="register-confirm" className="auth-label">
              Confirm Password
            </label>
            <input
              id="register-confirm"
              type="password"
              autoComplete="new-password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              placeholder="••••••••"
              className="auth-input"
              required
              disabled={submitting}
            />
          </div>

          <button
            id="register-submit"
            type="submit"
            className="auth-btn auth-btn-primary"
            disabled={submitting}
          >
            {submitting ? (
              <>
                <span className="auth-spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
                <span>Creating account…</span>
              </>
            ) : (
              "Create Account"
            )}
          </button>
        </form>

        <p className="auth-footer-text">
          Already have an account?{" "}
          <Link to="/login" className="auth-link">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
