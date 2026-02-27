"""
Retrieve context tool for OpenAI Agents SDK.

Agent tool that formats retrieved chunks with source metadata.
"""

from typing import List, Dict, Any


class RetrieveContextTool:
    """
    Agent tool for formatting retrieved context.

    Takes search results and formats them into a structured context
    with source attribution for the agent to use in response generation.
    """

    def __init__(self):
        """Initialize retrieve context tool."""
        self.name = "retrieve_context"
        self.description = "Format retrieved textbook chunks into structured context with sources"

    async def execute(
        self,
        search_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Execute context retrieval and formatting.

        Args:
            search_results: List of search results from vector_search_tool

        Returns:
            Formatted context dictionary with content and sources

        Raises:
            ValueError: If search_results is empty or invalid
        """
        if not search_results:
            return {
                "context": "",
                "sources": [],
                "has_context": False,
            }

        if not isinstance(search_results, list):
            raise ValueError("search_results must be a list")

        try:
            # Extract content from all chunks
            context_parts = []
            sources = []

            for i, result in enumerate(search_results, 1):
                # Validate result structure
                if not isinstance(result, dict):
                    continue

                content = result.get("content", "")
                metadata = result.get("metadata", {})
                confidence = result.get("confidence", 0.0)

                if not content:
                    continue

                # Truncate very long chunks to reduce context size (max 800 chars per chunk)
                if len(content) > 800:
                    content = content[:800] + "..."

                # Format context with source reference
                context_parts.append(f"[Source {i}] {content}")

                # Build source reference
                source = {
                    "index": i,
                    "chapter": metadata.get("chapter", "unknown"),
                    "module": metadata.get("module", "unknown"),
                    "section": metadata.get("section", "unknown"),
                    "url": metadata.get("url", ""),
                    "confidence": confidence,
                }
                sources.append(source)

            # Combine all context parts
            combined_context = "\n\n".join(context_parts)

            return {
                "context": combined_context,
                "sources": sources,
                "has_context": len(context_parts) > 0,
                "num_sources": len(sources),
            }

        except Exception as e:
            raise Exception(f"Context retrieval failed: {e}")

    def format_sources_for_response(self, sources: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Format sources for inclusion in chat response.

        Args:
            sources: List of source dictionaries

        Returns:
            List of formatted source references for ChatMessage
        """
        formatted_sources = []

        for source in sources:
            formatted_source = {
                "chapter": source.get("chapter", "unknown"),
                "section": source.get("section", "unknown"),
                "url": source.get("url", ""),
            }
            formatted_sources.append(formatted_source)

        return formatted_sources

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
                    "search_results": {
                        "type": "array",
                        "description": "List of search results from vector_search_tool",
                        "items": {
                            "type": "object",
                            "properties": {
                                "content": {"type": "string"},
                                "confidence": {"type": "number"},
                                "metadata": {"type": "object"},
                            },
                        },
                    },
                },
                "required": ["search_results"],
            },
        }


# Global retrieve context tool instance
retrieve_context_tool = RetrieveContextTool()
