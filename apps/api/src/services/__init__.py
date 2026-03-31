"""Service layer. `generation_service` is lazy-loaded to avoid circular imports with `orchestrator`."""

from __future__ import annotations

import importlib
from typing import Any

from . import (
    agent_team_service,
    analytics_service,
    asset_service,
    chat_service,
    export_service,
    fatigue_service,
    image_generation_service,
    image_render_service,
    merchant_service,
    note_package_service,
    persona_service,
    product_catalog_service,
    product_service,
    ranking_service,
    review_service,
)

__all__ = [
    "agent_team_service",
    "analytics_service",
    "asset_service",
    "chat_service",
    "export_service",
    "fatigue_service",
    "generation_service",
    "image_generation_service",
    "image_render_service",
    "merchant_service",
    "note_package_service",
    "persona_service",
    "product_catalog_service",
    "product_service",
    "ranking_service",
    "review_service",
]


def __getattr__(name: str) -> Any:
    if name == "generation_service":
        return importlib.import_module("src.services.generation_service")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
