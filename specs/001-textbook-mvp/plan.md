# Implementation Plan: Physical AI & Humanoid Robotics Textbook (Phase 1 - MVP)

**Branch**: `001-textbook-mvp` | **Date**: 2026-02-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-textbook-mvp/spec.md`

## Summary

Build a professional, static documentation website using Docusaurus to deliver the Physical AI & Humanoid Robotics course content. Phase 1 focuses on core reading experience with navigation, search, and mobile responsiveness. The textbook will feature 4 main modules (ROS 2, Gazebo/Unity, NVIDIA Isaac, VLA) plus hardware requirements, deployed to Vercel with placeholder content to establish infrastructure before full content creation.

## Technical Context

**Language/Version**: JavaScript/TypeScript with Node.js 20.x LTS (Docusaurus 3.x requirement)
**Primary Dependencies**: Docusaurus 3.x, React 18+, MDX for content authoring
**Storage**: Static files (Markdown/MDX), no database required for Phase 1
**Testing**: Jest for unit tests, React Testing Library for component tests, Playwright for E2E
**Target Platform**: Web (all modern browsers), mobile-responsive
**Project Type**: Single static site (Docusaurus monorepo structure)
**Performance Goals**:
- Page load < 3 seconds on standard broadband
- Time to Interactive < 5 seconds
- Lighthouse score > 80 for all metrics
**Constraints**:
- Static site only (no backend for Phase 1)
- Client-side search only
- Vercel free tier limits (bandwidth, build minutes)
**Scale/Scope**:
- 4 modules + 3 hardware chapters = ~17 total pages
- Estimated 50-100 concurrent users for MVP
- Content size < 10MB total

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Deliverables-First
✅ **PASS** - Maps to "AI-Native Technical Textbook (Docusaurus-based)" deliverable

### Principle II: UI-First Development
✅ **PASS** - Phase 1 is UI-only (static site), no backend APIs to integrate

### Principle III: Mandatory Unit Testing
✅ **PASS** - Plan includes Jest + React Testing Library for 80% coverage

### Principle IV: Project History Tracking
✅ **PASS** - history.md will be updated after each milestone

### Principle V: Tech Stack Compliance
✅ **PASS** - Using Docusaurus (required), deploying to Vercel (clarified choice)

### Principle VI: Content Completeness
✅ **PASS** - All 4 modules + hardware chapters included in structure

### Principle VII: Deployment Readiness
✅ **PASS** - Vercel deployment with environment variables, automated builds

### Principle VIII: Documentation-First Research
✅ **PASS** - Docusaurus official documentation consulted, research.md complete with 8 decisions documented

### Principle IX: Dependency Installation
✅ **PASS** - npm install will be documented and required before all operations

**Overall Status**: ✅ READY TO PROCEED (pending Phase 0 research)

## Project Structure

### Documentation (this feature)

```text
specs/001-textbook-mvp/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file
├── research.md          # Phase 0 output (Docusaurus best practices)
├── data-model.md        # Phase 1 output (content structure)
├── quickstart.md        # Phase 1 output (setup guide)
├── contracts/           # Phase 1 output (N/A for static site)
└── tasks.md             # Phase 2 output (created by /sp.tasks)
```

### Source Code (repository root)

```text
textbook/                    # Docusaurus site root
├── docs/                    # Course content (Markdown/MDX)
│   ├── intro.md            # Landing page content
│   ├── module-1-ros2/      # Module 1: ROS 2
│   │   ├── _category_.json
│   │   ├── middleware.md
│   │   ├── nodes-topics-services.md
│   │   ├── python-ros-bridging.md
│   │   └── urdf-humanoids.md
│   ├── module-2-digital-twin/  # Module 2: Gazebo & Unity
│   │   ├── _category_.json
│   │   ├── physics-simulation.md
│   │   ├── rendering-interaction.md
│   │   └── sensor-simulation.md
│   ├── module-3-isaac/     # Module 3: NVIDIA Isaac
│   │   ├── _category_.json
│   │   ├── isaac-sim.md
│   │   ├── isaac-ros.md
│   │   └── nav2-planning.md
│   ├── module-4-vla/       # Module 4: Vision-Language-Action
│   │   ├── _category_.json
│   │   ├── llm-robotics.md
│   │   ├── voice-to-action.md
│   │   ├── cognitive-planning.md
│   │   └── capstone-project.md
│   └── hardware/           # Hardware Requirements
│       ├── _category_.json
│       ├── workstations.md
│       ├── edge-kits.md
│       └── robot-tiers.md
├── src/                    # Custom React components
│   ├── components/
│   │   ├── HomepageFeatures/
│   │   └── LandingHero/
│   ├── css/
│   │   └── custom.css
│   └── pages/
│       └── index.tsx       # Custom landing page
├── static/                 # Static assets
│   ├── img/
│   └── fonts/
├── docusaurus.config.js    # Main configuration
├── sidebars.js             # Navigation structure
├── package.json
├── tsconfig.json
└── vercel.json             # Vercel deployment config

tests/                      # Test suite
├── unit/
│   └── components/
├── integration/
└── e2e/
    └── navigation.spec.ts

.github/
└── workflows/
    └── deploy.yml          # CI/CD for Vercel
```

**Structure Decision**: Using standard Docusaurus structure with docs-based routing. The `docs/` directory contains all course content organized by module, with `_category_.json` files defining sidebar navigation. Custom landing page in `src/pages/index.tsx` provides the hero section and "Begin Your Journey" CTA. This structure supports hierarchical URLs (`/module-name/chapter-name`) as clarified.

## Complexity Tracking

> No constitution violations - this section is empty.

