# Backend Bugs Report - Production Deployment

**Date**: 2026-03-02
**Environment**: Production (Render)
**Severity**: HIGH - Blocking core features

---

## Bug #1: Preferences API - Internal Server Error

**Status**: 🔴 CRITICAL
**Endpoint**: `POST /api/v1/preferences`
**HTTP Status**: 500 Internal Server Error

### Error Details
```
TypeError: 'preferred_language' is an invalid keyword argument for PersonalizationProfile
```

### Stack Trace
```
File "/opt/render/project/src/backend/src/services/preference_service.py", line 112, in create_preferences
    profile = PersonalizationProfile(
        user_id=user_id,
        is_personalized=is_personalized,
        **preferences  # <-- Error here
    )
```

### Root Cause
The API accepts `preferred_language` in the request body, but the `PersonalizationProfile` SQLAlchemy model doesn't have this field. Field name mismatch between API schema and database model.

### Impact
- Users cannot save language preferences
- Preference persistence feature non-functional
- Blocks T095 verification test

### Fix Required
**Option 1**: Update database model to include `preferred_language` field
**Option 2**: Update API to use correct field name from model
**Option 3**: Add field mapping in service layer

### Test Case
```bash
curl -X POST https://ai-native-book-backend.onrender.com/api/v1/preferences \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"preferred_language":"ur"}'
# Expected: 201 Created
# Actual: 500 Internal Server Error
```

---

## Bug #2: Chatbot Messages - Not Found

**Status**: 🔴 CRITICAL
**Endpoint**: `POST /api/chat/conversations/{conversation_id}/messages`
**HTTP Status**: 404 Not Found

### Error Details
```json
{"detail":"Not Found"}
```

### Root Cause
Endpoint exists in OpenAPI specification but returns 404. Possible causes:
1. Route not registered in FastAPI router
2. Path parameter name mismatch
3. Router not included in main app
4. Middleware blocking the route

### Impact
- RAG chatbot completely non-functional
- Cannot send messages or get AI responses
- Cannot verify OpenAI API integration
- Cannot verify Qdrant vector database integration
- Blocks T093 verification test

### Verification
```bash
# Conversation exists
curl -X GET https://ai-native-book-backend.onrender.com/api/chat/conversations \
  -H "Authorization: Bearer <token>"
# Returns: [{"id":"24bb3d1e-fabe-4b35-8a61-1b2c468917c2",...}]

# But sending message fails
curl -X POST https://ai-native-book-backend.onrender.com/api/chat/conversations/24bb3d1e-fabe-4b35-8a61-1b2c468917c2/messages \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"content":"What is physical AI?"}'
# Returns: 404 Not Found
```

### Fix Required
1. Check if chat router is included in main app
2. Verify route path matches OpenAPI spec
3. Ensure authentication dependency is correct
4. Test route registration

---

## Bug #3: Translation - Not Authenticated

**Status**: 🔴 CRITICAL
**Endpoint**: `POST /api/v1/translate`
**HTTP Status**: 401 Not Authenticated

### Error Details
```json
{"detail":"Not authenticated"}
```

### Root Cause
Endpoint requires authentication but doesn't accept the JWT token in Authorization header. Possible causes:
1. Authentication dependency missing from route
2. Different auth method expected (cookie vs header)
3. Token validation failing silently
4. CORS preflight blocking auth header

### Impact
- Translation feature non-functional
- Cannot translate content to Urdu
- Cannot verify OpenAI API integration
- Blocks T094 verification test

### Test Case
```bash
# Valid token works for other endpoints
curl -X GET https://ai-native-book-backend.onrender.com/api/v1/auth/me \
  -H "Authorization: Bearer <token>"
# Returns: 200 OK with user data

# But translation fails
curl -X POST https://ai-native-book-backend.onrender.com/api/v1/translate \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"chapter_id":"01-introduction","target_language":"ur"}'
# Returns: 401 Not Authenticated
```

### Fix Required
1. Add authentication dependency to translation route
2. Verify auth dependency is correctly configured
3. Check if route expects different auth method
4. Test with same auth used by working endpoints

---

## Summary

### Bugs by Severity
- 🔴 Critical: 3 bugs (all core features blocked)
- 🟡 Medium: 0 bugs
- 🟢 Low: 0 bugs

### Features Affected
- User Preferences (Bug #1)
- RAG Chatbot (Bug #2)
- Translation (Bug #3)

### Credentials Status
- ✅ Database: Working
- ✅ JWT: Working
- ❓ OpenAI API: Cannot test (bugs #2, #3)
- ❓ Qdrant: Cannot test (bug #2)

### Recommended Action
Fix all 3 bugs before proceeding with Phase 8 documentation, as these are core features that users will immediately encounter.

---

**Reporter**: Claude Opus 4.6
**Environment**: Production (https://ai-native-book-backend.onrender.com)
**Date**: 2026-03-02
