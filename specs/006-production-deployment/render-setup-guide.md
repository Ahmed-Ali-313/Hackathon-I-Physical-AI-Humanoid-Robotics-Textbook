# Render Backend Deployment Guide

## Prerequisites
✅ Branch pushed to GitHub: `006-production-deployment`
✅ JWT Secret generated: `1d1df21fa279a0c843c348b4a4a9509f97a0b76cee74442f926dcc931de75a0c`
⚠️ Payment info required: https://dashboard.render.com/billing

## Step 1: Add Payment Information (T037)
1. Visit https://dashboard.render.com/billing
2. Add credit card (required even for free tier)
3. Return here once complete

## Step 2: Create Web Service (T038-T039)
1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect GitHub repository: `Hackathon-I-Physical-AI-Humanoid-Robotics-Textbook`
4. Select branch: `006-production-deployment`
5. Render will auto-detect `render.yaml` configuration
6. Click "Create Web Service" and wait ~5 minutes for initial deployment

## Step 3: Configure Environment Variables (T040-T046)

Go to your service → "Environment" tab → Add the following 6 variables:

### 1. DATABASE_URL (T040)
```
postgresql+asyncpg://neondb_owner:<password>@<host>.neon.tech/neondb?ssl=require
```
**Source**: From Phase 3 Neon migration (check your Neon dashboard or local .env)

### 2. OPENAI_API_KEY (T041)
```
sk-proj-...
```
**Source**: Your OpenAI API key from https://platform.openai.com/api-keys

### 3. QDRANT_URL (T042)
```
https://<cluster-id>.gcp.cloud.qdrant.io
```
**Source**: Your Qdrant cluster URL from https://cloud.qdrant.io

### 4. QDRANT_API_KEY (T043)
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
**Source**: Your Qdrant API key from cluster settings

### 5. JWT_SECRET_KEY (T044)
```
1d1df21fa279a0c843c348b4a4a9509f97a0b76cee74442f926dcc931de75a0c
```
**Source**: Generated above ✅

### 6. FRONTEND_URL (T045)
```
https://ai-native-book.vercel.app
```
**Note**: Use placeholder for now, update after Vercel deployment in Phase 5

## Step 4: Save and Redeploy (T046)
1. Click "Save Changes"
2. Service will automatically redeploy with new environment variables
3. Wait ~3-5 minutes for deployment to complete

## Step 5: Test Backend (T047-T051)

### Copy Backend URL (T047)
From Render dashboard, copy your service URL (e.g., `https://ai-native-book-backend.onrender.com`)

### Test Health Check (T048-T049)
```bash
curl https://ai-native-book-backend.onrender.com/health
```
Expected: `200 OK` with JSON response showing all services healthy

### Test Authentication Endpoint (T050)
```bash
curl https://ai-native-book-backend.onrender.com/api/v1/auth/health
```
Expected: `200 OK`

### Test CORS Configuration (T051)
```bash
curl -H "Origin: https://ai-native-book.vercel.app" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://ai-native-book-backend.onrender.com/api/v1/auth/signup
```
Expected: CORS headers in response

## Step 6: Document Results (T052)
Update `deployment-urls.md` with:
- Backend URL
- Deployment timestamp
- Health check status

## Troubleshooting

### Build Fails
- Check Render logs for Python dependency errors
- Verify `backend/requirements.txt` is accessible
- Ensure Python version matches (3.11+)

### Health Check Fails
- Check environment variables are set correctly
- Verify DATABASE_URL connects to Neon
- Check Render logs for startup errors

### CORS Errors
- Verify FRONTEND_URL is set correctly
- Check backend CORS configuration in `src/main.py`
- Ensure Vercel domain matches exactly

---

**Next Steps**: Once backend is deployed and tested, proceed to Phase 5 (Frontend Deployment)
