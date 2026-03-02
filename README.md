# 🤖 AI-Native Textbook: Physical AI & Humanoid Robotics

An intelligent, interactive online textbook for learning Physical AI and Humanoid Robotics, featuring an integrated RAG (Retrieval-Augmented Generation) chatbot assistant, Urdu translation support, and personalized learning experiences.

Built for **Hackathon I: Physical AI & Humanoid Robotics** - A comprehensive educational platform that combines cutting-edge AI technology with technical education.

---

## 📖 Project Overview

This project is an **AI-Native Technical Textbook** that revolutionizes how students learn complex robotics concepts. Unlike traditional static textbooks, this platform provides:

- **Interactive Learning**: 17 comprehensive chapters covering ROS 2, Digital Twin, NVIDIA Isaac Sim, and Vision-Language-Action (VLA) models
- **AI-Powered Assistance**: A RAG chatbot that answers questions grounded in textbook content with source attribution
- **Multilingual Support**: Urdu translation for accessibility to non-English speakers
- **Personalized Experience**: User authentication, conversation history, and preference management
- **Modern Web Experience**: Responsive design, dark mode, and seamless navigation

The platform bridges the gap between theoretical knowledge and practical understanding by providing instant, context-aware assistance while students read.

---

## ✨ Key Features

### 🎓 Educational Features
- **17 Comprehensive Chapters**: Covering Physical AI fundamentals, ROS 2, Digital Twin, NVIDIA Isaac Sim, and VLA models
- **Interactive Textbook**: Built with Docusaurus for fast, searchable, and mobile-responsive reading
- **Source Attribution**: Every AI response includes clickable links to relevant textbook sections
- **Selection-Based Questions**: Highlight text and ask specific questions about complex passages

### 🤖 AI-Powered Chatbot
- **RAG Architecture**: Retrieves relevant textbook chunks from Qdrant vector database before generating responses
- **Grounded Responses**: Prioritizes textbook content over general LLM knowledge to prevent hallucinations
- **Streaming Responses**: Real-time message streaming for better user experience
- **Conversation History**: Persistent chat history across sessions with user authentication
- **Uncertainty Handling**: Explicitly states when information is not available in the textbook

### 🌍 Multilingual Support
- **Urdu Translation**: Full chapter translation support for Urdu-speaking students
- **Translation Caching**: Translated chapters are cached for instant retrieval
- **Language Preferences**: User-specific language settings persist across sessions

### 🔐 User Management
- **Secure Authentication**: JWT-based authentication with Better-Auth
- **User Profiles**: Personalized preferences (language, theme, notification settings)
- **Session Management**: Secure session handling with automatic expiry
- **Privacy-First**: User data stored securely in Neon Postgres

### 🎨 User Experience
- **Dark/Light Mode**: Seamless theme switching with system preference detection
- **Mobile Responsive**: Optimized for desktop, tablet, and mobile devices
- **Fast Performance**: Static site generation with Vercel edge network
- **Accessibility**: WCAG-compliant design with keyboard navigation support

---

## 🛠️ Tech Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| **Docusaurus** | 3.x | Static site generator for documentation |
| **React** | 19.x | UI component library |
| **TypeScript** | 5.x | Type-safe JavaScript |
| **CSS Modules** | - | Component-scoped styling |
| **Vercel** | - | Deployment platform with global CDN |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | 0.115+ | High-performance Python web framework |
| **Python** | 3.11+ | Backend programming language |
| **Uvicorn** | - | ASGI server for async Python |
| **Pydantic** | 2.x | Data validation and settings management |
| **Render** | - | Backend hosting with persistent connections |

### Databases
| Technology | Purpose |
|------------|---------|
| **Neon Serverless Postgres** | User data, chat history, translations (production) |
| **SQLite** | Local development database |
| **Qdrant Cloud** | Vector database for semantic search (768-dim embeddings) |

### AI/LLM
| Technology | Purpose |
|------------|---------|
| **OpenAI GPT-4o-mini** | Chat completion and response generation |
| **text-embedding-3-small** | Generate 768-dimensional embeddings for RAG |
| **OpenAI API** | Unified API for chat and embeddings |

