"""
Embedding service for generating text embeddings.

Supports dual providers:
- Gemini text-embedding-004 (primary, free tier)
- OpenAI text-embedding-3-small (secondary, fallback)

Both generate 768-dimensional embeddings for semantic search.
"""

from typing import List
import google.generativeai as genai
from openai import OpenAI
from src.config import settings


class EmbeddingService:
    """Service for generating text embeddings using Gemini or OpenAI."""

    def __init__(self, provider: str = None):
        """
        Initialize embedding service.

        Args:
            provider: "gemini" or "openai". If None, uses settings.llm_provider
        """
        self.provider = provider or settings.llm_provider

        if self.provider == "gemini":
            if not settings.gemini_api_key:
                raise ValueError("GEMINI_API_KEY not configured")
            genai.configure(api_key=settings.gemini_api_key)

        elif self.provider == "openai":
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY not configured")
            self.openai_client = OpenAI(api_key=settings.openai_api_key)

        else:
            raise ValueError(f"Invalid provider: {self.provider}. Must be 'gemini' or 'openai'")

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

        if self.provider == "gemini":
            return await self._generate_gemini_embedding(text)
        else:
            return await self._generate_openai_embedding(text)

    async def _generate_gemini_embedding(self, text: str) -> List[float]:
        """
        Generate embedding using Gemini text-embedding-004.

        Args:
            text: Text to embed

        Returns:
            768-dimensional embedding vector
        """
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document",
            )
            return result['embedding']
        except Exception as e:
            raise Exception(f"Gemini embedding generation failed: {e}")

    async def _generate_openai_embedding(self, text: str) -> List[float]:
        """
        Generate embedding using OpenAI text-embedding-3-small.

        Args:
            text: Text to embed

        Returns:
            768-dimensional embedding vector
        """
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
                dimensions=768,
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
            768 (both Gemini and OpenAI use 768 dimensions)
        """
        return 768


# Global embedding service instance
embedding_service = EmbeddingService()
