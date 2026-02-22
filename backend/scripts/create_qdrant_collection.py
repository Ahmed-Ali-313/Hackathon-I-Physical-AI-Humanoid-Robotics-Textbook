#!/usr/bin/env python3
"""
Create Qdrant collection for textbook chunks.

This script creates a Qdrant collection with 768-dimensional vectors
for storing textbook content embeddings.

Usage:
    python backend/scripts/create_qdrant_collection.py

Environment Variables:
    QDRANT_URL: Qdrant server URL (e.g., https://your-cluster.qdrant.io)
    QDRANT_API_KEY: Qdrant API key
    QDRANT_COLLECTION_NAME: Collection name (default: textbook_chunks)
"""

import os
import sys
from pathlib import Path

# Add backend/src to Python path
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "textbook_chunks")
VECTOR_SIZE = 768  # Gemini text-embedding-004 and OpenAI text-embedding-3-small both use 768 dimensions


def create_collection():
    """Create Qdrant collection for textbook chunks."""

    # Validate environment variables
    if not QDRANT_URL:
        print("❌ Error: QDRANT_URL environment variable not set")
        sys.exit(1)

    if not QDRANT_API_KEY:
        print("❌ Error: QDRANT_API_KEY environment variable not set")
        sys.exit(1)

    print(f"🔗 Connecting to Qdrant at {QDRANT_URL}...")

    try:
        # Initialize Qdrant client
        client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
        )

        # Check if collection already exists
        collections = client.get_collections().collections
        collection_names = [col.name for col in collections]

        if COLLECTION_NAME in collection_names:
            print(f"⚠️  Collection '{COLLECTION_NAME}' already exists")
            response = input("Do you want to recreate it? (yes/no): ")
            if response.lower() in ['yes', 'y']:
                print(f"🗑️  Deleting existing collection '{COLLECTION_NAME}'...")
                client.delete_collection(collection_name=COLLECTION_NAME)
            else:
                print("✅ Keeping existing collection")
                return

        # Create collection
        print(f"📦 Creating collection '{COLLECTION_NAME}' with {VECTOR_SIZE}-dimensional vectors...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,  # Cosine similarity for semantic search
            ),
        )

        # Verify collection was created
        collection_info = client.get_collection(collection_name=COLLECTION_NAME)
        print(f"✅ Collection created successfully!")
        print(f"   - Name: {collection_info.config.params.vectors.size}")
        print(f"   - Vector size: {collection_info.config.params.vectors.size}")
        print(f"   - Distance metric: {collection_info.config.params.vectors.distance}")
        print(f"   - Points count: {collection_info.points_count}")

        # Create a test point to verify the collection works
        print("\n🧪 Testing collection with a sample point...")
        test_vector = [0.0] * VECTOR_SIZE
        test_point = PointStruct(
            id="test-point",
            vector=test_vector,
            payload={
                "content": "Test content",
                "chapter": "test",
                "section": "test",
                "url": "/test",
            }
        )

        client.upsert(
            collection_name=COLLECTION_NAME,
            points=[test_point],
        )

        # Delete test point
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=["test-point"],
        )

        print("✅ Collection is ready for indexing!")
        print(f"\n📝 Next steps:")
        print(f"   1. Run: python backend/scripts/index_textbook.py")
        print(f"   2. This will index all textbook chapters into Qdrant")

    except Exception as e:
        print(f"❌ Error creating collection: {e}")
        sys.exit(1)


if __name__ == "__main__":
    create_collection()
