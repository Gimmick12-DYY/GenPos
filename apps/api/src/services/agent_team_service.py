from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import (
    AgentRole,
    AgentTeam,
    AgentTeamMember,
    PersonaExperiment,
)
from src.schemas import (
    AgentTeamCreate,
    AgentTeamMemberCreate,
    AgentTeamUpdate,
    ExperimentCreate,
)


async def create_agent_team(db: AsyncSession, data: AgentTeamCreate) -> AgentTeam:
    team = AgentTeam(**data.model_dump())
    db.add(team)
    await db.commit()
    await db.refresh(team)
    return team


async def get_agent_team(db: AsyncSession, team_id: UUID) -> AgentTeam | None:
    return await db.get(AgentTeam, team_id)


async def get_agent_team_detail(db: AsyncSession, team_id: UUID) -> AgentTeam | None:
    stmt = (
        select(AgentTeam)
        .where(AgentTeam.id == team_id)
        .options(
            selectinload(AgentTeam.members).selectinload(AgentTeamMember.role),
            selectinload(AgentTeam.members).selectinload(AgentTeamMember.persona),
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_agent_team(db: AsyncSession, team_id: UUID, data: AgentTeamUpdate) -> AgentTeam:
    team = await db.get(AgentTeam, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Agent team not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(team, field, value)

    await db.commit()
    await db.refresh(team)
    return team


async def add_team_member(db: AsyncSession, team_id: UUID, data: AgentTeamMemberCreate) -> AgentTeamMember:
    team = await db.get(AgentTeam, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Agent team not found")

    member = AgentTeamMember(team_id=team_id, **data.model_dump())
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return member


async def remove_team_member(db: AsyncSession, team_id: UUID, member_id: UUID) -> None:
    member = await db.get(AgentTeamMember, member_id)
    if member is None or member.team_id != team_id:
        raise HTTPException(status_code=404, detail="Team member not found")

    await db.delete(member)
    await db.commit()


async def list_agent_roles(db: AsyncSession) -> list[AgentRole]:
    stmt = select(AgentRole).order_by(AgentRole.role_key)
    return list((await db.execute(stmt)).scalars().all())


async def create_experiment(db: AsyncSession, team_id: UUID, data: ExperimentCreate) -> PersonaExperiment:
    team = await db.get(AgentTeam, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Agent team not found")

    experiment = PersonaExperiment(team_id=team_id, **data.model_dump())
    db.add(experiment)
    await db.commit()
    await db.refresh(experiment)
    return experiment
