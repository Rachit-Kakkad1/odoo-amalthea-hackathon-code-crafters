from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./expenses.db"  # Default SQLite
    # Example for PostgreSQL: DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/expenses"

    # Authentication
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Email Notifications
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "your-email@gmail.com"
    SMTP_PASSWORD: str = "your-app-password"

    # External APIs
    COUNTRIES_API_URL: str = "https://restcountries.com/v3.1/all?fields=name,currencies"
    EXCHANGE_API_URL: str = "https://api.exchangerate-api.com/v4/latest/{base}"
    EXCHANGE_API_KEY: str | None = None  # Optional API key for premium tier
    QUICKBOOKS_API_URL: str | None = None
    STRIPE_API_KEY: str | None = None

    # Application Settings
    APP_NAME: str = "Expense Management System"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

settings = Settings()