# Feature Specification: Urdu Translation for Textbook Chapters

**Feature Branch**: `005-urdu-translation`
**Created**: 2026-02-28
**Status**: Draft
**Input**: User description: "Premium authenticated feature for translating textbook chapters to Urdu with OpenAI API, preserving technical terms and code blocks, with RTL layout support and database caching"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Translate Chapter to Urdu (Priority: P1)

As a logged-in student, I want to translate any textbook chapter from English to Urdu so that I can learn Physical AI and Robotics concepts in my native language while maintaining technical accuracy.

**Why this priority**: This is the core MVP functionality. Without the ability to translate chapters, the entire feature has no value. This delivers immediate value to Urdu-speaking students who struggle with English technical content.

**Independent Test**: Can be fully tested by logging in, navigating to any chapter, clicking the "Translate to Urdu" button, and verifying that the chapter content appears in Urdu with technical terms preserved in English and code blocks unchanged. Delivers standalone value of making content accessible to Urdu speakers.

**Acceptance Scenarios**:

1. **Given** I am a logged-in user viewing Chapter 1 in English, **When** I click the "Translate to Urdu" button at the top of the chapter, **Then** the chapter content is displayed in Urdu with RTL layout, technical terms remain in English, and code blocks remain unchanged
2. **Given** I am viewing a chapter in Urdu, **When** I click the "Show Original English" button, **Then** the chapter switches back to English with LTR layout
3. **Given** I am viewing a chapter with mathematical equations, **When** I translate to Urdu, **Then** all LaTeX equations remain in their original format and are not translated
4. **Given** I am viewing a chapter with code examples, **When** I translate to Urdu, **Then** all code blocks (Python, C++, Bash) remain in English and are not translated
5. **Given** I am viewing a chapter with technical terms like "ROS 2", "VSLAM", "URDF", **When** I translate to Urdu, **Then** these terms remain in English within the Urdu text

---

### User Story 2 - Language Preference Persistence (Priority: P2)

As a logged-in student, I want my language preference to persist across all chapters and browser sessions so that I don't have to manually translate every chapter I visit.

**Why this priority**: This significantly improves user experience by eliminating repetitive actions. Once a user chooses Urdu, they expect all subsequent chapters to open in Urdu automatically. This is essential for a smooth learning experience but the feature can function without it (users can manually translate each chapter).

**Independent Test**: Can be tested by logging in, translating Chapter 1 to Urdu, navigating to Chapter 2, and verifying it automatically displays in Urdu. Then close browser, reopen, login, and verify preference is still Urdu. Delivers standalone value of convenience and seamless experience.

**Acceptance Scenarios**:

1. **Given** I have translated Chapter 1 to Urdu, **When** I navigate to Chapter 2, **Then** Chapter 2 automatically displays in Urdu without requiring me to click translate again
2. **Given** I have set my preference to Urdu, **When** I close my browser and return later (still logged in), **Then** all chapters continue to display in Urdu
3. **Given** I switch back to English on Chapter 5, **When** I navigate to Chapter 6, **Then** Chapter 6 displays in English (preference updated)
4. **Given** I am viewing chapters in Urdu, **When** I log out and log back in, **Then** my Urdu preference is restored and chapters display in Urdu

---

### User Story 3 - Fast Translation with Caching (Priority: P3)

As a logged-in student, I want translated chapters to load instantly on subsequent visits so that I can focus on learning without waiting for translation processing.

**Why this priority**: This enhances performance and reduces costs but is not critical for MVP. The feature works without caching (just slower and more expensive). Caching becomes important as user base grows and translation requests increase.

**Independent Test**: Can be tested by translating a chapter for the first time (may take 3-5 seconds), then navigating away and returning to the same chapter. Verify the Urdu version loads instantly (<500ms). Delivers standalone value of improved performance and reduced API costs.

**Acceptance Scenarios**:

1. **Given** I am translating Chapter 1 to Urdu for the first time, **When** the translation completes, **Then** the Urdu version is saved in the database for future use
2. **Given** Chapter 1 has been translated to Urdu previously, **When** I request the Urdu version, **Then** it loads from the database cache in under 500ms without calling the translation API
3. **Given** a chapter's English content has been updated, **When** I request the Urdu translation, **Then** the system detects the change and requests a fresh translation from the API
4. **Given** multiple users request the same chapter in Urdu, **When** the first user's translation is cached, **Then** all subsequent users receive the cached version instantly

---

### User Story 4 - Unauthenticated User Experience (Priority: P1)

