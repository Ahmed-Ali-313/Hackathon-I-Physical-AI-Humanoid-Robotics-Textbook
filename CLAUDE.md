# Claude Code Rules - AI-Native Textbook Project

This file contains project-specific instructions for Claude Code when working on the AI-Native Physical AI & Humanoid Robotics Textbook.

---

## 🎯 Project Overview

**Project Name**: AI-Native Textbook: Physical AI & Humanoid Robotics
**Type**: Educational Platform with AI-Powered Features
**Status**: ✅ Production (Live at https://textbook-liart.vercel.app)

**Core Features**:
- Interactive Docusaurus textbook (17 chapters)
- RAG chatbot with OpenAI GPT-4o-mini
- Urdu translation with RTL layout
- User authentication and preferences
- Real-time streaming responses
- Mobile responsive design

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: Docusaurus 3.x (Static Site Generator)
- **UI Library**: React 18
- **Language**: TypeScript 5.x
- **Styling**: CSS Modules
- **Deployment**: Vercel (Global CDN)
- **Port**: 3000 (local), 3001 (alternative)

### Backend
- **Framework**: FastAPI 0.115+
- **Language**: Python 3.12
- **Server**: Uvicorn (ASGI)
- **Validation**: Pydantic 2.x
- **Deployment**: Render (Oregon)
- **Port**: 8001

### Databases
- **Primary**: Neon Serverless Postgres (Production)
- **Local**: SQLite (Development)
- **Vector DB**: Qdrant Cloud (768-dim embeddings)

### AI/LLM
- **Chat Model**: OpenAI GPT-4o-mini
- **Embeddings**: text-embedding-3-small (768 dimensions)
- **RAG**: Retrieval-Augmented Generation with Qdrant

### Authentication
- **Method**: JWT-based authentication
- **Hashing**: bcrypt (8 rounds)
- **Token Expiry**: 7 days

---

## 📁 Project Structure

```
ai-native-book/
├── backend/                          # FastAPI backend
│   ├── src/
│   │   ├── api/                      # API endpoints
│   │   │   ├── auth.py               # Authentication (signup, login)
│   │   │   ├── chat.py               # Chatbot endpoints (streaming)
│   │   │   ├── translation.py        # Urdu translation
│   │   │   ├── preferences.py        # User preferences
│   │   │   └── admin.py              # Admin endpoints
│   │   ├── models/                   # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── conversation.py
│   │   │   ├── chat_message.py
│   │   │   ├── translated_chapter.py
│   │   │   └── personalization_profile.py
│   │   ├── services/                 # Business logic
│   │   │   ├── auth_service.py
│   │   │   ├── chat_service.py
│   │   │   ├── agent_service.py      # OpenAI integration
│   │   │   ├── embedding_service.py
│   │   │   ├── vector_service.py     # Qdrant integration
│   │   │   ├── translation_service.py
│   │   │   └── preference_service.py
│   │   ├── tools/                    # Agent tools
│   │   │   ├── retrieve_context_tool.py
│   │   │   └── vector_search_tool.py
│   │   ├── middleware/               # Middleware
│   │   │   ├── auth.py               # JWT verification
│   │   │   └── error_handler.py
│   │   ├── database.py               # Database configuration
│   │   ├── config.py                 # Settings management
│   │   └── main.py                   # FastAPI application
│   ├── tests/                        # Backend tests
│   │   ├── unit/
│   │   ├── integration/
│   │   └── conftest.py
│   ├── migrations/                   # SQL migrations
│   ├── scripts/                      # Utility scripts
│   │   ├── run_migrations.py
│   │   ├── index_textbook.py
│   │   └── deployment/
│   │       ├── migrate-to-neon.sh
│   │       └── rollback-database.sh
│   ├── requirements.txt
│   ├── .env.example
│   └── app.db                        # SQLite (local dev)
│
├── textbook/                         # Docusaurus frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatPanel/            # Main chat interface
│   │   │   ├── ChatButton/           # Floating chat button
│   │   │   ├── ConversationSidebar/  # Chat history
│   │   │   ├── MessageList/          # Message display
│   │   │   ├── MessageInput/         # Input field
│   │   │   ├── ErrorMessage/         # Error handling
│   │   │   └── TranslationControl/   # Translation button
│   │   ├── contexts/
│   │   │   ├── AuthContext.tsx
│   │   │   ├── ChatContext.tsx
│   │   │   └── LanguageContext.tsx
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── useChat.ts
│   │   │   ├── useTranslation.ts
│   │   │   └── useTextSelection.ts
│   │   ├── services/
│   │   │   ├── authApi.ts
│   │   │   ├── chatApi.ts            # SSE streaming
│   │   │   ├── translationApi.ts
│   │   │   └── personalizationApi.ts
│   │   ├── theme/
│   │   │   ├── Root.tsx              # App wrapper
│   │   │   └── DocItem/              # Custom doc page
│   │   └── css/
│   │       ├── custom.css            # Global styles
│   │       └── fonts.css             # Urdu fonts
│   ├── docs/                         # Textbook content (Markdown)
│   │   ├── intro.md
│   │   ├── module-1-ros2/
│   │   ├── module-2-digital-twin/
│   │   └── module-3-vla/
│   ├── static/
│   ├── tests/e2e/                    # Playwright tests
│   ├── docusaurus.config.js
│   ├── package.json
│   └── .env.example
│
├── specs/                            # Feature specifications
│   ├── 003-rag-chatbot/
│   ├── 005-urdu-translation/
│   └── 006-production-deployment/
│
├── history/                          # Development history
│   ├── prompts/                      # PHRs
│   ├── adr/                          # ADRs
│   └── history.md                    # Complete project history
│
├── .specify/                         # Spec-Kit Plus
│   └── memory/
│       └── constitution.md           # Project principles (v3.1.0)
│
├── README.md                         # Project documentation
├── CLAUDE.md                         # This file
└── render.yaml                       # Render deployment config
```

---

## 🚀 Development Commands

### Backend Commands

**Start Backend Server**:
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn src.main:app --reload --port 8001
```

**Run Database Migrations**:
```bash
cd backend
python scripts/run_migrations.py
```

**Index Textbook Content** (populate Qdrant):
```bash
cd backend
python scripts/index_textbook.py
```

**Run Backend Tests**:
```bash
cd backend
pytest                                    # All tests
pytest tests/unit/                        # Unit tests only
pytest tests/integration/                 # Integration tests only
pytest --cov=src --cov-report=html        # With coverage
```

**Database Migration** (SQLite → Neon):
```bash
cd scripts/deployment
./migrate-to-neon.sh
```

**Database Rollback**:
```bash
cd scripts/deployment
./rollback-database.sh
```

### Frontend Commands

**Start Frontend Server**:
```bash
cd textbook
npm start                                 # Default port 3000
npm start -- --port 3001                  # Alternative port
```

**Build for Production**:
```bash
cd textbook
npm run build
```

**Run Frontend Tests**:
```bash
cd textbook
npm test                                  # Unit tests
npm run test:e2e                          # E2E tests (requires backend)
```

**Deploy to Vercel**:
```bash
cd textbook
vercel --prod                             # Production deployment
vercel                                    # Preview deployment
```

### Git Commands

**Standard Workflow**:
```bash
git status                                # Check status
git add .                                 # Stage all changes
git commit -m "message"                   # Commit with message
git push origin main                      # Push to main (triggers CI/CD)
```

**Branch Management**:
```bash
git checkout -b feature-name              # Create new branch
git checkout main                         # Switch to main
git merge feature-name                    # Merge branch
```

---

## 🔧 Environment Variables

### Backend (.env)

**Required for Local Development**:
```bash
# Database
DATABASE_URL=sqlite+aiosqlite:///./app.db

# Authentication
JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=10080

# OpenAI
OPENAI_API_KEY=sk-proj-your-key-here

# Qdrant
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-key
QDRANT_COLLECTION_NAME=textbook_chunks

# RAG Configuration
RAG_CONFIDENCE_THRESHOLD=0.3
RAG_TOP_K_RESULTS=5

# CORS
FRONTEND_URL=http://localhost:3000
```

**Required for Production** (Render):
```bash
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require
OPENAI_API_KEY=sk-proj-your-key
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-key
JWT_SECRET_KEY=your-32-char-secret
FRONTEND_URL=https://textbook-liart.vercel.app
```

### Frontend (.env)

**Local Development**:
```bash
REACT_APP_API_URL=http://localhost:8001
```

**Production** (Vercel):
```bash
REACT_APP_API_URL=https://ai-native-book-backend.onrender.com
```

---

## 🌐 Production URLs

**Frontend**: https://textbook-liart.vercel.app
**Backend**: https://ai-native-book-backend.onrender.com
**API Docs**: https://ai-native-book-backend.onrender.com/docs
**Health Check**: https://ai-native-book-backend.onrender.com/api/health

---

## 🔄 CI/CD Pipeline

**Automatic Deployment Enabled**:
- Push to `main` branch triggers automatic deployments
- **Vercel**: Builds and deploys frontend (~45 seconds)
- **Render**: Builds and deploys backend (~3 minutes)

**Deployment Flow**:
```
git push origin main
    ↓
GitHub (main branch)
    ↓
    ├─→ Vercel: npm run build → Deploy to CDN
    └─→ Render: pip install → uvicorn start → Deploy
```

**No manual action required!**

---

## 🧪 Testing Strategy

### Backend Tests
- **Unit Tests**: Service layer logic (40+ tests)
- **Integration Tests**: API endpoints with database
- **Coverage Target**: 80%+

### Frontend Tests
- **Unit Tests**: Component testing with Jest
- **E2E Tests**: Full user flows with Playwright
- **Manual Testing**: Browser testing on mobile/desktop

---

## 🐛 Common Issues & Solutions

### Backend Won't Start
```bash
# Check Python version (must be 3.11+)
python --version

# Verify virtual environment
which python  # Should point to venv/bin/python

# Check .env file exists
ls -la backend/.env

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend Can't Connect to Backend
```bash
# Verify backend is running
curl http://localhost:8001/api/health

# Check CORS configuration
# Ensure FRONTEND_URL in backend/.env includes frontend URL

# Check browser console for errors
```

### Chatbot Returns "I don't have information"
```bash
# Verify Qdrant credentials
echo $QDRANT_URL
echo $QDRANT_API_KEY

# Re-index textbook
cd backend
python scripts/index_textbook.py

# Check RAG_CONFIDENCE_THRESHOLD (should be 0.3)
```

### Database Connection Fails
```bash
# For Neon, ensure SSL mode is required
# postgresql://user:pass@host/db?sslmode=require

# Test connection
python -c "from src.database import engine; print(engine)"
```

---

## 📝 Development Workflow

### Adding a New Feature

1. **Create Specification**:
   ```bash
   # Create spec directory
   mkdir -p specs/007-feature-name

   # Run spec-driven workflow
   /sp.specify "Feature description"
   /sp.plan
   /sp.tasks
   ```

2. **Implement Feature**:
   ```bash
   # Create feature branch
   git checkout -b 007-feature-name

   # Implement according to tasks.md
   # Write tests first (TDD)
   # Implement code
   # Run tests
   ```

3. **Test Locally**:
   ```bash
   # Backend tests
   cd backend && pytest

   # Frontend tests
   cd textbook && npm test

   # Manual testing
   # Start both servers and test in browser
   ```

4. **Deploy**:
   ```bash
   # Commit and push
   git add .
   git commit -m "Add feature: description"
   git push origin 007-feature-name

   # Merge to main (triggers auto-deploy)
   git checkout main
   git merge 007-feature-name
   git push origin main
   ```

### Fixing a Bug

1. **Reproduce the Bug**:
   - Test locally to confirm the issue
   - Check logs (Render dashboard for backend, browser console for frontend)

2. **Fix the Bug**:
   ```bash
   # Create fix branch
   git checkout -b fix-bug-description

   # Make minimal changes to fix the issue
   # Add test to prevent regression
   ```

3. **Test the Fix**:
   ```bash
   # Run relevant tests
   pytest tests/unit/test_affected_module.py

   # Manual testing
   # Verify fix works in browser
   ```

4. **Deploy**:
   ```bash
   # Commit and push to main
   git checkout main
   git merge fix-bug-description
   git push origin main  # Auto-deploys to production
   ```

---

## 🎨 Code Style Guidelines

### Python (Backend)
- **Formatter**: Black
- **Linter**: Flake8
- **Type Hints**: Required for all functions
- **Docstrings**: Required for public APIs
- **Async/Await**: Use for all I/O operations

### TypeScript (Frontend)
- **Formatter**: Prettier
- **Linter**: ESLint
- **Type Safety**: Strict mode enabled
- **Components**: Functional components with hooks
- **CSS**: CSS Modules for component styling

---

## 🔐 Security Guidelines

- **Never commit secrets**: Use .env files (gitignored)
- **JWT tokens**: 32+ character secret keys
- **Password hashing**: bcrypt with 8 rounds minimum
- **SQL injection**: Use SQLAlchemy ORM (never raw SQL)
- **XSS protection**: React escapes by default
- **CORS**: Whitelist specific origins only

---

## 📚 Key Architecture Decisions

See `history/adr/` for detailed ADRs:
- **ADR-0007**: Migrate from dual API to OpenAI-only
- **ADR-0008**: Translation architecture and caching strategy
- **ADR-0009**: RTL layout and typography implementation

---

## 🎯 Project Principles

See `.specify/memory/constitution.md` (v3.1.0) for complete principles:
- Spec-Driven Development (SDD)
- Test-Driven Development (TDD)
- Minimal viable changes
- Security-first approach
- User-centric design
- Performance optimization
- Accessibility compliance (WCAG 2.1 AA)

---

## 📞 Support & Resources

**Documentation**:
- API Docs: http://localhost:8001/docs (local)
- Project History: `history.md`
- Feature Specs: `specs/` directory

**External Resources**:
- FastAPI: https://fastapi.tiangolo.com
- Docusaurus: https://docusaurus.io
- OpenAI API: https://platform.openai.com/docs
- Qdrant: https://qdrant.tech/documentation

---

**Last Updated**: March 3, 2026
**Project Status**: ✅ Production Ready
**Version**: 1.0.0
