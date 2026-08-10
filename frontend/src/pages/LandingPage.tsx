import { Link } from "react-router-dom";
import Navbar from "../components/layout/Navbar";

/* ---- Feature cards data ---------------------------------- */
const features = [
  {
    icon: "🧠",
    title: "Resume Intelligence",
    description:
      "AI extracts every skill, project, and achievement from your resume and builds a structured candidate profile.",
    phase: "Phase 2",
    color: "#3b82f6",
  },
  {
    icon: "🎯",
    title: "Job Matching",
    description:
      "Upload a job description and instantly see matched skills, gaps, and tailored interview strategies.",
    phase: "Phase 3",
    color: "#06b6d4",
  },
  {
    icon: "🤖",
    title: "Adaptive Interview Agent",
    description:
      "LangGraph-powered AI that adjusts difficulty, probes weak areas, and generates contextual follow-ups in real time.",
    phase: "Phase 7",
    color: "#8b5cf6",
  },
  {
    icon: "🗣️",
    title: "3D AI Interviewer",
    description:
      "Interview with a lifelike 3D avatar that speaks, listens, and reacts — powered by TTS and lip synchronization.",
    phase: "Phase 12",
    color: "#06b6d4",
  },
  {
    icon: "✅",
    title: "Skill Verification",
    description:
      "Claims on your resume are verified through targeted technical questions. Observed vs claimed skill analysis.",
    phase: "Phase 10",
    color: "#3b82f6",
  },
  {
    icon: "📊",
    title: "Interview Readiness Score",
    description:
      "Multi-dimensional scoring across technical accuracy, communication, behavioral skills, and problem solving.",
    phase: "Phase 14",
    color: "#8b5cf6",
  },
  {
    icon: "💡",
    title: "AI Career Coach",
    description:
      "Evidence-based personalized improvement plan with recommended topics, practice questions, and timelines.",
    phase: "Phase 15",
    color: "#06b6d4",
  },
  {
    icon: "📈",
    title: "Progress Tracking",
    description:
      "Track your growth across interviews. See score trends, skill improvements, and weak areas over time.",
    phase: "Phase 16",
    color: "#3b82f6",
  },
];

/* ---- Workflow steps -------------------------------------- */
const workflowSteps = [
  { step: "01", label: "Upload Resume", description: "PDF parsing + structured extraction" },
  { step: "02", label: "Add Job Description", description: "Skill matching & gap analysis" },
  { step: "03", label: "Configure Interview", description: "Type, difficulty, and duration" },
  { step: "04", label: "Interview with AI", description: "Voice + 3D adaptive session" },
  { step: "05", label: "Get Evaluated", description: "Multi-dimensional scoring" },
  { step: "06", label: "Coach & Improve", description: "Personalized practice plan" },
];

/* ---- Stats ----------------------------------------------- */
const stats = [
  { value: "10+", label: "Interview Types" },
  { value: "24", label: "Development Phases" },
  { value: "AI", label: "Adaptive Engine" },
  { value: "3D", label: "Avatar Interface" },
];

