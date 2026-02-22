/**
 * MessageList component.
 *
 * Displays chat messages with typing indicator and source links.
 */

import React, { useEffect, useRef } from 'react';
import { useChatContext } from '../../contexts/ChatContext';
import TypingIndicator from './TypingIndicator';
import SourceLink from '../SourceLink';
import styles from './MessageList.module.css';

export default function MessageList(): JSX.Element {
  const { messages, isTyping } = useChatContext();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  if (messages.length === 0 && !isTyping) {
    return (
      <div className={styles.emptyState}>
        <div className={styles.emptyIcon}>💬</div>
        <p className={styles.emptyText}>
          Ask me anything about the textbook!
        </p>
        <p className={styles.emptyHint}>
          I can help explain concepts, clarify topics, and guide your learning.
        </p>
      </div>
    );
  }

  return (
    <div className={styles.messageList}>
      {messages.map((message) => (
        <div
          key={message.id}
          className={`${styles.message} ${
            message.sender_type === 'user' ? styles.userMessage : styles.assistantMessage
          }`}
        >
          {/* Message icon */}
          <div className={styles.messageIcon}>
            {message.sender_type === 'user' ? '👤' : '🤖'}
          </div>

          {/* Message content */}
          <div className={styles.messageContent}>
            <div className={styles.messageText}>{message.content}</div>

            {/* Source references (for assistant messages) */}
            {message.sender_type === 'assistant' && message.source_references && message.source_references.length > 0 && (
              <div className={styles.sources}>
                <div className={styles.sourcesLabel}>Sources:</div>
                <div className={styles.sourcesList}>
                  {message.source_references.map((source, index) => (
                    <SourceLink
                      key={index}
                      chapter={source.chapter}
                      section={source.section}
                      url={source.url}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Confidence score (for assistant messages) */}
            {message.sender_type === 'assistant' && message.confidence_score !== undefined && (
              <div className={styles.confidence}>
                Confidence: {Math.round(message.confidence_score * 100)}%
              </div>
            )}
          </div>
        </div>
      ))}

      {/* Typing indicator */}
      {isTyping && (
        <div className={`${styles.message} ${styles.assistantMessage}`}>
          <div className={styles.messageIcon}>🤖</div>
          <div className={styles.messageContent}>
            <TypingIndicator />
          </div>
        </div>
      )}

      {/* Scroll anchor */}
      <div ref={messagesEndRef} />
    </div>
  );
}
