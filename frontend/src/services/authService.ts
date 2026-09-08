import axios from "axios";

export interface AuthUser {
  id: string;
  email: string;
  full_name?: string | null;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: AuthUser;
}

const AUTH_TOKEN_KEY = "intervia_access_token";
const AUTH_USER_KEY = "intervia_user";
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const authClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
});

const persistSession = (data: AuthResponse) => {
  localStorage.setItem(AUTH_TOKEN_KEY, data.access_token);
  localStorage.setItem(AUTH_USER_KEY, JSON.stringify(data.user));
  return data;
};

export const authService = {
  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await authClient.post<AuthResponse>("/auth/login", {
      email,
      password,
    });

    return persistSession(response.data);
  },

  async register(fullName: string, email: string, password: string): Promise<AuthResponse> {
    const response = await authClient.post<AuthResponse>("/auth/register", {
      full_name: fullName,
      email,
      password,
    });

    return persistSession(response.data);
  },

  logout(): void {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(AUTH_USER_KEY);
  },

  getToken(): string | null {
    return localStorage.getItem(AUTH_TOKEN_KEY);
  },

  getStoredUser(): AuthUser | null {
    const rawUser = localStorage.getItem(AUTH_USER_KEY);
    if (!rawUser) return null;

    try {
      return JSON.parse(rawUser) as AuthUser;
    } catch {
      localStorage.removeItem(AUTH_USER_KEY);
      return null;
    }
  },
};

export default authService;
