"""
Chat API endpoints.

Provides REST API for chat conversations and messages.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from src.database import get_db
from src.services.chat_service import ChatService
from src.services.agent_service import agent_service
from src.tools.tool_registry import tool_registry
from src.middleware.error_handler import handle_validation_error
import logging

logger = logging.getLogger(__name__)


# Request/Response models
class CreateConversationRequest(BaseModel):
    """Request model for creating a conversation."""
    title: str = Field(..., min_length=1, max_length=100)


class SendMessageRequest(BaseModel):
    """Request model for sending a message."""
    content: str = Field(..., min_length=1, max_length=500)
    selected_text: Optional[str] = None
    selected_text_metadata: Optional[dict] = None


class ConversationResponse(BaseModel):
    """Response model for conversation."""
    id: str
    user_id: str
    title: str
    message_count: int
    created_at: str
    updated_at: str


class MessageResponse(BaseModel):
    """Response model for message."""
    id: str
    conversation_id: str
    content: str
    sender_type: str
    confidence_score: Optional[float] = None
    source_references: List[dict] = []
    created_at: str


class SendMessageResponse(BaseModel):
    """Response model for send message."""
    user_message: MessageResponse
    assistant_message: MessageResponse


# Router
router = APIRouter(prefix="/api/chat", tags=["chat"])


# Dependency to get current user (placeholder - will be implemented with Better-Auth)
async def get_current_user():
    """
    Get current authenticated user.

    TODO: Implement with Better-Auth JWT validation
    For now, returns mock user for testing.
    """
    # This will be replaced with actual JWT validation
    return {
        "id": "test-user-id",
        "email": "test@example.com",
    }


# Dependency to get chat service
async def get_chat_service(db: AsyncSession = Depends(get_db)) -> ChatService:
    """Get chat service instance."""
    # Register tools with agent service
    agent_service.register_tools(tool_registry.get_all_tools())

    return ChatService(db_session=db, agent_service=agent_service)


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    request: CreateConversationRequest,
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Create a new conversation.

    Args:
        request: Conversation creation request
        current_user: Authenticated user
        chat_service: Chat service instance

    Returns:
        Created conversation
    """
    try:
        conversation = await chat_service.create_conversation(
            user_id=current_user["id"],
            title=request.title,
        )

        return ConversationResponse(**conversation.to_dict())

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create conversation: {str(e)}",
        )


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Get user's conversations.

    Args:
        limit: Maximum number of conversations to return
        offset: Number of conversations to skip
        current_user: Authenticated user
        chat_service: Chat service instance

    Returns:
        List of conversations
    """
    try:
        conversations = await chat_service.get_user_conversations(
            user_id=current_user["id"],
            limit=limit,
            offset=offset,
        )

        return [ConversationResponse(**conv.to_dict()) for conv in conversations]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversations: {str(e)}",
        )


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Get a conversation by ID.

    Args:
        conversation_id: Conversation ID
        current_user: Authenticated user
        chat_service: Chat service instance

    Returns:
        Conversation details

    Raises:
        404: Conversation not found
    """
    conversation = await chat_service.get_conversation(
        conversation_id=conversation_id,
        user_id=current_user["id"],
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    return ConversationResponse(**conversation.to_dict())


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Delete a conversation.

    Args:
        conversation_id: Conversation ID
        current_user: Authenticated user
        chat_service: Chat service instance

    Raises:
        404: Conversation not found
    """
    deleted = await chat_service.delete_conversation(
        conversation_id=conversation_id,
        user_id=current_user["id"],
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: str,
    limit: int = 500,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Get messages for a conversation.

    Args:
        conversation_id: Conversation ID
        limit: Maximum number of messages to return
        offset: Number of messages to skip
        current_user: Authenticated user
        chat_service: Chat service instance

    Returns:
        List of messages

    Raises:
        404: Conversation not found
    """
    # Verify conversation exists and user has access
    conversation = await chat_service.get_conversation(
        conversation_id=conversation_id,
        user_id=current_user["id"],
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    messages = await chat_service.get_conversation_messages(
        conversation_id=conversation_id,
        limit=limit,
        offset=offset,
    )

    return [MessageResponse(**msg.to_dict()) for msg in messages]


@router.post("/conversations/{conversation_id}/messages", response_model=SendMessageResponse)
async def send_message(
    conversation_id: str,
    request: SendMessageRequest,
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Send a message to a conversation.

    Args:
        conversation_id: Conversation ID
        request: Message request
        current_user: Authenticated user
        chat_service: Chat service instance

    Returns:
        User message and AI response

    Raises:
        404: Conversation not found
        403: Unauthorized access to conversation
        400: Invalid message content
    """
    # Verify conversation exists and user has access
    conversation = await chat_service.get_conversation(
        conversation_id=conversation_id,
        user_id=current_user["id"],
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Verify user owns the conversation
    if conversation.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized access to conversation",
        )

    try:
        result = await chat_service.send_message(
            conversation=conversation,
            user_message=request.content,
            selected_text=request.selected_text,
            selected_text_metadata=request.selected_text_metadata,
        )

        return SendMessageResponse(
            user_message=MessageResponse(**result["user_message"].to_dict()),
            assistant_message=MessageResponse(**result["assistant_message"].to_dict()),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}",
        )
