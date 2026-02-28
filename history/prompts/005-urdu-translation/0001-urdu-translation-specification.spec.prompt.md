---
id: 0001
title: Urdu Translation Specification
stage: spec
date: 2026-02-28
surface: agent
model: claude-opus-4-6
feature: 005-urdu-translation
branch: 005-urdu-translation
user: ahmeddev
command: /sp.specify
labels: ["urdu-translation", "i18n", "internationalization", "rtl", "openai", "caching", "authentication", "premium-feature"]
links:
  spec: /mnt/e/ai-native-book/specs/005-urdu-translation/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/005-urdu-translation/spec.md
 - specs/005-urdu-translation/checklists/requirements.md
tests:
 - None (specification phase)
---

## Prompt

1. Feature Overview: A premium, authenticated feature that allows students to toggle the language of any textbook chapter between English and Urdu. The translation is performed by the OpenAI API, ensuring that technical robotics terminology and code structures are preserved while the narrative text is localized.

2. Functional Requirements:
- Authenticated Access: The translation button must only be visible and functional for users who are logged in.
- Chapter Translation: Upon clicking the "Translate" button, the system must fetch the Urdu version of the current Markdown chapter.
- Preservation Rules: Technical Terms (ROS 2, URDF, VSLAM, etc.) must remain in English. Code Blocks (all python, cpp, and bash blocks) must remain untranslated. Math (LaTeX equations) must remain in their original format.
- Layout Switch: The UI must switch to a Right-to-Left (RTL) orientation when Urdu is active.

3. Technical Architecture:
- Frontend (Docusaurus/React): Component TranslationControl.tsx placed at the top of the DocItem or Chapter layout. State tracks currentLanguage (en/ur) using React Context or Local Storage. Renderer uses react-markdown.
- Backend (FastAPI): Endpoint POST /api/v1/translate. Logic: Check Neon Postgres translations table for chapter_id + lang='ur'. If result exists, return cached Markdown. If not, send English Markdown to OpenAI with "Robotics Expert Translator" system prompt. Save result to Neon and return to frontend.
- Database (Neon Postgres): Table translations (columns: id, chapter_id, language, content, created_at).

4. Design & Theme Integration:
- Theme Mirroring: The Urdu content must use the same CSS variables as the English theme (colors, spacing, dark/light mode).
- Typography: Font Noto Nastaliq Urdu (primary) or system-ui. Line Height increased to 2.2 for Urdu script readability.
- RTL Support: Apply global CSS class .rtl-content { direction: rtl; text-align: right; } to the Markdown container.

5. User Data & Personalization: Background Awareness - The translation prompt can be subtly adjusted based on the user's "Software/Hardware Background" (collected during signup) to simplify or deepen the Urdu explanation.

## Response snapshot

Created comprehensive specification for Phase 4 Urdu Translation feature with 5 prioritized user stories, 38 functional requirements, 15 success criteria, and complete validation checklist.

**Feature Structure Created**:
- Branch: 005-urdu-translation
- Spec file: specs/005-urdu-translation/spec.md
- Checklist: specs/005-urdu-translation/checklists/requirements.md

**5 User Stories (Prioritized)**:
1. P1: Translate Chapter to Urdu - Core MVP functionality with 5 acceptance scenarios
2. P2: Language Preference Persistence - Seamless experience across chapters and sessions
3. P3: Fast Translation with Caching - Performance optimization with database caching
4. P1: Unauthenticated User Experience - Access control and premium feature protection
5. P4: Background-Aware Translation - Personalized complexity levels (optional enhancement)

**38 Functional Requirements** organized by category:
- Authentication & Access Control (FR-001 to FR-004)
- Translation Functionality (FR-005 to FR-010)
- User Interface & Layout (FR-011 to FR-019)
- Language Preference Persistence (FR-020 to FR-023)
- Translation Caching & Performance (FR-024 to FR-030)
- Error Handling (FR-031 to FR-035)
- Optional: Background-Aware Translation (FR-036 to FR-038)

**15 Success Criteria** - all measurable and technology-agnostic:
- Translation speed: <5s first-time, <500ms cached
- 100% preservation of technical terms, code blocks, LaTeX equations
- 100% preference persistence across sessions
- RTL layout correctness
- 80%+ cache hit rate
- 90% user success rate

**Comprehensive Coverage**:
- 7 edge cases with handling strategies
- 10 assumptions documented
- 10 out-of-scope items clearly defined
- 10 dependencies identified
- 15 constraints enforced
- 10 risks with mitigation strategies

**Validation Results**: ✅ All checklist items passed - specification is ready for planning phase

## Outcome

- ✅ Impact: Phase 4 Urdu Translation specification complete with comprehensive requirements, user stories, and validation
- 🧪 Tests: None (specification phase - tests will be defined in tasks phase)
- 📁 Files: 2 files created (spec.md, requirements.md checklist)
- 🔁 Next prompts: /sp.plan (create architecture plan with API contracts, database schema, component structure, translation prompt engineering)
- 🧠 Reflection: Specification follows constitution principles (Principles XI-XV) with strong focus on authentication, technical term preservation, RTL layout, caching strategy, and TDD approach. All requirements are testable and unambiguous. No clarifications needed - ready for planning.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Specification quality checklist PASSED (all items validated)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to planning phase to define technical architecture, API contracts, and database schema
