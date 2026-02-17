# API Contracts

**Feature**: 001-textbook-mvp
**Date**: 2026-02-16

## Overview

Phase 1 is a **static Docusaurus site** with no backend APIs. Therefore, there are no traditional API contracts (REST endpoints, GraphQL schemas, etc.).

## Content Contracts

The "contracts" for this phase are the content structure and navigation schema, which are documented in:

- **data-model.md**: Defines Module, Chapter, and Navigation Item structures
- **sidebars.js**: Navigation configuration contract
- **Frontmatter schema**: Metadata contract for all Markdown files

## Future Phases

When backend APIs are added in future phases (chatbot, authentication, personalization), API contracts will be documented here:

- **Phase 2**: Authentication endpoints (Better-Auth)
- **Phase 3**: RAG chatbot endpoints (FastAPI + OpenAI)
- **Phase 4**: Personalization endpoints (user preferences)

## Static Site "Contracts"

### URL Contract

All chapter URLs follow the pattern: `/{module-slug}/{chapter-slug}`

Examples:
- `/module-1-ros2/middleware`
- `/module-2-digital-twin/physics-simulation`
- `/hardware/workstations`

### Navigation Contract

Sidebar structure defined in `sidebars.js`:
```javascript
{
  type: 'category',
  label: 'Module Name',
  items: ['module-slug/chapter-slug', ...]
}
```

### Content Contract

All Markdown files must include frontmatter:
```yaml
---
sidebar_position: number
title: string
description: string (optional)
keywords: string[] (optional)
---
```

### Search Contract

Search plugin indexes:
- Chapter titles
- Chapter content (excluding code blocks)
- Frontmatter keywords

Returns results with:
- Title
- Snippet (with highlighted terms)
- URL

## Notes

This directory will remain minimal for Phase 1. API contracts will be added when backend services are implemented in future phases.
