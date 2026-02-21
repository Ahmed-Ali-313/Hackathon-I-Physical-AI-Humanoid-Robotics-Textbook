from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

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
# Allow both port 3000 and 3001 for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ],
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
from src.api.auth import router as auth_router

app.include_router(api_router)
app.include_router(auth_router)
