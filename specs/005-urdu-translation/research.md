# Research: Urdu Translation Technical Decisions

**Feature**: 005-urdu-translation
**Date**: 2026-02-28
**Purpose**: Document technical research and decisions made during planning phase

## Overview

This document captures all technical research, decisions, rationales, and alternatives considered for the Urdu Translation feature. All NEEDS CLARIFICATION markers from the Technical Context have been resolved.

---

## 1. OpenAI Translation Prompt Engineering

### Decision

Use GPT-4o-mini with structured system prompt for technical translation.

### Rationale

- **Cost-Effective**: GPT-4o-mini costs $0.15/1M input tokens and $0.60/1M output tokens (vs GPT-4o at $2.50/$10.00)
- **Quality**: Sufficient quality for technical translation with proper prompting
- **Context-Aware**: Can understand Physical AI & Humanoid Robotics domain with system prompt
- **Control**: Structured prompt ensures technical term preservation and academic tone
- **Estimated Cost**: ~$0.01-0.03 per chapter translation (5,000 words average)

### Prompt Template

```
System: You are a technical translator specializing in Physical AI and Humanoid Robotics education. Translate the following English textbook content to Urdu while strictly following these rules:

1. PRESERVE ALL TECHNICAL TERMS IN ENGLISH: ROS 2, VSLAM, URDF, Kinematics, SLAM, Isaac Sim, Gazebo, RViz, MoveIt, Jetson Nano, Jetson Orin, Raspberry Pi, MQTT, DDS, TCP/IP, Python, C++, JavaScript, FastAPI, React, Docusaurus, and all similar technical terms.

2. DO NOT TRANSLATE CODE BLOCKS: Keep all fenced code blocks (```python, ```cpp, ```bash) and inline code (`code`) exactly as they are.

3. DO NOT TRANSLATE LATEX EQUATIONS: Keep all mathematical equations and symbols unchanged.

