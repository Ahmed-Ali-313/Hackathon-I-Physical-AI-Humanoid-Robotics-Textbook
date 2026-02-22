/**
 * useChat hook.
 *
 * Manages chat state and provides methods for sending messages and managing conversations.
 */

import { useCallback } from 'react';
import { useChatContext } from '../contexts/ChatContext';
import * as chatApi from '../services/chatApi';

export function useChat() {
  const {
    currentConversation,
    setCurrentConversation,
    conversations,
    setConversations,
    messages,
    setMessages,
    addMessage,
    setIsLoading,
    setIsTyping,
    setError,
    setIsPanelOpen,
  } = useChatContext();

  /**
   * Load user's conversations.
   */
  const loadConversations = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const convs = await chatApi.getConversations();
      setConversations(convs);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load conversations');
    } finally {
      setIsLoading(false);
    }
  }, [setIsLoading, setError, setConversations]);

  /**
   * Load messages for a conversation.
   */
  const loadMessages = useCallback(
    async (conversationId: string) => {
      try {
        setIsLoading(true);
        setError(null);

        const msgs = await chatApi.getMessages(conversationId);
        setMessages(msgs);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load messages');
      } finally {
        setIsLoading(false);
      }
    },
    [setIsLoading, setError, setMessages]
  );

  /**
   * Switch to a different conversation.
   */
  const switchConversation = useCallback(
    async (conversation: chatApi.Conversation) => {
      setCurrentConversation(conversation);
      await loadMessages(conversation.id);
    },
    [setCurrentConversation, loadMessages]
  );

  /**
   * Create a new conversation.
   */
  const createConversation = useCallback(
    async (title: string) => {
      try {
        setIsLoading(true);
        setError(null);

        const conversation = await chatApi.createConversation(title);
        setCurrentConversation(conversation);
        setConversations([conversation, ...conversations]);
        setMessages([]);

        return conversation;
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to create conversation');
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [setIsLoading, setError, setCurrentConversation, setConversations, conversations, setMessages]
  );

  /**
   * Send a message.
   */
  const sendMessage = useCallback(
    async (content: string, selectedText?: string, selectedTextMetadata?: Record<string, any>) => {
      try {
        setError(null);

        // Create conversation if none exists
        let conversation = currentConversation;
        if (!conversation) {
          const result = await chatApi.createConversationWithMessage(
            content,
            selectedText,
            selectedTextMetadata
          );
          conversation = result.conversation;
          setCurrentConversation(conversation);
          setConversations([conversation, ...conversations]);

          // Add messages
          addMessage(result.response.user_message);
          addMessage(result.response.assistant_message);

          return;
        }

        // Add user message immediately (optimistic update)
        const tempUserMessage = {
          id: `temp-${Date.now()}`,
          conversation_id: conversation.id,
          content,
          sender_type: 'user' as const,
          created_at: new Date().toISOString(),
        };
        addMessage(tempUserMessage);

        // Show typing indicator
        setIsTyping(true);

        // Send message to backend
        const response = await chatApi.sendMessage(
          conversation.id,
          content,
          selectedText,
          selectedTextMetadata
        );

        // Remove temp message and add real messages
        setMessages((prev) => prev.filter((msg) => msg.id !== tempUserMessage.id));
        addMessage(response.user_message);
        addMessage(response.assistant_message);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to send message');
        throw err;
      } finally {
        setIsTyping(false);
      }
    },
    [
      currentConversation,
      setCurrentConversation,
      conversations,
      setConversations,
      addMessage,
      setMessages,
      setIsTyping,
      setError,
    ]
  );

  /**
   * Delete a conversation.
   */
  const deleteConversation = useCallback(
    async (conversationId: string) => {
      try {
        setIsLoading(true);
        setError(null);

        await chatApi.deleteConversation(conversationId);

        // Remove from list
        setConversations(conversations.filter((c) => c.id !== conversationId));

        // Clear current conversation if it was deleted
        if (currentConversation?.id === conversationId) {
          setCurrentConversation(null);
          setMessages([]);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete conversation');
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [
      setIsLoading,
      setError,
      conversations,
      setConversations,
      currentConversation,
      setCurrentConversation,
      setMessages,
    ]
  );

  /**
   * Open chat panel.
   */
  const openChat = useCallback(() => {
    setIsPanelOpen(true);
  }, [setIsPanelOpen]);

  /**
   * Close chat panel.
   */
  const closeChat = useCallback(() => {
    setIsPanelOpen(false);
  }, [setIsPanelOpen]);

  return {
    // State
    currentConversation,
    conversations,
    messages,

    // Actions
    loadConversations,
    loadMessages,
    switchConversation,
    createConversation,
    sendMessage,
    deleteConversation,
    openChat,
    closeChat,
  };
}
