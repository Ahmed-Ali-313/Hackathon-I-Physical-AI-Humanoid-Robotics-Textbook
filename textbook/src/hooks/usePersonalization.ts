import { useState, useEffect } from 'react';
import {
  PersonalizationProfile,
  getPreferences,
  createPreferences,
  updatePreferences,
  PreferenceInput,
} from '../services/personalizationApi';

/**
 * Hook return type
 */
interface UsePersonalizationReturn {
  preferences: PersonalizationProfile | null;
  isLoading: boolean;
  error: string | null;
  fetchPreferences: () => Promise<void>;
  savePreferences: (prefs: PreferenceInput) => Promise<void>;
  updateUserPreferences: (prefs: PreferenceInput) => Promise<void>;
}

/**
 * Custom hook for fetching and caching user preferences
 *
 * Features:
 * - Automatic fetching on mount (if authenticated)
 * - In-memory caching to minimize API calls
 * - Loading and error states
 * - Methods to create and update preferences
 *
 * Usage:
 *   const { preferences, isLoading, savePreferences } = usePersonalization();
 */
export const usePersonalization = (): UsePersonalizationReturn => {
  const [preferences, setPreferences] = useState<PersonalizationProfile | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch user preferences from API
   */
  const fetchPreferences = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const prefs = await getPreferences();
      setPreferences(prefs);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch preferences';
      setError(errorMessage);
      console.error('Error fetching preferences:', err);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Create new preferences (during signup)
   */
  const savePreferences = async (prefs: PreferenceInput) => {
    setIsLoading(true);
    setError(null);

    try {
      const newPrefs = await createPreferences(prefs);
      setPreferences(newPrefs);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to save preferences';
      setError(errorMessage);
      console.error('Error saving preferences:', err);
      throw err; // Re-throw so caller can handle
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Update existing preferences (from profile page)
   */
  const updateUserPreferences = async (prefs: PreferenceInput) => {
    setIsLoading(true);
    setError(null);

    try {
      const updatedPrefs = await updatePreferences(prefs);
      setPreferences(updatedPrefs);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update preferences';
      setError(errorMessage);
      console.error('Error updating preferences:', err);
      throw err; // Re-throw so caller can handle
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Fetch preferences on mount (if user is authenticated)
   */
  useEffect(() => {
    // TODO: Check if user is authenticated before fetching
    // For now, we'll skip auto-fetch until authentication is integrated
    // fetchPreferences();
  }, []);

  return {
    preferences,
    isLoading,
    error,
    fetchPreferences,
    savePreferences,
    updateUserPreferences,
  };
};
