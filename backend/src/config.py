from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    database_url: str = "sqlite+aiosqlite:///./app.db"

    # Authentication - use same defaults as auth_service.py
    jwt_secret_key: str = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60 * 24 * 7  # 7 days

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000"

    # Cache Configuration
    preference_cache_ttl_seconds: int = 300
    preference_cache_max_size: int = 1000

    # Environment
    environment: str = "development"

    # RAG Chatbot Configuration (OpenAI-only)
    openai_api_key: str = ""

    # Qdrant Vector Database
    qdrant_url: str = ""
    qdrant_api_key: str = ""
    qdrant_collection_name: str = "textbook_chunks"

    # RAG Configuration
    rag_confidence_threshold: float = 0.7
    rag_top_k_results: int = 5
    rag_chunk_size: int = 1000
    rag_chunk_overlap: int = 100

    # Conversation Configuration
    max_conversations_per_user: int = 50
    max_messages_per_conversation: int = 500
    conversation_retention_months: int = 12
    session_expiry_minutes: int = 30

    # Message Limits
    max_user_message_length: int = 500
    max_ai_message_length: int = 2000

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"


# Global settings instance
settings = Settings()