As an unauthenticated visitor, I should see the textbook in English only and be prompted to sign up/login if I attempt to access translation features, so that translation remains a premium feature for registered students.

**Why this priority**: This is critical for the business model and feature access control. Without authentication enforcement, the premium feature becomes freely available to everyone, defeating the purpose of requiring registration.

**Independent Test**: Can be tested by visiting the textbook without logging in, verifying no translate button appears, and attempting to access a translated URL directly results in redirect to login. Delivers standalone value of access control and premium feature protection.

**Acceptance Scenarios**:

1. **Given** I am not logged in, **When** I view any chapter, **Then** I see only English content and no "Translate to Urdu" button is visible
2. **Given** I am not logged in, **When** I attempt to access a translated chapter URL directly, **Then** I am redirected to the login page with a message "Sign up to access Urdu translations"
3. **Given** I am on the login page after attempting to access translation, **When** I successfully log in, **Then** I am redirected back to the chapter with the translate button now visible

---

### User Story 5 - Background-Aware Translation (Priority: P4)

As a logged-in student with a specific technical background (beginner/intermediate/advanced), I want the Urdu translation to match my comprehension level so that explanations are neither too simple nor too complex for my understanding.

**Why this priority**: This is an enhancement that personalizes the learning experience but is not essential for MVP. The feature provides full value without this personalization. This can be added later based on user feedback.

**Independent Test**: Can be tested by creating two user accounts with different background levels (beginner vs advanced), translating the same chapter, and verifying the Urdu translations use different complexity levels in explanations. Delivers standalone value of personalized learning experience.

**Acceptance Scenarios**:

1. **Given** I am a beginner-level user, **When** I translate a chapter about VSLAM, **Then** the Urdu translation includes simplified explanations with more context and analogies
2. **Given** I am an advanced-level user, **When** I translate the same VSLAM chapter, **Then** the Urdu translation uses more technical vocabulary and assumes prior knowledge
3. **Given** I update my background level in preferences, **When** I request a new translation, **Then** the translation complexity adjusts to match my updated level

---

### Edge Cases

- **What happens when the OpenAI API is unavailable or returns an error?**
  - System displays user-friendly error message: "Translation service temporarily unavailable. Please try again in a few moments."
  - Provides "Retry" button to attempt translation again
  - Falls back to displaying English content so user can continue reading

- **What happens when a chapter is extremely long (>10,000 words)?**
  - System chunks the chapter by section boundaries (markdown headers) to preserve context and meaning
  - Each section is translated independently while maintaining semantic coherence
  - Displays loading indicator showing translation progress (e.g., "Translating section 3 of 8... 38% complete")
  - Ensures all sections are translated before displaying the full Urdu version
  - Reassembles sections in correct order maintaining document structure

- **What happens when a user's cached translation is outdated (chapter content updated)?**
  - System compares hash of current English content with hash stored in cache
  - If hashes don't match, system automatically requests fresh translation
  - Old cached version is replaced with new translation

- **What happens when a user switches language mid-chapter (while reading)?**
  - System preserves scroll position when switching between English and Urdu
  - User continues reading from the same location in the new language
  - Smooth transition without page reload

- **What happens when translation contains formatting errors or broken markdown?**
  - System validates translated markdown before caching
  - If validation fails, system logs error and retries translation with stricter preservation rules
  - If retry fails, displays English version with error notification to user

- **What happens when a user has slow internet connection?**
  - System displays loading indicator immediately when translate button is clicked
  - Shows estimated time remaining for translation (first-time) or "Loading from cache" (cached)
  - Allows user to cancel translation request and return to English

- **What happens when multiple users translate the same chapter simultaneously?**
  - System uses optimistic locking with version field to prevent duplicate translation API calls
  - First request checks if translation exists, if not, creates cache entry with version 1 and initiates translation
  - Concurrent requests detect existing cache entry (even if translation incomplete) and wait for completion
  - If race condition occurs (two requests start simultaneously), second request detects version conflict and retrieves the cached result from first request
  - No database locks held during long-running OpenAI API call (3-5 seconds), preventing lock contention

## Requirements *(mandatory)*

### Functional Requirements

#### Authentication & Access Control

- **FR-001**: System MUST display the "Translate to Urdu" button only to authenticated (logged-in) users
- **FR-002**: System MUST hide the translation button from unauthenticated visitors
- **FR-003**: System MUST redirect unauthenticated users to login page if they attempt to access translated content via direct URL
- **FR-004**: System MUST display a message "Sign up to access Urdu translations" when unauthenticated users are redirected

#### Translation Functionality

