-- Migration: Create chat tables for RAG chatbot (Phase 3) - SQLite Version
-- Created: 2026-02-25
-- Description: Conversations, chat messages, and chat sessions for RAG chatbot

-- Conversations table: Groups messages, auto-generated title, 12-month retention
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL CHECK (length(title) <= 100),
    message_count INTEGER DEFAULT 0 CHECK (message_count >= 0),
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Chat messages table: User questions and AI responses with source attribution
CREATE TABLE IF NOT EXISTS chat_messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    content TEXT NOT NULL CHECK (length(content) <= 2000),
    sender_type TEXT NOT NULL CHECK (sender_type IN ('user', 'assistant')),
    confidence_score REAL CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    source_references TEXT DEFAULT '[]',
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

-- Chat sessions table: Tracks active sessions, 30-minute expiry
CREATE TABLE IF NOT EXISTS chat_sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    conversation_id TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    expires_at TEXT DEFAULT (datetime('now', '+30 minutes')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE SET NULL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_messages_conversation_id ON chat_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_is_active ON chat_sessions(is_active) WHERE is_active = 1;
CREATE INDEX IF NOT EXISTS idx_chat_sessions_expires_at ON chat_sessions(expires_at);

-- Trigger to update conversation.updated_at when messages are added
CREATE TRIGGER IF NOT EXISTS trigger_update_conversation_timestamp
AFTER INSERT ON chat_messages
FOR EACH ROW
BEGIN
    UPDATE conversations
    SET updated_at = datetime('now'),
        message_count = message_count + 1
    WHERE id = NEW.conversation_id;
END;
