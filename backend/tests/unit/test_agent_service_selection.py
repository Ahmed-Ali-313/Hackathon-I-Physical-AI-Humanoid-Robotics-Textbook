"""
Tests for agent service selection mode.

Tests agent behavior when selected text is provided (skips vector search).
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.services.agent_service import AgentService


@pytest.fixture
def mock_config():
    """Mock configuration."""
    with patch('src.services.agent_service.settings') as mock_settings:
        # OpenAI-only configuration
        mock_settings.openai_api_key = "test-openai-key"
        
        yield mock_settings


@pytest.fixture
def mock_tools():
    """Mock agent tools."""
    mock_vector_search = Mock()
    mock_vector_search.name = "vector_search"
    mock_vector_search.execute = AsyncMock()

    mock_retrieve_context = Mock()
    mock_retrieve_context.name = "retrieve_context"
    mock_retrieve_context.execute = AsyncMock(return_value={
        "context": "[Source 1] Selected text content",
        "sources": [{"index": 1, "chapter": "selected", "url": "/test", "confidence": 1.0}],
        "has_context": True,
    })
    mock_retrieve_context.format_sources_for_response = Mock(return_value=[
        {"chapter": "selected", "section": "selected", "url": "/test"}
    ])

    return mock_vector_search, mock_retrieve_context


@pytest.mark.asyncio
async def test_selection_mode_skips_vector_search(mock_config, mock_tools):
    """Test that selection mode skips vector search tool."""
    mock_vector_search, mock_retrieve_context = mock_tools

    service = AgentService()
    service.register_tools([mock_vector_search, mock_retrieve_context])

    await service.generate_response(
        question="Explain this",
        selected_text="VSLAM is a technique for simultaneous localization and mapping.",
    )

    # Vector search should NOT be called
    mock_vector_search.execute.assert_not_called()


@pytest.mark.asyncio
async def test_selection_mode_uses_selected_text_as_context(mock_config, mock_tools):
    """Test that selection mode uses selected text directly as context."""
    mock_vector_search, mock_retrieve_context = mock_tools

    service = AgentService()
    service.register_tools([mock_vector_search, mock_retrieve_context])

    selected_text = "VSLAM is a technique for simultaneous localization and mapping."

    response = await service.generate_response(
        question="Explain this in simpler terms",
        selected_text=selected_text,
    )

    # Retrieve context should be called with selected text
    mock_retrieve_context.execute.assert_called_once()
    call_args = mock_retrieve_context.execute.call_args[0][0]
    assert call_args[0]["content"] == selected_text


@pytest.mark.asyncio
async def test_selection_mode_confidence_is_1_0(mock_config, mock_tools):
    """Test that selection mode returns confidence score of 1.0."""
    mock_vector_search, mock_retrieve_context = mock_tools

    service = AgentService()
    service.register_tools([mock_vector_search, mock_retrieve_context])

    response = await service.generate_response(
        question="Explain this",
        selected_text="Test content",
    )

    assert response["confidence_score"] == 1.0


@pytest.mark.asyncio
async def test_selection_mode_with_metadata(mock_config, mock_tools):
    """Test selection mode with metadata (chapter, url)."""
    mock_vector_search, mock_retrieve_context = mock_tools

    service = AgentService()
    service.register_tools([mock_vector_search, mock_retrieve_context])

    metadata = {
        "chapter": "isaac-sim",
        "module": "module-3-isaac",
        "url": "/docs/module-3-isaac/isaac-sim",
    }

    response = await service.generate_response(
        question="Explain this",
        selected_text="Test content",
        selected_text_metadata=metadata,
    )

    # Metadata should be included in source references
    call_args = mock_retrieve_context.execute.call_args[0][0]
    assert call_args[0]["metadata"]["chapter"] == "isaac-sim"
    assert call_args[0]["metadata"]["url"] == "/docs/module-3-isaac/isaac-sim"


@pytest.mark.asyncio
async def test_selection_mode_without_metadata(mock_config, mock_tools):
    """Test selection mode without metadata uses defaults."""
    mock_vector_search, mock_retrieve_context = mock_tools

    service = AgentService()
    service.register_tools([mock_vector_search, mock_retrieve_context])

    response = await service.generate_response(
        question="Explain this",
        selected_text="Test content",
    )

    # Should use default metadata
    call_args = mock_retrieve_context.execute.call_args[0][0]
    assert call_args[0]["metadata"]["chapter"] == "selected"


@pytest.mark.asyncio
async def test_selection_mode_empty_selected_text_falls_back_to_rag(mock_config, mock_tools):
    """Test that empty selected text falls back to normal RAG mode."""
    mock_vector_search, mock_retrieve_context = mock_tools

    mock_vector_search.execute = AsyncMock(return_value=[])
    mock_retrieve_context.execute = AsyncMock(return_value={
        "context": "",
        "sources": [],
        "has_context": False,
    })

    service = AgentService()
    service.register_tools([mock_vector_search, mock_retrieve_context])

    response = await service.generate_response(
        question="What is VSLAM?",
        selected_text="",  # Empty
    )

    # Should fall back to vector search
    mock_vector_search.execute.assert_called_once()


@pytest.mark.asyncio
async def test_selection_mode_whitespace_only_falls_back_to_rag(mock_config, mock_tools):
    """Test that whitespace-only selected text falls back to RAG."""
    mock_vector_search, mock_retrieve_context = mock_tools

    mock_vector_search.execute = AsyncMock(return_value=[])
    mock_retrieve_context.execute = AsyncMock(return_value={
        "context": "",
        "sources": [],
        "has_context": False,
    })

    service = AgentService()
    service.register_tools([mock_vector_search, mock_retrieve_context])

    response = await service.generate_response(
        question="What is VSLAM?",
        selected_text="   ",  # Whitespace only
    )

    # Should fall back to vector search
    mock_vector_search.execute.assert_called_once()


@pytest.mark.asyncio
async def test_selection_mode_returns_source_references(mock_config, mock_tools):
    """Test that selection mode returns source references."""
    mock_vector_search, mock_retrieve_context = mock_tools

    service = AgentService()
    service.register_tools([mock_vector_search, mock_retrieve_context])

    response = await service.generate_response(
        question="Explain this",
        selected_text="Test content",
        selected_text_metadata={"chapter": "test", "url": "/test"},
    )

    assert "source_references" in response
    assert len(response["source_references"]) > 0
    assert response["source_references"][0]["chapter"] == "selected"
