-- Migration: Create chat tables for RAG chatbot (Phase 3)
-- Created: 2026-02-22
-- Description: Conversations, chat messages, and chat sessions for RAG chatbot

-- Conversations table: Groups messages, auto-generated title, 12-month retention
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(100) NOT NULL,
    message_count INTEGER DEFAULT 0 CHECK (message_count >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT max_conversations_per_user CHECK (
        (SELECT COUNT(*) FROM conversations WHERE user_id = conversations.user_id) <= 50
    )
);

-- Chat messages table: User questions and AI responses with source attribution
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    content TEXT NOT NULL CHECK (char_length(content) <= 2000),
    sender_type VARCHAR(10) NOT NULL CHECK (sender_type IN ('user', 'assistant')),
    confidence_score DECIMAL(3, 2) CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    source_references JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT max_messages_per_conversation CHECK (
        (SELECT COUNT(*) FROM chat_messages WHERE conversation_id = chat_messages.conversation_id) <= 500
    )
);

-- Chat sessions table: Tracks active sessions, 30-minute expiry
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (CURRENT_TIMESTAMP + INTERVAL '30 minutes')
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_messages_conversation_id ON chat_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_is_active ON chat_sessions(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_chat_sessions_expires_at ON chat_sessions(expires_at);

-- Trigger to update conversation.updated_at when messages are added
CREATE OR REPLACE FUNCTION update_conversation_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations
    SET updated_at = CURRENT_TIMESTAMP,
        message_count = message_count + 1
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_conversation_timestamp
AFTER INSERT ON chat_messages
FOR EACH ROW
EXECUTE FUNCTION update_conversation_timestamp();

-- Trigger to auto-expire sessions after 30 minutes
CREATE OR REPLACE FUNCTION expire_old_sessions()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE chat_sessions
    SET is_active = FALSE
    WHERE expires_at < CURRENT_TIMESTAMP AND is_active = TRUE;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_expire_old_sessions
AFTER INSERT OR UPDATE ON chat_sessions
FOR EACH STATEMENT
EXECUTE FUNCTION expire_old_sessions();

-- Comments for documentation
COMMENT ON TABLE conversations IS 'Chat conversations with auto-generated titles and 12-month retention';
COMMENT ON TABLE chat_messages IS 'User questions and AI responses with source attribution';
COMMENT ON TABLE chat_sessions IS 'Active chat sessions with 30-minute expiry';
COMMENT ON COLUMN chat_messages.confidence_score IS 'RAG confidence score (0.0-1.0) for AI responses';
COMMENT ON COLUMN chat_messages.source_references IS 'JSONB array of source links: [{"chapter": "...", "section": "...", "url": "..."}]';
