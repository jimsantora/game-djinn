import React, { createContext, useContext, useEffect, useState } from 'react';
import { authApi } from '@/lib/api';

interface User {
  email: string;
  is_admin: boolean;
}

interface AuthConfig {
  auth_enabled: boolean;
  token_expire_minutes: number;
}

interface AuthState {
  isLoading: boolean;
  isAuthenticated: boolean;
  authEnabled: boolean | null;
  user: User | null;
  token: string | null;
  config: AuthConfig | null;
}

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshConfig: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    isLoading: true,
    isAuthenticated: false,
    authEnabled: null,
    user: null,
    token: null,
    config: null,
  });

  // Check auth config on mount
  useEffect(() => {
    checkAuthConfig();
  }, []);

  // Check if user has valid token when auth is enabled
  useEffect(() => {
    if (state.authEnabled !== null) { // Only run when authEnabled is determined
      if (state.authEnabled && !state.isAuthenticated) {
        const savedToken = localStorage.getItem('auth_token');
        if (savedToken) {
          // Validate token by making an authenticated request
          validateToken(savedToken);
        } else {
          setState(prev => ({ ...prev, isLoading: false }));
        }
      } else if (!state.authEnabled) {
        setState(prev => ({ 
          ...prev, 
          isLoading: false, 
          isAuthenticated: true, // Always authenticated when auth is disabled
          user: { email: 'admin', is_admin: true } // Default user when auth disabled
        }));
      }
    }
  }, [state.authEnabled, state.isAuthenticated]);

  const checkAuthConfig = async () => {
    try {
      const response = await authApi.config();
      const config = response.data;
      setState(prev => ({
        ...prev,
        config,
        authEnabled: config.auth_enabled,
        isLoading: false,
      }));
    } catch (error) {
      console.error('Failed to check auth config:', error);
      setState(prev => ({ ...prev, isLoading: false }));
    }
  };

  const validateToken = async (token: string) => {
    try {
      // In a real app, you'd validate the token with a /me endpoint
      // For now, just assume it's valid if it exists
      setState(prev => ({
        ...prev,
        isAuthenticated: true,
        token,
        user: { email: 'admin', is_admin: true },
        isLoading: false,
      }));
    } catch (error) {
      console.error('Token validation failed:', error);
      localStorage.removeItem('auth_token');
      setState(prev => ({ ...prev, isLoading: false }));
    }
  };

  const login = async (email: string, password: string) => {
    try {
      const response = await authApi.login(email, password);
      const { access_token } = response.data;
      
      localStorage.setItem('auth_token', access_token);
      setState(prev => ({
        ...prev,
        isAuthenticated: true,
        token: access_token,
        user: { email, is_admin: true }, // Assume admin for now
      }));
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    setState(prev => ({
      ...prev,
      isAuthenticated: prev.authEnabled === false, // Stay authenticated if auth is disabled
      token: null,
      user: prev.authEnabled === false ? { email: 'admin', is_admin: true } : null,
    }));
  };

  const refreshConfig = async () => {
    await checkAuthConfig();
  };

  const contextValue: AuthContextType = {
    ...state,
    login,
    logout,
    refreshConfig,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// Hook for protecting routes
export function useRequireAuth() {
  const auth = useAuth();
  
  useEffect(() => {
    if (auth.authEnabled && !auth.isLoading && !auth.isAuthenticated) {
      // Redirect to login page
      window.location.href = '/login';
    }
  }, [auth.authEnabled, auth.isLoading, auth.isAuthenticated]);
  
  return auth;
}