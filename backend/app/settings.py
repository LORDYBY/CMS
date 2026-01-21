from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    ENV: str = "dev"

    app_timezone: str

    DATABASE_URL: str
    REDIS_URL: str

    JWT_SECRET: str
    JWT_ALGO: str = "HS256"

    MEDIA_ROOT: Path = Path("./media")
    MEDIA_PUBLIC_BASE_URL: str = "http://localhost"
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

settings = Settings()

