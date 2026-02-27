"""
Conversation model for chat conversations.

Represents a conversation thread with auto-generated title and message tracking.
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.models.user import User
from src.database import Base
import uuid


def generate_uuid():
    """Generate UUID for PostgreSQL."""
    return uuid.uuid4()


class Conversation(Base):
    """
    Conversation model.

    Groups chat messages into conversation threads with auto-generated titles.
    Enforces 12-month retention and max 50 conversations per user.
    """

    __tablename__ = "conversations"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)

    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Conversation metadata
    title = Column(String(100), nullable=False)
    message_count = Column(Integer, default=0, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan", lazy="selectin")
    sessions = relationship("ChatSession", back_populates="conversation", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint("message_count >= 0", name="check_message_count_non_negative"),
        CheckConstraint("length(title) > 0", name="check_title_not_empty"),
    )

    def __repr__(self):
        return f"<Conversation(id={self.id}, title={self.title}, messages={self.message_count})>"

    def to_dict(self):
        """Convert conversation to dictionary."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "title": self.title,
            "message_count": self.message_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @staticmethod
    def generate_title_from_question(question: str, max_length: int = 50) -> str:
        """
        Generate conversation title from first question.

        Rules:
        - If question < 50 chars: use full question (no "...")
        - If question >= 50 chars: truncate at word boundary + "..."

        Args:
            question: User's first question
            max_length: Maximum title length (default: 50)

        Returns:
            Generated title
        """
        question = question.strip()

        if len(question) <= max_length:
            return question

        # Truncate at word boundary
        truncated = question[:max_length]
        last_space = truncated.rfind(' ')

        if last_space > 0:
            # Truncate at last complete word
            return truncated[:last_space] + "..."
        else:
            # No space found, truncate at max_length
            return truncated + "..."
