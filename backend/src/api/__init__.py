"""
API Router Setup

This module provides the base APIRouter configuration for all API endpoints.
Individual routers (preferences, content, auth, translation, admin) will be registered here.
"""

from fastapi import APIRouter

# Create main API router with v1 prefix
api_router = APIRouter(prefix="/api/v1")

# Import and register routers
from src.api.preferences import router as preferences_router
from src.api.content import router as content_router
from src.api.translation import router as translation_router
from src.api.admin import router as admin_router
from src.api.auth import router as auth_router

api_router.include_router(preferences_router, tags=["preferences"])
api_router.include_router(content_router, tags=["content"])
api_router.include_router(translation_router, tags=["translation"])
api_router.include_router(admin_router, tags=["admin"])
api_router.include_router(auth_router, tags=["auth"])

__all__ = ["api_router"]
