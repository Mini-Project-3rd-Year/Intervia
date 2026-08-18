/**
 * frontend/src/pages/DashboardPage.tsx
 * Phase 1 — Protected dashboard stub.
 *
 * Shows authenticated user info and a logout button.
 * Placeholder for Phase 18 (full Dashboard) content.
 */

import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../features/auth/authStore";

export default function DashboardPage() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  const fullName =
    (user?.user_metadata?.full_name as string | undefined) ||
    user?.email ||
    "User";

  const handleLogout = async () => {
    try {
      await logout();
      navigate("/login", { replace: true });
    } catch {
      // logout errors are non-critical — navigate anyway
      navigate("/login", { replace: true });
    }
  };

  return (
    <div className="dashboard-page">
      {/* Top bar */}
      <header className="dashboard-header">
        <div className="dashboard-brand">
          <span className="auth-brand-icon">🎯</span>
          <span className="auth-brand-name">Intervia</span>
        </div>
        <div className="dashboard-header-right">
          <span className="dashboard-user-email">{user?.email}</span>
          <button
            id="dashboard-logout"
            onClick={handleLogout}
            className="auth-btn auth-btn-secondary"
          >
            Sign Out
          </button>
        </div>
      </header>

      {/* Main content */}
      <main className="dashboard-main">
        <section className="dashboard-welcome">
          <h1 className="dashboard-welcome-title">
            Welcome back, {fullName} 👋
          </h1>
          <p className="dashboard-welcome-subtitle">
            Your AI-powered interview platform is ready.
          </p>
        </section>

        {/* Phase placeholder cards */}
        <section className="dashboard-cards">
          {[
            {
              icon: "📄",
              title: "Resume Intelligence",
              description: "Upload your resume for AI-powered skill extraction.",
              phase: "Phase 2",
            },
            {
              icon: "🎯",
              title: "Job Matching",
              description: "Match your profile against job descriptions.",
              phase: "Phase 3",
            },
            {
              icon: "🤖",
              title: "Adaptive Interview",
              description: "Start an AI-driven adaptive interview session.",
              phase: "Phase 7",
            },
            {
              icon: "💡",
              title: "AI Career Coach",
              description: "Get a personalized improvement plan.",
              phase: "Phase 15",
            },
          ].map((card) => (
            <div key={card.title} className="dashboard-card dashboard-card-coming-soon">
              <div className="dashboard-card-icon">{card.icon}</div>
              <h2 className="dashboard-card-title">{card.title}</h2>
              <p className="dashboard-card-desc">{card.description}</p>
              <span className="dashboard-phase-badge">{card.phase}</span>
            </div>
          ))}
        </section>
      </main>
    </div>
  );
}
