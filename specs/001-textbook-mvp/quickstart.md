# Quickstart Guide: Physical AI & Humanoid Robotics Textbook

**Feature**: 001-textbook-mvp
**Date**: 2026-02-16
**Purpose**: Step-by-step guide to set up, develop, and deploy the Docusaurus textbook locally

## Prerequisites

Before starting, ensure you have:

- **Node.js 20.x LTS** or higher ([Download](https://nodejs.org/))
- **npm 9.x** or higher (comes with Node.js)
- **Git** for version control
- **Code editor** (VS Code recommended)
- **Terminal/Command Line** access

**Verify Installation**:
```bash
node -v    # Should show v20.x.x or higher
npm -v     # Should show 9.x.x or higher
git --version
```

## Initial Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd "ai  native book"
git checkout 001-textbook-mvp
```

### 2. Install Dependencies

**CRITICAL**: Always install dependencies before running any commands (Constitution Principle IX)

```bash
cd textbook
npm install
```

This installs:
- Docusaurus 3.x
- React 18+
- TypeScript
- @easyops-cn/docusaurus-search-local (client-side search)
- All required dependencies

**Expected Output**:
```
added 1234 packages in 45s
```

### 3. Verify Installation

```bash
npm run docusaurus --version
```

Should output: `3.9.2` or similar

## Development Workflow

### Start Development Server

```bash
npm start
```

This command:
- Starts local development server at `http://localhost:3000`
- Enables hot reload (changes appear instantly)
- Opens browser automatically

**Expected Output**:
```
[SUCCESS] Docusaurus website is running at: http://localhost:3000/
```

### Project Structure Overview

```
textbook/
├── docs/                    # All course content (Markdown/MDX)
│   ├── module-1-ros2/      # Module 1 chapters
│   ├── module-2-digital-twin/
│   ├── module-3-isaac/
│   ├── module-4-vla/
│   └── hardware/
├── src/                     # Custom React components
│   ├── components/         # Reusable components
│   ├── css/               # Global styles
│   └── pages/             # Custom pages (landing page)
├── static/                 # Static assets (images, fonts)
├── docusaurus.config.js   # Main configuration
├── sidebars.js            # Navigation structure
└── package.json           # Dependencies
```

## Common Development Tasks

### Adding a New Chapter

1. **Create Markdown file** in appropriate module folder:
   ```bash
   touch docs/module-1-ros2/new-chapter.md
   ```

2. **Add frontmatter**:
   ```markdown
   ---
   sidebar_position: 5
   title: "New Chapter Title"
   description: "Brief description for SEO"
   keywords: ["keyword1", "keyword2"]
   ---

   # New Chapter Title

   Your content here...
   ```

3. **Save and check browser** - hot reload will show changes immediately

### Modifying Navigation

Edit `sidebars.js` to change sidebar structure:

```javascript
module.exports = {
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Module 1: ROS 2',
      items: [
        'module-1-ros2/middleware',
        'module-1-ros2/new-chapter',  // Add new chapter here
      ],
    },
  ],
};
```

### Customizing Styles

Edit `src/css/custom.css` for global styles:

```css
/* Light mode colors */
:root {
  --ifm-color-primary: #2e8555;
  --ifm-color-primary-dark: #29784c;
  /* ... */
}

/* Dark mode colors */
[data-theme='dark'] {
  --ifm-color-primary: #4e89e8;
  --ifm-color-primary-darker: #3a7bd5;
  /* ... */
}
```

### Testing Search Functionality

1. Build the site first (search index generated during build):
   ```bash
   npm run build
   npm run serve
   ```

2. Open `http://localhost:3000` and use search bar

3. Search should:
   - Return relevant chapters
   - Highlight search terms
   - Work offline (client-side)

### Adding Code Examples

Use fenced code blocks with language identifier:

```markdown
```python
import rclpy
from rclpy.node import Node

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
```
```

Supported languages: python, cpp, yaml, bash, json, xml

## Building for Production

### Build Static Site

```bash
npm run build
```

This command:
- Generates static HTML/CSS/JS in `build/` directory
- Optimizes assets for production
- Creates search index
- Validates all links

**Expected Output**:
```
[SUCCESS] Generated static files in "build"
[SUCCESS] Use `npm run serve` to test your build locally
```

### Test Production Build Locally

```bash
npm run serve
```

Opens production build at `http://localhost:3000`

**Differences from dev server**:
- No hot reload
- Optimized assets
- Search fully functional
- Matches production environment

## Deployment to Vercel

### First-Time Setup

1. **Install Vercel CLI** (optional):
   ```bash
   npm install -g vercel
   ```

2. **Connect Git Repository**:
   - Go to [vercel.com](https://vercel.com)
   - Click "Import Project"
   - Select your Git repository
   - Vercel auto-detects Docusaurus

3. **Configure Project**:
   - Framework Preset: Docusaurus
   - Build Command: `npm run build` (auto-detected)
   - Output Directory: `build` (auto-detected)
   - Install Command: `npm install` (auto-detected)
   - Node.js Version: 20.x (set in project settings)

### Automatic Deployments

Once connected:
- **Push to main branch** → Production deployment
- **Push to any branch** → Preview deployment
- **Pull requests** → Preview deployment with unique URL

### Manual Deployment (CLI)

```bash
cd textbook
vercel
```

Follow prompts to deploy.

## Testing

### Run Unit Tests

```bash
npm test
```

Tests custom React components using Jest + React Testing Library.

### Run E2E Tests

```bash
npm run test:e2e
```

Tests navigation, search, mobile responsiveness using Playwright.

### Check Test Coverage

```bash
npm run test:coverage
```

Must achieve 80% coverage for critical paths (Constitution Principle III).

## Troubleshooting

### Port 3000 Already in Use

```bash
# Kill process on port 3000
npx kill-port 3000

# Or use different port
npm start -- --port 3001
```

### Dependencies Out of Sync

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Build Fails

```bash
# Clear Docusaurus cache
npm run clear

# Rebuild
npm run build
```

### Search Not Working

Search only works in production build:
```bash
npm run build
npm run serve
```

Development server (`npm start`) doesn't generate search index.

## Development Best Practices

### Before Starting Work

1. **Pull latest changes**:
   ```bash
   git pull origin 001-textbook-mvp
   ```

2. **Install dependencies** (if package.json changed):
   ```bash
   npm install
   ```

3. **Start dev server**:
   ```bash
   npm start
   ```

### Before Committing

1. **Run tests**:
   ```bash
   npm test
   ```

2. **Build successfully**:
   ```bash
   npm run build
   ```

3. **Update history.md** with changes made

### Before Creating PR

1. **All tests pass**:
   ```bash
   npm test
   npm run test:e2e
   ```

2. **Build succeeds**:
   ```bash
   npm run build
   ```

3. **Test production build**:
   ```bash
   npm run serve
   ```

4. **Check constitution compliance** (see plan.md)

## Useful Commands Reference

| Command | Purpose |
|---------|---------|
| `npm install` | Install all dependencies |
| `npm start` | Start development server |
| `npm run build` | Build for production |
| `npm run serve` | Serve production build locally |
| `npm test` | Run unit tests |
| `npm run test:e2e` | Run E2E tests |
| `npm run test:coverage` | Check test coverage |
| `npm run clear` | Clear Docusaurus cache |
| `npm run docusaurus --version` | Check Docusaurus version |

## Environment Variables

For local development, create `.env.local`:

```bash
# Not needed for Phase 1 (static site only)
# Future phases may require:
# OPENAI_API_KEY=your_key_here
# QDRANT_URL=your_url_here
```

**Note**: Phase 1 is a static site with no backend, so no environment variables are required.

## Getting Help

- **Docusaurus Docs**: https://docusaurus.io/docs
- **Project Spec**: `specs/001-textbook-mvp/spec.md`
- **Implementation Plan**: `specs/001-textbook-mvp/plan.md`
- **Research Notes**: `specs/001-textbook-mvp/research.md`
- **Constitution**: `.specify/memory/constitution.md`

## Next Steps

After completing quickstart setup:

1. Review `specs/001-textbook-mvp/spec.md` for requirements
2. Review `specs/001-textbook-mvp/data-model.md` for content structure
3. Run `/sp.tasks` to generate implementation tasks
4. Begin UI-first development (Constitution Principle II)
5. Write unit tests for components (Constitution Principle III)
6. Update `history.md` after each session (Constitution Principle IV)

## Success Criteria

You've successfully set up the project when:

- ✅ Development server runs at `http://localhost:3000`
- ✅ Landing page displays with "Begin Your Journey" button
- ✅ All modules appear in sidebar navigation
- ✅ Dark mode toggle works
- ✅ Production build completes without errors
- ✅ Search works in production build
- ✅ Site is mobile-responsive

**Estimated Setup Time**: 10-15 minutes
