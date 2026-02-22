"""
Vector service for Qdrant search operations.

Handles vector search with confidence threshold filtering and top-k retrieval.
"""

from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, ScoredPoint
from src.config import settings


class VectorService:
    """Service for vector search operations using Qdrant."""

    def __init__(self):
        """Initialize vector service with Qdrant client."""
        if not settings.qdrant_url:
            raise ValueError("QDRANT_URL not configured")

        if not settings.qdrant_api_key:
            raise ValueError("QDRANT_API_KEY not configured")

        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
        self.collection_name = settings.qdrant_collection_name
        self.confidence_threshold = settings.rag_confidence_threshold
        self.top_k = settings.rag_top_k_results

    async def search(
        self,
        query_vector: List[float],
        top_k: Optional[int] = None,
        confidence_threshold: Optional[float] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in Qdrant.

        Args:
            query_vector: Query embedding vector (768-dim)
            top_k: Number of results to return (default: from config)
            confidence_threshold: Minimum cosine similarity score (default: 0.7)
            filters: Optional metadata filters (e.g., {"chapter": "isaac-sim"})

        Returns:
            List of search results with content, metadata, and confidence scores

        Raises:
            ValueError: If query_vector is invalid
            Exception: If Qdrant search fails
        """
        if not query_vector:
            raise ValueError("Query vector cannot be empty")

        if len(query_vector) != 768:
            raise ValueError(f"Query vector must be 768-dimensional, got {len(query_vector)}")

        top_k = top_k or self.top_k
        confidence_threshold = confidence_threshold or self.confidence_threshold

        try:
            # Build filter if provided
            query_filter = None
            if filters:
                conditions = []
                for key, value in filters.items():
                    conditions.append(
                        FieldCondition(key=key, match=MatchValue(value=value))
                    )
                if conditions:
                    query_filter = Filter(must=conditions)

            # Perform search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
                query_filter=query_filter,
                score_threshold=confidence_threshold,
            )

            # Format results
            results = []
            for point in search_results:
                result = {
                    "id": point.id,
                    "content": point.payload.get("content", ""),
                    "confidence": float(point.score),  # Cosine similarity (0.0-1.0)
                    "metadata": {
                        "chapter": point.payload.get("chapter", ""),
                        "module": point.payload.get("module", ""),
                        "section": point.payload.get("section", ""),
                        "url": point.payload.get("url", ""),
                        "chunk_index": point.payload.get("chunk_index", 0),
                        "total_chunks": point.payload.get("total_chunks", 0),
                    }
                }
                results.append(result)

            return results

        except Exception as e:
            raise Exception(f"Qdrant search failed: {e}")

    async def search_by_text(
        self,
        query_text: str,
        embedding_vector: List[float],
        top_k: Optional[int] = None,
        confidence_threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search using text query (with pre-generated embedding).

        Args:
            query_text: Original query text (for logging/debugging)
            embedding_vector: Query embedding vector
            top_k: Number of results to return
            confidence_threshold: Minimum confidence score

        Returns:
            List of search results
        """
        if not query_text or not query_text.strip():
            raise ValueError("Query text cannot be empty")

        return await self.search(
            query_vector=embedding_vector,
            top_k=top_k,
            confidence_threshold=confidence_threshold,
        )

    async def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the Qdrant collection.

        Returns:
            Collection metadata (name, vector size, points count)
        """
        try:
            collection_info = self.client.get_collection(collection_name=self.collection_name)

            return {
                "name": self.collection_name,
                "vector_size": collection_info.config.params.vectors.size,
                "distance_metric": collection_info.config.params.vectors.distance.name,
                "points_count": collection_info.points_count,
            }
        except Exception as e:
            raise Exception(f"Failed to get collection info: {e}")

    async def health_check(self) -> bool:
        """
        Check if Qdrant connection is healthy.

        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            # Try to get collection info
            await self.get_collection_info()
            return True
        except Exception:
            return False

    def validate_confidence_score(self, score: float) -> bool:
        """
        Validate that confidence score is in valid range (0.0-1.0).

        Args:
            score: Confidence score to validate

        Returns:
            True if valid, False otherwise
        """
        return 0.0 <= score <= 1.0


# Global vector service instance
vector_service = VectorService()