### Authentication & Security
| Technology | Purpose |
|------------|---------|
| **Better-Auth** | JWT-based authentication |
| **bcrypt** | Password hashing |
| **CORS Middleware** | Cross-origin request handling |

### Development Tools
| Technology | Purpose |
|------------|---------|
| **pytest** | Backend testing framework |
| **Playwright** | End-to-end frontend testing |
| **Black** | Python code formatting |
| **Prettier** | TypeScript/JavaScript formatting |
| **Claude Code** | AI-assisted development |
| **Spec-Kit Plus** | Spec-Driven Development workflow |

---

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js**: 20.x or higher ([Download](https://nodejs.org/))
- **Python**: 3.11 or higher ([Download](https://www.python.org/))
- **Git**: Latest version ([Download](https://git-scm.com/))

You'll also need API keys for:
- **OpenAI API Key**: [Get it here](https://platform.openai.com/api-keys)
- **Qdrant Cloud Account**: [Sign up here](https://cloud.qdrant.io) (free tier available)
- **Neon Postgres**: [Sign up here](https://neon.tech) (optional for local development)

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/Ahmed-Ali-313/ai-native-book.git
cd ai-native-book
```

#### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env

# Edit .env and add your credentials:
# OPENAI_API_KEY=sk-proj-your-key-here
# QDRANT_URL=https://your-cluster.qdrant.io
# QDRANT_API_KEY=your-qdrant-key-here
# DATABASE_URL=sqlite+aiosqlite:///./ai_native_book.db

# Run database migrations
python scripts/run_migrations.py

# Index textbook content into Qdrant (requires Qdrant credentials)
python scripts/index_textbook.py

# Start backend server
uvicorn src.main:app --reload --port 8001
```

Backend will be available at: **http://localhost:8001**

API Documentation:
- Swagger UI: **http://localhost:8001/docs**
- ReDoc: **http://localhost:8001/redoc**

#### 3. Frontend Setup

Open a new terminal window:

```bash
cd textbook

# Install dependencies
npm install

# Create .env file (optional for local development)
echo "REACT_APP_API_URL=http://localhost:8001" > .env

# Start development server
npm start
```

Frontend will be available at: **http://localhost:3000**

---

## 🔧 Configuration

### Backend Environment Variables

Create `backend/.env` with the following variables:

```bash
# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./ai_native_book.db

# Authentication
JWT_SECRET_KEY=your-secret-key-change-in-production-32-chars-min
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60

# API Configuration
API_HOST=0.0.0.0
API_PORT=8001
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-openai-api-key-here

# Qdrant Vector Database
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key-here
QDRANT_COLLECTION_NAME=textbook_chunks

# RAG Configuration
RAG_CONFIDENCE_THRESHOLD=0.3
RAG_TOP_K_RESULTS=5
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=100

# Conversation Configuration
MAX_CONVERSATIONS_PER_USER=50
MAX_MESSAGES_PER_CONVERSATION=500
CONVERSATION_RETENTION_MONTHS=12
```

### Frontend Environment Variables

Create `textbook/.env` (optional for local development):

```bash
# Backend API URL
REACT_APP_API_URL=http://localhost:8001

# Feature Flags
REACT_APP_ENABLE_PERSONALIZATION=true
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_chat_service.py

# Run integration tests only
pytest tests/integration/

# View coverage report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

### Frontend Tests

```bash
cd textbook

# Run unit tests
npm test

# Run E2E tests (requires backend running)
npm run test:e2e

# Run specific E2E test
npx playwright test tests/e2e/chatbot.spec.ts

# View test report
npx playwright show-report
```

---

## 📁 Project Structure

```
ai-native-book/
├── backend/                          # FastAPI backend
│   ├── src/
│   │   ├── api/                      # API endpoints
│   │   │   ├── v1/
│   │   │   │   ├── auth.py          # Authentication endpoints
│   │   │   │   ├── chat.py          # Chatbot endpoints
│   │   │   │   ├── translation.py   # Translation endpoints
│   │   │   │   └── preferences.py   # User preferences
│   │   ├── models/                   # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── conversation.py
│   │   │   └── translation.py
│   │   ├── services/                 # Business logic
│   │   │   ├── chat_service.py
│   │   │   ├── rag_service.py
│   │   │   └── translation_service.py
│   │   ├── database.py               # Database configuration
│   │   ├── config.py                 # Settings management
│   │   └── main.py                   # FastAPI application
│   ├── tests/                        # Backend tests
│   │   ├── unit/
│   │   ├── integration/
│   │   └── conftest.py
│   ├── migrations/                   # Database migrations
│   ├── scripts/                      # Utility scripts
│   │   ├── run_migrations.py
│   │   └── index_textbook.py
│   ├── requirements.txt              # Python dependencies
│   └── .env.example                  # Environment variables template
│
├── textbook/                         # Docusaurus frontend
│   ├── src/
│   │   ├── components/               # React components
│   │   │   ├── ChatBot/
│   │   │   ├── AuthModal/
│   │   │   └── TranslationButton/
│   │   ├── contexts/                 # React contexts
│   │   │   ├── AuthContext.tsx
│   │   │   └── ChatContext.tsx
│   │   ├── hooks/                    # Custom React hooks
│   │   │   ├── useAuth.ts
│   │   │   └── useChat.ts
│   │   ├── services/                 # API clients
│   │   │   ├── authApi.ts
│   │   │   ├── chatApi.ts
│   │   │   └── translationApi.ts
│   │   └── theme/                    # Custom theme
│   ├── docs/                         # Textbook content (Markdown)
│   │   ├── chapter-01/
│   │   ├── chapter-02/
│   │   └── ...
│   ├── static/                       # Static assets
│   ├── tests/                        # Frontend tests
│   │   └── e2e/
│   ├── docusaurus.config.js          # Docusaurus configuration
│   ├── package.json                  # Node dependencies
│   └── .env.example                  # Environment variables template
│
├── specs/                            # Feature specifications (SDD)
│   ├── 001-rag-chatbot/
│   ├── 002-authentication/
│   ├── 003-translation/
│   └── 006-production-deployment/
│
├── history/                          # Development history
│   ├── prompts/                      # Prompt History Records (PHR)
│   └── adr/                          # Architecture Decision Records
│
├── .specify/                         # Spec-Kit Plus configuration
│   ├── memory/
│   │   └── constitution.md           # Project principles
│   ├── templates/
│   └── scripts/
│
├── .gitignore
├── README.md                         # This file
└── CLAUDE.md                         # Claude Code instructions
```

---

## 🚢 Production Deployment

### Prerequisites

1. **Neon Account**: [Sign up](https://neon.tech) and create a database
2. **Render Account**: [Sign up](https://render.com) for backend hosting
3. **Vercel Account**: [Sign up](https://vercel.com) for frontend hosting
4. **GitHub Repository**: Push your code to GitHub

### Backend Deployment (Render)

1. **Connect GitHub Repository**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select branch: `main`

2. **Configure Service**:
   - Name: `ai-native-book-backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables**:
   - `DATABASE_URL`: Your Neon Postgres connection string
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `QDRANT_URL`: Your Qdrant cluster URL
   - `QDRANT_API_KEY`: Your Qdrant API key
   - `JWT_SECRET_KEY`: Generate with `openssl rand -hex 32`
   - `FRONTEND_URL`: Your Vercel deployment URL (add after frontend deployment)

4. **Deploy**: Click "Create Web Service"

### Frontend Deployment (Vercel)

Using Vercel CLI (already connected to GitHub):

```bash
cd textbook

# Login to Vercel (if not already logged in)
vercel login

# Deploy to production
vercel --prod

# Set environment variable
vercel env add REACT_APP_API_URL production
# Enter your Render backend URL: https://ai-native-book-backend.onrender.com
```

Or via Vercel Dashboard:
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New..." → "Project"
3. Import your GitHub repository
4. Configure:
   - Framework Preset: `Docusaurus`
   - Root Directory: `textbook`
   - Build Command: `npm run build`
   - Output Directory: `build`
5. Add Environment Variable:
   - Key: `REACT_APP_API_URL`
   - Value: `https://ai-native-book-backend.onrender.com`
6. Click "Deploy"

### Post-Deployment

1. **Update CORS**: Add Vercel URL to `FRONTEND_URL` in Render environment variables
2. **Run Migrations**: SSH into Render and run `python scripts/run_migrations.py`
3. **Index Textbook**: Run `python scripts/index_textbook.py` on Render
4. **Test Deployment**: Visit your Vercel URL and test all features

---

## 🐛 Troubleshooting

### Backend Issues

**Problem**: Backend won't start
```bash
# Check Python version
python --version  # Should be 3.11+

# Verify virtual environment is activated
which python  # Should point to venv/bin/python

# Check .env file exists
ls -la backend/.env

# Verify dependencies are installed
pip list | grep fastapi
```

**Problem**: Database connection fails
```bash
# Check DATABASE_URL format
echo $DATABASE_URL

# For Neon, ensure it includes ?sslmode=require
# postgresql://user:pass@ep-xxx.neon.tech/db?sslmode=require

# Test connection
python -c "from src.database import engine; print(engine)"
```

**Problem**: OpenAI API errors
```bash
# Verify API key is set
echo $OPENAI_API_KEY | head -c 10

# Check API key validity at https://platform.openai.com/api-keys
# Ensure you have sufficient credits
```

### Frontend Issues

**Problem**: Frontend can't connect to backend
```bash
# Check backend is running
curl http://localhost:8001/api/health

# Verify REACT_APP_API_URL in .env
cat textbook/.env

# Check browser console for CORS errors
# Ensure CORS_ORIGINS in backend/.env includes frontend URL
```

**Problem**: Chatbot returns "I don't have information"
```bash
# Verify Qdrant credentials
curl -H "api-key: $QDRANT_API_KEY" $QDRANT_URL/collections

# Re-index textbook
cd backend
python scripts/index_textbook.py

# Check RAG_CONFIDENCE_THRESHOLD (should be 0.3)
```

### Deployment Issues

**Problem**: Render deployment fails
- Check build logs in Render dashboard
- Verify `requirements.txt` includes all dependencies
- Ensure Python version is 3.11+ in Render settings

**Problem**: Vercel deployment fails
- Check build logs in Vercel dashboard
- Verify `package.json` has correct build script
- Ensure Node.js version is 20+ in Vercel settings

---

## 📚 Documentation

- **API Documentation**: Available at `/docs` endpoint when backend is running
- **Feature Specifications**: See `specs/` directory for detailed feature specs
- **Architecture Decisions**: See `history/adr/` for ADRs
- **Development History**: See `history.md` for project evolution

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Follow Spec-Driven Development**:
   - Create specification in `specs/`
   - Get approval before implementation
   - Write tests first (TDD)
4. **Commit your changes**: `git commit -m "Add feature: description"`
5. **Push to branch**: `git push origin feature/your-feature-name`
6. **Create Pull Request**

### Development Guidelines

- Follow the project constitution in `.specify/memory/constitution.md`
- Write tests for all new features (80% coverage minimum)
- Use Black for Python formatting, Prettier for TypeScript
- Update documentation for API changes
- Create PHR (Prompt History Record) for significant changes

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Ahmed Ali**
- GitHub: [@Ahmed-Ali-313](https://github.com/Ahmed-Ali-313)
- Project: [AI-Native Textbook](https://github.com/Ahmed-Ali-313/ai-native-book)

---

## 🙏 Acknowledgments

- **OpenAI** for GPT-4o-mini and embedding models
- **Qdrant** for vector database technology
- **Neon** for serverless Postgres
- **Docusaurus** for the amazing documentation framework
- **FastAPI** for the high-performance Python framework
- **Anthropic Claude** for AI-assisted development

---

## 📞 Support

For issues, questions, or feature requests:
- **GitHub Issues**: [Create an issue](https://github.com/Ahmed-Ali-313/ai-native-book/issues)
- **Discussions**: [Join the discussion](https://github.com/Ahmed-Ali-313/ai-native-book/discussions)

---

**Built with ❤️ for the Physical AI & Humanoid Robotics community**

## CI/CD Testing

Testing automatic deployment pipeline - 2026-03-02
