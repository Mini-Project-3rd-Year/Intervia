/**
 * frontend/src/features/auth/authStore.ts
 * Phase 1 — Zustand auth store for Intervia.
 *
 * Supabase JS SDK manages token storage and refresh automatically.
 * Do NOT manually persist access or refresh tokens in localStorage.
 * Use supabase.auth.getSession() / onAuthStateChange() for all session work.
 */

import { create } from "zustand";
import type { Session, User } from "@supabase/supabase-js";
import { supabase } from "../../services/supabase";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface AuthState {
  user: User | null;
  session: Session | null;
  loading: boolean;
  error: string | null;
}

interface AuthActions {
  /** Register a new user via Supabase Auth. */
  register: (email: string, password: string, fullName: string) => Promise<void>;
  /** Sign in with email + password via Supabase Auth. */
  login: (email: string, password: string) => Promise<void>;
  /** One-click demo login for instant evaluation and preview. */
  loginDemo: () => Promise<void>;
  /** Sign out and clear local session. */
  logout: () => Promise<void>;
  /** Manually trigger a session refresh (usually handled automatically by SDK). */
  refreshSession: () => Promise<void>;
  /** Initialize the store: restore session and subscribe to auth state changes. */
  initialize: () => () => void;
  /** Clear any auth error. */
  clearError: () => void;
}

type AuthStore = AuthState & AuthActions;

// ---------------------------------------------------------------------------
// Demo User & Session Fixture
// ---------------------------------------------------------------------------

const DEMO_USER: User = {
  id: "00000000-0000-0000-0000-000000000001",
  app_metadata: { provider: "email" },
  user_metadata: { full_name: "Demo Candidate" },
  aud: "authenticated",
  created_at: new Date().toISOString(),
  email: "demo@intervia.ai",
  role: "authenticated",
  updated_at: new Date().toISOString(),
} as unknown as User;

const DEMO_SESSION: Session = {
  access_token: "demo-access-token-intervia",
  refresh_token: "demo-refresh-token-intervia",
  expires_in: 86400,
  token_type: "bearer",
  user: DEMO_USER,
};

// ---------------------------------------------------------------------------
// Store
// ---------------------------------------------------------------------------

export const useAuthStore = create<AuthStore>((set, get) => ({
  // ---- Initial state -------------------------------------------------------
  user: null,
  session: null,
  loading: true, // true on mount until session is restored
  error: null,

  // ---- Actions -------------------------------------------------------------

  register: async (email, password, fullName) => {
    set({ loading: true, error: null });
    try {
      const { error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: { full_name: fullName },
        },
      });
      if (error) throw error;
      // onAuthStateChange will update user + session automatically after confirm
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Registration failed.";
      set({ error: message, loading: false });
      throw err;
    }
  },

  login: async (email, password) => {
    set({ loading: true, error: null });
    try {
      const { error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });
      if (error) throw error;
      // onAuthStateChange handles user + session update
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Login failed.";
      set({ error: message, loading: false });
      throw err;
    }
  },

  loginDemo: async () => {
    set({ loading: true, error: null });
    try {
      localStorage.setItem("intervia_demo_session", "true");
      set({
        user: DEMO_USER,
        session: DEMO_SESSION,
        loading: false,
        error: null,
      });
    } catch {
      set({ error: "Demo login failed.", loading: false });
    }
  },

  logout: async () => {
    set({ loading: true, error: null });
    try {
      localStorage.removeItem("intervia_demo_session");
      const { error } = await supabase.auth.signOut();
      if (error && error.message !== "Auth session missing!") {
        // Ignore session missing error for demo logout
        console.warn(error);
      }
      set({ user: null, session: null, loading: false });
    } catch (err: unknown) {
      set({ user: null, session: null, loading: false });
    }
  },

  refreshSession: async () => {
    if (localStorage.getItem("intervia_demo_session")) {
      set({ session: DEMO_SESSION, user: DEMO_USER });
      return;
    }
    try {
      const { data, error } = await supabase.auth.refreshSession();
      if (error) throw error;
      set({ session: data.session, user: data.user });
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Session refresh failed.";
      set({ error: message });
    }
  },

  initialize: () => {
    // Check if demo session is active
    if (localStorage.getItem("intervia_demo_session")) {
      set({
        session: DEMO_SESSION,
        user: DEMO_USER,
        loading: false,
      });
      return () => {};
    }

    // Restore existing Supabase session on app load
    supabase.auth.getSession().then(({ data }) => {
      if (data.session) {
        set({
          session: data.session,
          user: data.session.user ?? null,
          loading: false,
        });
      } else if (localStorage.getItem("intervia_demo_session")) {
        set({
          session: DEMO_SESSION,
          user: DEMO_USER,
          loading: false,
        });
      } else {
        set({
          session: null,
          user: null,
          loading: false,
        });
      }
    });

    // Subscribe to auth state changes (login, logout, token refresh, etc.)
    const { data: listener } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        if (!localStorage.getItem("intervia_demo_session")) {
          set({
            session,
            user: session?.user ?? null,
            loading: false,
          });
        }
      }
    );

    // Return unsubscribe function for cleanup in useEffect
    return () => {
      listener.subscription.unsubscribe();
    };
  },

  clearError: () => set({ error: null }),
}));
