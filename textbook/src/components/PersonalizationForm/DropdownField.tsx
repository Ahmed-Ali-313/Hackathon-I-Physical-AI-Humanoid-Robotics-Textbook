/**
 * DropdownField Component
 *
 * Reusable dropdown field with "Other" option support.
 * When "Other" is selected, shows a text input for custom values.
 */

import React, { useState, useEffect } from 'react';
import styles from './styles.module.css';

interface DropdownOption {
  value: string;
  label: string;
}

interface DropdownFieldProps {
  label: string;
  name: string;
  value: string;
  onChange: (name: string, value: string) => void;
  options: DropdownOption[];
  required?: boolean;
  allowOther?: boolean;
  helperText?: string;
  error?: string;
}

const DropdownField: React.FC<DropdownFieldProps> = ({
  label,
  name,
  value,
  onChange,
  options,
  required = false,
  allowOther = true,
  helperText,
  error,
}) => {
  const [showOtherInput, setShowOtherInput] = useState(false);
  const [otherValue, setOtherValue] = useState('');

  // Check if current value is a custom "Other" value
  useEffect(() => {
    const isStandardOption = options.some(opt => opt.value === value);
    if (value && !isStandardOption && value !== 'other') {
      setShowOtherInput(true);
      setOtherValue(value);
    } else {
      setShowOtherInput(value === 'other');
    }
  }, [value, options]);

  const handleSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedValue = e.target.value;

    if (selectedValue === 'other') {
      setShowOtherInput(true);
      setOtherValue('');
    } else {
      setShowOtherInput(false);
      setOtherValue('');
      onChange(name, selectedValue);
    }
  };

  const handleOtherInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const customValue = e.target.value;
    setOtherValue(customValue);
    onChange(name, customValue);
  };

  // Determine select value
  const selectValue = showOtherInput ? 'other' : (value || '');

  return (
    <div className={styles.fieldGroup}>
      <label htmlFor={name} className={styles.label}>
        {label}
        {required && <span className={styles.required}>*</span>}
      </label>

      <select
        id={name}
        name={name}
        value={selectValue}
        onChange={handleSelectChange}
        required={required}
        className={`${styles.select} ${error ? styles.error : ''}`}
      >
        <option value="">Select...</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
        {allowOther && <option value="other">Other</option>}
      </select>

      {showOtherInput && (
        <input
          type="text"
          value={otherValue}
          onChange={handleOtherInputChange}
          placeholder={`Specify your ${label.toLowerCase()}`}
          className={styles.otherInput}
          required={required}
        />
      )}

      {helperText && !error && (
        <span className={styles.helperText}>{helperText}</span>
      )}

      {error && <span className={styles.errorText}>{error}</span>}
    </div>
  );
};

export default DropdownField;
