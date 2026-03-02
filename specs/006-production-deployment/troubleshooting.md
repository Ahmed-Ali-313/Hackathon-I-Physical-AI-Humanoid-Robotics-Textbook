# Deployment Troubleshooting Guide

## Common Issues and Solutions

### Backend Deployment Issues

#### Issue: Build fails with "pydantic-core compilation error"
**Symptom**: Render build fails during `pip install` with Rust compilation errors
**Cause**: Old pydantic version incompatible with Python 3.14
**Solution**:
```bash
# Update requirements.txt
pydantic>=2.10.0
pydantic-settings>=2.6.0
```

#### Issue: "email-validator not installed" error
**Symptom**: Application crashes on startup with ImportError
**Cause**: Pydantic 2.10+ requires email-validator for EmailStr
**Solution**:
```bash
# Add to requirements.txt
email-validator>=2.0.0
```

#### Issue: Database connection fails
**Symptom**: "could not connect to server" in logs
**Cause**: DATABASE_URL not configured or incorrect
**Solution**:
1. Verify DATABASE_URL in Render dashboard
2. Ensure format: `postgresql+asyncpg://user:pass@host/db?ssl=require`
3. Check Neon database is active

#### Issue: Cold start takes 30+ seconds
**Symptom**: First request after inactivity is very slow
**Cause**: Render free tier spins down after 15 minutes
**Solution**:
- Expected behavior on free tier
- Upgrade to paid tier for always-on service
- Or implement external ping service

---

### Frontend Deployment Issues

#### Issue: Build fails with "ERESOLVE could not resolve"
**Symptom**: Vercel build fails with React peer dependency conflicts
**Cause**: React 19 incompatible with @easyops-cn/docusaurus-search-local
**Solution**:
```bash
# Downgrade React in package.json
"react": "^18.2.0",
"react-dom": "^18.2.0"

# Add .npmrc file
legacy-peer-deps=true
```

#### Issue: Environment variables not loaded
**Symptom**: Frontend shows "undefined" for API URL
**Cause**: Environment variable not configured or wrong name
**Solution**:
1. Add via Vercel CLI: `vercel env add REACT_APP_API_URL production --value "https://backend-url" --yes`
2. Redeploy: `vercel redeploy <deployment-url>`
3. Verify in Vercel dashboard → Settings → Environment Variables

#### Issue: API calls fail with CORS error
**Symptom**: Browser console shows "CORS policy blocked"
**Cause**: Backend FRONTEND_URL doesn't match Vercel domain
**Solution**:
1. Update FRONTEND_URL in Render to exact Vercel URL
2. Wait for backend to redeploy (~3 minutes)
3. Clear browser cache and retry

---

### Database Issues

#### Issue: Migration fails with "relation already exists"
**Symptom**: Alembic migration fails
**Cause**: Schema already exists in target database
**Solution**:
```bash
# Mark migration as complete without running
alembic stamp head
```

#### Issue: Connection pool exhausted
**Symptom**: "connection pool exhausted" errors in logs
**Cause**: Too many concurrent connections
**Solution**:
1. Reduce pool size in database config
2. Enable connection pooling in Neon
3. Upgrade Neon plan for more connections

---

### CI/CD Issues

#### Issue: Auto-deploy not triggering
**Symptom**: Push to branch doesn't trigger deployment
**Cause**: Auto-deploy disabled or wrong branch configured
**Solution**:
1. Render: Check dashboard → Settings → Auto-Deploy = Yes
2. Vercel: Check dashboard → Git → Production Branch matches
3. Verify webhook in GitHub repository settings

#### Issue: Deployment succeeds but old code running
**Symptom**: Changes not visible after deployment
**Cause**: Browser cache or CDN cache
**Solution**:
1. Hard refresh browser (Ctrl+Shift+R)
2. Clear browser cache
3. Wait 5 minutes for CDN propagation
4. Check deployment URL directly (not alias)

---

### Authentication Issues

#### Issue: JWT token expired immediately
**Symptom**: User logged out right after login
**Cause**: JWT_SECRET_KEY mismatch or clock skew
**Solution**:
1. Verify JWT_SECRET_KEY is same across deployments
2. Check server time is correct
3. Increase JWT_EXPIRATION_MINUTES if needed

#### Issue: Signup fails with "user already exists"
**Symptom**: Cannot create account with email
**Cause**: Email already registered
**Solution**:
- Use different email
- Or implement password reset flow
- Check database for existing user

---

### Performance Issues

#### Issue: Slow API responses (>5s)
**Symptom**: API calls take very long
**Cause**: Database queries not optimized or cold start
**Solution**:
1. Check if cold start (first request after 15min)
2. Add database indexes for frequent queries
3. Enable query caching
4. Upgrade to paid tier

#### Issue: Frontend loads slowly
**Symptom**: Page takes >5s to load
**Cause**: Large bundle size or slow CDN
**Solution**:
1. Check bundle size: `npm run build` and review build/
2. Optimize images and assets
3. Enable code splitting
4. Use Vercel Analytics to identify bottlenecks

---

## Debugging Steps

### Backend Debugging
1. Check Render logs: Dashboard → Logs tab
2. Test health endpoint: `curl https://backend-url/health`
3. Test API docs: Visit `https://backend-url/docs`
4. Check environment variables: Dashboard → Environment tab
5. Review recent deployments: Dashboard → Deployments tab

### Frontend Debugging
1. Check Vercel logs: Dashboard → Deployments → View Function Logs
2. Open browser DevTools (F12) → Console tab
3. Check Network tab for failed requests
4. Verify environment variables: Dashboard → Settings → Environment Variables
5. Test deployment URL directly (not production alias)

### Database Debugging
1. Check Neon dashboard for connection status
2. Test connection: `psql $DATABASE_URL`
3. Review query performance in Neon dashboard
4. Check connection pool settings
5. Verify SSL is enabled

---

## Getting Help

### Documentation
- Render: https://render.com/docs
- Vercel: https://vercel.com/docs
- Neon: https://neon.tech/docs
- FastAPI: https://fastapi.tiangolo.com
- Docusaurus: https://docusaurus.io/docs

### Support Channels
- Render: support@render.com
- Vercel: support@vercel.com
- Neon: support@neon.tech

### Project-Specific
- Repository: https://github.com/Ahmed-Ali-313/Hackathon-I-Physical-AI-Humanoid-Robotics-Textbook
- Issues: Create GitHub issue with error logs and steps to reproduce

---

**Last Updated**: 2026-03-02
**Version**: 1.0.0
