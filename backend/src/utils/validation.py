"""
Validation Utilities
Feature: 005-urdu-translation
Purpose: Validation functions for translation quality and structural integrity
"""

import re
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of translation validation."""
    passed: bool
    issues: List[str]

    def __bool__(self):
        """Allow using ValidationResult in boolean context."""
        return self.passed


class ValidationUtils:
    """Utilities for validating translated content."""

    @staticmethod
    def validate_chapter_id(chapter_id: str) -> bool:
        """
        Validate chapter ID format.

        Args:
            chapter_id: Chapter identifier (e.g., "01-introduction-to-ros2")

        Returns:
            True if valid, False otherwise
        """
        pattern = r'^\d{2}-[a-z0-9-]+$'
        return bool(re.match(pattern, chapter_id))

    @staticmethod
    def validate_language_code(language_code: str) -> bool:
        """
        Validate language code.

        Args:
            language_code: Language code (e.g., "ur", "en")

        Returns:
            True if valid, False otherwise
        """
        return language_code in ['en', 'ur']

    @staticmethod
    def validate_hash(hash_string: str) -> bool:
        """
        Validate SHA-256 hash format.

        Args:
            hash_string: Hash string to validate

        Returns:
            True if valid SHA-256 hash, False otherwise
        """
        pattern = r'^[a-f0-9]{64}$'
        return bool(re.match(pattern, hash_string))

    @staticmethod
    def count_headers(markdown: str) -> Dict[str, int]:
        """
        Count markdown headers by level.

        Args:
            markdown: Markdown content

        Returns:
            Dictionary with header counts by level (e.g., {'h1': 1, 'h2': 5, 'h3': 10})
        """
        counts = {'h1': 0, 'h2': 0, 'h3': 0, 'h4': 0, 'h5': 0, 'h6': 0}

        # Match headers at start of line
        for line in markdown.split('\n'):
            line = line.strip()
            if line.startswith('# '):
                counts['h1'] += 1
            elif line.startswith('## '):
                counts['h2'] += 1
            elif line.startswith('### '):
                counts['h3'] += 1
            elif line.startswith('#### '):
                counts['h4'] += 1
            elif line.startswith('##### '):
                counts['h5'] += 1
            elif line.startswith('###### '):
                counts['h6'] += 1

        return counts

    @staticmethod
    def extract_code_blocks(markdown: str) -> List[str]:
        """
        Extract all code blocks from markdown.

        Args:
            markdown: Markdown content

        Returns:
            List of code block contents (including fenced and inline code)
        """
        code_blocks = []

        # Extract fenced code blocks (```language\ncode\n```)
        fenced_pattern = r'```[\w]*\n(.*?)```'
        fenced_blocks = re.findall(fenced_pattern, markdown, re.DOTALL)
        code_blocks.extend(fenced_blocks)

        # Extract inline code (`code`)
        inline_pattern = r'`([^`]+)`'
        inline_blocks = re.findall(inline_pattern, markdown)
        code_blocks.extend(inline_blocks)

        return code_blocks

    @staticmethod
    def extract_latex(markdown: str) -> List[str]:
        """
        Extract all LaTeX equations from markdown.

        Args:
            markdown: Markdown content

        Returns:
            List of LaTeX equation contents
        """
        latex_equations = []

        # Extract display math ($$...$$)
        display_pattern = r'\$\$(.*?)\$\$'
        display_equations = re.findall(display_pattern, markdown, re.DOTALL)
        latex_equations.extend(display_equations)

        # Extract inline math ($...$)
        inline_pattern = r'\$([^\$]+)\$'
        inline_equations = re.findall(inline_pattern, markdown)
        latex_equations.extend(inline_equations)

        return latex_equations

    @staticmethod
    def validate_markdown_structure(original: str, translated: str) -> ValidationResult:
        """
        Validate that translated markdown preserves structural elements.

        Checks:
        - Header count matches
        - Code blocks are preserved
        - LaTeX equations are preserved
        - Markdown can be parsed

        Args:
            original: Original English markdown
            translated: Translated Urdu markdown

        Returns:
            ValidationResult with pass/fail and specific issues
        """
        issues = []

        # Check header count
        original_headers = ValidationUtils.count_headers(original)
        translated_headers = ValidationUtils.count_headers(translated)

        for level, count in original_headers.items():
            if translated_headers[level] != count:
                issues.append(
                    f"Header count mismatch for {level}: "
                    f"original has {count}, translated has {translated_headers[level]}"
                )

        # Check code blocks
        original_code = ValidationUtils.extract_code_blocks(original)
        translated_code = ValidationUtils.extract_code_blocks(translated)

        if len(original_code) != len(translated_code):
            issues.append(
                f"Code block count mismatch: "
                f"original has {len(original_code)}, translated has {len(translated_code)}"
            )
        else:
            # Verify code blocks are unchanged
            for i, (orig, trans) in enumerate(zip(original_code, translated_code)):
                if orig.strip() != trans.strip():
                    issues.append(f"Code block {i+1} was modified")

        # Check LaTeX equations
        original_latex = ValidationUtils.extract_latex(original)
        translated_latex = ValidationUtils.extract_latex(translated)

        if len(original_latex) != len(translated_latex):
            issues.append(
                f"LaTeX equation count mismatch: "
                f"original has {len(original_latex)}, translated has {len(translated_latex)}"
            )
        else:
            # Verify equations are unchanged
            for i, (orig, trans) in enumerate(zip(original_latex, translated_latex)):
                if orig.strip() != trans.strip():
                    issues.append(f"LaTeX equation {i+1} was modified")

        # Check if translated markdown is valid (basic check)
        if not translated.strip():
            issues.append("Translated content is empty")

        return ValidationResult(
            passed=len(issues) == 0,
            issues=issues
        )

    @staticmethod
    def validate_technical_terms_preserved(original: str, translated: str) -> ValidationResult:
        """
        Validate that technical terms are preserved in English.

        Args:
            original: Original English markdown
            translated: Translated Urdu markdown

        Returns:
            ValidationResult with pass/fail and specific issues
        """
        issues = []

        # List of technical terms that must be preserved
        technical_terms = [
            'ROS 2', 'VSLAM', 'URDF', 'Kinematics', 'SLAM',
            'Isaac Sim', 'Gazebo', 'RViz', 'MoveIt',
            'Jetson Nano', 'Jetson Orin', 'Raspberry Pi',
            'MQTT', 'DDS', 'TCP/IP',
            'Python', 'C++', 'JavaScript',
            'FastAPI', 'React', 'Docusaurus'
        ]

        # Check if technical terms in original are present in translation
        for term in technical_terms:
            if term in original and term not in translated:
                issues.append(f"Technical term '{term}' was translated or removed")

        return ValidationResult(
            passed=len(issues) == 0,
            issues=issues
        )

    @staticmethod
    def compute_content_hash(content: str) -> str:
        """
        Compute SHA-256 hash of content for cache invalidation.

        Args:
            content: Content to hash

        Returns:
            Hexadecimal hash string (64 characters)
        """
        import hashlib
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    @staticmethod
    def is_content_empty(content: str) -> bool:
        """
        Check if content is empty or whitespace only.

        Args:
            content: Content to check

        Returns:
            True if empty, False otherwise
        """
        return not content or not content.strip()
