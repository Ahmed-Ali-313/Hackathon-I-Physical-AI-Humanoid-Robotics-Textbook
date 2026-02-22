"""
Tests for Conversation model.

Tests conversation creation, title generation, and constraints.
"""

import pytest
from datetime import datetime
from src.models.conversation import Conversation


def test_conversation_creation():
    """Test conversation can be created with required fields."""
    conversation = Conversation(
        user_id="test-user-id",
        title="What is VSLAM?",
    )

    assert conversation.user_id == "test-user-id"
    assert conversation.title == "What is VSLAM?"
    assert conversation.message_count == 0
    assert conversation.id is not None


def test_conversation_default_message_count():
    """Test conversation has default message count of 0."""
    conversation = Conversation(
        user_id="test-user-id",
        title="Test conversation",
    )

    assert conversation.message_count == 0


def test_conversation_to_dict():
    """Test conversation can be converted to dictionary."""
    conversation = Conversation(
        id="test-id",
        user_id="test-user-id",
        title="What is VSLAM?",
        message_count=5,
    )
    conversation.created_at = datetime(2026, 2, 22, 10, 0, 0)
    conversation.updated_at = datetime(2026, 2, 22, 11, 0, 0)

    result = conversation.to_dict()

    assert result["id"] == "test-id"
    assert result["user_id"] == "test-user-id"
    assert result["title"] == "What is VSLAM?"
    assert result["message_count"] == 5
    assert "2026-02-22" in result["created_at"]
    assert "2026-02-22" in result["updated_at"]


def test_conversation_repr():
    """Test conversation string representation."""
    conversation = Conversation(
        id="test-id",
        user_id="test-user-id",
        title="What is VSLAM?",
        message_count=3,
    )

    repr_str = repr(conversation)

    assert "test-id" in repr_str
    assert "What is VSLAM?" in repr_str
    assert "3" in repr_str


def test_generate_title_short_question():
    """Test title generation for short questions (< 50 chars)."""
    question = "What is VSLAM?"
    title = Conversation.generate_title_from_question(question)

    assert title == "What is VSLAM?"
    assert "..." not in title


def test_generate_title_exact_50_chars():
    """Test title generation for exactly 50 character question."""
    question = "A" * 50
    title = Conversation.generate_title_from_question(question)

    assert title == question
    assert "..." not in title


def test_generate_title_long_question_with_spaces():
    """Test title generation for long questions with word boundaries."""
    question = "What is the difference between VSLAM and traditional SLAM algorithms in robotics?"
    # This is > 50 chars, should truncate at word boundary

    title = Conversation.generate_title_from_question(question)

    assert len(title) <= 53  # 50 + "..."
    assert title.endswith("...")
    assert not title[:-3].endswith(" ")  # No trailing space before "..."
    assert "VSLAM" in title  # Should include beginning of question


def test_generate_title_long_question_no_spaces():
    """Test title generation for long questions without spaces."""
    question = "A" * 60  # No spaces
    title = Conversation.generate_title_from_question(question)

    assert len(title) == 53  # 50 + "..."
    assert title.endswith("...")


def test_generate_title_strips_whitespace():
    """Test title generation strips leading/trailing whitespace."""
    question = "  What is VSLAM?  "
    title = Conversation.generate_title_from_question(question)

    assert title == "What is VSLAM?"
    assert not title.startswith(" ")
    assert not title.endswith(" ")


def test_generate_title_custom_max_length():
    """Test title generation with custom max length."""
    question = "What is the difference between VSLAM and SLAM?"
    title = Conversation.generate_title_from_question(question, max_length=20)

    assert len(title) <= 23  # 20 + "..."
    assert title.endswith("...")


def test_generate_title_edge_case_51_chars():
    """Test title generation for 51 character question (just over limit)."""
    question = "What is the main difference between VSLAM and SLA"  # 49 chars
    question += "M?"  # Now 51 chars

    title = Conversation.generate_title_from_question(question)

    assert title.endswith("...")
    assert len(title) <= 53


def test_generate_title_preserves_question_mark():
    """Test title generation preserves question mark if within limit."""
    question = "What is VSLAM?"
    title = Conversation.generate_title_from_question(question)

    assert title.endswith("?")
    assert "..." not in title


def test_generate_title_word_boundary_truncation():
    """Test title truncates at word boundary, not mid-word."""
    question = "How do I configure the Isaac Sim environment for robotics simulation?"
    title = Conversation.generate_title_from_question(question)

    # Should not end with partial word before "..."
    assert title.endswith("...")
    words_before_ellipsis = title[:-3].split()
    last_word = words_before_ellipsis[-1] if words_before_ellipsis else ""

    # Last word should be complete (not cut off mid-word)
    # Check that it's a reasonable word from the original question
    assert last_word in question.split()
