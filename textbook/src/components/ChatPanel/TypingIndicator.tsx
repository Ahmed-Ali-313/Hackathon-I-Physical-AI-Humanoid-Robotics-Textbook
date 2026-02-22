/**
 * TypingIndicator component.
 *
 * Three-dot animation to show AI is responding.
 */

import React from 'react';
import styles from './TypingIndicator.module.css';

export default function TypingIndicator(): JSX.Element {
  return (
    <div className={styles.typingIndicator} aria-label="AI is typing">
      <span className={styles.dot}></span>
      <span className={styles.dot}></span>
      <span className={styles.dot}></span>
    </div>
  );
}
