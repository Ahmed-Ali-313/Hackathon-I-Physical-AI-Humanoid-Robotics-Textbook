# Data Model: Physical AI & Humanoid Robotics Textbook

**Feature**: 001-textbook-mvp
**Date**: 2026-02-16
**Purpose**: Define content structure, metadata schema, and navigation hierarchy for the Docusaurus-based textbook

## Overview

This document defines the data structures for organizing course content in a static Docusaurus site. Since there's no database, "entities" represent file structures, frontmatter schemas, and navigation configurations.

## Content Entities

### Module

Represents a major course section grouping related chapters.

**Structure**:
```
docs/module-{id}-{slug}/
├── _category_.json
└── [chapter files]
```

**Category Configuration** (`_category_.json`):
```json
{
  "label": "Module {number}: {Full Title}",
  "position": {number},
  "link": {
    "type": "generated-index",
    "description": "{Module description}"
  },
  "collapsed": false
}
```

**Attributes**:
- `id`: Numeric identifier (1-4)
- `slug`: URL-friendly name (e.g., "ros2", "digital-twin", "isaac", "vla")
- `label`: Display name in sidebar (e.g., "Module 1: The Robotic Nervous System (ROS 2)")
- `position`: Order in sidebar (1-4)
- `description`: Brief overview shown on module index page
- `collapsed`: Whether sidebar group starts collapsed (false for all modules)

**Validation Rules**:
- Module ID must be unique (1-4)
- Slug must be lowercase, hyphenated, no special characters
- Label must match specification requirements
- Position determines sidebar order

**Instances**:
1. Module 1: ROS 2 (id: 1, slug: "module-1-ros2")
2. Module 2: Gazebo & Unity (id: 2, slug: "module-2-digital-twin")
3. Module 3: NVIDIA Isaac (id: 3, slug: "module-3-isaac")
4. Module 4: VLA (id: 4, slug: "module-4-vla")
5. Hardware Requirements (id: H, slug: "hardware")

### Chapter

Represents a single learning unit within a module.

**File Structure**:
```
docs/module-{id}-{slug}/{chapter-slug}.md
```

**Frontmatter Schema**:
```yaml
---
sidebar_position: {number}
title: "{Chapter Title}"
description: "{Brief description for SEO}"
keywords: ["{keyword1}", "{keyword2}", ...]
---
```

**Content Structure**:
```markdown
# {Chapter Title}

{Introduction paragraph}

## {Section 1}

{Content with text, lists, images}

## Code Examples

```{language}
{code block with syntax highlighting}
```

## Summary

{Conclusion paragraph}
```

**Attributes**:
- `sidebar_position`: Order within module (1-based)
- `title`: Display name in sidebar and page header
- `description`: SEO meta description (150-160 characters)
- `keywords`: Array of searchable terms
- `slug`: Derived from filename (e.g., "middleware.md" → "/module-1-ros2/middleware")
- `content`: Markdown/MDX body with headings, code blocks, images

**Validation Rules**:
- Title must be unique within module
- Sidebar position must be sequential (1, 2, 3, ...)
- Description must be 150-160 characters for optimal SEO
- Keywords must be relevant to chapter content
- Code blocks must specify language for syntax highlighting

**Relationships**:
- Belongs to exactly one Module
- Has sequential navigation (previous/next chapter)
- Appears in Module's sidebar group

### Navigation Item

Represents an entry in the sidebar navigation.

**Types**:
1. **Category** (Module): Expandable group containing chapters
2. **Doc** (Chapter): Link to individual chapter page
3. **Link** (External): External resource (not used in Phase 1)

**Hierarchy**:
```
Sidebar
├── Module 1: ROS 2 (Category)
│   ├── Introduction to ROS 2 Middleware (Doc)
│   ├── ROS 2 Nodes, Topics, and Services (Doc)
│   ├── Bridging Python Agents to ROS Controllers (Doc)
│   └── Understanding URDF for Humanoids (Doc)
├── Module 2: Digital Twin (Category)
│   ├── Physics Simulation in Gazebo (Doc)
│   ├── Rendering and Interaction in Unity (Doc)
│   └── Simulating Sensors (Doc)
├── Module 3: NVIDIA Isaac (Category)
│   ├── Isaac Sim (Doc)
│   ├── Isaac ROS (Doc)
│   └── Nav2 Path Planning (Doc)
├── Module 4: VLA (Category)
│   ├── LLM-Robotics Convergence (Doc)
│   ├── Voice-to-Action with Whisper (Doc)
│   ├── Cognitive Planning (Doc)
│   └── Capstone Project (Doc)
└── Hardware Requirements (Category)
    ├── Workstations (Doc)
    ├── Edge Kits (Doc)
    └── Robot Tiers (Doc)
```

