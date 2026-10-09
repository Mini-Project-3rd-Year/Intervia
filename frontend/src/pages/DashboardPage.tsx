/**
 * frontend/src/pages/DashboardPage.tsx
 * Redesigned dashboard — clean hierarchy, readiness score focal point,
 * skill bars with trends, interview history with actions.
 * Preserves all auth/state/navigation logic.
 */

import { useNavigate, Link } from "react-router-dom";
import { useAuthStore } from "../features/auth/authStore";
import AppShell from "../components/layout/AppShell";

/* ── Static demo data (replaced by real API in Phase 18) ── */
const readinessScore = 72;
const readinessDelta = "+8%";
const readinessInsight = "Improving steadily. Focus on System Design and Communication next.";

const supportingStats = [
  { label: "Interviews",       value: "3",   delta: "+1 this week",      positive: true },
  { label: "Skills Practiced", value: "14",  delta: "across 3 sessions", positive: null },
  { label: "Improvement",      value: "+18%",delta: "last 30 days",      positive: true },
];

const skills = [
  { name: "React & TypeScript", score: 90, trend: "up",   color: "var(--blue)" },
  { name: "Problem Solving",    score: 82, trend: "up",   color: "var(--blue)" },
  { name: "Communication",      score: 68, trend: "flat", color: "var(--cyan)" },
  { name: "System Design",      score: 55, trend: "down", color: "var(--amber)" },
  { name: "Behavioral / STAR",  score: 72, trend: "up",   color: "var(--violet)" },
  { name: "Data Structures",    score: 63, trend: "flat", color: "var(--cyan)" },
];

const recentInterviews = [
  { id: 1, role: "Frontend Developer — React",     type: "Technical",            date: "Sep 29, 2026", score: 78 },
  { id: 2, role: "Full Stack Engineer",             type: "Mixed (HR + Technical)",date: "Sep 25, 2026", score: 65 },
  { id: 3, role: "Software Engineer — Backend",    type: "Behavioral",           date: "Sep 20, 2026", score: 54 },
];

/* ── Score ring SVG ──────────────────────────────────────── */
function ScoreRing({ score, size = 120 }: { score: number; size?: number }) {
  const r = (size / 2) - 10;
  const circ = 2 * Math.PI * r;
  const filled = (score / 100) * circ;
  const scoreColor = score >= 70 ? "var(--green)" : score >= 50 ? "var(--amber)" : "var(--red)";

  return (
    <div className="score-ring-container" style={{ width: size, height: size }} aria-label={`Readiness score: ${score}%`}>
      <svg className="score-ring-svg" width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle
          className="score-ring-track"
          cx={size / 2} cy={size / 2} r={r}
          strokeWidth="8"
        />
        <circle
          className="score-ring-fill"
          cx={size / 2} cy={size / 2} r={r}
          strokeWidth="8"
          stroke={scoreColor}
          strokeDasharray={`${filled} ${circ}`}
          strokeLinecap="round"
        />
      </svg>
      <div className="score-ring-center">
        <div style={{ fontSize: size > 100 ? "1.5rem" : "1.125rem", fontWeight: 800, color: "var(--text-primary)", letterSpacing: "-0.04em", lineHeight: 1 }}>
          {score}%
        </div>
      </div>
    </div>
  );
}

/* ── Trend indicator ────────────────────────────────────── */
function Trend({ direction }: { direction: "up" | "down" | "flat" }) {
  if (direction === "up")   return <span style={{ color: "var(--green)", fontSize: "0.75rem", fontWeight: 700 }}>↑</span>;
  if (direction === "down") return <span style={{ color: "var(--red)",   fontSize: "0.75rem", fontWeight: 700 }}>↓</span>;
  return <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>→</span>;
}

/* ── Score color helper ─────────────────────────────────── */
function scoreColor(score: number) {
  if (score >= 70) return "var(--green)";
  if (score >= 55) return "var(--amber)";
  return "var(--red)";
}

/* ── Score fill class helper ───────────────────────────── */
function fillClass(score: number) {
  if (score >= 70) return "progress-fill progress-fill-green";
  if (score >= 55) return "progress-fill progress-fill-amber";
  return "progress-fill progress-fill-red";
}

