"""
Tests for retrieve context tool.

Tests context formatting and source attribution.
"""

import pytest
from src.tools.retrieve_context_tool import RetrieveContextTool


@pytest.mark.asyncio
async def test_retrieve_context_tool_initialization():
    """Test retrieve context tool initializes correctly."""
    tool = RetrieveContextTool()

    assert tool.name == "retrieve_context"
    assert tool.description is not None
    assert "format" in tool.description.lower()


@pytest.mark.asyncio
async def test_execute_success():
    """Test successful context retrieval and formatting."""
    tool = RetrieveContextTool()

    search_results = [
        {
            "content": "VSLAM is Visual SLAM",
            "confidence": 0.85,
            "metadata": {
                "chapter": "isaac-sim",
                "module": "module-3-isaac",
                "section": "chunk-0",
                "url": "/docs/module-3-isaac/isaac-sim",
            }
        },
        {
            "content": "SLAM stands for Simultaneous Localization and Mapping",
            "confidence": 0.80,
            "metadata": {
                "chapter": "vslam",
                "module": "module-2",
                "section": "chunk-1",
                "url": "/docs/module-2/vslam",
            }
        }
    ]

    result = await tool.execute(search_results)

    assert result["has_context"] is True
    assert result["num_sources"] == 2
    assert len(result["sources"]) == 2
    assert "[Source 1]" in result["context"]
    assert "[Source 2]" in result["context"]
    assert "VSLAM is Visual SLAM" in result["context"]


@pytest.mark.asyncio
async def test_execute_empty_results():
    """Test execute with empty search results."""
    tool = RetrieveContextTool()

    result = await tool.execute([])

    assert result["has_context"] is False
    assert result["context"] == ""
    assert result["sources"] == []


@pytest.mark.asyncio
async def test_execute_invalid_type():
    """Test execute raises error for invalid search_results type."""
    tool = RetrieveContextTool()

    with pytest.raises(ValueError, match="search_results must be a list"):
        await tool.execute("not a list")


@pytest.mark.asyncio
async def test_execute_formats_sources_correctly():
    """Test execute formats sources with all metadata."""
    tool = RetrieveContextTool()

    search_results = [
        {
            "content": "Test content",
            "confidence": 0.85,
            "metadata": {
                "chapter": "isaac-sim",
                "module": "module-3-isaac",
                "section": "chunk-0",
                "url": "/docs/module-3-isaac/isaac-sim",
            }
        }
    ]

    result = await tool.execute(search_results)

    source = result["sources"][0]
    assert source["index"] == 1
    assert source["chapter"] == "isaac-sim"
    assert source["module"] == "module-3-isaac"
    assert source["section"] == "chunk-0"
    assert source["url"] == "/docs/module-3-isaac/isaac-sim"
    assert source["confidence"] == 0.85


@pytest.mark.asyncio
async def test_execute_handles_missing_metadata():
    """Test execute handles missing metadata gracefully."""
    tool = RetrieveContextTool()

    search_results = [
        {
            "content": "Test content",
            "confidence": 0.85,
            "metadata": {},
        }
    ]

    result = await tool.execute(search_results)

    assert result["has_context"] is True
    source = result["sources"][0]
    assert source["chapter"] == "unknown"
    assert source["module"] == "unknown"
    assert source["section"] == "unknown"
    assert source["url"] == ""


@pytest.mark.asyncio
async def test_execute_skips_invalid_results():
    """Test execute skips invalid result items."""
    tool = RetrieveContextTool()

    search_results = [
        {
            "content": "Valid content",
            "confidence": 0.85,
            "metadata": {"chapter": "test", "url": "/test"},
        },
        "invalid item",  # Should be skipped
        {
            "content": "",  # Empty content, should be skipped
            "confidence": 0.80,
            "metadata": {},
        },
        {
            "content": "Another valid content",
            "confidence": 0.75,
            "metadata": {"chapter": "test2", "url": "/test2"},
        }
    ]

    result = await tool.execute(search_results)

    assert result["num_sources"] == 2
    assert "Valid content" in result["context"]
    assert "Another valid content" in result["context"]


