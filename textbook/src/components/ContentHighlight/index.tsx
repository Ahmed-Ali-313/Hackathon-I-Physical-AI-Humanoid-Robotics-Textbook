/**
 * ContentHighlight Component
 *
 * Wraps content sections and highlights them if recommended for the user.
 * Shows a "Recommended for You" badge in personalized view mode.
 * Displays fallback message when content is not recommended.
 */

import React, { ReactNode } from 'react';
import { usePersonalizationContext } from '../../contexts/PersonalizationContext';
import styles from './styles.module.css';

interface ContentHighlightProps {
  hardware?: string[];
  software?: Record<string, string>;
  fallbackMessage?: string;
  children: ReactNode;
}

const ContentHighlight: React.FC<ContentHighlightProps> = ({
  hardware = [],
  software = {},
  fallbackMessage,
  children,
}) => {
  console.log('[ContentHighlight] Component rendered with props:', { hardware, software, fallbackMessage });

  const { preferences, viewMode } = usePersonalizationContext();

  // Compute if content is recommended based on user preferences
  const isRecommended = React.useMemo(() => {
    console.log('[ContentHighlight] Checking recommendation:', {
      hasPreferences: !!preferences,
      isPersonalized: preferences?.is_personalized,
      hardware,
      software,
      viewMode
    });

    if (!preferences || !preferences.is_personalized) {
      console.log('[ContentHighlight] No preferences or not personalized');
      return false;
    }

    // Hardware matching (OR logic - any match is sufficient)
    const hardwareMatch = hardware.length === 0 || hardware.some(hw => {
      if (hw === 'rtx_4090' || hw === 'rtx_a6000') {
        // Check if user has high-end workstation or workstation type
        return preferences.workstation_type === 'high_end_desktop' ||
               preferences.workstation_type === 'workstation';
      }
      if (hw === 'jetson_orin') {
        return preferences.edge_kit_available === 'jetson_orin';
      }
      return false;
    });

    // Software matching (AND logic - all requirements must be met)
    const softwareMatch = Object.entries(software).every(([key, requiredLevel]) => {
      const levelOrder = ['none', 'beginner', 'intermediate', 'advanced'];
      let userLevel = 'none';

      if (key === 'ros2_level') userLevel = preferences.ros2_level || 'none';
      if (key === 'gazebo_level') userLevel = preferences.gazebo_level || 'none';
      if (key === 'unity_level') userLevel = preferences.unity_level || 'none';
      if (key === 'isaac_level') userLevel = preferences.isaac_level || 'none';
      if (key === 'vla_level') userLevel = preferences.vla_level || 'none';

      const userLevelIndex = levelOrder.indexOf(userLevel);
      const requiredLevelIndex = levelOrder.indexOf(requiredLevel);

      return userLevelIndex >= requiredLevelIndex;
    });

    return hardwareMatch && softwareMatch;
  }, [preferences, hardware, software]);

  // Show fallback message if not recommended and in personalized view
  const showFallback =
    preferences &&
    preferences.is_personalized &&
    !isRecommended &&
    viewMode === 'personalized' &&
    fallbackMessage;

  // Highlight if recommended and in personalized view
  const shouldHighlight =
    preferences &&
    preferences.is_personalized &&
    isRecommended &&
    viewMode === 'personalized';

  if (showFallback) {
    return (
      <div className={styles.fallback}>
        <div className={styles.fallbackBanner}>
          <span className={styles.fallbackIcon}>ℹ️</span>
          {fallbackMessage}
        </div>
        <div className={styles.fallbackContent}>
          {children}
        </div>
      </div>
    );
  }

  if (shouldHighlight) {
    return (
      <div className={styles.highlighted}>
        <div className={styles.badge}>
          <span className={styles.badgeIcon}>✨</span>
          Recommended for You
        </div>
        {children}
      </div>
    );
  }

  return <>{children}</>;
};

export default ContentHighlight;
