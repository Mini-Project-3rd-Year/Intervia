import { Link } from "react-router-dom";

const NotFoundPage = () => {
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
        textAlign: "center",
      }}
    >
      <div
        style={{
          fontSize: "7rem",
          fontWeight: 900,
          letterSpacing: "-0.04em",
          lineHeight: 1,
          marginBottom: "1.5rem",
        }}
        className="gradient-text"
      >
        404
      </div>
      <h1
        style={{
          fontSize: "1.75rem",
          fontWeight: 700,
          color: "white",
          marginBottom: "0.75rem",
          letterSpacing: "-0.02em",
        }}
      >
        Page Not Found
      </h1>
      <p
        style={{
          color: "rgba(255,255,255,0.5)",
          marginBottom: "2.5rem",
          maxWidth: "360px",
        }}
      >
        The page you're looking for doesn't exist or has been moved.
      </p>
      <Link to="/" style={{ textDecoration: "none" }}>
        <button className="btn-primary">← Back to Intervia</button>
      </Link>
    </div>
  );
};

export default NotFoundPage;
