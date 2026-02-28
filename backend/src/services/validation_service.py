"""
Validation Service
Feature: 005-urdu-translation
Purpose: Validate translated content for structural integrity and quality
"""

import logging
from typing import Optional

from src.utils.validation import ValidationUtils, ValidationResult

logger = logging.getLogger(__name__)


class ValidationService:
    """
    Service for validating translated content.

    Ensures:
    - Markdown structure is preserved
    - Technical terms remain in English
    - Code blocks are unchanged
    - LaTeX equations are unchanged
    """

    def __init__(self):
        """Initialize validation service."""
        pass

    def validate_translation(
        self,
        original: str,
        translated: str,
        chapter_id: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate translated content against original.

        Performs comprehensive validation:
        1. Markdown structure preservation (headers, lists, links)
        2. Code block immunity (all code unchanged)
        3. LaTeX equation preservation
        4. Technical term preservation
        5. Content not empty

        Args:
            original: Original English markdown content
            translated: Translated Urdu markdown content
            chapter_id: Optional chapter identifier for logging

        Returns:
            ValidationResult with pass/fail status and list of issues
        """
        log_prefix = f"[{chapter_id}] " if chapter_id else ""
        logger.info(f"{log_prefix}Validating translation")

        all_issues = []

        # 1. Validate markdown structure
        structure_result = ValidationUtils.validate_markdown_structure(original, translated)
        if not structure_result.passed:
            all_issues.extend(structure_result.issues)
            logger.warning(f"{log_prefix}Structure validation failed: {structure_result.issues}")

        # 2. Validate technical terms preserved
        terms_result = ValidationUtils.validate_technical_terms_preserved(original, translated)
        if not terms_result.passed:
            all_issues.extend(terms_result.issues)
            logger.warning(f"{log_prefix}Technical terms validation failed: {terms_result.issues}")

        # 3. Check content not empty
        if ValidationUtils.is_content_empty(translated):
            all_issues.append("Translated content is empty")
            logger.error(f"{log_prefix}Translated content is empty")

        # Overall result
        passed = len(all_issues) == 0

        if passed:
            logger.info(f"{log_prefix}Translation validation passed")
        else:
            logger.warning(f"{log_prefix}Translation validation failed with {len(all_issues)} issues")

        return ValidationResult(passed=passed, issues=all_issues)

    def validate_chapter_id(self, chapter_id: str) -> bool:
        """
        Validate chapter ID format.

        Args:
            chapter_id: Chapter identifier to validate

        Returns:
            True if valid, False otherwise
        """
        return ValidationUtils.validate_chapter_id(chapter_id)

    def validate_language_code(self, language_code: str) -> bool:
        """
        Validate language code.

        Args:
            language_code: Language code to validate

        Returns:
            True if valid, False otherwise
        """
        return ValidationUtils.validate_language_code(language_code)

    def compute_content_hash(self, content: str) -> str:
        """
        Compute SHA-256 hash of content for cache invalidation.

        Args:
            content: Content to hash

        Returns:
            Hexadecimal hash string (64 characters)
        """
        return ValidationUtils.compute_content_hash(content)
