/**
 * frontend/src/services/supabase.ts
 * Phase 1 — Supabase client singleton for the Intervia frontend.
 *
 * Uses VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY from environment.
 * The anon key is safe to expose in the browser — it is intentionally public.
 * Never use SUPABASE_SERVICE_ROLE_KEY here.
 */

import { createClient } from "@supabase/supabase-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL as string;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string;

if (!supabaseUrl || !supabaseAnonKey) {
  console.error(
    "[Intervia] Missing Supabase environment variables. " +
      "Set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in your .env file."
  );
}

/**
 * Supabase client for browser use.
 * Supabase JS SDK manages session persistence automatically via localStorage.
 * Do NOT manually read/write access tokens — use supabase.auth.getSession().
 */
export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export default supabase;
