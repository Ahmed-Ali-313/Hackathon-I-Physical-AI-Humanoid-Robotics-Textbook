/**
 * Tests for ErrorMessage component.
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ErrorMessage from '../../src/components/ChatPanel/ErrorMessage';

describe('ErrorMessage', () => {
  test('renders error message', () => {
    render(<ErrorMessage message="Test error message" />);

    expect(screen.getByText('Test error message')).toBeInTheDocument();
    expect(screen.getByRole('alert')).toBeInTheDocument();
  });

  test('displays error type when provided', () => {
    render(
      <ErrorMessage
        message="Database error"
        errorType="database_error"
      />
    );

    expect(screen.getByText(/Error type: database error/i)).toBeInTheDocument();
  });

  test('shows authentication icon for auth errors', () => {
    render(
      <ErrorMessage
        message="Session expired"
        errorType="authentication_expired"
      />
    );

    expect(screen.getByText('🔒')).toBeInTheDocument();
  });

  test('shows connection icon for network errors', () => {
    render(
      <ErrorMessage
        message="Connection failed"
        errorType="connection_error"
      />
    );

    expect(screen.getByText('📡')).toBeInTheDocument();
  });

  test('shows timeout icon for timeout errors', () => {
    render(
      <ErrorMessage
        message="Request timeout"
        errorType="timeout_error"
      />
    );

    expect(screen.getByText('⏱️')).toBeInTheDocument();
  });

  test('shows warning icon for service errors', () => {
    render(
      <ErrorMessage
        message="Service unavailable"
        errorType="database_error"
      />
    );

    expect(screen.getByText('⚠️')).toBeInTheDocument();
  });

  test('shows default error icon for unknown errors', () => {
    render(
      <ErrorMessage
        message="Unknown error"
        errorType="unknown_error"
      />
    );

    expect(screen.getByText('❌')).toBeInTheDocument();
  });

  test('displays login link for authentication errors', () => {
    render(
      <ErrorMessage
        message="Session expired"
        errorType="authentication_expired"
      />
    );

    const loginLink = screen.getByText('Log in again');
    expect(loginLink).toBeInTheDocument();
    expect(loginLink).toHaveAttribute('href', '/login');
  });

  test('displays retry button when onRetry provided', () => {
    const handleRetry = jest.fn();

    render(
      <ErrorMessage
        message="Connection failed"
        onRetry={handleRetry}
      />
    );

    const retryButton = screen.getByText('Try again');
    expect(retryButton).toBeInTheDocument();

    fireEvent.click(retryButton);
    expect(handleRetry).toHaveBeenCalledTimes(1);
  });

  test('displays dismiss button when onDismiss provided', () => {
    const handleDismiss = jest.fn();

    render(
      <ErrorMessage
        message="Test error"
        onDismiss={handleDismiss}
      />
    );

    const dismissButton = screen.getByLabelText('Dismiss error');
    expect(dismissButton).toBeInTheDocument();

    fireEvent.click(dismissButton);
    expect(handleDismiss).toHaveBeenCalledTimes(1);
  });

  test('does not show retry button for auth errors', () => {
    const handleRetry = jest.fn();

    render(
      <ErrorMessage
        message="Session expired"
        errorType="authentication_expired"
        onRetry={handleRetry}
      />
    );

    expect(screen.queryByText('Try again')).not.toBeInTheDocument();
    expect(screen.getByText('Log in again')).toBeInTheDocument();
  });

  test('shows both retry and dismiss buttons when both provided', () => {
    const handleRetry = jest.fn();
    const handleDismiss = jest.fn();

    render(
      <ErrorMessage
        message="Connection failed"
        onRetry={handleRetry}
        onDismiss={handleDismiss}
      />
    );

    expect(screen.getByText('Try again')).toBeInTheDocument();
    expect(screen.getByLabelText('Dismiss error')).toBeInTheDocument();
  });

  test('formats error type with spaces', () => {
    render(
      <ErrorMessage
        message="Error occurred"
        errorType="connection_error"
      />
    );

    expect(screen.getByText(/Error type: connection error/i)).toBeInTheDocument();
  });
});
