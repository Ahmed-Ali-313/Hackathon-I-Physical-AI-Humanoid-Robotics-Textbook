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
        Initialize embedding service with lazy OpenAI client initialization.

        The OpenAI client is only created when actually needed, allowing
        the server to start even without an API key configured.
        """
        self.client = None
        self._client_initialized = False
        self.model = "text-embedding-3-small"

        # Check if API key is available but don't fail if missing
        if not settings.openai_api_key:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("OPENAI_API_KEY not configured - embedding features will be unavailable")

    def _ensure_client_initialized(self):
        """
        Ensure OpenAI client is initialized (lazy initialization).

        Raises:
            ValueError: If OPENAI_API_KEY is not configured
        """
        if self._client_initialized:
            return

        if not settings.openai_api_key:
            raise ValueError("Embedding features are currently unavailable. OpenAI API key is not configured.")

        self.client = OpenAI(
            api_key=settings.openai_api_key,
            timeout=10.0,  # 10 second timeout for embedding calls
        )
        self._client_initialized = True
        import logging
        logger = logging.getLogger(__name__)
        logger.info("OpenAI embedding client initialized successfully")

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

        # Ensure OpenAI client is initialized (lazy initialization)
        self._ensure_client_initialized()

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
