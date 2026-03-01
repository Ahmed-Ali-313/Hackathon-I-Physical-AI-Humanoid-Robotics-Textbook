/**
 * Unit Tests for useTranslation Hook
 * Task: T038
 * Feature: 005-urdu-translation
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import { useTranslation } from './useTranslation';
import { translateChapter, getCachedTranslation } from '../services/translationApi';
import { useLanguageContext } from '../contexts/LanguageContext';

// Mock the dependencies
jest.mock('../services/translationApi');
jest.mock('../contexts/LanguageContext');

describe('useTranslation Hook', () => {
  const mockChapterId = '01-test-chapter';
  const mockOriginalContent = '# Test Chapter\n\nTest content';
  const mockTranslatedContent = '# ٹیسٹ باب\n\nٹیسٹ مواد';

  let mockSetPreferredLanguage: jest.Mock;

  beforeEach(() => {
    jest.clearAllMocks();
    mockSetPreferredLanguage = jest.fn().mockResolvedValue(undefined);

    (useLanguageContext as jest.Mock).mockReturnValue({
      preferredLanguage: 'en',
      setPreferredLanguage: mockSetPreferredLanguage
    });

    (getCachedTranslation as jest.Mock).mockResolvedValue(null);
  });

  describe('Initial State', () => {
    it('should initialize with English mode when preference is "en"', () => {
      const { result } = renderHook(() =>
        useTranslation(mockChapterId, mockOriginalContent)
      );

      expect(result.current.isUrdu).toBe(false);
      expect(result.current.translatedContent).toBe(null);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBe(null);
    });

    it('should initialize with Urdu mode when preference is "ur"', () => {
      (useLanguageContext as jest.Mock).mockReturnValue({
        preferredLanguage: 'ur',
        setPreferredLanguage: mockSetPreferredLanguage
      });

      const { result } = renderHook(() =>
        useTranslation(mockChapterId, mockOriginalContent)
      );

      expect(result.current.isUrdu).toBe(true);
    });

    it('should load cached translation on mount when preference is "ur"', async () => {
      const mockCached = {
        chapter_id: mockChapterId,
        language_code: 'ur',
        translated_content: mockTranslatedContent,
        cached: true,
        translated_at: '2026-03-01T10:00:00'
      };

      (getCachedTranslation as jest.Mock).mockResolvedValue(mockCached);
      (useLanguageContext as jest.Mock).mockReturnValue({
        preferredLanguage: 'ur',
        setPreferredLanguage: mockSetPreferredLanguage
      });

      const { result } = renderHook(() =>
        useTranslation(mockChapterId, mockOriginalContent)
      );

      await waitFor(() => {
        expect(result.current.translatedContent).toBe(mockTranslatedContent);
      });

      expect(getCachedTranslation).toHaveBeenCalledWith(mockChapterId);
    });
  });

  describe('toggleLanguage - English to Urdu', () => {
    it('should fetch translation when switching to Urdu for the first time', async () => {
      const mockResponse = {
        chapter_id: mockChapterId,
        language_code: 'ur',
        translated_content: mockTranslatedContent,
        cached: false,
        translated_at: '2026-03-01T10:00:00'
      };

      (translateChapter as jest.Mock).mockResolvedValue(mockResponse);

      const { result } = renderHook(() =>
        useTranslation(mockChapterId, mockOriginalContent)
      );

      expect(result.current.isUrdu).toBe(false);

      await act(async () => {
        await result.current.toggleLanguage();
      });

      expect(translateChapter).toHaveBeenCalledWith(mockChapterId, 'ur');
      expect(result.current.isUrdu).toBe(true);
      expect(result.current.translatedContent).toBe(mockTranslatedContent);
      expect(mockSetPreferredLanguage).toHaveBeenCalledWith('ur');
    });

    it('should show loading state during translation', async () => {
      let resolveTranslation: (value: any) => void;
      const translationPromise = new Promise((resolve) => {
        resolveTranslation = resolve;
      });

      (translateChapter as jest.Mock).mockReturnValue(translationPromise);

      const { result } = renderHook(() =>
        useTranslation(mockChapterId, mockOriginalContent)
      );

      act(() => {
        result.current.toggleLanguage();
      });

      // Should be loading
      await waitFor(() => {
        expect(result.current.isLoading).toBe(true);
      });

      // Resolve the translation
      act(() => {
        resolveTranslation!({
          chapter_id: mockChapterId,
          language_code: 'ur',
          translated_content: mockTranslatedContent,
          cached: false,
          translated_at: '2026-03-01T10:00:00'
        });
      });

      // Should stop loading
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });
    });

    it('should toggle to Urdu without fetching if translation already exists', async () => {
      const mockResponse = {
        chapter_id: mockChapterId,
        language_code: 'ur',
        translated_content: mockTranslatedContent,
        cached: false,
        translated_at: '2026-03-01T10:00:00'
      };

      (translateChapter as jest.Mock).mockResolvedValue(mockResponse);

      const { result } = renderHook(() =>
        useTranslation(mockChapterId, mockOriginalContent)
      );

      // First toggle - should fetch
      await act(async () => {
        await result.current.toggleLanguage();
      });

      expect(translateChapter).toHaveBeenCalledTimes(1);

      // Toggle back to English
      await act(async () => {
        await result.current.toggleLanguage();
      });

      expect(result.current.isUrdu).toBe(false);

      // Toggle to Urdu again - should NOT fetch
      (translateChapter as jest.Mock).mockClear();

      await act(async () => {
        await result.current.toggleLanguage();
      });

      expect(translateChapter).not.toHaveBeenCalled();
      expect(result.current.isUrdu).toBe(true);
      expect(result.current.translatedContent).toBe(mockTranslatedContent);
    });
  });

  describe('toggleLanguage - Urdu to English', () => {
    it('should switch back to English without API call', async () => {
      const mockResponse = {
        chapter_id: mockChapterId,
        language_code: 'ur',
        translated_content: mockTranslatedContent,
        cached: false,
        translated_at: '2026-03-01T10:00:00'
      };

      (translateChapter as jest.Mock).mockResolvedValue(mockResponse);

      const { result } = renderHook(() =>
        useTranslation(mockChapterId, mockOriginalContent)
      );

      // Switch to Urdu first
      await act(async () => {
        await result.current.toggleLanguage();
      });

      expect(result.current.isUrdu).toBe(true);

      // Clear mock to verify no new calls
      (translateChapter as jest.Mock).mockClear();

      // Switch back to English
      await act(async () => {
        await result.current.toggleLanguage();
      });

      expect(result.current.isUrdu).toBe(false);
      expect(translateChapter).not.toHaveBeenCalled();
      expect(mockSetPreferredLanguage).toHaveBeenCalledWith('en');
    });
  });

  describe('Error Handling', () => {
    it('should set error message on 401 unauthorized', async () => {
      const error = {
        response: {
          status: 401
        }
      };

      (translateChapter as jest.Mock).mockRejectedValue(error);

      const { result } = renderHook(() =>
        useTranslation(mockChapterId, mockOriginalContent)
      );

      await act(async () => {
        await result.current.toggleLanguage();
      });

      expect(result.current.error).toBe('Please log in to access translations.');
      expect(result.current.isUrdu).toBe(false);
    });

    it('should set error message on 429 rate limit', async () => {
      const error = {
        response: {
          status: 429
        }
      };

      (translateChapter as jest.Mock).mockRejectedValue(error);

      const { result } = renderHook(() =>
        useTranslation(mockChapterId, mockOriginalContent)
      );

      await act(async () => {
        await result.current.toggleLanguage();
      });

      expect(result.current.error).toBe('Too many translation requests. Please wait a moment and try again.');
    });

    it('should set error message on 404 not found', async () => {
      const error = {
        response: {
          status: 404
        }
      };

      (translateChapter as jest.Mock).mockRejectedValue(error);

      const { result } = renderHook(() =>
        useTranslation(mockChapterId, mockOriginalContent)
      );

      await act(async () => {
        await result.current.toggleLanguage();
      });

      expect(result.current.error).toBe('Chapter not found. Please try a different chapter.');
    });

    it('should set generic error message on unknown error', async () => {
      const error = new Error('Network error');

      (translateChapter as jest.Mock).mockRejectedValue(error);

      const { result } = renderHook(() =>
        useTranslation(mockChapterId, mockOriginalContent)
      );

      await act(async () => {
        await result.current.toggleLanguage();
      });

      expect(result.current.error).toBe('Translation failed. Please try again later.');
    });

    it('should clear error when clearError is called', async () => {
      const error = {
        response: {
          status: 500
        }
      };

      (translateChapter as jest.Mock).mockRejectedValue(error);

      const { result } = renderHook(() =>
        useTranslation(mockChapterId, mockOriginalContent)
      );

      await act(async () => {
        await result.current.toggleLanguage();
      });

      expect(result.current.error).toBeTruthy();

      act(() => {
        result.current.clearError();
      });

      expect(result.current.error).toBe(null);
    });
  });

  describe('Preference Persistence', () => {
    it('should save preference when switching to Urdu', async () => {
      const mockResponse = {
        chapter_id: mockChapterId,
        language_code: 'ur',
        translated_content: mockTranslatedContent,
        cached: false,
        translated_at: '2026-03-01T10:00:00'
      };

      (translateChapter as jest.Mock).mockResolvedValue(mockResponse);

      const { result } = renderHook(() =>
        useTranslation(mockChapterId, mockOriginalContent)
      );

      await act(async () => {
        await result.current.toggleLanguage();
      });

      expect(mockSetPreferredLanguage).toHaveBeenCalledWith('ur');
    });

    it('should save preference when switching to English', async () => {
      (useLanguageContext as jest.Mock).mockReturnValue({
        preferredLanguage: 'ur',
        setPreferredLanguage: mockSetPreferredLanguage
      });

      const { result } = renderHook(() =>
        useTranslation(mockChapterId, mockOriginalContent)
      );

      await act(async () => {
        await result.current.toggleLanguage();
      });

      expect(mockSetPreferredLanguage).toHaveBeenCalledWith('en');
    });

    it('should continue even if preference save fails', async () => {
      mockSetPreferredLanguage.mockRejectedValue(new Error('Save failed'));

      const mockResponse = {
        chapter_id: mockChapterId,
        language_code: 'ur',
        translated_content: mockTranslatedContent,
        cached: false,
        translated_at: '2026-03-01T10:00:00'
      };

      (translateChapter as jest.Mock).mockResolvedValue(mockResponse);

      const { result } = renderHook(() =>
        useTranslation(mockChapterId, mockOriginalContent)
      );

      await act(async () => {
        await result.current.toggleLanguage();
      });

      // Should still switch to Urdu despite preference save failure
      expect(result.current.isUrdu).toBe(true);
      expect(result.current.translatedContent).toBe(mockTranslatedContent);
    });
  });
});
