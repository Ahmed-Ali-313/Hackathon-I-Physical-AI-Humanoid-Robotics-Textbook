"""
Tests for ChatMessage model.

Tests message creation, source references, and constraints.
"""

import pytest
from datetime import datetime
from src.models.chat_message import ChatMessage


def test_chat_message_creation_user():
    """Test user message can be created."""
    message = ChatMessage(
        conversation_id="test-conv-id",
        content="What is VSLAM?",
        sender_type="user",
    )

    assert message.conversation_id == "test-conv-id"
    assert message.content == "What is VSLAM?"
    assert message.sender_type == "user"
    assert message.confidence_score is None
    assert message.id is not None


def test_chat_message_creation_assistant():
    """Test assistant message can be created."""
    message = ChatMessage(
        conversation_id="test-conv-id",
        content="VSLAM stands for Visual Simultaneous Localization and Mapping.",
        sender_type="assistant",
        confidence_score=0.85,
    )

    assert message.sender_type == "assistant"
    assert message.confidence_score == 0.85


def test_chat_message_to_dict():
    """Test message can be converted to dictionary."""
    message = ChatMessage(
        id="test-id",
        conversation_id="test-conv-id",
        content="What is VSLAM?",
        sender_type="user",
    )
    message.created_at = datetime(2026, 2, 22, 10, 0, 0)

    result = message.to_dict()

    assert result["id"] == "test-id"
    assert result["conversation_id"] == "test-conv-id"
    assert result["content"] == "What is VSLAM?"
    assert result["sender_type"] == "user"
    assert result["confidence_score"] is None
    assert result["source_references"] == []
    assert "2026-02-22" in result["created_at"]


def test_chat_message_repr():
    """Test message string representation."""
    message = ChatMessage(
        id="test-id",
        conversation_id="test-conv-id",
        content="What is VSLAM?",
        sender_type="user",
    )

    repr_str = repr(message)

    assert "test-id" in repr_str
    assert "user" in repr_str
    assert "What is VSLAM?" in repr_str


def test_chat_message_repr_long_content():
    """Test message repr truncates long content."""
    long_content = "A" * 100
    message = ChatMessage(
        id="test-id",
        conversation_id="test-conv-id",
        content=long_content,
        sender_type="user",
    )

    repr_str = repr(message)

    assert "..." in repr_str
    assert len(repr_str) < len(long_content) + 50


def test_get_source_references_empty():
    """Test getting empty source references."""
    message = ChatMessage(
        conversation_id="test-conv-id",
        content="Test",
        sender_type="assistant",
    )

    refs = message.get_source_references()

    assert refs == []


def test_set_and_get_source_references():
    """Test setting and getting source references."""
    message = ChatMessage(
        conversation_id="test-conv-id",
        content="Test",
        sender_type="assistant",
    )

    references = [
        {"chapter": "isaac-sim", "section": "intro", "url": "/docs/module-3-isaac/isaac-sim"},
        {"chapter": "vslam", "section": "basics", "url": "/docs/module-2/vslam"},
    ]

    message.set_source_references(references)
    result = message.get_source_references()

    assert len(result) == 2
    assert result[0]["chapter"] == "isaac-sim"
    assert result[1]["url"] == "/docs/module-2/vslam"


def test_set_source_references_invalid_type():
    """Test setting source references with invalid type raises error."""
    message = ChatMessage(
        conversation_id="test-conv-id",
        content="Test",
        sender_type="assistant",
    )

    with pytest.raises(ValueError, match="Source references must be a list"):
        message.set_source_references("not a list")


def test_set_source_references_invalid_item():
    """Test setting source references with invalid item raises error."""
    message = ChatMessage(
        conversation_id="test-conv-id",
        content="Test",
        sender_type="assistant",
    )

    with pytest.raises(ValueError, match="Each source reference must be a dictionary"):
        message.set_source_references(["not a dict"])


def test_set_source_references_missing_url():
    """Test setting source references without URL raises error."""
    message = ChatMessage(
        conversation_id="test-conv-id",
        content="Test",
        sender_type="assistant",
    )

    with pytest.raises(ValueError, match="Each source reference must have a 'url' field"):
        message.set_source_references([{"chapter": "test"}])


def test_create_user_message():
    """Test creating user message with factory method."""
    message = ChatMessage.create_user_message(
        conversation_id="test-conv-id",
        content="What is VSLAM?",
    )

    assert message.conversation_id == "test-conv-id"
    assert message.content == "What is VSLAM?"
    assert message.sender_type == "user"
    assert message.confidence_score is None


def test_create_user_message_too_long():
    """Test creating user message with content > 500 chars raises error."""
    long_content = "A" * 501

    with pytest.raises(ValueError, match="User message cannot exceed 500 characters"):
        ChatMessage.create_user_message(
            conversation_id="test-conv-id",
            content=long_content,
        )


def test_create_assistant_message():
    """Test creating assistant message with factory method."""
    references = [{"chapter": "test", "url": "/test"}]

    message = ChatMessage.create_assistant_message(
        conversation_id="test-conv-id",
        content="VSLAM is Visual SLAM.",
        confidence_score=0.85,
        source_references=references,
    )

    assert message.conversation_id == "test-conv-id"
    assert message.content == "VSLAM is Visual SLAM."
    assert message.sender_type == "assistant"
    assert message.confidence_score == 0.85
    assert message.get_source_references() == references


def test_create_assistant_message_too_long():
    """Test creating assistant message with content > 2000 chars raises error."""
    long_content = "A" * 2001

    with pytest.raises(ValueError, match="Assistant message cannot exceed 2000 characters"):
        ChatMessage.create_assistant_message(
            conversation_id="test-conv-id",
            content=long_content,
            confidence_score=0.85,
            source_references=[],
        )


def test_create_assistant_message_invalid_confidence():
    """Test creating assistant message with invalid confidence raises error."""
    with pytest.raises(ValueError, match="Confidence score must be between 0.0 and 1.0"):
        ChatMessage.create_assistant_message(
            conversation_id="test-conv-id",
            content="Test",
            confidence_score=1.5,
            source_references=[],
        )

    with pytest.raises(ValueError, match="Confidence score must be between 0.0 and 1.0"):
        ChatMessage.create_assistant_message(
            conversation_id="test-conv-id",
            content="Test",
            confidence_score=-0.1,
            source_references=[],
        )


def test_confidence_score_boundary_values():
    """Test confidence score accepts boundary values 0.0 and 1.0."""
    message_min = ChatMessage.create_assistant_message(
        conversation_id="test-conv-id",
        content="Test",
        confidence_score=0.0,
        source_references=[],
    )
    assert message_min.confidence_score == 0.0

    message_max = ChatMessage.create_assistant_message(
        conversation_id="test-conv-id",
        content="Test",
        confidence_score=1.0,
        source_references=[],
    )
    assert message_max.confidence_score == 1.0


def test_source_references_to_dict():
    """Test source references are included in to_dict output."""
    references = [
        {"chapter": "isaac-sim", "url": "/docs/isaac-sim"},
    ]

    message = ChatMessage.create_assistant_message(
        conversation_id="test-conv-id",
        content="Test",
        confidence_score=0.85,
        source_references=references,
    )

    result = message.to_dict()

    assert result["source_references"] == references
    assert result["confidence_score"] == 0.85
