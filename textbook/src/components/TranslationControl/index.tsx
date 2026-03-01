/**
 * TranslationControl Component
 * Feature: 005-urdu-translation
 * Purpose: Button to toggle between English and Urdu translations
 */

import React, { useState, useEffect } from 'react';
import styles from './styles.module.css';

interface TranslationControlProps {
  chapterId: string;
  originalContent: string;
  isUrdu: boolean;
  isLoading: boolean;
  error: string | null;
  onToggle: () => Promise<void>;
  onClearError: () => void;
}

export default function TranslationControl({
  chapterId,
  originalContent,
  isUrdu,
  isLoading,
  error,
  onToggle,
  onClearError
}: TranslationControlProps) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check authentication status
  useEffect(() => {
    const checkAuth = () => {
      const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
      setIsAuthenticated(!!token);
    };

    checkAuth();

    // Listen for auth changes
    window.addEventListener('storage', checkAuth);
    return () => window.removeEventListener('storage', checkAuth);
  }, []);

  const [showError, setShowError] = useState(true);

  const handleToggle = async () => {
    if (!isAuthenticated) {
      // Redirect to login
      window.location.href = '/login';
      return;
    }

    setShowError(true);
    await onToggle();
  };

  const handleDismissError = () => {
    setShowError(false);
    onClearError();
  };

  // Don't show button if not authenticated
  if (!isAuthenticated) {
    return (
      <div className={styles.translationControl}>
        <div className={styles.authMessage}>
          <span className={styles.lockIcon}>🔒</span>
          <span>
            <strong>Urdu translations are available for registered users.</strong>
            {' '}
            <a href="/signup" className={styles.signupLink}>Sign up</a>
            {' or '}
            <a href="/login" className={styles.loginLink}>log in</a>
            {' to access translations.'}
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.translationControl}>
      <button
        className={styles.toggleButton}
        onClick={handleToggle}
        disabled={isLoading}
        aria-label={isUrdu ? 'Show original English' : 'Translate to Urdu'}
      >
        {isLoading ? (
          <>
            <span className={styles.spinner} />
            <span>Translating...</span>
          </>
        ) : isUrdu ? (
          <>
            <span className={styles.icon}>🇬🇧</span>
            <span>Show Original English</span>
          </>
        ) : (
          <>
            <span className={styles.icon}>🇵🇰</span>
            <span>Translate to Urdu</span>
          </>
        )}
      </button>

      {error && showError && (
        <div className={styles.errorMessage}>
          <span className={styles.errorIcon}>⚠️</span>
          <span className={styles.errorText}>{error}</span>
          <button
            className={styles.dismissButton}
            onClick={handleDismissError}
            aria-label="Dismiss error"
          >
            ✕
          </button>
        </div>
      )}
    </div>
  );
}
