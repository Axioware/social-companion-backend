"""
Configuration settings for the News API MCP Server.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv()
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # SerpAPI Configuration
    serpapi_api_key: Optional[str] = os.getenv("SERPAPI_API_KEY")
    serpapi_base_url: str = os.getenv("SERPAPI_BASE_URL")
    librivox_api: str = os.getenv("LIBRIVOX_API")
    
    # API Settings
    timeout: float = 30.0
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env


# Global settings instance
settings = Settings()
