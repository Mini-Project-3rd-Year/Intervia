/**
 * frontend/src/pages/InterviewPage.tsx
 * Redesigned interview page — professional session UI.
 * Preserves all existing interview logic and state machine.
 */

import { useState, useRef, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import AppShell from "../components/layout/AppShell";

type Stage = "setup" | "briefing" | "session" | "completed";
type Mode  = "technical" | "hr" | "mixed" | "pressure";

/* ── Interview modes ───────────────────────────────────── */
const modes: { id: Mode; label: string; desc: string; color: string }[] = [
  { id: "technical", label: "Technical",        desc: "DSA, system design, frameworks", color: "var(--blue)" },
  { id: "hr",        label: "HR / Behavioral",  desc: "Soft skills, STAR method, culture fit", color: "var(--violet)" },
  { id: "mixed",     label: "Mixed",            desc: "Balanced HR + Technical session", color: "var(--cyan)" },
  { id: "pressure",  label: "Pressure Test",    desc: "Fast-paced, stress simulation",  color: "var(--red)" },
];

/* ── Sample questions ──────────────────────────────────── */
const sampleQuestions = [
  { id: 1, text: "Tell me about yourself and what makes you a strong candidate for a frontend developer role.", type: "HR / Intro",       difficulty: "Easy" },
  { id: 2, text: "Explain the difference between useMemo and useCallback in React. When would you use each?",  type: "Technical",       difficulty: "Medium" },
  { id: 3, text: "Describe a situation where you had to debug a complex performance issue. What was your approach?", type: "Behavioral / STAR", difficulty: "Medium" },
  { id: 4, text: "How would you design a real-time chat system? Describe the architecture and key technical decisions.", type: "System Design", difficulty: "Hard" },
];

/* ── Difficulty badge ─────────────────────────────────── */
function DiffBadge({ difficulty }: { difficulty: string }) {
  const cls = difficulty === "Easy" ? "badge-green" : difficulty === "Medium" ? "badge-amber" : "badge-red";
  return <span className={`badge ${cls}`}>{difficulty}</span>;
}

/* ── Score color ──────────────────────────────────────── */
function scoreColor(score: number) {
  return score >= 70 ? "var(--green)" : score >= 55 ? "var(--amber)" : "var(--red)";
}

/* ── Timer format ─────────────────────────────────────── */
const fmt = (s: number) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;

/* ============================================================
   SETUP STAGE
   ============================================================ */
function SetupStage({ onStart }: { onStart: (mode: Mode, role: string) => void }) {
  const [mode, setMode] = useState<Mode>("mixed");
  const [role, setRole] = useState("Frontend Developer — React / TypeScript");

  return (
    <AppShell pageTitle="New Interview">
      <div className="page-content" style={{ maxWidth: 720, paddingTop: "2rem" }}>
        {/* Breadcrumb */}
        <div style={{ marginBottom: "1.75rem" }}>
          <Link to="/dashboard" style={{ fontSize: "0.8375rem", color: "var(--text-muted)", textDecoration: "none" }}>
            ← Dashboard
          </Link>
          <span style={{ color: "var(--border-strong)", margin: "0 0.5rem" }}>/</span>
          <span style={{ fontSize: "0.8375rem", color: "var(--text-secondary)" }}>New Interview</span>
        </div>

        <h1 className="page-title" style={{ marginBottom: "0.375rem" }}>Configure Interview</h1>
        <p className="page-subtitle" style={{ marginBottom: "2rem" }}>
          Choose a mode and target role. We'll tailor every question to your resume.
        </p>

        {/* Mode selection */}
        <div style={{ marginBottom: "1.75rem" }}>
          <label className="form-label" style={{ marginBottom: "0.75rem", display: "block" }}>
            Interview Mode
          </label>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "0.75rem" }}>
            {modes.map((m) => (
              <div
                key={m.id}
                role="radio"
                aria-checked={mode === m.id}
                tabIndex={0}
                onClick={() => setMode(m.id)}
                onKeyDown={(e) => e.key === "Enter" && setMode(m.id)}
                style={{
                  padding: "1.125rem",
                  borderRadius: "var(--r-lg)",
                  background: mode === m.id ? `${m.color}12` : "var(--bg-elevated)",
                  border: `1px solid ${mode === m.id ? m.color + "44" : "var(--border-default)"}`,
                  cursor: "pointer",
                  transition: "all 0.15s ease",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.25rem" }}>
                  <span style={{ fontSize: "0.9375rem", fontWeight: 700, color: mode === m.id ? m.color : "var(--text-primary)" }}>
                    {m.label}
                  </span>
                  {mode === m.id && (
                    <span style={{ width: 18, height: 18, borderRadius: "50%", background: m.color, display: "flex", alignItems: "center", justifyContent: "center", color: "white", fontSize: "0.625rem", fontWeight: 800 }}>
                      ✓
                    </span>
                  )}
                </div>
                <p style={{ fontSize: "0.8125rem", color: "var(--text-muted)", margin: 0 }}>{m.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Role input */}
        <div style={{ marginBottom: "2rem" }}>
          <label htmlFor="target-role" className="form-label">Target Role (optional)</label>
          <input
            id="target-role"
            className="form-input"
            value={role}
            onChange={(e) => setRole(e.target.value)}
            placeholder="e.g. Frontend Developer — React"
            aria-label="Target job role"
          />
          <p style={{ fontSize: "0.775rem", color: "var(--text-muted)", marginTop: "0.375rem" }}>
            Questions will be tailored to this role and your uploaded resume.
          </p>
        </div>

        <button
          className="btn btn-primary btn-full"
          id="start-interview-btn"
          onClick={() => onStart(mode, role)}
          style={{ padding: "0.875rem" }}
        >
          Start Interview Session →
        </button>
      </div>
    </AppShell>
  );
}

/* ============================================================
   BRIEFING STAGE
   ============================================================ */
function BriefingStage({ mode, role, onReady }: { mode: Mode; role: string; onReady: () => void }) {
  const modeInfo = modes.find((m) => m.id === mode)!;

  return (
    <AppShell pageTitle="Interview Briefing">
      <div
        className="page-content"
        style={{ maxWidth: 560, paddingTop: "3rem", margin: "0 auto", textAlign: "center" }}
      >
        {/* AI avatar */}
        <div
          style={{
            width: 100, height: 100, borderRadius: "50%",
            background: "linear-gradient(135deg, var(--blue), var(--violet))",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: "2.25rem",
            margin: "0 auto 1.5rem",
            border: "3px solid rgba(59,130,246,0.25)",
            boxShadow: "0 0 40px rgba(59,130,246,0.2)",
          }}
          aria-hidden="true"
        >
          ◉
        </div>

        <h1 className="page-title" style={{ marginBottom: "0.5rem" }}>
          Hi, I'm <span className="text-gradient">Aria</span>
        </h1>
        <p style={{ fontSize: "0.875rem", color: "var(--text-muted)", marginBottom: "0.375rem" }}>
          Your AI Interviewer
        </p>
        <p style={{ fontSize: "1rem", color: "var(--text-secondary)", lineHeight: 1.65, marginBottom: "1.75rem", maxWidth: 420, margin: "0 auto 1.75rem" }}>
          I've prepared <strong style={{ color: "var(--text-primary)" }}>{sampleQuestions.length} questions</strong> for your{" "}
          <strong style={{ color: "var(--text-primary)" }}>{modeInfo.label}</strong> interview. You'll have{" "}
          <strong style={{ color: "var(--text-primary)" }}>2 minutes</strong> per question.
        </p>

        {role && (
          <div className="badge badge-blue" style={{ marginBottom: "1.75rem", display: "inline-flex" }}>
            Target: {role}
          </div>
        )}

        {/* Ready checklist */}
        <div style={{ display: "flex", flexDirection: "column", gap: "0.625rem", marginBottom: "2rem", textAlign: "left" }}>
          {[
            "Resume analyzed and ready",
            "Questions tailored to your experience",
            "Real-time scoring after each answer",
            "Full feedback report on completion",
          ].map((item) => (
            <div
              key={item}
              style={{
                display: "flex", alignItems: "center", gap: "0.75rem",
                background: "var(--bg-elevated)", border: "1px solid var(--border-default)",
                borderRadius: "var(--r-md)", padding: "0.6875rem 1rem",
                fontSize: "0.875rem", color: "var(--text-secondary)",
              }}
            >
              <span style={{ color: "var(--green)", fontWeight: 700, flexShrink: 0 }}>✓</span>
              {item}
            </div>
          ))}
        </div>

        <button
          className="btn btn-primary btn-full"
          id="ready-btn"
          onClick={onReady}
          style={{ padding: "0.875rem" }}
        >
          I'm Ready — Start Now
        </button>
      </div>
    </AppShell>
  );
}

/* ============================================================
   SESSION STAGE
   ============================================================ */
interface SessionProps {
  mode: Mode;
  answers: { q: string; a: string; score: number }[];
  onSubmit: (answer: string) => void;
  onEnd: () => void;
  currentQ: number;
}

function SessionStage({ answers, onSubmit, onEnd, currentQ }: SessionProps) {
  const [answer, setAnswer] = useState("");
  const [timer, setTimer] = useState(120);
  const [recording, setRecording] = useState(false);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const total = sampleQuestions.length;
  const q = sampleQuestions[currentQ];
  const progress = (currentQ / total) * 100;
  const timerColor = timer > 60 ? "var(--green)" : timer > 30 ? "var(--amber)" : "var(--red)";

  // Reset timer when question changes
  useEffect(() => {
    setTimer(120);
    setAnswer("");
    if (textareaRef.current) textareaRef.current.focus();
  }, [currentQ]);

  // Countdown
  useEffect(() => {
    timerRef.current = setInterval(() => setTimer((t) => Math.max(0, t - 1)), 1000);
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [currentQ]);

  const handleSubmit = () => {
    if (!answer.trim()) return;
    if (timerRef.current) clearInterval(timerRef.current);
    onSubmit(answer.trim());
  };

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg-base)", display: "flex", flexDirection: "column", fontFamily: "inherit" }}>

      {/* Top progress bar */}
      <div
        style={{
          height: 60,
          display: "flex",
          alignItems: "center",
          gap: "1.25rem",
          padding: "0 2rem",
          borderBottom: "1px solid var(--border-subtle)",
          background: "var(--bg-surface)",
          position: "sticky",
          top: 0,
          zIndex: 10,
        }}
      >
        <div style={{ fontWeight: 700, fontSize: "0.9375rem", color: "var(--text-primary)", flexShrink: 0 }}>Intervia</div>

        <div style={{ flex: 1, display: "flex", alignItems: "center", gap: "0.875rem" }}>
          <div className="progress-track" style={{ flex: 1 }}>
            <div
              className="progress-fill progress-fill-blue"
              style={{ width: `${progress}%`, transition: "width 0.5s ease" }}
              role="progressbar"
              aria-valuenow={currentQ}
              aria-valuemax={total}
              aria-label="Interview progress"
            />
          </div>
          <span style={{ fontSize: "0.8125rem", color: "var(--text-muted)", flexShrink: 0, fontVariantNumeric: "tabular-nums" }}>
            Q{currentQ + 1} / {total}
          </span>
        </div>

        {/* Timer */}
        <div
          style={{
            display: "flex", alignItems: "center", gap: "0.375rem",
            background: "var(--bg-elevated)",
            border: `1px solid ${timer < 30 ? "rgba(239,68,68,0.3)" : "var(--border-default)"}`,
            borderRadius: "var(--r-md)",
            padding: "0.375rem 0.875rem",
          }}
          aria-live="polite"
          aria-label={`Time remaining: ${fmt(timer)}`}
        >
          <span style={{ fontSize: "0.75rem", color: timerColor }}>◷</span>
          <span style={{ fontSize: "0.875rem", fontWeight: 700, color: timerColor, fontVariantNumeric: "tabular-nums" }}>
            {fmt(timer)}
          </span>
        </div>

        <button
          className="btn btn-secondary btn-sm"
          id="end-interview-btn"
          onClick={onEnd}
          aria-label="End interview early"
        >
          End Interview
        </button>
      </div>

      {/* Main layout */}
      <div style={{ flex: 1, display: "grid", gridTemplateColumns: "280px 1fr", overflow: "hidden" }}>

        {/* Left panel — AI + meta */}
        <div
          style={{
            background: "var(--bg-surface)",
            borderRight: "1px solid var(--border-subtle)",
            padding: "2rem 1.5rem",
            display: "flex",
            flexDirection: "column",
            gap: "1.5rem",
            overflow: "auto",
          }}
        >
          {/* Avatar */}
          <div style={{ textAlign: "center" }}>
            <div
              style={{
                width: 80, height: 80,
                borderRadius: "50%",
                background: "linear-gradient(135deg, var(--blue), var(--violet))",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: "1.75rem",
                margin: "0 auto 0.875rem",
                border: "2px solid rgba(59,130,246,0.2)",
              }}
              aria-hidden="true"
            >
              ◉
            </div>
            <div style={{ fontSize: "0.875rem", fontWeight: 600, color: "var(--text-primary)" }}>Aria</div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.375rem", justifyContent: "center", marginTop: "0.25rem" }}>
              <span className="pulse-dot" style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--green)", display: "inline-block" }}/>
              <span style={{ fontSize: "0.75rem", color: "var(--green)", fontWeight: 500 }}>Live Session</span>
            </div>
          </div>

          {/* Question meta */}
          <div style={{ background: "var(--bg-elevated)", border: "1px solid var(--border-default)", borderRadius: "var(--r-md)", padding: "1rem" }}>
            <div className="section-title" style={{ fontSize: "0.8125rem", marginBottom: "0.75rem" }}>Question Info</div>
            <div style={{ marginBottom: "0.75rem" }}>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: "0.25rem" }}>Category</div>
              <span className="badge badge-blue">{q.type}</span>
            </div>
            <div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: "0.25rem" }}>Difficulty</div>
              <DiffBadge difficulty={q.difficulty} />
            </div>
          </div>

          {/* Previous answers */}
          {answers.length > 0 && (
            <div>
              <div className="section-title" style={{ fontSize: "0.8125rem", marginBottom: "0.625rem" }}>Answered</div>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.375rem" }}>
                {answers.map((a, i) => (
                  <div
                    key={i}
                    style={{
                      display: "flex", justifyContent: "space-between", alignItems: "center",
                      padding: "0.5rem 0.75rem",
                      background: "var(--bg-elevated)",
                      border: "1px solid var(--border-default)",
                      borderRadius: "var(--r-sm)",
                    }}
                  >
                    <span style={{ fontSize: "0.8125rem", color: "var(--text-muted)" }}>Q{i + 1}</span>
                    <span style={{ fontSize: "0.875rem", fontWeight: 700, color: scoreColor(a.score) }}>
                      {a.score}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right panel — question + answer */}
        <div style={{ padding: "2rem 2.5rem", display: "flex", flexDirection: "column", overflow: "auto" }}>

          {/* Question */}
          <div
            style={{
              background: "var(--blue-dim)",
              border: "1px solid var(--blue-border)",
              borderRadius: "var(--r-lg)",
              padding: "1.375rem 1.625rem",
              marginBottom: "1.75rem",
            }}
            aria-live="polite"
          >
            <p style={{ fontSize: "0.75rem", fontWeight: 700, color: "#93C5FD", letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: "0.625rem" }}>
              Aria is asking:
            </p>
            <p style={{ fontSize: "1.0625rem", color: "var(--text-primary)", lineHeight: 1.6, fontWeight: 500, margin: 0 }}>
              {q.text}
            </p>
          </div>

          {/* Answer area */}
          <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "0.75rem" }}>
            <label htmlFor="answer-textarea" className="form-label">
              Your Answer
            </label>
            <textarea
              id="answer-textarea"
              ref={textareaRef}
              className="form-textarea"
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="Type your answer here... or click the microphone button to use voice input."
              style={{ flex: 1, minHeight: 200, fontSize: "0.9375rem", lineHeight: 1.65 }}
              aria-label="Your interview answer"
            />

            {/* Controls */}
            <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
              {/* Mic button */}
              <button
                className="btn btn-secondary"
                id="mic-btn"
                onClick={() => setRecording(!recording)}
                aria-label={recording ? "Stop recording" : "Start voice recording"}
                style={{
                  width: 44, height: 44, padding: 0, borderRadius: "50%",
                  borderColor: recording ? "rgba(239,68,68,0.4)" : undefined,
                  color: recording ? "var(--red)" : undefined,
                  flexShrink: 0,
                }}
              >
                {recording ? "⏹" : "◎"}
              </button>

              <span style={{ fontSize: "0.8125rem", color: "var(--text-muted)", flex: 1 }}>
                {recording
                  ? <span style={{ color: "var(--red)" }}>◉ Recording... speak clearly</span>
                  : "Voice input available"}
              </span>

              <button
                className="btn btn-secondary btn-sm"
                id="skip-btn"
                onClick={() => onSubmit("")}
                aria-label="Skip this question"
              >
                Skip
              </button>

              <button
                className="btn btn-primary"
                id="submit-answer-btn"
                disabled={!answer.trim()}
                onClick={handleSubmit}
                aria-label="Submit your answer"
                style={{ minWidth: 140 }}
              >
                {currentQ + 1 >= total ? "Finish Interview" : "Submit Answer →"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ============================================================
   COMPLETED STAGE
   ============================================================ */
function CompletedStage({ answers }: { answers: { q: string; a: string; score: number }[] }) {
  const navigate = useNavigate();
  const avgScore = answers.length
    ? Math.round(answers.reduce((s, a) => s + a.score, 0) / answers.length)
    : 0;

  const breakdown = [
    { label: "Technical Knowledge", score: Math.min(99, avgScore + 6) },
    { label: "Communication",       score: Math.max(20, avgScore - 10) },
    { label: "Problem Solving",     score: Math.min(99, avgScore + 4) },
    { label: "Confidence",          score: Math.max(20, avgScore - 4) },
    { label: "Clarity",             score: Math.min(99, avgScore + 1) },
  ];

  const strengths = [
    "Clear technical explanations",
    "Good problem-solving approach",
    "Structured answer format",
  ];

  const focusAreas = [
    "Expand system design explanations",
    "Give more concrete examples",
    "Reduce filler words",
  ];

  return (
    <AppShell pageTitle="Interview Results">
      <div className="page-content" style={{ maxWidth: 720, paddingTop: "2rem", paddingBottom: "3rem" }}>
        <h1 className="page-title" style={{ marginBottom: "0.375rem" }}>Interview Complete</h1>
        <p className="page-subtitle" style={{ marginBottom: "2rem" }}>
          You answered {answers.length} of {sampleQuestions.length} questions
        </p>

        {/* Overall score */}
        <div
          className="card"
          style={{ textAlign: "center", padding: "2rem", marginBottom: "1.25rem" }}
        >
          <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.07em", marginBottom: "1.25rem" }}>
            Overall Score
          </div>

          {/* Score ring */}
          <div style={{ marginBottom: "1rem" }}>
            {(() => {
              const r = 52;
              const circ = 2 * Math.PI * r;
              const filled = (avgScore / 100) * circ;
              const color = scoreColor(avgScore);
              return (
                <svg width={128} height={128} viewBox="0 0 128 128" aria-label={`Score: ${avgScore}%`}>
                  <circle cx={64} cy={64} r={r} fill="none" stroke="rgba(255,255,255,0.07)" strokeWidth="10"/>
                  <circle cx={64} cy={64} r={r} fill="none" stroke={color} strokeWidth="10"
                    strokeDasharray={`${filled} ${circ}`} strokeLinecap="round"
                    transform="rotate(-90 64 64)"/>
                  <text x={64} y={60} textAnchor="middle" fill="var(--text-primary)" fontSize={20} fontWeight={800}>{avgScore}%</text>
                  <text x={64} y={78} textAnchor="middle" fill="var(--text-muted)" fontSize={11}>Score</text>
                </svg>
              );
            })()}
          </div>

          <div
            className={`badge ${avgScore >= 70 ? "badge-green" : avgScore >= 55 ? "badge-amber" : "badge-red"}`}
            style={{ fontSize: "0.875rem", padding: "0.375rem 1rem" }}
          >
            {avgScore >= 70 ? "Great job!" : avgScore >= 55 ? "Keep practicing!" : "Room to improve"}
          </div>
        </div>

        {/* Dimension breakdown */}
        <div className="card" style={{ marginBottom: "1.25rem" }}>
          <div className="section-header" style={{ marginBottom: "1.25rem" }}>
            <div className="section-title">Score Breakdown</div>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            {breakdown.map((dim) => (
              <div key={dim.label} className="skill-bar">
                <div className="skill-bar-header">
                  <span className="skill-bar-name">{dim.label}</span>
                  <span className="skill-bar-score" style={{ color: scoreColor(dim.score) }}>{dim.score}%</span>
                </div>
                <div className="progress-track">
                  <div
                    className={`progress-fill ${dim.score >= 70 ? "progress-fill-green" : dim.score >= 55 ? "progress-fill-amber" : "progress-fill-red"}`}
                    style={{ width: `${dim.score}%` }}
                    role="progressbar"
                    aria-valuenow={dim.score}
                    aria-valuemin={0}
                    aria-valuemax={100}
                    aria-label={dim.label}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* What went well + Focus */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1.5rem" }}>
          <div className="card">
            <div className="section-title" style={{ marginBottom: "0.875rem", color: "var(--green)" }}>What Went Well</div>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              {strengths.map((s) => (
                <div key={s} style={{ display: "flex", gap: "0.5rem", fontSize: "0.84375rem", color: "var(--text-secondary)" }}>
                  <span style={{ color: "var(--green)", flexShrink: 0 }}>✓</span>
                  {s}
                </div>
              ))}
            </div>
          </div>

          <div className="card">
            <div className="section-title" style={{ marginBottom: "0.875rem" }}>Focus Next</div>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              {focusAreas.map((f) => (
                <div key={f} style={{ display: "flex", gap: "0.5rem", fontSize: "0.84375rem", color: "var(--text-secondary)" }}>
                  <span style={{ color: "var(--blue)", flexShrink: 0 }}>→</span>
                  {f}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Actions */}
        <div style={{ display: "flex", gap: "0.875rem" }}>
          <Link to="/coaching" style={{ textDecoration: "none", flex: 1 }}>
            <button className="btn btn-primary btn-full" id="practice-weak-btn">
              Practice Weak Areas →
            </button>
          </Link>
          <button
            className="btn btn-secondary"
            id="retry-interview-btn"
            onClick={() => window.location.reload()}
            aria-label="Retry this interview"
          >
            Retry Interview
          </button>
          <Link to="/dashboard" style={{ textDecoration: "none" }}>
            <button className="btn btn-secondary" id="back-dashboard-btn">
              ← Dashboard
            </button>
          </Link>
        </div>
      </div>
    </AppShell>
  );
}

/* ============================================================
   ROOT COMPONENT
   ============================================================ */
export default function InterviewPage() {
  const [stage, setStage] = useState<Stage>("setup");
  const [mode, setMode]   = useState<Mode>("mixed");
  const [role, setRole]   = useState("");
  const [currentQ, setCurrentQ] = useState(0);
  const [answers, setAnswers]   = useState<{ q: string; a: string; score: number }[]>([]);

  const handleStart = (m: Mode, r: string) => { setMode(m); setRole(r); setStage("briefing"); };
  const handleReady = () => setStage("session");

  const handleSubmit = (answer: string) => {
    const score = answer.trim()
      ? Math.floor(52 + Math.random() * 38)
      : 0;

    setAnswers((prev) => [...prev, { q: sampleQuestions[currentQ].text, a: answer, score }]);

    if (currentQ + 1 >= sampleQuestions.length) {
      setStage("completed");
    } else {
      setCurrentQ((q) => q + 1);
    }
  };

  const handleEnd = () => {
    // submit remaining as empty and show results
    setStage("completed");
  };

  if (stage === "setup")     return <SetupStage onStart={handleStart} />;
  if (stage === "briefing")  return <BriefingStage mode={mode} role={role} onReady={handleReady} />;
  if (stage === "session")   return <SessionStage mode={mode} answers={answers} onSubmit={handleSubmit} onEnd={handleEnd} currentQ={currentQ} />;
  if (stage === "completed") return <CompletedStage answers={answers} />;
  return null;
}
