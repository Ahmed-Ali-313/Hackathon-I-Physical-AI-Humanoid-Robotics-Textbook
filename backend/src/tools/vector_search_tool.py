"""
Vector search tool for OpenAI Agents SDK.

Agent tool that searches Qdrant for relevant textbook chunks.
"""

from typing import List, Dict, Any
from src.services.vector_service import vector_service
from src.services.embedding_service import embedding_service


class VectorSearchTool:
    """
    Agent tool for searching Qdrant vector database.

    Generates embeddings for queries and searches for top-k relevant chunks
    with confidence threshold filtering.
    """

    def __init__(self):
        """Initialize vector search tool."""
        self.name = "vector_search"
        self.description = "Search the textbook for relevant content based on a question"
        self.vector_service = vector_service
        self.embedding_service = embedding_service

    async def execute(
        self,
        query: str,
        top_k: int = 5,
        confidence_threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        Execute vector search for query.

        Args:
            query: User's question
            top_k: Number of results to return (default: 5)
            confidence_threshold: Minimum confidence score (default: 0.7)

        Returns:
            List of search results with content, metadata, and confidence scores

        Raises:
            ValueError: If query is empty
            Exception: If search fails
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        try:
            # Generate embedding for query
            query_embedding = await self.embedding_service.generate_embedding(query)

            # Search Qdrant
            results = await self.vector_service.search(
                query_vector=query_embedding,
                top_k=top_k,
                confidence_threshold=confidence_threshold,
            )

            return results

        except Exception as e:
            raise Exception(f"Vector search failed: {e}")

    def get_tool_definition(self) -> Dict[str, Any]:
        """
        Get tool definition for OpenAI Agents SDK.

        Returns:
            Tool definition dictionary
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user's question to search for in the textbook",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5)",
                        "default": 5,
                    },
                    "confidence_threshold": {
                        "type": "number",
                        "description": "Minimum confidence score (0.0-1.0, default: 0.7)",
                        "default": 0.7,
                    },
                },
                "required": ["query"],
            },
        }


# Global vector search tool instance
vector_search_tool = VectorSearchTool()
