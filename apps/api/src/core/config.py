from __future__ import annotations

import json
from typing import Union

from pydantic import Field, field_validator, model_validator
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
    s3_public_base_url: str = Field(
        default="",
        description=(
            "Public HTTPS base for object reads in the browser. "
            "Use R2 public bucket URL or a CDN origin; leave empty to use S3_ENDPOINT (OK for MinIO locally)."
        ),
    )

    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    openai_api_key: str = ""

    temporal_host: str = "localhost:7233"
    temporal_namespace: str = "default"
    temporal_task_queue: str = "genpos-tasks"
    use_temporal_for_generation: bool = Field(
        default=False,
        description="Run on-demand generation as a Temporal workflow (worker process required).",
    )
    use_temporal_for_daily_batch: bool = Field(
        default=False,
        description="Run POST /generate/daily/run as a Temporal workflow (BL-201).",
    )

    max_concurrent_generation_jobs: int = Field(
        default=10,
        description="Per-merchant cap on pending+running generation jobs (BL-111).",
    )
    generation_job_timeout_seconds: int = Field(
        default=900,
        description="Mark stale pending/running jobs as failed after this age (seconds).",
    )

    llm_secondary_api_key: str = ""
    llm_secondary_base_url: str = ""
    llm_secondary_model: str = "gpt-4o-mini"

    image_generation_enabled: bool = Field(
        default=True,
        description="If false, only local placeholder images are used (no OpenAI Images API).",
    )
    image_gen_model: str = Field(
        default="dall-e-3",
        description="OpenAI Images model (e.g. dall-e-3, dall-e-2, gpt-image-1).",
    )
    image_gen_size_cover: str = Field(
        default="1024x1792",
        description="Portrait-friendly cover size (DALL-E 3: 1024x1792 | 1792x1024 | 1024x1024).",
    )
    image_gen_size_carousel: str = Field(
        default="1024x1024",
        description="Square carousel slide size for DALL-E 3.",
    )
    image_gen_quality: str = Field(
        default="standard",
        description="DALL-E 3 quality: standard | hd",
    )
    image_gen_style: str = Field(
        default="vivid",
        description="DALL-E 3 style: vivid | natural",
    )

    cors_origins: Union[str, list[str]] = ["http://localhost:3000"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: object) -> list[str]:
        """Accept JSON array or a single URL / comma-separated URLs (env: CORS_ORIGINS)."""
        if isinstance(v, list):
            return [str(x) for x in v]
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return ["http://localhost:3000"]
            if v.startswith("["):
                return json.loads(v)
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return ["http://localhost:3000"]

    @model_validator(mode="after")
    def normalize_database_url(self) -> "Settings":
        url = self.database_url
        if url.startswith("postgresql://"):
            self.database_url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            self.database_url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        return self

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
