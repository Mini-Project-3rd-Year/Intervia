/**
 * frontend/src/components/layout/AppShell.tsx
 * Shared authenticated layout with sidebar navigation.
 * Used by Dashboard, Interview, Resume, Jobs, Coaching, Profile pages.
 */

import { useState, type ReactNode } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuthStore } from "../../features/auth/authStore";

interface NavItem {
  label: string;
  to: string;
  icon: string;
}

const mainNav: NavItem[] = [
  { label: "Dashboard", to: "/dashboard", icon: "⊞" },
  { label: "Job Match",  to: "/jobs",      icon: "⌖" },
  { label: "Interview",  to: "/interview", icon: "◉" },
  { label: "AI Coach",   to: "/coaching",  icon: "✦" },
];

const prepNav: NavItem[] = [
  { label: "Resume",          to: "/resume",  icon: "▤" },
  { label: "Practice History",to: "/history", icon: "◷" },
];

const accountNav: NavItem[] = [
  { label: "Profile",  to: "/profile",  icon: "◯" },
];

interface AppShellProps {
  children: ReactNode;
  /** Page title shown in top bar on mobile */
  pageTitle?: string;
}

export default function AppShell({ children, pageTitle }: AppShellProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [collapsed, setCollapsed] = useState(false);

  const fullName =
    (user?.user_metadata?.full_name as string | undefined) ||
    user?.email?.split("@")[0] ||
    "User";

  const initials = fullName
    .split(" ")
    .map((w) => w[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  const handleLogout = async () => {
    try { await logout(); } catch { /* ignore */ }
    navigate("/login", { replace: true });
  };

  const isActive = (to: string) => location.pathname === to;

  const renderNavItem = (item: NavItem) => (
    <Link
      key={item.to}
      to={item.to}
      className={`sidebar-item${isActive(item.to) ? " active" : ""}`}
      title={collapsed ? item.label : undefined}
    >
      <span className="sidebar-item-icon" aria-hidden="true">
        {item.icon}
      </span>
      {!collapsed && (
        <span className="sidebar-item-label">{item.label}</span>
      )}
    </Link>
  );

  return (
    <div className="app-shell">
      {/* ── Sidebar ──────────────────────────────────── */}
      <aside className={`sidebar${collapsed ? " collapsed" : ""}`}>
        {/* Logo + collapse toggle */}
        <div className="sidebar-logo" style={{ cursor: "pointer" }} onClick={() => setCollapsed(!collapsed)}>
          <div className="sidebar-logo-mark" aria-label="Intervia">I</div>
          {!collapsed && <span className="sidebar-logo-name">Intervia</span>}
        </div>

        <nav className="sidebar-nav" aria-label="Main navigation">
          {/* MAIN */}
          {!collapsed && <span className="sidebar-section-label">Main</span>}
          {mainNav.map(renderNavItem)}

          {/* PREPARE */}
          {!collapsed && <span className="sidebar-section-label" style={{ marginTop: "0.5rem" }}>Prepare</span>}
          {prepNav.map(renderNavItem)}

          {/* ACCOUNT */}
          {!collapsed && <span className="sidebar-section-label" style={{ marginTop: "0.5rem" }}>Account</span>}
          {accountNav.map(renderNavItem)}
        </nav>

        {/* User footer */}
        <div className="sidebar-footer">
          <div
            className="sidebar-user"
            role="button"
            tabIndex={0}
            onClick={handleLogout}
            onKeyDown={(e) => e.key === "Enter" && handleLogout()}
            title="Sign out"
            aria-label={`Sign out as ${fullName}`}
          >
            <div className="sidebar-avatar" aria-hidden="true">{initials}</div>
            {!collapsed && (
              <div className="sidebar-user-info">
                <div className="sidebar-user-name">{fullName}</div>
                <div className="sidebar-user-email">Sign out</div>
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* ── Main content ─────────────────────────────── */}
      <main className={`app-main${collapsed ? " sidebar-collapsed" : ""}`}>
        {/* Mobile top bar */}
        <div
          style={{
            display: "none",
            alignItems: "center",
            gap: "0.875rem",
            padding: "0.875rem 1.25rem",
            borderBottom: "1px solid var(--border-subtle)",
            background: "var(--bg-surface)",
          }}
          className="mobile-topbar"
          aria-label="Mobile navigation"
        >
          <div
            style={{
              width: 28, height: 28, borderRadius: 7,
              background: "var(--blue)",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontWeight: 800, color: "white", fontSize: "0.875rem",
            }}
          >I</div>
          <span style={{ fontWeight: 700, fontSize: "0.9375rem", color: "var(--text-primary)" }}>
            {pageTitle || "Intervia"}
          </span>
        </div>

        {children}
      </main>

      <style>{`
        @media (max-width: 768px) {
          .mobile-topbar { display: flex !important; }
        }
      `}</style>
    </div>
  );
}
