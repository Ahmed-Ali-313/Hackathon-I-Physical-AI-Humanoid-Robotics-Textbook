"""
Tests for agent service.

Tests agent initialization, model configuration, and tool registration.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.services.agent_service import AgentService


@pytest.fixture
def mock_openai_config():
    """Mock OpenAI configuration."""
    with patch('src.services.agent_service.settings') as mock_settings:
        mock_settings.openai_api_key = "test-openai-key"
        yield mock_settings


def test_agent_service_initialization_openai(mock_openai_config):
    """Test agent service initializes with OpenAI."""
    service = AgentService()

    assert service.model_name == "gpt-4o-mini"
    assert service.system_prompt is not None
    assert len(service.tools) == 0


def test_agent_service_missing_openai_key():
    """Test agent service raises error when OpenAI key is missing."""
    with patch('src.services.agent_service.settings') as mock_settings:
        mock_settings.openai_api_key = ""

        with pytest.raises(ValueError, match="OPENAI_API_KEY not configured"):
            AgentService()


def test_system_prompt_includes_tone_guidelines(mock_openai_config):
    """Test system prompt includes professional tone guidelines (FR-027)."""
    service = AgentService()

    assert "professional" in service.system_prompt.lower()
    assert "academic" in service.system_prompt.lower()
    assert "tone" in service.system_prompt.lower()


def test_system_prompt_includes_step_by_step(mock_openai_config):
    """Test system prompt includes step-by-step explanation guidelines (FR-028)."""
    service = AgentService()

    assert "step-by-step" in service.system_prompt.lower()
    assert "explanation" in service.system_prompt.lower()


def test_system_prompt_includes_analogies(mock_openai_config):
    """Test system prompt includes analogy guidelines (FR-029)."""
    service = AgentService()

    assert "analogies" in service.system_prompt.lower() or "analogy" in service.system_prompt.lower()


def test_system_prompt_includes_prerequisites(mock_openai_config):
    """Test system prompt includes prerequisite suggestion guidelines (FR-030)."""
    service = AgentService()

    assert "prerequisite" in service.system_prompt.lower()
    assert "foundational" in service.system_prompt.lower() or "background" in service.system_prompt.lower()


def test_system_prompt_includes_rag_grounding(mock_openai_config):
    """Test system prompt includes strict RAG grounding instructions."""
    service = AgentService()

    assert "only" in service.system_prompt.lower()
    assert "textbook" in service.system_prompt.lower()
    assert "provided" in service.system_prompt.lower()


def test_system_prompt_includes_source_attribution(mock_openai_config):
    """Test system prompt includes source attribution instructions."""
    service = AgentService()

    assert "source" in service.system_prompt.lower()
    assert "cite" in service.system_prompt.lower() or "reference" in service.system_prompt.lower()


def test_register_tool(mock_openai_config):
    """Test registering a single tool."""
    service = AgentService()
    mock_tool = Mock()

    service.register_tool(mock_tool)

    assert len(service.tools) == 1
    assert service.tools[0] == mock_tool


def test_register_multiple_tools(mock_openai_config):
    """Test registering multiple tools."""
    service = AgentService()
    mock_tool_1 = Mock()
    mock_tool_2 = Mock()

    service.register_tools([mock_tool_1, mock_tool_2])

    assert len(service.tools) == 2
    assert mock_tool_1 in service.tools
    assert mock_tool_2 in service.tools


def test_register_tools_extends_existing(mock_openai_config):
    """Test registering tools extends existing tool list."""
    service = AgentService()
    mock_tool_1 = Mock()
    mock_tool_2 = Mock()
    mock_tool_3 = Mock()

    service.register_tool(mock_tool_1)
    service.register_tools([mock_tool_2, mock_tool_3])

    assert len(service.tools) == 3


@pytest.mark.asyncio
async def test_generate_response_empty_question(mock_openai_config):
    """Test generate_response raises error for empty question."""
    service = AgentService()

    with pytest.raises(ValueError, match="Question cannot be empty"):
        await service.generate_response("")

    with pytest.raises(ValueError, match="Question cannot be empty"):
        await service.generate_response("   ")


@pytest.mark.asyncio
async def test_generate_response_returns_structure(mock_openai_config):
    """Test generate_response returns expected structure."""
    service = AgentService()

    result = await service.generate_response("What is VSLAM?")

    assert "content" in result
    assert "confidence_score" in result
    assert "source_references" in result
    assert isinstance(result["source_references"], list)


@pytest.mark.asyncio
async def test_generate_response_with_selected_text(mock_openai_config):
    """Test generate_response accepts selected text parameters."""
    service = AgentService()

    result = await service.generate_response(
        question="Explain this",
        selected_text="VSLAM is a technique...",
        selected_text_metadata={"chapter": "isaac-sim", "url": "/docs/isaac-sim"},
    )

    assert result is not None


def test_get_model_info_openai(mock_openai_config):
    """Test get_model_info returns correct info for OpenAI."""
    service = AgentService()

    info = service.get_model_info()

    assert info["provider"] == "openai"
    assert info["model"] == "gpt-4o-mini"


def test_get_api_key_openai(mock_openai_config):
    """Test _get_api_key returns OpenAI key."""
    service = AgentService()

    api_key = service._get_api_key()

    assert api_key == "test-openai-key"


def test_system_prompt_not_empty(mock_openai_config):
    """Test system prompt is not empty."""
    service = AgentService()

    assert service.system_prompt
    assert len(service.system_prompt) > 100  # Should be substantial


def test_system_prompt_includes_uncertainty_handling(mock_openai_config):
    """Test system prompt includes uncertainty handling (FR-017, FR-018)."""
    service = AgentService()

    prompt_lower = service.system_prompt.lower()
    assert "don't have information" in prompt_lower or "insufficient" in prompt_lower
    assert "suggest" in prompt_lower or "related" in prompt_lower
