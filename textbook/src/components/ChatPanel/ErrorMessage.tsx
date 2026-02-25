/**
 * ErrorMessage component.
 *
 * Displays user-friendly error messages with retry functionality.
 */

import React from 'react';
import styles from './ErrorMessage.module.css';

interface ErrorMessageProps {
  message: string;
  errorType?: string;
  onRetry?: () => void;
  onDismiss?: () => void;
}

export default function ErrorMessage({
  message,
  errorType,
  onRetry,
  onDismiss,
}: ErrorMessageProps): JSX.Element {
  const getErrorIcon = () => {
    switch (errorType) {
      case 'authentication_expired':
        return '🔒';
      case 'connection_error':
      case 'network_error':
        return '📡';
      case 'timeout_error':
        return '⏱️';
      case 'database_error':
      case 'search_service_error':
        return '⚠️';
      default:
        return '❌';
    }
  };

  const getActionButton = () => {
    if (errorType === 'authentication_expired') {
      return (
        <a href="/login" className={styles.actionButton}>
          Log in again
        </a>
      );
    }

    if (onRetry) {
      return (
        <button
          className={styles.actionButton}
          onClick={onRetry}
          type="button"
        >
          Try again
        </button>
      );
    }

    return null;
  };

  return (
    <div className={styles.errorContainer} role="alert">
      <div className={styles.errorContent}>
        <span className={styles.errorIcon}>{getErrorIcon()}</span>
        <div className={styles.errorText}>
          <div className={styles.errorMessage}>{message}</div>
          {errorType && (
            <div className={styles.errorType}>
              Error type: {errorType.replace(/_/g, ' ')}
            </div>
          )}
        </div>
      </div>
      <div className={styles.errorActions}>
        {getActionButton()}
        {onDismiss && (
          <button
            className={styles.dismissButton}
            onClick={onDismiss}
            aria-label="Dismiss error"
            type="button"
          >
            ✕
          </button>
        )}
      </div>
    </div>
  );
}
