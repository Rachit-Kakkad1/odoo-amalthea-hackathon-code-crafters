from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    This class loads environment variables from the .env file.
    All variables defined here MUST be present in your .env file.
    """
    # Database
    DATABASE_URL: str

    # Authentication
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    RESET_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email Settings
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str

    # SMS Settings from your .env file
    SMS_API_URL: str
    SMS_API_KEY: str
    SMS_SENDER_ID: str

    # Application Settings
    APP_NAME: str = "Expense Management System"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    class Config:
        # This tells pydantic-settings to load variables from a file named .env
        env_file = ".env"

# Create a single instance of the Settings class.
# The rest of your application will import this `settings` object.
settings = Settings()
