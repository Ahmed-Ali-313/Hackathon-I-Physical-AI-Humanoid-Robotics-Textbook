"""
Add sample content metadata to database for personalization testing
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.models.content_metadata import ContentMetadata

DATABASE_URL = "sqlite+aiosqlite:///./app.db"

async def add_sample_metadata():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Sample content metadata for textbook chapters
        metadata_items = [
            ContentMetadata(
                content_id="ros2-middleware",
                content_path="/docs/module-1-ros2/middleware",
                title="ROS 2 Middleware Architecture",
                hardware_tags=["workstation", "high_end_desktop"],
                software_requirements={
                    "ros2_level": "intermediate",
                    "gazebo_level": "beginner"
                }
            ),
            ContentMetadata(
                content_id="isaac-sim-intro",
                content_path="/docs/module-3-isaac/isaac-sim",
                title="NVIDIA Isaac Sim Introduction",
                hardware_tags=["workstation", "high_end_desktop"],
                software_requirements={
                    "isaac_level": "beginner",
                    "ros2_level": "intermediate"
                }
            ),
            ContentMetadata(
                content_id="jetson-orin-setup",
                content_path="/docs/hardware/edge-kits",
                title="Jetson Orin Setup Guide",
                hardware_tags=["jetson_orin"],
                software_requirements={
                    "ros2_level": "intermediate"
                }
            ),
        ]
        
        for item in metadata_items:
            session.add(item)
        
        await session.commit()
        print(f"✅ Added {len(metadata_items)} content metadata items")

if __name__ == "__main__":
    asyncio.run(add_sample_metadata())
