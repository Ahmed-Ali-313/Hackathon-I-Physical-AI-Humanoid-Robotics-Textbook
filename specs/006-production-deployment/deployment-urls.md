# Production Deployment URLs

## Backend (Render)
- Service Name: ai-native-book-backend
- Service ID: srv-d6imb915pdvs73bnk5g0
- URL: https://ai-native-book-backend.onrender.com
- Health Check: https://ai-native-book-backend.onrender.com/health ✅ LIVE
- Dashboard: https://dashboard.render.com/web/srv-d6imb915pdvs73bnk5g0
- Status: ✅ DEPLOYED AND VERIFIED (2026-03-02)
- Deploy ID: dep-d6imeptactks73a1ca2g
- CORS: ✅ Configured for Vercel domain

## Frontend (Vercel)
- Project Name: ai-native-book
- URL: (pending deployment)
- Status: Not yet deployed

## Database (Neon)
- Status: ✅ Migrated (Phase 3 complete)
- Connection: Configured via DATABASE_URL environment variable

## Environment Variables Status

### Backend (Render) - 6 variables configured:
- [x] DATABASE_URL (from Neon - Phase 3) ✅
- [x] OPENAI_API_KEY (user provided) ✅
- [x] QDRANT_URL (user provided) ✅
- [x] QDRANT_API_KEY (user provided) ✅
- [x] JWT_SECRET_KEY (generated: 1d1df21fa279a0c843c348b4a4a9509f97a0b76cee74442f926dcc931de75a0c) ✅
- [x] FRONTEND_URL (placeholder: https://ai-native-book.vercel.app) ✅

### Frontend (Vercel) - 1 variable needed:
- [ ] REACT_APP_API_URL (after Render deployment)

---

Last updated: 2026-03-02
