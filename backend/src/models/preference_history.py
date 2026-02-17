"""
PreferenceHistory Model

SQLAlchemy model for preference_history table.
Tracks all changes to user personalization preferences for audit purposes.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, CheckConstraint, TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from src.database import Base


class UUID(TypeDecorator):
    """Platform-independent UUID type."""
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            return str(value) if isinstance(value, uuid.UUID) else value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return value if isinstance(value, uuid.UUID) else uuid.UUID(value)


class PreferenceHistory(Base):
    """PreferenceHistory model for tracking preference changes"""

    __tablename__ = "preference_history"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    profile_id = Column(UUID(), ForeignKey("personalization_profiles.id", ondelete="CASCADE"), nullable=False)

    # Change details
    field_name = Column(String(100), nullable=False)
    old_value = Column(String(255), nullable=True)
    new_value = Column(String(255), nullable=True)

    # Metadata
    change_source = Column(String(50), nullable=False)  # 'signup', 'profile_page', 'api', 'admin'
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", backref="preference_history")

    # Check constraints
    __table_args__ = (
        CheckConstraint(
            "change_source IN ('signup', 'profile_page', 'api', 'admin')",
            name="valid_change_source"
        ),
        CheckConstraint(
            "old_value IS NOT NULL OR new_value IS NOT NULL",
            name="has_value"
        ),
    )

    def __repr__(self):
        return f"<PreferenceHistory(id={self.id}, user_id={self.user_id}, field={self.field_name}, {self.old_value}->{self.new_value})>"
