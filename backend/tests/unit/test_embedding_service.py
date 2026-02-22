"""
Tests for embedding service.

Tests embedding generation with both Gemini and OpenAI providers.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.services.embedding_service import EmbeddingService


@pytest.fixture
def mock_gemini_config():
    """Mock Gemini configuration."""
    with patch('src.services.embedding_service.settings') as mock_settings:
        mock_settings.llm_provider = "gemini"
        mock_settings.gemini_api_key = "test-gemini-key"
        mock_settings.openai_api_key = ""
        yield mock_settings


@pytest.fixture
def mock_openai_config():
    """Mock OpenAI configuration."""
    with patch('src.services.embedding_service.settings') as mock_settings:
        mock_settings.llm_provider = "openai"
        mock_settings.gemini_api_key = ""
        mock_settings.openai_api_key = "test-openai-key"
        yield mock_settings


@pytest.mark.asyncio
async def test_embedding_service_initialization_gemini(mock_gemini_config):
    """Test embedding service initializes with Gemini provider."""
    with patch('src.services.embedding_service.genai.configure') as mock_configure:
        service = EmbeddingService(provider="gemini")

        assert service.provider == "gemini"
        mock_configure.assert_called_once_with(api_key="test-gemini-key")


@pytest.mark.asyncio
async def test_embedding_service_initialization_openai(mock_openai_config):
    """Test embedding service initializes with OpenAI provider."""
    with patch('src.services.embedding_service.OpenAI') as mock_openai:
        service = EmbeddingService(provider="openai")

        assert service.provider == "openai"
        mock_openai.assert_called_once_with(api_key="test-openai-key")


@pytest.mark.asyncio
async def test_embedding_service_invalid_provider():
    """Test embedding service raises error for invalid provider."""
    with pytest.raises(ValueError, match="Invalid provider"):
        EmbeddingService(provider="invalid")


@pytest.mark.asyncio
async def test_embedding_service_missing_gemini_key():
    """Test embedding service raises error when Gemini key is missing."""
    with patch('src.services.embedding_service.settings') as mock_settings:
        mock_settings.llm_provider = "gemini"
        mock_settings.gemini_api_key = ""

        with pytest.raises(ValueError, match="GEMINI_API_KEY not configured"):
            EmbeddingService(provider="gemini")


@pytest.mark.asyncio
async def test_embedding_service_missing_openai_key():
    """Test embedding service raises error when OpenAI key is missing."""
    with patch('src.services.embedding_service.settings') as mock_settings:
        mock_settings.llm_provider = "openai"
        mock_settings.openai_api_key = ""

        with pytest.raises(ValueError, match="OPENAI_API_KEY not configured"):
            EmbeddingService(provider="openai")


@pytest.mark.asyncio
async def test_generate_embedding_gemini(mock_gemini_config):
    """Test embedding generation with Gemini provider."""
    mock_embedding = [0.1] * 768

    with patch('src.services.embedding_service.genai.configure'):
        with patch('src.services.embedding_service.genai.embed_content') as mock_embed:
            mock_embed.return_value = {'embedding': mock_embedding}

            service = EmbeddingService(provider="gemini")
            result = await service.generate_embedding("test text")

            assert result == mock_embedding
            assert len(result) == 768
            mock_embed.assert_called_once_with(
                model="models/text-embedding-004",
                content="test text",
                task_type="retrieval_document",
            )


@pytest.mark.asyncio
async def test_generate_embedding_openai(mock_openai_config):
    """Test embedding generation with OpenAI provider."""
    mock_embedding = [0.2] * 768

    with patch('src.services.embedding_service.OpenAI') as mock_openai_class:
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=mock_embedding)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        service = EmbeddingService(provider="openai")
        result = await service.generate_embedding("test text")

        assert result == mock_embedding
        assert len(result) == 768
        mock_client.embeddings.create.assert_called_once_with(
            model="text-embedding-3-small",
            input="test text",
            dimensions=768,
        )


@pytest.mark.asyncio
async def test_generate_embedding_empty_text(mock_gemini_config):
    """Test embedding generation raises error for empty text."""
    with patch('src.services.embedding_service.genai.configure'):
        service = EmbeddingService(provider="gemini")

        with pytest.raises(ValueError, match="Text cannot be empty"):
            await service.generate_embedding("")

        with pytest.raises(ValueError, match="Text cannot be empty"):
            await service.generate_embedding("   ")


@pytest.mark.asyncio
async def test_generate_embedding_gemini_api_error(mock_gemini_config):
    """Test embedding generation handles Gemini API errors."""
    with patch('src.services.embedding_service.genai.configure'):
        with patch('src.services.embedding_service.genai.embed_content') as mock_embed:
            mock_embed.side_effect = Exception("API error")

            service = EmbeddingService(provider="gemini")

            with pytest.raises(Exception, match="Gemini embedding generation failed"):
                await service.generate_embedding("test text")


@pytest.mark.asyncio
async def test_generate_embedding_openai_api_error(mock_openai_config):
    """Test embedding generation handles OpenAI API errors."""
    with patch('src.services.embedding_service.OpenAI') as mock_openai_class:
        mock_client = Mock()
        mock_client.embeddings.create.side_effect = Exception("API error")
        mock_openai_class.return_value = mock_client

        service = EmbeddingService(provider="openai")

        with pytest.raises(Exception, match="OpenAI embedding generation failed"):
            await service.generate_embedding("test text")


@pytest.mark.asyncio
async def test_generate_embeddings_batch(mock_gemini_config):
    """Test batch embedding generation."""
    mock_embedding_1 = [0.1] * 768
    mock_embedding_2 = [0.2] * 768

    with patch('src.services.embedding_service.genai.configure'):
        with patch('src.services.embedding_service.genai.embed_content') as mock_embed:
            mock_embed.side_effect = [
                {'embedding': mock_embedding_1},
                {'embedding': mock_embedding_2},
            ]

            service = EmbeddingService(provider="gemini")
            results = await service.generate_embeddings_batch(["text 1", "text 2"])

            assert len(results) == 2
            assert results[0] == mock_embedding_1
            assert results[1] == mock_embedding_2
            assert mock_embed.call_count == 2


@pytest.mark.asyncio
async def test_generate_embeddings_batch_empty_list(mock_gemini_config):
    """Test batch embedding generation raises error for empty list."""
    with patch('src.services.embedding_service.genai.configure'):
        service = EmbeddingService(provider="gemini")

        with pytest.raises(ValueError, match="Texts list cannot be empty"):
            await service.generate_embeddings_batch([])


@pytest.mark.asyncio
async def test_get_embedding_dimension(mock_gemini_config):
    """Test embedding dimension is 768 for both providers."""
    with patch('src.services.embedding_service.genai.configure'):
        service = EmbeddingService(provider="gemini")
        assert service.get_embedding_dimension() == 768

    with patch('src.services.embedding_service.settings') as mock_settings:
        mock_settings.llm_provider = "openai"
        mock_settings.openai_api_key = "test-key"

        with patch('src.services.embedding_service.OpenAI'):
            service = EmbeddingService(provider="openai")
            assert service.get_embedding_dimension() == 768
