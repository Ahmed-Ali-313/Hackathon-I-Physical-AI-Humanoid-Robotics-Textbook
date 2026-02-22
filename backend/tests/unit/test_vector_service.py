"""
Tests for vector service.

Tests Qdrant search operations with confidence threshold filtering.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.services.vector_service import VectorService


@pytest.fixture
def mock_qdrant_config():
    """Mock Qdrant configuration."""
    with patch('src.services.vector_service.settings') as mock_settings:
        mock_settings.qdrant_url = "https://test.qdrant.io"
        mock_settings.qdrant_api_key = "test-api-key"
        mock_settings.qdrant_collection_name = "test_collection"
        mock_settings.rag_confidence_threshold = 0.7
        mock_settings.rag_top_k_results = 5
        yield mock_settings


@pytest.fixture
def mock_qdrant_client():
    """Mock Qdrant client."""
    with patch('src.services.vector_service.QdrantClient') as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        yield mock_client


def test_vector_service_initialization(mock_qdrant_config, mock_qdrant_client):
    """Test vector service initializes with Qdrant client."""
    service = VectorService()

    assert service.collection_name == "test_collection"
    assert service.confidence_threshold == 0.7
    assert service.top_k == 5


def test_vector_service_missing_url():
    """Test vector service raises error when URL is missing."""
    with patch('src.services.vector_service.settings') as mock_settings:
        mock_settings.qdrant_url = ""
        mock_settings.qdrant_api_key = "test-key"

        with pytest.raises(ValueError, match="QDRANT_URL not configured"):
            VectorService()


def test_vector_service_missing_api_key():
    """Test vector service raises error when API key is missing."""
    with patch('src.services.vector_service.settings') as mock_settings:
        mock_settings.qdrant_url = "https://test.qdrant.io"
        mock_settings.qdrant_api_key = ""

        with pytest.raises(ValueError, match="QDRANT_API_KEY not configured"):
            VectorService()


@pytest.mark.asyncio
async def test_search_success(mock_qdrant_config, mock_qdrant_client):
    """Test successful vector search."""
    # Mock search results
    mock_point = Mock()
    mock_point.id = "test-id-1"
    mock_point.score = 0.85
    mock_point.payload = {
        "content": "Test content about VSLAM",
        "chapter": "isaac-sim",
        "module": "module-3-isaac",
        "section": "chunk-0",
        "url": "/docs/module-3-isaac/isaac-sim",
        "chunk_index": 0,
        "total_chunks": 5,
    }

    mock_qdrant_client.search.return_value = [mock_point]

    service = VectorService()
    query_vector = [0.1] * 768

    results = await service.search(query_vector=query_vector)

    assert len(results) == 1
    assert results[0]["id"] == "test-id-1"
    assert results[0]["content"] == "Test content about VSLAM"
    assert results[0]["confidence"] == 0.85
    assert results[0]["metadata"]["chapter"] == "isaac-sim"
    assert results[0]["metadata"]["url"] == "/docs/module-3-isaac/isaac-sim"

    # Verify search was called with correct parameters
    mock_qdrant_client.search.assert_called_once()
    call_args = mock_qdrant_client.search.call_args
    assert call_args.kwargs["collection_name"] == "test_collection"
    assert call_args.kwargs["query_vector"] == query_vector
    assert call_args.kwargs["limit"] == 5
    assert call_args.kwargs["score_threshold"] == 0.7


@pytest.mark.asyncio
async def test_search_with_custom_parameters(mock_qdrant_config, mock_qdrant_client):
    """Test search with custom top_k and confidence threshold."""
    mock_qdrant_client.search.return_value = []

    service = VectorService()
    query_vector = [0.1] * 768

    await service.search(
        query_vector=query_vector,
        top_k=10,
        confidence_threshold=0.8,
    )

    call_args = mock_qdrant_client.search.call_args
    assert call_args.kwargs["limit"] == 10
    assert call_args.kwargs["score_threshold"] == 0.8


@pytest.mark.asyncio
async def test_search_with_filters(mock_qdrant_config, mock_qdrant_client):
    """Test search with metadata filters."""
    mock_qdrant_client.search.return_value = []

    service = VectorService()
    query_vector = [0.1] * 768

    await service.search(
        query_vector=query_vector,
        filters={"chapter": "isaac-sim", "module": "module-3-isaac"},
    )

    call_args = mock_qdrant_client.search.call_args
    assert call_args.kwargs["query_filter"] is not None


@pytest.mark.asyncio
async def test_search_empty_vector(mock_qdrant_config, mock_qdrant_client):
    """Test search raises error for empty vector."""
    service = VectorService()

    with pytest.raises(ValueError, match="Query vector cannot be empty"):
        await service.search(query_vector=[])


@pytest.mark.asyncio
async def test_search_invalid_vector_dimension(mock_qdrant_config, mock_qdrant_client):
    """Test search raises error for invalid vector dimension."""
    service = VectorService()
    query_vector = [0.1] * 512  # Wrong dimension

    with pytest.raises(ValueError, match="Query vector must be 768-dimensional"):
        await service.search(query_vector=query_vector)


@pytest.mark.asyncio
async def test_search_qdrant_error(mock_qdrant_config, mock_qdrant_client):
    """Test search handles Qdrant errors."""
    mock_qdrant_client.search.side_effect = Exception("Connection error")

    service = VectorService()
    query_vector = [0.1] * 768

    with pytest.raises(Exception, match="Qdrant search failed"):
        await service.search(query_vector=query_vector)


@pytest.mark.asyncio
async def test_search_filters_results_by_threshold(mock_qdrant_config, mock_qdrant_client):
    """Test search filters results by confidence threshold."""
    # Mock results with varying scores
    mock_point_1 = Mock()
    mock_point_1.id = "high-score"
    mock_point_1.score = 0.85
    mock_point_1.payload = {"content": "High confidence", "chapter": "test", "module": "test", "section": "test", "url": "/test"}

    mock_point_2 = Mock()
    mock_point_2.id = "low-score"
    mock_point_2.score = 0.65
    mock_point_2.payload = {"content": "Low confidence", "chapter": "test", "module": "test", "section": "test", "url": "/test"}

    # Qdrant already filters by score_threshold, so only high-score should be returned
    mock_qdrant_client.search.return_value = [mock_point_1]

    service = VectorService()
    query_vector = [0.1] * 768

    results = await service.search(query_vector=query_vector, confidence_threshold=0.7)

    assert len(results) == 1
    assert results[0]["id"] == "high-score"
    assert results[0]["confidence"] == 0.85


@pytest.mark.asyncio
async def test_search_by_text(mock_qdrant_config, mock_qdrant_client):
    """Test search by text with embedding."""
    mock_qdrant_client.search.return_value = []

    service = VectorService()
    query_vector = [0.1] * 768

    await service.search_by_text(
        query_text="What is VSLAM?",
        embedding_vector=query_vector,
    )

    mock_qdrant_client.search.assert_called_once()


@pytest.mark.asyncio
async def test_search_by_text_empty_query(mock_qdrant_config, mock_qdrant_client):
    """Test search by text raises error for empty query."""
    service = VectorService()
    query_vector = [0.1] * 768

    with pytest.raises(ValueError, match="Query text cannot be empty"):
        await service.search_by_text(query_text="", embedding_vector=query_vector)


@pytest.mark.asyncio
async def test_get_collection_info(mock_qdrant_config, mock_qdrant_client):
    """Test getting collection information."""
    mock_collection_info = Mock()
    mock_collection_info.config.params.vectors.size = 768
    mock_collection_info.config.params.vectors.distance.name = "COSINE"
    mock_collection_info.points_count = 1500

    mock_qdrant_client.get_collection.return_value = mock_collection_info

    service = VectorService()
    info = await service.get_collection_info()

    assert info["name"] == "test_collection"
    assert info["vector_size"] == 768
    assert info["distance_metric"] == "COSINE"
    assert info["points_count"] == 1500


@pytest.mark.asyncio
async def test_get_collection_info_error(mock_qdrant_config, mock_qdrant_client):
    """Test get collection info handles errors."""
    mock_qdrant_client.get_collection.side_effect = Exception("Collection not found")

    service = VectorService()

    with pytest.raises(Exception, match="Failed to get collection info"):
        await service.get_collection_info()


@pytest.mark.asyncio
async def test_health_check_success(mock_qdrant_config, mock_qdrant_client):
    """Test health check returns True when connection is healthy."""
    mock_collection_info = Mock()
    mock_collection_info.config.params.vectors.size = 768
    mock_collection_info.config.params.vectors.distance.name = "COSINE"
    mock_collection_info.points_count = 1500

    mock_qdrant_client.get_collection.return_value = mock_collection_info

    service = VectorService()
    is_healthy = await service.health_check()

    assert is_healthy is True


@pytest.mark.asyncio
async def test_health_check_failure(mock_qdrant_config, mock_qdrant_client):
    """Test health check returns False when connection fails."""
    mock_qdrant_client.get_collection.side_effect = Exception("Connection error")

    service = VectorService()
    is_healthy = await service.health_check()

    assert is_healthy is False


def test_validate_confidence_score(mock_qdrant_config, mock_qdrant_client):
    """Test confidence score validation."""
    service = VectorService()

    # Valid scores
    assert service.validate_confidence_score(0.0) is True
    assert service.validate_confidence_score(0.5) is True
    assert service.validate_confidence_score(0.7) is True
    assert service.validate_confidence_score(1.0) is True

    # Invalid scores
    assert service.validate_confidence_score(-0.1) is False
    assert service.validate_confidence_score(1.1) is False
    assert service.validate_confidence_score(2.0) is False
