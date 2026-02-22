/**
 * ChatContext for managing chat state.
 *
 * Provides global state management for chat conversations, messages, and UI state.
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';

// Types
interface Conversation {
  id: string;
  user_id: string;
  title: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

interface Message {
  id: string;
  conversation_id: string;
  content: string;
  sender_type: 'user' | 'assistant';
  confidence_score?: number;
  source_references?: Array<{
    chapter: string;
    section: string;
    url: string;
  }>;
  created_at: string;
}

interface ChatContextType {
  // State
  conversations: Conversation[];
  currentConversation: Conversation | null;
  messages: Message[];
  isLoading: boolean;
  isTyping: boolean;
  error: string | null;
  isPanelOpen: boolean;

  // Actions
  setConversations: (conversations: Conversation[]) => void;
  setCurrentConversation: (conversation: Conversation | null) => void;
  setMessages: (messages: Message[]) => void;
  addMessage: (message: Message) => void;
  setIsLoading: (loading: boolean) => void;
  setIsTyping: (typing: boolean) => void;
  setError: (error: string | null) => void;
  setIsPanelOpen: (open: boolean) => void;
}

// Create context
const ChatContext = createContext<ChatContextType | undefined>(undefined);

// Provider component
export function ChatProvider({ children }: { children: ReactNode }) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isPanelOpen, setIsPanelOpen] = useState(false);

  const addMessage = (message: Message) => {
    setMessages((prev) => [...prev, message]);
  };

  const value: ChatContextType = {
    conversations,
    currentConversation,
    messages,
    isLoading,
    isTyping,
    error,
    isPanelOpen,
    setConversations,
    setCurrentConversation,
    setMessages,
    addMessage,
    setIsLoading,
    setIsTyping,
    setError,
    setIsPanelOpen,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}

// Hook to use chat context
export function useChatContext(): ChatContextType {
  const context = useContext(ChatContext);

  if (context === undefined) {
    throw new Error('useChatContext must be used within ChatProvider');
  }

  return context;
}

// Export types
export type { Conversation, Message, ChatContextType };
