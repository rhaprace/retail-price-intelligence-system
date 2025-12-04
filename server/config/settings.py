"""
Configuration settings for the application.
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings."""
    
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: int = int(os.getenv('DB_PORT', 5432))
    DB_NAME: str = os.getenv('DB_NAME', 'retail_price_intelligence')
    DB_USER: str = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', '')
    
    DEFAULT_USER_AGENT: str = os.getenv(
        'USER_AGENT',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
    DEFAULT_TIMEOUT: int = int(os.getenv('REQUEST_TIMEOUT', 30))
    DEFAULT_RETRIES: int = int(os.getenv('MAX_RETRIES', 3))
    
    DEFAULT_RATE_LIMIT: int = int(os.getenv('DEFAULT_RATE_LIMIT', 60))


settings = Settings()

