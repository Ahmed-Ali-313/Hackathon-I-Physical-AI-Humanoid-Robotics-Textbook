"""
Unit Tests for ValidationService
Feature: 005-urdu-translation
Purpose: Test validation logic for translation quality
"""

import pytest
from src.services.validation_service import ValidationService


@pytest.fixture
def validation_service():
    """Create ValidationService instance for testing."""
    return ValidationService()


def test_validate_translation_success(validation_service):
    """Test successful validation (T017)."""
    # Arrange
    original = """
# Header 1

## Header 2

Some text with `code` and **bold**.

```python
print("test")
```

Math: $E = mc^2$
"""

    translated = """
# عنوان 1

## عنوان 2

کچھ متن `code` اور **بولڈ** کے ساتھ۔

```python
print("test")
```

ریاضی: $E = mc^2$
"""

    # Act
    result = validation_service.validate_translation(original, translated, "01-test")

    # Assert
    assert result.passed is True
    assert len(result.issues) == 0


def test_validate_translation_header_mismatch(validation_service):
    """Test validation fails when header count doesn't match."""
    # Arrange
    original = "# Header 1\n## Header 2\n### Header 3"
    translated = "# عنوان 1\n## عنوان 2"  # Missing H3

    # Act
    result = validation_service.validate_translation(original, translated)

    # Assert
    assert result.passed is False
    assert any('Header count mismatch' in issue for issue in result.issues)


def test_validate_translation_code_block_changed(validation_service):
    """Test validation fails when code blocks are modified."""
    # Arrange
    original = "```python\nprint('hello')\n```"
    translated = "```python\nprint('مرحبا')\n```"  # Code changed!

    # Act
    result = validation_service.validate_translation(original, translated)

    # Assert
    assert result.passed is False
    assert any('Code block' in issue for issue in result.issues)


def test_validate_translation_latex_changed(validation_service):
    """Test validation fails when LaTeX is modified."""
    # Arrange
    original = "The equation is $E = mc^2$"
    translated = "مساوات $E = mc^3$ ہے"  # LaTeX changed!

    # Act
    result = validation_service.validate_translation(original, translated)

    # Assert
    assert result.passed is False
    assert any('LaTeX equation' in issue for issue in result.issues)


def test_validate_translation_empty_content(validation_service):
    """Test validation fails for empty translated content."""
    # Arrange
    original = "Some content"
    translated = ""

    # Act
    result = validation_service.validate_translation(original, translated)

    # Assert
    assert result.passed is False
    assert any('empty' in issue.lower() for issue in result.issues)


def test_validate_chapter_id_valid(validation_service):
    """Test valid chapter ID formats."""
    # Arrange & Act & Assert
    assert validation_service.validate_chapter_id("01-introduction") is True
    assert validation_service.validate_chapter_id("12-advanced-topics") is True
    assert validation_service.validate_chapter_id("05-ros2-basics") is True


def test_validate_chapter_id_invalid(validation_service):
    """Test invalid chapter ID formats."""
    # Arrange & Act & Assert
    assert validation_service.validate_chapter_id("1-intro") is False  # Single digit
    assert validation_service.validate_chapter_id("introduction") is False  # No number
    assert validation_service.validate_chapter_id("01_intro") is False  # Underscore
    assert validation_service.validate_chapter_id("01-Intro") is False  # Capital letter


def test_validate_language_code_valid(validation_service):
    """Test valid language codes."""
    # Arrange & Act & Assert
    assert validation_service.validate_language_code("en") is True
    assert validation_service.validate_language_code("ur") is True


def test_validate_language_code_invalid(validation_service):
    """Test invalid language codes."""
    # Arrange & Act & Assert
    assert validation_service.validate_language_code("fr") is False
    assert validation_service.validate_language_code("es") is False
    assert validation_service.validate_language_code("") is False


def test_compute_content_hash(validation_service):
    """Test SHA-256 hash computation."""
    # Arrange
    content = "Test content for hashing"

    # Act
    hash1 = validation_service.compute_content_hash(content)
    hash2 = validation_service.compute_content_hash(content)
    hash3 = validation_service.compute_content_hash("Different content")

    # Assert
    assert len(hash1) == 64, "SHA-256 hash should be 64 characters"
    assert hash1 == hash2, "Same content should produce same hash"
    assert hash1 != hash3, "Different content should produce different hash"
    assert all(c in '0123456789abcdef' for c in hash1), "Hash should be hexadecimal"


def test_validate_technical_terms_preserved(validation_service):
    """Test technical term preservation validation."""
    # Arrange
    original = "ROS 2 and VSLAM are used in robotics. Python and C++ are programming languages."
    translated_good = "ROS 2 اور VSLAM robotics میں استعمال ہوتے ہیں۔ Python اور C++ programming languages ہیں۔"
    translated_bad = "روس 2 اور وی ایس ایل اے ایم روبوٹکس میں استعمال ہوتے ہیں۔"  # Terms translated!

    # Act
    result_good = validation_service.validate_translation(original, translated_good)
    result_bad = validation_service.validate_translation(original, translated_bad)

    # Assert
    assert result_good.passed is True
    assert result_bad.passed is False
    assert any('Technical term' in issue for issue in result_bad.issues)
