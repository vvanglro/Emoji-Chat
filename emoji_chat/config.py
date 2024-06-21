from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    DEBUG: bool = False

    REDIS_URL: str = "redis://127.0.0.1:6379"

    ROOM_MAX_ONLINE: int = 30


settings = Settings()
