"""
ChatMessage model for chat messages.

Represents user questions and AI responses with source attribution.
"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, CheckConstraint, Numeric
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database import Base
import uuid
import json


def generate_uuid():
    """Generate UUID for PostgreSQL."""
    return uuid.uuid4()


class ChatMessage(Base):
    """
    ChatMessage model.

    Stores user questions and AI responses with confidence scores and source attribution.
    Supports both user and assistant message types.
    """

    __tablename__ = "chat_messages"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)

    # Foreign keys
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)

    # Message content
    content = Column(Text, nullable=False)
    sender_type = Column(String(10), nullable=False)  # "user" or "assistant"

    # AI response metadata (only for assistant messages)
    confidence_score = Column(Numeric(3, 2), nullable=True)  # 0.00-1.00
    source_references = Column(JSONB, nullable=False, default=list)  # JSONB for PostgreSQL

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    # Constraints
    __table_args__ = (
        CheckConstraint("sender_type IN ('user', 'assistant')", name="check_sender_type_valid"),
        CheckConstraint("length(content) > 0", name="check_content_not_empty"),
        CheckConstraint("length(content) <= 4000", name="check_content_max_length"),
        CheckConstraint(
            "confidence_score IS NULL OR (confidence_score >= 0.0 AND confidence_score <= 1.0)",
            name="check_confidence_score_range"
        ),
    )

    def __repr__(self):
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<ChatMessage(id={self.id}, sender={self.sender_type}, content={content_preview})>"

    def to_dict(self):
        """Convert message to dictionary."""
        return {
            "id": str(self.id),
            "conversation_id": str(self.conversation_id),
            "content": self.content,
            "sender_type": self.sender_type,
            "confidence_score": float(self.confidence_score) if self.confidence_score else None,
            "source_references": self.get_source_references(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def get_source_references(self):
        """
        Get source references as list of dictionaries.

        Returns:
            List of source reference dictionaries
        """
        if not self.source_references:
            return []

        # JSONB column returns list directly
        if isinstance(self.source_references, list):
            return self.source_references

        # Fallback for string (shouldn't happen with JSONB)
        try:
            return json.loads(self.source_references)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_source_references(self, references):
        """
        Set source references from list of dictionaries.

        Args:
            references: List of source reference dictionaries
                       [{"chapter": "...", "section": "...", "url": "..."}]
        """
        if not isinstance(references, list):
            raise ValueError("Source references must be a list")

        # Validate each reference has required fields
        for ref in references:
            if not isinstance(ref, dict):
                raise ValueError("Each source reference must be a dictionary")
            if "url" not in ref:
                raise ValueError("Each source reference must have a 'url' field")

        # JSONB column accepts list directly
        self.source_references = references

    @staticmethod
    def create_user_message(conversation_id: str, content: str):
        """
        Create a user message.

        Args:
            conversation_id: Conversation ID
            content: User question

        Returns:
            ChatMessage instance
        """
        if len(content) > 500:
            raise ValueError("User message cannot exceed 500 characters")

        return ChatMessage(
            conversation_id=conversation_id,
            content=content,
            sender_type="user",
        )

    @staticmethod
    def create_assistant_message(
        conversation_id: str,
        content: str,
        confidence_score: float,
        source_references: list,
    ):
        """
        Create an assistant message.

        Args:
            conversation_id: Conversation ID
            content: AI response
            confidence_score: Confidence score (0.0-1.0)
            source_references: List of source references

        Returns:
            ChatMessage instance
        """
        if len(content) > 4000:
            raise ValueError("Assistant message cannot exceed 4000 characters")

        if not (0.0 <= confidence_score <= 1.0):
            raise ValueError("Confidence score must be between 0.0 and 1.0")

        message = ChatMessage(
            conversation_id=conversation_id,
            content=content,
            sender_type="assistant",
            confidence_score=confidence_score,
        )
        message.set_source_references(source_references)

        return message
