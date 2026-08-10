import { BrowserRouter, Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage.tsx";
import NotFoundPage from "./pages/NotFoundPage.tsx";
import PlaceholderPage from "./pages/PlaceholderPage.tsx";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<LandingPage />} />
        <Route
          path="/login"
          element={
            <PlaceholderPage
              title="Sign In"
              description="Authentication — coming in Phase 1"
              phase="Phase 1"
            />
          }
        />
        <Route
          path="/register"
          element={
            <PlaceholderPage
              title="Create Account"
              description="Authentication — coming in Phase 1"
              phase="Phase 1"
            />
          }
        />

        {/* Protected routes (auth guard in Phase 1) */}
        <Route
          path="/dashboard"
          element={
            <PlaceholderPage
              title="Dashboard"
              description="Your interview overview and progress — coming in Phase 18"
              phase="Phase 18"
            />
          }
        />
        <Route
          path="/interview"
          element={
            <PlaceholderPage
              title="Interview Session"
              description="Adaptive AI interview engine — coming in Phase 7"
              phase="Phase 7"
            />
          }
        />
        <Route
          path="/resume"
          element={
            <PlaceholderPage
              title="Resume Intelligence"
              description="Upload and analyze your resume — coming in Phase 2"
              phase="Phase 2"
            />
          }
        />
        <Route
          path="/jobs"
          element={
            <PlaceholderPage
              title="Job Matching"
              description="Match your profile to job descriptions — coming in Phase 3"
              phase="Phase 3"
            />
          }
        />
        <Route
          path="/coaching"
          element={
            <PlaceholderPage
              title="AI Coach"
              description="Personalized coaching and improvement plan — coming in Phase 15"
              phase="Phase 15"
            />
          }
        />
        <Route
          path="/profile"
          element={
            <PlaceholderPage
              title="Profile"
              description="Your account and settings — coming in Phase 1"
              phase="Phase 1"
            />
          }
        />

        {/* 404 */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
