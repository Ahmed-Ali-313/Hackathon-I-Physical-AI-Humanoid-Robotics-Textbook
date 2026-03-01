from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from src.config import settings

# Create async engine with connection pooling (only for PostgreSQL)
# SQLite doesn't support pooling parameters
engine_kwargs = {
    "echo": not settings.is_production,  # Log SQL queries in development
}

# Add pooling parameters only for PostgreSQL
if not settings.database_url.startswith("sqlite"):
    engine_kwargs.update({
        "pool_size": 5,
        "max_overflow": 10,
        "pool_pre_ping": True,  # Verify connections before use (prevents stale connections)
        "pool_recycle": 3600,  # Recycle connections after 1 hour
    })

engine = create_async_engine(settings.database_url, **engine_kwargs)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for SQLAlchemy models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Dependency function to get database session.

    Usage in FastAPI endpoints:
        @app.get("/example")
        async def example(db: AsyncSession = Depends(get_db)):
            # Use db session here
            pass
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize database - create all tables.

    Note: In production, use Alembic migrations instead.
    This is useful for development/testing.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """
    Close database connections.

    Call this during application shutdown.
    """
    await engine.dispose()
