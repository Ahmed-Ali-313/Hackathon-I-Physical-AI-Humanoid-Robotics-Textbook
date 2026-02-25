"""
Cleanup script for old conversations.

Deletes conversations older than 12 months (1 academic year) as per FR-020.
Should be run as a cron job.
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import async_session_maker
from src.models.conversation import Conversation
from src.models.chat_message import ChatMessage
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def cleanup_old_conversations(dry_run: bool = False):
    """
    Delete conversations older than 12 months.

    Args:
        dry_run: If True, only log what would be deleted without actually deleting

    Returns:
        Number of conversations deleted
    """
    # Calculate cutoff date (12 months ago)
    cutoff_date = datetime.utcnow() - timedelta(days=365)

    logger.info(f"Starting conversation cleanup (cutoff date: {cutoff_date})")
    logger.info(f"Dry run: {dry_run}")

    async with async_session_maker() as session:
        # Find old conversations
        result = await session.execute(
            select(Conversation).where(Conversation.updated_at < cutoff_date)
        )
        old_conversations = result.scalars().all()

        if not old_conversations:
            logger.info("No old conversations found")
            return 0

        logger.info(f"Found {len(old_conversations)} conversations to delete")

        if dry_run:
            for conv in old_conversations:
                logger.info(
                    f"Would delete: {conv.id} - {conv.title} "
                    f"(last updated: {conv.updated_at})"
                )
            return 0

        # Delete conversations (messages will be cascade deleted)
        deleted_count = 0
        for conv in old_conversations:
            logger.info(
                f"Deleting: {conv.id} - {conv.title} "
                f"(last updated: {conv.updated_at})"
            )
            await session.delete(conv)
            deleted_count += 1

        await session.commit()

        logger.info(f"Successfully deleted {deleted_count} conversations")
        return deleted_count


async def cleanup_inactive_sessions():
    """
    Mark sessions as inactive after 30 minutes of inactivity.
    Delete sessions older than 24 hours.
    """
    from src.models.chat_session import ChatSession

    # Mark inactive sessions
    inactive_cutoff = datetime.utcnow() - timedelta(minutes=30)
    delete_cutoff = datetime.utcnow() - timedelta(hours=24)

    logger.info("Cleaning up inactive sessions")

    async with async_session_maker() as session:
        # Mark sessions as inactive
        result = await session.execute(
            select(ChatSession).where(
                ChatSession.updated_at < inactive_cutoff,
                ChatSession.is_active == True
            )
        )
        inactive_sessions = result.scalars().all()

        for chat_session in inactive_sessions:
            chat_session.is_active = False
            logger.info(f"Marked session {chat_session.id} as inactive")

        # Delete old sessions
        result = await session.execute(
            select(ChatSession).where(ChatSession.updated_at < delete_cutoff)
        )
        old_sessions = result.scalars().all()

        for chat_session in old_sessions:
            await session.delete(chat_session)
            logger.info(f"Deleted old session {chat_session.id}")

        await session.commit()

        logger.info(
            f"Marked {len(inactive_sessions)} sessions as inactive, "
            f"deleted {len(old_sessions)} old sessions"
        )


async def main():
    """Main cleanup function."""
    import argparse

    parser = argparse.ArgumentParser(description="Cleanup old conversations and sessions")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting"
    )
    parser.add_argument(
        "--skip-sessions",
        action="store_true",
        help="Skip session cleanup"
    )

    args = parser.parse_args()

    try:
        # Cleanup old conversations
        deleted_count = await cleanup_old_conversations(dry_run=args.dry_run)

        # Cleanup inactive sessions
        if not args.skip_sessions and not args.dry_run:
            await cleanup_inactive_sessions()

        logger.info("Cleanup completed successfully")
        return 0

    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
