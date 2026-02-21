# Troubleshooting Guide - AI Native Book Project

## Purpose
This document records all issues encountered during development, their root causes, attempted solutions, and what actually worked. Use this to prevent token burn and solve issues quickly in future sessions.

---

## Issue 1: Bcrypt/Passlib Compatibility Error (2026-02-19)

### Symptoms
- Internal Server Error on `/api/auth/signup`
- Error: `AttributeError: module 'bcrypt' has no attribute '__about__'`
- Error: `ValueError: password cannot be longer than 72 bytes`

### Root Cause
- passlib 1.7.4 is incompatible with bcrypt 5.0.0
- passlib tries to access `bcrypt.__about__.__version__` which doesn't exist in bcrypt 5.x
- passlib 1.7.4 is unmaintained (last release 2020)

### Attempted Solutions
1. ❌ Upgrade passlib to newer version - No newer version exists
2. ❌ Downgrade bcrypt to 4.x - Would reintroduce original bug
3. ✅ **SUCCESSFUL**: Remove passlib entirely, use bcrypt directly

### Working Solution
```python
# backend/src/services/auth_service.py
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
```

### Files Modified
- `backend/src/services/auth_service.py` - Replaced passlib with bcrypt
- `backend/requirements.txt` - Removed `passlib[bcrypt]==1.7.4`, kept `bcrypt==5.0.0`

### Prevention
- Always check library compatibility before upgrading
- Prefer actively maintained libraries
- Use direct APIs instead of wrappers when possible

---

## Issue 2: Frontend Blank Screen - process.env Error (2026-02-19)

### Symptoms
- Browser shows blank white screen
- Console error: `Uncaught ReferenceError: process is not defined`
- Error at `authApi.ts:5:1`

### Root Cause
- `process.env` is a Node.js API, not available in browser
- Webpack doesn't automatically polyfill `process.env` in Docusaurus
- Code was using `process.env.NEXT_PUBLIC_API_URL` and `process.env.REACT_APP_API_URL`

### Attempted Solutions
1. ❌ Add webpack polyfill - Too complex, not recommended
2. ❌ Use environment variables plugin - Docusaurus doesn't support it easily
3. ✅ **SUCCESSFUL**: Use browser-safe window object checks with fallbacks

### Working Solution
```typescript
// textbook/src/services/authApi.ts
const API_URL = typeof window !== 'undefined' && (window as any).API_URL
  ? (window as any).API_URL
  : 'http://localhost:8001';

// textbook/src/services/personalizationApi.ts
const API_BASE_URL = typeof window !== 'undefined' && (window as any).API_BASE_URL
  ? (window as any).API_BASE_URL
  : 'http://localhost:8001/api/v1';
```

### Files Modified
- `textbook/src/services/authApi.ts` - Removed process.env
- `textbook/src/services/personalizationApi.ts` - Removed process.env

### Prevention
- Never use `process.env` in browser-side code
- Use `typeof window !== 'undefined'` checks for browser-only code
- Provide hardcoded fallbacks for development

### Important Note
- Must clear webpack cache after fixing: `rm -rf .docusaurus node_modules/.cache`
- Recompilation takes 4-5 minutes after cache clear

---

## Issue 3: CORS "Failed to Fetch" Error (2026-02-19)

### Symptoms
- Signup form submits but shows "Failed to fetch" error
- Network tab shows request blocked by CORS policy
- Browser console: CORS policy error

### Root Cause
- Backend CORS only allowed `http://localhost:3000`
- Frontend running on `http://localhost:3001`
- Browser blocks cross-origin requests without proper CORS headers

### Attempted Solutions
1. ❌ Add port 3001 to environment variable - Still used string split, fragile
2. ✅ **SUCCESSFUL**: Hardcode all development origins in array

### Working Solution
```python
# backend/src/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)
```

### Files Modified
- `backend/src/main.py` - Fixed CORS configuration

### Prevention
- Always configure CORS for all development ports
- Include both localhost and 127.0.0.1
- Test CORS with: `curl -I -X OPTIONS http://localhost:8001/api/auth/signup -H "Origin: http://localhost:3001"`
- Ensure backend runs on `0.0.0.0` for WSL2 compatibility

---

## Issue 4: Webpack Cache Serving Old Code (2026-02-19)

### Symptoms
- Code changes not reflected in browser
- Old errors persist after fixes
- Browser still shows `process.env` error after fix

### Root Cause
- Docusaurus/Webpack caches compiled bundles
- Cache not invalidated when source files change
- `.docusaurus` and `node_modules/.cache` contain stale builds

