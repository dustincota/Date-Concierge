import { create } from 'zustand';
import { authAPI } from '../utils/api';
import type { User } from '../types';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name?: string) => Promise<void>;
  logout: () => void;
  loadUser: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: false,
  isLoading: false,
  error: null,

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const data = await authAPI.login(email, password);
      localStorage.setItem('token', data.access_token);
      set({ token: data.access_token, isLoading: false });

      // Load user data
      const user = await authAPI.getCurrentUser();
      set({ user, isAuthenticated: true });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Login failed',
        isLoading: false,
      });
    }
  },

  register: async (email: string, password: string, name?: string) => {
    set({ isLoading: true, error: null });
    try {
      const data = await authAPI.register(email, password, name);
      localStorage.setItem('token', data.access_token);
      set({ token: data.access_token, isLoading: false });

      // Load user data
      const user = await authAPI.getCurrentUser();
      set({ user, isAuthenticated: true });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Registration failed',
        isLoading: false,
      });
    }
  },

  logout: () => {
    localStorage.removeItem('token');
    set({
      user: null,
      token: null,
      isAuthenticated: false,
    });
  },

  loadUser: async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      set({ isAuthenticated: false });
      return;
    }

    set({ isLoading: true });
    try {
      const user = await authAPI.getCurrentUser();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch (error) {
      localStorage.removeItem('token');
      set({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      });
    }
  },

  clearError: () => set({ error: null }),
}));
