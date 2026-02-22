/**
 * Chat API client.
 *
 * Handles communication with the chat backend API.
 */

const API_BASE_URL = typeof window !== 'undefined'
  ? (window.location.hostname === 'localhost' ? 'http://localhost:8001' : '')
  : '';

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
 * Handle API errors.
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
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

export type { Conversation, Message, SendMessageResponse };
