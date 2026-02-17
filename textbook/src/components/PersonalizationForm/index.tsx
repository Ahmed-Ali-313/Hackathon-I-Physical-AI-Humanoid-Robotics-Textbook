/**
 * PersonalizationForm Component
 *
 * Form for collecting user hardware and software preferences.
 * Used during signup and in profile settings.
 */

import React, { useState, useEffect } from 'react';
import DropdownField from './DropdownField';
import { createPreferences, updatePreferences, PreferenceInput } from '../../services/personalizationApi';
import styles from './styles.module.css';

interface PersonalizationFormProps {
  mode?: 'create' | 'edit';
  initialValues?: Partial<PreferenceInput>;
  onSubmit?: (preferences: PreferenceInput) => void;
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

const PersonalizationForm: React.FC<PersonalizationFormProps> = ({
  mode = 'create',
  initialValues = {},
  onSubmit,
  onSuccess,
  onError,
}) => {
  const [formData, setFormData] = useState<Partial<PreferenceInput>>(initialValues);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Hardware options
  const workstationOptions = [
    { value: 'laptop', label: 'Laptop' },
    { value: 'mid_range_desktop', label: 'Mid-Range Desktop' },
    { value: 'high_end_desktop', label: 'High-End Desktop' },
    { value: 'workstation', label: 'Workstation' },
    { value: 'cloud_instance', label: 'Cloud Instance' },
  ];

  const edgeKitOptions = [
    { value: 'none', label: 'None' },
    { value: 'jetson_nano', label: 'NVIDIA Jetson Nano' },
    { value: 'jetson_orin', label: 'NVIDIA Jetson Orin' },
    { value: 'raspberry_pi', label: 'Raspberry Pi' },
  ];

  const robotTierOptions = [
    { value: 'none', label: 'None' },
    { value: 'tier_1', label: 'Tier 1 (Basic)' },
    { value: 'tier_2', label: 'Tier 2 (Intermediate)' },
    { value: 'tier_3', label: 'Tier 3 (Advanced)' },
  ];

  // Software experience options
  const experienceLevelOptions = [
    { value: 'none', label: 'None' },
    { value: 'beginner', label: 'Beginner' },
    { value: 'intermediate', label: 'Intermediate' },
    { value: 'advanced', label: 'Advanced' },
  ];

  const handleFieldChange = (name: string, value: string) => {
    setFormData((prev) => ({ ...prev, [name]: value }));
    setErrorMessage(null);
  };

  const validateForm = (): boolean => {
    // At least one preference must be selected
    const hasAtLeastOne = Object.values(formData).some(
      (value) => value !== null && value !== undefined && value !== ''
    );

    if (!hasAtLeastOne) {
      setErrorMessage('Please select at least one preference');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setSuccessMessage(null);

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      // Call custom onSubmit if provided
      if (onSubmit) {
        onSubmit(formData as PreferenceInput);
      }

      // Call API
      if (mode === 'create') {
        await createPreferences(formData as PreferenceInput);
        setSuccessMessage('Preferences saved successfully!');
      } else {
        await updatePreferences(formData as PreferenceInput);
        setSuccessMessage('Preferences updated successfully!');
      }

      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to save preferences';
      setErrorMessage(message);
      if (onError) {
        onError(message);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>Hardware Preferences</h3>
        <p className={styles.sectionDescription}>
          Tell us about your hardware setup to personalize content recommendations
        </p>

        <DropdownField
          label="Workstation Type"
          name="workstation_type"
          value={formData.workstation_type || ''}
          onChange={handleFieldChange}
          options={workstationOptions}
          helperText="What type of computer do you primarily use?"
        />

        <DropdownField
          label="Edge Kit Available"
          name="edge_kit_available"
          value={formData.edge_kit_available || ''}
          onChange={handleFieldChange}
          options={edgeKitOptions}
          helperText="Do you have access to edge computing hardware?"
        />

        <DropdownField
          label="Robot Tier Access"
          name="robot_tier_access"
          value={formData.robot_tier_access || ''}
          onChange={handleFieldChange}
          options={robotTierOptions}
          helperText="What level of robot hardware do you have access to?"
        />
      </div>

      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>Software Experience</h3>
        <p className={styles.sectionDescription}>
          Help us understand your experience level with different tools
        </p>

        <DropdownField
          label="ROS2 Experience"
          name="ros2_level"
          value={formData.ros2_level || ''}
          onChange={handleFieldChange}
          options={experienceLevelOptions}
          allowOther={false}
        />

        <DropdownField
          label="Gazebo Experience"
          name="gazebo_level"
          value={formData.gazebo_level || ''}
          onChange={handleFieldChange}
          options={experienceLevelOptions}
          allowOther={false}
        />

        <DropdownField
          label="Unity Experience"
          name="unity_level"
          value={formData.unity_level || ''}
          onChange={handleFieldChange}
          options={experienceLevelOptions}
          allowOther={false}
        />

        <DropdownField
          label="Isaac Sim Experience"
          name="isaac_level"
          value={formData.isaac_level || ''}
          onChange={handleFieldChange}
          options={experienceLevelOptions}
          allowOther={false}
        />

        <DropdownField
          label="VLA Experience"
          name="vla_level"
          value={formData.vla_level || ''}
          onChange={handleFieldChange}
          options={experienceLevelOptions}
          allowOther={false}
        />
      </div>

      {errorMessage && (
        <div className={styles.errorMessage}>{errorMessage}</div>
      )}

      {successMessage && (
        <div className={styles.successMessage}>{successMessage}</div>
      )}

      <button
        type="submit"
        disabled={isSubmitting}
        className={styles.submitButton}
      >
        {isSubmitting ? 'Saving...' : mode === 'create' ? 'Save Preferences' : 'Update Preferences'}
      </button>
    </form>
  );
};

export default PersonalizationForm;
