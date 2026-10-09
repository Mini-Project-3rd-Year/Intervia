/**
 * frontend/src/pages/RegisterPage.tsx
 * Phase 1 — Registration page using Supabase Auth via authStore.
 */

import { useState, useEffect, type FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuthStore } from "../features/auth/authStore";

export default function RegisterPage() {
  const navigate = useNavigate();
  const { register, session, loading, error, clearError } = useAuthStore();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // If already logged in, redirect to dashboard
  useEffect(() => {
    if (!loading && session) {
      navigate("/dashboard", { replace: true });
    }
  }, [session, loading, navigate]);

  const validate = (): boolean => {
    if (!fullName.trim()) {
      setValidationError("Full name is required.");
      return false;
    }
    if (!email.trim()) {
      setValidationError("Email is required.");
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
    clearError();
    setSuccessMessage(null);
    if (!validate()) return;

    setSubmitting(true);
    try {
      await register(email.trim(), password, fullName.trim());
      // If Supabase email confirmation is enabled, the session won't be set yet
      // Show a friendly message instead of redirecting
      setSuccessMessage(
        "Account created! Check your email to confirm your address, then sign in."
      );
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

        <h1 className="auth-title">Create your account</h1>
        <p className="auth-subtitle">Start your AI-powered interview journey</p>

        {displayError && (
          <div className="auth-error" role="alert">
            {displayError}
          </div>
        )}
        {successMessage && (
          <div className="auth-success" role="status">
            {successMessage}
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
              aria-required="true"
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
              aria-required="true"
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
              aria-required="true"
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
              aria-required="true"
            />
          </div>

          <button
            id="register-submit"
            type="submit"
            className="auth-btn auth-btn-primary"
            disabled={submitting}
            aria-label="Create your Intervia account"
          >
            {submitting ? "Creating account…" : "Create Account"}
          </button>

          <div className="auth-divider"><span>or</span></div>

          <button
            id="register-demo"
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
          Already have an account?{" "}
          <Link to="/login" className="auth-link">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
