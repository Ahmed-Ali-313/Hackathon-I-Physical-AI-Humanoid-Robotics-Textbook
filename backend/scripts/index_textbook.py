#!/usr/bin/env python3
"""
Index textbook content into Qdrant vector database.

This script reads all textbook chapters, chunks the content, generates embeddings,
and uploads them to Qdrant for RAG retrieval.

Usage:
    python backend/scripts/index_textbook.py

Environment Variables:
    QDRANT_URL: Qdrant server URL
    QDRANT_API_KEY: Qdrant API key
    QDRANT_COLLECTION_NAME: Collection name (default: textbook_chunks)
    LLM_PROVIDER: "gemini" or "openai" (default: gemini)
    GEMINI_API_KEY: Gemini API key (if using Gemini)
    OPENAI_API_KEY: OpenAI API key (if using OpenAI)
    RAG_CHUNK_SIZE: Chunk size in tokens (default: 1000)
    RAG_CHUNK_OVERLAP: Overlap in tokens (default: 100)
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Any
import time

# Add backend/src to Python path
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from dotenv import load_dotenv
import google.generativeai as genai
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "textbook_chunks")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "100"))

# Textbook directory
TEXTBOOK_DIR = Path(__file__).parent.parent.parent / "textbook" / "docs"


def validate_environment():
    """Validate required environment variables."""
    if not QDRANT_URL or not QDRANT_API_KEY:
        print("❌ Error: QDRANT_URL and QDRANT_API_KEY must be set")
        sys.exit(1)

    if LLM_PROVIDER == "gemini" and not GEMINI_API_KEY:
        print("❌ Error: GEMINI_API_KEY must be set when using Gemini provider")
        sys.exit(1)

    if LLM_PROVIDER == "openai" and not OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY must be set when using OpenAI provider")
        sys.exit(1)

    if LLM_PROVIDER not in ["gemini", "openai"]:
        print(f"❌ Error: Invalid LLM_PROVIDER '{LLM_PROVIDER}'. Must be 'gemini' or 'openai'")
        sys.exit(1)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Chunk text into smaller pieces with overlap.

    Uses paragraph boundaries for natural chunking.
    """
    # Split by paragraphs (double newline)
    paragraphs = re.split(r'\n\n+', text)

    chunks = []
    current_chunk = []
    current_size = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # Rough token estimate (1 token ≈ 4 characters)
        para_tokens = len(para) // 4

        if current_size + para_tokens > chunk_size and current_chunk:
            # Save current chunk
            chunks.append('\n\n'.join(current_chunk))

            # Start new chunk with overlap (keep last paragraph)
            if overlap > 0 and current_chunk:
                current_chunk = [current_chunk[-1]]
                current_size = len(current_chunk[-1]) // 4
            else:
                current_chunk = []
                current_size = 0

        current_chunk.append(para)
        current_size += para_tokens

    # Add final chunk
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))

    return chunks


def generate_embedding(text: str, provider: str = LLM_PROVIDER) -> List[float]:
    """Generate embedding for text using specified provider."""

    if provider == "gemini":
        genai.configure(api_key=GEMINI_API_KEY)
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document",
        )
        return result['embedding']

    elif provider == "openai":
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
            dimensions=768,
        )
        return response.data[0].embedding

    else:
        raise ValueError(f"Invalid provider: {provider}")


def extract_metadata_from_path(file_path: Path) -> Dict[str, str]:
    """Extract chapter and section metadata from file path."""

    # Example: textbook/docs/module-1-ros2/middleware.md
    parts = file_path.parts

    # Find the module and chapter
    module = None
    chapter = None

    for i, part in enumerate(parts):
        if part == "docs" and i + 1 < len(parts):
            module = parts[i + 1]
            if i + 2 < len(parts):
                chapter = parts[i + 2].replace('.md', '')

    # Generate URL
    if module and chapter:
        url = f"/docs/{module}/{chapter}"
    else:
        url = f"/docs/{file_path.stem}"

    return {
        "module": module or "unknown",
        "chapter": chapter or file_path.stem,
        "url": url,
    }


def read_markdown_file(file_path: Path) -> str:
    """Read markdown file and extract content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove frontmatter if present
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2].strip()

        return content
    except Exception as e:
        print(f"⚠️  Error reading {file_path}: {e}")
        return ""


def index_textbook():
    """Index all textbook chapters into Qdrant."""

    print("🚀 Starting textbook indexing...")
    print(f"   Provider: {LLM_PROVIDER}")
    print(f"   Chunk size: {CHUNK_SIZE} tokens")
    print(f"   Overlap: {CHUNK_OVERLAP} tokens")
    print(f"   Collection: {COLLECTION_NAME}")
    print()

    # Validate environment
    validate_environment()

    # Connect to Qdrant
    print(f"🔗 Connecting to Qdrant at {QDRANT_URL}...")
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

    # Verify collection exists
    try:
        collection_info = client.get_collection(collection_name=COLLECTION_NAME)
        print(f"✅ Connected to collection '{COLLECTION_NAME}'")
        print(f"   Current points: {collection_info.points_count}")
        print()
    except Exception as e:
        print(f"❌ Error: Collection '{COLLECTION_NAME}' not found")
        print(f"   Run: python backend/scripts/create_qdrant_collection.py")
        sys.exit(1)

    # Find all markdown files
    print(f"📚 Scanning textbook directory: {TEXTBOOK_DIR}")
    md_files = list(TEXTBOOK_DIR.rglob("*.md"))

    # Filter out intro.md and other non-chapter files
    chapter_files = [f for f in md_files if f.name not in ['intro.md', 'README.md']]

    print(f"   Found {len(chapter_files)} chapter files")
    print()

    # Process each file
    total_chunks = 0
    points = []

    for i, file_path in enumerate(chapter_files, 1):
        print(f"[{i}/{len(chapter_files)}] Processing {file_path.name}...")

        # Read content
        content = read_markdown_file(file_path)
        if not content:
            continue

        # Extract metadata
        metadata = extract_metadata_from_path(file_path)

        # Chunk content
        chunks = chunk_text(content)
        print(f"   → {len(chunks)} chunks")

        # Generate embeddings and create points
        for j, chunk in enumerate(chunks):
            try:
                # Generate embedding
                embedding = generate_embedding(chunk)

                # Create point
                point_id = f"{metadata['module']}-{metadata['chapter']}-{j}"
                point = PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "content": chunk,
                        "chapter": metadata['chapter'],
                        "module": metadata['module'],
                        "section": f"chunk-{j}",
                        "url": metadata['url'],
                        "chunk_index": j,
                        "total_chunks": len(chunks),
                    }
                )
                points.append(point)
                total_chunks += 1

                # Upload in batches of 100
                if len(points) >= 100:
                    client.upsert(collection_name=COLLECTION_NAME, points=points)
                    print(f"   ✓ Uploaded {len(points)} points")
                    points = []

                # Rate limiting
                time.sleep(0.1)

            except Exception as e:
                print(f"   ⚠️  Error processing chunk {j}: {e}")
                continue

        print()

    # Upload remaining points
    if points:
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"✓ Uploaded final {len(points)} points")

    # Verify indexing
    collection_info = client.get_collection(collection_name=COLLECTION_NAME)
    print()
    print("✅ Indexing complete!")
    print(f"   Total chunks indexed: {total_chunks}")
    print(f"   Total points in collection: {collection_info.points_count}")
    print()
    print("📝 Next steps:")
    print("   1. Test retrieval: Search for 'What is VSLAM?' in the chatbot")
    print("   2. Verify source attribution links work correctly")


if __name__ == "__main__":
    index_textbook()
