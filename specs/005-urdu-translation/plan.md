# Implementation Plan: Urdu Translation for Textbook Chapters

**Branch**: `005-urdu-translation` | **Date**: 2026-02-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-urdu-translation/spec.md`

## Summary

Implement a premium, authenticated feature that allows students to translate any textbook chapter from English to Urdu using OpenAI API. The system preserves technical terms in English, excludes code blocks and LaTeX equations from translation, applies RTL layout for Urdu content, and caches translations in PostgreSQL for performance. Language preference persists across sessions. Translation button appears only for authenticated users.

**Technical Approach**:
- Backend: FastAPI endpoint for translation with OpenAI GPT-4o-mini, PostgreSQL caching with optimistic locking, semantic chunking for large chapters
- Frontend: React component with RTL CSS, Noto Nastaliq Urdu font, state-based language toggle without page reload
- Performance: Cache-first strategy (80%+ hit rate target), <500ms cached responses, <5s first-time translation

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5.x (frontend)
**Primary Dependencies**:
- Backend: FastAPI, SQLAlchemy 2.x (async), OpenAI Python SDK, hashlib (content hashing)
- Frontend: React 18+, Docusaurus 3.x, Noto Nastaliq Urdu font (Google Fonts)

**Storage**: Neon Serverless Postgres (production), SQLite (development)
- Tables: `translated_chapters` (cache), `user_preferences` (language preference)
- Indexes: `(chapter_id, language_code)` for fast cache lookups

**Testing**:
- Backend: pytest with async support, pytest-asyncio
- Frontend: Playwright (E2E), Jest (unit tests)
- Test coverage: Unit (translation service, validation), Integration (API endpoints, database), E2E (full translation flow)

**Target Platform**:
- Backend: Linux server (Railway/Render)
- Frontend: Docusaurus static site (Vercel)
- Browsers: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+ (RTL layout support required)

**Project Type**: Web application (backend API + frontend React components)

**Performance Goals**:
- First-time translation: <5 seconds (per chapter)
- Cached translation: <500ms (p95)
- Cache hit rate: 80%+ after first week
- API cost reduction: 90%+ through caching
- Scroll position preservation: 100% (no jumping)

**Constraints**:
- Authentication required: Translation strictly for logged-in users only
- Technical term preservation: 100% of terms remain in English (verified by automated tests)
- Code block immunity: 100% of code blocks unchanged (verified by automated tests)
- RTL layout: Mandatory for Urdu content (CSS direction: rtl)
- Font requirements: Noto Nastaliq Urdu with line-height ≥1.8
- Cache validity: Must invalidate when content hash changes
- Browser compatibility: Modern browsers only (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)

**Scale/Scope**:
- Users: ~1,000 students (initial), 10,000+ (growth)
- Chapters: 17 chapters (current), expandable
- Translations: 17 cached translations (Urdu), shared across all users
- API calls: ~17 initial translations, then 90%+ cache hits
- Storage: ~500KB per translated chapter (estimated 8.5MB total for 17 chapters)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Principle I: Documentation-First Development
- **Status**: PASS
- **Evidence**: Specification complete (spec.md), clarifications resolved, plan in progress

### ✅ Principle II: Dependency Installation Before Implementation
- **Status**: PASS
- **Plan**: Dependencies identified in Technical Context, will be installed before implementation
- **Backend**: OpenAI SDK, SQLAlchemy async, pytest-asyncio
- **Frontend**: Noto Nastaliq Urdu font (Google Fonts CDN)

### ✅ Principle III: ALWAYS Use Test-Driven Development
- **Status**: PASS
- **Plan**: TDD approach mandatory for all implementation
- **Test Strategy**:
  - Unit tests: Translation service, validation logic, cache service
  - Integration tests: API endpoints, database operations, OpenAI API mocking
  - E2E tests: Full translation flow, RTL layout, preference persistence

### ✅ Principle IV: Incremental Development
- **Status**: PASS
- **Plan**: 5 user stories prioritized (P1-P4), each independently testable
- **Increments**: US1 (core translation) → US2 (preference persistence) → US3 (caching) → US4 (auth enforcement) → US5 (background-aware, optional)

### ✅ Principle V: Security & Privacy First
- **Status**: PASS
- **Authentication**: JWT-based (existing system), server-side validation on all translation API requests
- **Data Protection**: No PII in translations, chapter content only
- **API Security**: OpenAI API key in .env, not exposed to frontend

### ✅ Principle VI: Performance & Scalability
- **Status**: PASS
- **Targets Met**: <5s first-time, <500ms cached (within constitution targets)
- **Optimization**: Cache-first strategy, optimistic locking (no lock contention), semantic chunking for large chapters

### ✅ Principle VII: Accessibility (WCAG 2.1 AA)
- **Status**: PASS
- **Plan**:
  - Keyboard navigation: Tab to translate button, Enter to activate
  - Screen reader: ARIA labels on translate button ("Translate chapter to Urdu")
  - Color contrast: Button uses Docusaurus theme colors (4.5:1 ratio)
  - Focus indicators: Visible on translate button

### ✅ Principle VIII: Theme Consistency
- **Status**: PASS
- **Plan**: Use Docusaurus CSS variables for all colors, backgrounds, fonts
- **Dark Mode**: RTL layout works in both light and dark themes

### ✅ Principle IX: Error Handling & User Feedback
- **Status**: PASS
- **Plan**: User-friendly error messages, retry button, fallback to English on failure
- **Logging**: All translation errors logged with context (chapter_id, user_id, error_message, timestamp)

### ✅ Principle X: RAG Chatbot Architecture
- **Status**: N/A (not applicable to translation feature)

### ✅ Principle XI: User-Centric Translation Accessibility
- **Status**: PASS
- **Translation Trigger**: Button at start of each chapter (authenticated users only)
- **State Management**: Language preference stored in user profile, persists across sessions
- **Authentication Dependency**: Translation strictly for authenticated users

### ✅ Principle XII: Technical & Linguistic Fidelity
- **Status**: PASS
- **Term Preservation**: All technical terms remain in English (ROS 2, VSLAM, URDF, etc.)
- **Translation Engine**: OpenAI GPT-4o-mini with context-aware prompts
- **Contextual Accuracy**: Academic tone, Panaversity curriculum alignment

### ✅ Principle XIII: Structural Integrity (Markdown & Code)
- **Status**: PASS
- **Code Block Immunity**: All code blocks excluded from translation (fenced and inline)
- **Mathematical Preservation**: LaTeX equations remain untouched
- **Markdown Syntax**: Headers, lists, links, images preserved

### ✅ Principle XIV: Translation Performance & Caching
- **Status**: PASS
- **Database Integration**: `translated_chapters` table with (chapter_id, language_code) index
- **Inference Optimization**: Cache-first strategy, 30-day expiration, hash-based invalidation
- **Admin Invalidation**: API endpoint for manual cache clearing

### ✅ Principle XV: UI/UX & RTL Standards
- **Status**: PASS
- **Visual Direction**: RTL layout (direction: rtl) when Urdu active
- **Font Legibility**: Noto Nastaliq Urdu, line-height ≥1.8, 16px minimum
- **No Page Reload**: React state-based toggle, scroll position preserved

**Overall Constitution Compliance**: ✅ PASS - All applicable principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/005-urdu-translation/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   ├── api-contracts.md # Translation API endpoint specifications
│   └── prompts.md       # OpenAI translation prompt templates
├── checklists/          # Quality validation
│   └── requirements.md  # Specification quality checklist (complete)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── translated_chapter.py      # NEW: Translation cache model
│   │   └── user.py                     # MODIFY: Add preferred_language field
│   ├── services/
│   │   ├── translation_service.py      # NEW: Core translation logic
│   │   ├── cache_service.py            # NEW: Cache management with optimistic locking
│   │   ├── validation_service.py       # NEW: Markdown validation (structural checks)
│   │   └── chunking_service.py         # NEW: Semantic chunking by headers
│   ├── api/
│   │   ├── translation.py              # NEW: Translation endpoints
│   │   └── admin.py                    # MODIFY: Add cache invalidation endpoint
│   └── prompts/
│       └── translation_prompt.py       # NEW: OpenAI prompt templates
├── tests/
│   ├── unit/
│   │   ├── test_translation_service.py # NEW: Translation logic tests
│   │   ├── test_cache_service.py       # NEW: Cache and locking tests
│   │   ├── test_validation_service.py  # NEW: Validation tests
│   │   └── test_chunking_service.py    # NEW: Chunking tests
│   ├── integration/
│   │   ├── test_translation_api.py     # NEW: API endpoint tests
│   │   └── test_cache_integration.py   # NEW: Database cache tests
│   └── e2e/
│       └── test_translation_flow.py    # NEW: Full translation flow tests
└── migrations/
    └── 006_add_translation_tables.sql  # NEW: Database migration

frontend/ (textbook/)
├── src/
│   ├── components/
│   │   └── TranslationControl/
│   │       ├── index.tsx               # NEW: Translation button component
│   │       ├── styles.module.css       # NEW: RTL layout styles
│   │       └── TranslationControl.test.tsx # NEW: Component tests
│   ├── hooks/
│   │   └── useTranslation.ts           # NEW: Translation state management hook
│   ├── services/
│   │   └── translationApi.ts           # NEW: API client for translation
│   ├── contexts/
│   │   └── LanguageContext.tsx         # NEW: Global language state
│   └── theme/
│       ├── DocItem/                    # MODIFY: Integrate TranslationControl
│       └── fonts.css                   # NEW: Noto Nastaliq Urdu font import
└── tests/
    └── e2e/
        ├── translation.spec.ts         # NEW: E2E translation tests
        └── rtl-layout.spec.ts          # NEW: RTL layout tests
```

