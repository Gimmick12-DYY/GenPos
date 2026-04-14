from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Persona
from src.schemas import PersonaCreate, PersonaUpdate


async def create_persona(db: AsyncSession, data: PersonaCreate) -> Persona:
    payload = data.model_dump()
    persona = Persona(
        name=payload["name"],
        description=payload.get("description"),
        communication_style=payload.get("communication_style"),
        decision_style=payload.get("decision_style"),
        tone_rules_json=payload.get("tone_rules"),
        forbidden_behaviors_json=payload.get("forbidden_behaviors"),
    )
    db.add(persona)
    await db.commit()
    await db.refresh(persona)
    return persona


async def list_personas(
    db: AsyncSession, limit: int, offset: int, active_only: bool = True
) -> tuple[list[Persona], int]:
    base = select(Persona)
    count_base = select(func.count()).select_from(Persona)

    if active_only:
        base = base.where(Persona.active.is_(True))
        count_base = count_base.where(Persona.active.is_(True))

    total = (await db.execute(count_base)).scalar_one()

    items_stmt = base.order_by(Persona.created_at.desc()).limit(limit).offset(offset)
    items = list((await db.execute(items_stmt)).scalars().all())

    return items, total


async def get_persona(db: AsyncSession, persona_id: UUID) -> Persona | None:
    return await db.get(Persona, persona_id)


async def update_persona(db: AsyncSession, persona_id: UUID, data: PersonaUpdate) -> Persona:
    persona = await db.get(Persona, persona_id)
    if persona is None:
        raise HTTPException(status_code=404, detail="Persona not found")

    update_data = data.model_dump(exclude_unset=True)

    field_map = {
        "tone_rules": "tone_rules_json",
        "forbidden_behaviors": "forbidden_behaviors_json",
    }

    for field, value in update_data.items():
        attr = field_map.get(field, field)
        setattr(persona, attr, value)

    await db.commit()
    await db.refresh(persona)
    return persona
