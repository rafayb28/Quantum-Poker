// Authentication store using Zustand

import { create } from 'zustand';
import { api } from '@/lib/api';

interface AuthState {
  token: string | null;
  username: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  login: (username: string) => Promise<void>;
  logout: () => void;
  validateToken: () => Promise<boolean>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  token: null,
  username: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  
  login: async (username: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await api.createSession(username);
      const token = response.token;
      
      localStorage.setItem('token', token);
      localStorage.setItem('username', username);
      
      set({
        token,
        username,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error: any) {
      set({
        error: error.message || 'Login failed',
        isLoading: false,
      });
      throw error;
    }
  },
  
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    
    set({
      token: null,
      username: null,
      isAuthenticated: false,
      error: null,
    });
  },
  
  validateToken: async () => {
    const token = localStorage.getItem('token');
    const username = localStorage.getItem('username');
    
    if (!token || !username) {
      return false;
    }
    
    try {
      await api.validateSession();
      set({
        token,
        username,
        isAuthenticated: true,
      });
      return true;
    } catch {
      get().logout();
      return false;
    }
  },
  
  clearError: () => set({ error: null }),
}));