### Attempted Solutions
1. ❌ Browser hard refresh - Only clears browser cache, not webpack cache
2. ❌ Restart dev server - Cache persists across restarts
3. ✅ **SUCCESSFUL**: Clear all caches and rebuild

### Working Solution
```bash
# Stop all servers
pkill -9 -f docusaurus

# Clear all caches
rm -rf .docusaurus
rm -rf build
rm -rf node_modules/.cache

# Restart dev server
npm start -- --port 3001 --host 0.0.0.0
```

### Prevention
- Clear caches after major code changes
- Expect 4-5 minute recompilation after cache clear
- Use `--no-cache` flag if available

---

## Issue 5: Port Conflicts and Multiple Server Instances (2026-02-19)

### Symptoms
- "Address already in use" error
- Multiple docusaurus processes running
- Server not responding on expected port

### Root Cause
- Previous server instances not properly killed
- Background processes still holding ports
- Multiple npm start commands running

### Attempted Solutions
1. ❌ `pkill docusaurus` - Doesn't kill all child processes
2. ❌ Kill by process name - Misses some instances
3. ✅ **SUCCESSFUL**: Kill by port number

### Working Solution
```bash
# Kill process using specific port
lsof -ti:8001 | xargs kill -9 2>/dev/null
lsof -ti:3001 | xargs kill -9 2>/dev/null

# Or kill all docusaurus/uvicorn
pkill -9 -f "docusaurus|uvicorn"
```

### Prevention
- Always check running processes before starting servers
- Use `ps aux | grep -E "docusaurus|uvicorn"` to verify
- Kill by port number, not process name

---

## Issue 6: WSL2 Slow Compilation (2026-02-19)

### Symptoms
- Frontend compilation takes 4-5 minutes
- Much slower than expected
- File watching has delays

### Root Cause
- WSL2 cross-boundary file access is slow
- Node.js file watching in WSL2 has overhead
- Large codebase (5.8MB main.js bundle)

### Solutions
- ✅ Accept compilation time as normal for WSL2
- ✅ Avoid clearing cache unless necessary
- ✅ Use incremental builds (hot reload) instead of full rebuilds

### Prevention
- Don't clear cache unnecessarily
- Let webpack hot reload handle changes
- Consider moving project to native Linux filesystem for better performance

---

## Quick Reference: Common Commands

### Start Backend
```bash
cd /mnt/e/ai-native-book/backend
./venv/bin/python3 -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```

### Start Frontend
```bash
cd /mnt/e/ai-native-book/textbook
npm start -- --port 3001 --host 0.0.0.0
```

### Kill Servers
```bash
lsof -ti:8001 | xargs kill -9 2>/dev/null  # Backend
lsof -ti:3001 | xargs kill -9 2>/dev/null  # Frontend
```

### Clear Caches
```bash
cd /mnt/e/ai-native-book/textbook
rm -rf .docusaurus node_modules/.cache build
```

### Test CORS
```bash
curl -I -X OPTIONS http://localhost:8001/api/auth/signup \
  -H "Origin: http://localhost:3001" \
  -H "Access-Control-Request-Method: POST"
```

### Test API
```bash
curl -X POST http://localhost:8001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
```

---

## Token Burn Prevention Checklist

Before debugging:
- [ ] Read history.md for context
- [ ] Read TROUBLESHOOTING.md for known issues
- [ ] Check if issue is already documented
- [ ] Verify servers are running on correct ports
- [ ] Check browser console for exact error message

During debugging:
- [ ] Test one solution at a time
- [ ] Verify each fix before moving to next
- [ ] Clear caches when changing source code
- [ ] Use curl to test APIs directly
- [ ] Check CORS with OPTIONS request

After fixing:
- [ ] Document the issue in TROUBLESHOOTING.md
- [ ] Update history.md with session summary
- [ ] Test the fix end-to-end
- [ ] Commit changes with descriptive message

---

## Success Metrics

**Today's Session (2026-02-19):**
- Issues encountered: 6
- Issues resolved: 6
- Token usage: ~96K tokens
- Time to resolution: ~2 hours
- Authentication: ✅ Working
- Frontend: ✅ Working
- CORS: ✅ Fixed

**Key Learnings:**
1. Always check library compatibility before upgrading
2. Never use process.env in browser code
3. CORS must include all development ports
4. Clear webpack cache after major changes
5. WSL2 compilation is inherently slow
6. Kill processes by port number, not name

---

## Issue 7: JWT Secret Key Mismatch (2026-02-19)

