"""
TranslatedChapter Model
Feature: 005-urdu-translation
Purpose: Cache translated chapter content with optimistic locking
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from .base import Base


class TranslatedChapter(Base):
    """
    Stores cached translations of textbook chapters.

    Uses optimistic locking (version field) to handle concurrent translation requests
    without holding database locks during long-running OpenAI API calls.
    """

    __tablename__ = "translated_chapters"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Chapter identification
    chapter_id = Column(String(255), nullable=False, index=True)
    language_code = Column(String(10), nullable=False, index=True)

    # Translation content
    translated_content = Column(Text, nullable=False)
    original_hash = Column(String(64), nullable=False)

    # Optimistic locking
    version = Column(Integer, nullable=False, default=1)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Constraints
    __table_args__ = (
        # Unique constraint: one translation per chapter per language
        Index('idx_chapter_language', 'chapter_id', 'language_code', unique=True),

        # Index for cache expiration queries
        Index('idx_updated_at', 'updated_at'),

        # Check constraints
        CheckConstraint("language_code IN ('ur')", name='check_language_code'),
        CheckConstraint("chapter_id ~ '^\\d{2}-[a-z0-9-]+$'", name='check_chapter_id_format'),
        CheckConstraint("original_hash ~ '^[a-f0-9]{64}$'", name='check_original_hash_format'),
        CheckConstraint('version > 0', name='check_version_positive'),
    )

    def to_dict(self):
        """Convert model to dictionary for API responses."""
        return {
            'id': str(self.id),
            'chapter_id': self.chapter_id,
            'language_code': self.language_code,
            'translated_content': self.translated_content,
            'original_hash': self.original_hash,
            'version': self.version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<TranslatedChapter(chapter_id='{self.chapter_id}', language='{self.language_code}', version={self.version})>"
