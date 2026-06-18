from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'LifePlanner API'
    environment: str = 'development'
    api_v1_prefix: str = '/api/v1'
    secret_key: str = 'change-me'
    access_token_expire_minutes: int = 60 * 24
    algorithm: str = 'HS256'
    cors_origins: str = 'http://localhost:5173'

    database_url: str = 'sqlite:///./lifeplanner.db'

    admin_email: str = 'admin@local.dev'
    admin_password: str = 'admin1234'

    default_timezone: str = 'America/New_York'

    @field_validator('cors_origins')
    @classmethod
    def normalize_origins(cls, value: str) -> str:
        return ','.join([item.strip() for item in value.split(',') if item.strip()])

    @property
    def cors_origins_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(',') if item.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