### Symptoms
- Personalization API returns 401 Unauthorized
- Error: "Could not validate credentials"
- Signup/login works but preferences API fails

### Root Cause
- `auth_service.py` used `JWT_SECRET` environment variable
- `config.py` and `middleware/auth.py` used `JWT_SECRET_KEY`
- `.env` file had `JWT_SECRET_KEY`
- Tokens created with one secret, validated with another

### Working Solution
```python
# backend/src/services/auth_service.py
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "10080"))
```

### Files Modified
- `backend/src/services/auth_service.py`
- `backend/src/config.py`

### Prevention
- Use consistent environment variable names across all files
- Use centralized config module for all settings

---

## Issue 8: JWT Token Contains Email Instead of User ID (2026-02-19)

### Symptoms
- Personalization API returns "badly formed hexadecimal UUID string"
- Token validation succeeds but UUID parsing fails

### Root Cause
- JWT token stored `user.email` in "sub" field
- Middleware expected `user.id` (UUID string)

### Working Solution
```python
# backend/src/api/auth.py
access_token = create_access_token(data={"sub": str(user.id)})
```

### Files Modified
- `backend/src/api/auth.py`

### Prevention
- JWT "sub" field should always contain user ID, not email

---

## Issue 9: UUID Type Conversion in PreferenceHistory (2026-02-19)

### Symptoms
- Update preferences returns Internal Server Error
- Type mismatch when creating PreferenceHistory

### Root Cause
- `user_id` from JWT is a string
- PreferenceHistory model expects UUID type

### Working Solution
```python
# backend/src/services/preference_service.py
import uuid
user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
```

### Files Modified
- `backend/src/services/preference_service.py`

### Prevention
- Always convert JWT user_id strings to UUID when needed

---

## Issue 10: SQLAlchemy Session Cache Issue (2026-02-19)

### Symptoms
- Update preferences returns "Instance is not persistent within this Session"

### Root Cause
- Cached profile object not attached to current database session
- `db.refresh(profile)` fails on detached object

### Working Solution
```python
# Query fresh from database for updates, skip cache
result = await db.execute(
    select(PersonalizationProfile).where(PersonalizationProfile.user_id == user_id)
)
profile = result.scalar_one_or_none()
```

### Files Modified
- `backend/src/services/preference_service.py`

### Prevention
- Only use cache for read operations
- Always query fresh from DB for write operations

---

## Success Metrics Update

**Session 2 (2026-02-19 Afternoon):**
- Issues encountered: 4 (JWT secret, JWT payload, UUID conversion, cache)
- Issues resolved: 4
- Token usage: ~130K tokens
- Time to resolution: ~1.5 hours
- Phase 2 Backend: ✅ Complete

**Total Today:**
- Issues encountered: 10
- Issues resolved: 10
- Success rate: 100%
- Authentication: ✅ Working
- Personalization: ✅ Working

---

## Issue 11: User Lookup by Email Instead of ID (2026-02-19)

### Symptoms
- /me endpoint returns "User not found"
- Token validation succeeds but user lookup fails
- Console shows "No auth token found" after page refresh

### Root Cause
- JWT token contains user_id (UUID) in "sub" field
- /me endpoint's get_current_user() was calling `get_user_by_email(db, user_id)`
- Trying to look up user by UUID using email lookup function
- No user found because UUID is not an email

### Working Solution
```python
# backend/src/services/auth_service.py
async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    """Get a user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

# backend/src/api/auth.py
user_id = payload.get("sub")
user = await get_user_by_id(db, user_id)  # Changed from get_user_by_email
```

### Files Modified
- `backend/src/services/auth_service.py` - Added get_user_by_id()
- `backend/src/api/auth.py` - Updated get_current_user() to use get_user_by_id()

### Prevention
- Function names should match their parameters
- Add type hints to make expectations clear
- Test /me endpoint after changing JWT payload structure

---

## Success Metrics Final Update

**Session 3 (2026-02-19 Late Afternoon):**
- Issues encountered: 1 (user lookup bug)
- Issues resolved: 1
- Token usage: ~155K tokens
- Time to resolution: ~30 minutes
- All endpoints: ✅ Working

**Total Today (All Sessions):**
- Issues encountered: 11
- Issues resolved: 11
- Success rate: 100%
- Total tokens: ~385K tokens
- Total time: ~4 hours
- Authentication: ✅ Complete
- Personalization: ✅ Complete
- Phase 2 Backend: ✅ Complete

**Key Achievement:**
All 11 issues documented with root causes, solutions, and prevention strategies.
This documentation will prevent repeating these mistakes in future sessions.
