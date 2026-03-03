/**
 * Authentication API Service
 *
 * Handles all authentication-related API calls.
 */

const API_URL = typeof window !== 'undefined'
  ? (window.location.hostname === 'localhost'
      ? 'http://localhost:8001'
      : 'https://ai-native-book-backend.onrender.com')
  : 'http://localhost:8001';

export interface SignupRequest {
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  email: string;
}

export interface User {
  id: string;
  email: string;
}

export async function signup(data: SignupRequest): Promise<AuthResponse> {
  const response = await fetch(`${API_URL}/api/v1/auth/signup`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Signup failed');
  }

  return response.json();
}

export async function login(data: LoginRequest): Promise<AuthResponse> {
  const response = await fetch(`${API_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Login failed');
  }

  return response.json();
}

export async function getCurrentUser(token: string): Promise<User> {
  const response = await fetch(`${API_URL}/api/v1/auth/me`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error('Failed to get user');
  }

  return response.json();
}

export function saveToken(token: string): void {
  localStorage.setItem('auth_token', token);
}

export function getToken(): string | null {
  return localStorage.getItem('auth_token');
}

export function removeToken(): void {
  localStorage.removeItem('auth_token');
}
