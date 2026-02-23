"""
Tests for configuration module.

Tests environment variable loading and configuration validation.
"""

import pytest
import os
from unittest.mock import patch
from src.config import Settings


def test_default_config_values():
    """Test that default configuration values are set correctly."""
    settings = Settings()

    # RAG defaults
    assert settings.rag_confidence_threshold == 0.7
    assert settings.rag_top_k_results == 5
    assert settings.rag_chunk_size == 1000
    assert settings.rag_chunk_overlap == 100

    # Conversation defaults
    assert settings.max_conversations_per_user == 50
    assert settings.max_messages_per_conversation == 500
    assert settings.conversation_retention_months == 12
    assert settings.session_expiry_minutes == 30

    # Message limits
    assert settings.max_user_message_length == 500
    assert settings.max_ai_message_length == 2000

    # Qdrant defaults
    assert settings.qdrant_collection_name == "textbook_chunks"


def test_config_loads_from_environment():
    """Test that configuration loads from environment variables."""
    with patch.dict(os.environ, {
        "OPENAI_API_KEY": "test-openai-key",
        "QDRANT_URL": "https://test.qdrant.io",
        "QDRANT_API_KEY": "test-qdrant-key",
        "RAG_CONFIDENCE_THRESHOLD": "0.8",
        "RAG_TOP_K_RESULTS": "10",
    }):
        settings = Settings()

        assert settings.openai_api_key == "test-openai-key"
        assert settings.qdrant_url == "https://test.qdrant.io"
        assert settings.qdrant_api_key == "test-qdrant-key"
        assert settings.rag_confidence_threshold == 0.8
        assert settings.rag_top_k_results == 10


def test_config_case_insensitive():
    """Test that environment variables are case-insensitive."""
    with patch.dict(os.environ, {
        "openai_api_key": "test-key",
    }):
        settings = Settings()

        assert settings.openai_api_key == "test-key"


def test_cors_origins_list_property():
    """Test CORS origins parsing into list."""
    with patch.dict(os.environ, {
        "CORS_ORIGINS": "http://localhost:3000,http://localhost:3001,https://example.com",
    }):
        settings = Settings()

        origins = settings.cors_origins_list
        assert len(origins) == 3
        assert "http://localhost:3000" in origins
        assert "http://localhost:3001" in origins
        assert "https://example.com" in origins


def test_is_production_property():
    """Test production environment detection."""
    # Development
    with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
        settings = Settings()
        assert settings.is_production is False

    # Production
    with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
        settings = Settings()
        assert settings.is_production is True

    # Case insensitive
    with patch.dict(os.environ, {"ENVIRONMENT": "PRODUCTION"}):
        settings = Settings()
        assert settings.is_production is True


def test_qdrant_collection_name_customizable():
    """Test that Qdrant collection name can be customized."""
    with patch.dict(os.environ, {
        "QDRANT_COLLECTION_NAME": "custom_collection",
    }):
        settings = Settings()
        assert settings.qdrant_collection_name == "custom_collection"


def test_message_limits_configurable():
    """Test that message limits can be configured."""
    with patch.dict(os.environ, {
        "MAX_USER_MESSAGE_LENGTH": "1000",
        "MAX_AI_MESSAGE_LENGTH": "3000",
    }):
        settings = Settings()
        assert settings.max_user_message_length == 1000
        assert settings.max_ai_message_length == 3000


def test_conversation_limits_configurable():
    """Test that conversation limits can be configured."""
    with patch.dict(os.environ, {
        "MAX_CONVERSATIONS_PER_USER": "100",
        "MAX_MESSAGES_PER_CONVERSATION": "1000",
        "CONVERSATION_RETENTION_MONTHS": "24",
    }):
        settings = Settings()
        assert settings.max_conversations_per_user == 100
        assert settings.max_messages_per_conversation == 1000
        assert settings.conversation_retention_months == 24
