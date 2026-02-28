"""
Chunking Service
Feature: 005-urdu-translation
Purpose: Split large chapters into semantic chunks for translation
"""

import logging
import re
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class ChunkingService:
    """
    Service for chunking large chapters by markdown headers.

    For chapters >10,000 words, splits content by headers (## and ###)
    to maintain semantic context and improve translation quality.
    """

    def __init__(self, word_threshold: int = 10000):
        """
        Initialize chunking service.

        Args:
            word_threshold: Word count threshold for chunking (default: 10,000)
        """
        self.word_threshold = word_threshold

    def should_chunk(self, content: str) -> bool:
        """
        Determine if content should be chunked based on word count.

        Args:
            content: Markdown content

        Returns:
            True if content exceeds word threshold, False otherwise
        """
        word_count = self._count_words(content)
        should_chunk = word_count > self.word_threshold

        logger.info(f"Content has {word_count} words, chunking: {should_chunk}")
        return should_chunk

    def chunk_by_headers(self, content: str) -> List[Dict[str, Any]]:
        """
        Split markdown content by headers (## and ###).

        Each chunk contains one complete section with its header.
        Preserves document structure and semantic context.

        Args:
            content: Markdown content to chunk

        Returns:
            List of chunks, each with:
            - header: Section header text
            - level: Header level (2 or 3)
            - content: Section content including header
            - word_count: Approximate word count
            - section_number: 1-indexed section number
        """
        logger.info("Chunking content by headers")

        chunks = []
        lines = content.split('\n')
        current_chunk = []
        current_header = None
        current_level = None
        section_number = 0

        for line in lines:
            # Check if line is a header (## or ###)
            header_match = re.match(r'^(#{2,3})\s+(.+)$', line)

            if header_match:
                # Save previous chunk if exists
                if current_chunk:
                    chunk_content = '\n'.join(current_chunk)
                    chunks.append({
                        'header': current_header or 'Introduction',
                        'level': current_level or 2,
                        'content': chunk_content,
                        'word_count': self._count_words(chunk_content),
                        'section_number': section_number
                    })

                # Start new chunk
                section_number += 1
                current_level = len(header_match.group(1))
                current_header = header_match.group(2).strip()
                current_chunk = [line]
            else:
                current_chunk.append(line)

        # Add final chunk
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            chunks.append({
                'header': current_header or 'Conclusion',
                'level': current_level or 2,
                'content': chunk_content,
                'word_count': self._count_words(chunk_content),
                'section_number': section_number
            })

        logger.info(f"Created {len(chunks)} chunks")
        return chunks

    def _count_words(self, text: str) -> int:
        """
        Count approximate words in text.

        Args:
            text: Text to count words in

        Returns:
            Approximate word count
        """
        # Remove code blocks (don't count code as words)
        text_without_code = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text_without_code = re.sub(r'`[^`]+`', '', text_without_code)

        # Split by whitespace and count
        words = text_without_code.split()
        return len(words)

    def combine_chunks(self, translated_chunks: List[str]) -> str:
        """
        Combine translated chunks back into single document.

        Args:
            translated_chunks: List of translated chunk contents

        Returns:
            Combined markdown content
        """
        # Join chunks with double newline for proper spacing
        combined = '\n\n'.join(translated_chunks)

        logger.info(f"Combined {len(translated_chunks)} chunks into single document")
        return combined

    def get_chunk_summary(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get summary statistics for chunks.

        Args:
            chunks: List of chunks

        Returns:
            Dictionary with summary statistics
        """
        total_words = sum(chunk['word_count'] for chunk in chunks)
        avg_words = total_words // len(chunks) if chunks else 0

        return {
            'total_chunks': len(chunks),
            'total_words': total_words,
            'avg_words_per_chunk': avg_words,
            'min_words': min((chunk['word_count'] for chunk in chunks), default=0),
            'max_words': max((chunk['word_count'] for chunk in chunks), default=0)
        }