**Configuration** (`sidebars.js`):
```javascript
module.exports = {
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Module 1: The Robotic Nervous System (ROS 2)',
      items: [
        'module-1-ros2/middleware',
        'module-1-ros2/nodes-topics-services',
        'module-1-ros2/python-ros-bridging',
        'module-1-ros2/urdf-humanoids'
      ],
    },
    // ... other modules
  ],
};
```

**Attributes**:
- `type`: 'category' or 'doc'
- `label`: Display text in sidebar
- `items`: Array of child navigation items (for categories)
- `id`: Document ID (for docs)

**Validation Rules**:
- Category must have at least one item
- Doc ID must reference existing markdown file
- Hierarchy must not exceed 2 levels (module → chapter)

### Code Example

Represents a code snippet within chapter content.

**Markdown Structure**:
```markdown
```{language}
{code content}
```
```

**Attributes**:
- `language`: Programming language identifier (python, cpp, yaml, bash, etc.)
- `content`: Raw code text
- `caption`: Optional description (via preceding text)

**Supported Languages**:
- Python (python, py)
- C++ (cpp, c++)
- YAML (yaml, yml)
- Bash (bash, sh)
- JSON (json)
- XML (xml)
- ROS Launch (xml with ros context)

**Validation Rules**:
- Language must be specified for syntax highlighting
- Code must be properly indented
- Special characters must be escaped if needed

### Landing Page

Custom React component for the homepage.

**File**: `src/pages/index.tsx`

**Structure**:
```typescript
export default function Home(): JSX.Element {
  return (
    <Layout>
      <HomepageHeader />
      <main>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}
```

**Components**:
- `HomepageHeader`: Hero section with title, description, CTA button
- `HomepageFeatures`: Module preview cards

**Attributes**:
- `title`: "Physical AI & Humanoid Robotics"
- `tagline`: Course description
- `ctaText`: "Begin Your Journey"
- `ctaLink`: "/docs/intro" or first chapter
- `features`: Array of module previews

**Validation Rules**:
- CTA button must link to valid docs page
- Features must match module structure
- Must be mobile-responsive

## URL Patterns

### Chapter URLs

**Pattern**: `/{module-slug}/{chapter-slug}`

**Examples**:
- `/module-1-ros2/middleware`
- `/module-2-digital-twin/physics-simulation`
- `/module-3-isaac/isaac-sim`
- `/module-4-vla/voice-to-action`
- `/hardware/workstations`

**Rules**:
- All lowercase
- Hyphens for word separation
- No special characters
- No trailing slashes
- Must be unique across entire site

### Module Index URLs

**Pattern**: `/{module-slug}`

**Examples**:
- `/module-1-ros2`
- `/module-2-digital-twin`
- `/module-3-isaac`
- `/module-4-vla`
- `/hardware`

**Behavior**: Auto-generated index page listing all chapters in module

### Special URLs

- `/` - Landing page (custom React component)
- `/docs/intro` - Optional introduction page
- `/search` - Search results page (if using search plugin with dedicated page)

## Content Metadata Schema

### Frontmatter Fields

**Required**:
```yaml
sidebar_position: number
title: string
```

**Optional**:
```yaml
description: string        # SEO meta description
keywords: string[]         # Search keywords
slug: string              # Custom URL (overrides filename)
hide_title: boolean       # Hide page title (default: false)
hide_table_of_contents: boolean  # Hide TOC (default: false)
```

**Example**:
```yaml
---
sidebar_position: 1
title: "Introduction to ROS 2 Middleware"
description: "Learn about ROS 2 middleware architecture and communication patterns for humanoid robotics"
keywords: ["ROS 2", "middleware", "DDS", "communication"]
---
```

## Navigation State

### Sidebar State

**Attributes**:
- `expanded`: Boolean indicating if sidebar is visible
- `activeCategory`: Currently selected module
- `activeDoc`: Currently viewed chapter

