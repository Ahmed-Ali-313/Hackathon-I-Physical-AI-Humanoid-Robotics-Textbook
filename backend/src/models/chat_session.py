"""
ChatSession model for tracking active chat sessions.

Represents active user sessions with 30-minute expiry.
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database import Base
import uuid
from datetime import datetime, timedelta


def generate_uuid():
    """Generate UUID for PostgreSQL."""
    return uuid.uuid4()


class ChatSession(Base):
    """
    ChatSession model.

    Tracks active chat sessions with automatic expiry after 30 minutes.
    Links users to their current conversation.
    """

    __tablename__ = "chat_sessions"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)

    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True)

    # Session state
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    conversation = relationship("Conversation", back_populates="sessions")

    def __repr__(self):
        return f"<ChatSession(id={self.id}, user_id={self.user_id}, active={self.is_active})>"

    def to_dict(self):
        """Convert session to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "conversation_id": self.conversation_id,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }

    def is_expired(self) -> bool:
        """
        Check if session has expired.

        Returns:
            True if session has expired, False otherwise
        """
        if not self.expires_at:
            return True

        return datetime.utcnow() > self.expires_at

    def extend_expiry(self, minutes: int = 30):
        """
        Extend session expiry time.

        Args:
            minutes: Number of minutes to extend (default: 30)
        """
        self.expires_at = datetime.utcnow() + timedelta(minutes=minutes)
        self.updated_at = datetime.utcnow()

    def deactivate(self):
        """Deactivate the session."""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    @staticmethod
    def create_session(user_id: str, conversation_id: str = None, expiry_minutes: int = 30):
        """
        Create a new chat session.

        Args:
            user_id: User ID
            conversation_id: Optional conversation ID
            expiry_minutes: Session expiry time in minutes (default: 30)

        Returns:
            ChatSession instance
        """
        expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)

        return ChatSession(
            user_id=user_id,
            conversation_id=conversation_id,
            is_active=True,
            expires_at=expires_at,
        )

    @staticmethod
    def cleanup_expired_sessions(sessions: list):
        """
        Deactivate expired sessions.

        Args:
            sessions: List of ChatSession instances

        Returns:
            Number of sessions deactivated
        """
        count = 0
        for session in sessions:
            if session.is_active and session.is_expired():
                session.deactivate()
                count += 1

        return count
