/**
 * Unit Tests for TranslationControl Component
 * Task: T037
 * Feature: 005-urdu-translation
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import TranslationControl from './index';
import { useTranslation } from '../../hooks/useTranslation';

// Mock the useTranslation hook
jest.mock('../../hooks/useTranslation');

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString();
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    }
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

describe('TranslationControl Component', () => {
  const mockChapterId = '01-test-chapter';
  const mockOriginalContent = '# Test Chapter\n\nTest content';

  beforeEach(() => {
    localStorageMock.clear();
    jest.clearAllMocks();
  });

  describe('Unauthenticated User', () => {
    it('should show auth message when user is not authenticated', () => {
      (useTranslation as jest.Mock).mockReturnValue({
        isUrdu: false,
        translatedContent: null,
        isLoading: false,
        error: null,
        toggleLanguage: jest.fn(),
        clearError: jest.fn()
      });

      render(
        <TranslationControl
          chapterId={mockChapterId}
          originalContent={mockOriginalContent}
        />
      );

      expect(screen.getByText(/Urdu translations are available for registered users/i)).toBeInTheDocument();
      expect(screen.getByText(/Sign up/i)).toBeInTheDocument();
      expect(screen.getByText(/log in/i)).toBeInTheDocument();
    });

    it('should not show toggle button when user is not authenticated', () => {
      (useTranslation as jest.Mock).mockReturnValue({
        isUrdu: false,
        translatedContent: null,
        isLoading: false,
        error: null,
        toggleLanguage: jest.fn(),
        clearError: jest.fn()
      });

      render(
        <TranslationControl
          chapterId={mockChapterId}
          originalContent={mockOriginalContent}
        />
      );

      expect(screen.queryByRole('button')).not.toBeInTheDocument();
    });
  });

  describe('Authenticated User', () => {
    beforeEach(() => {
      localStorageMock.setItem('auth_token', 'test-token');
    });

    it('should show "Translate to Urdu" button when in English mode', () => {
      (useTranslation as jest.Mock).mockReturnValue({
        isUrdu: false,
        translatedContent: null,
        isLoading: false,
        error: null,
        toggleLanguage: jest.fn(),
        clearError: jest.fn()
      });

      render(
        <TranslationControl
          chapterId={mockChapterId}
          originalContent={mockOriginalContent}
        />
      );

      expect(screen.getByText(/Translate to Urdu/i)).toBeInTheDocument();
      expect(screen.getByRole('button')).toBeEnabled();
    });

    it('should show "Show Original English" button when in Urdu mode', () => {
      (useTranslation as jest.Mock).mockReturnValue({
        isUrdu: true,
        translatedContent: '# ٹیسٹ باب\n\nٹیسٹ مواد',
        isLoading: false,
        error: null,
        toggleLanguage: jest.fn(),
        clearError: jest.fn()
      });

      render(
        <TranslationControl
          chapterId={mockChapterId}
          originalContent={mockOriginalContent}
        />
      );

      expect(screen.getByText(/Show Original English/i)).toBeInTheDocument();
    });

    it('should call toggleLanguage when button is clicked', async () => {
      const mockToggleLanguage = jest.fn();
      (useTranslation as jest.Mock).mockReturnValue({
        isUrdu: false,
        translatedContent: null,
        isLoading: false,
        error: null,
        toggleLanguage: mockToggleLanguage,
        clearError: jest.fn()
      });

      render(
        <TranslationControl
          chapterId={mockChapterId}
          originalContent={mockOriginalContent}
        />
      );

      const button = screen.getByRole('button');
      fireEvent.click(button);

      await waitFor(() => {
        expect(mockToggleLanguage).toHaveBeenCalledTimes(1);
      });
    });

    it('should show loading state during translation', () => {
      (useTranslation as jest.Mock).mockReturnValue({
        isUrdu: false,
        translatedContent: null,
        isLoading: true,
        error: null,
        toggleLanguage: jest.fn(),
        clearError: jest.fn()
      });

      render(
        <TranslationControl
          chapterId={mockChapterId}
          originalContent={mockOriginalContent}
        />
      );

      expect(screen.getByText(/Translating.../i)).toBeInTheDocument();
      expect(screen.getByRole('button')).toBeDisabled();
    });

    it('should display error message when translation fails', () => {
      (useTranslation as jest.Mock).mockReturnValue({
        isUrdu: false,
        translatedContent: null,
        isLoading: false,
        error: 'Translation failed',
        toggleLanguage: jest.fn(),
        clearError: jest.fn()
      });

      render(
        <TranslationControl
          chapterId={mockChapterId}
          originalContent={mockOriginalContent}
        />
      );

      expect(screen.getByText(/Translation failed/i)).toBeInTheDocument();
    });

    it('should clear error when dismiss button is clicked', async () => {
      const mockClearError = jest.fn();
      (useTranslation as jest.Mock).mockReturnValue({
        isUrdu: false,
        translatedContent: null,
        isLoading: false,
        error: 'Translation failed',
        toggleLanguage: jest.fn(),
        clearError: mockClearError
      });

      render(
        <TranslationControl
          chapterId={mockChapterId}
          originalContent={mockOriginalContent}
        />
      );

      const dismissButton = screen.getByLabelText(/dismiss/i);
      fireEvent.click(dismissButton);

      await waitFor(() => {
        expect(mockClearError).toHaveBeenCalledTimes(1);
      });
    });
  });

  describe('Accessibility', () => {
    beforeEach(() => {
      localStorageMock.setItem('auth_token', 'test-token');
    });

    it('should have proper aria-label for English mode', () => {
      (useTranslation as jest.Mock).mockReturnValue({
        isUrdu: false,
        translatedContent: null,
        isLoading: false,
        error: null,
        toggleLanguage: jest.fn(),
        clearError: jest.fn()
      });

      render(
        <TranslationControl
          chapterId={mockChapterId}
          originalContent={mockOriginalContent}
        />
      );

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', 'Translate to Urdu');
    });

    it('should have proper aria-label for Urdu mode', () => {
      (useTranslation as jest.Mock).mockReturnValue({
        isUrdu: true,
        translatedContent: '# ٹیسٹ',
        isLoading: false,
        error: null,
        toggleLanguage: jest.fn(),
        clearError: jest.fn()
      });

      render(
        <TranslationControl
          chapterId={mockChapterId}
          originalContent={mockOriginalContent}
        />
      );

      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', 'Show original English');
    });
  });
});