**Behavior**:
- Desktop: Sidebar visible by default, collapsible via toggle
- Mobile: Sidebar hidden by default, slides in as overlay
- State persists during navigation within site
- Active chapter highlighted in sidebar

### Sequential Navigation

**Attributes**:
- `previousChapter`: Link to previous chapter (null if first)
- `nextChapter`: Link to next chapter (null if last)

**Behavior**:
- Flows across module boundaries
- "Previous" button disabled on first chapter
- "Next" button disabled on last chapter or shows "Course Complete"

## Search Index

### Indexed Content

**Fields**:
- `title`: Chapter title
- `content`: Full chapter text (excluding code blocks)
- `keywords`: Frontmatter keywords
- `url`: Chapter URL
- `module`: Parent module name

**Exclusions**:
- Navigation elements
- Footer content
- Code block content (indexed separately if needed)

### Search Result

**Attributes**:
- `title`: Chapter title
- `snippet`: Text excerpt with search term highlighted
- `url`: Link to chapter
- `module`: Module name for context

## File System Structure

```
textbook/
├── docs/
│   ├── intro.md                          # Optional intro page
│   ├── module-1-ros2/
│   │   ├── _category_.json
│   │   ├── middleware.md
│   │   ├── nodes-topics-services.md
│   │   ├── python-ros-bridging.md
│   │   └── urdf-humanoids.md
│   ├── module-2-digital-twin/
│   │   ├── _category_.json
│   │   ├── physics-simulation.md
│   │   ├── rendering-interaction.md
│   │   └── sensor-simulation.md
│   ├── module-3-isaac/
│   │   ├── _category_.json
│   │   ├── isaac-sim.md
│   │   ├── isaac-ros.md
│   │   └── nav2-planning.md
│   ├── module-4-vla/
│   │   ├── _category_.json
│   │   ├── llm-robotics.md
│   │   ├── voice-to-action.md
│   │   ├── cognitive-planning.md
│   │   └── capstone-project.md
│   └── hardware/
│       ├── _category_.json
│       ├── workstations.md
│       ├── edge-kits.md
│       └── robot-tiers.md
├── src/
│   ├── components/
│   │   ├── HomepageFeatures/
│   │   │   ├── index.tsx
│   │   │   └── styles.module.css
│   │   └── LandingHero/
│   │       ├── index.tsx
│   │       └── styles.module.css
│   ├── css/
│   │   └── custom.css
│   └── pages/
│       └── index.tsx
├── static/
│   └── img/
│       ├── logo.svg
│       └── [module preview images]
├── docusaurus.config.js
├── sidebars.js
└── package.json
```

## Configuration Files

### docusaurus.config.js

**Key Sections**:
```javascript
module.exports = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'Master the fundamentals of humanoid robotics...',
  url: 'https://your-site.vercel.app',
  baseUrl: '/',

  themeConfig: {
    navbar: {
      title: 'Physical AI & Humanoid Robotics',
      items: [
        {
          type: 'doc',
          docId: 'intro',
          position: 'left',
          label: 'Course',
        },
        {
          type: 'search',
          position: 'right',
        },
      ],
    },

    colorMode: {
      defaultMode: 'light',
      disableSwitch: false,
      respectPrefersColorScheme: true,
    },

    footer: {
      style: 'dark',
      links: [],
      copyright: `Copyright © ${new Date().getFullYear()} Physical AI Course`,
    },
  },

  plugins: [
    [
      '@easyops-cn/docusaurus-search-local',
      {
        hashed: true,
        indexDocs: true,
        indexBlog: false,
        highlightSearchTermsOnTargetPage: true,
      },
    ],
  ],
};
```

### sidebars.js

**Structure**:
```javascript
module.exports = {
  tutorialSidebar: [
    // Auto-generated from _category_.json files
    // Or manually defined as shown in Navigation Item section
  ],
};
```

## Summary

This data model defines:
- 5 Module entities (4 course modules + hardware)
- 17 Chapter entities across all modules
- Hierarchical navigation structure
- URL patterns following `/module-name/chapter-name` convention
- Content metadata schema for frontmatter
- File system organization
- Configuration structure

All entities support the functional requirements from spec.md and align with Docusaurus best practices from research.md.
