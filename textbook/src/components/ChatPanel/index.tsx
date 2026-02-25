/**
 * ChatPanel component.
 *
 * Slide-out chat panel with conversation sidebar, message list, and input field.
 * Supports selection mode when text is highlighted.
 */

import React, { useEffect, useRef } from 'react';
import { useChatContext } from '../../contexts/ChatContext';
import { useTextSelection } from '../../hooks/useTextSelection';
import { useChat } from '../../hooks/useChat';
import ConversationSidebar from './ConversationSidebar';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import styles from './styles.module.css';

export default function ChatPanel(): JSX.Element | null {
  const { isPanelOpen, setIsPanelOpen, currentConversation, error } = useChatContext();
  const { selectedText, metadata, clearSelection } = useTextSelection();
  const { loadConversations } = useChat();
  const panelRef = useRef<HTMLDivElement>(null);

  // Load conversations when panel opens
  useEffect(() => {
    if (isPanelOpen) {
      loadConversations();
    }
  }, [isPanelOpen, loadConversations]);

  // Close panel on Escape key
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isPanelOpen) {
        setIsPanelOpen(false);
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isPanelOpen, setIsPanelOpen]);

  // Focus trap within panel
  useEffect(() => {
    if (isPanelOpen && panelRef.current) {
      const focusableElements = panelRef.current.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );

      if (focusableElements.length > 0) {
        (focusableElements[0] as HTMLElement).focus();
      }
    }
  }, [isPanelOpen]);

  if (!isPanelOpen) {
    return null;
  }

  const handleClose = () => {
    setIsPanelOpen(false);
    clearSelection();
  };

  const handleClearSelection = () => {
    clearSelection();
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className={styles.backdrop}
        onClick={handleClose}
        aria-hidden="true"
      />

      {/* Panel */}
      <div
        ref={panelRef}
        className={styles.chatPanel}
        role="dialog"
        aria-label="Chat assistant"
        aria-modal="true"
      >
        {/* Header */}
        <div className={styles.header}>
          <div className={styles.headerContent}>
            <h2 className={styles.title}>
              {currentConversation ? currentConversation.title : 'Chat Assistant'}
            </h2>
            <button
              className={styles.closeButton}
              onClick={handleClose}
              aria-label="Close chat"
              type="button"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Selection mode banner */}
        {selectedText && (
          <div className={styles.selectionBanner}>
            <div className={styles.selectionContent}>
              <span className={styles.selectionIcon}>📝</span>
              <div className={styles.selectionInfo}>
                <div className={styles.selectionLabel}>Ask about selection</div>
                <div className={styles.selectionText}>
                  {selectedText.substring(0, 100)}
                  {selectedText.length > 100 ? '...' : ''}
                </div>
              </div>
              <button
                className={styles.clearSelectionButton}
                onClick={handleClearSelection}
                aria-label="Clear selection"
                type="button"
              >
                ✕
              </button>
            </div>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className={styles.errorBanner} role="alert">
            <span className={styles.errorIcon}>⚠️</span>
            <span className={styles.errorText}>{error}</span>
          </div>
        )}

        {/* Content */}
        <div className={styles.content}>
          {/* Conversation sidebar */}
          <ConversationSidebar />

          {/* Main chat area */}
          <div className={styles.mainArea}>
            {/* Message list */}
            <div className={styles.messageArea}>
              <MessageList />
            </div>

            {/* Input area */}
            <div className={styles.inputArea}>
              <MessageInput selectedText={selectedText} selectedTextMetadata={metadata} />
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
