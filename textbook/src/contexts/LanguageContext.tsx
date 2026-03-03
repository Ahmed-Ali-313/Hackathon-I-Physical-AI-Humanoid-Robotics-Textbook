/**
 * Language Context
 * Feature: 005-urdu-translation
 * Purpose: Global language state management for preference persistence
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';

// Detect environment: localhost vs production
const API_BASE_URL = typeof window !== 'undefined'
  ? (window.location.hostname === 'localhost'
      ? 'http://localhost:8001/api/v1'
      : 'https://ai-native-book-backend.onrender.com/api/v1')
  : 'http://localhost:8001/api/v1';

interface LanguageContextType {
  preferredLanguage: string;
  setPreferredLanguage: (language: string) => Promise<void>;
  isLoading: boolean;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

interface LanguageProviderProps {
  children: ReactNode;
}

export function LanguageProvider({ children }: LanguageProviderProps) {
  const [preferredLanguage, setPreferredLanguageState] = useState<string>('en');
  const [isLoading, setIsLoading] = useState(true);

  // Load user's language preference on mount
  useEffect(() => {
    const loadPreference = async () => {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        const response = await axios.get(`${API_BASE_URL}/preferences`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.data?.preferred_language) {
          setPreferredLanguageState(response.data.preferred_language);
        }
      } catch (error) {
        console.debug('No language preference found, using default');
      } finally {
        setIsLoading(false);
      }
    };

    loadPreference();
  }, []);

  const setPreferredLanguage = async (language: string) => {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      console.warn('Cannot save language preference: not authenticated');
      return;
    }

    try {
      // Update state immediately for responsive UI
      setPreferredLanguageState(language);

      // Save to backend
      await axios.put(
        `${API_BASE_URL}/preferences`,
        { preferred_language: language },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      console.log(`Language preference saved: ${language}`);
    } catch (error) {
      console.error('Failed to save language preference:', error);
      // Revert on error
      setPreferredLanguageState(preferredLanguage);
      throw error;
    }
  };

  return (
    <LanguageContext.Provider
      value={{
        preferredLanguage,
        setPreferredLanguage,
        isLoading,
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguageContext() {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguageContext must be used within a LanguageProvider');
  }
  return context;
}
