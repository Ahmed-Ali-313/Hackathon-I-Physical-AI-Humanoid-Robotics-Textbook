/**
 * PreferenceBanner Component
 *
 * Dismissible banner prompting non-personalized users to set preferences.
 * Persists dismissal state to localStorage.
 */

import React, { useState, useEffect } from 'react';
import { usePersonalizationContext } from '../../contexts/PersonalizationContext';
import styles from './styles.module.css';

const PreferenceBanner: React.FC = () => {
  const { preferences } = usePersonalizationContext();
  const [isDismissed, setIsDismissed] = useState(false);

  useEffect(() => {
    // Check if banner was previously dismissed
    const dismissed = localStorage.getItem('preference_banner_dismissed');
    if (dismissed === 'true') {
      setIsDismissed(true);
    }
  }, []);

  const handleDismiss = () => {
    setIsDismissed(true);
    localStorage.setItem('preference_banner_dismissed', 'true');
  };

  // Don't show banner if:
  // - User has no preferences (not logged in)
  // - User is already personalized
  // - Banner was dismissed
  if (!preferences || preferences.is_personalized || isDismissed) {
    return null;
  }

  return (
    <div className={styles.preferenceBanner}>
      <div className={styles.content}>
        <span className={styles.icon}>💡</span>
        <div className={styles.text}>
          <strong>Personalize your experience!</strong>
          <p>Get content recommendations tailored to your hardware and experience level.</p>
        </div>
        <a href="/profile" className={styles.link}>
          Set Preferences
        </a>
        <button
          onClick={handleDismiss}
          className={styles.dismissButton}
          aria-label="Dismiss banner"
        >
          ✕
        </button>
      </div>
    </div>
  );
};

export default PreferenceBanner;
