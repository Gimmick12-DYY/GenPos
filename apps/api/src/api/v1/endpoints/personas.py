from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import verify_token
from src.schemas import (
    PersonaCreate,
    PersonaListResponse,
    PersonaResponse,
    PersonaUpdate,
)
from src.services import persona_service

router = APIRouter()


@router.post(
    "",
    response_model=PersonaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_persona(
    body: PersonaCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Create a new AI agent persona."""
    return await persona_service.create_persona(db, body)


@router.get("", response_model=PersonaListResponse)
async def list_personas(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    active: bool | None = None,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """List personas for the current tenant."""
    active_only = active if active is not None else True
    items, total = await persona_service.list_personas(
        db, limit=limit, offset=offset, active_only=active_only
    )
    return PersonaListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona(
    persona_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Get persona by ID."""
    persona = await persona_service.get_persona(db, persona_id)
    if persona is None:
        raise HTTPException(status_code=404, detail="Persona not found")
    return persona


@router.patch("/{persona_id}", response_model=PersonaResponse)
async def update_persona(
    persona_id: UUID,
    body: PersonaUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Update persona definition (creates new version)."""
    return await persona_service.update_persona(db, persona_id, body)
