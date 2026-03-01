# Vercel Deployment Configuration

**File**: `vercel.json` (optional, place in `/textbook` directory)
**Purpose**: Configure Vercel deployment for Docusaurus frontend

## Configuration (Optional)

Vercel auto-detects Docusaurus projects, so `vercel.json` is optional. If needed:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "build",
  "installCommand": "npm install",
  "framework": "docusaurus",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

## Field Descriptions

| Field | Value | Description |
|-------|-------|-------------|
| buildCommand | npm run build | Build Docusaurus static site |
| outputDirectory | build | Output directory for static files |
| installCommand | npm install | Install Node.js dependencies |
| framework | docusaurus | Framework detection (auto-detected) |
| rewrites | (see above) | Handle client-side routing |

## Environment Variables

**Set in Vercel dashboard** (Project Settings → Environment Variables)

| Variable | Example | Required | Scope |
|----------|---------|----------|-------|
| REACT_APP_API_URL | https://ai-native-book-backend.onrender.com | Yes | Production, Preview |

**Important**: Set for both Production and Preview environments

## Deployment Settings

**Root Directory**: `textbook` (set in Vercel dashboard)

**Build Settings**:
- Framework Preset: Docusaurus
- Build Command: `npm run build` (auto-detected)
- Output Directory: `build` (auto-detected)
- Install Command: `npm install` (auto-detected)

## Deployment Triggers

- **Automatic (Production)**: Push to `main` branch
- **Automatic (Preview)**: Pull request created/updated
- **Manual**: Via Vercel dashboard or CLI

## Preview Deployments

Each pull request gets a unique preview URL:
- Format: `https://ai-native-book-<pr-id>.vercel.app`
- Automatically updated on new commits
- Deleted when PR is closed

## Environment Variable Configuration

**Production**:
```
REACT_APP_API_URL=https://ai-native-book-backend.onrender.com
```

**Preview** (optional, for testing against staging backend):
```
REACT_APP_API_URL=https://ai-native-book-backend-staging.onrender.com
```

## Rollback Procedure

**Via Dashboard**:
1. Go to Vercel dashboard
2. Select project: ai-native-book
3. Go to "Deployments" tab
4. Find previous successful deployment
5. Click "..." → "Promote to Production"

**Via CLI**:
```bash
vercel rollback
```

## Performance Optimization

**Automatic Optimizations** (enabled by default):
- Image optimization
- Font optimization
- Code splitting
- Compression (gzip/brotli)
- Edge caching

**CDN Configuration**:
- Global edge network (automatic)
- Cache headers (automatic)
- No additional configuration needed

## Custom Domain (Optional)

**Setup**:
1. Go to Vercel dashboard
2. Select project: ai-native-book
3. Go to "Settings" → "Domains"
4. Add custom domain
5. Configure DNS records as instructed

**DNS Records** (example):
```
Type: CNAME
Name: www
Value: cname.vercel-dns.com
```

## Monitoring

**Analytics**: Available in Vercel dashboard
- Page views
- Unique visitors
- Top pages
- Geographic distribution

**Logs**: Available in Vercel dashboard under "Deployments" → "Logs"

## Troubleshooting

**Build fails**:
- Check build logs in Vercel dashboard
- Verify package.json scripts are correct
- Ensure all dependencies are in package.json

**Environment variable not working**:
- Verify variable name starts with `REACT_APP_`
- Check variable is set for correct environment (Production/Preview)
- Redeploy after adding/changing variables

**404 errors on routes**:
- Verify rewrites configuration in vercel.json
- Check Docusaurus routing configuration

**API calls failing**:
- Verify REACT_APP_API_URL is set correctly
- Check CORS configuration on backend
- Verify backend is deployed and healthy

## Free Tier Limitations

- Unlimited bandwidth
- Unlimited deployments
- 100GB bandwidth/month (soft limit)
- No credit card required

## References

- Vercel Documentation: https://vercel.com/docs
- Vercel CLI: https://vercel.com/docs/cli
- Docusaurus Deployment: https://docusaurus.io/docs/deployment#deploying-to-vercel
