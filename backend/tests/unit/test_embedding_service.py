"""
Tests for embedding service.

Tests embedding generation with OpenAI provider.
"""

import pytest
from unittest.mock import Mock, patch
from src.services.embedding_service import EmbeddingService


@pytest.fixture
def mock_openai_config():
    """Mock OpenAI configuration."""
    with patch('src.services.embedding_service.settings') as mock_settings:
        mock_settings.openai_api_key = "test-openai-key"
        yield mock_settings


@pytest.mark.asyncio
async def test_embedding_service_initialization_openai(mock_openai_config):
    """Test embedding service initializes with OpenAI."""
    with patch('src.services.embedding_service.OpenAI') as mock_openai:
        service = EmbeddingService()

        mock_openai.assert_called_once_with(api_key="test-openai-key")
        assert service.model == "text-embedding-3-small"


@pytest.mark.asyncio
async def test_embedding_service_missing_openai_key():
    """Test embedding service raises error when OpenAI key is missing."""
    with patch('src.services.embedding_service.settings') as mock_settings:
        mock_settings.openai_api_key = ""

        with pytest.raises(ValueError, match="OPENAI_API_KEY not configured"):
            EmbeddingService()


@pytest.mark.asyncio
async def test_generate_embedding_openai(mock_openai_config):
    """Test embedding generation with OpenAI."""
    mock_embedding = [0.2] * 768

    with patch('src.services.embedding_service.OpenAI') as mock_openai_class:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=mock_embedding)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        service = EmbeddingService()
        result = await service.generate_embedding("test text")

        assert result == mock_embedding
        assert len(result) == 768
        mock_client.embeddings.create.assert_called_once_with(
            model="text-embedding-3-small",
            input="test text",
            dimensions=768,
        )


@pytest.mark.asyncio
async def test_generate_embedding_empty_text(mock_openai_config):
    """Test embedding generation raises error for empty text."""
    with patch('src.services.embedding_service.OpenAI'):
        service = EmbeddingService()

        with pytest.raises(ValueError, match="Text cannot be empty"):
            await service.generate_embedding("")

        with pytest.raises(ValueError, match="Text cannot be empty"):
            await service.generate_embedding("   ")


@pytest.mark.asyncio
async def test_generate_embedding_openai_api_error(mock_openai_config):
    """Test embedding generation handles OpenAI API errors."""
    with patch('src.services.embedding_service.OpenAI') as mock_openai_class:
        mock_client = Mock()
        mock_client.embeddings.create.side_effect = Exception("API error")
        mock_openai_class.return_value = mock_client

        service = EmbeddingService()

        with pytest.raises(Exception, match="OpenAI embedding generation failed"):
            await service.generate_embedding("test text")


@pytest.mark.asyncio
async def test_generate_embeddings_batch(mock_openai_config):
    """Test batch embedding generation."""
    mock_embedding_1 = [0.1] * 768
    mock_embedding_2 = [0.2] * 768

    with patch('src.services.embedding_service.OpenAI') as mock_openai_class:
        mock_client = Mock()
        mock_response_1 = Mock()
        mock_response_1.data = [Mock(embedding=mock_embedding_1)]
        mock_response_2 = Mock()
        mock_response_2.data = [Mock(embedding=mock_embedding_2)]
        mock_client.embeddings.create.side_effect = [mock_response_1, mock_response_2]
        mock_openai_class.return_value = mock_client

        service = EmbeddingService()
        results = await service.generate_embeddings_batch(["text 1", "text 2"])

        assert len(results) == 2
        assert results[0] == mock_embedding_1
        assert results[1] == mock_embedding_2
        assert mock_client.embeddings.create.call_count == 2


@pytest.mark.asyncio
async def test_generate_embeddings_batch_empty_list(mock_openai_config):
    """Test batch embedding generation raises error for empty list."""
    with patch('src.services.embedding_service.OpenAI'):
        service = EmbeddingService()

        with pytest.raises(ValueError, match="Texts list cannot be empty"):
            await service.generate_embeddings_batch([])


@pytest.mark.asyncio
async def test_get_embedding_dimension(mock_openai_config):
    """Test embedding dimension is 768 for OpenAI."""
    with patch('src.services.embedding_service.OpenAI'):
        service = EmbeddingService()
        assert service.get_embedding_dimension() == 768
