# Production Deployment URLs

## Backend (Render)
- Service Name: ai-native-book-backend
- URL: (pending deployment)
- Health Check: (pending)/health
- Status: Awaiting payment info setup

## Frontend (Vercel)
- Project Name: ai-native-book
- URL: (pending deployment)
- Status: Not yet deployed

## Database (Neon)
- Status: ✅ Migrated (Phase 3 complete)
- Connection: Configured via DATABASE_URL environment variable

## Environment Variables Status

### Backend (Render) - 6 variables needed:
- [ ] DATABASE_URL (from Neon - Phase 3)
- [ ] OPENAI_API_KEY (user provided)
- [ ] QDRANT_URL (user provided)
- [ ] QDRANT_API_KEY (user provided)
- [ ] JWT_SECRET_KEY (generated below)
- [ ] FRONTEND_URL (after Vercel deployment)

### Frontend (Vercel) - 1 variable needed:
- [ ] REACT_APP_API_URL (after Render deployment)

---

Last updated: 2026-03-02
