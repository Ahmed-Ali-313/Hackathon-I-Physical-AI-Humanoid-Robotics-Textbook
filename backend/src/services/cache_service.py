"""
Cache service for frequent questions.

Implements in-memory caching with TTL and LRU eviction for RAG responses.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from collections import OrderedDict
import hashlib
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """
    In-memory cache service for RAG responses.

    Features:
    - TTL-based expiration (default: 1 hour)
    - LRU eviction when max size reached
    - Cache key based on question hash
    - Thread-safe operations
    """

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """
        Initialize cache service.

        Args:
            max_size: Maximum number of cached items (default: 1000)
            ttl_seconds: Time-to-live in seconds (default: 3600 = 1 hour)
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self.hits = 0
        self.misses = 0

        logger.info(f"Cache service initialized: max_size={max_size}, ttl={ttl_seconds}s")

    def _generate_key(self, question: str, selected_text: Optional[str] = None) -> str:
        """
        Generate cache key from question and optional selected text.

        Args:
            question: User question
            selected_text: Optional selected text for context

        Returns:
            Cache key (SHA256 hash)
        """
        # Normalize question (lowercase, strip whitespace)
        normalized = question.lower().strip()

        # Include selected text in key if provided
        if selected_text:
            normalized += f"|{selected_text.lower().strip()}"

        # Generate hash
        return hashlib.sha256(normalized.encode()).hexdigest()

    def get(self, question: str, selected_text: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get cached response for question.

        Args:
            question: User question
            selected_text: Optional selected text

        Returns:
            Cached response dict or None if not found/expired
        """
        key = self._generate_key(question, selected_text)

        # Check if key exists
        if key not in self.cache:
            self.misses += 1
            logger.debug(f"Cache miss: {question[:50]}...")
            return None

        # Get cached item
        item = self.cache[key]

        # Check if expired
        if datetime.now() > item['expires_at']:
            # Remove expired item
            del self.cache[key]
            self.misses += 1
            logger.debug(f"Cache expired: {question[:50]}...")
            return None

        # Move to end (LRU)
        self.cache.move_to_end(key)

        self.hits += 1
        logger.debug(f"Cache hit: {question[:50]}...")

        return item['response']

    def set(
        self,
        question: str,
        response: Dict[str, Any],
        selected_text: Optional[str] = None
    ):
        """
        Cache response for question.

        Args:
            question: User question
            response: Response dict to cache
            selected_text: Optional selected text
        """
        key = self._generate_key(question, selected_text)

        # Check if cache is full
        if len(self.cache) >= self.max_size and key not in self.cache:
            # Remove oldest item (LRU)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            logger.debug(f"Cache eviction (LRU): removed oldest item")

        # Calculate expiration time
        expires_at = datetime.now() + timedelta(seconds=self.ttl_seconds)

        # Store in cache
        self.cache[key] = {
            'response': response,
            'cached_at': datetime.now(),
            'expires_at': expires_at,
            'question': question[:100]  # Store truncated question for debugging
        }

        logger.debug(f"Cache set: {question[:50]}... (expires in {self.ttl_seconds}s)")

    def clear(self):
        """Clear all cached items."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        logger.info("Cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict with cache stats (size, hits, misses, hit_rate)
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'total_requests': total_requests,
            'hit_rate_percent': round(hit_rate, 2),
            'ttl_seconds': self.ttl_seconds
        }

    def cleanup_expired(self):
        """Remove all expired items from cache."""
        now = datetime.now()
        expired_keys = [
            key for key, item in self.cache.items()
            if now > item['expires_at']
        ]

        for key in expired_keys:
            del self.cache[key]

        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache items")


# Global cache service instance
cache_service = CacheService(max_size=1000, ttl_seconds=3600)
