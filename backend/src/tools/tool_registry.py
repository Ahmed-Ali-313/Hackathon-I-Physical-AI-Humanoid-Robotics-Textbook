"""
Tool registry for OpenAI Agents SDK.

Registers all agent tools and provides tool management functionality.
"""

from typing import List, Dict, Any
from src.tools.vector_search_tool import vector_search_tool
from src.tools.retrieve_context_tool import retrieve_context_tool


class ToolRegistry:
    """
    Registry for managing agent tools.

    Provides centralized tool registration and retrieval for the agent service.
    """

    def __init__(self):
        """Initialize tool registry."""
        self.tools = {}
        self._register_default_tools()

    def _register_default_tools(self):
        """Register default RAG tools."""
        self.register_tool(vector_search_tool)
        self.register_tool(retrieve_context_tool)

    def register_tool(self, tool: Any):
        """
        Register a tool.

        Args:
            tool: Tool instance to register

        Raises:
            ValueError: If tool is invalid or already registered
        """
        if not hasattr(tool, 'name'):
            raise ValueError("Tool must have a 'name' attribute")

        if tool.name in self.tools:
            raise ValueError(f"Tool '{tool.name}' is already registered")

        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> Any:
        """
        Get a tool by name.

        Args:
            name: Tool name

        Returns:
            Tool instance

        Raises:
            KeyError: If tool not found
        """
        if name not in self.tools:
            raise KeyError(f"Tool '{name}' not found in registry")

        return self.tools[name]

    def get_all_tools(self) -> List[Any]:
        """
        Get all registered tools.

        Returns:
            List of tool instances
        """
        return list(self.tools.values())

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Get tool definitions for all registered tools.

        Returns:
            List of tool definition dictionaries for OpenAI Agents SDK
        """
        definitions = []

        for tool in self.tools.values():
            if hasattr(tool, 'get_tool_definition'):
                definitions.append(tool.get_tool_definition())

        return definitions

    def get_tool_names(self) -> List[str]:
        """
        Get names of all registered tools.

        Returns:
            List of tool names
        """
        return list(self.tools.keys())

    def has_tool(self, name: str) -> bool:
        """
        Check if a tool is registered.

        Args:
            name: Tool name

        Returns:
            True if tool is registered, False otherwise
        """
        return name in self.tools

    def unregister_tool(self, name: str):
        """
        Unregister a tool.

        Args:
            name: Tool name

        Raises:
            KeyError: If tool not found
        """
        if name not in self.tools:
            raise KeyError(f"Tool '{name}' not found in registry")

        del self.tools[name]

    def clear_tools(self):
        """Clear all registered tools."""
        self.tools.clear()

    def get_tool_count(self) -> int:
        """
        Get number of registered tools.

        Returns:
            Number of tools
        """
        return len(self.tools)


# Global tool registry instance
tool_registry = ToolRegistry()
