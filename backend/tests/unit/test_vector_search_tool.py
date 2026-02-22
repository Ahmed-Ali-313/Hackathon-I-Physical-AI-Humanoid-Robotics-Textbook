"""
Tests for vector search tool.

Tests vector search tool execution and integration with services.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.tools.vector_search_tool import VectorSearchTool


@pytest.fixture
def mock_services():
    """Mock vector and embedding services."""
    with patch('src.tools.vector_search_tool.vector_service') as mock_vector:
        with patch('src.tools.vector_search_tool.embedding_service') as mock_embedding:
            yield mock_vector, mock_embedding


@pytest.mark.asyncio
async def test_vector_search_tool_initialization():
    """Test vector search tool initializes correctly."""
    tool = VectorSearchTool()

    assert tool.name == "vector_search"
    assert tool.description is not None
    assert "textbook" in tool.description.lower()


@pytest.mark.asyncio
async def test_execute_success(mock_services):
    """Test successful vector search execution."""
    mock_vector, mock_embedding = mock_services

    # Mock embedding generation
    mock_embedding_vector = [0.1] * 768
    mock_embedding.generate_embedding = AsyncMock(return_value=mock_embedding_vector)

    # Mock search results
    mock_results = [
        {
            "id": "test-1",
            "content": "VSLAM is Visual SLAM",
            "confidence": 0.85,
            "metadata": {
                "chapter": "isaac-sim",
                "url": "/docs/isaac-sim",
            }
        }
    ]
    mock_vector.search = AsyncMock(return_value=mock_results)

    tool = VectorSearchTool()
    results = await tool.execute(query="What is VSLAM?")

    assert len(results) == 1
    assert results[0]["content"] == "VSLAM is Visual SLAM"
    assert results[0]["confidence"] == 0.85

    # Verify services were called correctly
    mock_embedding.generate_embedding.assert_called_once_with("What is VSLAM?")
    mock_vector.search.assert_called_once()


@pytest.mark.asyncio
async def test_execute_empty_query(mock_services):
    """Test execute raises error for empty query."""
    tool = VectorSearchTool()

    with pytest.raises(ValueError, match="Query cannot be empty"):
        await tool.execute(query="")

    with pytest.raises(ValueError, match="Query cannot be empty"):
        await tool.execute(query="   ")


@pytest.mark.asyncio
async def test_execute_with_custom_parameters(mock_services):
    """Test execute with custom top_k and confidence_threshold."""
    mock_vector, mock_embedding = mock_services

    mock_embedding.generate_embedding = AsyncMock(return_value=[0.1] * 768)
    mock_vector.search = AsyncMock(return_value=[])

    tool = VectorSearchTool()
    await tool.execute(
        query="What is VSLAM?",
        top_k=10,
        confidence_threshold=0.8,
    )

    # Verify search was called with custom parameters
    call_args = mock_vector.search.call_args
    assert call_args.kwargs["top_k"] == 10
    assert call_args.kwargs["confidence_threshold"] == 0.8


@pytest.mark.asyncio
async def test_execute_embedding_failure(mock_services):
    """Test execute handles embedding generation failure."""
    mock_vector, mock_embedding = mock_services

    mock_embedding.generate_embedding = AsyncMock(side_effect=Exception("Embedding failed"))

    tool = VectorSearchTool()

    with pytest.raises(Exception, match="Vector search failed"):
        await tool.execute(query="What is VSLAM?")


@pytest.mark.asyncio
async def test_execute_search_failure(mock_services):
    """Test execute handles search failure."""
    mock_vector, mock_embedding = mock_services

    mock_embedding.generate_embedding = AsyncMock(return_value=[0.1] * 768)
    mock_vector.search = AsyncMock(side_effect=Exception("Search failed"))

    tool = VectorSearchTool()

    with pytest.raises(Exception, match="Vector search failed"):
        await tool.execute(query="What is VSLAM?")


@pytest.mark.asyncio
async def test_execute_returns_multiple_results(mock_services):
    """Test execute returns multiple search results."""
    mock_vector, mock_embedding = mock_services

    mock_embedding.generate_embedding = AsyncMock(return_value=[0.1] * 768)

    mock_results = [
        {"id": "1", "content": "Result 1", "confidence": 0.9, "metadata": {}},
        {"id": "2", "content": "Result 2", "confidence": 0.85, "metadata": {}},
        {"id": "3", "content": "Result 3", "confidence": 0.8, "metadata": {}},
    ]
    mock_vector.search = AsyncMock(return_value=mock_results)

    tool = VectorSearchTool()
    results = await tool.execute(query="What is VSLAM?")

    assert len(results) == 3
    assert results[0]["confidence"] == 0.9
    assert results[1]["confidence"] == 0.85
    assert results[2]["confidence"] == 0.8


@pytest.mark.asyncio
async def test_execute_no_results(mock_services):
    """Test execute handles no search results."""
    mock_vector, mock_embedding = mock_services

    mock_embedding.generate_embedding = AsyncMock(return_value=[0.1] * 768)
    mock_vector.search = AsyncMock(return_value=[])

    tool = VectorSearchTool()
    results = await tool.execute(query="What is quantum robotics?")

    assert len(results) == 0


def test_get_tool_definition():
    """Test get_tool_definition returns correct structure."""
    tool = VectorSearchTool()
    definition = tool.get_tool_definition()

    assert definition["name"] == "vector_search"
    assert definition["description"] is not None
    assert "parameters" in definition
    assert definition["parameters"]["type"] == "object"
    assert "query" in definition["parameters"]["properties"]
    assert "top_k" in definition["parameters"]["properties"]
    assert "confidence_threshold" in definition["parameters"]["properties"]
    assert "query" in definition["parameters"]["required"]


def test_get_tool_definition_parameter_types():
    """Test tool definition has correct parameter types."""
    tool = VectorSearchTool()
    definition = tool.get_tool_definition()

    props = definition["parameters"]["properties"]

    assert props["query"]["type"] == "string"
    assert props["top_k"]["type"] == "integer"
    assert props["confidence_threshold"]["type"] == "number"


def test_get_tool_definition_default_values():
    """Test tool definition includes default values."""
    tool = VectorSearchTool()
    definition = tool.get_tool_definition()

    props = definition["parameters"]["properties"]

    assert props["top_k"]["default"] == 5
    assert props["confidence_threshold"]["default"] == 0.7


@pytest.mark.asyncio
async def test_execute_preserves_metadata(mock_services):
    """Test execute preserves all metadata from search results."""
    mock_vector, mock_embedding = mock_services

    mock_embedding.generate_embedding = AsyncMock(return_value=[0.1] * 768)

    mock_results = [
        {
            "id": "test-1",
            "content": "Test content",
            "confidence": 0.85,
            "metadata": {
                "chapter": "isaac-sim",
                "module": "module-3-isaac",
                "section": "chunk-0",
                "url": "/docs/module-3-isaac/isaac-sim",
                "chunk_index": 0,
                "total_chunks": 5,
            }
        }
    ]
    mock_vector.search = AsyncMock(return_value=mock_results)

    tool = VectorSearchTool()
    results = await tool.execute(query="What is VSLAM?")

    assert results[0]["metadata"]["chapter"] == "isaac-sim"
    assert results[0]["metadata"]["module"] == "module-3-isaac"
    assert results[0]["metadata"]["url"] == "/docs/module-3-isaac/isaac-sim"
    assert results[0]["metadata"]["chunk_index"] == 0
