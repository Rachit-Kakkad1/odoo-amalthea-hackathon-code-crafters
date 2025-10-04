from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./expenses.db"  # Default SQLite
    # Example for PostgreSQL: "postgresql+asyncpg://user:password@localhost:5432/expenses"
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "your-email@gmail.com"
    SMTP_PASSWORD: str = "your-app-password"
    EXCHANGE_API_KEY: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

settings = Settings()