import { create } from "zustand";
import type { AuthUser } from "../services/authService";
import { authService } from "../services/authService";

interface AuthState {
  user: AuthUser | null;
  token: string | null;
  isAuthenticated: boolean;
  initialized: boolean;
  setAuth: (user: AuthUser | null, token: string | null) => void;
  clearAuth: () => void;
  initialize: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  initialized: false,

  setAuth: (user, token) => {
    if (user && token) {
      localStorage.setItem("intervia_user", JSON.stringify(user));
      localStorage.setItem("intervia_access_token", token);
    } else {
      localStorage.removeItem("intervia_user");
      localStorage.removeItem("intervia_access_token");
    }

    set({
      user,
      token,
      isAuthenticated: Boolean(user && token),
      initialized: true,
    });
  },

  clearAuth: () => {
    authService.logout();
    set({
      user: null,
      token: null,
      isAuthenticated: false,
      initialized: true,
    });
  },

  initialize: () => {
    const token = authService.getToken();
    const user = authService.getStoredUser();

    set({
      user,
      token,
      isAuthenticated: Boolean(token),
      initialized: true,
    });
  },
}));

export default useAuthStore;
