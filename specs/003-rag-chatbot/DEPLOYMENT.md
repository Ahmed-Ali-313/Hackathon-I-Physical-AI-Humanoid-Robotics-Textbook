# RAG Chatbot Deployment Guide

**Version**: 1.0
**Last Updated**: 2026-02-26
**Status**: Production Ready

## Overview

This guide covers deploying the RAG chatbot system with:
- **Backend**: FastAPI + PostgreSQL + Qdrant (Railway/Render)
- **Frontend**: Docusaurus + React (Vercel)
- **Vector DB**: Qdrant Cloud
- **Database**: Neon Postgres (Serverless)

---

## Prerequisites

### Required Accounts
- [ ] Railway or Render account (backend hosting)
- [ ] Vercel account (frontend hosting)
- [ ] Qdrant Cloud account (vector database)
- [ ] Neon account (PostgreSQL database)
- [ ] OpenAI account (API access)

### Required Tools
- [ ] Git
- [ ] Node.js 18+ (for local testing)
- [ ] Python 3.11+ (for local testing)
- [ ] Railway CLI or Render CLI (optional)

---

## Part 1: Database Setup

### 1.1 Neon Postgres Setup

1. **Create Neon Project**
   ```bash
   # Go to https://neon.tech
   # Create new project: "ai-native-book-prod"
   # Select region: us-east-1 (or closest to your users)
   ```

2. **Get Connection String**
   ```bash
   # Copy connection string from Neon dashboard
   # Format: postgresql://user:password@ep-xxx.us-east-1.aws.neon.tech/dbname
   ```

3. **Run Migrations**
   ```bash
   cd backend

   # Set DATABASE_URL
   export DATABASE_URL="postgresql+asyncpg://user:password@ep-xxx.us-east-1.aws.neon.tech/dbname?ssl=require"

   # Run migrations
   python -c "
   import asyncio
   import asyncpg
   from pathlib import Path

   async def migrate():
       conn = await asyncpg.connect('postgresql://...')

       # Run migration
       with open('migrations/003_create_chat_tables.sql') as f:
           await conn.execute(f.read())

       await conn.close()

   asyncio.run(migrate())
   "
   ```

### 1.2 Qdrant Cloud Setup

1. **Create Qdrant Cluster**
   ```bash
   # Go to https://cloud.qdrant.io
   # Create cluster: "textbook-vectors-prod"
   # Select: 1GB RAM, 0.5 vCPU (sufficient for <10k vectors)
   # Region: us-east (match your backend region)
   ```

2. **Get API Credentials**
   ```bash
   # Copy from Qdrant dashboard:
   # - Cluster URL: https://xxx.qdrant.io
   # - API Key: qdr_xxx...
   ```

3. **Create Collection & Index Data**
   ```bash
   cd backend

   # Set environment variables
   export QDRANT_URL="https://xxx.qdrant.io"
   export QDRANT_API_KEY="qdr_xxx..."
   export OPENAI_API_KEY="sk-proj-..."

   # Create collection
   python scripts/create_qdrant_collection.py

   # Index textbook content
   python scripts/index_textbook.py

   # Verify indexing
   # Expected output: ~1000-2000 chunks indexed
   ```

---

## Part 2: Backend Deployment

### Option A: Railway Deployment

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Create Railway Project**
   ```bash
   cd backend
   railway init
   # Project name: ai-native-book-backend
   ```

3. **Configure Environment Variables**
   ```bash
   railway variables set DATABASE_URL="postgresql+asyncpg://..."
   railway variables set OPENAI_API_KEY="sk-proj-..."
   railway variables set QDRANT_URL="https://..."
   railway variables set QDRANT_API_KEY="qdr_..."
   railway variables set QDRANT_COLLECTION_NAME="textbook_chunks"
   railway variables set RAG_CONFIDENCE_THRESHOLD="0.3"
   railway variables set RAG_TOP_K_RESULTS="5"
   railway variables set CORS_ORIGINS="https://your-domain.vercel.app"
   railway variables set JWT_SECRET_KEY="your-production-secret-key"
   ```

4. **Deploy**
   ```bash
   railway up
   # Wait for deployment...
   # Get URL: https://xxx.railway.app
   ```

5. **Verify Deployment**
   ```bash
   curl https://xxx.railway.app/health
   # Expected: {"status": "healthy", "qdrant": "connected", "database": "connected"}
   ```

### Option B: Render Deployment

1. **Create Render Web Service**
   - Go to https://render.com
   - New → Web Service
   - Connect GitHub repo
   - Root directory: `backend`
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

2. **Configure Environment Variables**
   ```
   DATABASE_URL=postgresql+asyncpg://...
   OPENAI_API_KEY=sk-proj-...
   QDRANT_URL=https://...
   QDRANT_API_KEY=qdr_...
   QDRANT_COLLECTION_NAME=textbook_chunks
   RAG_CONFIDENCE_THRESHOLD=0.3
   RAG_TOP_K_RESULTS=5
   CORS_ORIGINS=https://your-domain.vercel.app
   JWT_SECRET_KEY=your-production-secret-key
   ```

3. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment
   - Get URL: https://xxx.onrender.com

---

## Part 3: Frontend Deployment

