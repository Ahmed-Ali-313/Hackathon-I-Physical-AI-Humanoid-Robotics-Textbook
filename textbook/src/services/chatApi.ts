/**
 * Chat API client.
 *
 * Handles communication with the chat backend API.
 */

const API_BASE_URL = typeof window !== 'undefined'
  ? (window.location.hostname === 'localhost'
      ? 'http://localhost:8001'
      : 'https://ai-native-book-backend.onrender.com')
  : 'http://localhost:8001';

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

interface SendMessageResponse {
  user_message: Message;
  assistant_message: Message;
}

/**
 * Get authentication token from localStorage.
 */
function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('auth_token');
}

/**
 * Get authorization headers.
 */
function getAuthHeaders(): HeadersInit {
  const token = getAuthToken();
  return {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
  };
}

/**
 * Handle API errors and return user-friendly messages.
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));

    // Extract error details
    const errorMessage = error.detail || `HTTP ${response.status}: ${response.statusText}`;
    const errorType = error.error_type || 'unknown_error';

    // Map to user-friendly messages
    if (response.status === 401) {
      throw new Error('Your session has expired. Please log in again.');
    }

    if (response.status === 403) {
      throw new Error("You don't have permission to access this resource.");
    }

    if (response.status === 404) {
      throw new Error('The requested resource was not found.');
    }

    if (response.status === 503) {
      if (errorType === 'database_error') {
        throw new Error('The database is temporarily unavailable. Please try again in a few moments.');
      }
      if (errorType === 'search_service_error') {
        throw new Error('The search service is temporarily unavailable. Please try again in a few moments.');
      }
      throw new Error('The service is temporarily unavailable. Please try again in a few moments.');
    }

    if (response.status === 504) {
      throw new Error('The request took too long to complete. Please try again.');
    }

    if (response.status >= 500) {
      throw new Error('An unexpected error occurred. Please try again later.');
    }

    // Return the error message from backend
    throw new Error(errorMessage);
  }

  return response.json();
}

/**
 * Create a new conversation.
 */
export async function createConversation(title: string): Promise<Conversation> {
  const response = await fetch(`${API_BASE_URL}/api/chat/conversations`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ title }),
  });

  return handleResponse<Conversation>(response);
}

/**
 * Get user's conversations.
 */
export async function getConversations(
  limit: number = 50,
  offset: number = 0
): Promise<Conversation[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/chat/conversations?limit=${limit}&offset=${offset}`,
    {
      method: 'GET',
      headers: getAuthHeaders(),
    }
  );

  return handleResponse<Conversation[]>(response);
}

/**
 * Get a conversation by ID.
 */
export async function getConversation(conversationId: string): Promise<Conversation> {
  const response = await fetch(`${API_BASE_URL}/api/chat/conversations/${conversationId}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  return handleResponse<Conversation>(response);
}

/**
 * Delete a conversation.
 */
export async function deleteConversation(conversationId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/chat/conversations/${conversationId}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
  }
}

/**
 * Get messages for a conversation.
 */
export async function getMessages(
  conversationId: string,
  limit: number = 500,
  offset: number = 0
): Promise<Message[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/chat/conversations/${conversationId}/messages?limit=${limit}&offset=${offset}`,
    {
      method: 'GET',
      headers: getAuthHeaders(),
    }
  );

  return handleResponse<Message[]>(response);
}

/**
 * Send a message to a conversation.
 */
export async function sendMessage(
  conversationId: string,
  content: string,
  selectedText?: string,
  selectedTextMetadata?: Record<string, any>
): Promise<SendMessageResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/chat/conversations/${conversationId}/messages`,
    {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        content,
        selected_text: selectedText,
        selected_text_metadata: selectedTextMetadata,
      }),
    }
  );

  return handleResponse<SendMessageResponse>(response);
}

/**
 * Create a conversation and send the first message.
 */
export async function createConversationWithMessage(
  question: string,
  selectedText?: string,
  selectedTextMetadata?: Record<string, any>
): Promise<{ conversation: Conversation; response: SendMessageResponse }> {
  // Create conversation with auto-generated title
  const conversation = await createConversation(question);

  // Send first message
  const response = await sendMessage(
    conversation.id,
    question,
    selectedText,
    selectedTextMetadata
  );

  return { conversation, response };
}

/**
 * Send a message with streaming response.
 */
export async function sendMessageStream(
  conversationId: string,
  content: string,
  selectedText?: string,
  selectedTextMetadata?: Record<string, any>,
  onChunk?: (chunk: string) => void,
  onUserMessage?: (message: Message) => void,
  onComplete?: (message: Message) => void,
  onError?: (error: Error) => void
): Promise<void> {
  const token = getAuthToken();

  try {
    const response = await fetch(
      `${API_BASE_URL}/api/chat/conversations/${conversationId}/messages/stream`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: JSON.stringify({
          content,
          selected_text: selectedText,
          selected_text_metadata: selectedTextMetadata,
        }),
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error('Response body is not readable');
    }

    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();

      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      // Process complete SSE messages
      const lines = buffer.split('\n');
      buffer = lines.pop() || ''; // Keep incomplete line in buffer

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6); // Remove 'data: ' prefix

          try {
            const event = JSON.parse(data);

            if (event.type === 'user_message' && onUserMessage && event.message) {
              onUserMessage(event.message);
            } else if (event.type === 'content' && onChunk) {
              onChunk(event.chunk);
            } else if (event.type === 'done' && onComplete) {
              // Validate message has required fields before passing to callback
              if (event.message && event.message.sender_type && event.message.content !== undefined) {
                onComplete(event.message);
              } else {
                console.error('Invalid message structure in done event:', event.message);
                // Still call onComplete with a fallback to clear typing indicator
                if (onComplete) {
                  onComplete(event.message || { sender_type: 'assistant', content: '' });
                }
              }
            } else if (event.type === 'error') {
              throw new Error(event.message || 'Unknown streaming error');
            }
          } catch (parseError) {
            console.error('Failed to parse SSE event:', parseError);
          }
        }
      }
    }
  } catch (error) {
    if (onError) {
      onError(error instanceof Error ? error : new Error('Unknown error'));
    } else {
      throw error;
    }
  }
}

export type { Conversation, Message, SendMessageResponse };
