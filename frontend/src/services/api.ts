/**
 * Intervia API Client
 * Base Axios instance configured for the Intervia backend.
 * All API calls should go through this client.
 */

import axios from "axios";
import type { AxiosError, AxiosResponse } from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
});

/* ---- Request interceptor (auth token) -------------------- */
apiClient.interceptors.request.use(
  (config) => {
    // Phase 1: Attach JWT token from localStorage / Supabase session
    const token = localStorage.getItem("intervia_access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

/* ---- Response interceptor (error handling) --------------- */
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Phase 1: Redirect to login on token expiry
      localStorage.removeItem("intervia_access_token");
      // window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

/* ---- Health check ---------------------------------------- */
export const checkHealth = async () => {
  const response = await apiClient.get("/health");
  return response.data;
};

export default apiClient;
