"""
ContentMetadata Model

SQLAlchemy model for content_metadata table.
Stores hardware and software requirements for content personalization.
"""

from sqlalchemy import Column, String, DateTime, ARRAY, Text, TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from datetime import datetime
import uuid
import json

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


class JSONType(TypeDecorator):
    """Platform-independent JSON type."""
    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        else:
            return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        else:
            return json.loads(value) if isinstance(value, str) else value


class ArrayType(TypeDecorator):
    """Platform-independent Array type."""
    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(ARRAY(String))
        else:
            return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        else:
            return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        else:
            return json.loads(value) if isinstance(value, str) else value


class ContentMetadata(Base):
    """ContentMetadata model for content personalization"""

    __tablename__ = "content_metadata"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    content_id = Column(String(255), unique=True, nullable=False, index=True)
    content_path = Column(String(512), nullable=False)
    title = Column(String(512), nullable=False)

    # Hardware tags (array of strings)
    hardware_tags = Column(ArrayType(), nullable=True)

    # Software requirements (JSON object)
    software_requirements = Column(JSONType(), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<ContentMetadata(id={self.id}, content_id={self.content_id}, title={self.title})>"
