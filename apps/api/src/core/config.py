from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "GenPos API"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/genpos"
    redis_url: str = "redis://localhost:6379"

    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "genpos-assets"

    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    openai_api_key: str = ""

    temporal_host: str = "localhost:7233"
    temporal_namespace: str = "genpos"

    cors_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
