/**
 * Component tests for Profile page - Phase 5
 *
 * Tests:
 * - Profile page rendering with current preferences
 * - Preference update functionality
 * - Clear all preferences functionality
 * - Success/error message display
 * - Context refetch after update
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ProfilePage from '../../src/pages/profile';
import { PersonalizationContext } from '../../src/contexts/PersonalizationContext';
import * as personalizationApi from '../../src/services/personalizationApi';

// Mock the API
jest.mock('../../src/services/personalizationApi');

describe('ProfilePage', () => {
  const mockPreferences = {
    id: '123',
    user_id: '456',
    workstation_type: 'high_end_desktop',
    edge_kit_available: 'jetson_orin',
    ros2_level: 'intermediate',
    gazebo_level: 'beginner',
    is_personalized: true,
    created_at: '2024-01-01',
    updated_at: '2024-01-01',
  };

  const mockRefetchPreferences = jest.fn();
  const mockSetPreferences = jest.fn();

  const mockContextValue = {
    preferences: mockPreferences,
    viewMode: 'personalized' as const,
    isLoading: false,
    error: null,
    setPreferences: mockSetPreferences,
    setViewMode: jest.fn(),
    refetchPreferences: mockRefetchPreferences,
  };

  const renderWithContext = (contextValue = mockContextValue) => {
    return render(
      <PersonalizationContext.Provider value={contextValue}>
        <ProfilePage />
      </PersonalizationContext.Provider>
    );
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders profile page with current preferences', () => {
    renderWithContext();

    expect(screen.getByText(/your profile/i)).toBeInTheDocument();
    expect(screen.getByDisplayValue('high_end_desktop')).toBeInTheDocument();
    expect(screen.getByDisplayValue('intermediate')).toBeInTheDocument();
  });

  test('displays loading state while fetching preferences', () => {
    renderWithContext({
      ...mockContextValue,
      isLoading: true,
      preferences: null,
    });

    expect(screen.getByText(/loading preferences/i)).toBeInTheDocument();
  });

  test('displays error message when preferences fail to load', () => {
    renderWithContext({
      ...mockContextValue,
      error: 'Failed to load preferences',
      preferences: null,
    });

    expect(screen.getByText(/failed to load preferences/i)).toBeInTheDocument();
  });

  test('updates preferences successfully', async () => {
    (personalizationApi.updatePreferences as jest.Mock).mockResolvedValue({
      ...mockPreferences,
      ros2_level: 'advanced',
    });

    renderWithContext();

    // Change ROS2 level
    const ros2Select = screen.getByLabelText(/ros2 experience/i);
    fireEvent.change(ros2Select, { target: { value: 'advanced' } });

    // Click save
    const saveButton = screen.getByRole('button', { name: /update preferences/i });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(personalizationApi.updatePreferences).toHaveBeenCalledWith(
        expect.objectContaining({
          ros2_level: 'advanced',
        })
      );
    });

    // Should refetch preferences
    await waitFor(() => {
      expect(mockRefetchPreferences).toHaveBeenCalled();
    });

    // Should show success message
    expect(screen.getByText(/preferences updated successfully/i)).toBeInTheDocument();
  });

  test('displays error message when update fails', async () => {
    (personalizationApi.updatePreferences as jest.Mock).mockRejectedValue(
      new Error('Update failed')
    );

    renderWithContext();

    const saveButton = screen.getByRole('button', { name: /update preferences/i });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(screen.getByText(/failed to update preferences/i)).toBeInTheDocument();
    });
  });

  test('clears all preferences successfully', async () => {
    (personalizationApi.clearPreferences as jest.Mock).mockResolvedValue(undefined);

    renderWithContext();

    const clearButton = screen.getByRole('button', { name: /clear all preferences/i });
    fireEvent.click(clearButton);

    // Should show confirmation dialog
    const confirmButton = screen.getByRole('button', { name: /confirm/i });
    fireEvent.click(confirmButton);

    await waitFor(() => {
      expect(personalizationApi.clearPreferences).toHaveBeenCalled();
    });

    // Should refetch preferences
    await waitFor(() => {
      expect(mockRefetchPreferences).toHaveBeenCalled();
    });

    // Should show success message
    expect(screen.getByText(/preferences cleared successfully/i)).toBeInTheDocument();
  });

  test('shows confirmation dialog before clearing preferences', () => {
    renderWithContext();

    const clearButton = screen.getByRole('button', { name: /clear all preferences/i });
    fireEvent.click(clearButton);

    expect(screen.getByText(/are you sure/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /confirm/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
  });

  test('cancels clear preferences action', () => {
    renderWithContext();

    const clearButton = screen.getByRole('button', { name: /clear all preferences/i });
    fireEvent.click(clearButton);

    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    fireEvent.click(cancelButton);

    expect(personalizationApi.clearPreferences).not.toHaveBeenCalled();
    expect(screen.queryByText(/are you sure/i)).not.toBeInTheDocument();
  });

  test('disables save button while updating', async () => {
    (personalizationApi.updatePreferences as jest.Mock).mockImplementation(
      () => new Promise(resolve => setTimeout(resolve, 100))
    );

    renderWithContext();

    const saveButton = screen.getByRole('button', { name: /update preferences/i });
    fireEvent.click(saveButton);

    expect(saveButton).toBeDisabled();
  });

  test('shows create preferences form when user has no preferences', () => {
    renderWithContext({
      ...mockContextValue,
      preferences: null,
    });

    expect(screen.getByText(/set up your preferences/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /save preferences/i })).toBeInTheDocument();
  });
});
