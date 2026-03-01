from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from src.config import settings

# Load environment variables
load_dotenv()

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up personalization API...")
    yield
    # Shutdown
    print("Shutting down personalization API...")

# Create FastAPI app
app = FastAPI(
    title="Personalization API",
    description="API for managing user personalization preferences",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS - MUST be first middleware
# Support both local development and production Vercel URLs
cors_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001"
]

# Add production frontend URL if configured (for Vercel deployment)
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    cors_origins.append(frontend_url)
    # Also allow Vercel preview deployments (*.vercel.app)
    if "vercel.app" in frontend_url:
        cors_origins.append("https://*.vercel.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "personalization-api"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Personalization API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Register API routers
from src.api import api_router
from src.api.chat import router as chat_router

app.include_router(api_router)
app.include_router(chat_router)  # Chat router already has /api/chat prefix
