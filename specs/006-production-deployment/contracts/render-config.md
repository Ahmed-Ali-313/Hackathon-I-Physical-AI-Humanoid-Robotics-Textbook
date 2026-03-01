# Render Deployment Configuration

**File**: `render.yaml` (place in repository root)
**Purpose**: Configure Render Web Service for FastAPI backend deployment

## Configuration

```yaml
services:
  - type: web
    name: ai-native-book-backend
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && uvicorn src.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /api/health
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: QDRANT_URL
        sync: false
      - key: QDRANT_API_KEY
        sync: false
      - key: JWT_SECRET_KEY
        sync: false
      - key: FRONTEND_URL
        sync: false
```

## Field Descriptions

| Field | Value | Description |
|-------|-------|-------------|
| type | web | Web Service (persistent, not serverless) |
| name | ai-native-book-backend | Service name in Render dashboard |
| env | python | Python runtime environment |
| region | oregon | US West region (free tier) |
| plan | free | Free tier (750 hours/month) |
| buildCommand | pip install -r backend/requirements.txt | Install Python dependencies |
| startCommand | cd backend && uvicorn src.main:app --host 0.0.0.0 --port $PORT | Start FastAPI server |
| healthCheckPath | /api/health | Health check endpoint |
| envVars | (see below) | Environment variables (set in dashboard) |

## Environment Variables

**Important**: Set these in Render dashboard (not in render.yaml for security)

| Variable | Example | Required | Notes |
|----------|---------|----------|-------|
| DATABASE_URL | postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require | Yes | Neon connection string with SSL |
| OPENAI_API_KEY | sk-proj-xxx | Yes | OpenAI API key for chat/translation |
| QDRANT_URL | https://xxx.qdrant.io | Yes | Qdrant Cloud URL |
| QDRANT_API_KEY | xxx | Yes | Qdrant API key |
| JWT_SECRET_KEY | (32+ characters) | Yes | JWT signing secret (generate random) |
| FRONTEND_URL | https://ai-native-book.vercel.app | Yes | Production Vercel URL for CORS |

## Health Check Configuration

**Endpoint**: `/api/health`

**Expected Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2026-03-02T12:00:00Z",
  "services": {
    "database": "healthy",
    "openai": "healthy",
    "qdrant": "healthy"
  }
}
```

**Health Check Settings**:
- Interval: 60 seconds
- Timeout: 10 seconds
- Failure threshold: 3 consecutive failures

## Deployment Triggers

- **Automatic**: Push to `main` branch
- **Manual**: Via Render dashboard or CLI

## Free Tier Limitations

- 750 hours/month (31 days = 744 hours, so effectively always-on)
- Spins down after 15 minutes of inactivity
- Cold start: 20-30 seconds
- 512MB RAM
- Shared CPU

## Rollback Procedure

**Via Dashboard**:
1. Go to Render dashboard
2. Select service: ai-native-book-backend
3. Click "Manual Deploy"
4. Select previous commit from dropdown
5. Click "Deploy"

**Via CLI** (if Render CLI installed):
```bash
render deploy --service=ai-native-book-backend --commit=<previous-hash>
```

## Monitoring

**Logs**: Available in Render dashboard under "Logs" tab

**Metrics**: Available in Render dashboard under "Metrics" tab
- CPU usage
- Memory usage
- Request count
- Response time

## Troubleshooting

**Service won't start**:
- Check logs for missing environment variables
- Verify buildCommand completed successfully
- Ensure requirements.txt includes all dependencies

**Health check failing**:
- Verify /api/health endpoint exists
- Check database connection (DATABASE_URL)
- Verify OpenAI and Qdrant credentials

**Cold start delays**:
- Expected behavior on free tier
- Frontend should show "Waking up..." message
- Consider upgrading to paid tier for always-on

## References

- Render Documentation: https://render.com/docs
- Render YAML Reference: https://render.com/docs/yaml-spec
