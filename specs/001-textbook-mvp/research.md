# Research: Docusaurus Implementation for Phase 1 Textbook MVP

**Date**: 2026-02-16
**Feature**: 001-textbook-mvp
**Purpose**: Resolve technical unknowns and establish implementation approach based on official Docusaurus documentation

## Research Questions & Findings

### 1. Node.js Version & Environment Requirements

**Question**: What Node.js version is required for Docusaurus 3.x?

**Finding**: Node.js version 20.0 or above is required for Docusaurus 3.9.2 (current stable)

**Decision**: Use Node.js 20.x LTS
- **Rationale**: Meets minimum requirement, LTS provides stability for production
- **Alternatives Considered**:
  - Node.js 18.x: Below minimum requirement for Docusaurus 3.x
  - Node.js 21.x: Non-LTS, less stable for production use
- **Source**: https://docusaurus.io/docs/installation

### 2. Project Initialization Approach

**Question**: What's the recommended way to initialize a Docusaurus project?

**Finding**: Official command is `npx create-docusaurus@latest my-website classic`

**Decision**: Use classic template with TypeScript flag
- **Command**: `npx create-docusaurus@latest textbook classic --typescript`
- **Rationale**:
  - Classic template includes preset-classic with docs, blog, pages, and dark mode
  - TypeScript provides type safety for custom components
  - Official recommendation for quick starts
- **Alternatives Considered**:
  - JavaScript-only: Less type safety, harder to maintain custom components
  - Custom template: Unnecessary complexity for MVP
- **Source**: https://docusaurus.io/docs/installation

### 3. Client-Side Search Implementation

**Question**: Which local search plugin should we use for client-side search?

**Finding**: Multiple community plugins available:
- `docusaurus-lunr-search` - Offline search with Lunr.js
- `docusaurus-search-local` - Offline/local search
- `@easyops-cn/docusaurus-search-local` - With Chinese language support
- `@orama/plugin-docusaurus-v3` - Orama plugin for Docusaurus v3

**Decision**: Use `@easyops-cn/docusaurus-search-local`
- **Rationale**:
  - Most popular local search plugin for Docusaurus (based on community adoption)
  - Zero configuration required for basic setup
  - Supports highlighting search terms (required by FR-014)
  - Works offline/client-side (no backend needed)
  - Actively maintained for Docusaurus v3
- **Alternatives Considered**:
  - Algolia DocSearch: Requires server-side crawling, not client-side
  - `docusaurus-lunr-search`: Less feature-rich, older implementation
  - `@orama/plugin-docusaurus-v3`: Newer, less battle-tested
- **Installation**: `npm install --save @easyops-cn/docusaurus-search-local`
- **Source**: https://docusaurus.io/community/resources

### 4. Dark Mode Configuration

**Question**: How do we implement dark mode toggle?

**Finding**: Docusaurus has built-in dark mode support using data attributes and CSS custom properties

**Decision**: Use built-in dark mode with custom color palette
- **Rationale**:
  - Built into preset-classic, no additional plugins needed
  - Uses `data-theme='light'` and `data-theme='dark'` attributes
  - Respects system preferences automatically
  - Customizable via CSS custom properties
- **Implementation**:
  ```javascript
  // docusaurus.config.js
  themeConfig: {
    colorMode: {
      defaultMode: 'light',
      disableSwitch: false,
      respectPrefersColorScheme: true,
    }
  }
  ```
  ```css
  /* src/css/custom.css */
  :root {
    --ifm-color-primary: #2e8555;
    /* ... other light mode colors */
  }

  [data-theme='dark'] {
    --ifm-color-primary: #4e89e8;
    /* ... other dark mode colors */
  }
  ```
- **Alternatives Considered**:
  - Custom theme switcher: Unnecessary, built-in works well
  - Third-party theme plugin: Adds complexity without benefit
- **Source**: https://docusaurus.io/docs/styling-layout

### 5. URL Structure & Routing

**Question**: How do we implement hierarchical URL structure (`/module-name/chapter-name`)?

**Finding**: Docusaurus uses file-based routing with folder structure determining URLs

**Decision**: Use folder-based organization with slug frontmatter
- **Rationale**:
  - Folder structure naturally creates hierarchical URLs
  - `_category_.json` files control sidebar grouping and labels
  - Slug frontmatter allows custom URL paths if needed
  - Supports the clarified requirement for `/module-name/chapter-name` structure
- **Implementation**:
  ```
  docs/
  ├── module-1-ros2/
  │   ├── _category_.json          # Defines "Module 1: ROS 2" label
  │   ├── middleware.md            # URL: /module-1-ros2/middleware
  │   └── nodes-topics-services.md # URL: /module-1-ros2/nodes-topics-services
  ```
- **Alternatives Considered**:
  - Flat structure with manual routing: More complex, harder to maintain
  - Custom routing plugin: Unnecessary, file-based routing sufficient