@pytest.mark.asyncio
async def test_execute_combines_context_with_newlines():
    """Test execute combines context parts with double newlines."""
    tool = RetrieveContextTool()

    search_results = [
        {"content": "Content 1", "confidence": 0.9, "metadata": {}},
        {"content": "Content 2", "confidence": 0.8, "metadata": {}},
    ]

    result = await tool.execute(search_results)

    assert "\n\n" in result["context"]
    assert result["context"].count("\n\n") == 1  # One separator between two items


@pytest.mark.asyncio
async def test_execute_indexes_sources_sequentially():
    """Test execute indexes sources starting from 1."""
    tool = RetrieveContextTool()

    search_results = [
        {"content": "Content 1", "confidence": 0.9, "metadata": {}},
        {"content": "Content 2", "confidence": 0.8, "metadata": {}},
        {"content": "Content 3", "confidence": 0.7, "metadata": {}},
    ]

    result = await tool.execute(search_results)

    assert result["sources"][0]["index"] == 1
    assert result["sources"][1]["index"] == 2
    assert result["sources"][2]["index"] == 3


def test_format_sources_for_response():
    """Test formatting sources for chat response."""
    tool = RetrieveContextTool()

    sources = [
        {
            "index": 1,
            "chapter": "isaac-sim",
            "module": "module-3-isaac",
            "section": "chunk-0",
            "url": "/docs/module-3-isaac/isaac-sim",
            "confidence": 0.85,
        },
        {
            "index": 2,
            "chapter": "vslam",
            "module": "module-2",
            "section": "chunk-1",
            "url": "/docs/module-2/vslam",
            "confidence": 0.80,
        }
    ]

    formatted = tool.format_sources_for_response(sources)

    assert len(formatted) == 2
    assert formatted[0]["chapter"] == "isaac-sim"
    assert formatted[0]["section"] == "chunk-0"
    assert formatted[0]["url"] == "/docs/module-3-isaac/isaac-sim"
    assert "index" not in formatted[0]  # Should not include index
    assert "confidence" not in formatted[0]  # Should not include confidence


def test_format_sources_for_response_handles_missing_fields():
    """Test format_sources_for_response handles missing fields."""
    tool = RetrieveContextTool()

    sources = [
        {
            "index": 1,
            "confidence": 0.85,
        }
    ]

    formatted = tool.format_sources_for_response(sources)

    assert len(formatted) == 1
    assert formatted[0]["chapter"] == "unknown"
    assert formatted[0]["section"] == "unknown"
    assert formatted[0]["url"] == ""


def test_format_sources_for_response_empty_list():
    """Test format_sources_for_response with empty list."""
    tool = RetrieveContextTool()

    formatted = tool.format_sources_for_response([])

    assert formatted == []


def test_get_tool_definition():
    """Test get_tool_definition returns correct structure."""
    tool = RetrieveContextTool()
    definition = tool.get_tool_definition()

    assert definition["name"] == "retrieve_context"
    assert definition["description"] is not None
    assert "parameters" in definition
    assert definition["parameters"]["type"] == "object"
    assert "search_results" in definition["parameters"]["properties"]
    assert "search_results" in definition["parameters"]["required"]


def test_get_tool_definition_parameter_structure():
    """Test tool definition has correct parameter structure."""
    tool = RetrieveContextTool()
    definition = tool.get_tool_definition()

    props = definition["parameters"]["properties"]

    assert props["search_results"]["type"] == "array"
    assert "items" in props["search_results"]
    assert props["search_results"]["items"]["type"] == "object"


@pytest.mark.asyncio
async def test_execute_preserves_confidence_scores():
    """Test execute preserves confidence scores in sources."""
    tool = RetrieveContextTool()

    search_results = [
        {"content": "Content 1", "confidence": 0.95, "metadata": {}},
        {"content": "Content 2", "confidence": 0.72, "metadata": {}},
    ]

    result = await tool.execute(search_results)

    assert result["sources"][0]["confidence"] == 0.95
    assert result["sources"][1]["confidence"] == 0.72


@pytest.mark.asyncio
async def test_execute_handles_missing_confidence():
    """Test execute handles missing confidence score."""
    tool = RetrieveContextTool()

    search_results = [
        {"content": "Content 1", "metadata": {}},
    ]

    result = await tool.execute(search_results)

    assert result["sources"][0]["confidence"] == 0.0
