/**
 * Intervia API Client
 * Base Axios instance configured for the Intervia backend.
 * All API calls should go through this client.
 *
 * Phase 1: Reads Supabase session access_token automatically.
 * Do NOT manually manage tokens here — the Supabase SDK handles storage + refresh.
 */

import axios from "axios";
import type { AxiosError, AxiosResponse, InternalAxiosRequestConfig } from "axios";
import { supabase } from "./supabase";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
});

/* ---- Request interceptor: attach Supabase access token ------------------- */
apiClient.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    // Get the current session from Supabase SDK — never read localStorage directly
    const { data } = await supabase.auth.getSession();
    const token = data.session?.access_token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

/* ---- Response interceptor: handle 401 ------------------------------------ */
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Sign out via Supabase SDK to clear session cleanly
      await supabase.auth.signOut();
      // Redirect to login — use window.location to avoid circular React import
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

/* ---- Health check -------------------------------------------------------- */
export const checkHealth = async () => {
  const response = await apiClient.get("/health");
  return response.data;
};

export default apiClient;

