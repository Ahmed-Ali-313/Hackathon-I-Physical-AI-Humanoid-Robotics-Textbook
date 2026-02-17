/**
 * ViewToggle Component
 *
 * Toggle button to switch between Personalized and Full content view.
 * Only visible for users with personalized preferences.
 */

import React from 'react';
import { usePersonalizationContext } from '../../contexts/PersonalizationContext';
import styles from './styles.module.css';

const ViewToggle: React.FC = () => {
  const { preferences, viewMode, setViewMode } = usePersonalizationContext();

  // Don't show toggle if user has no preferences or is not personalized
  if (!preferences || !preferences.is_personalized) {
    return null;
  }

  const handleToggle = () => {
    setViewMode(viewMode === 'personalized' ? 'full' : 'personalized');
  };

  return (
    <button
      onClick={handleToggle}
      className={styles.viewToggle}
      aria-label={`Switch to ${viewMode === 'personalized' ? 'full' : 'personalized'} view`}
    >
      {viewMode === 'personalized' ? (
        <>
          <span className={styles.icon}>👤</span>
          Personalized
        </>
      ) : (
        <>
          <span className={styles.icon}>📚</span>
          Full Content
        </>
      )}
    </button>
  );
};

export default ViewToggle;
