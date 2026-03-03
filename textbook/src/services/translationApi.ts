/**
 * Translation API Service
 * Feature: 005-urdu-translation
 * Purpose: API client for translation endpoints
 */

import axios from 'axios';

// Detect environment: localhost vs production
const API_BASE_URL = typeof window !== 'undefined'
  ? (window.location.hostname === 'localhost'
      ? 'http://localhost:8001/api/v1'
      : 'https://ai-native-book-backend.onrender.com/api/v1')
  : 'http://localhost:8001/api/v1';

// Get auth token from localStorage
const getAuthToken = (): string | null => {
  return localStorage.getItem('auth_token');
};

// Create axios instance with auth header
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = getAuthToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response types
export interface TranslateResponse {
  chapter_id: string;
  language_code: string;
  translated_content: string;
  cached: boolean;
  translated_at: string;
}

export interface TranslateRequest {
  chapter_id: string;
  language_code: string;
  force_refresh?: boolean;
}

/**
 * Translate a chapter to target language.
 *
 * @param chapterId - Chapter identifier (e.g., "01-introduction-to-ros2")
 * @param languageCode - Target language code (default: "ur")
 * @param forceRefresh - Force fresh translation, bypass cache
 * @returns Translation response with content
 */
export async function translateChapter(
  chapterId: string,
  languageCode: string = 'ur',
  forceRefresh: boolean = false
): Promise<TranslateResponse> {
  const response = await apiClient.post<TranslateResponse>('/translate', {
    chapter_id: chapterId,
    language_code: languageCode,
    force_refresh: forceRefresh,
  });

  return response.data;
}

/**
 * Get cached translation for a chapter.
 *
 * @param chapterId - Chapter identifier
 * @param languageCode - Language code (default: "ur")
 * @returns Cached translation if available
 * @throws Error if translation not found in cache
 */
export async function getCachedTranslation(
  chapterId: string,
  languageCode: string = 'ur'
): Promise<TranslateResponse> {
  const response = await apiClient.get<TranslateResponse>(
    `/translate/${chapterId}`,
    {
      params: { language_code: languageCode },
    }
  );

  return response.data;
}

/**
 * Update user's language preference.
 *
 * @param preferredLanguage - Preferred language code ("en" or "ur")
 * @returns Updated preference
 */
export async function updateLanguagePreference(
  preferredLanguage: string
): Promise<{ user_id: string; preferred_language: string; updated_at: string }> {
  const response = await apiClient.put('/user/preferences', {
    preferred_language: preferredLanguage,
  });

  return response.data;
}

/**
 * Get user's current language preference.
 *
 * @returns User's language preference
 */
export async function getLanguagePreference(): Promise<{
  user_id: string;
  preferred_language: string;
}> {
  const response = await apiClient.get('/user/preferences');
  return response.data;
}
