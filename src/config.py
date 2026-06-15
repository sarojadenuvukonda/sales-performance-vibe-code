"""Configuration management for the sales performance analytics system."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "Sales Performance Analytics"
    environment: str = "development"
    debug: bool = True
    
    # Database
    database_url: str = "sqlite:///./data/sales_performance.db"
    
    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-3.5-turbo"
    
    # Paths
    raw_data_path: str = "./data/raw"
    processed_data_path: str = "./data/processed"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
