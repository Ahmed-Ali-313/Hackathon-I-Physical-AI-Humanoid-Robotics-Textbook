"""
Chat service for conversation and message management.

Handles conversation creation, message persistence, and integration with agent service.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.conversation import Conversation
from src.models.chat_message import ChatMessage
from src.services.agent_service import agent_service


class ChatService:
    """
    Service for managing chat conversations and messages.

    Handles conversation lifecycle, message persistence, and RAG integration.
    """

    def __init__(self, db_session: AsyncSession, agent_service=None):
        """
        Initialize chat service.

        Args:
            db_session: Database session
            agent_service: Agent service for generating responses (optional, uses global if not provided)
        """
        self.db_session = db_session
        self.agent_service = agent_service or agent_service

    async def create_conversation(
        self,
        user_id,  # Can be str or UUID
        title: str,
    ) -> Conversation:
        """
        Create a new conversation.

        Args:
            user_id: User ID (str or UUID)
            title: Conversation title

        Returns:
            Created conversation

        Raises:
            ValueError: If user_id or title is empty
        """
        if not user_id:
            raise ValueError("user_id cannot be empty")

        if not title or not title.strip():
            raise ValueError("title cannot be empty")

        conversation = Conversation(
            user_id=user_id,
            title=title,
        )

        self.db_session.add(conversation)
        await self.db_session.commit()
        await self.db_session.refresh(conversation)

        return conversation

    async def create_conversation_from_question(
        self,
        user_id: str,
        question: str,
    ) -> Conversation:
        """
        Create a new conversation with auto-generated title from question.

        Args:
            user_id: User ID
            question: User's first question

        Returns:
            Created conversation
        """
        # Generate title from question (max 50 chars with word boundary truncation)
        title = Conversation.generate_title_from_question(question, max_length=50)

        return await self.create_conversation(user_id=user_id, title=title)

    async def send_message(
        self,
        conversation: Conversation,
        user_message: str,
        selected_text: Optional[str] = None,
        selected_text_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, ChatMessage]:
        """
        Send a message and get AI response.

        Args:
            conversation: Conversation to add message to
            user_message: User's message content
            selected_text: Optional selected text for context
            selected_text_metadata: Optional metadata for selected text

        Returns:
            Dictionary with user_message and assistant_message

        Raises:
            ValueError: If user_message is empty or too long
        """
        if not user_message or not user_message.strip():
            raise ValueError("user_message cannot be empty")

        if len(user_message) > 500:
            raise ValueError("user_message cannot exceed 500 characters")

        # Create user message
        user_msg = ChatMessage.create_user_message(
            conversation_id=conversation.id,
            content=user_message,
        )

        self.db_session.add(user_msg)

        # Generate AI response using agent service
        response = await self.agent_service.generate_response(
            question=user_message,
            selected_text=selected_text,
            selected_text_metadata=selected_text_metadata,
        )

        # Create assistant message
        assistant_msg = ChatMessage.create_assistant_message(
            conversation_id=conversation.id,
            content=response["content"],
            confidence_score=response["confidence_score"],
            source_references=response["source_references"],
        )

        self.db_session.add(assistant_msg)

        # Commit both messages
        await self.db_session.commit()
        await self.db_session.refresh(user_msg)
        await self.db_session.refresh(assistant_msg)

        return {
            "user_message": user_msg,
            "assistant_message": assistant_msg,
        }

    async def get_conversation(
        self,
        conversation_id: str,
        user_id: str,
    ) -> Optional[Conversation]:
        """
        Get a conversation by ID.

        Args:
            conversation_id: Conversation ID
            user_id: User ID (for authorization)

        Returns:
            Conversation or None if not found
        """
        result = await self.db_session.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_user_conversations(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Conversation]:
        """
        Get all conversations for a user.

        Args:
            user_id: User ID
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip

        Returns:
            List of conversations ordered by updated_at (most recent first)
        """
        result = await self.db_session.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )

        return result.scalars().all()

    async def get_conversation_messages(
        self,
        conversation_id: str,
        limit: int = 500,
        offset: int = 0,
    ) -> List[ChatMessage]:
        """
        Get messages for a conversation.

        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages to return
            offset: Number of messages to skip

        Returns:
            List of messages ordered by created_at (oldest first)
        """
        result = await self.db_session.execute(
            select(ChatMessage)
            .where(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
            .offset(offset)
        )

        return result.scalars().all()

    async def delete_conversation(
        self,
        conversation_id: str,
        user_id: str,
    ) -> bool:
        """
        Delete a conversation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID (for authorization)

        Returns:
            True if deleted, False if not found
        """
        conversation = await self.get_conversation(conversation_id, user_id)

        if not conversation:
            return False

        await self.db_session.delete(conversation)
        await self.db_session.commit()

        return True

    async def _save_user_message(
        self,
        conversation: Conversation,
        content: str,
    ) -> ChatMessage:
        """
        Save user message (helper for streaming).

        Args:
            conversation: Conversation to add message to
            content: Message content

        Returns:
            Created user message
        """
        user_msg = ChatMessage.create_user_message(
            conversation_id=conversation.id,
            content=content,
        )

        self.db_session.add(user_msg)
        await self.db_session.commit()
        await self.db_session.refresh(user_msg)

        return user_msg

    async def _save_assistant_message(
        self,
        conversation: Conversation,
        content: str,
        confidence_score: float,
        source_references: List[Dict[str, Any]],
    ) -> ChatMessage:
        """
        Save assistant message (helper for streaming).

        Args:
            conversation: Conversation to add message to
            content: Message content
            confidence_score: Confidence score
            source_references: Source references

        Returns:
            Created assistant message
        """
        assistant_msg = ChatMessage.create_assistant_message(
            conversation_id=conversation.id,
            content=content,
            confidence_score=confidence_score,
            source_references=source_references,
        )

        self.db_session.add(assistant_msg)
        await self.db_session.commit()
        await self.db_session.refresh(assistant_msg)

        return assistant_msg

    async def get_conversation_count(self, user_id: str) -> int:
        """
        Get number of conversations for a user.

        Args:
            user_id: User ID

        Returns:
            Number of conversations
        """
        result = await self.db_session.execute(
            select(Conversation).where(Conversation.user_id == user_id)
        )

        conversations = result.scalars().all()
        return len(conversations)
