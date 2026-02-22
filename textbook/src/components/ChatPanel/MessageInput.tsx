/**
 * MessageInput component.
 *
 * Input field with send button and character limit.
 * Supports selection mode by sending selected text with message.
 */

import React, { useState, useRef } from 'react';
import { useChatContext } from '../../contexts/ChatContext';
import { useChat } from '../../hooks/useChat';
import styles from './MessageInput.module.css';

interface MessageInputProps {
  selectedText?: string | null;
  selectedTextMetadata?: Record<string, any> | null;
}

export default function MessageInput({ selectedText, selectedTextMetadata }: MessageInputProps): JSX.Element {
  const [input, setInput] = useState('');
  const { isLoading } = useChatContext();
  const { sendMessage } = useChat();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const maxLength = 500;
  const remainingChars = maxLength - input.length;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!input.trim() || isLoading) {
      return;
    }

    // Send message with selected text if available
    await sendMessage(
      input.trim(),
      selectedText || undefined,
      selectedTextMetadata || undefined
    );

    setInput('');

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);

    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  };

  // Update placeholder based on selection mode
  const placeholder = selectedText
    ? 'Ask about the selected text...'
    : 'Ask a question...';

  return (
    <form className={styles.messageInput} onSubmit={handleSubmit}>
      <div className={styles.inputWrapper}>
        <textarea
          ref={textareaRef}
          className={styles.textarea}
          value={input}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={isLoading}
          maxLength={maxLength}
          rows={1}
          aria-label="Message input"
        />

        <button
          type="submit"
          className={styles.sendButton}
          disabled={!input.trim() || isLoading}
          aria-label="Send message"
        >
          <span className={styles.sendIcon}>➤</span>
        </button>
      </div>

      <div className={styles.footer}>
        <span
          className={`${styles.charCount} ${
            remainingChars < 50 ? styles.charCountWarning : ''
          }`}
        >
          {remainingChars} characters remaining
        </span>
        <span className={styles.hint}>
          {selectedText ? 'Selection mode active' : 'Press Enter to send, Shift+Enter for new line'}
        </span>
      </div>
    </form>
  );
}
