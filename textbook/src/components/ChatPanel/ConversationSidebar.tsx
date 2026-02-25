/**
 * ConversationSidebar component.
 *
 * Displays list of user's conversations with ability to switch between them.
 */

import React from 'react';
import { useChatContext } from '../../contexts/ChatContext';
import { useChat } from '../../hooks/useChat';
import type { Conversation } from '../../services/chatApi';
import styles from './ConversationSidebar.module.css';

export default function ConversationSidebar(): JSX.Element {
  const { conversations, currentConversation, isLoading } = useChatContext();
  const { switchConversation, createConversation, deleteConversation } = useChat();

  const handleNewConversation = async () => {
    try {
      await createConversation('New conversation');
    } catch (err) {
      console.error('Failed to create conversation:', err);
    }
  };

  const handleSelectConversation = async (conversation: Conversation) => {
    if (currentConversation?.id === conversation.id) return;

    try {
      await switchConversation(conversation);
    } catch (err) {
      console.error('Failed to switch conversation:', err);
    }
  };

  const handleDeleteConversation = async (
    e: React.MouseEvent,
    conversationId: string
  ) => {
    e.stopPropagation();

    if (!confirm('Delete this conversation?')) return;

    try {
      await deleteConversation(conversationId);
    } catch (err) {
      console.error('Failed to delete conversation:', err);
    }
  };

  return (
    <div className={styles.sidebar}>
      {/* Header */}
      <div className={styles.header}>
        <h3 className={styles.title}>Conversations</h3>
        <button
          className={styles.newButton}
          onClick={handleNewConversation}
          disabled={isLoading}
          aria-label="New conversation"
          type="button"
        >
          + New
        </button>
      </div>

      {/* Conversation list */}
      <div className={styles.conversationList}>
        {isLoading && conversations.length === 0 ? (
          <div className={styles.loading}>Loading...</div>
        ) : conversations.length === 0 ? (
          <div className={styles.empty}>
            <p>No conversations yet</p>
            <p className={styles.emptyHint}>Start by asking a question</p>
          </div>
        ) : (
          conversations.map((conversation) => (
            <div
              key={conversation.id}
              className={`${styles.conversationItem} ${
                currentConversation?.id === conversation.id ? styles.active : ''
              }`}
              onClick={() => handleSelectConversation(conversation)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  handleSelectConversation(conversation);
                }
              }}
            >
              <div className={styles.conversationContent}>
                <div className={styles.conversationTitle}>
                  {conversation.title}
                </div>
                <div className={styles.conversationMeta}>
                  {conversation.message_count} messages · {formatDate(conversation.updated_at)}
                </div>
              </div>
              <button
                className={styles.deleteButton}
                onClick={(e) => handleDeleteConversation(e, conversation.id)}
                aria-label="Delete conversation"
                type="button"
              >
                🗑️
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

/**
 * Format date for display.
 */
function formatDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;

  return date.toLocaleDateString();
}
