# ADR-0004: Frontend Chat UI Integration

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-02-22
- **Feature:** 003-rag-chatbot
- **Context:** Need to integrate chat UI into existing Docusaurus textbook without disrupting reading experience. Must support slide-out panel (per clarification), theme matching (light/dark mode), text selection detection for "Ask about selection" mode, and conversation history navigation. UI must be non-invasive and maintain professional academic appearance.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Defines UI architecture and user interaction pattern
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Plugin, separate page, iframe, browser extension evaluated
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects all textbook pages and user experience
-->

## Decision

**Docusaurus Theme Components Integration:**
- **Root Wrapper**: Wrap app in `src/theme/Root.tsx` with ChatProvider (React Context)
- **Floating Button**: ChatButton component (bottom-right, "Ask" text, theme-matched)
- **Chat Panel**: Slide-out side panel from right (overlays textbook, semi-transparent backdrop)
- **Conversation Sidebar**: Left section of panel shows conversation list
- **State Management**: React Context API for chat state (messages, conversations, UI state)
- **Theme Matching**: Use Docusaurus CSS variables (`--ifm-*`) for consistent styling
- **Text Selection**: Browser Selection API with React hooks (`useTextSelection`)

## Consequences

### Positive

- **Non-Invasive**: Doesn't modify existing textbook pages, only adds overlay UI
- **Theme Matching**: Automatic light/dark mode support via Docusaurus CSS variables
- **Standard React**: Uses familiar React patterns (Context API, hooks, components)
- **No Ejecting**: Docusaurus theme system allows customization without ejecting
- **Slide-Out Panel**: Standard chat UX pattern (Slack, Discord, ChatGPT) - familiar to users
- **Conversation Sidebar**: Easy navigation between conversation threads
- **Mobile Support**: Responsive design adapts to small screens

### Negative

- **Docusaurus Coupling**: Tightly coupled to Docusaurus theme system (hard to port to other platforms)
- **CSS Variable Dependency**: Relies on Docusaurus CSS variables (breaks if Docusaurus changes naming)
- **Context Performance**: React Context re-renders all consumers on state change (acceptable for chat UI)
- **Selection API Limitations**: Browser Selection API doesn't work in all edge cases
- **Overlay Z-Index**: Must manage z-index carefully to avoid conflicts with Docusaurus navbar/sidebar

## Alternatives Considered

**Alternative A: Docusaurus Plugin**
- **Why Rejected**: Plugins are for build-time features, not runtime UI; theme components are the recommended approach

**Alternative B: Separate Chat Page**
- **Why Rejected**: Breaks user flow (students must leave textbook to ask questions); doesn't support "Ask about selection" mode

**Alternative C: Iframe Embed**
- **Why Rejected**: Styling challenges, cross-origin issues, poor accessibility, harder to detect text selection

**Alternative D: Browser Extension**
- **Why Rejected**: Requires users to install extension (poor UX, adoption barrier); doesn't work on mobile

## References

- Feature Spec: [specs/003-rag-chatbot/spec.md](../../specs/003-rag-chatbot/spec.md) (FR-004 to FR-009, FR-031 to FR-033)
- Implementation Plan: [specs/003-rag-chatbot/plan.md](../../specs/003-rag-chatbot/plan.md)
- Research: [specs/003-rag-chatbot/research.md](../../specs/003-rag-chatbot/research.md) (Section 4)
- Clarifications: [specs/003-rag-chatbot/spec.md](../../specs/003-rag-chatbot/spec.md#clarifications) (Q1: Slide-out panel)
- Related ADRs: None
- Official Documentation:
  - [Docusaurus Swizzling Guide](https://docusaurus.io/docs/swizzling)
  - [Docusaurus Theming](https://docusaurus.io/docs/styling-layout)
  - [React Context API](https://react.dev/reference/react/useContext)