**Structure Decision**: Web application structure selected. Backend provides translation API with caching, frontend integrates translation button into Docusaurus theme. Separation allows independent scaling and deployment.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitution principles are satisfied by the proposed architecture.

## Phase 0: Research & Technical Decisions

### Research Topics

#### 1. OpenAI Translation Prompt Engineering

**Decision**: Use GPT-4o-mini with structured system prompt for technical translation

**Rationale**:
- GPT-4o-mini provides good quality at lower cost ($0.15/1M input tokens, $0.60/1M output tokens)
- Structured prompt ensures technical term preservation and academic tone
- Context-aware translation (Physical AI & Humanoid Robotics domain)

**Prompt Template**:
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

**Alternatives Considered**:
- GPT-4o: Higher quality but 10x more expensive, not justified for this use case
- Google Translate API: Cheaper but lacks context awareness and technical term preservation
- DeepL: Good quality but no fine-grained control over term preservation

#### 2. Semantic Chunking Strategy

**Decision**: Chunk by markdown headers (##, ###) for chapters >10,000 words

**Rationale**:
- Preserves semantic context (complete sections translated together)
- Natural break points that maintain document structure
- Easier to track progress (e.g., "Translating section 3 of 8")
- Better translation quality than arbitrary word-count chunking

**Implementation**:
```python
def chunk_by_headers(markdown_content: str) -> List[Chunk]:
    """
    Split markdown content by headers (## and ###).
    Each chunk contains one complete section with its header.
    """
    # Parse markdown to identify header positions
    # Split at header boundaries
    # Return list of chunks with metadata (section_number, header_text, content)
```

**Alternatives Considered**:
- Fixed word count (2000 words): Simpler but may break mid-sentence or mid-paragraph
- Paragraph-based: Too many chunks, more API calls, higher cost
- No chunking: Simpler but may timeout on very large chapters (>10,000 words)

#### 3. Optimistic Locking for Concurrent Translations

**Decision**: Use version field in `translated_chapters` table for optimistic locking

**Rationale**:
- Avoids holding database locks during long-running OpenAI API calls (3-5 seconds)
- Prevents lock contention and timeout issues
- Race conditions are rare (most chapters translated once and cached)
- If conflict occurs, second request simply uses cached result from first request

**Implementation**:
```python
# Check if translation exists
existing = await db.query(TranslatedChapter).filter_by(
    chapter_id=chapter_id, language_code="ur"
).first()

if existing:
    return existing.translated_content

# Create cache entry with version 1
new_translation = TranslatedChapter(
    chapter_id=chapter_id,
    language_code="ur",
    translated_content="",  # Placeholder
    version=1
)
await db.add(new_translation)
await db.commit()

# Perform translation (long-running)
translated_content = await openai_translate(content)

# Update with actual content (check version to detect conflicts)
result = await db.execute(
    update(TranslatedChapter)
    .where(
        TranslatedChapter.chapter_id == chapter_id,
        TranslatedChapter.language_code == "ur",
        TranslatedChapter.version == 1
    )
    .values(translated_content=translated_content, version=2)
)

if result.rowcount == 0:
    # Conflict detected, another request completed first
    # Retrieve the cached result
    existing = await db.query(TranslatedChapter).filter_by(
        chapter_id=chapter_id, language_code="ur"
    ).first()
    return existing.translated_content
```

**Alternatives Considered**:
- Pessimistic locking (row-level lock): Holds lock for entire API call duration, causes contention
- Advisory locks: More complex, requires custom lock management
- No locking: Wastes API costs on race conditions (duplicate translations)

#### 4. Structural Validation Criteria

**Decision**: Validate header count, code blocks, LaTeX equations, and markdown parsing

**Rationale**:
- Catches critical issues that would break page rendering or lose important content
- Fast enough to run on every translation (<100ms)
- Balances thoroughness with performance

**Validation Checks**:
1. **Header Count**: Verify same number of headers (##, ###) in original and translation
2. **Code Blocks**: Verify all fenced code blocks (```python, ```cpp, ```bash) present and unchanged
3. **LaTeX Equations**: Verify all LaTeX equations ($...$, $$...$$) present and unchanged
4. **Markdown Parsing**: Verify translated markdown parses without errors (using markdown parser)

**Implementation**:
```python
def validate_translation(original: str, translated: str) -> ValidationResult:
    """
    Validate translated markdown against original.
    Returns ValidationResult with pass/fail and specific issues.
    """
    issues = []

    # Check header count
    original_headers = count_headers(original)
    translated_headers = count_headers(translated)
    if original_headers != translated_headers:
        issues.append(f"Header count mismatch: {original_headers} vs {translated_headers}")

    # Check code blocks
    original_code_blocks = extract_code_blocks(original)
    translated_code_blocks = extract_code_blocks(translated)
    if original_code_blocks != translated_code_blocks:
        issues.append("Code blocks changed or missing")

    # Check LaTeX equations
    original_latex = extract_latex(original)
    translated_latex = extract_latex(translated)
    if original_latex != translated_latex:
        issues.append("LaTeX equations changed or missing")

    # Check markdown parsing
    try:
        parse_markdown(translated)
    except Exception as e:
        issues.append(f"Markdown parsing error: {str(e)}")

    return ValidationResult(
        passed=len(issues) == 0,
        issues=issues
    )
```

**Alternatives Considered**:
- Full content comparison: Too strict, translations naturally differ
- Minimal validation (parsing only): Too risky, may miss critical issues
- No validation: Unacceptable, could cache broken translations

#### 5. RTL Layout Implementation

**Decision**: Use CSS `direction: rtl` with conditional class on content container

**Rationale**:
- Standard CSS approach for RTL languages
- Works across all modern browsers
- Allows exceptions (code blocks, LaTeX remain LTR)
- Integrates cleanly with Docusaurus theme

**Implementation**:
```css
/* styles.module.css */
.contentUrdu {
  direction: rtl;
  text-align: right;
  font-family: 'Noto Nastaliq Urdu', 'Noto Sans Arabic', system-ui, sans-serif;
  line-height: 1.8;
  font-size: 18px;
}

/* Keep code blocks LTR */
.contentUrdu pre,
.contentUrdu code {
  direction: ltr;
  text-align: left;
}

/* Keep LaTeX LTR */
.contentUrdu .math {
  direction: ltr;
}
```

**Alternatives Considered**:
- JavaScript-based text reversal: Complex, error-prone, poor performance
- Server-side RTL transformation: Unnecessary, CSS handles it natively
- Separate Urdu-specific components: Duplication, harder to maintain

#### 6. Font Loading Strategy

**Decision**: Load Noto Nastaliq Urdu from Google Fonts CDN

**Rationale**:
- Google Fonts provides reliable CDN with global distribution
- Noto Nastaliq Urdu is traditional Urdu script, preferred for readability
- Fallback to Noto Sans Arabic if Nastaliq fails to load
- No need to self-host fonts (adds complexity)

**Implementation**:
```css
/* fonts.css */
@import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;600&family=Noto+Sans+Arabic:wght@400;600&display=swap');
```

**Alternatives Considered**:
- Self-hosted fonts: More control but adds complexity and CDN costs
- System fonts only: Poor Urdu rendering, inconsistent across platforms
- Multiple font options: Unnecessary complexity, Noto Nastaliq is sufficient

### Research Summary

All technical decisions resolved. No NEEDS CLARIFICATION markers remain. Ready to proceed to Phase 1 (Design & Contracts).

## Phase 1: Design & Contracts

### Data Model

See [data-model.md](./data-model.md) for complete entity definitions, relationships, and validation rules.

**Key Entities**:
1. **TranslatedChapter**: Cache for translated content with optimistic locking
2. **User**: Extended with `preferred_language` field
3. **Chapter**: Slug-based identifier (e.g., "01-introduction-to-ros2")

### API Contracts

See [contracts/api-contracts.md](./contracts/api-contracts.md) for complete OpenAPI specifications.

**Key Endpoints**:
1. `POST /api/v1/translate` - Translate chapter to Urdu
2. `GET /api/v1/translate/{chapter_id}` - Get cached translation
3. `DELETE /api/v1/admin/cache/{chapter_id}` - Admin cache invalidation
4. `PUT /api/v1/user/preferences` - Update language preference

### Translation Prompts

See [contracts/prompts.md](./contracts/prompts.md) for complete prompt templates and examples.

### Quickstart Guide

See [quickstart.md](./quickstart.md) for setup instructions, development workflow, and testing procedures.

## Next Steps

1. **Phase 1 Completion**: Generate data-model.md, contracts/, quickstart.md
2. **Agent Context Update**: Run `.specify/scripts/bash/update-agent-context.sh claude`
3. **Constitution Re-check**: Verify all principles still satisfied after design
4. **Task Breakdown**: Run `/sp.tasks` to generate prioritized task list with test scenarios
5. **Implementation**: Follow TDD approach - write tests first, then implement features incrementally

## Notes

- All constitution principles satisfied
- No complexity violations
- All technical decisions resolved through research
- Ready for task breakdown and implementation
