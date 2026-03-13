from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import verify_token
from src.schemas import (
    AgentRoleResponse,
    AgentTeamCreate,
    AgentTeamDetailResponse,
    AgentTeamMemberCreate,
    AgentTeamMemberResponse,
    AgentTeamResponse,
    AgentTeamUpdate,
    ExperimentCreate,
    ExperimentResponse,
)
from src.services import agent_team_service

router = APIRouter()


@router.post(
    "",
    response_model=AgentTeamResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_agent_team(
    body: AgentTeamCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Create a new agent team."""
    return await agent_team_service.create_agent_team(db, body)


@router.get("", response_model=list[AgentTeamResponse])
async def list_agent_teams(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """List agent teams (placeholder — returns empty list)."""
    return []


@router.get("/roles", response_model=list[AgentRoleResponse])
async def list_agent_roles(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """List available agent roles."""
    return await agent_team_service.list_agent_roles(db)


@router.get("/{team_id}", response_model=AgentTeamDetailResponse)
async def get_agent_team(
    team_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Get agent team by ID with full member details."""
    team = await agent_team_service.get_agent_team_detail(db, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Agent team not found")
    return team


@router.patch("/{team_id}", response_model=AgentTeamResponse)
async def update_agent_team(
    team_id: UUID,
    body: AgentTeamUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Update agent team."""
    return await agent_team_service.update_agent_team(db, team_id, body)


@router.post(
    "/{team_id}/members",
    response_model=AgentTeamMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_team_member(
    team_id: UUID,
    body: AgentTeamMemberCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Add a role-persona binding to the team."""
    return await agent_team_service.add_team_member(db, team_id, body)


@router.delete(
    "/{team_id}/members/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_team_member(
    team_id: UUID,
    member_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Remove a role-persona binding from the team."""
    await agent_team_service.remove_team_member(db, team_id, member_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{team_id}/experiments",
    response_model=ExperimentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_persona_experiment(
    team_id: UUID,
    body: ExperimentCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Create an A/B persona experiment."""
    return await agent_team_service.create_experiment(db, team_id, body)
