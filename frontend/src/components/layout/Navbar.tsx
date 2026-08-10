import { Link } from "react-router-dom";

const Navbar = () => {
  return (
    <nav
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        zIndex: 100,
        padding: "1rem 2rem",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        background: "rgba(5, 12, 26, 0.8)",
        backdropFilter: "blur(20px)",
        WebkitBackdropFilter: "blur(20px)",
        borderBottom: "1px solid rgba(255, 255, 255, 0.06)",
      }}
    >
      {/* Logo */}
      <Link to="/" style={{ textDecoration: "none" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.625rem" }}>
          <div
            style={{
              width: "32px",
              height: "32px",
              borderRadius: "8px",
              background: "linear-gradient(135deg, #2563eb, #06b6d4)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "16px",
              fontWeight: 700,
              color: "white",
            }}
          >
            I
          </div>
          <span
            style={{
              fontSize: "1.125rem",
              fontWeight: 700,
              color: "white",
              letterSpacing: "-0.02em",
            }}
          >
            Intervia
          </span>
        </div>
      </Link>

      {/* Nav links */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "2rem",
        }}
      >
        {["Features", "How it Works", "About"].map((item) => (
          <span
            key={item}
            style={{
              color: "rgba(255,255,255,0.6)",
              fontSize: "0.875rem",
              fontWeight: 500,
              cursor: "pointer",
              transition: "color 0.2s",
            }}
            onMouseEnter={(e) =>
              ((e.target as HTMLElement).style.color = "white")
            }
            onMouseLeave={(e) =>
              ((e.target as HTMLElement).style.color =
                "rgba(255,255,255,0.6)")
            }
          >
            {item}
          </span>
        ))}
      </div>

      {/* CTA buttons */}
      <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
        <Link to="/login" style={{ textDecoration: "none" }}>
          <button className="btn-secondary" style={{ padding: "0.5rem 1.25rem" }}>
            Sign In
          </button>
        </Link>
        <Link to="/register" style={{ textDecoration: "none" }}>
          <button className="btn-primary" style={{ padding: "0.5rem 1.25rem" }}>
            Get Started
          </button>
        </Link>
      </div>
    </nav>
  );
};

export default Navbar;
