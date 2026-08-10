import { Link } from "react-router-dom";

interface PlaceholderPageProps {
  title: string;
  description: string;
  phase: string;
}

const PlaceholderPage = ({ title, description, phase }: PlaceholderPageProps) => {
  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#050c1a",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "2rem",
      }}
    >
      {/* Badge */}
      <div
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: "0.5rem",
          background: "rgba(37, 99, 235, 0.15)",
          border: "1px solid rgba(37, 99, 235, 0.3)",
          borderRadius: "100px",
          padding: "0.375rem 1rem",
          marginBottom: "1.5rem",
        }}
      >
        <div
          style={{
            width: "6px",
            height: "6px",
            borderRadius: "50%",
            background: "#06b6d4",
          }}
          className="pulse-dot"
        />
        <span
          style={{
            fontSize: "0.75rem",
            fontWeight: 600,
            color: "#60a5fa",
            letterSpacing: "0.08em",
            textTransform: "uppercase",
          }}
        >
          {phase}
        </span>
      </div>

      {/* Title */}
      <h1
        style={{
          fontSize: "2.5rem",
          fontWeight: 800,
          color: "white",
          marginBottom: "1rem",
          letterSpacing: "-0.03em",
          textAlign: "center",
        }}
      >
        {title}
      </h1>

      {/* Description */}
      <p
        style={{
          fontSize: "1.05rem",
          color: "rgba(255,255,255,0.5)",
          maxWidth: "480px",
          textAlign: "center",
          lineHeight: 1.6,
          marginBottom: "2.5rem",
        }}
      >
        {description}
      </p>

      {/* Construction indicator */}
      <div
        className="glass"
        style={{
          borderRadius: "12px",
          padding: "1.5rem 2rem",
          display: "flex",
          alignItems: "center",
          gap: "1rem",
          marginBottom: "2rem",
        }}
      >
        <span style={{ fontSize: "1.5rem" }}>🚧</span>
        <div>
          <p style={{ color: "rgba(255,255,255,0.7)", fontSize: "0.875rem", fontWeight: 500 }}>
            Under Construction
          </p>
          <p style={{ color: "rgba(255,255,255,0.4)", fontSize: "0.8rem" }}>
            This feature will be ready soon.
          </p>
        </div>
      </div>

      {/* Back button */}
      <Link to="/" style={{ textDecoration: "none" }}>
        <button className="btn-secondary">← Back to Home</button>
      </Link>
    </div>
  );
};

export default PlaceholderPage;
