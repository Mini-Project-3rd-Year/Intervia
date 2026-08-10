import { StrictMode, Component } from "react";
import type { ReactNode, ErrorInfo } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.tsx";

/* ---- Error Boundary --------------------------------------- */
interface EBState {
  error: Error | null;
}

class ErrorBoundary extends Component<{ children: ReactNode }, EBState> {
  state: EBState = { error: null };

  static getDerivedStateFromError(error: Error): EBState {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("[Intervia] Uncaught render error:", error, info);
  }

  render() {
    if (this.state.error) {
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
            fontFamily: "monospace",
            color: "#f87171",
          }}
        >
          <div
            style={{
              background: "rgba(239,68,68,0.1)",
              border: "1px solid rgba(239,68,68,0.3)",
              borderRadius: "12px",
              padding: "2rem",
              maxWidth: "640px",
              width: "100%",
            }}
          >
            <h1
              style={{
                fontSize: "1.25rem",
                fontWeight: 700,
                marginBottom: "1rem",
                color: "#fca5a5",
              }}
            >
              ⚠️ Render Error
            </h1>
            <pre
              style={{
                fontSize: "0.8rem",
                whiteSpace: "pre-wrap",
                wordBreak: "break-word",
                color: "#fca5a5",
                lineHeight: 1.6,
              }}
            >
              {this.state.error.message}
              {"\n\n"}
              {this.state.error.stack}
            </pre>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

/* ---- Mount ------------------------------------------------ */
const root = document.getElementById("root");
if (!root) {
  throw new Error(
    '[Intervia] Could not find #root element. Check index.html.'
  );
}

createRoot(root).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>
);
