from __future__ import annotations

import abc
import logging
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

logger = logging.getLogger(__name__)


@dataclass
class AgentContext:
    """Shared context passed through the agent pipeline."""

    merchant_id: UUID
    product_id: UUID | None = None
    job_id: UUID | None = None

    # Merchant data
    merchant_name: str = ""
    merchant_industry: str = ""
    merchant_rules: dict = field(default_factory=dict)

    # Product data
    product_name: str = ""
    product_category: str = ""
    product_description: str = ""

    # Asset data
    asset_urls: list[str] = field(default_factory=list)

    # Persona context (injected from team composition)
    persona_context: dict = field(default_factory=dict)

    # Pipeline artifacts (populated as agents run)
    user_message: str = ""
    conversation_history: list[dict] = field(default_factory=list)
    structured_job: dict = field(default_factory=dict)
    strategy_plan: dict = field(default_factory=dict)
    note_content: dict = field(default_factory=dict)
    visual_assets: dict = field(default_factory=dict)
    compliance_report: dict = field(default_factory=dict)
    ranking_result: dict = field(default_factory=dict)


@dataclass
class AgentResult:
    """Result from an agent execution."""

    success: bool
    output: dict = field(default_factory=dict)
    error: str | None = None
    token_usage: dict = field(default_factory=dict)


class BaseAgent(abc.ABC):
    """Base class for all AI agents in the pipeline.

    Subclasses must set ``role_key`` and ``display_name`` as class attributes and
    implement ``execute`` and ``_get_role_prompt``.
    """

    role_key: str = ""
    display_name: str = ""

    def __init__(self, llm_client: Any = None):
        self._llm = llm_client
        self._logger = logging.getLogger(f"agent.{self.role_key}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @abc.abstractmethod
    async def execute(self, ctx: AgentContext) -> AgentResult:
        """Run the agent's logic and return a result."""
        ...

    # ------------------------------------------------------------------
    # Prompt helpers
    # ------------------------------------------------------------------

    def _build_system_prompt(self, ctx: AgentContext) -> str:
        """Build the system prompt, optionally injecting persona context."""
        base_prompt = self._get_role_prompt()
        if ctx.persona_context:
            persona_prefix = self._format_persona(ctx.persona_context)
            return f"{persona_prefix}\n\n{base_prompt}"
        return base_prompt

    @abc.abstractmethod
    def _get_role_prompt(self) -> str:
        """Return the role-specific system prompt."""
        ...

    def _format_persona(self, persona: dict) -> str:
        """Format persona context as a system prompt prefix."""
        style = persona.get("communication_style", "")
        name = persona.get("display_name", "")
        tone_rules = persona.get("tone_rules", [])
        desc = persona.get("description", "")

        parts: list[str] = []
        if name:
            parts.append(f"你是{name}。")
        if desc:
            parts.append(desc)
        if style:
            parts.append(f"你的沟通风格是{style}。")
        if tone_rules:
            parts.append(f"语气规则：{'、'.join(tone_rules)}。")
        return " ".join(parts)
