"""
Tests for agent service.

Tests agent initialization, model configuration, and tool registration.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.services.agent_service import AgentService


@pytest.fixture
def mock_gemini_config():
    """Mock Gemini configuration."""
    with patch('src.services.agent_service.settings') as mock_settings:
        mock_settings.llm_provider = "gemini"
        mock_settings.gemini_api_key = "test-gemini-key"
        mock_settings.openai_api_key = ""
        yield mock_settings


@pytest.fixture
def mock_openai_config():
    """Mock OpenAI configuration."""
    with patch('src.services.agent_service.settings') as mock_settings:
        mock_settings.llm_provider = "openai"
        mock_settings.gemini_api_key = ""
        mock_settings.openai_api_key = "test-openai-key"
        yield mock_settings


def test_agent_service_initialization_gemini(mock_gemini_config):
    """Test agent service initializes with Gemini provider."""
    service = AgentService(provider="gemini")

    assert service.provider == "gemini"
    assert service.model_name == "gemini-1.5-flash"
    assert service.system_prompt is not None
    assert len(service.tools) == 0


def test_agent_service_initialization_openai(mock_openai_config):
    """Test agent service initializes with OpenAI provider."""
    service = AgentService(provider="openai")

    assert service.provider == "openai"
    assert service.model_name == "gpt-4o-mini"
    assert service.system_prompt is not None


def test_agent_service_invalid_provider():
    """Test agent service raises error for invalid provider."""
    with pytest.raises(ValueError, match="Invalid provider"):
        AgentService(provider="invalid")


def test_agent_service_missing_gemini_key():
    """Test agent service raises error when Gemini key is missing."""
    with patch('src.services.agent_service.settings') as mock_settings:
        mock_settings.llm_provider = "gemini"
        mock_settings.gemini_api_key = ""

        with pytest.raises(ValueError, match="GEMINI_API_KEY not configured"):
            AgentService(provider="gemini")


def test_agent_service_missing_openai_key():
    """Test agent service raises error when OpenAI key is missing."""
    with patch('src.services.agent_service.settings') as mock_settings:
        mock_settings.llm_provider = "openai"
        mock_settings.openai_api_key = ""

        with pytest.raises(ValueError, match="OPENAI_API_KEY not configured"):
            AgentService(provider="openai")


def test_agent_service_defaults_to_config_provider(mock_gemini_config):
    """Test agent service uses provider from config when not specified."""
    service = AgentService()

    assert service.provider == "gemini"


def test_system_prompt_includes_tone_guidelines(mock_gemini_config):
    """Test system prompt includes professional tone guidelines (FR-027)."""
    service = AgentService(provider="gemini")

    assert "professional" in service.system_prompt.lower()
    assert "academic" in service.system_prompt.lower()
    assert "tone" in service.system_prompt.lower()


def test_system_prompt_includes_step_by_step(mock_gemini_config):
    """Test system prompt includes step-by-step explanation guidelines (FR-028)."""
    service = AgentService(provider="gemini")

    assert "step-by-step" in service.system_prompt.lower()
    assert "explanation" in service.system_prompt.lower()


def test_system_prompt_includes_analogies(mock_gemini_config):
    """Test system prompt includes analogy guidelines (FR-029)."""
    service = AgentService(provider="gemini")

    assert "analogies" in service.system_prompt.lower() or "analogy" in service.system_prompt.lower()


def test_system_prompt_includes_prerequisites(mock_gemini_config):
    """Test system prompt includes prerequisite suggestion guidelines (FR-030)."""
    service = AgentService(provider="gemini")

    assert "prerequisite" in service.system_prompt.lower()
    assert "foundational" in service.system_prompt.lower() or "background" in service.system_prompt.lower()


def test_system_prompt_includes_rag_grounding(mock_gemini_config):
    """Test system prompt includes strict RAG grounding instructions."""
    service = AgentService(provider="gemini")

    assert "only" in service.system_prompt.lower()
    assert "textbook" in service.system_prompt.lower()
    assert "provided" in service.system_prompt.lower()


def test_system_prompt_includes_source_attribution(mock_gemini_config):
    """Test system prompt includes source attribution instructions."""
    service = AgentService(provider="gemini")

    assert "source" in service.system_prompt.lower()
    assert "cite" in service.system_prompt.lower() or "reference" in service.system_prompt.lower()


def test_register_tool(mock_gemini_config):
    """Test registering a single tool."""
    service = AgentService(provider="gemini")
    mock_tool = Mock()

    service.register_tool(mock_tool)

    assert len(service.tools) == 1
    assert service.tools[0] == mock_tool


def test_register_multiple_tools(mock_gemini_config):
    """Test registering multiple tools."""
    service = AgentService(provider="gemini")
    mock_tool_1 = Mock()
    mock_tool_2 = Mock()

    service.register_tools([mock_tool_1, mock_tool_2])

    assert len(service.tools) == 2
    assert mock_tool_1 in service.tools
    assert mock_tool_2 in service.tools


def test_register_tools_extends_existing(mock_gemini_config):
    """Test registering tools extends existing tool list."""
    service = AgentService(provider="gemini")
    mock_tool_1 = Mock()
    mock_tool_2 = Mock()
    mock_tool_3 = Mock()

    service.register_tool(mock_tool_1)
    service.register_tools([mock_tool_2, mock_tool_3])

    assert len(service.tools) == 3


@pytest.mark.asyncio
async def test_generate_response_empty_question(mock_gemini_config):
    """Test generate_response raises error for empty question."""
    service = AgentService(provider="gemini")

    with pytest.raises(ValueError, match="Question cannot be empty"):
        await service.generate_response("")

    with pytest.raises(ValueError, match="Question cannot be empty"):
        await service.generate_response("   ")


@pytest.mark.asyncio
async def test_generate_response_returns_structure(mock_gemini_config):
    """Test generate_response returns expected structure."""
    service = AgentService(provider="gemini")

    result = await service.generate_response("What is VSLAM?")

    assert "content" in result
    assert "confidence_score" in result
    assert "source_references" in result
    assert isinstance(result["source_references"], list)


@pytest.mark.asyncio
async def test_generate_response_with_selected_text(mock_gemini_config):
    """Test generate_response accepts selected text parameters."""
    service = AgentService(provider="gemini")

    result = await service.generate_response(
        question="Explain this",
        selected_text="VSLAM is a technique...",
        selected_text_metadata={"chapter": "isaac-sim", "url": "/docs/isaac-sim"},
    )

    assert result is not None


def test_get_model_info_gemini(mock_gemini_config):
    """Test get_model_info returns correct info for Gemini."""
    service = AgentService(provider="gemini")

    info = service.get_model_info()

    assert info["provider"] == "gemini"
    assert info["model"] == "gemini-1.5-flash"


def test_get_model_info_openai(mock_openai_config):
    """Test get_model_info returns correct info for OpenAI."""
    service = AgentService(provider="openai")

    info = service.get_model_info()

    assert info["provider"] == "openai"
    assert info["model"] == "gpt-4o-mini"


def test_get_api_key_gemini(mock_gemini_config):
    """Test _get_api_key returns Gemini key."""
    service = AgentService(provider="gemini")

    api_key = service._get_api_key()

    assert api_key == "test-gemini-key"


def test_get_api_key_openai(mock_openai_config):
    """Test _get_api_key returns OpenAI key."""
    service = AgentService(provider="openai")

    api_key = service._get_api_key()

    assert api_key == "test-openai-key"


def test_get_model_name_gemini(mock_gemini_config):
    """Test _get_model_name returns correct model for Gemini."""
    service = AgentService(provider="gemini")

    model_name = service._get_model_name()

    assert model_name == "gemini-1.5-flash"


def test_get_model_name_openai(mock_openai_config):
    """Test _get_model_name returns correct model for OpenAI."""
    service = AgentService(provider="openai")

    model_name = service._get_model_name()

    assert model_name == "gpt-4o-mini"


def test_system_prompt_not_empty(mock_gemini_config):
    """Test system prompt is not empty."""
    service = AgentService(provider="gemini")

    assert service.system_prompt
    assert len(service.system_prompt) > 100  # Should be substantial


def test_system_prompt_includes_uncertainty_handling(mock_gemini_config):
    """Test system prompt includes uncertainty handling (FR-017, FR-018)."""
    service = AgentService(provider="gemini")

    prompt_lower = service.system_prompt.lower()
    assert "don't have information" in prompt_lower or "insufficient" in prompt_lower
    assert "suggest" in prompt_lower or "related" in prompt_lower
