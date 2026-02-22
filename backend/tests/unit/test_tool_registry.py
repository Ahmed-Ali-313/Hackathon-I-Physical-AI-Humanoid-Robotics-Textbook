"""
Tests for tool registry.

Tests tool registration and management.
"""

import pytest
from unittest.mock import Mock
from src.tools.tool_registry import ToolRegistry


@pytest.fixture
def mock_tool():
    """Create a mock tool."""
    tool = Mock()
    tool.name = "test_tool"
    tool.description = "Test tool description"
    tool.get_tool_definition.return_value = {
        "name": "test_tool",
        "description": "Test tool",
        "parameters": {},
    }
    return tool


def test_tool_registry_initialization():
    """Test tool registry initializes with default tools."""
    registry = ToolRegistry()

    # Should have default RAG tools registered
    assert registry.get_tool_count() >= 2
    assert registry.has_tool("vector_search")
    assert registry.has_tool("retrieve_context")


def test_register_tool(mock_tool):
    """Test registering a tool."""
    registry = ToolRegistry()
    registry.clear_tools()

    registry.register_tool(mock_tool)

    assert registry.has_tool("test_tool")
    assert registry.get_tool_count() == 1


def test_register_tool_without_name():
    """Test registering tool without name raises error."""
    registry = ToolRegistry()
    invalid_tool = Mock(spec=[])  # No 'name' attribute

    with pytest.raises(ValueError, match="Tool must have a 'name' attribute"):
        registry.register_tool(invalid_tool)


def test_register_duplicate_tool(mock_tool):
    """Test registering duplicate tool raises error."""
    registry = ToolRegistry()
    registry.clear_tools()

    registry.register_tool(mock_tool)

    with pytest.raises(ValueError, match="Tool 'test_tool' is already registered"):
        registry.register_tool(mock_tool)


def test_get_tool(mock_tool):
    """Test getting a tool by name."""
    registry = ToolRegistry()
    registry.clear_tools()
    registry.register_tool(mock_tool)

    tool = registry.get_tool("test_tool")

    assert tool == mock_tool


def test_get_tool_not_found():
    """Test getting non-existent tool raises error."""
    registry = ToolRegistry()
    registry.clear_tools()

    with pytest.raises(KeyError, match="Tool 'nonexistent' not found"):
        registry.get_tool("nonexistent")


def test_get_all_tools(mock_tool):
    """Test getting all registered tools."""
    registry = ToolRegistry()
    registry.clear_tools()

    mock_tool_2 = Mock()
    mock_tool_2.name = "test_tool_2"

    registry.register_tool(mock_tool)
    registry.register_tool(mock_tool_2)

    tools = registry.get_all_tools()

    assert len(tools) == 2
    assert mock_tool in tools
    assert mock_tool_2 in tools


def test_get_tool_definitions(mock_tool):
    """Test getting tool definitions."""
    registry = ToolRegistry()
    registry.clear_tools()
    registry.register_tool(mock_tool)

    definitions = registry.get_tool_definitions()

    assert len(definitions) == 1
    assert definitions[0]["name"] == "test_tool"
    mock_tool.get_tool_definition.assert_called_once()


def test_get_tool_definitions_skips_tools_without_method():
    """Test get_tool_definitions skips tools without get_tool_definition method."""
    registry = ToolRegistry()
    registry.clear_tools()

    tool_without_method = Mock(spec=['name'])
    tool_without_method.name = "incomplete_tool"

    registry.register_tool(tool_without_method)

    definitions = registry.get_tool_definitions()

    assert len(definitions) == 0


def test_get_tool_names(mock_tool):
    """Test getting tool names."""
    registry = ToolRegistry()
    registry.clear_tools()

    mock_tool_2 = Mock()
    mock_tool_2.name = "test_tool_2"

    registry.register_tool(mock_tool)
    registry.register_tool(mock_tool_2)

    names = registry.get_tool_names()

    assert len(names) == 2
    assert "test_tool" in names
    assert "test_tool_2" in names


def test_has_tool(mock_tool):
    """Test checking if tool exists."""
    registry = ToolRegistry()
    registry.clear_tools()

    assert registry.has_tool("test_tool") is False

    registry.register_tool(mock_tool)

    assert registry.has_tool("test_tool") is True


def test_unregister_tool(mock_tool):
    """Test unregistering a tool."""
    registry = ToolRegistry()
    registry.clear_tools()
    registry.register_tool(mock_tool)

    assert registry.has_tool("test_tool") is True

    registry.unregister_tool("test_tool")

    assert registry.has_tool("test_tool") is False
    assert registry.get_tool_count() == 0


def test_unregister_tool_not_found():
    """Test unregistering non-existent tool raises error."""
    registry = ToolRegistry()
    registry.clear_tools()

    with pytest.raises(KeyError, match="Tool 'nonexistent' not found"):
        registry.unregister_tool("nonexistent")


def test_clear_tools(mock_tool):
    """Test clearing all tools."""
    registry = ToolRegistry()
    registry.clear_tools()

    mock_tool_2 = Mock()
    mock_tool_2.name = "test_tool_2"

    registry.register_tool(mock_tool)
    registry.register_tool(mock_tool_2)

    assert registry.get_tool_count() == 2

    registry.clear_tools()

    assert registry.get_tool_count() == 0


def test_get_tool_count(mock_tool):
    """Test getting tool count."""
    registry = ToolRegistry()
    registry.clear_tools()

    assert registry.get_tool_count() == 0

    registry.register_tool(mock_tool)

    assert registry.get_tool_count() == 1

    mock_tool_2 = Mock()
    mock_tool_2.name = "test_tool_2"
    registry.register_tool(mock_tool_2)

    assert registry.get_tool_count() == 2


def test_default_tools_registered():
    """Test default RAG tools are registered on initialization."""
    registry = ToolRegistry()

    # Should have vector_search and retrieve_context
    assert registry.has_tool("vector_search")
    assert registry.has_tool("retrieve_context")

    # Should be able to get them
    vector_search = registry.get_tool("vector_search")
    retrieve_context = registry.get_tool("retrieve_context")

    assert vector_search is not None
    assert retrieve_context is not None


def test_default_tools_have_definitions():
    """Test default tools have valid definitions."""
    registry = ToolRegistry()

    definitions = registry.get_tool_definitions()

    assert len(definitions) >= 2

    # Check vector_search definition
    vector_search_def = next((d for d in definitions if d["name"] == "vector_search"), None)
    assert vector_search_def is not None
    assert "parameters" in vector_search_def

    # Check retrieve_context definition
    retrieve_context_def = next((d for d in definitions if d["name"] == "retrieve_context"), None)
    assert retrieve_context_def is not None
    assert "parameters" in retrieve_context_def


def test_registry_is_independent():
    """Test multiple registry instances are independent."""
    registry1 = ToolRegistry()
    registry2 = ToolRegistry()

    registry1.clear_tools()

    # registry2 should still have default tools
    assert registry2.get_tool_count() >= 2


def test_get_all_tools_returns_copy():
    """Test get_all_tools returns a list (not direct reference)."""
    registry = ToolRegistry()

    tools1 = registry.get_all_tools()
    tools2 = registry.get_all_tools()

    # Should be different list objects
    assert tools1 is not tools2
    # But contain same tools
    assert len(tools1) == len(tools2)
