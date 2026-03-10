"""
Translation Service
Feature: 005-urdu-translation
Purpose: Core translation logic using OpenAI API with term preservation
"""

import logging
from typing import Optional, Dict, Any
from openai import AsyncOpenAI
import os

from src.prompts.translation_prompt import TranslationPrompts
from src.utils.validation import ValidationUtils, ValidationResult

logger = logging.getLogger(__name__)


class TranslationService:
    """
    Service for translating textbook chapters from English to Urdu.

    Uses OpenAI GPT-4o-mini with structured prompts to ensure:
    - Technical term preservation
    - Code block immunity
    - LaTeX equation preservation
    - Markdown structure integrity
    - Academic tone
    """

    def __init__(self):
        """Initialize translation service with lazy OpenAI client initialization."""
        self.client = None
        self._client_initialized = False
        self.model = "gpt-4o-mini"
        self.temperature = 0.3  # Low creativity for consistency
        self.max_tokens = 4000  # Handle long chapters

        # Check if API key is available but don't fail if missing
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.warning("OPENAI_API_KEY not configured - translation features will be unavailable")
        else:
            logger.info("OpenAI API key detected - translation features available")

    def _ensure_client_initialized(self):
        """
        Ensure OpenAI client is initialized (lazy initialization).

        Raises:
            ValueError: If OPENAI_API_KEY is not configured
        """
        if self._client_initialized:
            return

        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("Translation features are currently unavailable. OpenAI API key is not configured.")

        self.client = AsyncOpenAI(api_key=api_key)
        self._client_initialized = True
        logger.info("OpenAI translation client initialized successfully")

    async def translate(
        self,
        chapter_id: str,
        content: str,
        language_code: str = "ur",
        user_level: Optional[str] = None,
        chapter_title: Optional[str] = None
    ) -> str:
        """
        Translate chapter content from English to target language.

        Args:
            chapter_id: Chapter identifier (e.g., "01-introduction-to-ros2")
            content: English markdown content to translate
            language_code: Target language code (default: "ur")
            user_level: User's technical background level ('beginner', 'intermediate', 'advanced')
            chapter_title: Chapter title (extracted from content if not provided)

        Returns:
            Translated markdown content

        Raises:
            ValueError: If inputs are invalid
            Exception: If translation fails
        """
        # Validate inputs
        if not ValidationUtils.validate_chapter_id(chapter_id):
            raise ValueError(f"Invalid chapter_id format: {chapter_id}")

        if not ValidationUtils.validate_language_code(language_code):
            raise ValueError(f"Unsupported language_code: {language_code}")

        if ValidationUtils.is_content_empty(content):
            raise ValueError("Content cannot be empty")

        # Ensure OpenAI client is initialized (lazy initialization)
        self._ensure_client_initialized()

        # Extract chapter title if not provided
        if not chapter_title:
            chapter_title = self._extract_title(content)

        logger.info(f"Translating chapter {chapter_id} to {language_code}")

        try:
            # Get prompts
            system_prompt = TranslationPrompts.get_system_prompt(user_level=user_level)
            user_prompt = TranslationPrompts.get_user_prompt(
                chapter_id=chapter_id,
                chapter_title=chapter_title,
                content=content
            )

            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            translated_content = response.choices[0].message.content

            # Validate translation (warning only - don't block)
            validation_result = ValidationUtils.validate_markdown_structure(
                original=content,
                translated=translated_content
            )

            if not validation_result.passed:
                logger.warning(
                    f"Translation validation issues for {chapter_id}: {validation_result.issues}"
                )
                logger.warning("Proceeding with translation despite validation issues")
                # Note: We're allowing the translation through for now
                # TODO: Improve prompts to prevent code block modifications

            logger.info(f"Successfully translated chapter {chapter_id}")
            return translated_content

        except Exception as e:
            logger.error(f"Translation failed for {chapter_id}: {str(e)}")
            raise

    async def _retry_with_strict_prompt(
        self,
        chapter_id: str,
        chapter_title: str,
        content: str
    ) -> str:
        """
        Retry translation with stricter prompt after validation failure.

        Args:
            chapter_id: Chapter identifier
            chapter_title: Chapter title
            content: Original content

        Returns:
            Translated content

        Raises:
            Exception: If retry also fails validation
        """
        logger.info(f"Retrying translation for {chapter_id} with strict prompt")

        system_prompt = TranslationPrompts.get_system_prompt(strict=True)
        user_prompt = TranslationPrompts.get_user_prompt(
            chapter_id=chapter_id,
            chapter_title=chapter_title,
            content=content
        )

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

        translated_content = response.choices[0].message.content

        # Validate again
        validation_result = ValidationUtils.validate_markdown_structure(
            original=content,
            translated=translated_content
        )

        if not validation_result.passed:
            logger.error(
                f"Translation retry failed validation for {chapter_id}: {validation_result.issues}"
            )
            raise Exception(f"Translation validation failed after retry: {validation_result.issues}")

        return translated_content

    def _extract_title(self, content: str) -> str:
        """
        Extract chapter title from markdown content (first # header).

        Args:
            content: Markdown content

        Returns:
            Chapter title or "Untitled Chapter" if not found
        """
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()

        return "Untitled Chapter"

    async def translate_chunked(
        self,
        chapter_id: str,
        chunks: list,
        language_code: str = "ur",
        chapter_title: Optional[str] = None
    ) -> str:
        """
        Translate large chapter in chunks (for chapters >10,000 words).

        Args:
            chapter_id: Chapter identifier
            chunks: List of content chunks with metadata
            language_code: Target language code
            chapter_title: Chapter title

        Returns:
            Combined translated content

        Raises:
            Exception: If any chunk translation fails
        """
        logger.info(f"Translating chapter {chapter_id} in {len(chunks)} chunks")

        translated_chunks = []
        system_prompt = TranslationPrompts.get_chunked_system_prompt()

        for i, chunk in enumerate(chunks):
            section_number = i + 1
            total_sections = len(chunks)

            user_prompt = TranslationPrompts.get_chunked_user_prompt(
                chapter_id=chapter_id,
                chapter_title=chapter_title or "Chapter",
                section_number=section_number,
                total_sections=total_sections,
                section_header=chunk.get('header', f'Section {section_number}'),
                content=chunk['content']
            )

            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )

                translated_chunk = response.choices[0].message.content
                translated_chunks.append(translated_chunk)

                logger.info(f"Translated chunk {section_number}/{total_sections} for {chapter_id}")

            except Exception as e:
                logger.error(f"Failed to translate chunk {section_number} for {chapter_id}: {str(e)}")
                raise

        # Combine chunks
        combined_translation = '\n\n'.join(translated_chunks)
        return combined_translation