const LandingPage = () => {
  return (
    <div style={{ minHeight: "100vh", background: "#050c1a", overflowX: "hidden" }}>
      <Navbar />

      {/* ---- HERO SECTION ----------------------------------- */}
      <section
        style={{
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "8rem 2rem 4rem",
          position: "relative",
          textAlign: "center",
        }}
      >
        {/* Background orbs */}
        <div
          style={{
            position: "absolute",
            top: "15%",
            left: "20%",
            width: "500px",
            height: "500px",
            borderRadius: "50%",
            background: "radial-gradient(circle, rgba(37, 99, 235, 0.12) 0%, transparent 70%)",
            pointerEvents: "none",
          }}
        />
        <div
          style={{
            position: "absolute",
            top: "30%",
            right: "15%",
            width: "400px",
            height: "400px",
            borderRadius: "50%",
            background: "radial-gradient(circle, rgba(6, 182, 212, 0.1) 0%, transparent 70%)",
            pointerEvents: "none",
          }}
        />
        <div
          style={{
            position: "absolute",
            bottom: "20%",
            left: "35%",
            width: "300px",
            height: "300px",
            borderRadius: "50%",
            background: "radial-gradient(circle, rgba(139, 92, 246, 0.08) 0%, transparent 70%)",
            pointerEvents: "none",
          }}
        />

        {/* Badge */}
        <div
          className="animate-fade-in-up"
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "0.5rem",
            background: "rgba(37, 99, 235, 0.12)",
            border: "1px solid rgba(37, 99, 235, 0.25)",
            borderRadius: "100px",
            padding: "0.375rem 1.25rem",
            marginBottom: "2rem",
          }}
        >
          <div
            className="pulse-dot"
            style={{
              width: "7px",
              height: "7px",
              borderRadius: "50%",
              background: "#22d3ee",
            }}
          />
          <span
            style={{
              fontSize: "0.8rem",
              fontWeight: 600,
              color: "#60a5fa",
              letterSpacing: "0.06em",
              textTransform: "uppercase" as const,
            }}
          >
            AI-Powered Interview Platform
          </span>
        </div>

        {/* Headline */}
        <h1
          className="animate-fade-in-up-delay-1"
          style={{
            fontSize: "clamp(2.75rem, 6vw, 5rem)",
            fontWeight: 900,
            lineHeight: 1.05,
            letterSpacing: "-0.04em",
            maxWidth: "820px",
            marginBottom: "1.5rem",
          }}
        >
          <span style={{ color: "white" }}>Master Every </span>
          <span className="gradient-text">Interview</span>
          <br />
          <span style={{ color: "white" }}>with Adaptive </span>
          <span className="gradient-text-blue">AI Coaching</span>
        </h1>

        {/* Subheading */}
        <p
          className="animate-fade-in-up-delay-2"
          style={{
            fontSize: "1.2rem",
            color: "rgba(255,255,255,0.55)",
            maxWidth: "600px",
            lineHeight: 1.65,
            marginBottom: "3rem",
          }}
        >
          Intervia analyzes your resume and target job, then conducts a
          personalized adaptive interview through a 3D AI interviewer.
          Get evidence-based feedback and a custom improvement plan.
        </p>

        {/* CTA buttons */}
        <div
          className="animate-fade-in-up-delay-3"
          style={{ display: "flex", gap: "1rem", flexWrap: "wrap" as const, justifyContent: "center" }}
        >
          <Link to="/register" style={{ textDecoration: "none" }}>
            <button
              className="btn-primary"
              style={{ fontSize: "1rem", padding: "0.875rem 2.25rem" }}
            >
              Start Your Interview →
            </button>
          </Link>
          <Link to="/dashboard" style={{ textDecoration: "none" }}>
            <button
              className="btn-secondary"
              style={{ fontSize: "1rem", padding: "0.875rem 2.25rem" }}
            >
              View Dashboard
            </button>
          </Link>
        </div>

        {/* Stats row */}
        <div
          className="animate-fade-in-up-delay-4"
          style={{
            display: "flex",
            gap: "3rem",
            marginTop: "4.5rem",
            flexWrap: "wrap" as const,
            justifyContent: "center",
          }}
        >
          {stats.map((stat) => (
            <div key={stat.label} style={{ textAlign: "center" }}>
              <div
                className="gradient-text"
                style={{
                  fontSize: "2rem",
                  fontWeight: 800,
                  letterSpacing: "-0.03em",
                }}
              >
                {stat.value}
              </div>
              <div
                style={{
                  fontSize: "0.8rem",
                  color: "rgba(255,255,255,0.4)",
                  fontWeight: 500,
                  marginTop: "0.25rem",
                  textTransform: "uppercase" as const,
                  letterSpacing: "0.06em",
                }}
              >
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ---- WORKFLOW SECTION ------------------------------- */}
      <section
        style={{
          padding: "5rem 2rem",
          maxWidth: "1100px",
          margin: "0 auto",
        }}
      >
        {/* Section header */}
        <div style={{ textAlign: "center", marginBottom: "3.5rem" }}>
          <p
            style={{
              fontSize: "0.75rem",
              fontWeight: 700,
              color: "#06b6d4",
              letterSpacing: "0.1em",
              textTransform: "uppercase" as const,
              marginBottom: "0.75rem",
            }}
          >
            How It Works
          </p>
          <h2
            style={{
              fontSize: "clamp(1.75rem, 3vw, 2.75rem)",
              fontWeight: 800,
              color: "white",
              letterSpacing: "-0.03em",
              lineHeight: 1.15,
            }}
          >
            From Resume to{" "}
            <span className="gradient-text">Interview Ready</span>
          </h2>
        </div>

        {/* Steps grid */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
            gap: "1.25rem",
          }}
        >
          {workflowSteps.map((item, idx) => (
            <div
              key={item.step}
              className="card"
              style={{
                display: "flex",
                gap: "1.25rem",
                alignItems: "flex-start",
                animationDelay: `${idx * 0.08}s`,
              }}
            >
              <div
                style={{
                  minWidth: "48px",
                  height: "48px",
                  borderRadius: "12px",
                  background: "linear-gradient(135deg, rgba(37,99,235,0.2), rgba(6,182,212,0.2))",
                  border: "1px solid rgba(37,99,235,0.3)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "0.8rem",
                  fontWeight: 800,
                  color: "#60a5fa",
                  letterSpacing: "0.05em",
                }}
              >
                {item.step}
              </div>
              <div>
                <h3
                  style={{
                    fontSize: "1rem",
                    fontWeight: 700,
                    color: "white",
                    marginBottom: "0.375rem",
                    letterSpacing: "-0.01em",
                  }}
                >
                  {item.label}
                </h3>
                <p
                  style={{
                    fontSize: "0.85rem",
                    color: "rgba(255,255,255,0.45)",
                    lineHeight: 1.5,
                  }}
                >
                  {item.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ---- FEATURES SECTION ------------------------------ */}
      <section
        style={{
          padding: "5rem 2rem",
          maxWidth: "1200px",
          margin: "0 auto",
        }}
      >
        {/* Section header */}
        <div style={{ textAlign: "center", marginBottom: "3.5rem" }}>
          <p
            style={{
              fontSize: "0.75rem",
              fontWeight: 700,
              color: "#8b5cf6",
              letterSpacing: "0.1em",
              textTransform: "uppercase" as const,
              marginBottom: "0.75rem",
            }}
          >
            Platform Features
          </p>
          <h2
            style={{
              fontSize: "clamp(1.75rem, 3vw, 2.75rem)",
              fontWeight: 800,
              color: "white",
              letterSpacing: "-0.03em",
            }}
          >
            Everything You Need to{" "}
            <span className="gradient-text">Ace Your Interview</span>
          </h2>
        </div>

        {/* Features grid */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
            gap: "1.25rem",
          }}
        >
          {features.map((feature) => (
            <div key={feature.title} className="card glass-hover">
              {/* Icon + badge row */}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  marginBottom: "1rem",
                }}
              >
                <div
                  style={{
                    width: "46px",
                    height: "46px",
                    borderRadius: "12px",
                    background: `${feature.color}1a`,
                    border: `1px solid ${feature.color}33`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: "1.375rem",
                  }}
                >
                  {feature.icon}
                </div>
                <span
                  style={{
                    fontSize: "0.7rem",
                    fontWeight: 600,
                    color: feature.color,
                    background: `${feature.color}18`,
                    border: `1px solid ${feature.color}30`,
                    borderRadius: "100px",
                    padding: "0.25rem 0.75rem",
                    letterSpacing: "0.04em",
                    textTransform: "uppercase" as const,
                  }}
                >
                  {feature.phase}
                </span>
              </div>

              {/* Text */}
              <h3
                style={{
                  fontSize: "1.05rem",
                  fontWeight: 700,
                  color: "white",
                  marginBottom: "0.5rem",
                  letterSpacing: "-0.01em",
                }}
              >
                {feature.title}
              </h3>
              <p
                style={{
                  fontSize: "0.875rem",
                  color: "rgba(255,255,255,0.48)",
                  lineHeight: 1.6,
                }}
              >
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* ---- TECH STACK SECTION ----------------------------- */}
      <section
        style={{
          padding: "4rem 2rem",
          borderTop: "1px solid rgba(255,255,255,0.06)",
          borderBottom: "1px solid rgba(255,255,255,0.06)",
          background: "rgba(255,255,255,0.015)",
        }}
      >
        <div style={{ maxWidth: "900px", margin: "0 auto", textAlign: "center" }}>
          <p
            style={{
              fontSize: "0.75rem",
              fontWeight: 600,
              color: "rgba(255,255,255,0.3)",
              letterSpacing: "0.1em",
              textTransform: "uppercase" as const,
              marginBottom: "2rem",
            }}
          >
            Built with industry-grade technology
          </p>
          <div
            style={{
              display: "flex",
              flexWrap: "wrap" as const,
              gap: "0.75rem",
              justifyContent: "center",
            }}
          >
            {[
              "React", "TypeScript", "Vite", "Tailwind CSS",
              "Three.js", "React Three Fiber", "Python",
              "FastAPI", "LangGraph", "Gemini AI",
              "PostgreSQL", "pgvector", "Supabase",
              "WebSockets", "Docker",
            ].map((tech) => (
              <span
                key={tech}
                style={{
                  padding: "0.375rem 1rem",
                  borderRadius: "100px",
                  background: "rgba(255,255,255,0.05)",
                  border: "1px solid rgba(255,255,255,0.08)",
                  fontSize: "0.8rem",
                  color: "rgba(255,255,255,0.6)",
                  fontWeight: 500,
                  transition: "all 0.2s ease",
                }}
                onMouseEnter={(e) => {
                  const el = e.currentTarget as HTMLElement;
                  el.style.background = "rgba(255,255,255,0.1)";
                  el.style.color = "white";
                }}
                onMouseLeave={(e) => {
                  const el = e.currentTarget as HTMLElement;
                  el.style.background = "rgba(255,255,255,0.05)";
                  el.style.color = "rgba(255,255,255,0.6)";
                }}
              >
                {tech}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* ---- CTA SECTION ------------------------------------ */}
      <section
        style={{
          padding: "7rem 2rem",
          textAlign: "center",
          position: "relative",
          overflow: "hidden",
        }}
      >
        {/* Background glow */}
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            width: "600px",
            height: "300px",
            borderRadius: "50%",
            background: "radial-gradient(ellipse, rgba(37,99,235,0.15) 0%, transparent 70%)",
            pointerEvents: "none",
          }}
        />

        <div style={{ position: "relative", zIndex: 1 }}>
          <h2
            style={{
              fontSize: "clamp(2rem, 4vw, 3.5rem)",
              fontWeight: 900,
              color: "white",
              letterSpacing: "-0.04em",
              lineHeight: 1.1,
              marginBottom: "1.25rem",
            }}
          >
            Ready to Become{" "}
            <span className="gradient-text">Interview Ready?</span>
          </h2>
          <p
            style={{
              fontSize: "1.1rem",
              color: "rgba(255,255,255,0.5)",
              marginBottom: "2.5rem",
              maxWidth: "480px",
              margin: "0 auto 2.5rem",
              lineHeight: 1.6,
            }}
          >
            Upload your resume, connect to a job description, and start
            your first adaptive AI interview session today.
          </p>
          <Link to="/register" style={{ textDecoration: "none" }}>
            <button
              className="btn-primary"
              style={{
                fontSize: "1.05rem",
                padding: "1rem 2.75rem",
              }}
            >
              Get Started Free →
            </button>
          </Link>
        </div>
      </section>

      {/* ---- FOOTER ----------------------------------------- */}
      <footer
        style={{
          borderTop: "1px solid rgba(255,255,255,0.06)",
          padding: "2rem",
          textAlign: "center",
        }}
      >
        <p style={{ color: "rgba(255,255,255,0.25)", fontSize: "0.8rem" }}>
          © 2025 Intervia — AI-Powered Interview Platform. Built with ❤️ using React, FastAPI & LangGraph.
        </p>
      </footer>
    </div>
  );
};

export default LandingPage;
