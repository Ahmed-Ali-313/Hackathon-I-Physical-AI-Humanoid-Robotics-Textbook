#!/usr/bin/env python3
"""
Content Metadata Sync Script

Extracts personalization metadata from Markdown frontmatter and syncs to database.

Usage:
    python scripts/sync_content_metadata.py

This script:
1. Scans all .md and .mdx files in the docs directory
2. Extracts personalization metadata from frontmatter
3. Upserts metadata to content_metadata table
4. Reports sync statistics

Frontmatter format:
---
id: nvidia-isaac-sim-intro
title: Introduction to NVIDIA Isaac Sim
personalization:
  hardware:
    - rtx_12gb
    - rtx_24gb
  software:
    ros2_level: intermediate
    isaac_level: beginner
---
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Optional
import frontmatter
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import AsyncSessionLocal
from sqlalchemy import text


async def extract_metadata_from_file(file_path: Path, docs_root: Path) -> Optional[Dict]:
    """
    Extract personalization metadata from a markdown file.

    Args:
        file_path: Path to markdown file
        docs_root: Root docs directory for relative path calculation

    Returns:
        Dictionary with metadata or None if no personalization data
    """
    try:
        # Parse frontmatter
        post = frontmatter.load(file_path)

        # Check if personalization metadata exists
        if 'personalization' not in post.metadata:
            return None

        # Extract required fields
        content_id = post.metadata.get('id')
        title = post.metadata.get('title', file_path.stem)
        personalization = post.metadata['personalization']

        if not content_id:
            print(f"Warning: No 'id' field in {file_path}, skipping")
            return None

        # Extract hardware tags (array)
        hardware_tags = personalization.get('hardware', [])
        if not isinstance(hardware_tags, list):
            hardware_tags = [hardware_tags]

        # Extract software requirements (dict)
        software_requirements = personalization.get('software', {})

        # Calculate relative path
        relative_path = file_path.relative_to(docs_root)

        return {
            'content_id': content_id,
            'content_path': str(relative_path),
            'title': title,
            'hardware_tags': hardware_tags,
            'software_requirements': software_requirements
        }

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None


async def upsert_metadata(session, metadata: Dict) -> bool:
    """
    Upsert metadata to database.

    Args:
        session: Database session
        metadata: Metadata dictionary

    Returns:
        True if successful, False otherwise
    """
    try:
        # Convert software_requirements to JSON string
        software_json = json.dumps(metadata['software_requirements']) if metadata['software_requirements'] else None

        # Upsert query (PostgreSQL specific)
        query = text("""
            INSERT INTO content_metadata (content_id, content_path, title, hardware_tags, software_requirements, updated_at)
            VALUES (:content_id, :content_path, :title, :hardware_tags, :software_requirements::jsonb, NOW())
            ON CONFLICT (content_id)
            DO UPDATE SET
                content_path = EXCLUDED.content_path,
                title = EXCLUDED.title,
                hardware_tags = EXCLUDED.hardware_tags,
                software_requirements = EXCLUDED.software_requirements,
                updated_at = NOW()
        """)

        await session.execute(query, {
            'content_id': metadata['content_id'],
            'content_path': metadata['content_path'],
            'title': metadata['title'],
            'hardware_tags': metadata['hardware_tags'],
            'software_requirements': software_json
        })

        return True

    except Exception as e:
        print(f"Error upserting metadata for {metadata['content_id']}: {e}")
        return False


async def sync_content_metadata(docs_dir: str = "../../textbook/docs"):
    """
    Main sync function.

    Args:
        docs_dir: Path to docs directory (relative to script location)
    """
    print("Starting content metadata sync...")

    # Resolve docs directory
    script_dir = Path(__file__).parent
    docs_root = (script_dir / docs_dir).resolve()

    if not docs_root.exists():
        print(f"Error: Docs directory not found: {docs_root}")
        return

    print(f"Scanning directory: {docs_root}")

    # Find all markdown files
    md_files = list(docs_root.rglob("*.md")) + list(docs_root.rglob("*.mdx"))
    print(f"Found {len(md_files)} markdown files")

    # Extract metadata from all files
    metadata_list = []
    for md_file in md_files:
        metadata = await extract_metadata_from_file(md_file, docs_root)
        if metadata:
            metadata_list.append(metadata)

    print(f"Extracted metadata from {len(metadata_list)} files with personalization data")

    if not metadata_list:
        print("No files with personalization metadata found")
        return

    # Sync to database
    async with AsyncSessionLocal() as session:
        success_count = 0
        for metadata in metadata_list:
            if await upsert_metadata(session, metadata):
                success_count += 1
                print(f"✓ Synced: {metadata['content_id']}")

        await session.commit()

    print(f"\nSync complete: {success_count}/{len(metadata_list)} entries synced successfully")


if __name__ == "__main__":
    # Run sync
    asyncio.run(sync_content_metadata())
