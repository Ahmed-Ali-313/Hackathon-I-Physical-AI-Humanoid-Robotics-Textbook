# Physical AI & Humanoid Robotics Textbook

An interactive online textbook for learning Physical AI and Humanoid Robotics with an integrated RAG chatbot assistant.

## Features

- **Interactive Textbook**: 17 chapters covering ROS 2, Digital Twin, NVIDIA Isaac, and VLA
- **RAG Chatbot**: AI assistant grounded in textbook content with source attribution
- **Conversation History**: Persistent chat history across sessions
- **Selection Mode**: Ask questions about highlighted text
- **Theme Support**: Seamless light/dark mode switching
- **User Authentication**: Secure login and personalization
- **Mobile Responsive**: Works on desktop, tablet, and mobile devices

## Tech Stack

### Frontend
- **Framework**: Docusaurus 3.x (React-based)
- **Language**: TypeScript
- **Styling**: CSS Modules with Docusaurus theme variables
- **Testing**: Playwright (E2E), Jest (Unit)

### Backend
- **Framework**: FastAPI (Python 3.12)
- **Database**: SQLite (development), PostgreSQL (production)
- **Vector Database**: Qdrant Cloud
- **LLM**: OpenAI GPT-4o-mini
- **Embeddings**: OpenAI text-embedding-3-small (768 dimensions)
- **Testing**: pytest

## Prerequisites

- **Node.js**: 18.x or higher
- **Python**: 3.12 or higher
- **OpenAI API Key**: For chat and embeddings
- **Qdrant Cloud Account**: For vector search (optional for development)

## Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd ai-native-book
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your API keys:
# OPENAI_API_KEY=your_openai_api_key
# QDRANT_URL=your_qdrant_url (optional)
# QDRANT_API_KEY=your_qdrant_api_key (optional)

# Run database migrations
python scripts/run_migrations.py

# Index textbook content (requires Qdrant)
python scripts/index_textbook.py

# Start backend server
uvicorn src.main:app --reload --port 8001
```

Backend will be available at: http://localhost:8001

### 3. Frontend Setup

```bash
cd textbook

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will be available at: http://localhost:3000

## Environment Variables

### Backend (.env)

```bash
# Required
OPENAI_API_KEY=sk-...                    # OpenAI API key

# Optional (for vector search)
QDRANT_URL=https://...                   # Qdrant Cloud URL
QDRANT_API_KEY=...                       # Qdrant API key
QDRANT_COLLECTION_NAME=textbook_chunks   # Collection name

# Database
DATABASE_URL=sqlite+aiosqlite:///./app.db  # SQLite for development

# RAG Configuration
RAG_CONFIDENCE_THRESHOLD=0.3             # Confidence threshold for vector search
RAG_TOP_K=5                              # Number of results to retrieve
```

### Frontend

No environment variables required for development. Backend URL is auto-detected.

## Database Migrations

Run migrations to create database tables:

```bash
cd backend
python scripts/run_migrations.py
```

Migrations are located in `backend/migrations/`.

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_agent_service.py

# Run integration tests
pytest tests/integration/
```

### Frontend Tests

```bash
cd textbook

# Run unit tests
npm test

# Run E2E tests (requires backend running)
npm run test:e2e

# Run specific E2E test
npx playwright test tests/e2e/chat-history.spec.ts
```

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## Project Structure

```
ai-native-book/
├── backend/                    # FastAPI backend
│   ├── src/
│   │   ├── api/               # API endpoints
│   │   ├── models/            # Database models
│   │   ├── services/          # Business logic
│   │   ├── tools/             # Agent tools
│   │   └── middleware/        # Error handling
│   ├── tests/                 # Backend tests
│   ├── scripts/               # Utility scripts
│   └── migrations/            # Database migrations
├── textbook/                  # Docusaurus frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── contexts/          # React contexts
│   │   ├── hooks/             # Custom hooks
│   │   └── services/          # API clients
│   ├── docs/                  # Textbook content
│   └── tests/                 # Frontend tests
├── specs/                     # Feature specifications
└── history/                   # Development history
```

## Deployment

### Backend Deployment (Railway/Render)

1. Set environment variables in platform dashboard
2. Deploy from GitHub repository
3. Run migrations: `python scripts/run_migrations.py`
4. Index textbook: `python scripts/index_textbook.py`

### Frontend Deployment (Vercel)

1. Connect GitHub repository
2. Set build command: `npm run build`
3. Set output directory: `build`
4. Deploy

## Maintenance

### Cleanup Old Conversations

Run cleanup script to delete conversations older than 12 months:

```bash
cd backend

# Dry run (see what would be deleted)
python scripts/cleanup_old_conversations.py --dry-run

# Actually delete
python scripts/cleanup_old_conversations.py
```

Set up as a cron job to run monthly:
```bash
0 0 1 * * cd /path/to/backend && python scripts/cleanup_old_conversations.py
```

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (should be 3.12+)
- Verify virtual environment is activated
- Check .env file has OPENAI_API_KEY

### Chatbot returns "I don't have information"
- Verify Qdrant credentials in .env
- Run indexing script: `python scripts/index_textbook.py`
- Check RAG_CONFIDENCE_THRESHOLD (should be 0.3)

### Frontend can't connect to backend
- Verify backend is running on port 8001
- Check browser console for CORS errors
- Ensure API_BASE_URL is correct in chatApi.ts

## Contributing

1. Create feature branch from `main`
2. Follow Spec-Driven Development process
3. Write tests for new features
4. Update documentation
5. Create pull request

## License

[Add license information]

## Support

For issues and questions:
- GitHub Issues: [repository-url]/issues
- Documentation: [docs-url]
