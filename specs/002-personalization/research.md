# Research & Technical Decisions: User Personalization System

**Feature**: 002-personalization
**Date**: 2026-02-17
**Status**: Phase 0 Complete

## Overview

This document captures research findings and technical decisions for implementing the user personalization system. All decisions are based on official documentation, best practices, and MVP constraints.

---

## Decision 1: Better-Auth Integration with FastAPI

### Context
Need to integrate Better-Auth (authentication system) with FastAPI backend to validate user sessions and associate preferences with authenticated users.

### Research Sources
- Better-Auth official documentation (https://better-auth.com)
- FastAPI security documentation (https://fastapi.tiangolo.com/tutorial/security/)
- JWT token validation patterns

### Decision
Use Better-Auth's JWT token validation with FastAPI dependency injection pattern.

**Implementation Approach**:
- Better-Auth issues JWT tokens on login
- Frontend includes JWT in Authorization header for all API requests
- FastAPI middleware validates JWT and extracts user_id
- Use FastAPI's `Depends()` for authentication dependency injection

**Code Pattern**:
```python
from fastapi import Depends, HTTPException, Header
from jose import jwt, JWTError

async def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/preferences")
async def get_preferences(user_id: str = Depends(get_current_user)):
    # user_id is automatically injected
    return fetch_preferences(user_id)
```

### Rationale
- Standard JWT pattern widely supported
- FastAPI's dependency injection keeps auth logic DRY
- Better-Auth handles token generation; we only validate
- Stateless validation (no session storage needed)

### Alternatives Considered
- **Session-based auth**: Rejected - requires server-side session storage, doesn't scale horizontally
- **OAuth2 password flow**: Rejected - Better-Auth already handles this, we just validate tokens
- **API keys**: Rejected - less secure, no user context

---

## Decision 2: Neon Postgres Connection Management

### Context
Need efficient database connection handling for Neon Serverless Postgres with FastAPI, supporting 1000 concurrent users.

### Research Sources
- Neon Postgres documentation (https://neon.tech/docs)
- SQLAlchemy async patterns (https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- FastAPI database integration guide

### Decision
Use SQLAlchemy 2.0 async engine with connection pooling.

**Implementation Approach**:
- SQLAlchemy async engine with asyncpg driver
- Connection pool: min=5, max=20 connections
- FastAPI lifespan events for pool initialization/cleanup
- Dependency injection for database sessions

**Code Pattern**:
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:pass@neon-host/db"

engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=15,
    pool_pre_ping=True  # Verify connections before use
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

### Rationale
- Neon recommends connection pooling for serverless
- Async engine matches FastAPI's async nature
- Pool size (5-20) handles 1000 concurrent users efficiently
- `pool_pre_ping` prevents stale connection errors

### Alternatives Considered
- **Direct asyncpg**: Rejected - SQLAlchemy ORM provides better abstraction and migrations
- **Sync SQLAlchemy**: Rejected - blocks event loop, poor performance
- **Prisma**: Rejected - adds Node.js dependency, complicates Python backend

---

## Decision 3: Docusaurus Content Metadata Storage

### Context
Need to store content metadata tags (hardware requirements, difficulty levels) for matching with user preferences.

### Research Sources
- Docusaurus frontmatter documentation (https://docusaurus.io/docs/markdown-features)
- MDX custom components guide
- Content plugin API

### Decision
Store metadata in Markdown frontmatter, sync to database on build.

**Implementation Approach**:
- Add custom frontmatter fields to each .md/.mdx file
- Build-time script extracts frontmatter and syncs to Postgres
- Backend API serves metadata for matching logic
- Frontend fetches metadata once per session

**Frontmatter Example**:
```yaml
---
id: nvidia-isaac-sim-intro
title: Introduction to NVIDIA Isaac Sim
personalization:
  hardware:
    - workstation_rtx_gpu
    - jetson_orin_nano
  software:
    ros2_level: intermediate
    isaac_level: beginner
---
```

**Sync Script**:
```python
# scripts/sync_content_metadata.py
import frontmatter
from pathlib import Path

def sync_metadata():
    for md_file in Path("docs").rglob("*.md"):
        post = frontmatter.load(md_file)
        if "personalization" in post.metadata:
            upsert_to_database(post["id"], post["personalization"])
```

### Rationale
- Frontmatter keeps metadata close to content (author convenience)
- Database enables fast querying without parsing files at runtime
- Build-time sync ensures consistency
- Authors can see/edit metadata directly in content files

### Alternatives Considered
- **Database-only**: Rejected - separates metadata from content, harder for authors
- **JSON sidecar files**: Rejected - extra files to maintain, easy to get out of sync
- **Runtime parsing**: Rejected - too slow, would violate <500ms load requirement

---

## Decision 4: User Preference Caching Strategy

### Context
Need to minimize database queries for preference retrieval (target: <200ms p95) while ensuring updates are immediately visible.

### Research Sources
- FastAPI caching patterns
- Redis vs in-memory caching
- Cache invalidation strategies

### Decision
Use in-memory LRU cache with TTL and explicit invalidation on updates.

**Implementation Approach**:
- Python `functools.lru_cache` with TTL wrapper
- Cache key: user_id
- TTL: 5 minutes (balances freshness and DB load)
- Explicit cache invalidation on preference updates
- Cache size: 1000 entries (covers all concurrent users)

**Code Pattern**:
```python
from functools import lru_cache
from datetime import datetime, timedelta

class CacheWithTTL:
    def __init__(self, ttl_seconds=300):
        self.cache = {}
        self.ttl = timedelta(seconds=ttl_seconds)

    def get(self, key):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                return value
            del self.cache[key]
        return None

    def set(self, key, value):
        self.cache[key] = (value, datetime.now())

    def invalidate(self, key):
        self.cache.pop(key, None)

preference_cache = CacheWithTTL(ttl_seconds=300)

async def get_preferences(user_id: str):
    cached = preference_cache.get(user_id)
    if cached:
        return cached

    prefs = await db.fetch_preferences(user_id)
    preference_cache.set(user_id, prefs)
    return prefs

async def update_preferences(user_id: str, new_prefs):
    await db.update_preferences(user_id, new_prefs)
    preference_cache.invalidate(user_id)  # Immediate visibility
```

### Rationale
- In-memory cache is fast (<1ms lookup)
- TTL prevents stale data for most cases
- Explicit invalidation ensures updates are immediate
- No external dependency (Redis) needed for MVP
- 1000-entry cache fits in memory (~1MB)

### Alternatives Considered
- **Redis**: Rejected - adds infrastructure complexity, overkill for 1000 users
- **No caching**: Rejected - would violate <200ms requirement under load
- **Longer TTL**: Rejected - users expect immediate updates (FR-010)
- **Database query cache**: Rejected - doesn't help with repeated same-user requests

---

## Decision 5: Docusaurus Personalization UI Integration

### Context
Need to add personalization UI (toggle, highlights, banners) to Docusaurus without breaking existing theme.

### Research Sources
- Docusaurus swizzling documentation (https://docusaurus.io/docs/swizzling)
- React Context API patterns
- Docusaurus theme customization guide

### Decision
Use React Context for personalization state + swizzled DocItem component for content highlighting.

**Implementation Approach**:
- Create `PersonalizationContext` to hold user preferences and view mode
- Swizzle `DocItem/Content` component to wrap content sections
- Custom `<Highlight>` component checks context and applies styling
- Toggle button in navbar updates context state

**Code Pattern**:
```tsx
// src/contexts/PersonalizationContext.tsx
export const PersonalizationContext = createContext({
  preferences: null,
  viewMode: 'personalized', // or 'full'
  setViewMode: (mode) => {}
});

// src/theme/DocItem/Content/index.tsx (swizzled)
export default function ContentWrapper(props) {
  const { preferences, viewMode } = useContext(PersonalizationContext);

  return (
    <PersonalizationProvider preferences={preferences} viewMode={viewMode}>
      <Content {...props} />
    </PersonalizationProvider>
  );
}

// Usage in MDX
<Highlight hardware="workstation_rtx_gpu">
  This section requires an RTX GPU workstation.
</Highlight>
```

### Rationale
- React Context is Docusaurus-native (no external state library)
- Swizzling allows theme customization without forking
- Component-based highlights are author-friendly
- Toggle in navbar is discoverable and accessible

### Alternatives Considered
- **Redux/Zustand**: Rejected - overkill for simple state, adds dependency
- **URL parameters**: Rejected - state doesn't persist across navigation
- **LocalStorage only**: Rejected - doesn't sync with backend, can get stale
- **CSS-only highlighting**: Rejected - can't conditionally render based on preferences

---

## Decision 6: Preference Dropdown Options

### Context
Need to define the exact dropdown options for hardware and software preferences (clarified in spec as "predefined dropdown options with Other field").

### Research Sources
- Project guide.md (hardware requirements section)
- Industry-standard experience level taxonomies
- Accessibility best practices for form dropdowns

### Decision
Define specific dropdown options based on project hardware tiers and standard skill levels.

**Hardware Dropdowns**:
1. **Workstation Type**:
   - No workstation
   - Standard workstation (no GPU)
   - Workstation with RTX GPU (12GB+ VRAM)
   - Workstation with RTX GPU (24GB+ VRAM)
   - Other (text field)

2. **Edge Kit Availability**:
   - No edge kit
   - NVIDIA Jetson Orin Nano
   - Intel RealSense camera
   - Both Jetson and RealSense
   - Other (text field)

3. **Robot Tier Access**:
   - No robot hardware
   - Quadruped (e.g., Unitree Go2)
   - Humanoid (e.g., Unitree G1)
   - Both quadruped and humanoid
   - Other (text field)

**Software Experience Dropdowns** (5 separate dropdowns):
- ROS 2 Experience: [None, Beginner, Intermediate, Advanced, Expert]
- Gazebo Experience: [None, Beginner, Intermediate, Advanced, Expert]
- Unity Experience: [None, Beginner, Intermediate, Advanced, Expert]
- NVIDIA Isaac Experience: [None, Beginner, Intermediate, Advanced, Expert]
- VLA Experience: [None, Beginner, Intermediate, Advanced, Expert]

### Rationale
- Hardware options match project guide.md specifications
- 5-level skill taxonomy is industry standard (clear progression)
- "Other" field handles edge cases without cluttering main options
- Separate software dropdowns enable precise matching (per clarification)

### Alternatives Considered
- **3-level skills**: Rejected - not granular enough for content matching
- **7-level skills**: Rejected - too many options, decision paralysis
- **Free-text hardware**: Rejected - makes matching logic impossible

---

## Decision 7: Content-to-Preference Matching Algorithm

### Context
Need to implement the exact match logic for showing "Recommended for your setup" (clarified in spec).

### Research Sources
- Specification clarifications (exact match requirement)
- Database indexing strategies for fast lookups
- Boolean logic patterns for multi-criteria matching

### Decision
Use exact match with AND logic for multiple criteria, OR logic within same category.

**Matching Rules**:
1. Content tagged with `hardware: [workstation_rtx_gpu]` matches users with that exact hardware
2. Content tagged with multiple hardware options uses OR: `[workstation_rtx_gpu, jetson_orin_nano]` matches users with EITHER
3. Content tagged with software level matches users at that level OR HIGHER: `ros2_level: intermediate` matches intermediate, advanced, expert
4. Content with multiple criteria uses AND: must match hardware AND software requirements

**Implementation**:
```python
def is_recommended(content_metadata, user_preferences):
    # Check hardware match (OR logic)
    if content_metadata.get("hardware"):
        hardware_match = any(
            hw in user_preferences.hardware
            for hw in content_metadata["hardware"]
        )
        if not hardware_match:
            return False

    # Check software level match (level >= required)
    if content_metadata.get("software"):
        for tool, required_level in content_metadata["software"].items():
            user_level = user_preferences.software.get(tool)
            if not user_level or LEVEL_ORDER[user_level] < LEVEL_ORDER[required_level]:
                return False

    return True

LEVEL_ORDER = {"none": 0, "beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}
```

### Rationale
- Exact match is simple, predictable, and fast
- OR within category (hardware) allows flexible content tagging
- AND across categories ensures content truly matches user setup
- Software level hierarchy (beginner < intermediate < advanced) is intuitive

### Alternatives Considered
- **Fuzzy matching**: Rejected - unpredictable, hard to explain to users
- **Weighted scoring**: Rejected - adds complexity, threshold tuning needed
- **ML-based**: Rejected - out of scope for MVP, requires training data

---

## Summary of Technical Decisions

| Area | Decision | Key Benefit |
|------|----------|-------------|
| Authentication | JWT validation with FastAPI Depends | Stateless, scalable, DRY |
| Database | SQLAlchemy async + connection pooling | Handles 1000 users, prevents stale connections |
| Content Metadata | Frontmatter + build-time sync | Author-friendly, fast queries |
| Caching | In-memory LRU with TTL + invalidation | <200ms retrieval, immediate updates |
| UI Integration | React Context + swizzled components | Docusaurus-native, no external deps |
| Dropdown Options | 3 hardware + 5 software (5-level scale) | Matches project specs, precise matching |
| Matching Logic | Exact match with AND/OR rules | Simple, predictable, fast |

## Next Steps

1. Create data-model.md with entity schemas based on these decisions
2. Create API contracts in contracts/ directory
3. Create quickstart.md with setup instructions
4. Proceed to task generation (/sp.tasks)
