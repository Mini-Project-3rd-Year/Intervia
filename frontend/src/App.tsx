import { useEffect } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

// Pages
import LandingPage from "./pages/LandingPage.tsx";
import LoginPage from "./pages/LoginPage.tsx";
import RegisterPage from "./pages/RegisterPage.tsx";
import DashboardPage from "./pages/DashboardPage.tsx";
import NotFoundPage from "./pages/NotFoundPage.tsx";
import PlaceholderPage from "./pages/PlaceholderPage.tsx";

// Auth
import { ProtectedRoute } from "./components/auth/ProtectedRoute.tsx";
import { useAuthStore } from "./store/authStore.ts";

function App() {
  const initialize = useAuthStore((s) => s.initialize);

  useEffect(() => {
    initialize();
  }, [initialize]);

  return (
    <BrowserRouter>
      <Routes>
        {/* ── Public routes ─────────────────────────────────── */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* ── Protected routes ──────────────────────────────── */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/resume"
          element={
            <ProtectedRoute>
              <PlaceholderPage
                title="Resume Intelligence"
                description="Upload and analyze your resume — coming in Phase 2"
                phase="Phase 2"
              />
            </ProtectedRoute>
          }
        />
        <Route
          path="/interview"
          element={
            <ProtectedRoute>
              <PlaceholderPage
                title="Interview Session"
                description="Adaptive AI interview engine — coming in Phase 7"
                phase="Phase 7"
              />
            </ProtectedRoute>
          }
        />
        <Route
          path="/jobs"
          element={
            <ProtectedRoute>
              <PlaceholderPage
                title="Job Matching"
                description="Match your profile to job descriptions — coming in Phase 3"
                phase="Phase 3"
              />
            </ProtectedRoute>
          }
        />
        <Route
          path="/coaching"
          element={
            <ProtectedRoute>
              <PlaceholderPage
                title="AI Coach"
                description="Personalized coaching and improvement plan — coming in Phase 15"
                phase="Phase 15"
              />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <PlaceholderPage
                title="Profile"
                description="Your account and settings — coming in Phase 1"
                phase="Phase 1"
              />
            </ProtectedRoute>
          }
        />

        {/* ── 404 ───────────────────────────────────────────── */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

