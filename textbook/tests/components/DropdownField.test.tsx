/**
 * Component tests for DropdownField
 *
 * Tests:
 * - Dropdown rendering with options
 * - Option selection
 * - "Other" option toggle
 * - "Other" text input
 * - Value change callbacks
 * - Accessibility attributes
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import DropdownField from '../../src/components/PersonalizationForm/DropdownField';

describe('DropdownField', () => {
  const defaultProps = {
    label: 'Test Field',
    name: 'test_field',
    value: '',
    onChange: jest.fn(),
    options: [
      { value: 'option1', label: 'Option 1' },
      { value: 'option2', label: 'Option 2' },
      { value: 'option3', label: 'Option 3' },
    ],
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders dropdown with label', () => {
    render(<DropdownField {...defaultProps} />);

    expect(screen.getByLabelText('Test Field')).toBeInTheDocument();
  });

  test('renders all options including "Other"', () => {
    render(<DropdownField {...defaultProps} />);

    const select = screen.getByLabelText('Test Field');
    const options = select.querySelectorAll('option');

    // Should have default empty option + 3 options + "Other"
    expect(options).toHaveLength(5);
    expect(options[0]).toHaveTextContent('Select...');
    expect(options[1]).toHaveTextContent('Option 1');
    expect(options[2]).toHaveTextContent('Option 2');
    expect(options[3]).toHaveTextContent('Option 3');
    expect(options[4]).toHaveTextContent('Other');
  });

  test('calls onChange when option is selected', () => {
    const onChange = jest.fn();
    render(<DropdownField {...defaultProps} onChange={onChange} />);

    const select = screen.getByLabelText('Test Field');
    fireEvent.change(select, { target: { value: 'option2' } });

    expect(onChange).toHaveBeenCalledWith('test_field', 'option2');
  });

  test('shows "Other" input field when "Other" is selected', () => {
    render(<DropdownField {...defaultProps} />);

    const select = screen.getByLabelText('Test Field');
    fireEvent.change(select, { target: { value: 'other' } });

    expect(screen.getByPlaceholderText(/specify/i)).toBeInTheDocument();
  });

  test('hides "Other" input field when different option selected', () => {
    render(<DropdownField {...defaultProps} />);

    const select = screen.getByLabelText('Test Field');

    // Select "Other"
    fireEvent.change(select, { target: { value: 'other' } });
    expect(screen.getByPlaceholderText(/specify/i)).toBeInTheDocument();

    // Select different option
    fireEvent.change(select, { target: { value: 'option1' } });
    expect(screen.queryByPlaceholderText(/specify/i)).not.toBeInTheDocument();
  });

  test('calls onChange with "Other" text input value', () => {
    const onChange = jest.fn();
    render(<DropdownField {...defaultProps} onChange={onChange} />);

    const select = screen.getByLabelText('Test Field');
    fireEvent.change(select, { target: { value: 'other' } });

    const otherInput = screen.getByPlaceholderText(/specify/i);
    fireEvent.change(otherInput, { target: { value: 'Custom Value' } });

    expect(onChange).toHaveBeenCalledWith('test_field', 'Custom Value');
  });

  test('displays pre-selected value', () => {
    render(<DropdownField {...defaultProps} value="option2" />);

    const select = screen.getByLabelText('Test Field') as HTMLSelectElement;
    expect(select.value).toBe('option2');
  });

  test('displays "Other" input with custom value', () => {
    render(<DropdownField {...defaultProps} value="Custom Value" />);

    // Should show "Other" selected
    const select = screen.getByLabelText('Test Field') as HTMLSelectElement;
    expect(select.value).toBe('other');

    // Should show input with custom value
    const otherInput = screen.getByPlaceholderText(/specify/i) as HTMLInputElement;
    expect(otherInput.value).toBe('Custom Value');
  });

  test('has proper accessibility attributes', () => {
    render(<DropdownField {...defaultProps} required />);

    const select = screen.getByLabelText('Test Field');
    expect(select).toHaveAttribute('id', 'test_field');
    expect(select).toHaveAttribute('name', 'test_field');
    expect(select).toBeRequired();
  });

  test('renders without "Other" option when disabled', () => {
    render(<DropdownField {...defaultProps} allowOther={false} />);

    const select = screen.getByLabelText('Test Field');
    const options = select.querySelectorAll('option');

    // Should have default empty option + 3 options (no "Other")
    expect(options).toHaveLength(4);
    expect(options[3]).not.toHaveTextContent('Other');
  });

  test('displays helper text when provided', () => {
    render(<DropdownField {...defaultProps} helperText="This is helper text" />);

    expect(screen.getByText('This is helper text')).toBeInTheDocument();
  });

  test('displays error message when provided', () => {
    render(<DropdownField {...defaultProps} error="This field is required" />);

    expect(screen.getByText('This field is required')).toBeInTheDocument();
  });

  test('applies error styling when error is present', () => {
    render(<DropdownField {...defaultProps} error="Error message" />);

    const select = screen.getByLabelText('Test Field');
    expect(select).toHaveClass('error'); // Assuming error class is applied
  });
});
