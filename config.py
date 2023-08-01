from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    secret_key: str = Field("123456789")

    redis_url: str = Field('redis://localhost:6379/')

    class Config:
        env_file = ".env"

settings = Settings()
