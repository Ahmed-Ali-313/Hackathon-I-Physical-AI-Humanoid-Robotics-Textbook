/**
 * SourceLink component.
 *
 * Clickable link to textbook chapter/section for source attribution.
 */

import React from 'react';
import styles from './styles.module.css';

interface SourceLinkProps {
  chapter: string;
  section: string;
  url: string;
}

export default function SourceLink({ chapter, section, url }: SourceLinkProps): JSX.Element {
  const displayText = chapter || 'Source';

  return (
    <a
      href={url}
      className={styles.sourceLink}
      target="_self"
      rel="noopener"
      title={`View ${chapter} - ${section}`}
    >
      <span className={styles.icon}>📖</span>
      <span className={styles.text}>{displayText}</span>
    </a>
  );
}
