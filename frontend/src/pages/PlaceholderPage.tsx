/**
 * frontend/src/pages/PlaceholderPage.tsx
 * Redesigned coming-soon pages — useful, informative, not dead-ends.
 * Preserves all props interface.
 */

import { Link } from "react-router-dom";
import AppShell from "../components/layout/AppShell";

interface PlaceholderPageProps {
  title: string;
  description: string;
  phase: string;
}

/* ── Page-specific content ─────────────────────────────── */
const pageContent: Record<string, {
  heading: string;
  subtext: string;
  cta: string;
  ctaTo: string;
  preview?: { label: string; desc: string }[];
}> = {
  "Resume Intelligence": {
    heading: "Build Your Interview Profile",
    subtext: "Upload your resume to generate personalized interview questions and identify the skills recruiters are most likely to evaluate.",
    cta: "Start a Practice Interview",
    ctaTo: "/interview",
    preview: [
      { label: "Skill Extraction",    desc: "AI parses every skill and experience from your PDF" },
      { label: "Candidate Profile",   desc: "Structured profile built automatically from your resume" },
      { label: "Question Generation", desc: "Every interview question tailored to your actual experience" },
    ],
  },
  "Job Matching": {
    heading: "Find Your Interview Target",
    subtext: "Paste a job description to instantly see which skills you match, which gaps to close, and how to prepare specifically for that role.",
    cta: "Practice Without Job Match",
    ctaTo: "/interview",
    preview: [
      { label: "Skill Detection",   desc: "AI identifies required skills from the job description" },
      { label: "Gap Analysis",      desc: "See exactly what to learn before the interview" },
      { label: "Targeted Practice", desc: "Questions focused on the specific role requirements" },
    ],
  },
  "AI Coach": {
    heading: "Your AI Mentor",
    subtext: "After each interview, your coach analyzes where you struggled and creates a focused, actionable improvement plan — not generic advice.",
    cta: "Try an Interview First",
    ctaTo: "/interview",
    preview: [
      { label: "Personalized Plan",      desc: "7-day improvement roadmap based on your weak areas" },
      { label: "Practice Questions",     desc: "Curated questions targeting your specific gaps" },
      { label: "Progress Tracking",      desc: "Watch your readiness score climb over time" },
    ],
  },
  "Profile": {
    heading: "Your Account",
    subtext: "Manage your profile, update your preferences, and configure your interview settings.",
    cta: "Back to Dashboard",
    ctaTo: "/dashboard",
    preview: [
      { label: "Account Settings", desc: "Update your name, email, and password" },
      { label: "Interview Preferences", desc: "Set default interview type and difficulty" },
      { label: "Notification Settings", desc: "Choose how Intervia keeps you on track" },
    ],
  },
};

const defaultContent = {
  heading: "Coming Soon",
  subtext: "This feature is being built. Practice interviews are available right now.",
  cta: "Start Practicing",
  ctaTo: "/interview",
  preview: [] as { label: string; desc: string }[],
};

const PlaceholderPage = ({ title, description, phase }: PlaceholderPageProps) => {
  const content = pageContent[title] || defaultContent;

  return (
    <AppShell pageTitle={title}>
      <div className="page-content" style={{ maxWidth: 680, paddingTop: "2rem", paddingBottom: "3rem" }}>

        {/* Phase badge */}
        <div style={{ marginBottom: "1.5rem" }}>
          <span className="badge badge-muted">
            <span className="pulse-dot" style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--cyan)", display: "inline-block" }}/>
            {phase} — Coming Soon
          </span>
        </div>

        {/* Heading */}
        <h1 className="page-title" style={{ marginBottom: "0.625rem", fontSize: "1.875rem" }}>
          {content.heading}
        </h1>
        <p style={{ fontSize: "1rem", color: "var(--text-secondary)", lineHeight: 1.65, marginBottom: "2rem", maxWidth: 520 }}>
          {content.subtext}
        </p>

        {/* Preview list */}
        {((content.preview ?? []).length > 0) && (
          <div style={{ marginBottom: "2rem" }}>
            <p style={{ fontSize: "0.8125rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.07em", marginBottom: "0.875rem" }}>
              What you'll get
            </p>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.625rem" }}>
              {(content.preview ?? []).map((item) => (
                <div
                  key={item.label}
                  style={{
                    display: "flex",
                    gap: "1rem",
                    alignItems: "flex-start",
                    padding: "0.875rem 1.125rem",
                    background: "var(--bg-elevated)",
                    border: "1px solid var(--border-default)",
                    borderRadius: "var(--r-md)",
                  }}
                >
                  <span style={{ color: "var(--blue)", fontWeight: 700, flexShrink: 0, marginTop: "0.0625rem" }}>◈</span>
                  <div>
                    <div style={{ fontSize: "0.875rem", fontWeight: 600, color: "var(--text-primary)", marginBottom: "0.125rem" }}>
                      {item.label}
                    </div>
                    <div style={{ fontSize: "0.8125rem", color: "var(--text-muted)" }}>
                      {item.desc}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Upload area for Resume page */}
        {title === "Resume Intelligence" && (
          <div
            style={{
              border: "2px dashed var(--border-strong)",
              borderRadius: "var(--r-lg)",
              padding: "2.5rem",
              textAlign: "center",
              marginBottom: "2rem",
              background: "var(--bg-elevated)",
              cursor: "not-allowed",
              opacity: 0.7,
            }}
            aria-label="Resume upload area — coming soon"
          >
            <div style={{ fontSize: "2rem", marginBottom: "0.75rem", opacity: 0.6 }}>▤</div>
            <p style={{ fontSize: "0.9375rem", fontWeight: 600, color: "var(--text-primary)", marginBottom: "0.375rem" }}>
              Upload your resume
            </p>
            <p style={{ fontSize: "0.8125rem", color: "var(--text-muted)", marginBottom: "1.25rem" }}>
              PDF up to 5 MB
            </p>
            <button className="btn btn-secondary btn-sm" disabled aria-disabled="true">
              Choose Resume
            </button>
            <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "0.875rem" }}>
              Resume Intelligence — coming in {phase}
            </p>
          </div>
        )}

        {/* Job form preview for Job Matching */}
        {title === "Job Matching" && (
          <div className="card" style={{ marginBottom: "2rem" }}>
            <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              <div>
                <label className="form-label">Job Title</label>
                <input className="form-input" placeholder="Frontend Developer" disabled aria-disabled="true"/>
              </div>
              <div>
                <label className="form-label">Job Description</label>
                <textarea className="form-textarea" placeholder="Paste the job description here..." disabled aria-disabled="true" style={{ minHeight: 100 }}/>
              </div>
              <button className="btn btn-primary btn-sm btn-full" disabled aria-disabled="true">
                Analyze Job Description
              </button>
            </div>
            <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "0.875rem", textAlign: "center" }}>
              Job Intelligence — coming in {phase}
            </p>
          </div>
        )}

        {/* CTA */}
        <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
          <Link to={content.ctaTo} style={{ textDecoration: "none" }}>
            <button className="btn btn-primary" id={`placeholder-cta-${title.toLowerCase().replace(/\s+/g, "-")}`}>
              {content.cta} →
            </button>
          </Link>
          <Link to="/dashboard" style={{ textDecoration: "none" }}>
            <button className="btn btn-secondary" id="placeholder-back-btn">
              ← Dashboard
            </button>
          </Link>
        </div>
      </div>
    </AppShell>
  );
};

export default PlaceholderPage;
