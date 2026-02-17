/**
 * Component tests for PersonalizationForm
 *
 * Tests:
 * - Form rendering with all fields
 * - Dropdown field interactions
 * - "Other" field toggle and input
 * - Form validation
 * - Form submission
 * - Error handling
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import PersonalizationForm from '../../src/components/PersonalizationForm';
import { PersonalizationProvider } from '../../src/contexts/PersonalizationContext';

// Mock API
jest.mock('../../src/services/personalizationApi', () => ({
  createPreferences: jest.fn(),
  updatePreferences: jest.fn(),
}));

describe('PersonalizationForm', () => {
  const renderForm = (props = {}) => {
    return render(
      <PersonalizationProvider>
        <PersonalizationForm {...props} />
      </PersonalizationProvider>
    );
  };

  test('renders all hardware preference fields', () => {
    renderForm();

    expect(screen.getByLabelText(/workstation type/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/edge kit available/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/robot tier access/i)).toBeInTheDocument();
  });

  test('renders all software experience fields', () => {
    renderForm();

    expect(screen.getByLabelText(/ros2 experience/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/gazebo experience/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/unity experience/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/isaac sim experience/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/vla experience/i)).toBeInTheDocument();
  });

  test('shows "Other" input field when "Other" is selected', async () => {
    renderForm();

    const workstationDropdown = screen.getByLabelText(/workstation type/i);
    fireEvent.change(workstationDropdown, { target: { value: 'other' } });

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/specify your workstation/i)).toBeInTheDocument();
    });
  });

  test('hides "Other" input field when different option selected', async () => {
    renderForm();

    const workstationDropdown = screen.getByLabelText(/workstation type/i);

    // Select "Other"
    fireEvent.change(workstationDropdown, { target: { value: 'other' } });
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/specify your workstation/i)).toBeInTheDocument();
    });

    // Select different option
    fireEvent.change(workstationDropdown, { target: { value: 'high_end_desktop' } });
    await waitFor(() => {
      expect(screen.queryByPlaceholderText(/specify your workstation/i)).not.toBeInTheDocument();
    });
  });

  test('validates form before submission', async () => {
    const onSubmit = jest.fn();
    renderForm({ onSubmit });

    const submitButton = screen.getByRole('button', { name: /save preferences/i });
    fireEvent.click(submitButton);

    // Should show validation error if no fields filled
    await waitFor(() => {
      expect(screen.getByText(/please select at least one preference/i)).toBeInTheDocument();
    });

    expect(onSubmit).not.toHaveBeenCalled();
  });

  test('submits form with valid data', async () => {
    const { createPreferences } = require('../../src/services/personalizationApi');
    createPreferences.mockResolvedValue({
      id: '123',
      workstation_type: 'high_end_desktop',
      ros2_level: 'intermediate',
    });

    renderForm();

    // Fill form
    fireEvent.change(screen.getByLabelText(/workstation type/i), {
      target: { value: 'high_end_desktop' }
    });
    fireEvent.change(screen.getByLabelText(/ros2 experience/i), {
      target: { value: 'intermediate' }
    });

    // Submit
    const submitButton = screen.getByRole('button', { name: /save preferences/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(createPreferences).toHaveBeenCalledWith({
        workstation_type: 'high_end_desktop',
        ros2_level: 'intermediate',
      });
    });
  });

  test('displays error message on submission failure', async () => {
    const { createPreferences } = require('../../src/services/personalizationApi');
    createPreferences.mockRejectedValue(new Error('Network error'));

    renderForm();

    // Fill and submit form
    fireEvent.change(screen.getByLabelText(/workstation type/i), {
      target: { value: 'laptop' }
    });
    fireEvent.click(screen.getByRole('button', { name: /save preferences/i }));

    await waitFor(() => {
      expect(screen.getByText(/failed to save preferences/i)).toBeInTheDocument();
    });
  });

  test('disables submit button while submitting', async () => {
    const { createPreferences } = require('../../src/services/personalizationApi');
    createPreferences.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

    renderForm();

    fireEvent.change(screen.getByLabelText(/workstation type/i), {
      target: { value: 'laptop' }
    });

    const submitButton = screen.getByRole('button', { name: /save preferences/i });
    fireEvent.click(submitButton);

    expect(submitButton).toBeDisabled();
  });

  test('pre-fills form with existing preferences in edit mode', () => {
    const existingPreferences = {
      workstation_type: 'high_end_desktop',
      ros2_level: 'advanced',
      gazebo_level: 'intermediate',
    };

    renderForm({ initialValues: existingPreferences, mode: 'edit' });

    expect(screen.getByLabelText(/workstation type/i)).toHaveValue('high_end_desktop');
    expect(screen.getByLabelText(/ros2 experience/i)).toHaveValue('advanced');
    expect(screen.getByLabelText(/gazebo experience/i)).toHaveValue('intermediate');
  });
});
