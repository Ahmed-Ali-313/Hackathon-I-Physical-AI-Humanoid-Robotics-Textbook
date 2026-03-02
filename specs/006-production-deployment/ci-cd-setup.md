# CI/CD Configuration

## Overview
Automated deployment pipeline configured for both frontend and backend services.

## Backend (Render)

**Service**: ai-native-book-backend
**Service ID**: srv-d6imb915pdvs73bnk5g0

### Configuration
- **Auto-Deploy**: ✅ Enabled
- **Trigger**: Commit to branch
- **Branch**: 006-production-deployment
- **Build Failure Handling**: Blocks deployment on build errors (default)
- **Deployment Time**: ~2-3 minutes
- **Health Check**: Automatic via `/health` endpoint

### Verified Settings (T074, T074a)
```json
{
  "autoDeploy": "yes",
  "autoDeployTrigger": "commit",
  "branch": "006-production-deployment",
  "pullRequestPreviewsEnabled": "no"
}
```

## Frontend (Vercel)

**Project**: textbook
**Production URL**: https://textbook-liart.vercel.app

### Configuration
- **Auto-Deploy**: ✅ Enabled (via Git integration)
- **Trigger**: Push to repository
- **Production Branch**: 006-production-deployment
- **Build Failure Handling**: Blocks deployment on build errors (default)
- **Deployment Time**: ~2 minutes
- **Preview Deployments**: Available for all branches

### Verified Settings (T075, T075a)
- Framework: Docusaurus (auto-detected)
- Build Command: `npm run build`
- Output Directory: `build`
- Install Command: `npm install`
- Root Directory: `textbook`

## CI/CD Workflow

### Automatic Deployment Flow
1. Developer pushes commit to `006-production-deployment` branch
2. GitHub webhook triggers both Render and Vercel
3. **Render Backend**:
   - Pulls latest code
   - Runs `pip install -r backend/requirements.txt`
   - Starts service with `uvicorn`
   - Performs health check
   - Routes traffic to new deployment
4. **Vercel Frontend**:
   - Pulls latest code
   - Runs `npm install` (with legacy-peer-deps)
   - Runs `npm run build`
   - Deploys to CDN
   - Updates production alias

### Deployment Verification
- Backend health: `curl https://ai-native-book-backend.onrender.com/health`
- Frontend status: `curl -I https://textbook-liart.vercel.app`

## Testing CI/CD (T081-T082)

To test automatic deployments:
```bash
# Make a small change
echo "# Test CI/CD" >> README.md
git add README.md
git commit -m "Test: Verify CI/CD auto-deploy"
git push origin 006-production-deployment

# Monitor deployments
# Render: https://dashboard.render.com/web/srv-d6imb915pdvs73bnk5g0
# Vercel: https://vercel.com/ahmed-alis-projects-a93d38a3/textbook
```

## Preview Deployments (T083-T086)

### Vercel Preview Deployments
- **Status**: ✅ Enabled for all branches
- **Trigger**: Push to any non-production branch
- **URL Pattern**: `https://textbook-<hash>-<project>.vercel.app`
- **Lifecycle**: Deleted when branch is deleted

### Render Preview Deployments
- **Status**: ❌ Disabled (free tier limitation)
- **Alternative**: Manual deployment from feature branches

## Environment Variables

### Syncing to GitHub Secrets (T086a)
Not required for current setup. Environment variables managed directly in:
- Render Dashboard: Service → Environment
- Vercel Dashboard: Project → Settings → Environment Variables

## Rollback Procedures

### Backend Rollback
```bash
# Via Render dashboard
# 1. Go to Deployments tab
# 2. Find previous successful deployment
# 3. Click "Redeploy"
```

### Frontend Rollback
```bash
# Via Vercel CLI
vercel rollback <previous-deployment-url>

# Or via dashboard
# 1. Go to Deployments
# 2. Find previous deployment
# 3. Click "..." → "Promote to Production"
```

## Monitoring

### Deployment Status
- Render: Email notifications on deployment failure
- Vercel: Dashboard shows deployment status in real-time

### Build Logs
- Render: Dashboard → Logs tab
- Vercel: Dashboard → Deployments → View Function Logs

## Security

- ✅ Environment variables not exposed in build logs
- ✅ Secrets managed via platform dashboards
- ✅ HTTPS enforced on all deployments
- ✅ Build failures block deployment

---

**Last Updated**: 2026-03-02
**Verified By**: Automated deployment testing
