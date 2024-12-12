from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    secret_key: str = "development-secret-key-please-change"
    database_url: str = "sqlite:///./library.db"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

# Ensure required directories exist
os.makedirs("app/data", exist_ok=True)