### Vercel Deployment

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   vercel login
   ```

2. **Configure Environment Variables**
   ```bash
   cd textbook

   # Create .env.production
   cat > .env.production << EOF
   REACT_APP_API_URL=https://xxx.railway.app
   REACT_APP_QDRANT_URL=https://xxx.qdrant.io
   EOF
   ```

3. **Deploy**
   ```bash
   vercel --prod
   # Follow prompts
   # Get URL: https://your-domain.vercel.app
   ```

4. **Update Backend CORS**
   ```bash
   # Update backend CORS_ORIGINS with Vercel URL
   railway variables set CORS_ORIGINS="https://your-domain.vercel.app"
   ```

---

## Part 4: Verification & Testing

### 4.1 Health Checks

```bash
# Backend health
curl https://xxx.railway.app/health

# Expected response:
{
  "status": "healthy",
  "qdrant": {
    "status": "connected",
    "collection": "textbook_chunks",
    "points_count": 1500
  },
  "database": {
    "status": "connected"
  },
  "openai": {
    "status": "configured"
  }
}
```

### 4.2 End-to-End Test

1. **Test RAG Query**
   ```bash
   curl -X POST https://xxx.railway.app/chat/conversations \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -d '{"title": "Test Conversation"}'

   # Get conversation_id from response

   curl -X POST https://xxx.railway.app/chat/conversations/{id}/messages \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -d '{"content": "What is VSLAM?"}'

   # Expected: Response with sources and confidence score
   ```

2. **Test Frontend**
   - Visit https://your-domain.vercel.app
   - Click chat button
   - Ask: "What is VSLAM?"
   - Verify: Response appears with source links

---

## Part 5: Monitoring & Maintenance

### 5.1 Monitoring Setup

**Railway/Render Metrics**
- CPU usage: <50% average
- Memory: <512MB average
- Response time: p95 <5s

**Qdrant Metrics**
- Query latency: <200ms
- Storage: Monitor vector count growth

**Neon Metrics**
- Active connections: <20
- Query time: <100ms average

### 5.2 Maintenance Tasks

**Weekly**
- [ ] Check error logs
- [ ] Review response times
- [ ] Monitor database size

**Monthly**
- [ ] Run cleanup script (delete old conversations)
- [ ] Review and optimize slow queries
- [ ] Update dependencies

**Quarterly**
- [ ] Re-index textbook content (if updated)
- [ ] Review and adjust confidence threshold
- [ ] Performance optimization review

---

## Part 6: Troubleshooting

### Common Issues

**Issue: "Qdrant connection failed"**
```bash
# Check Qdrant cluster status
curl https://xxx.qdrant.io/collections \
  -H "api-key: qdr_xxx..."

# Verify API key is correct
# Check cluster is not paused (Qdrant Cloud auto-pauses after inactivity)
```

**Issue: "Database connection timeout"**
```bash
# Check Neon project status
# Verify connection string format
# Ensure ?ssl=require is appended
```

**Issue: "CORS error in frontend"**
```bash
# Verify CORS_ORIGINS includes Vercel URL
# Check backend logs for CORS errors
# Ensure no trailing slash in URL
```

**Issue: "No search results returned"**
```bash
# Check vector count
curl https://xxx.railway.app/health

# Verify confidence threshold (try lowering to 0.2)
# Re-run indexing script if needed
```

---

## Part 7: Scaling Considerations

### Current Capacity
- **Users**: ~1000 concurrent
- **Requests**: ~100 req/min
- **Vectors**: ~2000 chunks
- **Database**: ~10k conversations

### Scaling Up

**Backend (>1000 concurrent users)**
- Upgrade Railway/Render plan (2GB RAM, 1 vCPU)
- Add Redis for caching
- Enable connection pooling

**Qdrant (>10k vectors)**
- Upgrade to 2GB RAM cluster
- Enable quantization for faster search

**Database (>100k conversations)**
- Upgrade Neon plan
- Add read replicas
- Implement archival strategy

---

## Part 8: Cost Estimation

### Monthly Costs (Production)

| Service | Plan | Cost |
|---------|------|------|
| Railway/Render | Starter | $5-10 |
| Qdrant Cloud | 1GB | $25 |
| Neon Postgres | Free tier | $0 |
| Vercel | Hobby | $0 |
| OpenAI API | Pay-as-you-go | $10-50 |
| **Total** | | **$40-85/month** |

### Cost Optimization Tips
- Use caching to reduce OpenAI API calls
- Implement rate limiting
- Archive old conversations
- Monitor and optimize query patterns

---

## Support & Resources

- **Documentation**: `/specs/003-rag-chatbot/`
- **Health Endpoint**: `https://xxx.railway.app/health`
- **Logs**: Railway/Render dashboard
- **Metrics**: Built-in metrics service (`/metrics` endpoint)

---

## Checklist: Production Readiness

- [ ] Database migrated and verified
- [ ] Qdrant collection created and indexed
- [ ] Backend deployed and health check passing
- [ ] Frontend deployed and accessible
- [ ] CORS configured correctly
- [ ] Environment variables set
- [ ] End-to-end test passing
- [ ] Monitoring configured
- [ ] Backup strategy in place
- [ ] Documentation updated

---

**Deployment Complete! 🚀**

Your RAG chatbot is now live and ready for production use.
