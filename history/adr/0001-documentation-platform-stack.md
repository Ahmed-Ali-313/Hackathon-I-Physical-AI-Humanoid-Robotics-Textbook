# ADR-0001: Documentation Platform Stack

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-02-16
- **Feature:** 001-textbook-mvp
- **Context:** Phase 1 requires a professional, static documentation website to deliver the Physical AI & Humanoid Robotics course content with navigation, search, dark mode, and mobile responsiveness. The platform must support hierarchical content organization, client-side search, and deployment to Vercel. Constitution requires using Docusaurus (Principle V: Tech Stack Compliance) and consulting official documentation (Principle VIII).

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Defines entire frontend architecture
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Evaluated multiple doc platforms
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects all development, deployment, content authoring
-->

## Decision

We will use the following integrated documentation platform stack:

- **Framework:** Docusaurus 3.9.2 (classic template with TypeScript)
- **Runtime:** Node.js 20.x LTS
- **Component Library:** React 18+ (included with Docusaurus)
- **Content Format:** Markdown/MDX for authoring
- **Search:** @easyops-cn/docusaurus-search-local (client-side)
- **Deployment:** Vercel with Git integration
- **Styling:** Infima CSS framework (built into Docusaurus) with custom CSS variables
- **Testing:** Jest + React Testing Library (unit) + Playwright (E2E)

## Consequences

### Positive

- **Zero backend required:** Static site generation eliminates server infrastructure, databases, and operational complexity
- **Built-in features:** Dark mode, mobile responsiveness, navigation, and SEO optimizations included out-of-the-box
- **Developer experience:** Hot reload, TypeScript support, and React component model enable rapid development
- **Content authoring:** Markdown/MDX is familiar to technical writers and supports code syntax highlighting natively
- **Client-side search:** No server-side indexing needed, works offline, zero operational cost
- **Deployment simplicity:** Vercel auto-detects Docusaurus, provides preview deployments, and handles CDN distribution
- **Performance:** Static site achieves <3s page load and >80 Lighthouse scores by default
- **Constitution compliance:** Meets all 9 principles including tech stack requirement and documentation-first research
- **Extensibility:** Plugin ecosystem allows adding features (chatbot, auth) in future phases without platform migration

### Negative

- **Vercel vendor lock-in:** Deployment tied to Vercel platform, migration to other hosts requires configuration changes
- **Client-side search limitations:** Search quality degrades with very large content volumes (>1000 pages), though Phase 1 has only ~17 pages
- **Build-time generation:** Content changes require full rebuild and redeployment (no dynamic updates)
- **React dependency:** Custom components require React knowledge, limiting contributor pool to React developers
- **Plugin maturity:** Community search plugins less mature than Algolia, may have bugs or missing features
- **TypeScript overhead:** Type definitions add initial setup complexity for custom components
- **Docusaurus learning curve:** Team must learn Docusaurus-specific conventions (frontmatter, _category_.json, sidebars.js)

## Alternatives Considered

### Alternative Stack A: VuePress + Algolia + Netlify
- **Framework:** VuePress 2.x with Vue 3
- **Search:** Algolia DocSearch (server-side crawling)
- **Deployment:** Netlify
- **Why rejected:**
  - Algolia requires server-side crawling (violates client-side search requirement)
  - VuePress has smaller ecosystem and less active development than Docusaurus
  - Netlify offers similar features to Vercel but less optimized for React apps
  - Constitution requires Docusaurus specifically

### Alternative Stack B: Next.js + Contentlayer + Vercel
- **Framework:** Next.js 14 with App Router
- **Content:** Contentlayer for MDX processing
- **Search:** Custom implementation with FlexSearch
- **Deployment:** Vercel
- **Why rejected:**
  - Requires building documentation features from scratch (navigation, sidebar, dark mode)
  - Higher development effort for MVP (weeks vs days)
  - Custom search implementation adds complexity and maintenance burden
  - Docusaurus provides better out-of-box documentation experience
  - Constitution requires Docusaurus specifically

### Alternative Stack C: GitBook + Built-in Search + GitBook Hosting
- **Platform:** GitBook SaaS
- **Search:** Built-in GitBook search
- **Deployment:** GitBook hosting
- **Why rejected:**
  - SaaS platform limits customization (can't add custom React components for future phases)
  - Vendor lock-in more severe (content and hosting tied to GitBook)
  - Harder to integrate chatbot, authentication in future phases
  - No local development environment
  - Constitution requires Docusaurus specifically

### Alternative Stack D: Docusaurus + Algolia + GitHub Pages
- **Framework:** Docusaurus 3.9.2
- **Search:** Algolia DocSearch (server-side)
- **Deployment:** GitHub Pages
- **Why rejected:**
  - Algolia requires server-side crawling (violates client-side search requirement from clarification)
  - GitHub Pages lacks preview deployments for branches
  - Slower build and deployment times compared to Vercel
  - Less optimized CDN performance
  - Clarification session explicitly chose Vercel over GitHub Pages

## References

- Feature Spec: [specs/001-textbook-mvp/spec.md](../../specs/001-textbook-mvp/spec.md)
- Implementation Plan: [specs/001-textbook-mvp/plan.md](../../specs/001-textbook-mvp/plan.md)
- Research Notes: [specs/001-textbook-mvp/research.md](../../specs/001-textbook-mvp/research.md)
- Docusaurus Official Docs: https://docusaurus.io/docs
- Constitution: [.specify/memory/constitution.md](../../.specify/memory/constitution.md)
- Related ADRs: None (first ADR)
