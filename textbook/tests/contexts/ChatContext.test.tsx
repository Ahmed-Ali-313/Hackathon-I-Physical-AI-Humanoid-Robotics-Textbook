/**
 * Tests for ChatContext.
 *
 * Tests chat state management and context provider.
 */

import React from 'react';
import { renderHook, act } from '@testing-library/react';
import { ChatProvider, useChatContext } from '../../src/contexts/ChatContext';

describe('ChatContext', () => {
  it('should provide initial chat state', () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <ChatProvider>{children}</ChatProvider>
    );

    const { result } = renderHook(() => useChatContext(), { wrapper });

    expect(result.current.conversations).toEqual([]);
    expect(result.current.currentConversation).toBeNull();
    expect(result.current.messages).toEqual([]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('should throw error when used outside provider', () => {
    // Suppress console.error for this test
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

    expect(() => {
      renderHook(() => useChatContext());
    }).toThrow('useChatContext must be used within ChatProvider');

    consoleSpy.mockRestore();
  });

  it('should update conversations list', () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <ChatProvider>{children}</ChatProvider>
    );

    const { result } = renderHook(() => useChatContext(), { wrapper });

    const mockConversations = [
      { id: 'conv-1', title: 'Test 1', message_count: 5 },
      { id: 'conv-2', title: 'Test 2', message_count: 3 },
    ];

    act(() => {
      result.current.setConversations(mockConversations);
    });

    expect(result.current.conversations).toEqual(mockConversations);
  });

  it('should set current conversation', () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <ChatProvider>{children}</ChatProvider>
    );

    const { result } = renderHook(() => useChatContext(), { wrapper });

    const mockConversation = { id: 'conv-1', title: 'Test', message_count: 0 };

    act(() => {
      result.current.setCurrentConversation(mockConversation);
    });

    expect(result.current.currentConversation).toEqual(mockConversation);
  });

  it('should update messages list', () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <ChatProvider>{children}</ChatProvider>
    );

    const { result } = renderHook(() => useChatContext(), { wrapper });

    const mockMessages = [
      { id: 'msg-1', content: 'Question', sender_type: 'user' },
      { id: 'msg-2', content: 'Answer', sender_type: 'assistant' },
    ];

    act(() => {
      result.current.setMessages(mockMessages);
    });

    expect(result.current.messages).toEqual(mockMessages);
  });

  it('should set loading state', () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <ChatProvider>{children}</ChatProvider>
    );

    const { result } = renderHook(() => useChatContext(), { wrapper });

    act(() => {
      result.current.setIsLoading(true);
    });

    expect(result.current.isLoading).toBe(true);

    act(() => {
      result.current.setIsLoading(false);
    });

    expect(result.current.isLoading).toBe(false);
  });

  it('should set error state', () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <ChatProvider>{children}</ChatProvider>
    );

    const { result } = renderHook(() => useChatContext(), { wrapper });

    const errorMessage = 'Failed to send message';

    act(() => {
      result.current.setError(errorMessage);
    });

    expect(result.current.error).toBe(errorMessage);
  });

  it('should clear error state', () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <ChatProvider>{children}</ChatProvider>
    );

    const { result } = renderHook(() => useChatContext(), { wrapper });

    act(() => {
      result.current.setError('Error');
    });

    expect(result.current.error).toBe('Error');

    act(() => {
      result.current.setError(null);
    });

    expect(result.current.error).toBeNull();
  });

  it('should toggle chat panel visibility', () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <ChatProvider>{children}</ChatProvider>
    );

    const { result } = renderHook(() => useChatContext(), { wrapper });

    expect(result.current.isPanelOpen).toBe(false);

    act(() => {
      result.current.setIsPanelOpen(true);
    });

    expect(result.current.isPanelOpen).toBe(true);

    act(() => {
      result.current.setIsPanelOpen(false);
    });

    expect(result.current.isPanelOpen).toBe(false);
  });

  it('should add message to messages list', () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <ChatProvider>{children}</ChatProvider>
    );

    const { result } = renderHook(() => useChatContext(), { wrapper });

    const initialMessages = [
      { id: 'msg-1', content: 'Question', sender_type: 'user' },
    ];

    act(() => {
      result.current.setMessages(initialMessages);
    });

    const newMessage = { id: 'msg-2', content: 'Answer', sender_type: 'assistant' };

    act(() => {
      result.current.addMessage(newMessage);
    });

    expect(result.current.messages).toHaveLength(2);
    expect(result.current.messages[1]).toEqual(newMessage);
  });

  it('should handle typing indicator state', () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <ChatProvider>{children}</ChatProvider>
    );

    const { result } = renderHook(() => useChatContext(), { wrapper });

    expect(result.current.isTyping).toBe(false);

    act(() => {
      result.current.setIsTyping(true);
    });

    expect(result.current.isTyping).toBe(true);
  });
});
