/**
 * frontend/src/pages/LandingPage.tsx
 * Redesigned landing page — clean, modern SaaS aesthetic.
 * Preserves all existing routing and links.
 */

import { Link } from "react-router-dom";
import Navbar from "../components/layout/Navbar";

/* ── Feature data ──────────────────────────────────────── */
const features = [
  {
    icon: "⬡",
    title: "Resume Intelligence",
    description: "Upload your resume and watch AI extract every skill, project, and achievement to build a structured candidate profile.",
    color: "var(--blue)",
  },
  {
    icon: "⊕",
    title: "Adaptive Interviews",
    description: "Questions adapt to your answers in real time. Every session feels like a real interview — because it is.",
    color: "var(--violet)",
  },
  {
    icon: "◈",
    title: "Smart Evaluation",
    description: "Get scored across technical knowledge, communication, problem-solving, and confidence — not just right or wrong.",
    color: "var(--cyan)",
  },
  {
    icon: "✦",
    title: "AI Coach",
    description: "Receive a personalized improvement plan with specific topics, practice questions, and timelines — not generic advice.",
    color: "var(--green)",
  },
  {
    icon: "⌖",
    title: "Job Matching",
    description: "Paste a job description. See exactly which skills match your profile and which gaps to close before the interview.",
    color: "var(--amber)",
  },
  {
    icon: "◷",
    title: "Progress Tracking",
    description: "Track readiness over time. See your scores trend upward as you practice and improve across sessions.",
    color: "var(--blue)",
  },
];

/* ── Journey steps ─────────────────────────────────────── */
const steps = [
  { n: "01", icon: "▤", title: "Upload Resume",        desc: "AI parses your experience and skills" },
  { n: "02", icon: "⌖", title: "Match Your Role",      desc: "Identify skill gaps for your target job" },
  { n: "03", icon: "⚙", title: "Configure Interview",  desc: "Choose type, difficulty, and duration" },
  { n: "04", icon: "◉", title: "Practice With AI",     desc: "Adaptive voice or text-based session" },
  { n: "05", icon: "◈", title: "Get Feedback",         desc: "Scored breakdown with clear insights" },
  { n: "06", icon: "✦", title: "Improve",              desc: "Personalized coaching plan to grow" },
];

/* ── Trust items ────────────────────────────────────────── */
const trustItems = [
  "Resume-aware questions",
  "Adaptive difficulty",
  "Instant feedback",
  "Personalized coaching",
];