- **FR-005**: System MUST translate chapter content from English to Urdu using OpenAI API when user clicks "Translate to Urdu" button
- **FR-006**: System MUST preserve all technical terms in English during translation (ROS 2, VSLAM, URDF, Kinematics, SLAM, Isaac Sim, Gazebo, RViz, MoveIt, Jetson Nano, Jetson Orin, Raspberry Pi, MQTT, DDS, TCP/IP, Python, C++, JavaScript, FastAPI, React, Docusaurus)
- **FR-007**: System MUST exclude all code blocks from translation (fenced code blocks with ```python, ```cpp, ```bash, and inline code with backticks)
- **FR-008**: System MUST preserve all LaTeX equations and mathematical symbols in their original format
- **FR-009**: System MUST preserve all markdown syntax (headers #, ##, ###, lists *, -, 1., 2., images ![alt](path), links [text](url), bold **text**, italic *text*)
- **FR-010**: System MUST maintain academic tone suitable for university-level technical education in Urdu translations

#### User Interface & Layout

- **FR-011**: System MUST switch content container to Right-to-Left (RTL) layout when Urdu mode is active (CSS: direction: rtl, text-align: right)
- **FR-012**: System MUST apply Noto Nastaliq Urdu font (primary) or Noto Sans Arabic (fallback) to Urdu text
- **FR-013**: System MUST set line-height to minimum 1.8 for Urdu text to ensure readability of Nastaliq script
- **FR-014**: System MUST set font-size to minimum 16px (18px recommended) for Urdu text
- **FR-015**: System MUST keep code blocks, mathematical equations, URLs, and file paths in LTR layout even when Urdu mode is active
- **FR-016**: System MUST preserve user's scroll position when switching between English and Urdu
- **FR-017**: System MUST handle language toggle via React state without full page reload
- **FR-018**: System MUST display loading indicator during translation fetch with message "Translating chapter..."
- **FR-019**: System MUST change button text from "Translate to Urdu" to "Show Original English" when Urdu is active

#### Language Preference Persistence

- **FR-020**: System MUST save user's language preference (en/ur) to user profile in database when user toggles language
- **FR-021**: System MUST apply saved language preference to all chapters automatically when user navigates between chapters
- **FR-022**: System MUST persist language preference across browser sessions (user remains logged in)
- **FR-023**: System MUST restore language preference when user logs out and logs back in

#### Translation Caching & Performance

- **FR-024**: System MUST check database cache for existing Urdu translation before calling OpenAI API
- **FR-025**: System MUST save successfully translated chapters to database cache with chapter_id, language_code, translated_content, original_hash, created_at, updated_at
- **FR-026**: System MUST return cached translation in under 500ms when available
- **FR-027**: System MUST compute hash of original English content and store with cached translation
- **FR-028**: System MUST invalidate cached translation when original English content hash changes
- **FR-029**: System MUST request fresh translation from OpenAI API when cache is invalid or missing
- **FR-030**: System MUST implement cache expiration of 30 days for automatic refresh of translations
- **FR-031**: System MUST provide admin API endpoint for manual cache invalidation (per chapter or all chapters) to allow re-translation after prompt improvements or error corrections

#### Error Handling

- **FR-031**: System MUST display user-friendly error message when OpenAI API is unavailable: "Translation service temporarily unavailable. Please try again in a few moments."
- **FR-032**: System MUST provide "Retry" button when translation fails
- **FR-033**: System MUST fall back to displaying English content when translation fails so user can continue reading
- **FR-034**: System MUST log all translation errors with context (chapter_id, user_id, error_message, timestamp) for debugging
- **FR-035**: System MUST validate translated markdown before caching using structural validation: verify header count/structure matches original, all code blocks preserved with unchanged content, all LaTeX equations preserved with unchanged content, and markdown parses without rendering errors

#### Optional: Background-Aware Translation

- **FR-036**: System MAY adjust translation complexity based on user's technical background level (beginner/intermediate/advanced) stored in user preferences
- **FR-037**: System MAY include simplified explanations and analogies for beginner-level users
- **FR-038**: System MAY use more technical vocabulary for advanced-level users

### Key Entities

- **User**: Represents a registered student with authentication credentials, language preference (en/ur), and optional technical background level (beginner/intermediate/advanced)

- **Chapter**: Represents a textbook chapter with unique slug-based identifier (chapter_id format: "01-introduction-to-ros2"), English markdown content, title, and content hash for cache invalidation

- **Translation**: Represents a cached translation with chapter reference (slug-based chapter_id), target language code, translated content, original content hash, creation timestamp, and last update timestamp

- **Language Preference**: Represents user's preferred language setting, stored in user profile, persists across sessions

## Clarifications

### Session 2026-02-28

- Q: What format should the chapter identifier use? → A: Slug-based identifier (e.g., "01-introduction-to-ros2") - Human-readable, SEO-friendly, aligns with Docusaurus structure
- Q: How should large chapters be chunked for translation? → A: Semantic chunking by section boundaries (headers) - Preserves context, translates complete sections
- Q: Should there be a manual cache invalidation mechanism for administrators? → A: Yes, provide admin API endpoint for manual cache invalidation (per chapter or all chapters)
- Q: What database locking strategy should be used for concurrent translation requests? → A: Optimistic locking with version field - Check-then-act pattern, retry on conflict
- Q: What validation checks should be performed on translated markdown? → A: Structural validation (headers, code blocks, LaTeX preserved) + basic rendering test

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Authenticated users can translate any chapter to Urdu in under 5 seconds for first-time translation
- **SC-002**: Cached translations load in under 500ms for subsequent requests
- **SC-003**: 100% of technical terms remain in English after translation (verified by automated tests)
- **SC-004**: 100% of code blocks remain unchanged after translation (verified by automated tests)
- **SC-005**: 100% of LaTeX equations remain in original format after translation (verified by automated tests)
- **SC-006**: User's language preference persists across 100% of chapter navigations within same session
- **SC-007**: User's language preference persists across 100% of logout/login cycles
- **SC-008**: RTL layout applies correctly to Urdu content with proper text alignment and direction
- **SC-009**: Urdu text is readable with Noto Nastaliq Urdu font at line-height ≥1.8
- **SC-010**: Scroll position is preserved when switching languages (user stays at same reading location)
- **SC-011**: Translation feature is accessible only to authenticated users (0% access for unauthenticated visitors)
- **SC-012**: System handles translation errors gracefully with user-friendly messages and retry option
- **SC-013**: Cache hit rate reaches 80%+ after first week of usage (reduces API costs by 80%)
- **SC-014**: 90% of users successfully translate and read at least one chapter in Urdu within first session
- **SC-015**: Translation quality maintains academic tone suitable for university-level technical education (verified by manual review of sample translations)

## Assumptions

1. **OpenAI API Availability**: We assume OpenAI API (GPT-4o-mini) is available and reliable for translation requests with 99%+ uptime
2. **Database Performance**: We assume Neon Serverless Postgres can handle translation cache reads/writes with <100ms latency
3. **Chapter Size**: We assume most chapters are under 5,000 words; chapters exceeding 10,000 words will require chunking
4. **Font Availability**: We assume Noto Nastaliq Urdu and Noto Sans Arabic fonts can be loaded via Google Fonts or similar CDN
5. **User Authentication**: We assume existing authentication system (JWT-based) is functional and provides user_id for preference storage
6. **Browser Support**: We assume modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+) with RTL layout support
7. **Translation Quality**: We assume OpenAI GPT-4o-mini provides sufficient quality for technical Urdu translation with proper prompting
8. **Cost Budget**: We assume translation API costs are acceptable for premium feature (estimated $0.01-0.03 per chapter translation)
9. **User Preference Schema**: We assume user_preferences table exists and can be extended with preferred_language column
10. **Markdown Rendering**: We assume existing Docusaurus markdown renderer can handle RTL content without modifications

## Out of Scope

1. **Multiple Languages**: This feature supports only Urdu translation; other languages (Arabic, Hindi, etc.) are out of scope for Phase 4
2. **Offline Translation**: Translation requires internet connection; offline mode is not supported
3. **User-Editable Translations**: Users cannot edit or suggest improvements to translations; this is a read-only feature
4. **Translation History**: System does not track individual user's translation history or usage analytics
5. **Audio/Video Translation**: Only text content is translated; embedded videos, audio, or images with text are not translated
6. **Real-Time Collaboration**: Multiple users cannot collaboratively improve translations
7. **Translation API Alternatives**: Only OpenAI API is supported; alternative translation services (Google Translate, DeepL) are not integrated
8. **Custom Terminology Glossary**: System does not support user-defined custom terminology mappings
9. **Translation Versioning**: System does not maintain multiple versions of translations; only latest translation is cached
10. **Translation Quality Feedback**: Users cannot rate or provide feedback on translation quality

## Dependencies

1. **OpenAI API Access**: Requires valid OpenAI API key with sufficient quota for GPT-4o-mini model
2. **Database Schema Update**: Requires migration to create `translated_chapters` table and extend `user_preferences` table
3. **Authentication System**: Requires existing JWT-based authentication to identify logged-in users
4. **User Preferences System**: Requires existing user preferences infrastructure to store language preference
5. **Docusaurus Theme**: Requires Docusaurus 3.x with ability to customize DocItem layout for translation button
6. **Font Loading**: Requires Google Fonts or CDN access to load Noto Nastaliq Urdu and Noto Sans Arabic fonts
7. **Backend API**: Requires FastAPI backend with endpoint for translation requests
8. **React Context/State**: Requires React 18+ for state management of language preference
9. **CSS RTL Support**: Requires CSS framework that supports RTL layout (direction: rtl)
10. **Markdown Parser**: Requires markdown parser that can identify and preserve code blocks, LaTeX equations, and technical terms

## Constraints

1. **Authentication Required**: Translation feature is strictly for authenticated users only; no guest access
2. **Technical Term Preservation**: All technical terms MUST remain in English; no exceptions
3. **Code Block Immunity**: All code blocks MUST remain unchanged; no translation of code
4. **Mathematical Accuracy**: All LaTeX equations MUST remain in original format; no translation
5. **Markdown Structure**: All markdown syntax MUST be preserved; no breaking of Docusaurus rendering
6. **RTL Layout**: Urdu content MUST use RTL layout; no LTR layout for Urdu text
7. **Font Requirements**: Urdu text MUST use Noto Nastaliq Urdu or Noto Sans Arabic; no system default fonts
8. **Line Height**: Urdu text MUST have line-height ≥1.8; no lower values
9. **Cache Validity**: Cached translations MUST be invalidated when original content changes; no stale translations
10. **Performance**: Cached translations MUST load in <500ms; no slower response times
11. **API Cost**: Translation API costs MUST be minimized through caching; no unlimited API calls
12. **Browser Compatibility**: Feature MUST work on modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
13. **No Page Reload**: Language toggle MUST be handled via React state; no full page reload
14. **Scroll Preservation**: Scroll position MUST be preserved when switching languages; no jumping to top
15. **Academic Tone**: Translations MUST maintain academic tone suitable for university-level education; no casual language

## Risks

1. **Translation Quality**: OpenAI API may produce inconsistent or inaccurate Urdu translations for complex technical concepts
   - **Mitigation**: Implement manual review process for sample translations; refine system prompts based on feedback

2. **API Cost Overrun**: High translation volume could lead to unexpected OpenAI API costs
   - **Mitigation**: Implement aggressive caching strategy (30-day expiration); monitor API usage and set budget alerts

3. **Performance Degradation**: Large chapters (>10,000 words) may take too long to translate (>10 seconds)
   - **Mitigation**: Implement chunking strategy for large chapters; display progress indicator during translation

4. **Cache Invalidation Issues**: Stale translations may be served when chapter content is updated
   - **Mitigation**: Implement content hashing to detect changes; provide manual cache invalidation for admins

5. **RTL Layout Bugs**: Complex markdown structures may not render correctly in RTL layout
   - **Mitigation**: Extensive testing of various markdown patterns; fallback to LTR for problematic elements

6. **Font Loading Failures**: Noto Nastaliq Urdu font may fail to load on some networks or browsers
   - **Mitigation**: Provide fallback fonts (Noto Sans Arabic, system-ui); test on various browsers and networks

7. **Authentication Bypass**: Users may attempt to access translated content without authentication
   - **Mitigation**: Implement server-side authentication checks; validate JWT tokens on all translation API requests

8. **Database Performance**: High cache read/write volume may slow down database queries
   - **Mitigation**: Implement proper indexing on (chapter_id, language_code); monitor query performance

9. **Browser Compatibility**: Older browsers may not support RTL layout or modern CSS features
   - **Mitigation**: Define minimum browser versions; display upgrade message for unsupported browsers

10. **User Confusion**: Users may not understand why technical terms remain in English
    - **Mitigation**: Add tooltip or help text explaining technical term preservation policy

## Next Steps

1. **Clarification Phase** (`/sp.clarify`): Review specification with stakeholders and resolve any [NEEDS CLARIFICATION] markers
2. **Planning Phase** (`/sp.plan`): Create detailed architecture plan including API contracts, database schema, component structure, and translation prompt engineering
3. **Task Breakdown** (`/sp.tasks`): Generate prioritized task list with test scenarios for each user story
4. **Implementation**: Follow TDD approach - write tests first, then implement features incrementally
