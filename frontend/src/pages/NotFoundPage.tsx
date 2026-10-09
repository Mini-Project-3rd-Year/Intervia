/**
 * frontend/src/pages/NotFoundPage.tsx
 * Redesigned 404 page.
 */

import { Link } from "react-router-dom";

const NotFoundPage = () => {
  return (
    <div
      style={{
        minHeight: "100vh",
        background: "var(--bg-base)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "2rem",
        textAlign: "center",
        fontFamily: "inherit",
      }}
    >
      {/* Logo */}
      <div style={{ marginBottom: "2.5rem" }}>
        <Link to="/" style={{ textDecoration: "none", display: "inline-flex", alignItems: "center", gap: "0.5rem" }}>
          <div style={{ width: 32, height: 32, borderRadius: 8, background: "var(--blue)", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800, color: "white", fontSize: "0.875rem" }}>I</div>
          <span style={{ fontWeight: 700, fontSize: "1rem", color: "var(--text-primary)", letterSpacing: "-0.02em" }}>Intervia</span>
        </Link>
      </div>

      {/* 404 */}
      <div
        className="text-gradient"
        style={{
          fontSize: "5rem",
          fontWeight: 900,
          letterSpacing: "-0.05em",
          lineHeight: 1,
          marginBottom: "1.25rem",
        }}
        aria-hidden="true"
      >
        404
      </div>

      <h1
        style={{
          fontSize: "1.5rem",
          fontWeight: 700,
          color: "var(--text-primary)",
          letterSpacing: "-0.02em",
          marginBottom: "0.625rem",
        }}
      >
        Page Not Found
      </h1>

      <p
        style={{
          color: "var(--text-muted)",
          fontSize: "0.9375rem",
          maxWidth: 360,
          lineHeight: 1.6,
          marginBottom: "2rem",
        }}
      >
        The page you're looking for doesn't exist or has been moved.
      </p>

      <div style={{ display: "flex", gap: "0.75rem" }}>
        <Link to="/" style={{ textDecoration: "none" }}>
          <button className="btn btn-primary" id="notfound-home-btn">
            ← Back to Home
          </button>
        </Link>
        <Link to="/dashboard" style={{ textDecoration: "none" }}>
          <button className="btn btn-secondary" id="notfound-dashboard-btn">
            Go to Dashboard
          </button>
        </Link>
      </div>
    </div>
  );
};

export default NotFoundPage;
