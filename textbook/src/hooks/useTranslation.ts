/**
 * useTranslation Hook
 * Feature: 005-urdu-translation
 * Purpose: Manage translation state and API calls with preference persistence
 */

import { useState, useEffect, useCallback } from 'react';
import { translateChapter, getCachedTranslation } from '../services/translationApi';
import { useLanguageContext } from '../contexts/LanguageContext';

interface UseTranslationReturn {
  isUrdu: boolean;
  translatedContent: string | null;
  isLoading: boolean;
  error: string | null;
  toggleLanguage: () => Promise<void>;
  clearError: () => void;
}

export function useTranslation(
  chapterId: string,
  originalContent: string
): UseTranslationReturn {
  const { preferredLanguage, setPreferredLanguage } = useLanguageContext();
  const [isUrdu, setIsUrdu] = useState(preferredLanguage === 'ur');
  const [translatedContent, setTranslatedContent] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Sync with global language preference
  useEffect(() => {
    setIsUrdu(preferredLanguage === 'ur');
  }, [preferredLanguage]);

  // Load cached translation on mount if preference is Urdu
  useEffect(() => {
    const loadCachedTranslation = async () => {
      if (preferredLanguage === 'ur') {
        try {
          const cached = await getCachedTranslation(chapterId);
          if (cached) {
            setTranslatedContent(cached.translated_content);
          }
        } catch (err) {
          // Silently fail - cache miss is expected
          console.debug('No cached translation found');
        }
      }
    };

    loadCachedTranslation();
  }, [chapterId, preferredLanguage]);

  const toggleLanguage = useCallback(async () => {
    if (isUrdu) {
      // Switch back to English
      setIsUrdu(false);
      setError(null);

      // Save preference
      try {
        await setPreferredLanguage('en');
      } catch (err) {
        console.error('Failed to save language preference:', err);
      }
      return;
    }

    // Switch to Urdu
    if (translatedContent) {
      // Already have translation, just toggle
      setIsUrdu(true);
      setError(null);

      // Save preference
      try {
        await setPreferredLanguage('ur');
      } catch (err) {
        console.error('Failed to save language preference:', err);
      }
      return;
    }

    // Need to fetch translation
    setIsLoading(true);
    setError(null);

    try {
      const response = await translateChapter(chapterId, 'ur');
      setTranslatedContent(response.translated_content);
      setIsUrdu(true);

      // Save preference
      try {
        await setPreferredLanguage('ur');
      } catch (err) {
        console.error('Failed to save language preference:', err);
      }
    } catch (err: any) {
      console.error('Translation error:', err);

      // User-friendly error messages
      if (err.response?.status === 401) {
        setError('Please log in to access translations.');
      } else if (err.response?.status === 429) {
        setError('Too many translation requests. Please wait a moment and try again.');
      } else if (err.response?.status === 404) {
        setError('Chapter not found. Please try a different chapter.');
      } else if (err.response?.data?.detail?.message) {
        setError(err.response.data.detail.message);
      } else {
        setError('Translation failed. Please try again later.');
      }
    } finally {
      setIsLoading(false);
    }
  }, [chapterId, isUrdu, translatedContent, setPreferredLanguage]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    isUrdu,
    translatedContent,
    isLoading,
    error,
    toggleLanguage,
    clearError
  };
}
