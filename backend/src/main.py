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

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
app.include_router(api_router)
