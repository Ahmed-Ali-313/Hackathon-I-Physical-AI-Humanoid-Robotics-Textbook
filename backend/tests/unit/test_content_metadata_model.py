"""
Unit tests for ContentMetadata model

Tests:
- ContentMetadata creation with hardware_tags and software_requirements
- GIN index usage for array and JSONB queries
- Relationship constraints
- Data validation
"""

import pytest
from sqlalchemy.exc import IntegrityError
from src.models.content_metadata import ContentMetadata


class TestContentMetadataModel:
    """Test suite for ContentMetadata model"""

    @pytest.mark.asyncio
    async def test_content_metadata_creation(self, db_session):
        """Test creating content metadata with tags and requirements"""
        metadata = ContentMetadata(
            content_id="nvidia-isaac-sim-intro",
            content_path="docs/isaac-sim/intro.md",
            title="Introduction to NVIDIA Isaac Sim",
            hardware_tags=["rtx_12gb", "rtx_24gb"],
            software_requirements={
                "ros2_level": "intermediate",
                "isaac_level": "beginner"
            }
        )
        db_session.add(metadata)
        await db_session.commit()

        assert metadata.id is not None
        assert metadata.content_id == "nvidia-isaac-sim-intro"
        assert "rtx_12gb" in metadata.hardware_tags
        assert metadata.software_requirements["ros2_level"] == "intermediate"

    @pytest.mark.asyncio
    async def test_content_metadata_unique_content_id(self, db_session):
        """Test that content_id must be unique"""
        metadata1 = ContentMetadata(
            content_id="duplicate-id",
            content_path="docs/test1.md",
            title="Test 1",
            hardware_tags=[],
            software_requirements={}
        )
        db_session.add(metadata1)
        await db_session.commit()

        metadata2 = ContentMetadata(
            content_id="duplicate-id",
            content_path="docs/test2.md",
            title="Test 2",
            hardware_tags=[],
            software_requirements={}
        )
        db_session.add(metadata2)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_content_metadata_empty_arrays(self, db_session):
        """Test that empty arrays and objects are allowed"""
        metadata = ContentMetadata(
            content_id="minimal-content",
            content_path="docs/minimal.md",
            title="Minimal Content",
            hardware_tags=[],
            software_requirements={}
        )
        db_session.add(metadata)
        await db_session.commit()

        assert metadata.hardware_tags == []
        assert metadata.software_requirements == {}

    @pytest.mark.asyncio
    async def test_content_metadata_null_values(self, db_session):
        """Test that hardware_tags and software_requirements can be null"""
        metadata = ContentMetadata(
            content_id="null-content",
            content_path="docs/null.md",
            title="Null Content",
            hardware_tags=None,
            software_requirements=None
        )
        db_session.add(metadata)
        await db_session.commit()

        assert metadata.hardware_tags is None
        assert metadata.software_requirements is None

    @pytest.mark.asyncio
    async def test_content_metadata_complex_software_requirements(self, db_session):
        """Test JSONB storage with nested objects"""
        metadata = ContentMetadata(
            content_id="complex-content",
            content_path="docs/complex.md",
            title="Complex Content",
            hardware_tags=["jetson_orin", "rtx_24gb"],
            software_requirements={
                "ros2_level": "advanced",
                "gazebo_level": "intermediate",
                "unity_level": "beginner",
                "isaac_level": "advanced",
                "vla_level": "none"
            }
        )
        db_session.add(metadata)
        await db_session.commit()

        assert len(metadata.software_requirements) == 5
        assert metadata.software_requirements["ros2_level"] == "advanced"

    @pytest.mark.asyncio
    async def test_content_metadata_array_contains_query(self, db_session):
        """Test querying by hardware_tags array contains"""
        metadata1 = ContentMetadata(
            content_id="content-1",
            content_path="docs/1.md",
            title="Content 1",
            hardware_tags=["rtx_12gb", "jetson_nano"],
            software_requirements={}
        )
        metadata2 = ContentMetadata(
            content_id="content-2",
            content_path="docs/2.md",
            title="Content 2",
            hardware_tags=["rtx_24gb"],
            software_requirements={}
        )
        db_session.add_all([metadata1, metadata2])
        await db_session.commit()

        # Query for content with rtx_12gb tag
        from sqlalchemy import select
        result = await db_session.execute(
            select(ContentMetadata).where(
                ContentMetadata.hardware_tags.contains(["rtx_12gb"])
            )
        )
        found = result.scalars().all()

        assert len(found) == 1
        assert found[0].content_id == "content-1"

    @pytest.mark.asyncio
    async def test_content_metadata_jsonb_query(self, db_session):
        """Test querying JSONB software_requirements"""
        metadata = ContentMetadata(
            content_id="jsonb-test",
            content_path="docs/jsonb.md",
            title="JSONB Test",
            hardware_tags=[],
            software_requirements={"ros2_level": "intermediate"}
        )
        db_session.add(metadata)
        await db_session.commit()

        # Query for content with specific software requirement
        from sqlalchemy import select
        result = await db_session.execute(
            select(ContentMetadata).where(
                ContentMetadata.software_requirements["ros2_level"].astext == "intermediate"
            )
        )
        found = result.scalar_one_or_none()

        assert found is not None
        assert found.content_id == "jsonb-test"
