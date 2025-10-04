from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic_settings import BaseSettings

# Config class for DB URL (can read from .env later)
class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./expenses.db"  # Default to SQLite
    # Example for PostgreSQL: DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/expenses"

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

settings = Settings()

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Set to False in production
    future=True
)

# Create async session
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI routes
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()