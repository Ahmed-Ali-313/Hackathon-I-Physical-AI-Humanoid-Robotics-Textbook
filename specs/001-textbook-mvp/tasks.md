# Tasks: Physical AI & Humanoid Robotics Textbook (Phase 1 - MVP)

**Input**: Design documents from `/specs/001-textbook-mvp/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Unit test tasks included for custom React components (Constitution Principle III compliance)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Docusaurus site root**: `textbook/` at repository root
- **Content**: `textbook/docs/` for all course chapters
- **Components**: `textbook/src/components/` for custom React components
- **Styles**: `textbook/src/css/` for global styles
- **Config**: `textbook/docusaurus.config.js` and `textbook/sidebars.js`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic Docusaurus structure

- [ ] T001 Initialize Docusaurus project with TypeScript using `npx create-docusaurus@latest textbook classic --typescript` in repository root
- [ ] T002 Install Node.js 20.x LTS dependencies by running `npm install` in textbook/
- [ ] T003 [P] Install search plugin `@easyops-cn/docusaurus-search-local` in textbook/package.json
- [ ] T004 [P] Configure Git to ignore textbook/node_modules/, textbook/build/, and textbook/.docusaurus/ in .gitignore
- [ ] T005 Verify Docusaurus runs successfully with `npm start` in textbook/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core configuration that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Configure site metadata in textbook/docusaurus.config.js (title: "Physical AI & Humanoid Robotics", tagline, URL, baseUrl)
- [ ] T007 [P] Configure dark mode in textbook/docusaurus.config.js themeConfig.colorMode (defaultMode: 'light', disableSwitch: false, respectPrefersColorScheme: true)
- [ ] T008 [P] Configure search plugin in textbook/docusaurus.config.js plugins section with hashed: true, indexDocs: true, highlightSearchTermsOnTargetPage: true
- [ ] T009 [P] Create custom CSS variables for light and dark themes in textbook/src/css/custom.css
- [ ] T010 [P] Configure navbar in textbook/docusaurus.config.js themeConfig.navbar with course link and search
- [ ] T011 [P] Create Vercel deployment configuration in textbook/vercel.json with buildCommand, outputDirectory, framework, and Node.js 20.x
- [ ] T012 Configure footer in textbook/docusaurus.config.js themeConfig.footer with copyright information

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Discover and Enter Textbook (Priority: P1) 🎯 MVP

**Goal**: Students arrive at landing page, see course overview, and click "Begin Your Journey" to enter textbook

**Independent Test**: Visit landing page at `/`, verify hero section displays with course title and description, click "Begin Your Journey" button, confirm navigation to first chapter

### Implementation for User Story 1

- [ ] T013 [P] [US1] Create custom landing page component in textbook/src/pages/index.tsx replacing default Docusaurus homepage
- [ ] T014 [P] [US1] Create HomepageHeader component in textbook/src/components/LandingHero/index.tsx with hero section, course title, tagline, and CTA button
- [ ] T015 [P] [US1] Create HomepageHeader styles in textbook/src/components/LandingHero/styles.module.css with responsive layout and attractive design
- [ ] T016 [P] [US1] Create HomepageFeatures component in textbook/src/components/HomepageFeatures/index.tsx displaying 4 module preview cards
- [ ] T017 [P] [US1] Create HomepageFeatures styles in textbook/src/components/HomepageFeatures/styles.module.css with grid layout
- [ ] T018 [US1] Create intro page at textbook/docs/intro.md as entry point from landing page CTA
- [ ] T019 [US1] Configure "Begin Your Journey" button to link to `/docs/intro` in textbook/src/pages/index.tsx
- [ ] T020 [US1] Add module preview content (titles, descriptions, icons) for all 4 modules in HomepageFeatures component

**Checkpoint**: At this point, User Story 1 should be fully functional - landing page displays and navigates to textbook

---

## Phase 4: User Story 2 - Navigate and Read Course Content (Priority: P1) 🎯 MVP

**Goal**: Students navigate through modules and chapters, read content with code examples and syntax highlighting

**Independent Test**: Enter textbook, open sidebar, expand Module 1, click any chapter, verify content displays with formatted text and syntax-highlighted code, use prev/next navigation

### Implementation for User Story 2

#### Module Structure Setup

- [ ] T020 [P] [US2] Create Module 1 folder structure at textbook/docs/module-1-ros2/ with _category_.json
- [ ] T021 [P] [US2] Create Module 2 folder structure at textbook/docs/module-2-digital-twin/ with _category_.json
- [ ] T022 [P] [US2] Create Module 3 folder structure at textbook/docs/module-3-isaac/ with _category_.json
- [ ] T023 [P] [US2] Create Module 4 folder structure at textbook/docs/module-4-vla/ with _category_.json
- [ ] T024 [P] [US2] Create Hardware folder structure at textbook/docs/hardware/ with _category_.json

#### Module 1 Chapters (ROS 2)

- [ ] T025 [P] [US2] Create chapter file textbook/docs/module-1-ros2/middleware.md with frontmatter (sidebar_position: 1, title, description, keywords) and placeholder content
- [ ] T026 [P] [US2] Create chapter file textbook/docs/module-1-ros2/nodes-topics-services.md with frontmatter (sidebar_position: 2) and placeholder content
- [ ] T027 [P] [US2] Create chapter file textbook/docs/module-1-ros2/python-ros-bridging.md with frontmatter (sidebar_position: 3) and placeholder content
- [ ] T028 [P] [US2] Create chapter file textbook/docs/module-1-ros2/urdf-humanoids.md with frontmatter (sidebar_position: 4) and placeholder content

#### Module 2 Chapters (Digital Twin)

- [ ] T029 [P] [US2] Create chapter file textbook/docs/module-2-digital-twin/physics-simulation.md with frontmatter (sidebar_position: 1) and placeholder content
- [ ] T030 [P] [US2] Create chapter file textbook/docs/module-2-digital-twin/rendering-interaction.md with frontmatter (sidebar_position: 2) and placeholder content
- [ ] T031 [P] [US2] Create chapter file textbook/docs/module-2-digital-twin/sensor-simulation.md with frontmatter (sidebar_position: 3) and placeholder content

#### Module 3 Chapters (NVIDIA Isaac)

- [ ] T032 [P] [US2] Create chapter file textbook/docs/module-3-isaac/isaac-sim.md with frontmatter (sidebar_position: 1) and placeholder content
- [ ] T033 [P] [US2] Create chapter file textbook/docs/module-3-isaac/isaac-ros.md with frontmatter (sidebar_position: 2) and placeholder content
- [ ] T034 [P] [US2] Create chapter file textbook/docs/module-3-isaac/nav2-planning.md with frontmatter (sidebar_position: 3) and placeholder content

#### Module 4 Chapters (VLA)

- [ ] T035 [P] [US2] Create chapter file textbook/docs/module-4-vla/llm-robotics.md with frontmatter (sidebar_position: 1) and placeholder content
- [ ] T036 [P] [US2] Create chapter file textbook/docs/module-4-vla/voice-to-action.md with frontmatter (sidebar_position: 2) and placeholder content
- [ ] T037 [P] [US2] Create chapter file textbook/docs/module-4-vla/cognitive-planning.md with frontmatter (sidebar_position: 3) and placeholder content
- [ ] T038 [P] [US2] Create chapter file textbook/docs/module-4-vla/capstone-project.md with frontmatter (sidebar_position: 4) and placeholder content

#### Navigation Configuration

- [ ] T039 [US2] Configure sidebar navigation in textbook/sidebars.js with all 4 modules as categories and their respective chapter items
- [ ] T040 [US2] Add code examples with syntax highlighting to at least 3 chapters (one Python, one C++, one YAML example)
- [ ] T041 [US2] Verify sequential navigation (prev/next buttons) works across module boundaries by testing navigation flow

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - landing page + full navigation and content reading

---

## Phase 5: User Story 3 - Access Hardware Requirements (Priority: P2)

**Goal**: Students access hardware requirement chapters to understand equipment needs

**Independent Test**: Navigate to Hardware Requirements section in sidebar, click each of the 3 hardware chapters, verify content displays

### Implementation for User Story 3

- [ ] T042 [P] [US3] Create chapter file textbook/docs/hardware/workstations.md with frontmatter (sidebar_position: 1) and placeholder content about NVIDIA RTX GPUs and Ubuntu 22.04 LTS
- [ ] T043 [P] [US3] Create chapter file textbook/docs/hardware/edge-kits.md with frontmatter (sidebar_position: 2) and placeholder content about NVIDIA Jetson Orin Nano and Intel RealSense
- [ ] T044 [P] [US3] Create chapter file textbook/docs/hardware/robot-tiers.md with frontmatter (sidebar_position: 3) and placeholder content about Unitree Go2 vs Unitree G1 comparison
- [ ] T045 [US3] Add Hardware Requirements category to textbook/sidebars.js with all 3 hardware chapters

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Search for Topics (Priority: P2)

**Goal**: Students use search to quickly find specific topics across all modules

**Independent Test**: Use search bar in navbar, enter query like "ROS 2 nodes", verify results appear with relevant chapters, click result, verify navigation and term highlighting

### Implementation for User Story 4

- [ ] T046 [US4] Verify search plugin configuration in textbook/docusaurus.config.js includes highlightSearchTermsOnTargetPage: true
- [ ] T047 [US4] Build production site with `npm run build` to generate search index in textbook/
- [ ] T048 [US4] Test search functionality with `npm run serve` and verify search returns relevant results for test queries
- [ ] T049 [US4] Verify search term highlighting works when navigating from search results to chapter pages

**Checkpoint**: At this point, User Stories 1-4 should all work independently

---

## Phase 7: User Story 5 - Mobile Responsive (Priority: P3)

**Goal**: Students access textbook on mobile devices with responsive layout

**Independent Test**: Open textbook on mobile device or browser dev tools mobile view, verify layout adapts, sidebar becomes overlay, code blocks are scrollable

### Implementation for User Story 5

- [ ] T050 [P] [US5] Add mobile-responsive CSS media queries in textbook/src/css/custom.css for screens < 768px
- [ ] T051 [P] [US5] Configure mobile sidebar behavior in textbook/docusaurus.config.js themeConfig (should be default Docusaurus behavior)
- [ ] T052 [US5] Test mobile layout on multiple screen sizes (phone: 375px, tablet: 768px, desktop: 1024px+) using browser dev tools
- [ ] T053 [US5] Verify code blocks are horizontally scrollable on mobile without breaking layout
- [ ] T054 [US5] Verify landing page hero section and CTA button are properly sized and readable on mobile

**Checkpoint**: All user stories should now be independently functional across all device sizes

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [ ] T055 [P] Add placeholder images/icons for module previews in textbook/static/img/
- [ ] T056 [P] Optimize custom CSS for performance and consistency across themes in textbook/src/css/custom.css
- [ ] T057 [P] Add 404 error page configuration in textbook/docusaurus.config.js
- [ ] T058 [P] Create README.md in textbook/ with setup instructions, development commands, and deployment guide

### Unit Testing (Constitution Principle III - Mandatory)

**Purpose**: Achieve 80% test coverage for custom React components

- [ ] T059 [P] Configure Jest and React Testing Library in textbook/package.json with TypeScript support
- [ ] T060 [P] Create unit test for HomepageHeader component in textbook/src/components/LandingHero/__tests__/index.test.tsx (test rendering, CTA button click, responsive layout)
- [ ] T061 [P] Create unit test for HomepageFeatures component in textbook/src/components/HomepageFeatures/__tests__/index.test.tsx (test 4 module cards render, grid layout)
- [ ] T062 [P] Create unit test for landing page in textbook/src/pages/__tests__/index.test.tsx (test page structure, component integration)
- [ ] T063 Run unit tests with `npm test` in textbook/ and verify 80% coverage for custom components

### Build & Deployment Validation

- [ ] T064 Run production build with `npm run build` in textbook/ and verify no errors
- [ ] T065 Test production build locally with `npm run serve` and verify all features work
- [ ] T066 Run Lighthouse audit on production build and verify scores > 80 for performance, accessibility, best practices

### Success Criteria Validation

**Purpose**: Validate measurable outcomes from spec.md Success Criteria section

- [ ] T067 [P] Validate SC-001: Test navigation from landing page to any chapter completes within 30 seconds
- [ ] T068 [P] Validate SC-002: Measure page load time for 5 random chapters, verify all < 3 seconds
- [ ] T069 [P] Validate SC-003: Test search for 5 different queries, verify results appear within 15 seconds
- [ ] T070 [P] Validate SC-005: Test code block rendering on desktop (1920px), tablet (768px), mobile (375px) for proper formatting
- [ ] T071 [P] Validate SC-006: Navigate through complete Module 1, verify no broken links or navigation errors
- [ ] T072 [P] Validate SC-009: Test sidebar toggle animation, verify completes in < 1 second with smooth transition

### Edge Case Validation

**Purpose**: Verify edge cases from spec.md are handled correctly

- [ ] T073 [P] Test 404 page: Access non-existent URL, verify friendly error page with navigation back to table of contents
- [ ] T074 [P] Test long code blocks: Create chapter with 100+ line code example, verify vertical and horizontal scrolling works
- [ ] T075 [P] Test special character search: Search for "ros2::Node", "C++", verify search handles special characters correctly
- [ ] T076 [P] Test last chapter navigation: Navigate to Module 4 Capstone chapter, verify "Next Chapter" button shows appropriate message
- [ ] T077 [P] Test sidebar scrolling: Verify sidebar is independently scrollable when content exceeds screen height

### Final Documentation

- [ ] T078 Update history.md with Phase 1 implementation completion details
- [ ] T079 Validate quickstart.md instructions by following setup steps from scratch

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories (but logically follows US1)
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Actually part of content structure, minimal dependencies
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Requires content to exist for meaningful testing (depends on US2 content)
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - Should be tested after US1-4 are complete

### Within Each User Story

- Setup tasks before implementation
- Module structures before chapter files
- Chapter files can be created in parallel
- Configuration after content creation
- Testing after implementation

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, US1 and US2 can start in parallel
- All module folder structures (T020-T024) can be created in parallel
- All chapter files within each module can be created in parallel
- All hardware chapter files (T042-T044) can be created in parallel
- All Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 2 - Module Structures

```bash
# Launch all module structure tasks together:
Task: "Create Module 1 folder structure at textbook/docs/module-1-ros2/ with _category_.json"
Task: "Create Module 2 folder structure at textbook/docs/module-2-digital-twin/ with _category_.json"
Task: "Create Module 3 folder structure at textbook/docs/module-3-isaac/ with _category_.json"
Task: "Create Module 4 folder structure at textbook/docs/module-4-vla/ with _category_.json"
Task: "Create Hardware folder structure at textbook/docs/hardware/ with _category_.json"
```

## Parallel Example: User Story 2 - Module 1 Chapters

```bash
# Launch all Module 1 chapter creation tasks together:
Task: "Create chapter file textbook/docs/module-1-ros2/middleware.md with frontmatter and placeholder content"
Task: "Create chapter file textbook/docs/module-1-ros2/nodes-topics-services.md with frontmatter and placeholder content"
Task: "Create chapter file textbook/docs/module-1-ros2/python-ros-bridging.md with frontmatter and placeholder content"
Task: "Create chapter file textbook/docs/module-1-ros2/urdf-humanoids.md with frontmatter and placeholder content"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Landing Page)
4. Complete Phase 4: User Story 2 (Navigation & Content)
5. **STOP and VALIDATE**: Test US1 and US2 independently
6. Deploy to Vercel for demo

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (Landing page works!)
3. Add User Story 2 → Test independently → Deploy/Demo (MVP complete - can read content!)
4. Add User Story 3 → Test independently → Deploy/Demo (Hardware info added)
5. Add User Story 4 → Test independently → Deploy/Demo (Search works!)
6. Add User Story 5 → Test independently → Deploy/Demo (Mobile ready!)
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Landing Page)
   - Developer B: User Story 2 (Content Structure)
   - Developer C: User Story 3 (Hardware Chapters)
3. After US1-3 complete:
   - Developer A: User Story 4 (Search)
   - Developer B: User Story 5 (Mobile)
   - Developer C: Polish tasks
4. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Unit tests included for Constitution Principle III compliance (80% coverage requirement)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Placeholder content strategy: ~200-300 words per chapter with code examples
- All 17 chapters must be created for complete navigation structure
- Search requires production build (`npm run build`) to generate index
- Mobile responsiveness is mostly handled by Docusaurus defaults, minimal custom CSS needed
- Menu toggle: Docusaurus uses hamburger menu icon by default (satisfies FR-007 "three-dot icon or hamburger menu")
- Edge cases: Most handled by Docusaurus defaults (404, scrolling, loading indicators); custom validation tasks added for verification
- Success criteria: Analytics tracking (SC-007: 90% CTA clicks) out of scope for Phase 1; other criteria validated via manual testing tasks
