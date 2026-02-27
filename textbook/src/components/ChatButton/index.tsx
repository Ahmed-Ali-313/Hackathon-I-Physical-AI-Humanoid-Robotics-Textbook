/**
 * ChatButton component.
 *
 * Floating button to open the chat panel.
 */

import React from 'react';
import { useChatContext } from '../../contexts/ChatContext';
import styles from './styles.module.css';

interface ChatButtonProps {
  disabled?: boolean;
}

export default function ChatButton({ disabled = false }: ChatButtonProps): JSX.Element {
  const { setIsPanelOpen } = useChatContext();

  const handleClick = () => {
    if (!disabled) {
      setIsPanelOpen(true);
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleClick();
    }
  };

  return (
    <button
      className={styles.chatButton}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      disabled={disabled}
      aria-label="Open chat assistant"
      title="Ask a question about the textbook"
      type="button"
    >
      <span className={styles.icon}>
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M20 2H4C2.9 2 2 2.9 2 4V22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2Z" fill="currentColor"/>
          <circle cx="8" cy="10" r="1.5" fill="white"/>
          <circle cx="12" cy="10" r="1.5" fill="white"/>
          <circle cx="16" cy="10" r="1.5" fill="white"/>
        </svg>
      </span>
      <span className={styles.text}>Ask AI</span>
    </button>
  );
}