/* ── Main ────────────────────────────────────────────────── */
export default function DashboardPage() {
  const navigate = useNavigate();
  const { user } = useAuthStore();

  const greeting = () => {
    const h = new Date().getHours();
    if (h < 12) return "Good morning";
    if (h < 17) return "Good afternoon";
    return "Good evening";
  };

  const firstName =
    ((user?.user_metadata?.full_name as string | undefined) || "")
      .split(" ")[0] ||
    user?.email?.split("@")[0] ||
    "there";

  const weakestSkill = [...skills].sort((a, b) => a.score - b.score)[0];

  return (
    <AppShell pageTitle="Dashboard">
      <div className="page-content" style={{ paddingTop: "2rem", paddingBottom: "3rem" }}>

        {/* ── Page header ─────────────────────────────── */}
        <div className="page-header">
          <div>
            <h1 className="page-title">{greeting()}, {firstName}</h1>
            <p className="page-subtitle">Here's where you stand today.</p>
          </div>
          <Link to="/interview" style={{ textDecoration: "none" }}>
            <button className="btn btn-primary" id="dashboard-new-interview">
              + New Interview
            </button>
          </Link>
        </div>

        {/* ── READINESS + STATS ───────────────────────── */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "auto 1fr",
            gap: "1.25rem",
            marginBottom: "1.5rem",
            alignItems: "stretch",
          }}
        >
          {/* Readiness card */}
          <div
            className="card"
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              textAlign: "center",
              padding: "2rem 2.5rem",
              gap: "1rem",
              minWidth: 220,
            }}
          >
            <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--text-muted)", letterSpacing: "0.07em", textTransform: "uppercase" }}>
              Interview Readiness
            </div>
            <ScoreRing score={readinessScore} size={120} />
            <div>
              <div style={{ fontSize: "0.875rem", fontWeight: 600, color: "var(--green)", marginBottom: "0.25rem" }}>
                {readinessDelta} this month
              </div>
              <p style={{
                fontSize: "0.8125rem",
                color: "var(--text-muted)",
                maxWidth: 180,
                lineHeight: 1.5,
              }}>
                {readinessInsight}
              </p>
            </div>
          </div>

          {/* Supporting stats + quick actions */}
          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            {/* Stats row */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1rem" }}>
              {supportingStats.map((stat) => (
                <div key={stat.label} className="stat-card">
                  <div className="stat-card-label">{stat.label}</div>
                  <div className="stat-card-value">{stat.value}</div>
                  <div className={`stat-card-delta${stat.positive === true ? " positive" : stat.positive === false ? " negative" : ""}`}>
                    {stat.delta}
                  </div>
                </div>
              ))}
            </div>

            {/* Quick actions */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(4, 1fr)",
                gap: "0.75rem",
              }}
            >
              {[
                { label: "Start Interview", icon: "◉", to: "/interview", primary: true },
                { label: "Upload Resume",   icon: "▤", to: "/resume",    primary: false },
                { label: "Analyze Job",     icon: "⌖", to: "/jobs",      primary: false },
                { label: "AI Coach",        icon: "✦", to: "/coaching",  primary: false },
              ].map((a) => (
                <Link key={a.label} to={a.to} style={{ textDecoration: "none" }}>
                  <div
                    style={{
                      background: a.primary ? "var(--blue-dim)" : "var(--bg-elevated)",
                      border: `1px solid ${a.primary ? "var(--blue-border)" : "var(--border-default)"}`,
                      borderRadius: "var(--r-md)",
                      padding: "0.875rem 0.75rem",
                      textAlign: "center",
                      cursor: "pointer",
                      transition: "all 0.18s ease",
                    }}
                    onMouseEnter={(e) => {
                      const el = e.currentTarget as HTMLElement;
                      el.style.transform = "translateY(-2px)";
                      el.style.borderColor = "rgba(59,130,246,0.4)";
                    }}
                    onMouseLeave={(e) => {
                      const el = e.currentTarget as HTMLElement;
                      el.style.transform = "";
                      el.style.borderColor = a.primary ? "var(--blue-border)" : "var(--border-default)";
                    }}
                  >
                    <div style={{ fontSize: "1.125rem", marginBottom: "0.375rem", color: a.primary ? "#93C5FD" : "var(--text-secondary)" }}>
                      {a.icon}
                    </div>
                    <div style={{ fontSize: "0.775rem", fontWeight: 600, color: a.primary ? "#93C5FD" : "var(--text-secondary)" }}>
                      {a.label}
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>

        {/* ── SKILLS + RECENT INTERVIEWS ──────────────── */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1.4fr", gap: "1.25rem", marginBottom: "1.25rem" }}>

          {/* Skill breakdown */}
          <div className="card" style={{ display: "flex", flexDirection: "column" }}>
            <div className="section-header">
              <div>
                <div className="section-title">Skill Breakdown</div>
                <div className="section-subtitle">Based on last 3 interviews</div>
              </div>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              {skills.map((skill) => (
                <div key={skill.name} className="skill-bar">
                  <div className="skill-bar-header">
                    <span className="skill-bar-name">{skill.name}</span>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.375rem" }}>
                      <Trend direction={skill.trend as "up" | "down" | "flat"} />
                      <span className="skill-bar-score" style={{ color: scoreColor(skill.score) }}>
                        {skill.score}%
                      </span>
                    </div>
                  </div>
                  <div className="progress-track">
                    <div
                      className={fillClass(skill.score)}
                      style={{ width: `${skill.score}%` }}
                      role="progressbar"
                      aria-valuenow={skill.score}
                      aria-valuemin={0}
                      aria-valuemax={100}
                      aria-label={skill.name}
                    />
                  </div>
                </div>
              ))}
            </div>

            {/* Recommended focus */}
            <div
              style={{
                marginTop: "1.25rem",
                background: "var(--bg-elevated)",
                border: "1px solid var(--border-default)",
                borderRadius: "var(--r-md)",
                padding: "0.875rem 1rem",
              }}
            >
              <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "0.375rem" }}>
                Recommended Focus
              </div>
              <div style={{ fontSize: "0.875rem", fontWeight: 600, color: "var(--text-primary)", marginBottom: "0.25rem" }}>
                {weakestSkill.name}
              </div>
              <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: "0.75rem", lineHeight: 1.5 }}>
                Practice 3 {weakestSkill.name.toLowerCase()} sessions this week to improve your score.
              </p>
              <Link to="/coaching" style={{ textDecoration: "none" }}>
                <button className="btn btn-primary btn-sm" id="focus-practice-btn">
                  Start Practice
                </button>
              </Link>
            </div>
          </div>

          {/* Recent interviews */}
          <div className="card" style={{ display: "flex", flexDirection: "column" }}>
            <div className="section-header">
              <div>
                <div className="section-title">Recent Interviews</div>
                <div className="section-subtitle">Your last 3 sessions</div>
              </div>
              <Link to="/interview" className="section-action">View all →</Link>
            </div>

            {recentInterviews.length > 0 ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                {recentInterviews.map((iv) => (
                  <div
                    key={iv.id}
                    className="interview-card"
                    onClick={() => navigate("/interview")}
                    role="button"
                    tabIndex={0}
                    aria-label={`${iv.role} — Score ${iv.score}%`}
                    onKeyDown={(e) => e.key === "Enter" && navigate("/interview")}
                  >
                    <div style={{ minWidth: 0 }}>
                      <div className="interview-card-role">{iv.role}</div>
                      <div className="interview-card-meta">{iv.type} · {iv.date}</div>
                    </div>
                    <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: "0.25rem", flexShrink: 0 }}>
                      <div className="interview-card-score" style={{ color: scoreColor(iv.score) }}>
                        {iv.score}%
                      </div>
                      <div className="interview-card-score-label">Score</div>
                      <button
                        className="btn btn-ghost btn-sm"
                        onClick={(e) => { e.stopPropagation(); navigate("/interview"); }}
                        aria-label={`View feedback for ${iv.role}`}
                        style={{ fontSize: "0.725rem", padding: "0.25rem 0.5rem", marginTop: "0.125rem" }}
                      >
                        View Feedback →
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-state-icon">◉</div>
                <div className="empty-state-title">No interviews yet</div>
                <p className="empty-state-desc">Your first practice session will appear here.</p>
                <Link to="/interview" style={{ textDecoration: "none" }}>
                  <button className="btn btn-primary btn-sm" id="empty-start-interview">
                    Start Your First Interview
                  </button>
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* ── AI COACH BANNER ─────────────────────────── */}
        <div
          style={{
            background: "linear-gradient(135deg, rgba(139,92,246,0.1), rgba(59,130,246,0.06))",
            border: "1px solid rgba(139,92,246,0.18)",
            borderRadius: "var(--r-lg)",
            padding: "1.375rem 1.75rem",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: "1.5rem",
            flexWrap: "wrap",
          }}
        >
          <div>
            <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--violet)", letterSpacing: "0.07em", textTransform: "uppercase", marginBottom: "0.375rem" }}>
              AI Coach Insight
            </div>
            <h3 style={{ fontSize: "1rem", fontWeight: 700, color: "var(--text-primary)", marginBottom: "0.25rem" }}>
              {weakestSkill.name} is your current focus area
            </h3>
            <p style={{ fontSize: "0.84375rem", color: "var(--text-muted)", maxWidth: 480 }}>
              Your coach has prepared a personalized 7-day improvement plan based on your recent sessions.
            </p>
          </div>
          <Link to="/coaching" style={{ textDecoration: "none", flexShrink: 0 }}>
            <button className="btn btn-secondary" id="coach-banner-btn">
              View My Plan →
            </button>
          </Link>
        </div>

      </div>
    </AppShell>
  );
}
