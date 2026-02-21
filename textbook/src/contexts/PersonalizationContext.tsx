import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { PersonalizationProfile } from '../services/personalizationApi';

/**
 * View mode for content display
 */
export type ViewMode = 'personalized' | 'full';

/**
 * Personalization context state
 */
interface PersonalizationContextState {
  preferences: PersonalizationProfile | null;
  viewMode: ViewMode;
  isLoading: boolean;
  error: string | null;
  setPreferences: (preferences: PersonalizationProfile | null) => void;
  setViewMode: (mode: ViewMode) => void;
  refetchPreferences: () => Promise<void>;
}

/**
 * Default context value
 */
const defaultContextValue: PersonalizationContextState = {
  preferences: null,
  viewMode: 'personalized',
  isLoading: false,
  error: null,
  setPreferences: () => {},
  setViewMode: () => {},
  refetchPreferences: async () => {},
};

/**
 * Personalization Context
 *
 * Provides user preferences and view mode state throughout the application
 */
export const PersonalizationContext = createContext<PersonalizationContextState>(
  defaultContextValue
);

/**
 * Hook to use personalization context
 */
export const usePersonalizationContext = () => {
  const context = useContext(PersonalizationContext);
  if (!context) {
    throw new Error(
      'usePersonalizationContext must be used within PersonalizationProvider'
    );
  }
  return context;
};

/**
 * Personalization Provider Props
 */
interface PersonalizationProviderProps {
  children: ReactNode;
}

/**
 * Personalization Provider Component
 *
 * Wraps the application to provide personalization state
 */
export const PersonalizationProvider: React.FC<PersonalizationProviderProps> = ({
  children,
}) => {
  const [preferences, setPreferences] = useState<PersonalizationProfile | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('personalized');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch user preferences (memoized to prevent infinite loops)
   */
  const refetchPreferences = useCallback(async () => {
    // Check if user is authenticated
    const token = localStorage.getItem('auth_token');
    if (!token) {
      setPreferences(null);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const { getPreferences } = await import('../services/personalizationApi');
      const prefs = await getPreferences();

      // Set preferences even if null (user has no preferences yet)
      setPreferences(prefs);
      setIsLoading(false);
    } catch (err) {
      console.error('[PersonalizationContext] Failed to load preferences:', err);
      setError(err instanceof Error ? err.message : 'Failed to load preferences');
      setPreferences(null);
      setIsLoading(false);
    }
  }, []); // Empty dependency array - function doesn't depend on any props or state

  /**
   * Load preferences on mount (if user is authenticated)
   */
  useEffect(() => {
    refetchPreferences();
  }, [refetchPreferences]);

  /**
   * Save view mode to localStorage for persistence
   */
  useEffect(() => {
    localStorage.setItem('personalization_view_mode', viewMode);
  }, [viewMode]);

  /**
   * Load view mode from localStorage on mount
   */
  useEffect(() => {
    const savedViewMode = localStorage.getItem('personalization_view_mode') as ViewMode;
    if (savedViewMode === 'personalized' || savedViewMode === 'full') {
      setViewMode(savedViewMode);
    }
  }, []);

  const value: PersonalizationContextState = {
    preferences,
    viewMode,
    isLoading,
    error,
    setPreferences,
    setViewMode,
    refetchPreferences,
  };

  return (
    <PersonalizationContext.Provider value={value}>
      {children}
    </PersonalizationContext.Provider>
  );
};