4. PRESERVE MARKDOWN STRUCTURE: Maintain all headers (#, ##, ###), lists (*, -, 1., 2.), links ([text](url)), images (![alt](path)), bold (**text**), and italic (*text*).

5. MAINTAIN ACADEMIC TONE: Use formal, university-level Urdu suitable for technical education. Avoid casual language.

6. CONTEXT: This is a textbook for Panaversity's Physical AI & Humanoid Robotics course.

User: [English chapter content]
```

### Alternatives Considered

| Alternative | Pros | Cons | Reason Rejected |
|-------------|------|------|-----------------|
| GPT-4o | Higher quality, better context understanding | 10x more expensive ($2.50/$10.00 per 1M tokens) | Cost not justified for this use case; GPT-4o-mini quality sufficient |
| Google Translate API | Cheaper ($20/1M characters) | Lacks context awareness, poor technical term handling, no fine-grained control | Cannot preserve technical terms reliably |
| DeepL API | Good quality, competitive pricing | No fine-grained control over term preservation, limited language pairs | Cannot guarantee technical term preservation |
| Custom fine-tuned model | Perfect control, potentially better quality | High upfront cost, requires training data, maintenance overhead | Not justified for single language pair |

### Implementation Notes

- Use OpenAI Python SDK with async support
- Set `temperature=0.3` for consistent translations (low creativity, high consistency)
- Set `max_tokens=4000` to handle long chapters
- Include chapter title in prompt for additional context
- Retry with stricter prompt if validation fails

---

## 2. Semantic Chunking Strategy

### Decision

Chunk by markdown headers (##, ###) for chapters exceeding 10,000 words.

### Rationale

- **Context Preservation**: Complete sections translated together maintain semantic coherence
- **Natural Boundaries**: Headers provide logical break points that preserve document structure
- **Progress Tracking**: Easy to show progress (e.g., "Translating section 3 of 8... 38% complete")
- **Translation Quality**: Better quality than arbitrary word-count chunking
- **Reassembly**: Simple to reassemble sections in correct order

### Implementation Approach

```python
def chunk_by_headers(markdown_content: str) -> List[Chunk]:
    """
    Split markdown content by headers (## and ###).
    Each chunk contains one complete section with its header.

    Returns:
        List of Chunk objects with:
        - section_number: int
        - header_level: int (2 or 3)
        - header_text: str
        - content: str (including header)
    """
    import re

    # Regex to match headers: ## or ###
    header_pattern = r'^(#{2,3})\s+(.+)$'

    chunks = []
    current_chunk = []
    section_number = 0

    for line in markdown_content.split('\n'):
        match = re.match(header_pattern, line)
        if match and current_chunk:
            # Save previous chunk
            chunks.append(Chunk(
                section_number=section_number,
                header_level=len(match.group(1)),
                header_text=match.group(2),
                content='\n'.join(current_chunk)
            ))
            section_number += 1
            current_chunk = [line]
        else:
            current_chunk.append(line)

    # Save last chunk
    if current_chunk:
        chunks.append(Chunk(
            section_number=section_number,
            content='\n'.join(current_chunk)
        ))

    return chunks
```

### Alternatives Considered

| Alternative | Pros | Cons | Reason Rejected |
|-------------|------|------|-----------------|
| Fixed word count (2000 words) | Simple implementation, predictable chunk sizes | May break mid-sentence or mid-paragraph, loses context | Poor translation quality due to context loss |
| Paragraph-based chunking | Maintains paragraph integrity | Too many chunks, more API calls, higher cost, loses section context | Inefficient and expensive |
| No chunking | Simplest implementation, no reassembly needed | May timeout on very large chapters (>10,000 words), single point of failure | Risk of timeout and poor error recovery |
| Sentence-based chunking | Finest granularity | Extremely high API call count, very expensive, loses all context | Completely impractical |

### Edge Cases Handled

- **No headers**: Treat entire chapter as single chunk
- **Nested headers**: Respect hierarchy (## and ### both trigger new chunks)
- **Very long sections**: If single section >10,000 words, fall back to paragraph chunking for that section only
- **Progress tracking**: Calculate percentage based on section count (section N of M)

---

## 3. Optimistic Locking for Concurrent Translations

### Decision

Use version field in `translated_chapters` table for optimistic locking.

### Rationale

- **No Lock Contention**: Avoids holding database locks during long-running OpenAI API calls (3-5 seconds)
- **Performance**: No blocking, no timeouts, no deadlocks
- **Rare Conflicts**: Most chapters translated once and cached; race conditions are rare
- **Simple Recovery**: If conflict occurs, second request simply uses cached result from first request
- **Scalability**: Supports high concurrency without database bottlenecks

### Implementation Approach

```python
async def get_or_create_translation(
    db: AsyncSession,
    chapter_id: str,
    language_code: str,
    translate_fn: Callable
) -> str:
    """
    Get cached translation or create new one with optimistic locking.
    """
    # Check if translation exists
    existing = await db.execute(
        select(TranslatedChapter).where(
            TranslatedChapter.chapter_id == chapter_id,
            TranslatedChapter.language_code == language_code
        )
    )
    existing_translation = existing.scalar_one_or_none()

    if existing_translation:
        # Check if stale (>30 days old)
        if (datetime.utcnow() - existing_translation.updated_at).days < 30:
            return existing_translation.translated_content

    # Create placeholder entry with version 1
    new_translation = TranslatedChapter(
        chapter_id=chapter_id,
        language_code=language_code,
        translated_content="",  # Placeholder
        original_hash="",  # Will be updated
        version=1
    )
    db.add(new_translation)

    try:
        await db.commit()
    except IntegrityError:
        # Another request created entry first, retrieve it
        await db.rollback()
        existing = await db.execute(
            select(TranslatedChapter).where(
                TranslatedChapter.chapter_id == chapter_id,
                TranslatedChapter.language_code == language_code
            )
        )
        return existing.scalar_one().translated_content

    # Perform translation (long-running, outside transaction)
    translated_content = await translate_fn()
    content_hash = hashlib.sha256(translated_content.encode()).hexdigest()

    # Update with actual content (check version to detect conflicts)
    result = await db.execute(
        update(TranslatedChapter)
        .where(
            TranslatedChapter.chapter_id == chapter_id,
            TranslatedChapter.language_code == language_code,
            TranslatedChapter.version == 1
        )
        .values(
            translated_content=translated_content,
            original_hash=content_hash,
            version=2,
            updated_at=datetime.utcnow()
        )
    )
    await db.commit()

    if result.rowcount == 0:
        # Conflict: another request completed first
        # Retrieve the cached result
        existing = await db.execute(
            select(TranslatedChapter).where(
                TranslatedChapter.chapter_id == chapter_id,
                TranslatedChapter.language_code == language_code
            )
        )
        return existing.scalar_one().translated_content

    return translated_content
```

### Alternatives Considered

| Alternative | Pros | Cons | Reason Rejected |
|-------------|------|------|-----------------|
| Pessimistic locking (row-level lock) | Guaranteed no conflicts | Holds lock for entire API call (3-5s), causes contention and timeouts | Unacceptable performance impact |
| Advisory locks (application-level) | More flexible than row locks | Complex implementation, requires custom lock management, error-prone | Unnecessary complexity |
| No locking | Simplest implementation | Wastes API costs on race conditions (duplicate translations) | Cost inefficiency |
| Distributed locks (Redis) | Works across multiple servers | Requires Redis, adds infrastructure complexity | Overkill for this use case |

### Edge Cases Handled

- **Simultaneous requests**: Second request waits for first to complete, then retrieves cached result
- **Failed translation**: Placeholder entry deleted or marked as failed, allows retry
- **Stale cache**: Version field allows detecting and updating stale entries

---

## 4. Structural Validation Criteria

### Decision

Validate header count, code blocks, LaTeX equations, and markdown parsing.

### Rationale

- **Critical Issues Only**: Catches issues that would break page rendering or lose important content
- **Fast Performance**: Validation completes in <100ms, acceptable overhead
- **Balance**: Thorough enough to catch real problems, not so strict that it rejects valid translations
- **Automated**: Can run on every translation without manual review

### Validation Checks

1. **Header Count Validation**
   - Count headers (##, ###) in original and translation
   - Verify counts match exactly
   - Rationale: Missing headers indicate structural damage

2. **Code Block Validation**
   - Extract all fenced code blocks (```python, ```cpp, ```bash)
   - Extract all inline code (`code`)
   - Verify all blocks present and content unchanged
   - Rationale: Code must be executable, any change breaks functionality

