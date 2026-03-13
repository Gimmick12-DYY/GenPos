from fastapi import APIRouter

from src.api.v1.endpoints import (
    agent_teams,
    analytics,
    auth,
    assets,
    chat,
    export,
    generation,
    merchants,
    note_packages,
    personas,
    products,
    review,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(merchants.router, prefix="/merchants", tags=["merchants"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(assets.router, prefix="/asset-packs", tags=["assets"])
api_router.include_router(generation.router, prefix="/generate", tags=["generation"])
api_router.include_router(note_packages.router, prefix="/note-packages", tags=["note-packages"])
api_router.include_router(review.router, prefix="/review", tags=["review"])
api_router.include_router(export.router, prefix="/export", tags=["export"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(personas.router, prefix="/personas", tags=["personas"])
api_router.include_router(agent_teams.router, prefix="/agent-teams", tags=["agent-teams"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
