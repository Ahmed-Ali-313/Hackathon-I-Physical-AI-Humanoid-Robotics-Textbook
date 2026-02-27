"""
Embedding service for generating text embeddings using OpenAI.

Uses text-embedding-3-small model to generate 768-dimensional embeddings
for semantic search in the RAG chatbot.
"""

from typing import List
from openai import OpenAI
from src.config import settings


class EmbeddingService:
    """Service for generating text embeddings using OpenAI."""

    def __init__(self):
        """
        Initialize embedding service with OpenAI.

        Raises:
            ValueError: If OPENAI_API_KEY is not configured
        """
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY not configured")

        self.client = OpenAI(
            api_key=settings.openai_api_key,
            timeout=10.0,  # 10 second timeout for embedding calls
        )
        self.model = "text-embedding-3-small"

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text.

        Args:
            text: Text to embed

        Returns:
            768-dimensional embedding vector

        Raises:
            ValueError: If text is empty
            Exception: If API call fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
                dimensions=768
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"OpenAI embedding generation failed: {e}")

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of 768-dimensional embedding vectors

        Raises:
            ValueError: If texts list is empty
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")

        embeddings = []
        for text in texts:
            embedding = await self.generate_embedding(text)
            embeddings.append(embedding)

        return embeddings

    def get_embedding_dimension(self) -> int:
        """
        Get embedding dimension.

        Returns:
            768 (OpenAI text-embedding-3-small dimension)
        """
        return 768


# Global embedding service instance
embedding_service = EmbeddingService()
