"""
PersonalizationProfile Model

SQLAlchemy model for personalization_profiles table.
Stores user hardware and software preferences.
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, CheckConstraint, TypeDecorator, CHAR
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


class PersonalizationProfile(Base):
    """PersonalizationProfile model for user preferences"""

    __tablename__ = "personalization_profiles"

    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    # Hardware preferences
    workstation_type = Column(String(50), nullable=True)
    edge_kit_available = Column(String(50), nullable=True)
    robot_tier_access = Column(String(50), nullable=True)

    # Software experience levels
    ros2_level = Column(String(50), nullable=True)
    gazebo_level = Column(String(50), nullable=True)
    unity_level = Column(String(50), nullable=True)
    isaac_level = Column(String(50), nullable=True)
    vla_level = Column(String(50), nullable=True)

    # Language preference
    preferred_language = Column(String(10), nullable=True, default='en')

    # Personalization state
    is_personalized = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship to User (one-to-one)
    user = relationship("User", back_populates="personalization_profile")

    # Check constraints for enum validation
    __table_args__ = (
        CheckConstraint(
            "workstation_type IS NULL OR workstation_type IN ('laptop', 'mid_range_desktop', 'high_end_desktop', 'workstation', 'cloud_instance')",
            name="valid_workstation_type"
        ),
        CheckConstraint(
            "edge_kit_available IS NULL OR edge_kit_available IN ('none', 'jetson_nano', 'jetson_orin', 'raspberry_pi', 'other')",
            name="valid_edge_kit"
        ),
        CheckConstraint(
            "robot_tier_access IS NULL OR robot_tier_access IN ('none', 'tier_1', 'tier_2', 'tier_3')",
            name="valid_robot_tier"
        ),
        CheckConstraint(
            "ros2_level IS NULL OR ros2_level IN ('none', 'beginner', 'intermediate', 'advanced')",
            name="valid_ros2_level"
        ),
        CheckConstraint(
            "gazebo_level IS NULL OR gazebo_level IN ('none', 'beginner', 'intermediate', 'advanced')",
            name="valid_gazebo_level"
        ),
        CheckConstraint(
            "unity_level IS NULL OR unity_level IN ('none', 'beginner', 'intermediate', 'advanced')",
            name="valid_unity_level"
        ),
        CheckConstraint(
            "isaac_level IS NULL OR isaac_level IN ('none', 'beginner', 'intermediate', 'advanced')",
            name="valid_isaac_level"
        ),
        CheckConstraint(
            "vla_level IS NULL OR vla_level IN ('none', 'beginner', 'intermediate', 'advanced')",
            name="valid_vla_level"
        ),
    )

    def __repr__(self):
        return f"<PersonalizationProfile(id={self.id}, user_id={self.user_id}, is_personalized={self.is_personalized})>"
