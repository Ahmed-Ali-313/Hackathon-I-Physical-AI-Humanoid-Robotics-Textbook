# ADR-0009: RTL Layout and Typography Implementation

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2026-02-28
- **Feature:** 005-urdu-translation
- **Context:** Need to render Urdu content with proper right-to-left (RTL) layout while preserving left-to-right (LTR) layout for code blocks, LaTeX equations, and URLs. Must integrate cleanly with existing Docusaurus theme, support both light and dark modes, ensure readability with appropriate typography, and work across all modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+).

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - establishes RTL rendering pattern for future language expansion (Arabic, Persian)
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - evaluated CSS-based, JavaScript-based, and server-side approaches
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - affects frontend styling, theme integration, accessibility, and user experience
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We will implement RTL layout and typography with the following integrated components:

- **Layout Approach**: CSS `direction: rtl` property with conditional class on content container
- **Font Stack**: Noto Nastaliq Urdu (primary) + Noto Sans Arabic (fallback) from Google Fonts CDN
- **Font Loading**: Google Fonts CDN with `display=swap` parameter to prevent FOIT (Flash of Invisible Text)
- **Selective LTR Exceptions**: Code blocks, LaTeX equations, URLs, and file paths remain LTR using CSS overrides
- **Typography Specifications**: Line height ≥1.8, font size 18px (16px minimum), font weights 400/600
- **Theme Integration**: Use Docusaurus CSS variables for colors, support both light and dark modes

## Consequences

### Positive

- **Standards-Compliant**: CSS `direction` property is the W3C standard for RTL languages, works natively in all modern browsers
- **Performance**: Pure CSS solution with no JavaScript overhead, instant rendering
- **Readability**: Noto Nastaliq Urdu provides traditional Urdu script preferred by readers, line height 1.8 ensures proper spacing
- **Selective Control**: Can apply RTL to content while keeping code blocks and LaTeX in LTR through CSS specificity
- **Theme Consistency**: Integrates cleanly with Docusaurus theme, works in both light and dark modes without modifications
- **Reliability**: Google Fonts CDN provides 99.9%+ uptime with global distribution and automatic format optimization (WOFF2)
- **Accessibility**: Screen readers handle RTL content correctly with CSS direction property
- **Future-Proof**: Pattern extends to other RTL languages (Arabic, Persian) without redesign

### Negative

- **External Dependency**: Relies on Google Fonts CDN; if CDN fails, falls back to system fonts with degraded quality
- **Font Loading Delay**: Initial page load includes ~50-100KB font download (mitigated by CDN caching and `display=swap`)
- **Browser Compatibility**: Requires modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+); older browsers show LTR layout
- **CSS Complexity**: Requires careful CSS specificity to handle LTR exceptions (code blocks, LaTeX) without conflicts
- **List Marker Positioning**: RTL lists require padding adjustments (padding-right instead of padding-left)
- **Testing Overhead**: Must test RTL layout in all supported browsers and both light/dark themes

## Alternatives Considered

### Alternative Layout: JavaScript-Based Text Reversal
- **Pros**: Full control over text direction, can handle complex edge cases programmatically
- **Cons**: Complex implementation, error-prone, poor performance (runtime overhead), accessibility issues (screen readers confused)
- **Why Rejected**: CSS handles RTL natively; JavaScript adds unnecessary complexity and performance overhead

### Alternative Layout: Server-Side RTL Transformation
- **Pros**: No client-side overhead, works in all browsers including very old ones
- **Cons**: Requires duplicate HTML generation for RTL/LTR, harder to maintain, increases server load, complicates caching
- **Why Rejected**: CSS handles RTL natively; server-side transformation is redundant and adds maintenance burden

### Alternative Layout: Separate Urdu-Specific Components
- **Pros**: Complete isolation, no risk of CSS conflicts, easier to test in isolation
- **Cons**: Code duplication, harder to maintain, more testing needed, violates DRY principle
- **Why Rejected**: Conditional CSS class provides same isolation without duplication

### Alternative Font: Self-Hosted Fonts
- **Pros**: More control over font files, no external dependency, can optimize file sizes
- **Cons**: Adds complexity (font file management, CDN setup), higher costs, requires manual updates
- **Why Rejected**: Google Fonts CDN is more reliable and cost-effective; self-hosting not justified

### Alternative Font: System Fonts Only
- **Pros**: No external dependency, fastest loading (no download), works offline
- **Cons**: Poor Urdu rendering on most systems, inconsistent appearance across platforms, unprofessional look
- **Why Rejected**: Unacceptable quality; Urdu requires specialized fonts for proper rendering

### Alternative Font: Multiple Font Options (User Choice)
- **Pros**: User flexibility, accommodates different preferences (Nastaliq vs Naskh)
- **Cons**: Unnecessary complexity, most users prefer Nastaliq, adds UI clutter, more testing needed
- **Why Rejected**: Overkill for initial release; Noto Nastaliq Urdu is sufficient for 95%+ of users

## References

- Feature Spec: [specs/005-urdu-translation/spec.md](../../specs/005-urdu-translation/spec.md)
- Implementation Plan: [specs/005-urdu-translation/plan.md](../../specs/005-urdu-translation/plan.md)
- Research: [specs/005-urdu-translation/research.md](../../specs/005-urdu-translation/research.md)
- Related ADRs: ADR-0001 (Documentation Platform Stack), ADR-0004 (Frontend Chat UI Integration)
- Evaluator Evidence: To be added after implementation and testing
