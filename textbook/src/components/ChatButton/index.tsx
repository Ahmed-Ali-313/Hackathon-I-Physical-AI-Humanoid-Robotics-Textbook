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
      <span className={styles.icon}>💬</span>
      <span className={styles.text}>Ask</span>
    </button>
  );
}