- **Source**: https://docusaurus.io/docs/installation (folder structure section)

### 6. Vercel Deployment Configuration

**Question**: What configuration is needed for Vercel deployment?

**Finding**: Vercel auto-detects Docusaurus projects with minimal configuration

**Decision**: Use Vercel Git integration with auto-detection
- **Rationale**:
  - Vercel automatically detects Docusaurus and configures build settings
  - Git integration provides automatic deployments on push
  - Preview deployments for all branches
  - Production deployment for main branch
- **Configuration**:
  - Build Command: `npm run build` (auto-detected)
  - Output Directory: `build` (auto-detected)
  - Install Command: `npm install` (auto-detected)
  - Node.js Version: 20.x (set in Vercel project settings)
- **Optional `vercel.json`**:
  ```json
  {
    "buildCommand": "npm run build",
    "outputDirectory": "build",
    "framework": "docusaurus",
    "installCommand": "npm install"
  }
  ```
- **Alternatives Considered**:
  - GitHub Pages: Less features, slower deployments, no preview URLs
  - Netlify: Similar to Vercel but less optimized for React apps
  - Self-hosted: Unnecessary complexity for static site
- **Source**: https://docusaurus.io/docs/deployment

### 7. Content Structure & Placeholder Strategy

**Question**: How should we structure placeholder content for MVP?

**Finding**: Docusaurus uses Markdown/MDX files with frontmatter for metadata

**Decision**: Create minimal placeholder content with proper structure
- **Rationale**:
  - Establishes navigation and URL structure
  - Allows testing of all features (search, navigation, mobile)
  - Separates infrastructure from content creation
  - Each chapter gets ~200-300 words of placeholder text
- **Placeholder Content Template**:
  ```markdown
  ---
  sidebar_position: 1
  title: Chapter Title
  description: Brief chapter description
  ---

  # Chapter Title

  [Placeholder introduction paragraph explaining what this chapter will cover]

  ## Key Topics

  - Topic 1 (placeholder)
  - Topic 2 (placeholder)
  - Topic 3 (placeholder)

  ## Code Example

  ```python
  # Placeholder code example
  print("This is a placeholder")
  ```

  ## Summary

  [Placeholder summary paragraph]
  ```
- **Alternatives Considered**:
  - Lorem ipsum: Not domain-relevant, poor for testing search
  - Full content: Out of scope for Phase 1, delays infrastructure delivery
  - Empty files: Breaks navigation and search testing
- **Source**: Best practice from clarification session

### 8. Testing Strategy

**Question**: What testing tools should we use for Docusaurus?

**Finding**: Docusaurus is React-based, standard React testing tools apply

**Decision**: Use Jest + React Testing Library + Playwright
- **Rationale**:
  - Jest: Standard for React unit testing, built into Docusaurus
  - React Testing Library: Component testing with user-centric approach
  - Playwright: E2E testing for navigation, search, mobile responsiveness
  - Achieves 80% coverage requirement from constitution
- **Test Coverage**:
  - Unit: Custom React components (landing page, features)
  - Integration: Navigation flows, search functionality
  - E2E: Full user journeys from landing to chapter reading
- **Alternatives Considered**:
  - Cypress: Similar to Playwright but slower, less modern
  - Enzyme: Deprecated, not recommended for new projects
  - No E2E testing: Insufficient for validating mobile responsiveness
- **Source**: React testing best practices + constitution requirement

## Summary of Decisions

| Decision Area | Choice | Key Rationale |
|---------------|--------|---------------|
| Node.js Version | 20.x LTS | Meets Docusaurus 3.x requirement, stable |
| Project Template | Classic with TypeScript | Official recommendation, includes dark mode |
| Search Plugin | @easyops-cn/docusaurus-search-local | Client-side, zero config, actively maintained |
| Dark Mode | Built-in Docusaurus | No plugins needed, respects system preferences |
| URL Structure | Folder-based routing | Natural hierarchical URLs, easy to maintain |
| Deployment | Vercel Git integration | Auto-detection, preview deployments, fast |
| Content Strategy | Placeholder content | Separates infrastructure from content creation |
| Testing Stack | Jest + RTL + Playwright | Standard React tools, meets 80% coverage goal |

## Next Steps

1. Initialize Docusaurus project with TypeScript
2. Install local search plugin
3. Configure dark mode color palette
4. Create folder structure for all modules
5. Add placeholder content for each chapter
6. Configure Vercel deployment
7. Set up testing infrastructure

## References

- Docusaurus Official Documentation: https://docusaurus.io/docs
- Docusaurus Installation Guide: https://docusaurus.io/docs/installation
- Docusaurus Styling & Layout: https://docusaurus.io/docs/styling-layout
- Docusaurus Search: https://docusaurus.io/docs/search
- Docusaurus Deployment: https://docusaurus.io/docs/deployment
- Community Resources: https://docusaurus.io/community/resources
