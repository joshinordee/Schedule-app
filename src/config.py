from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import find_dotenv

class Settings(BaseSettings):
    gemini_api_key: str

    model_config = SettingsConfigDict(
        env_file=find_dotenv(),
        extra="ignore"

    )

@lru_cache
def get_settings() -> Settings:
    return Settings()
