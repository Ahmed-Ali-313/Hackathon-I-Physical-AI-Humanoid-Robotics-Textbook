/**
 * ContentHighlight Component
 *
 * Wraps content sections and highlights them if recommended for the user.
 * Shows a "Recommended for You" badge in personalized view mode.
 */

import React, { ReactNode } from 'react';
import { usePersonalizationContext } from '../../contexts/PersonalizationContext';
import styles from './styles.module.css';

interface ContentHighlightProps {
  contentId: string;
  isRecommended: boolean;
  children: ReactNode;
}

const ContentHighlight: React.FC<ContentHighlightProps> = ({
  contentId,
  isRecommended,
  children,
}) => {
  const { preferences, viewMode } = usePersonalizationContext();

  // Don't highlight if:
  // - User has no preferences
  // - User is not personalized
  // - Content is not recommended
  // - View mode is "full"
  const shouldHighlight =
    preferences &&
    preferences.is_personalized &&
    isRecommended &&
    viewMode === 'personalized';

  if (!shouldHighlight) {
    return <>{children}</>;
  }

  return (
    <div className={styles.highlighted}>
      <div className={styles.badge}>
        <span className={styles.badgeIcon}>✨</span>
        Recommended for You
      </div>
      {children}
    </div>
  );
};

export default ContentHighlight;
