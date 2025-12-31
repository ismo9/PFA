import React, { createContext, useContext, useState, useEffect } from 'react';
import { api, setAccessToken, getAccessToken } from '@/lib/api';
import { useNavigate } from 'react-router-dom';

interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: 'admin' | 'manager' | 'viewer';
}

interface RegisterData {
  username: string;
  email: string;
  password: string;
  full_name: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  demoLogin: (role: 'admin' | 'manager' | 'viewer') => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = getAccessToken();
    if (token) {
      try {
        const userData = await api.auth.me();
        setUser(userData);
      } catch (error) {
        setAccessToken(null);
      }
    }
    setLoading(false);
  };

  const login = async (username: string, password: string) => {
    const response = await api.auth.login(username, password);
    setAccessToken(response.access_token);
    const userData = await api.auth.me();
    setUser(userData);
    navigate('/dashboard');
  };

  const register = async (data: RegisterData) => {
    const response = await api.auth.register(data);
    setAccessToken(response.access_token);
    const userData = await api.auth.me();
    setUser(userData);
    navigate('/dashboard');
  };

  const demoLogin = async (role: 'admin' | 'manager' | 'viewer') => {
    const response = await api.auth.demoLogin(role);
    setAccessToken(response.access_token);
    const userData = await api.auth.me();
    setUser(userData);
    navigate('/dashboard');
  };

  const logout = async () => {
    try {
      await api.auth.logout();
    } catch (error) {
      // Ignore errors
    }
    setAccessToken(null);
    setUser(null);
    navigate('/login');
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, demoLogin, logout }}>
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
