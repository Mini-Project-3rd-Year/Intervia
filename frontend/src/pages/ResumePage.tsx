import { useState } from "react";
import { isAxiosError } from "axios";
import { Link } from "react-router-dom";
import { ResumeUpload } from "../features/resume";
import apiClient from "../services/api";

interface ResumeProfile {
  resume_id: string;
  name: string | null;
  skills: string[];
  experience_count: number;
  status: string;
}

export default function ResumePage() {
  const [resumeId, setResumeId] = useState<string | null>(null);
  const [profile, setProfile] = useState<ResumeProfile | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadProfile = async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await apiClient.get<ResumeProfile>(
        `/resume/${id}/profile`,
      );
      setProfile(data);
    } catch (caughtError) {
      setError(
        (isAxiosError<{ detail?: string }>(caughtError)
          ? caughtError.response?.data?.detail
          : undefined) ||
          "Your resume was uploaded, but its profile could not be created.",
      );
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (id: string, status: string, message: string) => {
    if (status !== "ready") {
      setResumeId(null);
      setError(message);
      return;
    }
    setResumeId(id);
    await loadProfile(id);
  };

  const reset = () => {
    setResumeId(null);
    setProfile(null);
    setError(null);
  };

  return (
    <div style={{ minHeight: "100vh", background: "#050c1a" }}>
      <header
        style={{
          padding: "1rem max(1.5rem, calc((100vw - 1100px) / 2))",
          borderBottom: "1px solid rgba(255,255,255,0.08)",
        }}
      >
        <Link to="/dashboard" style={{ color: "white", textDecoration: "none", fontWeight: 700 }}>
          ← Intervia
        </Link>
      </header>
      <main style={{ maxWidth: 760, margin: "0 auto", padding: "3rem 1.5rem" }}>
        <p style={{ color: "#60a5fa", fontSize: "0.875rem", fontWeight: 600 }}>
          RESUME INTELLIGENCE
        </p>
        <h1 style={{ fontSize: "2rem", margin: "0.5rem 0 0.75rem" }}>Your resume</h1>
        <p style={{ color: "rgba(255,255,255,0.6)", marginBottom: "2rem" }}>
          Upload a PDF or DOCX to extract your skills and experience.
        </p>

        {profile ? (
          <section
            aria-live="polite"
            style={{
              padding: "1.5rem",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: 16,
              background: "rgba(255,255,255,0.04)",
            }}
          >
            <h2 style={{ fontSize: "1.5rem" }}>{profile.name || "Your profile"}</h2>
            <p style={{ color: "rgba(255,255,255,0.65)", marginTop: 8 }}>
              {profile.experience_count} positions · {profile.skills.length} skills
            </p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 16 }}>
              {profile.skills.map((skill) => (
                <span
                  key={skill}
                  style={{
                    border: "1px solid rgba(96,165,250,0.3)",
                    borderRadius: 999,
                    padding: "0.35rem 0.75rem",
                    color: "#bfdbfe",
                    fontSize: "0.875rem",
                  }}
                >
                  {skill}
                </span>
              ))}
            </div>
            <button
              type="button"
              onClick={reset}
              style={{ marginTop: "1.5rem", padding: "0.65rem 1rem", cursor: "pointer" }}
            >
              Upload a different resume
            </button>
          </section>
        ) : (
          <>
            {loading && (
              <p role="status" style={{ color: "rgba(255,255,255,0.65)", marginTop: 16 }}>
                Building your resume profile…
              </p>
            )}
            {error && (
              <div role="alert" style={{ color: "#f87171", marginTop: 16 }}>
                <p>{error}</p>
                {resumeId && (
                  <button
                    type="button"
                    onClick={() => void loadProfile(resumeId)}
                    style={{ marginTop: 12, marginRight: 8, padding: "0.5rem 0.75rem", cursor: "pointer" }}
                  >
                    Retry profile extraction
                  </button>
                )}
                <button
                  type="button"
                  onClick={reset}
                  style={{ marginTop: 12, padding: "0.5rem 0.75rem", cursor: "pointer" }}
                >
                  Upload another resume
                </button>
              </div>
            )}
            {!loading && !error && <ResumeUpload onUploadComplete={handleUpload} />}
          </>
        )}
      </main>
    </div>
  );
}
