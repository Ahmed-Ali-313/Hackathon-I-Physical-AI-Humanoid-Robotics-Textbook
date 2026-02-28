"""
Unit Tests for TranslationService
Feature: 005-urdu-translation
Purpose: Test translation logic, term preservation, and validation
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.services.translation_service import TranslationService


@pytest.fixture
def translation_service():
    """Create TranslationService instance for testing."""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        return TranslationService()


@pytest.mark.asyncio
async def test_translate_preserves_technical_terms(translation_service):
    """Test that technical terms remain in English (T012, T013)."""
    # Arrange
    chapter_id = "01-test-chapter"
    content = "ROS 2 is a robotics middleware. VSLAM is used for localization."

    # Mock OpenAI response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "ROS 2 ایک robotics middleware ہے۔ VSLAM localization کے لیے استعمال ہوتا ہے۔"

    with patch.object(translation_service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response

        # Act
        result = await translation_service.translate(
            chapter_id=chapter_id,
            content=content,
            language_code="ur"
        )

        # Assert
        assert "ROS 2" in result, "ROS 2 should be preserved in English"
        assert "VSLAM" in result, "VSLAM should be preserved in English"
        assert "robotics middleware" in result, "Technical terms should be preserved"


@pytest.mark.asyncio
async def test_translate_code_block_immunity(translation_service):
    """Test that code blocks remain unchanged (T014)."""
    # Arrange
    chapter_id = "01-test-chapter"
    content = """
# Introduction

Here is some code:

```python
def hello():
    print("Hello World")
```

This is a Python function.
"""

    # Mock OpenAI response with code block preserved
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = """
# تعارف

یہاں کچھ code ہے:

```python
def hello():
    print("Hello World")
```

یہ ایک Python function ہے۔
"""

    with patch.object(translation_service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response

        # Act
        result = await translation_service.translate(
            chapter_id=chapter_id,
            content=content,
            language_code="ur"
        )

        # Assert
        assert '```python' in result, "Code fence should be preserved"
        assert 'def hello():' in result, "Code content should be unchanged"
        assert 'print("Hello World")' in result, "Code should be exactly the same"


@pytest.mark.asyncio
async def test_translate_latex_preservation(translation_service):
    """Test that LaTeX equations remain unchanged (T015)."""
    # Arrange
    chapter_id = "01-test-chapter"
    content = "The equation is $E = mc^2$ and the formula is $$\\int_0^1 x^2 dx$$"

    # Mock OpenAI response with LaTeX preserved
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "مساوات $E = mc^2$ ہے اور فارمولا $$\\int_0^1 x^2 dx$$ ہے"

    with patch.object(translation_service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response

        # Act
        result = await translation_service.translate(
            chapter_id=chapter_id,
            content=content,
            language_code="ur"
        )

        # Assert
        assert '$E = mc^2$' in result, "Inline LaTeX should be preserved"
        assert '$$\\int_0^1 x^2 dx$$' in result, "Display LaTeX should be preserved"


@pytest.mark.asyncio
async def test_translate_markdown_structure_preservation(translation_service):
    """Test that markdown structure is preserved (T016)."""
    # Arrange
    chapter_id = "01-test-chapter"
    content = """
# Main Header

## Subheader

- List item 1
- List item 2

**Bold text** and *italic text*

[Link text](https://example.com)
"""

    # Mock OpenAI response with structure preserved
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = """
# مرکزی عنوان

## ذیلی عنوان

- فہرست آئٹم 1
- فہرست آئٹم 2

**بولڈ متن** اور *ترچھا متن*

[لنک متن](https://example.com)
"""

    with patch.object(translation_service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response

        # Act
        result = await translation_service.translate(
            chapter_id=chapter_id,
            content=content,
            language_code="ur"
        )

        # Assert
        assert result.count('# ') == 1, "Should have 1 H1 header"
        assert result.count('## ') == 1, "Should have 1 H2 header"
        assert result.count('- ') == 2, "Should have 2 list items"
        assert '**' in result, "Bold markdown should be preserved"
        assert '*' in result, "Italic markdown should be preserved"
        assert '[' in result and '](' in result, "Link markdown should be preserved"


@pytest.mark.asyncio
async def test_translate_invalid_chapter_id(translation_service):
    """Test that invalid chapter_id raises ValueError."""
    # Arrange
    invalid_chapter_id = "invalid-format"
    content = "Test content"

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid chapter_id format"):
        await translation_service.translate(
            chapter_id=invalid_chapter_id,
            content=content,
            language_code="ur"
        )


@pytest.mark.asyncio
async def test_translate_empty_content(translation_service):
    """Test that empty content raises ValueError."""
    # Arrange
    chapter_id = "01-test-chapter"
    content = ""

    # Act & Assert
    with pytest.raises(ValueError, match="Content cannot be empty"):
        await translation_service.translate(
            chapter_id=chapter_id,
            content=content,
            language_code="ur"
        )


@pytest.mark.asyncio
async def test_translate_unsupported_language(translation_service):
    """Test that unsupported language raises ValueError."""
    # Arrange
    chapter_id = "01-test-chapter"
    content = "Test content"

    # Act & Assert
    with pytest.raises(ValueError, match="Unsupported language_code"):
        await translation_service.translate(
            chapter_id=chapter_id,
            content=content,
            language_code="fr"  # French not supported
        )


@pytest.mark.asyncio
async def test_translate_with_user_level(translation_service):
    """Test translation with user level (beginner/advanced)."""
    # Arrange
    chapter_id = "01-test-chapter"
    content = "ROS 2 is a robotics middleware."

    # Mock OpenAI response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "ROS 2 ایک robotics middleware ہے (یہ ایک سافٹ ویئر ہے جو robots کو کنٹرول کرتا ہے)"

    with patch.object(translation_service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response

        # Act
        result = await translation_service.translate(
            chapter_id=chapter_id,
            content=content,
            language_code="ur",
            user_level="beginner"
        )

        # Assert
        assert result is not None
        # Verify that beginner prompt was used
        call_args = mock_create.call_args
        system_message = call_args[1]['messages'][0]['content']
        assert 'beginner' in system_message.lower() or 'SIMPLIFY' in system_message


@pytest.mark.asyncio
async def test_translate_chunked_large_chapter(translation_service):
    """Test chunked translation for large chapters."""
    # Arrange
    chapter_id = "01-test-chapter"
    chunks = [
        {'header': 'Section 1', 'content': 'Content 1'},
        {'header': 'Section 2', 'content': 'Content 2'}
    ]

    # Mock OpenAI responses
    mock_response_1 = MagicMock()
    mock_response_1.choices = [MagicMock()]
    mock_response_1.choices[0].message.content = "مواد 1"

    mock_response_2 = MagicMock()
    mock_response_2.choices = [MagicMock()]
    mock_response_2.choices[0].message.content = "مواد 2"

    with patch.object(translation_service.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = [mock_response_1, mock_response_2]

        # Act
        result = await translation_service.translate_chunked(
            chapter_id=chapter_id,
            chunks=chunks,
            language_code="ur"
        )

        # Assert
        assert "مواد 1" in result
        assert "مواد 2" in result
        assert mock_create.call_count == 2, "Should call OpenAI twice for 2 chunks"
