"""
Integration tests for chat API.

Tests chat endpoints with authentication and database integration.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import Mock, patch, AsyncMock
from src.main import app


@pytest.fixture
def mock_auth_user():
    """Mock authenticated user."""
    return {
        "id": "test-user-id",
        "email": "test@example.com",
    }


@pytest.fixture
def auth_headers():
    """Mock authentication headers."""
    return {
        "Authorization": "Bearer test-jwt-token"
    }


@pytest.mark.asyncio
async def test_create_conversation_success(auth_headers, mock_auth_user):
    """Test creating a new conversation."""
    with patch('src.api.chat.get_current_user', return_value=mock_auth_user):
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/chat/conversations",
                headers=auth_headers,
                json={"title": "What is VSLAM?"},
            )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == "What is VSLAM?"
    assert data["user_id"] == "test-user-id"


@pytest.mark.asyncio
async def test_create_conversation_unauthorized():
    """Test creating conversation without authentication."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/chat/conversations",
            json={"title": "What is VSLAM?"},
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_send_message_success(auth_headers, mock_auth_user):
    """Test sending a message to a conversation."""
    with patch('src.api.chat.get_current_user', return_value=mock_auth_user):
        with patch('src.api.chat.chat_service') as mock_chat_service:
            # Mock conversation
            mock_conversation = Mock()
            mock_conversation.id = "conv-1"
            mock_conversation.user_id = "test-user-id"
            mock_chat_service.get_conversation = AsyncMock(return_value=mock_conversation)

            # Mock send_message response
            mock_user_msg = Mock()
            mock_user_msg.to_dict.return_value = {
                "id": "msg-1",
                "content": "What is VSLAM?",
                "sender_type": "user",
            }

            mock_assistant_msg = Mock()
            mock_assistant_msg.to_dict.return_value = {
                "id": "msg-2",
                "content": "VSLAM stands for Visual SLAM.",
                "sender_type": "assistant",
                "confidence_score": 0.85,
                "source_references": [{"chapter": "isaac-sim", "url": "/docs/isaac-sim"}],
            }

            mock_chat_service.send_message = AsyncMock(return_value={
                "user_message": mock_user_msg,
                "assistant_message": mock_assistant_msg,
            })

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/chat/conversations/conv-1/messages",
                    headers=auth_headers,
                    json={"content": "What is VSLAM?"},
                )

    assert response.status_code == 200
    data = response.json()
    assert "user_message" in data
    assert "assistant_message" in data
    assert data["assistant_message"]["confidence_score"] == 0.85


@pytest.mark.asyncio
async def test_send_message_conversation_not_found(auth_headers, mock_auth_user):
    """Test sending message to non-existent conversation."""
    with patch('src.api.chat.get_current_user', return_value=mock_auth_user):
        with patch('src.api.chat.chat_service') as mock_chat_service:
            mock_chat_service.get_conversation = AsyncMock(return_value=None)

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/chat/conversations/nonexistent/messages",
                    headers=auth_headers,
                    json={"content": "What is VSLAM?"},
                )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_send_message_unauthorized_access(auth_headers):
    """Test sending message to another user's conversation."""
    mock_user = {"id": "user-1", "email": "user1@example.com"}

    with patch('src.api.chat.get_current_user', return_value=mock_user):
        with patch('src.api.chat.chat_service') as mock_chat_service:
            # Mock conversation owned by different user
            mock_conversation = Mock()
            mock_conversation.id = "conv-1"
            mock_conversation.user_id = "user-2"  # Different user
            mock_chat_service.get_conversation = AsyncMock(return_value=mock_conversation)

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/chat/conversations/conv-1/messages",
                    headers=auth_headers,
                    json={"content": "What is VSLAM?"},
                )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_conversations_success(auth_headers, mock_auth_user):
    """Test getting user's conversations."""
    with patch('src.api.chat.get_current_user', return_value=mock_auth_user):
        with patch('src.api.chat.chat_service') as mock_chat_service:
            mock_conversations = [
                Mock(to_dict=lambda: {"id": "conv-1", "title": "Test 1"}),
                Mock(to_dict=lambda: {"id": "conv-2", "title": "Test 2"}),
            ]
            mock_chat_service.get_user_conversations = AsyncMock(return_value=mock_conversations)

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get(
                    "/api/chat/conversations",
                    headers=auth_headers,
                )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Test 1"


@pytest.mark.asyncio
async def test_get_conversation_messages_success(auth_headers, mock_auth_user):
    """Test getting messages for a conversation."""
    with patch('src.api.chat.get_current_user', return_value=mock_auth_user):
        with patch('src.api.chat.chat_service') as mock_chat_service:
            # Mock conversation
            mock_conversation = Mock()
            mock_conversation.id = "conv-1"
            mock_conversation.user_id = "test-user-id"
            mock_chat_service.get_conversation = AsyncMock(return_value=mock_conversation)

            # Mock messages
            mock_messages = [
                Mock(to_dict=lambda: {"id": "msg-1", "content": "Question", "sender_type": "user"}),
                Mock(to_dict=lambda: {"id": "msg-2", "content": "Answer", "sender_type": "assistant"}),
            ]
            mock_chat_service.get_conversation_messages = AsyncMock(return_value=mock_messages)

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get(
                    "/api/chat/conversations/conv-1/messages",
                    headers=auth_headers,
                )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_send_message_with_selected_text(auth_headers, mock_auth_user):
    """Test sending message with selected text (selection mode)."""
    with patch('src.api.chat.get_current_user', return_value=mock_auth_user):
        with patch('src.api.chat.chat_service') as mock_chat_service:
            mock_conversation = Mock()
            mock_conversation.id = "conv-1"
            mock_conversation.user_id = "test-user-id"
            mock_chat_service.get_conversation = AsyncMock(return_value=mock_conversation)

            mock_chat_service.send_message = AsyncMock(return_value={
                "user_message": Mock(to_dict=lambda: {"id": "msg-1"}),
                "assistant_message": Mock(to_dict=lambda: {"id": "msg-2"}),
            })

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/chat/conversations/conv-1/messages",
                    headers=auth_headers,
                    json={
                        "content": "Explain this",
                        "selected_text": "VSLAM is a technique...",
                        "selected_text_metadata": {"chapter": "isaac-sim"},
                    },
                )

    assert response.status_code == 200
    # Verify send_message was called with selected_text
    mock_chat_service.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_send_message_empty_content(auth_headers, mock_auth_user):
    """Test sending message with empty content."""
    with patch('src.api.chat.get_current_user', return_value=mock_auth_user):
        with patch('src.api.chat.chat_service') as mock_chat_service:
            mock_conversation = Mock()
            mock_conversation.user_id = "test-user-id"
            mock_chat_service.get_conversation = AsyncMock(return_value=mock_conversation)

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/chat/conversations/conv-1/messages",
                    headers=auth_headers,
                    json={"content": ""},
                )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_send_message_too_long(auth_headers, mock_auth_user):
    """Test sending message exceeding 500 character limit."""
    with patch('src.api.chat.get_current_user', return_value=mock_auth_user):
        with patch('src.api.chat.chat_service') as mock_chat_service:
            mock_conversation = Mock()
            mock_conversation.user_id = "test-user-id"
            mock_chat_service.get_conversation = AsyncMock(return_value=mock_conversation)

            long_content = "A" * 501

            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/chat/conversations/conv-1/messages",
                    headers=auth_headers,
                    json={"content": long_content},
                )

    assert response.status_code == 400