/* ── Mock dashboard preview ──────────────────────────────── */
const MockDashboard = () => (
  <div
    aria-hidden="true"
    style={{
      background: "var(--bg-surface)",
      border: "1px solid var(--border-default)",
      borderRadius: "var(--r-xl)",
      padding: "1.25rem",
      width: "100%",
      maxWidth: 440,
      boxShadow: "var(--shadow-lg)",
      overflow: "hidden",
    }}
  >
    {/* Top bar */}
    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1rem" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
        <div style={{ width: 24, height: 24, borderRadius: 6, background: "var(--blue)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "0.75rem", fontWeight: 800, color: "white" }}>I</div>
        <span style={{ fontSize: "0.8125rem", fontWeight: 700, color: "var(--text-primary)" }}>Intervia</span>
      </div>
      <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Dashboard</div>
    </div>

    {/* Readiness score */}
    <div style={{ background: "var(--bg-elevated)", border: "1px solid var(--border-default)", borderRadius: "var(--r-lg)", padding: "1.125rem", marginBottom: "0.875rem" }}>
      <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: "0.75rem", fontWeight: 500 }}>Interview Readiness</div>
      <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
        {/* Mini ring */}
        <svg width="56" height="56" viewBox="0 0 56 56">
          <circle cx="28" cy="28" r="22" fill="none" stroke="rgba(255,255,255,0.07)" strokeWidth="5"/>
          <circle cx="28" cy="28" r="22" fill="none" stroke="var(--blue)" strokeWidth="5"
            strokeDasharray={`${2 * Math.PI * 22 * 0.72} ${2 * Math.PI * 22}`}
            strokeLinecap="round" transform="rotate(-90 28 28)"/>
          <text x="28" y="32" textAnchor="middle" fill="var(--text-primary)" fontSize="11" fontWeight="800">72%</text>
        </svg>
        <div>
          <div style={{ fontSize: "1.25rem", fontWeight: 800, color: "var(--text-primary)", letterSpacing: "-0.03em" }}>72%</div>
          <div style={{ fontSize: "0.75rem", color: "var(--green)", fontWeight: 500 }}>↑ 8% this month</div>
          <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", marginTop: "0.125rem" }}>3 interviews completed</div>
        </div>
      </div>
    </div>

    {/* Skill bars */}
    <div style={{ display: "flex", flexDirection: "column", gap: "0.625rem", marginBottom: "0.875rem" }}>
      {[
        { name: "React & TypeScript", score: 90, color: "var(--blue)" },
        { name: "Problem Solving", score: 82, color: "var(--violet)" },
        { name: "Communication", score: 68, color: "var(--cyan)" },
        { name: "System Design", score: 55, color: "var(--amber)" },
      ].map((s) => (
        <div key={s.name}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.25rem" }}>
            <span style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>{s.name}</span>
            <span style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--text-primary)" }}>{s.score}%</span>
          </div>
          <div style={{ height: 4, background: "rgba(255,255,255,0.07)", borderRadius: 100, overflow: "hidden" }}>
            <div style={{ height: "100%", width: `${s.score}%`, background: s.color, borderRadius: 100 }}/>
          </div>
        </div>
      ))}
    </div>

    {/* Recent */}
    <div style={{ background: "var(--bg-elevated)", border: "1px solid var(--border-default)", borderRadius: "var(--r-md)", padding: "0.75rem 1rem", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
      <div>
        <div style={{ fontSize: "0.8125rem", fontWeight: 600, color: "var(--text-primary)" }}>Frontend Developer</div>
        <div style={{ fontSize: "0.725rem", color: "var(--text-muted)" }}>Technical · Sep 29</div>
      </div>
      <span style={{ fontSize: "1rem", fontWeight: 800, color: "var(--green)" }}>78%</span>
    </div>
  </div>
);

/* ── Main Component ─────────────────────────────────────── */
const LandingPage = () => {
  return (
    <div style={{ minHeight: "100vh", background: "var(--bg-base)", overflowX: "hidden" }}>
      <Navbar />

      {/* ── HERO ─────────────────────────────────────────── */}
      <section
        style={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          padding: "5rem 2rem 4rem",
          maxWidth: 1200,
          margin: "0 auto",
        }}
      >
        {/* Left — copy */}
        <div style={{ flex: "1 1 500px", maxWidth: 560 }}>
          {/* Badge */}
          <div
            className="badge badge-blue anim-fade-up"
            style={{ marginBottom: "1.75rem", display: "inline-flex" }}
          >
            <span className="pulse-dot" style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--cyan)", flexShrink: 0 }}/>
            AI-Powered Interview Preparation
          </div>

          {/* Headline */}
          <h1
            className="anim-fade-up anim-delay-1"
            style={{
              fontSize: "clamp(2.25rem, 5vw, 3.625rem)",
              fontWeight: 800,
              lineHeight: 1.08,
              letterSpacing: "-0.04em",
              marginBottom: "1.25rem",
            }}
          >
            Practice Smarter.{" "}
            <span className="text-gradient">Interview Better.</span>
          </h1>

          {/* Supporting text */}
          <p
            className="anim-fade-up anim-delay-2"
            style={{
              fontSize: "1.0625rem",
              color: "var(--text-secondary)",
              lineHeight: 1.65,
              maxWidth: 460,
              marginBottom: "2rem",
            }}
          >
            Turn your resume and target role into personalized AI interviews,
            instant feedback, and a focused coaching plan.
          </p>

          {/* Trust row */}
          <div
            className="anim-fade-up anim-delay-3"
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: "0.75rem",
              marginBottom: "2.25rem",
            }}
          >
            {trustItems.map((item) => (
              <div
                key={item}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "0.375rem",
                  fontSize: "0.8375rem",
                  color: "var(--text-secondary)",
                  fontWeight: 500,
                }}
              >
                <span style={{ color: "var(--green)", fontWeight: 700 }}>✓</span>
                {item}
              </div>
            ))}
          </div>

          {/* CTA buttons */}
          <div
            className="anim-fade-up anim-delay-4"
            style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}
          >
            <Link to="/register" style={{ textDecoration: "none" }}>
              <button className="btn btn-primary btn-xl" id="hero-cta-primary">
                Start Practicing
              </button>
            </Link>
            <a href="#how-it-works" style={{ textDecoration: "none" }}>
              <button className="btn btn-secondary btn-xl" id="hero-cta-secondary">
                See How It Works
              </button>
            </a>
          </div>
        </div>

        {/* Right — mock dashboard */}
        <div
          className="anim-fade-up anim-delay-5"
          style={{
            flex: "1 1 400px",
            display: "flex",
            justifyContent: "center",
            paddingLeft: "3rem",
          }}
        >
          <MockDashboard />
        </div>
      </section>

      {/* ── HOW IT WORKS ─────────────────────────────────── */}
      <section
        id="how-it-works"
        style={{
          padding: "5rem 2rem",
          borderTop: "1px solid var(--border-subtle)",
          background: "var(--bg-surface)",
        }}
      >
        <div style={{ maxWidth: 1100, margin: "0 auto" }}>
          {/* Header */}
          <div style={{ textAlign: "center", marginBottom: "3.5rem" }}>
            <p style={{
              fontSize: "0.75rem",
              fontWeight: 700,
              color: "var(--cyan)",
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              marginBottom: "0.625rem",
            }}>
              The Journey
            </p>
            <h2 style={{
              fontSize: "clamp(1.625rem, 3vw, 2.25rem)",
              fontWeight: 800,
              letterSpacing: "-0.03em",
            }}>
              From Resume to{" "}
              <span className="text-gradient-blue">Interview Ready</span>
            </h2>
          </div>

          {/* Steps */}
          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
            gap: "1rem",
            position: "relative",
          }}>
            {steps.map((step, i) => (
              <div
                key={step.n}
                style={{
                  position: "relative",
                  background: "var(--bg-elevated)",
                  border: "1px solid var(--border-default)",
                  borderRadius: "var(--r-lg)",
                  padding: "1.25rem 1rem",
                  textAlign: "center",
                  transition: "border-color 0.2s, transform 0.2s",
                  animationDelay: `${i * 0.06}s`,
                }}
                className="anim-fade-up"
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLElement).style.borderColor = "rgba(59,130,246,0.3)";
                  (e.currentTarget as HTMLElement).style.transform = "translateY(-3px)";
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLElement).style.borderColor = "var(--border-default)";
                  (e.currentTarget as HTMLElement).style.transform = "translateY(0)";
                }}
              >
                {/* Number */}
                <div style={{
                  fontSize: "0.6875rem",
                  fontWeight: 700,
                  color: "var(--blue)",
                  letterSpacing: "0.06em",
                  marginBottom: "0.625rem",
                }}>
                  {step.n}
                </div>

                {/* Icon */}
                <div style={{
                  width: 40, height: 40,
                  borderRadius: "var(--r-md)",
                  background: "var(--blue-dim)",
                  border: "1px solid var(--blue-border)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "1.125rem",
                  color: "#93C5FD",
                  margin: "0 auto 0.75rem",
                }}>
                  {step.icon}
                </div>

                <div style={{
                  fontSize: "0.875rem",
                  fontWeight: 700,
                  color: "var(--text-primary)",
                  marginBottom: "0.3rem",
                  letterSpacing: "-0.01em",
                }}>
                  {step.title}
                </div>
                <div style={{
                  fontSize: "0.775rem",
                  color: "var(--text-muted)",
                  lineHeight: 1.45,
                }}>
                  {step.desc}
                </div>

                {/* Connector dot */}
                {i < steps.length - 1 && (
                  <div style={{
                    position: "absolute",
                    top: "50%",
                    right: -8,
                    transform: "translateY(-50%)",
                    width: 14, height: 14,
                    borderRadius: "50%",
                    background: "var(--bg-surface)",
                    border: "2px solid var(--border-strong)",
                    zIndex: 1,
                  }}/>
                )}
              </div>
            ))}
          </div>

          {/* CTA below steps */}
          <div style={{ textAlign: "center", marginTop: "2.5rem" }}>
            <Link to="/register" style={{ textDecoration: "none" }}>
              <button className="btn btn-primary btn-lg" id="journey-cta">
                Start Your First Session
              </button>
            </Link>
          </div>
        </div>
      </section>

      {/* ── FEATURES ─────────────────────────────────────── */}
      <section
        id="features"
        style={{ padding: "5rem 2rem" }}
      >
        <div style={{ maxWidth: 1100, margin: "0 auto" }}>
          {/* Header */}
          <div style={{ textAlign: "center", marginBottom: "3rem" }}>
            <p style={{
              fontSize: "0.75rem",
              fontWeight: 700,
              color: "var(--violet)",
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              marginBottom: "0.625rem",
            }}>
              What You Get
            </p>
            <h2 style={{
              fontSize: "clamp(1.625rem, 3vw, 2.25rem)",
              fontWeight: 800,
              letterSpacing: "-0.03em",
            }}>
              Everything to{" "}
              <span className="text-gradient">Ace Your Interview</span>
            </h2>
          </div>

          {/* Feature grid */}
          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(310px, 1fr))",
            gap: "1rem",
          }}>
            {features.map((f, i) => (
              <div
                key={f.title}
                className="card card-hover anim-fade-up"
                style={{ animationDelay: `${i * 0.07}s` }}
              >
                {/* Icon */}
                <div style={{
                  width: 40, height: 40,
                  borderRadius: "var(--r-md)",
                  background: `${f.color}18`,
                  border: `1px solid ${f.color}30`,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "1.125rem",
                  color: f.color,
                  marginBottom: "1rem",
                }}>
                  {f.icon}
                </div>

                <h3 style={{
                  fontSize: "0.9375rem",
                  fontWeight: 700,
                  color: "var(--text-primary)",
                  marginBottom: "0.4rem",
                  letterSpacing: "-0.01em",
                }}>
                  {f.title}
                </h3>
                <p style={{
                  fontSize: "0.84375rem",
                  color: "var(--text-secondary)",
                  lineHeight: 1.6,
                }}>
                  {f.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── TECH STRIP ───────────────────────────────────── */}
      <section
        style={{
          padding: "3rem 2rem",
          borderTop: "1px solid var(--border-subtle)",
          borderBottom: "1px solid var(--border-subtle)",
          background: "var(--bg-surface)",
        }}
      >
        <div style={{ maxWidth: 900, margin: "0 auto", textAlign: "center" }}>
          <p style={{
            fontSize: "0.75rem",
            fontWeight: 600,
            color: "var(--text-muted)",
            letterSpacing: "0.08em",
            textTransform: "uppercase",
            marginBottom: "1.5rem",
          }}>
            Built with production-grade technology
          </p>
          <div style={{
            display: "flex",
            flexWrap: "wrap",
            gap: "0.625rem",
            justifyContent: "center",
          }}>
            {[
              "React", "TypeScript", "FastAPI", "LangGraph",
              "Gemini AI", "PostgreSQL", "pgvector", "Supabase",
              "WebSockets", "Docker",
            ].map((tech) => (
              <span
                key={tech}
                className="badge badge-muted"
                style={{ fontSize: "0.8125rem", padding: "0.3125rem 0.875rem" }}
              >
                {tech}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ──────────────────────────────────────────── */}
      <section style={{ padding: "6rem 2rem", textAlign: "center" }}>
        <div style={{ maxWidth: 560, margin: "0 auto" }}>
          <h2 style={{
            fontSize: "clamp(1.875rem, 4vw, 2.75rem)",
            fontWeight: 800,
            letterSpacing: "-0.04em",
            lineHeight: 1.1,
            marginBottom: "1rem",
          }}>
            Ready to become{" "}
            <span className="text-gradient">interview ready?</span>
          </h2>
          <p style={{
            fontSize: "1rem",
            color: "var(--text-secondary)",
            marginBottom: "2.25rem",
            lineHeight: 1.65,
          }}>
            Upload your resume, connect to a job description, and start your
            first adaptive AI interview session today.
          </p>
          <Link to="/register" style={{ textDecoration: "none" }}>
            <button className="btn btn-primary btn-xl" id="bottom-cta">
              Get Started Free →
            </button>
          </Link>
        </div>
      </section>

      {/* ── FOOTER ────────────────────────────────────────── */}
      <footer style={{
        borderTop: "1px solid var(--border-subtle)",
        padding: "1.75rem 2rem",
        textAlign: "center",
      }}>
        <p style={{ color: "var(--text-muted)", fontSize: "0.8125rem" }}>
          © 2026 Intervia — AI-Powered Interview Preparation
        </p>
      </footer>
    </div>
  );
};

export default LandingPage;
