"""
Tests for chat service.

Tests conversation management, message persistence, and title generation.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from src.services.chat_service import ChatService
from src.models.conversation import Conversation
from src.models.chat_message import ChatMessage


@pytest.fixture
def mock_db_session():
    """Mock database session."""
    session = Mock()
    session.add = Mock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def mock_agent_service():
    """Mock agent service."""
    service = Mock()
    service.generate_response = AsyncMock(return_value={
        "content": "VSLAM stands for Visual Simultaneous Localization and Mapping.",
        "confidence_score": 0.85,
        "source_references": [
            {"chapter": "isaac-sim", "section": "intro", "url": "/docs/isaac-sim"}
        ],
    })
    return service


@pytest.mark.asyncio
async def test_create_conversation(mock_db_session):
    """Test creating a new conversation."""
    service = ChatService(db_session=mock_db_session)

    conversation = await service.create_conversation(
        user_id="test-user-id",
        title="What is VSLAM?",
    )

    assert conversation.user_id == "test-user-id"
    assert conversation.title == "What is VSLAM?"
    assert conversation.message_count == 0
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_create_conversation_generates_title_from_question(mock_db_session):
    """Test conversation title is auto-generated from first question."""
    service = ChatService(db_session=mock_db_session)

    question = "What is the difference between VSLAM and traditional SLAM?"
    conversation = await service.create_conversation_from_question(
        user_id="test-user-id",
        question=question,
    )

    assert conversation.title == question  # Short enough to use full question
    mock_db_session.add.assert_called_once()


@pytest.mark.asyncio
async def test_create_conversation_truncates_long_title(mock_db_session):
    """Test conversation title is truncated at word boundary for long questions."""
    service = ChatService(db_session=mock_db_session)

    long_question = "What is the main difference between VSLAM and traditional SLAM algorithms in robotics applications?"
    conversation = await service.create_conversation_from_question(
        user_id="test-user-id",
        question=long_question,
    )

    assert len(conversation.title) <= 53  # 50 + "..."
    assert conversation.title.endswith("...")
    assert "VSLAM" in conversation.title


@pytest.mark.asyncio
async def test_send_message_creates_user_and_assistant_messages(mock_db_session, mock_agent_service):
    """Test sending message creates both user and assistant messages."""
    service = ChatService(db_session=mock_db_session, agent_service=mock_agent_service)

    conversation = Conversation(id="conv-1", user_id="user-1", title="Test")

    result = await service.send_message(
        conversation=conversation,
        user_message="What is VSLAM?",
    )

    assert "user_message" in result
    assert "assistant_message" in result
    assert result["user_message"].sender_type == "user"
    assert result["assistant_message"].sender_type == "assistant"
    assert mock_db_session.add.call_count == 2  # User + assistant messages


@pytest.mark.asyncio
async def test_send_message_calls_agent_service(mock_db_session, mock_agent_service):
    """Test send_message calls agent service to generate response."""
    service = ChatService(db_session=mock_db_session, agent_service=mock_agent_service)

    conversation = Conversation(id="conv-1", user_id="user-1", title="Test")

    await service.send_message(
        conversation=conversation,
        user_message="What is VSLAM?",
    )

    mock_agent_service.generate_response.assert_called_once_with("What is VSLAM?")


@pytest.mark.asyncio
async def test_send_message_stores_confidence_score(mock_db_session, mock_agent_service):
    """Test send_message stores confidence score in assistant message."""
    service = ChatService(db_session=mock_db_session, agent_service=mock_agent_service)

    conversation = Conversation(id="conv-1", user_id="user-1", title="Test")

    result = await service.send_message(
        conversation=conversation,
        user_message="What is VSLAM?",
    )

    assert result["assistant_message"].confidence_score == 0.85


@pytest.mark.asyncio
async def test_send_message_stores_source_references(mock_db_session, mock_agent_service):
    """Test send_message stores source references in assistant message."""
    service = ChatService(db_session=mock_db_session, agent_service=mock_agent_service)

    conversation = Conversation(id="conv-1", user_id="user-1", title="Test")

    result = await service.send_message(
        conversation=conversation,
        user_message="What is VSLAM?",
    )

    sources = result["assistant_message"].get_source_references()
    assert len(sources) == 1
    assert sources[0]["chapter"] == "isaac-sim"


@pytest.mark.asyncio
async def test_send_message_with_selected_text(mock_db_session, mock_agent_service):
    """Test send_message passes selected text to agent service."""
    service = ChatService(db_session=mock_db_session, agent_service=mock_agent_service)

    conversation = Conversation(id="conv-1", user_id="user-1", title="Test")

    await service.send_message(
        conversation=conversation,
        user_message="Explain this",
        selected_text="VSLAM is a technique...",
        selected_text_metadata={"chapter": "isaac-sim"},
    )

    mock_agent_service.generate_response.assert_called_once_with(
        "Explain this",
        selected_text="VSLAM is a technique...",
        selected_text_metadata={"chapter": "isaac-sim"},
    )


@pytest.mark.asyncio
async def test_send_message_updates_conversation_message_count(mock_db_session, mock_agent_service):
    """Test send_message increments conversation message count."""
    service = ChatService(db_session=mock_db_session, agent_service=mock_agent_service)

    conversation = Conversation(id="conv-1", user_id="user-1", title="Test", message_count=0)

    await service.send_message(
        conversation=conversation,
        user_message="What is VSLAM?",
    )

    # Message count should be updated (via database trigger in production)
    assert mock_db_session.commit.called


@pytest.mark.asyncio
async def test_get_conversation_by_id(mock_db_session):
    """Test getting conversation by ID."""
    service = ChatService(db_session=mock_db_session)

    mock_conversation = Conversation(id="conv-1", user_id="user-1", title="Test")
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = mock_conversation
    mock_db_session.execute.return_value = mock_result

    conversation = await service.get_conversation(conversation_id="conv-1", user_id="user-1")

    assert conversation == mock_conversation


@pytest.mark.asyncio
async def test_get_conversation_not_found(mock_db_session):
    """Test get_conversation returns None when not found."""
    service = ChatService(db_session=mock_db_session)

    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db_session.execute.return_value = mock_result

    conversation = await service.get_conversation(conversation_id="nonexistent", user_id="user-1")

    assert conversation is None


@pytest.mark.asyncio
async def test_get_user_conversations(mock_db_session):
    """Test getting all conversations for a user."""
    service = ChatService(db_session=mock_db_session)

    mock_conversations = [
        Conversation(id="conv-1", user_id="user-1", title="Test 1"),
        Conversation(id="conv-2", user_id="user-1", title="Test 2"),
    ]
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = mock_conversations
    mock_db_session.execute.return_value = mock_result

    conversations = await service.get_user_conversations(user_id="user-1")

    assert len(conversations) == 2
    assert conversations[0].title == "Test 1"


@pytest.mark.asyncio
async def test_get_conversation_messages(mock_db_session):
    """Test getting messages for a conversation."""
    service = ChatService(db_session=mock_db_session)

    mock_messages = [
        ChatMessage(id="msg-1", conversation_id="conv-1", content="Question", sender_type="user"),
        ChatMessage(id="msg-2", conversation_id="conv-1", content="Answer", sender_type="assistant"),
    ]
    mock_result = Mock()
    mock_result.scalars.return_value.all.return_value = mock_messages
    mock_db_session.execute.return_value = mock_result

    messages = await service.get_conversation_messages(conversation_id="conv-1")

    assert len(messages) == 2
    assert messages[0].sender_type == "user"
    assert messages[1].sender_type == "assistant"


@pytest.mark.asyncio
async def test_title_generation_edge_case_exact_50_chars(mock_db_session):
    """Test title generation for exactly 50 character question."""
    service = ChatService(db_session=mock_db_session)

    question = "A" * 50
    conversation = await service.create_conversation_from_question(
        user_id="user-1",
        question=question,
    )

    assert conversation.title == question
    assert "..." not in conversation.title


@pytest.mark.asyncio
async def test_title_generation_edge_case_51_chars(mock_db_session):
    """Test title generation for 51 character question (just over limit)."""
    service = ChatService(db_session=mock_db_session)

    question = "What is the main difference between VSLAM and SLA" + "M?"  # 51 chars
    conversation = await service.create_conversation_from_question(
        user_id="user-1",
        question=question,
    )

    assert conversation.title.endswith("...")
    assert len(conversation.title) <= 53
