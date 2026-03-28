from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # 앱 설정
    APP_ENV: str = "development"
    APP_SECRET_KEY: str = "change-this-secret-key"
    APP_DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # 데이터베이스
    DATABASE_URL: str = "postgresql://wiki_user:wiki_password@localhost:5432/opennaru"

    # JWT 설정
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]


settings = Settings()
