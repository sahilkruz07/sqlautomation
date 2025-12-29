from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    Application settings and configuration
    These can be overridden by environment variables
    """
    
    # Application settings
    APP_NAME: str = "SQL Automation API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database settings (SQL)
    DATABASE_URL: Optional[str] = None
    DB_ECHO: bool = False
    SQL_QUERY_ROW_LIMIT: int = 25
    
    # MongoDB settings
    MONGODB_URI: str = "mongodb://localhost:27017"  # Override with environment variable
    MONGODB_DB_NAME: str = "sqlautomation"
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    ALLOWED_ORIGINS: str = "*"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