3. **LaTeX Equation Validation**
   - Extract all LaTeX equations ($...$, $$...$$)
   - Verify all equations present and content unchanged
   - Rationale: Mathematical accuracy is critical

4. **Markdown Parsing Validation**
   - Parse translated markdown using markdown parser
   - Verify no parsing errors
   - Rationale: Ensures Docusaurus can render the content

### Implementation Approach

```python
from typing import List, Tuple
import re
import markdown

class ValidationResult:
    def __init__(self, passed: bool, issues: List[str]):
        self.passed = passed
        self.issues = issues

def validate_translation(original: str, translated: str) -> ValidationResult:
    """
    Validate translated markdown against original.
    Returns ValidationResult with pass/fail and specific issues.
    """
    issues = []

    # 1. Check header count
    original_headers = re.findall(r'^#{2,3}\s+.+$', original, re.MULTILINE)
    translated_headers = re.findall(r'^#{2,3}\s+.+$', translated, re.MULTILINE)
    if len(original_headers) != len(translated_headers):
        issues.append(
            f"Header count mismatch: {len(original_headers)} vs {len(translated_headers)}"
        )

    # 2. Check code blocks
    original_code_blocks = re.findall(r'```[\s\S]*?```', original)
    translated_code_blocks = re.findall(r'```[\s\S]*?```', translated)
    if original_code_blocks != translated_code_blocks:
        issues.append("Code blocks changed or missing")

    # 3. Check inline code
    original_inline = re.findall(r'`[^`]+`', original)
    translated_inline = re.findall(r'`[^`]+`', translated)
    if len(original_inline) != len(translated_inline):
        issues.append(
            f"Inline code count mismatch: {len(original_inline)} vs {len(translated_inline)}"
        )

    # 4. Check LaTeX equations
    original_latex = re.findall(r'\$\$?[^\$]+\$\$?', original)
    translated_latex = re.findall(r'\$\$?[^\$]+\$\$?', translated)
    if original_latex != translated_latex:
        issues.append("LaTeX equations changed or missing")

    # 5. Check markdown parsing
    try:
        markdown.markdown(translated)
    except Exception as e:
        issues.append(f"Markdown parsing error: {str(e)}")

    return ValidationResult(
        passed=len(issues) == 0,
        issues=issues
    )
```

### Alternatives Considered

| Alternative | Pros | Cons | Reason Rejected |
|-------------|------|------|-----------------|
| Full content comparison | Most thorough, catches all changes | Too strict, translations naturally differ in word order and phrasing | Would reject valid translations |
| Minimal validation (parsing only) | Fastest, simplest | May miss critical issues like missing code blocks | Too risky |
| No validation | No overhead | Could cache broken translations | Unacceptable quality risk |
| Manual review | Highest quality assurance | Not scalable, slow, expensive | Impractical for automated system |

### Retry Strategy

If validation fails:
1. Log validation issues with chapter_id and error details
2. Retry translation with stricter prompt emphasizing preservation rules
3. If retry fails, log error and return English content to user
4. Do not cache failed translations

---

## 5. RTL Layout Implementation

### Decision

Use CSS `direction: rtl` with conditional class on content container.

### Rationale

- **Standard Approach**: CSS `direction` property is the standard way to handle RTL languages
- **Browser Support**: Works across all modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- **Selective Application**: Can apply RTL to content while keeping code blocks and LaTeX in LTR
- **Docusaurus Integration**: Works cleanly with Docusaurus theme without modifications
- **Performance**: Pure CSS, no JavaScript overhead

### Implementation Approach

```css
/* TranslationControl/styles.module.css */

/* RTL layout for Urdu content */
.contentUrdu {
  direction: rtl;
  text-align: right;
  font-family: 'Noto Nastaliq Urdu', 'Noto Sans Arabic', system-ui, sans-serif;
  line-height: 1.8;
  font-size: 18px;
  font-weight: 400;
}

/* Keep code blocks LTR */
.contentUrdu pre,
.contentUrdu code,
.contentUrdu pre code {
  direction: ltr;
  text-align: left;
  font-family: 'Courier New', monospace;
}

/* Keep LaTeX equations LTR */
.contentUrdu .math,
.contentUrdu .math-display,
.contentUrdu .math-inline {
  direction: ltr;
  text-align: left;
}

/* Keep URLs and file paths LTR */
.contentUrdu a[href^="http"],
.contentUrdu a[href^="/"],
.contentUrdu .filepath {
  direction: ltr;
}

/* Adjust list markers for RTL */
.contentUrdu ul,
.contentUrdu ol {
  padding-right: 2rem;
  padding-left: 0;
}

/* Headings in Urdu */
.contentUrdu h1,
.contentUrdu h2,
.contentUrdu h3,
.contentUrdu h4,
.contentUrdu h5,
.contentUrdu h6 {
  font-weight: 600;
  text-align: right;
}
```

### Alternatives Considered

| Alternative | Pros | Cons | Reason Rejected |
|-------------|------|------|-----------------|
| JavaScript-based text reversal | Full control over text direction | Complex, error-prone, poor performance, accessibility issues | Unnecessary complexity |
| Server-side RTL transformation | No client-side overhead | Requires duplicate HTML generation, harder to maintain | CSS handles it natively |
| Separate Urdu-specific components | Complete isolation | Code duplication, harder to maintain, more testing needed | Violates DRY principle |
| Unicode bidirectional algorithm | Standards-compliant | Already handled by CSS direction property | Redundant |

### Browser Compatibility

- Chrome 90+: Full support
- Firefox 88+: Full support
- Safari 14+: Full support
- Edge 90+: Full support
- Older browsers: Graceful degradation (LTR layout, still readable)

---

## 6. Font Loading Strategy

### Decision

Load Noto Nastaliq Urdu from Google Fonts CDN.

### Rationale

- **Reliability**: Google Fonts CDN has 99.9%+ uptime and global distribution
- **Traditional Script**: Noto Nastaliq Urdu is traditional Urdu script, preferred for readability
- **Fallback**: Noto Sans Arabic provides fallback if Nastaliq fails to load
- **No Self-Hosting**: Avoids complexity of self-hosting fonts and CDN management
- **Performance**: Google Fonts CDN is optimized for fast loading with HTTP/2 and compression

### Implementation Approach

```css
/* theme/fonts.css */

/* Import Noto Nastaliq Urdu and Noto Sans Arabic from Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;600&family=Noto+Sans+Arabic:wght@400;600&display=swap');

/* Font stack for Urdu content */
:root {
  --font-urdu: 'Noto Nastaliq Urdu', 'Noto Sans Arabic', system-ui, sans-serif;
}
```

### Font Specifications

- **Primary**: Noto Nastaliq Urdu
  - Weights: 400 (regular), 600 (semibold)
  - Style: Traditional Nastaliq script
  - Line height: 1.8 minimum (Nastaliq requires extra vertical space)
  - Font size: 18px (16px minimum)

- **Fallback**: Noto Sans Arabic
  - Weights: 400 (regular), 600 (semibold)
  - Style: Modern sans-serif
  - Used if Nastaliq fails to load

- **System Fallback**: system-ui, sans-serif
  - Used if both Google Fonts fail to load
  - Ensures content is always readable

### Alternatives Considered

| Alternative | Pros | Cons | Reason Rejected |
|-------------|------|------|-----------------|
| Self-hosted fonts | More control, no external dependency | Adds complexity, requires CDN setup, higher costs | Unnecessary complexity |
| System fonts only | No external dependency, fastest loading | Poor Urdu rendering, inconsistent across platforms | Unacceptable quality |
| Multiple font options | User choice, flexibility | Unnecessary complexity, most users prefer Nastaliq | Overkill |
| Adobe Fonts | High quality fonts | Requires subscription, less reliable than Google Fonts | Cost and reliability concerns |

### Performance Optimization

- Use `display=swap` parameter to prevent FOIT (Flash of Invisible Text)
- Load only required weights (400, 600) to minimize file size
- Google Fonts CDN automatically serves optimized formats (WOFF2, WOFF)

---

## Summary

All technical decisions have been researched and documented. Key decisions:

1. **Translation Engine**: OpenAI GPT-4o-mini with structured prompts
2. **Chunking**: Semantic chunking by markdown headers
3. **Concurrency**: Optimistic locking with version field
4. **Validation**: Structural validation (headers, code, LaTeX, parsing)
5. **RTL Layout**: CSS direction property with selective exceptions
6. **Fonts**: Google Fonts CDN (Noto Nastaliq Urdu + Noto Sans Arabic)

All alternatives considered and rejected with clear rationales. Ready to proceed to Phase 1 (Design & Contracts).
