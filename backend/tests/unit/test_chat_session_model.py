"""
Tests for ChatSession model.

Tests session creation, expiry, and lifecycle management.
"""

import pytest
from datetime import datetime, timedelta
from src.models.chat_session import ChatSession


def test_chat_session_creation():
    """Test chat session can be created."""
    session = ChatSession(
        user_id="test-user-id",
        conversation_id="test-conv-id",
        is_active=True,
        expires_at=datetime.utcnow() + timedelta(minutes=30),
    )

    assert session.user_id == "test-user-id"
    assert session.conversation_id == "test-conv-id"
    assert session.is_active is True
    assert session.id is not None


def test_chat_session_default_active():
    """Test chat session defaults to active."""
    session = ChatSession(
        user_id="test-user-id",
        expires_at=datetime.utcnow() + timedelta(minutes=30),
    )

    assert session.is_active is True


def test_chat_session_to_dict():
    """Test session can be converted to dictionary."""
    expires_at = datetime(2026, 2, 22, 12, 0, 0)
    session = ChatSession(
        id="test-id",
        user_id="test-user-id",
        conversation_id="test-conv-id",
        is_active=True,
        expires_at=expires_at,
    )
    session.created_at = datetime(2026, 2, 22, 11, 0, 0)
    session.updated_at = datetime(2026, 2, 22, 11, 30, 0)

    result = session.to_dict()

    assert result["id"] == "test-id"
    assert result["user_id"] == "test-user-id"
    assert result["conversation_id"] == "test-conv-id"
    assert result["is_active"] is True
    assert "2026-02-22" in result["created_at"]
    assert "2026-02-22" in result["expires_at"]


def test_chat_session_repr():
    """Test session string representation."""
    session = ChatSession(
        id="test-id",
        user_id="test-user-id",
        is_active=True,
        expires_at=datetime.utcnow() + timedelta(minutes=30),
    )

    repr_str = repr(session)

    assert "test-id" in repr_str
    assert "test-user-id" in repr_str
    assert "True" in repr_str


def test_is_expired_not_expired():
    """Test session is not expired when expires_at is in future."""
    session = ChatSession(
        user_id="test-user-id",
        expires_at=datetime.utcnow() + timedelta(minutes=30),
    )

    assert session.is_expired() is False


def test_is_expired_expired():
    """Test session is expired when expires_at is in past."""
    session = ChatSession(
        user_id="test-user-id",
        expires_at=datetime.utcnow() - timedelta(minutes=1),
    )

    assert session.is_expired() is True


def test_is_expired_no_expiry():
    """Test session is expired when expires_at is None."""
    session = ChatSession(
        user_id="test-user-id",
        expires_at=None,
    )

    assert session.is_expired() is True


def test_extend_expiry():
    """Test extending session expiry time."""
    session = ChatSession(
        user_id="test-user-id",
        expires_at=datetime.utcnow() + timedelta(minutes=5),
    )

    old_expiry = session.expires_at
    session.extend_expiry(minutes=30)

    assert session.expires_at > old_expiry
    # Should be approximately 30 minutes from now
    time_diff = (session.expires_at - datetime.utcnow()).total_seconds()
    assert 29 * 60 < time_diff < 31 * 60  # Between 29 and 31 minutes


def test_extend_expiry_custom_minutes():
    """Test extending session expiry with custom minutes."""
    session = ChatSession(
        user_id="test-user-id",
        expires_at=datetime.utcnow() + timedelta(minutes=5),
    )

    session.extend_expiry(minutes=60)

    time_diff = (session.expires_at - datetime.utcnow()).total_seconds()
    assert 59 * 60 < time_diff < 61 * 60  # Between 59 and 61 minutes


def test_deactivate():
    """Test deactivating a session."""
    session = ChatSession(
        user_id="test-user-id",
        is_active=True,
        expires_at=datetime.utcnow() + timedelta(minutes=30),
    )

    assert session.is_active is True

    session.deactivate()

    assert session.is_active is False


def test_create_session():
    """Test creating session with factory method."""
    session = ChatSession.create_session(
        user_id="test-user-id",
        conversation_id="test-conv-id",
    )

    assert session.user_id == "test-user-id"
    assert session.conversation_id == "test-conv-id"
    assert session.is_active is True
    assert session.expires_at is not None

    # Should expire in approximately 30 minutes
    time_diff = (session.expires_at - datetime.utcnow()).total_seconds()
    assert 29 * 60 < time_diff < 31 * 60


def test_create_session_without_conversation():
    """Test creating session without conversation ID."""
    session = ChatSession.create_session(user_id="test-user-id")

    assert session.user_id == "test-user-id"
    assert session.conversation_id is None
    assert session.is_active is True


def test_create_session_custom_expiry():
    """Test creating session with custom expiry time."""
    session = ChatSession.create_session(
        user_id="test-user-id",
        expiry_minutes=60,
    )

    time_diff = (session.expires_at - datetime.utcnow()).total_seconds()
    assert 59 * 60 < time_diff < 61 * 60


def test_cleanup_expired_sessions_none_expired():
    """Test cleanup when no sessions are expired."""
    sessions = [
        ChatSession.create_session(user_id="user-1"),
        ChatSession.create_session(user_id="user-2"),
    ]

    count = ChatSession.cleanup_expired_sessions(sessions)

    assert count == 0
    assert all(s.is_active for s in sessions)


def test_cleanup_expired_sessions_some_expired():
    """Test cleanup deactivates expired sessions."""
    # Create expired session
    expired_session = ChatSession(
        user_id="user-1",
        is_active=True,
        expires_at=datetime.utcnow() - timedelta(minutes=1),
    )

    # Create active session
    active_session = ChatSession.create_session(user_id="user-2")

    sessions = [expired_session, active_session]

    count = ChatSession.cleanup_expired_sessions(sessions)

    assert count == 1
    assert expired_session.is_active is False
    assert active_session.is_active is True


def test_cleanup_expired_sessions_all_expired():
    """Test cleanup when all sessions are expired."""
    sessions = [
        ChatSession(
            user_id="user-1",
            is_active=True,
            expires_at=datetime.utcnow() - timedelta(minutes=1),
        ),
        ChatSession(
            user_id="user-2",
            is_active=True,
            expires_at=datetime.utcnow() - timedelta(minutes=5),
        ),
    ]

    count = ChatSession.cleanup_expired_sessions(sessions)

    assert count == 2
    assert all(not s.is_active for s in sessions)


def test_cleanup_expired_sessions_already_inactive():
    """Test cleanup skips already inactive sessions."""
    session = ChatSession(
        user_id="user-1",
        is_active=False,
        expires_at=datetime.utcnow() - timedelta(minutes=1),
    )

    count = ChatSession.cleanup_expired_sessions([session])

    assert count == 0
    assert session.is_active is False


def test_cleanup_expired_sessions_empty_list():
    """Test cleanup with empty session list."""
    count = ChatSession.cleanup_expired_sessions([])

    assert count == 0
